/**
 * MENTORA - MAIN JAVASCRIPT FILE
 * Core functionality for the medical education platform
 */

// ===== GLOBAL CONFIGURATION =====
window.Mentora = {
    version: '1.0.0',
    debug: false,
    currentUser: null,
    csrfToken: null,
    
    // Initialize when DOM is ready
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeApp();
        });
    },
    
    // Main initialization
    initializeApp() {
        this.loadConfiguration();
        this.initializeComponents();
        this.bindEventListeners();
        this.log('Mentora initialized successfully');
    },
    
    // Load configuration from meta tags
    loadConfiguration() {
        this.csrfToken = this.getMetaContent('csrf-token');
        this.currentUser = JSON.parse(this.getMetaContent('user-data') || 'null');
        
        if (window.AppConfig) {
            this.currentLanguage = window.AppConfig.currentLanguage;
            this.isAuthenticated = window.AppConfig.isAuthenticated === 'true';
            this.userId = window.AppConfig.userId;
        }
    },
    
    // Initialize all components
    initializeComponents() {
        this.themeManager.init();
        this.navigationManager.init();
        this.flashMessages.init();
        this.loadingManager.init();
        this.formManager.init();
    },
    
    // Bind global event listeners
    bindEventListeners() {
        // Handle AJAX errors globally
        window.addEventListener('unhandledrejection', this.handleError.bind(this));
        
        // Handle navigation
        window.addEventListener('popstate', this.handlePopState.bind(this));
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    },
    
    // Utility functions
    getMetaContent(name) {
        const meta = document.querySelector(`meta[name="${name}"]`);
        return meta ? meta.getAttribute('content') : null;
    },
    
    log(message, level = 'info') {
        if (this.debug) {
            console[level](`[Mentora] ${message}`);
        }
    },
    
    // Error handling
    handleError(event) {
        this.log(`Unhandled error: ${event.reason}`, 'error');
        this.flashMessages.show('Произошла ошибка. Пожалуйста, попробуйте еще раз.', 'error');
    },
    
    handlePopState(event) {
        this.log('Navigation state changed');
    },
    
    handleVisibilityChange() {
        if (document.hidden) {
            this.log('Page hidden');
        } else {
            this.log('Page visible');
        }
    }
};

// ===== THEME MANAGER =====
Mentora.themeManager = {
    currentTheme: 'light',
    
    init() {
        this.loadSavedTheme();
        this.bindThemeButtons();
        Mentora.log('Theme manager initialized');
    },
    
    loadSavedTheme() {
        const savedTheme = localStorage.getItem('dental-academy-theme') || 'light';
        this.setTheme(savedTheme);
    },
    
    setTheme(theme) {
        const validThemes = ['light', 'dark', 'gradient'];
        if (!validThemes.includes(theme)) {
            theme = 'light';
        }
        
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('dental-academy-theme', theme);
        
        // Update theme buttons
        this.updateThemeButtons();
        
        Mentora.log(`Theme changed to: ${theme}`);
    },
    
    bindThemeButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme]')) {
                const theme = e.target.getAttribute('data-theme');
                this.setTheme(theme);
            }
        });
    },
    
    updateThemeButtons() {
        const buttons = document.querySelectorAll('[data-theme]');
        buttons.forEach(button => {
            const theme = button.getAttribute('data-theme');
            button.classList.toggle('active', theme === this.currentTheme);
        });
    }
};

// ===== NAVIGATION MANAGER =====
Mentora.navigationManager = {
    init() {
        this.bindMobileToggle();
        // Отключаем нашу реализацию выпадающих меню, чтобы использовать Bootstrap
        // this.bindDropdowns();
        this.highlightActiveLinks();
        Mentora.log('Navigation manager initialized');
    },
    
    bindMobileToggle() {
        // Отключено - используем простую реализацию в base.html

    },
    
    // Оставляем функцию, но не используем ее
    bindDropdowns() {
        /* 
        // Эта функция отключена, чтобы избежать конфликта с Bootstrap
        document.addEventListener('click', (e) => {
            // Закрываем все выпадающие меню при клике вне них
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
            
            // Открываем/закрываем выпадающее меню при клике на кнопку
            if (e.target.matches('[data-bs-toggle="dropdown"]') || e.target.closest('[data-bs-toggle="dropdown"]')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('[data-bs-toggle="dropdown"]');
                const dropdownId = button.getAttribute('id');
                const menu = document.querySelector(`[aria-labelledby="${dropdownId}"]`) || button.nextElementSibling;
                
                if (menu && menu.classList.contains('dropdown-menu')) {
                    // Закрываем другие открытые меню
                    document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
                        if (otherMenu !== menu) {
                            otherMenu.classList.remove('show');
                        }
                    });
                    
                    // Переключаем текущее меню
                    menu.classList.toggle('show');
                    
                    // Устанавливаем aria-expanded
                    button.setAttribute('aria-expanded', menu.classList.contains('show'));
                    
                    // Правильное позиционирование меню
                    if (menu.classList.contains('show')) {
                        const buttonRect = button.getBoundingClientRect();
                        const menuRect = menu.getBoundingClientRect();
                        
                        // Проверяем, не выходит ли меню за пределы экрана
                        if (buttonRect.left + menuRect.width > window.innerWidth) {
                            menu.style.left = 'auto';
                            menu.style.right = '0';
                        }
                    }
                }
            }
        });
        
        // Обработчик для закрытия меню по клавише Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
        */
    },
    
    highlightActiveLinks() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath === href) {
                link.classList.add('active');
            }
        });
    }
};

