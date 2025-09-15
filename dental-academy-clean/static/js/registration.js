// Clean registration.js without Jinja2 template tags
document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    setupFileUploads();
    
    // Form validation
    setupFormValidation();
    
    // Progress indicator
    setupProgressIndicator();
    
    // Initialize other fields
    initializeOtherFields();
    
    // Initialize auto-fill signature
    initializeAutoFillSignature();
    
    // Initialize nationality search
    initializeNationalitySearch();
    
    // Setup form auto-save
    setupFormAutoSave();
});

// Function to toggle "Other" fields
function toggleOtherField(selectId, otherFieldId) {
    const select = document.getElementById(selectId);
    const otherGroup = document.getElementById(otherFieldId + '_group');
    const otherField = document.getElementById(otherFieldId);
    
    // Check if elements exist before proceeding
    if (!select || !otherGroup || !otherField) {
        console.warn(`toggleOtherField: Missing elements for ${selectId} -> ${otherFieldId}`);
        return;
    }
    
    // Check for both 'other' and 'OTHER' values
    if (select.value === 'other' || select.value === 'OTHER') {
        otherGroup.style.display = 'block';
        otherField.required = true;
    } else {
        otherGroup.style.display = 'none';
        otherField.required = false;
        otherField.value = '';
    }
}

// Initialize other fields on page load
function initializeOtherFields() {
    // Wait a bit to ensure DOM is fully loaded
    setTimeout(() => {
        // Check profession field
        toggleOtherField('profession', 'other_profession');
        
        // Check nationality field
        toggleOtherField('nationality', 'other_nationality');
        
        // Check legal status field
        toggleOtherField('legal_status', 'other_legal_status');
        
        // Check study country field
        toggleOtherField('study_country', 'other_country');
        
        // Initialize phone number formatting
        setupPhoneNumberFormatting();
    }, 100);
}

// Initialize auto-fill signature functionality
function initializeAutoFillSignature() {
    const autoFillBtn = document.getElementById('autoFillSignature');
    const signatureField = document.getElementById('digital_signature');
    const firstNameField = document.getElementById('first_name');
    const lastNameField = document.getElementById('last_name');
    
    if (autoFillBtn && signatureField && firstNameField && lastNameField) {
        // Auto-fill button click
        autoFillBtn.addEventListener('click', function() {
            const firstName = firstNameField.value.trim();
            const lastName = lastNameField.value.trim();
            
            if (firstName && lastName) {
                signatureField.value = `${firstName} ${lastName}`;
                signatureField.style.borderColor = '#27ae60';
                
                // Show success message
                showFieldSuccess(signatureField, 'Signature auto-filled successfully!');
            } else {
                showFieldError(signatureField, 'Please fill in your first and last name first');
            }
        });
        
        // Auto-fill when name fields change
        firstNameField.addEventListener('input', updateSignaturePreview);
        lastNameField.addEventListener('input', updateSignaturePreview);
        
        // Real-time validation for signature
        signatureField.addEventListener('input', function() {
            const firstName = firstNameField.value.trim();
            const lastName = lastNameField.value.trim();
            const signature = this.value.trim();
            const expectedSignature = `${firstName} ${lastName}`.trim();
            
            if (signature === expectedSignature && signature.length > 0) {
                this.style.borderColor = '#27ae60';
                clearFieldError(this);
            } else if (signature.length > 0) {
                this.style.borderColor = '#e74c3c';
            } else {
                this.style.borderColor = '#ecf0f1';
                clearFieldError(this);
            }
        });
    }
}

// Update signature preview
function updateSignaturePreview() {
    const firstName = document.getElementById('first_name').value.trim();
    const lastName = document.getElementById('last_name').value.trim();
    const signatureField = document.getElementById('digital_signature');
    
    if (firstName && lastName && !signatureField.value.trim()) {
        // Show preview in placeholder
        signatureField.placeholder = `Will be: ${firstName} ${lastName}`;
    }
}

// Show field success message
function showFieldSuccess(field, message) {
    clearFieldError(field);
    
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    
    field.parentNode.appendChild(successDiv);
    
    // Remove success message after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 3000);
}

