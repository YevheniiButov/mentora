// JavaScript для мобильной авторизации
// Вставьте сюда код для авторизации 

// ===== МОБИЛЬНАЯ АВТОРИЗАЦИЯ =====
class MobileAuthController {
    constructor() {
        this.form = document.querySelector('.auth-form') || document.querySelector('.register-form');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.confirmPasswordInput = document.getElementById('confirm_password');
        this.firstNameInput = document.getElementById('first_name');
        this.lastNameInput = document.getElementById('last_name');
        this.termsCheckbox = document.getElementById('terms');
        this.submitButton = document.getElementById('loginButton') || document.getElementById('registerButton');
        this.passwordStrength = document.getElementById('passwordStrength');
        
        this.passwordToggles = document.querySelectorAll('.password-toggle');
        
        this.isRegistrationForm = this.form && this.form.classList.contains('register-form');
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        this.setupPasswordToggles();
        if (this.isRegistrationForm) {
            this.setupPasswordStrength();
        }
        this.setupFormValidation();
        this.setupFormSubmission();
        this.setupInputEnhancements();
        this.setupAccessibility();
    }
    
    setupPasswordToggles() {
        this.passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                const input = toggle.previousElementSibling;
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                
                const icon = toggle.querySelector('i');
                icon.className = `bi bi-${isPassword ? 'eye-slash' : 'eye'}`;
                
                toggle.setAttribute(
                    'aria-label', 
                    isPassword ? 'Hide password' : 'Show password'
                );
            });
        });
    }
    
    setupPasswordStrength() {
        if (!this.passwordInput || !this.passwordStrength) return;
        
        this.passwordInput.addEventListener('input', () => {
            this.updatePasswordStrength();
        });
        
        this.passwordInput.addEventListener('focus', () => {
            this.passwordStrength.style.display = 'block';
        });
    }
    
    updatePasswordStrength() {
        const password = this.passwordInput.value;
        const lengthReq = document.getElementById('lengthReq');
        const letterReq = document.getElementById('letterReq');
        const numberReq = document.getElementById('numberReq');
        const strengthBar = document.querySelector('.strength-bar');
        
        if (!lengthReq || !letterReq || !numberReq || !strengthBar) return;
        
        // Проверка требований
        const hasLength = password.length >= 8;
        const hasLetters = /[a-z]/.test(password) && /[A-Z]/.test(password);
        const hasNumber = /\d/.test(password);
        
        // Обновление индикаторов
        this.updateRequirement(lengthReq, hasLength);
        this.updateRequirement(letterReq, hasLetters);
        this.updateRequirement(numberReq, hasNumber);
        
        // Определение силы пароля
        const score = [hasLength, hasLetters, hasNumber].filter(Boolean).length;
        
        strengthBar.className = 'strength-bar';
        if (score === 1) {
            strengthBar.classList.add('strength-weak');
        } else if (score === 2) {
            strengthBar.classList.add('strength-medium');
        } else if (score === 3) {
            strengthBar.classList.add('strength-strong');
        }
    }
    
    updateRequirement(element, isMet) {
        const icon = element.querySelector('i');
        
        if (isMet) {
            element.classList.add('met');
            icon.className = 'bi bi-check-circle-fill';
        } else {
            element.classList.remove('met');
            icon.className = 'bi bi-x-circle';
        }
    }
    
    setupFormValidation() {
        // Валидация в реальном времени
        if (this.firstNameInput) {
            this.firstNameInput.addEventListener('blur', () => this.validateName(this.firstNameInput));
        }
        if (this.lastNameInput) {
            this.lastNameInput.addEventListener('blur', () => this.validateName(this.lastNameInput));
        }
        if (this.emailInput) {
            this.emailInput.addEventListener('blur', () => this.validateEmail());
        }
        if (this.passwordInput) {
            this.passwordInput.addEventListener('blur', () => this.validatePassword());
        }
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('blur', () => this.validatePasswordConfirm());
        }
        if (this.termsCheckbox) {
            this.termsCheckbox.addEventListener('change', () => this.validateTerms());
        }
    }
    
    validateName(input) {
        const name = input.value.trim();
        
        if (name.length === 0) {
            this.showFieldError(input, 'This field is required');
            return false;
        } else if (name.length < 2) {
            this.showFieldError(input, 'Name must be at least 2 characters');
            return false;
        } else if (!/^[a-zA-ZÀ-ÿĀ-žА-я\s'-]+$/.test(name)) {
            this.showFieldError(input, 'Name contains invalid characters');
            return false;
        } else {
            this.clearFieldError(input);
            input.classList.add('success');
            return true;
        }
    }
    
    validateEmail() {
        if (!this.emailInput) return true;
        
        const email = this.emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email.length === 0) {
            this.showFieldError(this.emailInput, 'Email is required');
            return false;
        } else if (!emailRegex.test(email)) {
            this.showFieldError(this.emailInput, 'Please enter a valid email address');
            return false;
        } else {
            this.clearFieldError(this.emailInput);
            this.emailInput.classList.add('success');
            return true;
        }
    }
    
    validatePassword() {
        if (!this.passwordInput) return true;
        
        const password = this.passwordInput.value;
        
        if (password.length === 0) {
            this.showFieldError(this.passwordInput, 'Password is required');
            return false;
        } else if (password.length < 6 && !this.isRegistrationForm) {
            this.showFieldError(this.passwordInput, 'Password must be at least 6 characters');
            return false;
        } else if (this.isRegistrationForm && password.length < 8) {
            this.showFieldError(this.passwordInput, 'Password must be at least 8 characters');
            return false;
        } else if (this.isRegistrationForm && !/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
            this.showFieldError(this.passwordInput, 'Password must contain uppercase, lowercase, and number');
            return false;
        } else {
            this.clearFieldError(this.passwordInput);
            this.passwordInput.classList.add('success');
            return true;
        }
    }
    
    validatePasswordConfirm() {
        if (!this.confirmPasswordInput) return true;
        
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        
        if (confirmPassword.length === 0) {
            this.showFieldError(this.confirmPasswordInput, 'Please confirm your password');
            return false;
        } else if (password !== confirmPassword) {
            this.showFieldError(this.confirmPasswordInput, 'Passwords do not match');
            return false;
        } else {
            this.clearFieldError(this.confirmPasswordInput);
            this.confirmPasswordInput.classList.add('success');
            return true;
        }
    }
    
    validateTerms() {
        if (!this.termsCheckbox) return true;
        
        if (!this.termsCheckbox.checked) {
            this.showToast('Please accept the terms and conditions', 'error');
            return false;
        }
        return true;
    }
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.remove('success');
        field.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        
        const container = field.parentElement.parentElement || field.parentElement;
        container.appendChild(errorDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('error', 'success');
        
        const container = field.parentElement.parentElement || field.parentElement;
        const existingError = container.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    setupFormSubmission() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });
    }
    
    async handleFormSubmit() {
        // Валидация формы
        let isFormValid = true;
        
        if (this.isRegistrationForm) {
            const isFirstNameValid = this.validateName(this.firstNameInput);
            const isLastNameValid = this.validateName(this.lastNameInput);
            const isEmailValid = this.validateEmail();
            const isPasswordValid = this.validatePassword();
            const isPasswordConfirmValid = this.validatePasswordConfirm();
            const isTermsValid = this.validateTerms();
            
            isFormValid = isFirstNameValid && isLastNameValid && isEmailValid && 
                         isPasswordValid && isPasswordConfirmValid && isTermsValid;
        } else {
            const isEmailValid = this.validateEmail();
            const isPasswordValid = this.validatePassword();
            
            isFormValid = isEmailValid && isPasswordValid;
        }
        
        if (!isFormValid) {
            this.showToast('Please correct the errors above', 'error');
            return;
        }
        
        // Показываем состояние загрузки
        this.setLoadingState(true);
        
        try {
            // Собираем данные формы
            const formData = new FormData(this.form);
            
            // Отправляем запрос
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const message = this.isRegistrationForm ? 
                    'Account created successfully! Redirecting...' : 
                    'Login successful! Redirecting...';
                this.showToast(message, 'success');
                
                // Перенаправляем через небольшую задержку для UX
                setTimeout(() => {
                    window.location.href = result.redirect_url || '/';
                }, this.isRegistrationForm ? 1500 : 1000);
                
            } else {
                this.showToast(result.message || 'Request failed. Please try again.', 'error');
                this.setLoadingState(false);
                
                // Показываем ошибки полей если есть
                if (result.errors) {
                    Object.keys(result.errors).forEach(fieldName => {
                        const field = document.getElementById(fieldName);
                        if (field) {
                            this.showFieldError(field, result.errors[fieldName]);
                        }
                    });
                }
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            this.showToast('Network error. Please check your connection.', 'error');
            this.setLoadingState(false);
        }
    }
    
    setLoadingState(loading) {
        if (!this.submitButton) return;
        
        this.submitButton.disabled = loading;
        
        if (loading) {
            this.submitButton.classList.add('loading');
        } else {
            this.submitButton.classList.remove('loading');
        }
    }
    
    setupInputEnhancements() {
        // Автофокус на первое поле при загрузке
        setTimeout(() => {
            const firstInput = this.firstNameInput || this.emailInput;
            if (firstInput && !firstInput.value) {
                firstInput.focus();
            }
        }, 500);
        
        // Enter для перехода между полями
        const inputs = [];
        if (this.firstNameInput) inputs.push(this.firstNameInput);
        if (this.lastNameInput) inputs.push(this.lastNameInput);
        if (this.emailInput) inputs.push(this.emailInput);
        if (this.passwordInput) inputs.push(this.passwordInput);
        if (this.confirmPasswordInput) inputs.push(this.confirmPasswordInput);
        
        inputs.forEach((input, index) => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const nextInput = inputs[index + 1];
                    if (nextInput) {
                        nextInput.focus();
                    } else if (this.termsCheckbox) {
                        this.termsCheckbox.focus();
                    } else if (this.submitButton) {
                        this.submitButton.focus();
                    }
                }
            });
        });
        
        // Анимации при фокусе
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.style.transform = 'translateY(-2px)';
            });
            
            input.addEventListener('blur', () => {
                input.parentElement.style.transform = 'translateY(0)';
            });
        });
    }
    
    setupAccessibility() {
        // Объявления для скринридеров
        this.form.addEventListener('submit', () => {
            const message = this.isRegistrationForm ? 
                'Creating your account, please wait...' : 
                'Signing in, please wait...';
            this.announceToScreenReader(message);
        });
        
        // Клавиатурная навигация для чекбокса условий
        if (this.termsCheckbox) {
            this.termsCheckbox.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    if (this.termsCheckbox.checked) {
                        this.submitButton.focus();
                    } else {
                        this.termsCheckbox.checked = true;
                        this.validateTerms();
                    }
                }
            });
        }
        
        // Клавиатурная навигация для социальных кнопок
        const socialButtons = document.querySelectorAll('.social-button');
        socialButtons.forEach(button => {
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });
        });
    }
    
    showToast(message, type = 'info', duration = 3000) {
        // Удаляем существующие уведомления
        const existingToasts = document.querySelectorAll('.auth-toast, .register-toast');
        existingToasts.forEach(toast => toast.remove());
        
        // Создаем новое уведомление
        const toast = document.createElement('div');
        toast.className = `${this.isRegistrationForm ? 'register' : 'auth'}-toast ${this.isRegistrationForm ? 'register' : 'auth'}-toast-${type}`;
        toast.textContent = message;
        
        // Стили
        const colors = {
            success: '#22c55e',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        toast.style.cssText = `
            position: fixed;
            top: calc(var(--header-height) + 1rem);
            left: 1rem;
            right: 1rem;
            background: ${colors[type] || colors.info};
            color: white;
            padding: 1rem;
            border-radius: 12px;
            font-weight: 500;
            text-align: center;
            z-index: 1000;
            transform: translateY(-100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        `;
        
        document.body.appendChild(toast);
        
        // Анимация появления
        requestAnimationFrame(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        });
        
        // Автоматическое скрытие
        setTimeout(() => {
            toast.style.transform = 'translateY(-100px)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }
    
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    window.mobileAuth = new MobileAuthController();
    
    // Обработка социальной авторизации
    const socialButtons = document.querySelectorAll('.social-button');
    socialButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Показываем индикатор загрузки
            button.style.opacity = '0.7';
            button.style.pointerEvents = 'none';
            
            // Перенаправляем на авторизацию
            setTimeout(() => {
                window.location.href = button.href;
            }, 300);
        });
    });
    
    // Стили для screen reader
    if (!document.getElementById('sr-only-styles')) {
        const style = document.createElement('style');
        style.id = 'sr-only-styles';
        style.textContent = `
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
        `;
        document.head.appendChild(style);
    }
}); 