/**
 * JavaScript для отслеживания посетителей страниц регистрации
 */

class RegistrationTracker {
    constructor() {
        this.pageType = this.detectPageType();
        this.startTime = Date.now();
        this.emailEntered = false;
        this.nameEntered = false;
        this.formStarted = false;
        this.trackingActive = true;
        
        this.init();
    }
    
    detectPageType() {
        const path = window.location.pathname;
        if (path.includes('/quick-register')) return 'quick_register';
        if (path.includes('/register')) return 'full_register';
        if (path.includes('/login')) return 'login';
        return 'unknown';
    }
    
    init() {
        // Отслеживаем заход на страницу
        this.trackPageVisit();
        
        // Отслеживаем выход со страницы
        this.trackPageExit();
        
        // Отслеживаем ввод email
        this.trackEmailInput();
        
        // Отслеживаем ввод имени
        this.trackNameInput();
        
        // Отслеживаем начало заполнения формы
        this.trackFormStart();
        
        // Отслеживаем отправку формы
        this.trackFormSubmit();
    }
    
    async trackPageVisit() {
        try {
            const response = await fetch('/track-registration-visit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_type: this.pageType,
                    language: document.documentElement.lang || 'en'
                })
            });
            
            if (response.ok) {
                console.log('✅ Page visit tracked');
            }
        } catch (error) {
            console.error('❌ Error tracking page visit:', error);
        }
    }
    
    trackEmailInput() {
        const emailInputs = document.querySelectorAll('input[type="email"], input[name="email"]');
        
        emailInputs.forEach(input => {
            let timeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                
                // Ждем 2 секунды после остановки ввода
                timeout = setTimeout(() => {
                    if (e.target.value && e.target.value.includes('@')) {
                        this.trackEmailEntry(e.target.value);
                    }
                }, 2000);
            });
        });
    }
    
    trackNameInput() {
        const firstNameInputs = document.querySelectorAll('input[name="first_name"], input[name="firstName"], input[id="first_name"], input[id="firstName"]');
        const lastNameInputs = document.querySelectorAll('input[name="last_name"], input[name="lastName"], input[id="last_name"], input[id="lastName"]');
        
        // Отслеживаем поля имени
        [...firstNameInputs, ...lastNameInputs].forEach(input => {
            let timeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(timeout);
                
                // Ждем 2 секунды после остановки ввода
                timeout = setTimeout(() => {
                    const firstName = this.getValueByName('first_name') || this.getValueByName('firstName') || this.getValueById('first_name') || this.getValueById('firstName');
                    const lastName = this.getValueByName('last_name') || this.getValueByName('lastName') || this.getValueById('last_name') || this.getValueById('lastName');
                    
                    if (firstName && lastName && firstName.length > 1 && lastName.length > 1) {
                        this.trackNameEntry(firstName, lastName);
                    }
                }, 2000);
            });
        });
    }
    
    getValueByName(name) {
        const input = document.querySelector(`input[name="${name}"]`);
        return input ? input.value.trim() : null;
    }
    
    getValueById(id) {
        const input = document.getElementById(id);
        return input ? input.value.trim() : null;
    }
    
    async trackEmailEntry(email) {
        if (this.emailEntered) return;
        
        try {
            this.emailEntered = true;
            
            const response = await fetch('/track-email-entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    email: email,
                    page_type: this.pageType
                })
            });
            
            if (response.ok) {
                console.log('✅ Email entry tracked:', email);
            }
        } catch (error) {
            console.error('❌ Error tracking email entry:', error);
        }
    }
    
    async trackNameEntry(firstName, lastName) {
        if (this.nameEntered) return;
        
        try {
            this.nameEntered = true;
            
            const response = await fetch('/track-name-entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    first_name: firstName,
                    last_name: lastName,
                    page_type: this.pageType
                })
            });
            
            if (response.ok) {
                console.log('✅ Name entry tracked:', firstName, lastName);
            }
        } catch (error) {
            console.error('❌ Error tracking name entry:', error);
        }
    }
    
    trackFormStart() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    this.trackFormStart();
                });
            });
        });
    }
    
    async trackFormStart() {
        if (this.formStarted) return;
        
        try {
            this.formStarted = true;
            
            const response = await fetch('/track-form-start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_type: this.pageType
                })
            });
            
            if (response.ok) {
                console.log('✅ Form start tracked');
            }
        } catch (error) {
            console.error('❌ Error tracking form start:', error);
        }
    }
    
    trackFormSubmit() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.trackFormSubmit();
            });
        });
    }
    
    async trackFormSubmit() {
        try {
            const response = await fetch('/track-form-submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_type: this.pageType
                })
            });
            
            if (response.ok) {
                console.log('✅ Form submit tracked');
            }
        } catch (error) {
            console.error('❌ Error tracking form submit:', error);
        }
    }
    
    trackPageExit() {
        // Отслеживаем уход со страницы
        window.addEventListener('beforeunload', () => {
            this.trackPageExit();
        });
        
        // Отслеживаем неактивность (пользователь ушел, но не закрыл вкладку)
        let inactivityTimer;
        const inactivityThreshold = 30000; // 30 секунд
        
        const resetInactivityTimer = () => {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                if (this.formStarted && !document.hidden) {
                    this.trackFormAbandonment();
                }
            }, inactivityThreshold);
        };
        
        // Сбрасываем таймер при активности
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
            document.addEventListener(event, resetInactivityTimer, true);
        });
        
        resetInactivityTimer();
    }
    
    async trackFormAbandonment() {
        try {
            const response = await fetch('/track-form-abandonment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_type: this.pageType
                })
            });
            
            if (response.ok) {
                console.log('✅ Form abandonment tracked');
            }
        } catch (error) {
            console.error('❌ Error tracking form abandonment:', error);
        }
    }
    
    async trackPageExit() {
        try {
            const timeOnPage = Math.round((Date.now() - this.startTime) / 1000);
            
            const response = await fetch('/track-page-exit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    page_type: this.pageType,
                    time_on_page: timeOnPage
                })
            });
            
            if (response.ok) {
                console.log('✅ Page exit tracked');
            }
        } catch (error) {
            console.error('❌ Error tracking page exit:', error);
        }
    }
    
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Инициализируем трекер на страницах регистрации
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('/register') || 
        window.location.pathname.includes('/login') ||
        window.location.pathname.includes('/quick-register')) {
        
        window.registrationTracker = new RegistrationTracker();
        console.log('🔍 Registration tracker initialized');
    }
});
