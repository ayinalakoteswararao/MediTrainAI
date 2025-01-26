// UI Animation Constants
const ANIMATION_DURATION = 800;
const TYPING_DELAY = 30;

// UI Elements Cache
const elements = {
    form: document.querySelector('.form-card'),
    symptomsInput: document.getElementById('symptoms'),
    submitButton: document.querySelector('.submit-btn'),
    loadingSpinner: document.querySelector('.loading'),
    resultSection: document.getElementById('resultSection'),
    confidenceBar: document.getElementById('confidenceLevel'),
    confidenceText: document.getElementById('confidenceText'),
    severityBadge: document.getElementById('severityBadge'),
    conditionName: document.getElementById('conditionName'),
    recommendationText: document.getElementById('recommendationText'),
    duration: document.getElementById('duration'),
    severityDetails: document.getElementById('severityDetails')
};

// Typing Animation Effect
function typeWriter(element, text, delay = TYPING_DELAY) {
    let index = 0;
    element.textContent = '';
    
    return new Promise(resolve => {
        function type() {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(type, delay);
            } else {
                resolve();
            }
        }
        type();
    });
}

// Animated Number Counter
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();
    const updateInterval = 16; // ~60fps

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = start + (end - start) * easeOutQuart;
        
        element.textContent = `${Math.round(current)}% Confidence`;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Ripple Effect for Buttons
function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    
    const diameter = Math.max(rect.width, rect.height);
    const radius = diameter / 2;
    
    ripple.style.width = ripple.style.height = `${diameter}px`;
    ripple.style.left = `${event.clientX - rect.left - radius}px`;
    ripple.style.top = `${event.clientY - rect.top - radius}px`;
    ripple.classList.add('ripple');
    
    const existingRipple = button.querySelector('.ripple');
    if (existingRipple) {
        existingRipple.remove();
    }
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Enhanced Floating Label Effect
function initializeFloatingLabel() {
    const textarea = elements.symptomsInput;
    const wrapper = textarea.parentElement;
    
    textarea.addEventListener('focus', () => {
        wrapper.classList.add('focused');
    });
    
    textarea.addEventListener('blur', () => {
        if (!textarea.value.trim()) {
            wrapper.classList.remove('focused');
        }
    });
    
    textarea.addEventListener('input', () => {
        wrapper.classList[textarea.value.trim() ? 'add' : 'remove']('has-content');
    });
}

// Scroll Animation Observer
function initializeScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    if (entry.target.classList.contains('one-time-animation')) {
                        observer.unobserve(entry.target);
                    }
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px'
        }
    );

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });
}

// Custom Notification System
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 
                       type === 'warning' ? 'fa-exclamation-triangle' : 
                       'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Trigger reflow for animation
    notification.offsetHeight;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Toggle Severity Details
function toggleSeverityDetails() {
    const severityDetails = elements.severityDetails;
    const isVisible = severityDetails.style.display === 'block';
    
    if (isVisible) {
        severityDetails.style.display = 'none';
    } else {
        severityDetails.style.display = 'block';
        severityDetails.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Toggle Info Panels
function toggleInfo(section) {
    const infoPanel = document.getElementById(`${section}Info`);
    const allPanels = document.querySelectorAll('.info-panel');
    
    // Hide all other panels
    allPanels.forEach(panel => {
        if (panel !== infoPanel) {
            panel.style.display = 'none';
        }
    });
    
    // Toggle the clicked panel
    if (infoPanel.style.display === 'block') {
        infoPanel.style.display = 'none';
    } else {
        infoPanel.style.display = 'block';
        infoPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// Update severity badge with icon
function updateSeverityBadge(severity) {
    const badge = elements.severityBadge;
    let icon = '';
    
    switch(severity.toLowerCase()) {
        case 'male':
            icon = '<i class="fas fa-mars"></i>';
            break;
        case 'female':
            icon = '<i class="fas fa-venus"></i>';
            break;
        case 'low':
            icon = '<i class="fas fa-info-circle"></i>';
            break;
        case 'medium':
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        case 'high':
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
    }
    
    badge.className = `severity-badge ${severity.toLowerCase()}`;
    badge.innerHTML = `${icon} ${severity.toUpperCase()}`;
    badge.setAttribute('title', 'Click for severity details');
    badge.addEventListener('click', toggleSeverityDetails);
}

// Main Analysis Function
async function analyzeSymptoms() {
    const symptoms = elements.symptomsInput.value.trim();
    
    if (!symptoms) {
        showNotification('Please describe your symptoms', 'warning');
        elements.symptomsInput.focus();
        return;
    }

    try {
        elements.submitButton.disabled = true;
        elements.loadingSpinner.style.display = 'inline-block';
        elements.submitButton.classList.add('loading-state');

        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symptoms })
        });

        if (!response.ok) {
            throw new Error('Failed to analyze symptoms');
        }

        const result = await response.json();

        // Hide severity details if visible
        elements.severityDetails.style.display = 'none';

        // Show results section
        elements.resultSection.style.display = 'block';
        elements.resultSection.classList.add('fade-in');

        // Update severity badge with icon
        updateSeverityBadge(result.severity);

        // Animate confidence bar
        elements.confidenceBar.style.width = '0%';
        setTimeout(() => {
            elements.confidenceBar.style.width = `${result.confidence}%`;
            animateNumber(
                elements.confidenceText.querySelector('span'),
                0,
                result.confidence,
                ANIMATION_DURATION
            );
        }, 100);

        // Animate text elements
        await typeWriter(elements.conditionName, result.condition);
        await typeWriter(elements.recommendationText, result.suggestion, 20);

        // Update duration
        elements.duration.innerHTML = `
            <i class="fas fa-clock"></i>
            <span>Expected Duration: ${result.duration}</span>
        `;

        // Smooth scroll to results
        elements.resultSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

    } catch (error) {
        console.error('Error:', error);
        showNotification(
            'Failed to analyze symptoms. Please try again.',
            'error'
        );
    } finally {
        elements.submitButton.disabled = false;
        elements.loadingSpinner.style.display = 'none';
        elements.submitButton.classList.remove('loading-state');
    }
}

// Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI enhancements
    initializeFloatingLabel();
    initializeScrollAnimations();

    // Add ripple effect to buttons
    document.querySelectorAll('.submit-btn').forEach(button => {
        button.addEventListener('click', createRipple);
    });

    // Add input validation
    elements.symptomsInput.addEventListener('input', () => {
        const length = elements.symptomsInput.value.length;
        if (length >= 500) {
            showNotification('Maximum character limit reached', 'warning');
        }
    });

    // Close info panels when clicking outside
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.info-btn') && !event.target.closest('.info-panel')) {
            document.querySelectorAll('.info-panel').forEach(panel => {
                panel.style.display = 'none';
            });
        }
    });
});