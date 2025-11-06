/**
 * Diagnostic Core
 * Основные функции и утилиты для системы BIG диагностики
 */

class DiagnosticCore {
    constructor() {
        this.currentSession = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindGlobalEvents();
        this.setupGlobalFunctions();
    }

    bindGlobalEvents() {
        // Обработка глобальных событий
        document.addEventListener('keydown', (e) => this.handleGlobalKeyboard(e));
        
        // Обработка видимости страницы
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
        
        // Обработка ухода со страницы
        window.addEventListener('beforeunload', (e) => this.handleBeforeUnload(e));
    }

    setupGlobalFunctions() {
        // Делаем функции доступными глобально
        window.showLoading = this.showLoading.bind(this);
        window.hideLoading = this.hideLoading.bind(this);
        window.showModal = this.showModal.bind(this);
        window.hideModal = this.hideModal.bind(this);
        window.showNotification = this.showNotification.bind(this);
    }

    // ===== LOADING FUNCTIONS =====

    showLoading(message = 'Загрузка...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            const spinner = overlay.querySelector('.loading-spinner p');
            if (spinner) {
                spinner.textContent = message;
            }
            overlay.style.display = 'flex';
        }
        this.isLoading = true;
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        this.isLoading = false;
    }

    // ===== MODAL FUNCTIONS =====

    showModal(title, content, buttons = []) {
        const modal = document.getElementById('modal-container');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const modalFooter = document.getElementById('modal-footer');

        if (!modal || !modalTitle || !modalBody || !modalFooter) {
            console.error('Modal elements not found');
            return;
        }

        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        
        modalFooter.innerHTML = '';
        buttons.forEach(button => {
            const btn = document.createElement('button');
            btn.className = `btn ${button.class || 'btn-secondary'}`;
            btn.textContent = button.text;
            btn.onclick = button.onclick;
            modalFooter.appendChild(btn);
        });

        modal.style.display = 'flex';
        
        // Фокус на первую кнопку
        const firstButton = modalFooter.querySelector('.btn');
        if (firstButton) {
            firstButton.focus();
        }
    }

    hideModal() {
        const modal = document.getElementById('modal-container');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // ===== NOTIFICATION FUNCTIONS =====

    showNotification(message, type = 'info', duration = 5000) {
        const notification = this.createNotificationElement(message, type);
        document.body.appendChild(notification);

        // Анимация появления
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Автоматическое скрытие
        setTimeout(() => {
            this.hideNotification(notification);
        }, duration);
    }

    createNotificationElement(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="notification-icon ${this.getNotificationIcon(type)}"></i>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        return notification;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    // ===== PROGRESS FUNCTIONS =====

    updateProgress(percentage, current, total) {
        const progressFill = document.querySelector('.progress-fill');
        const progressInfo = document.querySelector('.progress-info');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressInfo) {
            progressInfo.innerHTML = `
                <span>Вопрос ${current} из ${total}</span>
                <span>${percentage}% завершено</span>
            `;
        }
    }

    // ===== API FUNCTIONS =====

    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    }

    // ===== VALIDATION FUNCTIONS =====

    validateAnswer(answer) {
        if (!answer || answer.trim() === '') {
            return { valid: false, message: 'Пожалуйста, выберите ответ' };
        }
        return { valid: true };
    }

    validateSession() {
        // Проверка активности сессии
        const sessionTimeout = 30 * 60 * 1000; // 30 минут
        const lastActivity = sessionStorage.getItem('lastActivity');
        
        if (lastActivity) {
            const timeSinceLastActivity = Date.now() - parseInt(lastActivity);
            if (timeSinceLastActivity > sessionTimeout) {
                return { valid: false, message: 'Сессия истекла. Пожалуйста, начните заново.' };
            }
        }
        
        return { valid: true };
    }

    // ===== UTILITY FUNCTIONS =====

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

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
    }

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
    }

    // ===== EVENT HANDLERS =====

    handleGlobalKeyboard(event) {
        // Глобальные горячие клавиши
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 's':
                    event.preventDefault();
                    this.saveProgress();
                    break;
                case 'n':
                    event.preventDefault();
                    this.nextQuestion();
                    break;
                case 'p':
                    event.preventDefault();
                    this.previousQuestion();
                    break;
            }
        }
    }

    handleVisibilityChange() {
        if (document.hidden) {
            // Страница скрыта - сохраняем прогресс
            this.saveProgress();
        } else {
            // Страница снова видна - обновляем активность
            sessionStorage.setItem('lastActivity', Date.now().toString());
        }
    }

    handleBeforeUnload(event) {
        if (this.isLoading) {
            event.preventDefault();
            event.returnValue = 'Идет загрузка. Вы уверены, что хотите покинуть страницу?';
            return event.returnValue;
        }
    }

    // ===== NAVIGATION FUNCTIONS =====

    saveProgress() {
        // Сохранение прогресса (реализация зависит от конкретной страницы)

    }

    nextQuestion() {
        // Переход к следующему вопросу (реализация зависит от конкретной страницы)

    }

    previousQuestion() {
        // Переход к предыдущему вопросу (реализация зависит от конкретной страницы)

    }

    // ===== ANALYTICS FUNCTIONS =====

    trackEvent(eventName, data = {}) {
        // Отправка аналитических данных
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, data);
        }
        
        // Локальное логирование

    }

    trackPageView(pageName) {
        this.trackEvent('page_view', { page_name: pageName });
    }

    trackUserAction(action, details = {}) {
        this.trackEvent('user_action', { action, ...details });
    }
}

// ===== GLOBAL UTILITY FUNCTIONS =====

// Функция для форматирования чисел
function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

// Функция для форматирования дат
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return new Intl.DateTimeFormat('ru-RU', { ...defaultOptions, ...options }).format(date);
}

// Функция для генерации уникального ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Функция для проверки поддержки функций браузера
function checkBrowserSupport() {
    const support = {
        fetch: typeof fetch !== 'undefined',
        localStorage: typeof localStorage !== 'undefined',
        sessionStorage: typeof sessionStorage !== 'undefined',
        serviceWorker: 'serviceWorker' in navigator,
        webGL: (() => {
            try {
                const canvas = document.createElement('canvas');
                return !!(window.WebGLRenderingContext && 
                    (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
            } catch (e) {
                return false;
            }
        })()
    };
    
    return support;
}

// Функция для определения типа устройства
function getDeviceType() {
    const ua = navigator.userAgent;
    
    if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
        return 'tablet';
    }
    
    if (/mobile|android|iphone|ipod|blackberry|opera mini|iemobile/i.test(ua)) {
        return 'mobile';
    }
    
    return 'desktop';
}

// ===== INITIALIZATION =====

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Создаем глобальный экземпляр DiagnosticCore
    window.diagnosticCore = new DiagnosticCore();
    
    // Обновляем время последней активности
    sessionStorage.setItem('lastActivity', Date.now().toString());
    
    // Отслеживаем просмотр страницы
    const pageName = document.title || window.location.pathname;
    window.diagnosticCore.trackPageView(pageName);

});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DiagnosticCore;
} 