// Setup phone number formatting
function setupPhoneNumberFormatting() {
    const countryCodeSelect = document.getElementById('country_code');
    const phoneInput = document.getElementById('phone');
    
    if (countryCodeSelect && phoneInput) {
        // Update phone placeholder based on country code
        countryCodeSelect.addEventListener('change', function() {
            const countryCode = this.value;
            const placeholders = {
                '+31': '612345678',  // Netherlands
                '+49': '15123456789', // Germany
                '+32': '471234567',  // Belgium
                '+33': '612345678',  // France
                '+34': '612345678',  // Spain
                '+39': '3123456789', // Italy
                '+351': '912345678', // Portugal
                '+48': '123456789',  // Poland
                '+40': '712345678',  // Romania
                '+359': '871234567', // Bulgaria
                '+36': '201234567',  // Hungary
                '+420': '123456789', // Czech Republic
                '+421': '123456789', // Slovakia
                '+385': '912345678', // Croatia
                '+386': '401234567', // Slovenia
                '+372': '51234567',  // Estonia
                '+371': '21234567',  // Latvia
                '+370': '61234567',  // Lithuania
                '+356': '21234567',  // Malta
                '+357': '96123456',  // Cyprus
                '+352': '621123456', // Luxembourg
                '+43': '664123456',  // Austria
                '+41': '791234567',  // Switzerland
                '+46': '701234567',  // Sweden
                '+47': '41234567',   // Norway
                '+45': '20123456',   // Denmark
                '+358': '401234567', // Finland
                '+354': '6123456',   // Iceland
                '+353': '851234567', // Ireland
                '+44': '7123456789', // United Kingdom
                '+1': '5551234567',  // United States/Canada
                '+61': '412345678',  // Australia
                '+64': '211234567',  // New Zealand
                '+27': '821234567',  // South Africa
                '+55': '11987654321', // Brazil
                '+54': '91123456789', // Argentina
                '+52': '5512345678', // Mexico
                '+91': '9876543210', // India
                '+86': '13812345678', // China
                '+81': '9012345678', // Japan
                '+82': '1012345678', // South Korea
                '+66': '812345678',  // Thailand
                '+84': '912345678',  // Vietnam
                '+63': '9171234567', // Philippines
                '+62': '8123456789', // Indonesia
                '+60': '123456789',  // Malaysia
                '+65': '81234567',   // Singapore
                '+90': '5321234567', // Turkey
                '+20': '1012345678', // Egypt
                '+212': '612345678', // Morocco
                '+216': '20123456',  // Tunisia
                '+213': '551234567', // Algeria
                '+234': '8012345678', // Nigeria
                '+254': '712345678', // Kenya
                '+233': '241234567', // Ghana
                '+251': '911234567', // Ethiopia
                '+380': '501234567', // Ukraine
                '+375': '291234567', // Belarus
                '+7': '9123456789',  // Russia
                '+381': '601234567', // Serbia
                '+387': '61123456',  // Bosnia
                '+382': '67123456',  // Montenegro
                '+389': '70123456',  // Macedonia
                '+355': '691234567', // Albania
                '+373': '60123456'   // Moldova
            };
            
            phoneInput.placeholder = placeholders[countryCode] || '123456789';
        });
        
        // Trigger initial placeholder update
        countryCodeSelect.dispatchEvent(new Event('change'));
    }
}

function setupFileUploads() {
    // Diploma file upload
    const diplomaInput = document.getElementById('diploma_file');
    const diplomaList = document.getElementById('diploma-list');
    
    if (diplomaInput) {
        diplomaInput.addEventListener('change', function(e) {
            handleFileUpload(e, diplomaList, 'diploma');
        });
    }
    
    // Language certificates upload
    const languageInput = document.getElementById('language_certificates');
    const languageList = document.getElementById('language-certificates-list');
    
    if (languageInput) {
        languageInput.addEventListener('change', function(e) {
            handleFileUpload(e, languageList, 'language');
        });
    }
    
    // Additional documents upload
    const additionalInput = document.getElementById('additional_documents');
    const additionalList = document.getElementById('additional-documents-list');
    
    if (additionalInput) {
        additionalInput.addEventListener('change', function(e) {
            handleFileUpload(e, additionalList, 'additional');
        });
    }
}

