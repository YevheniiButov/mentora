/* ===== ИСПРАВЛЕННАЯ СИСТЕМА FLASH СООБЩЕНИЙ ===== */
/* static/js/modern_flash_messages.js */

class ModernFlashMessages {
    constructor() {
        this.container = null;
        this.messages = new Map();
        this.maxMessages = 5;
        this.defaultDuration = 5000;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        // Создаем контейнер если его нет
        this.createContainer();
        
        // Обрабатываем существующие сообщения
        this.processExistingMessages();
        
        // Устанавливаем обработчики
        this.setupEventListeners();
        
        this.isInitialized = true;
    }

    createContainer() {
        // Ищем существующий контейнер
        this.container = document.getElementById('flash-container');
        
        if (!this.container) {
            // Создаем новый контейнер
            this.container = document.createElement('div');
            this.container.id = 'flash-container';
            this.container.className = 'flash-container';
            document.body.appendChild(this.container);
        }

        // Устанавливаем правильную позицию
        this.updateContainerPosition();
    }

    updateContainerPosition() {
        if (!this.container) return;
        
        const headerHeight = this.getHeaderHeight();
        
        // Применяем стили напрямую
        Object.assign(this.container.style, {
            position: 'fixed',
            top: `${headerHeight + 20}px`,
            right: '20px',
            zIndex: '1050',
            maxWidth: '400px',
            pointerEvents: 'none'
        });
    }

    getHeaderHeight() {
        const header = document.querySelector('.modern-header') || 
                      document.querySelector('header') || 
                      document.querySelector('.navbar');
        
        if (header) {
            return header.offsetHeight;
        }
        
        // Fallback значения
        return window.innerWidth <= 768 ? 60 : 70;
    }

    processExistingMessages() {
        if (!this.container) return;
        
        const existingMessages = this.container.querySelectorAll('.flash-message');
        existingMessages.forEach(message => {
            this.enhanceMessage(message);
            this.autoHideMessage(message);
        });
    }

    enhanceMessage(messageElement) {
        if (!messageElement || messageElement.dataset.enhanced) return;
        
        messageElement.style.pointerEvents = 'auto';
        messageElement.dataset.enhanced = 'true';
        
        // Добавляем кнопку закрытия если её нет
        if (!messageElement.querySelector('.flash-close')) {
            this.addCloseButton(messageElement);
        }
        
        // Добавляем анимацию появления
        setTimeout(() => {
            messageElement.classList.add('show');
        }, 10);
    }

    addCloseButton(messageElement) {
        const closeButton = document.createElement('button');
        closeButton.className = 'flash-close';
        closeButton.innerHTML = '<i class="bi bi-x"></i>';
        closeButton.onclick = () => this.hideMessage(messageElement);
        
        const content = messageElement.querySelector('.flash-content');
        if (content) {
            content.appendChild(closeButton);
        } else {
            messageElement.appendChild(closeButton);
        }
    }

    autoHideMessage(messageElement, duration = this.defaultDuration) {
        if (!messageElement) return;
        
        const messageId = this.generateMessageId();
        messageElement.dataset.messageId = messageId;
        
        // Сохраняем таймер
        const timer = setTimeout(() => {
            this.hideMessage(messageElement);
        }, duration);
        
        this.messages.set(messageId, {
            element: messageElement,
            timer: timer
        });
    }

    generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    showMessage(type, text, duration = this.defaultDuration) {
        if (!this.container) {
            this.createContainer();
        }

        // Проверяем лимит сообщений
        this.cleanupOldMessages();

        const messageElement = this.createMessageElement(type, text);
        this.container.appendChild(messageElement);
        
        this.enhanceMessage(messageElement);
        this.autoHideMessage(messageElement, duration);

        return messageElement;
    }

    createMessageElement(type, text) {
        const messageElement = document.createElement('div');
        messageElement.className = `flash-message alert alert-${type}`;
        
        const iconHtml = this.getIconForType(type);
        
        messageElement.innerHTML = `
            <div class="flash-content">
                <div class="flash-icon">${iconHtml}</div>
                <div class="flash-text">${text}</div>
            </div>
        `;

        return messageElement;
    }

    getIconForType(type) {
        const icons = {
            success: '<i class="bi bi-check-circle-fill"></i>',
            error: '<i class="bi bi-exclamation-triangle-fill"></i>',
            danger: '<i class="bi bi-exclamation-triangle-fill"></i>',
            warning: '<i class="bi bi-exclamation-circle-fill"></i>',
            info: '<i class="bi bi-info-circle-fill"></i>'
        };
        return icons[type] || icons.info;
    }

    hideMessage(messageElement) {
        if (!messageElement || messageElement.classList.contains('hiding')) return;
        
        messageElement.classList.add('hiding');
        
        // Очищаем таймер если есть
        const messageId = messageElement.dataset.messageId;
        if (messageId && this.messages.has(messageId)) {
            const messageData = this.messages.get(messageId);
            if (messageData.timer) {
                clearTimeout(messageData.timer);
            }
            this.messages.delete(messageId);
        }
        
        // Удаляем элемент после анимации
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 300);
    }

    cleanupOldMessages() {
        if (!this.container) return;
        
        const messages = this.container.querySelectorAll('.flash-message');
        if (messages.length >= this.maxMessages) {
            // Удаляем самое старое сообщение
            const oldestMessage = messages[0];
            if (oldestMessage) {
                this.hideMessage(oldestMessage);
            }
        }
    }

    setupEventListeners() {
        // Обновляем позицию при изменении размера окна
        const resizeHandler = () => {
            this.updateContainerPosition();
        };
        
        // Добавляем debounce для resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(resizeHandler, 100);
        });

        // Обновляем позицию при скролле (для мобильных браузеров)
        let scrollTimer;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                this.updateContainerPosition();
            }, 100);
        }, { passive: true });
    }

    // Публичные методы для совместимости
    success(text, duration) {
        return this.showMessage('success', text, duration);
    }

    error(text, duration) {
        return this.showMessage('error', text, duration);
    }

    warning(text, duration) {
        return this.showMessage('warning', text, duration);
    }

    info(text, duration) {
        return this.showMessage('info', text, duration);
    }

    // Очистка всех сообщений
    clearAll() {
        if (!this.container) return;
        
        const messages = this.container.querySelectorAll('.flash-message');
        messages.forEach(message => {
            this.hideMessage(message);
        });
        
        // Очищаем все таймеры
        this.messages.forEach(messageData => {
            if (messageData.timer) {
                clearTimeout(messageData.timer);
            }
        });
        this.messages.clear();
    }

    // Уничтожение экземпляра
    destroy() {
        this.clearAll();
        
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        
        this.isInitialized = false;
    }
}

// Создаем глобальный экземпляр только если его еще нет
if (typeof window.modernFlashMessages === 'undefined') {
    window.modernFlashMessages = new ModernFlashMessages();
}

// Экспортируем класс для использования
window.ModernFlashMessages = ModernFlashMessages;

// Совместимость с legacy кодом
window.showFlashMessage = function(type, message, duration) {
    return window.modernFlashMessages.showMessage(type, message, duration);
};

window.hideAllFlashMessages = function() {
    return window.modernFlashMessages.clearAll();
};

// Auto-init при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.modernFlashMessages && !window.modernFlashMessages.isInitialized) {
            window.modernFlashMessages.init();
        }
    });
} else {
    // DOM уже загружен
    if (window.modernFlashMessages && !window.modernFlashMessages.isInitialized) {
        window.modernFlashMessages.init();
    }
}