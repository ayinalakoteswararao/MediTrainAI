# 🏥 **MediTrainAI - Empowering the Doctors of Tomorrow, Today**  
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-orange)](https://streamlit.io/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

---

## 📋 **Overview**  
MediTrainAI is a **smart medical chatbot** designed to assist users with **general medical queries**. Powered by **Groq's AI models** and a sleek **Streamlit interface**, MediTrainAI offers **empathetic, accurate, and user-friendly interactions**.  

**⚠️ Note:** MediTrainAI is not a replacement for professional healthcare advice. Always consult a certified healthcare provider for medical concerns.  

---

## ⭐ **Key Features**  

### 🧠 **Smart Conversational Context**  
- Retains the context of recent interactions for cohesive and natural responses.  

### 🔍 **Medical Query Assistance**  
- Provides reliable, general health-related guidance while avoiding direct medical diagnoses.  

### 🖥️ **Streamlit-Based Interface**  
- Intuitive, modern, and interactive web UI, designed for seamless user experience.  

### 💬 **Empathy-Focused Responses**  
- Ensures that responses are accurate, considerate, and easy to understand for everyone.  

---

## 🛠️ Technology Stack
- **🐍 Backend**: Python Flask
- **💾 Database**: MySQL
- **🤖 AI/ML**: Sentence-Transformers (BERT)
- **🎨 Frontend**: HTML5, CSS3, JavaScript
- **🔐 Authentication**: Flask-Login
- **📁 File Handling**: Werkzeug
- **🎭 Icons**: Font Awesome 6

## 📂 Project Structure
```
MediTrainAI/
├── app.py                    # Main Flask application
├── database.py              # Database models and configuration
├── static/
│   ├── style.css           # Main stylesheet with profile styling
│   ├── uploads/            # User uploaded files
│   └── script.js           # Frontend JavaScript
├── templates/
│   ├── index.html          # Main application interface
│   └── patient_register.html # Registration page
└── data/
    └── medical_conditions.json # Medical conditions database
''' 


## 🚀 **Getting Started**  

### 🛑 **Prerequisites**  
Ensure you have the following installed on your system:  
1. **Python 3.8+**  
2. **Groq API Key** (get it from Groq's API portal)  

---

### 🛠️ **Setup Instructions**  

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/MediTrainAI.git
   cd MediTrainAI
   ```

2. **Create and activate a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**  
   Create a file named `.env` in the project root and add:  
   ```plaintext
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application**  
   ```bash
   streamlit run app.py
   ```
   The application will open in your browser (default: [http://localhost:8501](http://localhost:8501/)).  

---

## 🔒 **Security Features**  
- API key storage using `.env`.  
- Prevents exposure of sensitive information in logs or UI.  

---

## 📄 **License**  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.  

---

## 💬 **Contact & Support**  
For questions, suggestions, or issues, please reach out:  

✉️ **Email**: [ayinalakoteswararao15@gmail.com](mailto:ayinalakoteswararao15@gmail.com)  

Made with ❤️ by **Ayinala Koteswararao**