function handleFileUpload(event, container, type) {
    const files = event.target.files;
    
    if (!container) return;
    
    // Clear previous files
    container.innerHTML = '';
    
    Array.from(files).forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'uploaded-file';
        fileItem.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="remove-file" onclick="removeFile('${type}', ${index})">×</span>
        `;
        container.appendChild(fileItem);
    });
}

function removeFile(type, index) {
    const input = document.getElementById(type === 'diploma' ? 'diploma_file' : 
                                   type === 'language' ? 'language_certificates' : 'additional_documents');
    
    // Create new FileList without the removed file
    const dt = new DataTransfer();
    Array.from(input.files).forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    input.files = dt.files;
    
    // Update display
    const container = document.getElementById(type === 'diploma' ? 'diploma-list' : 
                                           type === 'language' ? 'language-certificates-list' : 'additional-documents-list');
    handleFileUpload({target: {files: input.files}}, container, type);
}

function setupFormValidation() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    
    if (!form || !submitBtn) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            submitForm();
        }
    });
    
    // Real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}

function validateForm() {
    let isValid = true;
    const form = document.getElementById('registrationForm');
    
    // Check required fields
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!validateField({target: field})) {
            isValid = false;
        }
    });
    
    // Check diploma fields
    const universityName = document.getElementById('university_name');
    const degreeType = document.getElementById('degree_type');
    const studyStartYear = document.getElementById('study_start_year');
    const studyEndYear = document.getElementById('study_end_year');
    const studyCountry = document.getElementById('study_country');
    
    if (universityName && !universityName.value.trim()) {
        showFieldError(universityName, 'University name is required');
        isValid = false;
    }
    
    if (degreeType && !degreeType.value) {
        showFieldError(degreeType, 'Degree type is required');
        isValid = false;
    }
    
    if (studyStartYear && studyEndYear) {
        if (!studyStartYear.value || !studyEndYear.value) {
            if (!studyStartYear.value) {
                showFieldError(studyStartYear, 'Start year is required');
            }
            if (!studyEndYear.value) {
                showFieldError(studyEndYear, 'End year is required');
            }
            isValid = false;
        } else {
            // Validate year range
            const startYear = parseInt(studyStartYear.value);
            const endYear = parseInt(studyEndYear.value);
            const currentYear = new Date().getFullYear();
            
            if (startYear > endYear) {
                showFieldError(studyEndYear, 'End year must be after start year');
                isValid = false;
            }
            
            if (startYear < 1950 || startYear > currentYear) {
                showFieldError(studyStartYear, 'Start year must be between 1950 and current year');
                isValid = false;
            }
            
            if (endYear < 1950 || endYear > currentYear) {
                showFieldError(studyEndYear, 'End year must be between 1950 and current year');
                isValid = false;
            }
        }
    }
    
    if (studyCountry && !studyCountry.value) {
        showFieldError(studyCountry, 'Country of study is required');
        isValid = false;
    }
    
    // Check other country name if "Other" is selected
    const otherCountryName = document.getElementById('other_country_name');
    if (studyCountry && studyCountry.value === 'OTHER' && otherCountryName && (!otherCountryName.value || !otherCountryName.value.trim())) {
        showFieldError(otherCountryName, 'Please specify the country name');
        isValid = false;
    }
    
    // Check "Other" fields
    const profession = document.getElementById('profession');
    const otherProfession = document.getElementById('other_profession');
    if (profession && profession.value === 'other' && otherProfession && !otherProfession.value.trim()) {
        showFieldError(otherProfession, 'Please specify your profession');
        isValid = false;
    }
    
    const nationality = document.getElementById('nationality');
    const otherNationality = document.getElementById('other_nationality');
    if (nationality && nationality.value === 'OTHER' && otherNationality && !otherNationality.value.trim()) {
        showFieldError(otherNationality, 'Please specify your nationality');
        isValid = false;
    }
    
    const legalStatus = document.getElementById('legal_status');
    const otherLegalStatus = document.getElementById('other_legal_status');
    if (legalStatus && legalStatus.value === 'other' && otherLegalStatus && !otherLegalStatus.value.trim()) {
        showFieldError(otherLegalStatus, 'Please specify your legal status');
        isValid = false;
    }
    
    // Check password confirmation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }
    
    // Check password strength
    if (password && password.value && !isPasswordStrong(password.value)) {
        showFieldError(password, 'Password must contain at least 8 characters with letters and numbers');
        isValid = false;
    }
    
    // Check digital signature
    const digitalSignature = document.getElementById('digital_signature');
    const firstName = document.getElementById('first_name');
    const lastName = document.getElementById('last_name');
    
    if (digitalSignature) {
        const signature = digitalSignature.value.trim();
        
        if (!signature) {
            showFieldError(digitalSignature, 'Digital signature is required');
            isValid = false;
        } else if (signature.length < 3) {
            showFieldError(digitalSignature, 'Digital signature must be at least 3 characters long');
            isValid = false;
        } else if (firstName && lastName) {
            // Check if signature contains both first and last name (flexible matching)
            const firstNameValue = firstName.value.trim();
            const lastNameValue = lastName.value.trim();
            const firstNameLower = firstNameValue.toLowerCase();
            const lastNameLower = lastNameValue.toLowerCase();
            const signatureLower = signature.toLowerCase();
            
            if (firstNameLower && lastNameLower && 
                (!signatureLower.includes(firstNameLower) || !signatureLower.includes(lastNameLower))) {
                showFieldError(digitalSignature, 'Digital signature should contain your first and last name');
                isValid = false;
            }
        }
    }
    
    return isValid;
}

// Check password strength
function isPasswordStrong(password) {
    // At least 8 characters
    if (password.length < 8) return false;
    
    // Contains at least one letter
    if (!/[a-zA-Z]/.test(password)) return false;
    
    // Contains at least one number
    if (!/[0-9]/.test(password)) return false;
    
    return true;
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && value) {
        const phoneRegex = /^[0-9\s\-\(\)]{7,15}$/;
        if (!phoneRegex.test(value)) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }
    }
    
    // Date validation
    if (field.type === 'date' && value) {
        const date = new Date(value);
        const today = new Date();
        
        if (field.id === 'birth_date' && date >= today) {
            showFieldError(field, 'Birth date cannot be in the future');
            return false;
        }
        
        if (field.id === 'exam_date' && date <= today) {
            showFieldError(field, 'Exam date must be in the future');
            return false;
        }
    }
    
    return true;
}

function showFieldError(field, message) {
    if (!field || !field.parentNode) {
        return;
    }
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
    field.style.borderColor = '#e74c3c';
}

function clearFieldError(field) {
    if (!field || !field.parentNode) {
        return;
    }
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.style.borderColor = '#ecf0f1';
}

function setupProgressIndicator() {
    const sections = document.querySelectorAll('.form-section');
    const steps = document.querySelectorAll('.progress-step');
    
    // Update progress based on completed sections
    function updateProgress() {
        let completedSections = 0;
        
        sections.forEach((section, index) => {
            const requiredFields = section.querySelectorAll('[required]');
            let sectionCompleted = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    sectionCompleted = false;
                }
            });
            
            if (sectionCompleted && requiredFields.length > 0) {
                completedSections++;
                if (steps[index]) {
                    steps[index].classList.add('completed');
                    steps[index].classList.remove('active');
                }
            } else if (steps[index]) {
                steps[index].classList.remove('completed');
                if (index === completedSections) {
                    steps[index].classList.add('active');
                }
            }
        });
    }
    
    // Update progress on field changes
    const allFields = document.querySelectorAll('input, select, textarea');
    allFields.forEach(field => {
        field.addEventListener('change', updateProgress);
        field.addEventListener('input', updateProgress);
    });
    
    // Initial progress update
    updateProgress();
}

// ===== IMPROVED MESSAGE FUNCTIONS =====

// Improved function for showing success messages
function showSuccessMessage(message) {
    // Create a large block with success message
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.5s ease-out;
    `;
    
    // Add CSS animation
    if (!document.getElementById('success-animation-style')) {
        const style = document.createElement('style');
        style.id = 'success-animation-style';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateY(-50px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .success-icon {
                font-size: 60px;
                margin-bottom: 20px;
                animation: bounce 1s ease-in-out;
            }
            
            @keyframes bounce {
                0%, 20%, 60%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-10px);
                }
                80% {
                    transform: translateY(-5px);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    messageDiv.innerHTML = `
        <div class="success-icon">✅</div>
        <h2 style="margin: 0 0 20px 0; font-size: 24px;">Registration Completed!</h2>
        <div style="font-size: 16px; line-height: 1.6;">${message}</div>
        <div style="margin-top: 30px;">
            <button id="continueBtn" style="
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
            " onmouseover="this.style.background='white'; this.style.color='#27ae60'" 
               onmouseout="this.style.background='rgba(255, 255, 255, 0.2)'; this.style.color='white'">
                Continue
            </button>
        </div>
    `;
    
    overlay.appendChild(messageDiv);
    document.body.appendChild(overlay);
    
    // "Continue" button or automatic redirect after 8 seconds
    let countdown = 8;
    const continueBtn = document.getElementById('continueBtn');
    
    const updateButton = () => {
        continueBtn.textContent = `Auto redirect in ${countdown}s (or click)`;
        countdown--;
        
        if (countdown < 0) {
            // Use relative URL for redirect
            window.location.href = '/auth/login';
        }
    };
    
    updateButton();
    const interval = setInterval(updateButton, 1000);
    
    continueBtn.addEventListener('click', () => {
        clearInterval(interval);
        window.location.href = '/auth/login';
    });
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            clearInterval(interval);
            window.location.href = '/auth/login';
        }
    });
}

