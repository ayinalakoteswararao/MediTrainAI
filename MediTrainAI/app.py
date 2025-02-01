from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import logging
from sentence_transformers import SentenceTransformer, util
import torch
from database import db, Patient, SearchHistory
import urllib.parse
from datetime import datetime
import os

app = Flask(__name__)

# App configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///meditrainai.db')  # Use environment variable or fallback to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload configurations
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'patient_login'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize BERT model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Successfully loaded the model")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None

def load_conditions():
    """Load medical conditions from JSON files"""
    conditions_dir = Path(__file__).parent / 'data' / 'conditions'
    conditions = []
    
    try:
        for file_path in conditions_dir.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'conditions' in data:
                    conditions.extend(data['conditions'])
                elif isinstance(data, list):
                    conditions.extend(data)
        logger.info(f"Loaded {len(conditions)} conditions")
        return conditions
    except Exception as e:
        logger.error(f"Error loading conditions: {str(e)}")
        return []

def analyze_symptoms_bert(text):
    """Analyze symptoms using BERT model"""
    if model is None:
        logger.warning("BERT model not available, falling back to keyword matching")
        return analyze_symptoms(text)
        
    try:
        # Encode user input
        text_embedding = model.encode(text, convert_to_tensor=True)
        
        best_match = None
        highest_score = 0
        
        # Compare with each condition
        for condition in conditions_data:
            # Create a comprehensive description for matching
            condition_text = f"{condition['name']} symptoms include: {' '.join(condition['symptoms'])}"
            condition_embedding = model.encode(condition_text, convert_to_tensor=True)
            
            # Calculate similarity score
            similarity = util.pytorch_cos_sim(text_embedding, condition_embedding)
            score = float(similarity[0][0]) * 100
            
            if score > highest_score:
                highest_score = score
                best_match = {
                    'condition': condition['name'],
                    'confidence': round(min(score, 95.0), 1),  # Cap at 95%
                    'severity': condition['severity'],
                    'suggestion': condition['suggestion'],
                    'duration': condition['duration']
                }
        
        if not best_match or highest_score < 30:  # Minimum confidence threshold
            return {
                'condition': 'Unknown',
                'confidence': 0,
                'severity': 'low',
                'suggestion': 'Please consult a healthcare provider for proper diagnosis.',
                'duration': 'unknown'
            }
        
        return best_match
        
    except Exception as e:
        logger.error(f"Error in BERT analysis: {str(e)}")
        return analyze_symptoms(text)  # Fallback to keyword matching

def analyze_symptoms(text):
    """Simple symptom analysis based on keyword matching (fallback method)"""
    text = text.lower()
    best_match = None
    highest_score = 0
    
    for condition in conditions_data:
        score = 0
        symptoms = [s.lower() for s in condition['symptoms']]
        
        for symptom in symptoms:
            if symptom in text:
                score += 1
        
        if len(symptoms) > 0:
            confidence = (score / len(symptoms)) * 100
            
            if confidence > highest_score:
                highest_score = confidence
                best_match = {
                    'condition': condition['name'],
                    'confidence': round(min(confidence, 95.0), 1),
                    'severity': condition['severity'],
                    'suggestion': condition['suggestion'],
                    'duration': condition['duration']
                }
    
    if not best_match:
        return {
            'condition': 'Unknown',
            'confidence': 0,
            'severity': 'low',
            'suggestion': 'Please consult a healthcare provider for proper diagnosis.',
            'duration': 'unknown'
        }
    
    return best_match

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get the current user's profile picture
    patient_photo = None
    if current_user.profile_picture:
        patient_photo = os.path.join('uploads', current_user.profile_picture)
    return render_template('index.html', patient_photo=patient_photo, current_user=current_user)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        logger.info("Received prediction request")
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or 'symptoms' not in data:
            logger.warning("No symptoms provided in request")
            return jsonify({
                'error': 'Please provide symptoms description'
            }), 400
        
        symptoms_text = data['symptoms'].strip()
        logger.info(f"Symptoms text: {symptoms_text}")
        
        if not symptoms_text:
            logger.warning("Empty symptoms text received")
            return jsonify({
                'error': 'Please provide symptoms description'
            }), 400
            
        # Try BERT analysis first, fallback to keyword matching if it fails
        try:
            result = analyze_symptoms_bert(symptoms_text)
        except Exception as e:
            logger.error(f"BERT analysis failed, falling back to keyword matching: {str(e)}")
            result = analyze_symptoms(symptoms_text)
            
        logger.info(f"Analysis result: {result}")

        # Store search history in database
        search_history = SearchHistory(
            patient_id=current_user.id,
            symptoms=symptoms_text,
            predicted_condition=result['condition'],
            confidence=result['confidence']
        )
        db.session.add(search_history)
        db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred during analysis'
        }), 500

@app.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            full_name = request.form.get('full_name')
            
            # Validate required fields
            if not all([username, email, password, confirm_password, full_name]):
                flash('Please fill in all required fields')
                return redirect(url_for('patient_register'))
            
            # Validate password match
            if password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('patient_register'))
            
            # Check if username or email already exists
            if Patient.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('patient_register'))
            
            if Patient.query.filter_by(email=email).first():
                flash('Email already exists')
                return redirect(url_for('patient_register'))
            
            # Create new patient with all form data
            new_patient = Patient(
                username=username,
                email=email,
                password=generate_password_hash(password),
                full_name=full_name
            )
            
            # Add optional fields if provided
            if request.form.get('date_of_birth'):
                try:
                    new_patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format for date of birth')
                    return redirect(url_for('patient_register'))
            
            if request.form.get('gender'):
                new_patient.gender = request.form.get('gender')
            if request.form.get('blood_group'):
                new_patient.blood_group = request.form.get('blood_group')
            if request.form.get('phone'):
                new_patient.phone = request.form.get('phone')
            if request.form.get('emergency_contact'):
                new_patient.emergency_contact = request.form.get('emergency_contact')
            if request.form.get('address'):
                new_patient.address = request.form.get('address')
            if request.form.get('medical_conditions'):
                new_patient.medical_conditions = request.form.get('medical_conditions')
            if request.form.get('allergies'):
                new_patient.allergies = request.form.get('allergies')
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    new_patient.profile_picture = filename
            
            # Save to database
            db.session.add(new_patient)
            db.session.commit()
            logger.info(f"Successfully registered user: {username}")
            
            flash('Registration successful! Please login.')
            return redirect(url_for('patient_login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash(f'An error occurred during registration. Please try again.')
            return redirect(url_for('patient_register'))
            
    return render_template('patient_register.html')

@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            user = Patient.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                logger.info(f"User {username} logged in successfully")
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                flash('Invalid username or password', 'error')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('patient_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('p_'):
        user_id = user_id[2:]  # Remove 'p_' prefix
    return Patient.query.get(int(user_id))

# Initialize database tables
with app.app_context():
    try:
        # Create tables if they don't exist
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Load conditions at startup
conditions_data = load_conditions()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