// ===== FLASH MESSAGES =====
Mentora.flashMessages = {
    container: null,
    
    init() {
        this.container = document.getElementById('flash-container');
        this.autoHideMessages();
        Mentora.log('Flash messages initialized');
    },
    
    show(message, type = 'info', duration = 5000) {
        if (!this.container) return;
        
        const messageElement = this.createMessage(message, type);
        this.container.appendChild(messageElement);
        
        // Trigger animation
        setTimeout(() => {
            messageElement.classList.add('show');
        }, 100);
        
        // Auto-hide
        if (duration > 0) {
            setTimeout(() => {
                this.hide(messageElement);
            }, duration);
        }
        
        return messageElement;
    },
    
    createMessage(message, type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `flash-message alert alert-${type === 'error' ? 'danger' : type}`;
        messageDiv.innerHTML = `
            <div class="flash-content">
                <div class="flash-icon">
                    <i class="${icons[type] || icons.info}"></i>
                </div>
                <div class="flash-text">${message}</div>
                <button type="button" class="flash-close">
                    <i class="bi bi-x"></i>
                </button>
            </div>
        `;
        
        // Bind close button
        messageDiv.querySelector('.flash-close').addEventListener('click', () => {
            this.hide(messageDiv);
        });
        
        return messageDiv;
    },
    
    hide(messageElement) {
        messageElement.classList.add('fade-out');
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 300);
    },
    
    autoHideMessages() {
        const existingMessages = document.querySelectorAll('.flash-message');
        existingMessages.forEach((message, index) => {
            // Show with delay for stacked effect
            setTimeout(() => {
                message.classList.add('show');
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    this.hide(message);
                }, 5000);
            }, index * 100);
        });
    }
};

// ===== LOADING MANAGER =====
Mentora.loadingManager = {
    indicator: null,
    
    init() {
        this.indicator = document.getElementById('loading-indicator');
        Mentora.log('Loading manager initialized');
    },
    
    show() {
        if (this.indicator) {
            this.indicator.classList.add('active');
        }
    },
    
    hide() {
        if (this.indicator) {
            this.indicator.classList.remove('active');
        }
    }
};

// ===== FORM MANAGER =====
Mentora.formManager = {
    init() {
        this.bindFormSubmissions();
        this.addCSRFTokens();
        Mentora.log('Form manager initialized');
    },
    
    bindFormSubmissions() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                this.handleFormSubmit(form);
            }
        });
    },
    
    handleFormSubmit(form) {
        // Add loading state
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            
            // Use translation if available, fallback to default
            const sendingText = (window.translations && window.translations.sending) || 'Sending...';
            submitBtn.textContent = sendingText;
            
            // Reset after 10 seconds (fallback)
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 10000);
        }
    },
    
    addCSRFTokens() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            if (!form.querySelector('input[name="csrf_token"]') && Mentora.csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = Mentora.csrfToken;
                form.appendChild(csrfInput);
            }
        });
    }
};

// ===== API HELPERS =====
Mentora.api = {
    async request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Mentora.csrfToken
            },
            credentials: 'same-origin'
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            Mentora.loadingManager.show();
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            Mentora.log(`API Error: ${error.message}`, 'error');
            throw error;
        } finally {
            Mentora.loadingManager.hide();
        }
    },
    
    async get(url) {
        return this.request(url);
    },
    
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// ===== UTILITY FUNCTIONS =====
Mentora.utils = {
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Format number with thousands separator
    formatNumber(num) {
        return new Intl.NumberFormat('ru-RU').format(num);
    },
    
    // Format time duration
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (hours > 0) {
            return `${hours}ч ${minutes}м`;
        }
        return `${minutes}м`;
    },
    
    // Copy text to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Mentora.flashMessages.show('Скопировано в буфер обмена', 'success');
        } catch (error) {
            Mentora.log('Copy to clipboard failed', 'error');
            Mentora.flashMessages.show('Не удалось скопировать', 'error');
        }
    }
};

// ===== SMOOTH SCROLLING =====
Mentora.scrollManager = {
    init() {
        this.bindSmoothScrolling();
    },
    
    bindSmoothScrolling() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (link) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    }
};

// ===== ANALYTICS =====
Mentora.analytics = {
    init() {
        this.trackPageView();
    },
    
    trackPageView() {
        // Simple page view tracking
        Mentora.log(`Page view: ${window.location.pathname}`);
    },
    
    trackEvent(action, category = 'general', label = '') {
        Mentora.log(`Event: ${category}/${action}${label ? '/' + label : ''}`);
    }
};

// ===== GLOBAL FUNCTIONS FOR BACKWARD COMPATIBILITY =====
window.setTheme = function(theme) {
    Mentora.themeManager.setTheme(theme);
};

window.showFlashMessage = function(message, type = 'info') {
    Mentora.flashMessages.show(message, type);
};

// ===== AUTO-INITIALIZATION =====
Mentora.init();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Mentora;
} 