// Improved function for showing errors
function showErrorMessage(message) {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    const messageDiv = document.createElement('div');
    messageDiv.style.cssText = `
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        max-width: 500px;
        width: 90%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.5s ease-out;
    `;
    
    messageDiv.innerHTML = `
        <div style="font-size: 50px; margin-bottom: 20px;">❌</div>
        <h2 style="margin: 0 0 20px 0; font-size: 24px;">Registration Error</h2>
        <div style="font-size: 16px; line-height: 1.6; margin-bottom: 30px;">${message}</div>
        <button id="closeErrorBtn" style="
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid white;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        " onmouseover="this.style.background='white'; this.style.color='#e74c3c'" 
           onmouseout="this.style.background='rgba(255, 255, 255, 0.2)'; this.style.color='white'">
            Try Again
        </button>
    `;
    
    overlay.appendChild(messageDiv);
    document.body.appendChild(overlay);
    
    // Close on button or overlay click
    const closeBtn = document.getElementById('closeErrorBtn');
    closeBtn.addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
        }
    });
    
    // Auto close after 8 seconds
    setTimeout(() => {
        if (overlay.parentNode) {
            overlay.remove();
        }
    }, 8000);
}

// Improved submitForm function with better UX
async function submitForm() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const formData = new FormData(form);
    
    // Validate reCAPTCHA
    if (!validateRecaptcha()) {
        return;
    }
    
    // Show loading indicator
    submitBtn.disabled = true;
    const originalContent = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing data...';
    
    // Add progress indicator
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0;
        height: 4px;
        background: linear-gradient(90deg, #3ECDC1, #44A08D);
        z-index: 9999;
        transition: width 0.3s ease;
    `;
    document.body.appendChild(progressBar);
    
    // Progress animation
    progressBar.style.width = '30%';
    
    try {
        // Use relative URL for the fetch request
        const response = await fetch('/auth/register', {
            method: 'POST',
            body: formData
        });
        
        progressBar.style.width = '70%';
        
        const result = await response.json();
        
        progressBar.style.width = '100%';
        
        setTimeout(() => {
            progressBar.remove();
        }, 500);
        
        if (result.success) {
            // Block form from resubmission
            form.style.pointerEvents = 'none';
            form.style.opacity = '0.7';
            
            // Clear saved data
            localStorage.removeItem('mentora_registration_draft');
            
            // Show beautiful success message
            const userEmail = formData.get('email') || 'your email';
            const successMessage = `
                <strong>🎉 Excellent! You are registered in the Mentora program</strong><br><br>
                📧 <strong>Check your email</strong><br>
                We sent a confirmation email to <strong>${userEmail}</strong><br><br>
                ⚠️ <strong>Important:</strong> Check your "Spam" or "Junk" folder<br>
                The email might have ended up there. If you find it - mark as "Not Spam"<br><br>
                🚀 After confirming your email, you will be able to log in and receive notifications about the program launch in Q1 2025
            `;
            showSuccessMessage(successMessage);
        } else {
            // Show detailed error
            const errorMessage = result.error || 'An error occurred during registration. Please try again.';
            showErrorMessage(`
                <strong>Failed to complete registration:</strong><br><br>
                ${errorMessage}<br><br>
                💡 <strong>Try:</strong><br>
                • Check that all required fields are filled correctly<br>
                • Make sure the email is not already registered<br>
                • Refresh the page and try again
            `);
        }
    } catch (error) {
        progressBar.remove();
        console.error('Registration error:', error);
        showErrorMessage(`
            <strong>Network Error:</strong><br><br>
            Could not connect to the server. Please check:<br>
            • Internet connection<br>
            • Try refreshing the page<br>
            • If the problem persists, contact support
        `);
    } finally {
        // Restore button only in case of error
        setTimeout(() => {
            if (submitBtn.disabled && !form.style.pointerEvents) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalContent;
            }
        }, 1000);
    }
}

// Auto-save form to localStorage
function setupFormAutoSave() {
    const form = document.getElementById('registrationForm');
    
    if (!form) return;
    
    // Load saved data on page load
    const savedData = localStorage.getItem('mentora_registration_draft');
    if (savedData) {
        try {
            const parsed = JSON.parse(savedData);
            Object.keys(parsed).forEach(key => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field && field.type !== 'password') { // Don't save passwords
                    if (field.type === 'checkbox') {
                        field.checked = parsed[key] === 'on' || parsed[key] === true;
                    } else {
                        field.value = parsed[key];
                    }
                }
            });
            
            // Update "other" fields after loading
            setTimeout(() => {
                toggleOtherField('profession', 'other_profession');
                toggleOtherField('nationality', 'other_nationality');
                toggleOtherField('legal_status', 'other_legal_status');
                toggleOtherField('study_country', 'other_country');
            }, 100);
        } catch (e) {
            console.warn('Could not load saved form data:', e);
        }
    }
    
    // Save data when fields change
    form.addEventListener('input', debounce((e) => {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // Don't save passwords and csrf tokens
            if (!key.includes('password') && !key.includes('csrf_token') && typeof value === 'string') {
                data[key] = value;
            }
        }
        
        // Save checkbox states separately
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            data[checkbox.name] = checkbox.checked;
        });
        
        localStorage.setItem('mentora_registration_draft', JSON.stringify(data));
    }, 1000));
}

// Helper debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const eyeIcon = document.getElementById(fieldId + '-eye');
    
    if (passwordField && eyeIcon) {
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            eyeIcon.classList.remove('fa-eye');
            eyeIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = 'password';
            eyeIcon.classList.remove('fa-eye-slash');
            eyeIcon.classList.add('fa-eye');
        }
    }
}

// Initialize nationality search functionality
function initializeNationalitySearch() {
    const searchInput = document.getElementById('nationality_search');
    const selectElement = document.getElementById('nationality');
    
    if (searchInput && selectElement) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const options = selectElement.querySelectorAll('option');
            
            options.forEach(option => {
                const text = option.textContent.toLowerCase();
                if (text.includes(searchTerm) || searchTerm === '') {
                    option.style.display = 'block';
                } else {
                    option.style.display = 'none';
                }
            });
            
            // If search matches exactly one option, select it
            const visibleOptions = Array.from(options).filter(option => 
                option.style.display !== 'none' && option.value !== ''
            );
            
            if (visibleOptions.length === 1 && searchTerm.length > 2) {
                selectElement.value = visibleOptions[0].value;
                toggleOtherField('nationality', 'other_nationality');
            }
        });
        
        // Clear search when selection is made
        selectElement.addEventListener('change', function() {
            if (this.value) {
                searchInput.value = this.options[this.selectedIndex].textContent;
            }
        });
    }
}

// reCAPTCHA validation
function validateRecaptcha() {
    // Check if reCAPTCHA is configured and loaded
    if (typeof grecaptcha === 'undefined') {
        return true; // Skip validation if reCAPTCHA is not configured
    }
    
    try {
        const recaptchaResponse = grecaptcha.getResponse();
        if (recaptchaResponse.length === 0) {
            showErrorMessage('Please complete the reCAPTCHA verification');
            return false;
        }
        return true;
    } catch (error) {
        console.warn('reCAPTCHA validation error:', error);
        return true; // Skip validation if there's an error
    }
}