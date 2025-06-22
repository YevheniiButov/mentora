/**
 * DENTAL ACADEMY MOBILE APP
 * Базовые функции для мобильного приложения
 */

class MobileApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTouchGestures();
        this.setupProgressAnimations();
        this.setupCardInteractions();
        this.setupSearchFunctionality();
        this.setupFilterChips();
        this.setupNavTabs();
    }

    setupEventListeners() {
        // Обработка кликов по карточкам
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.mobile-card');
            if (card && !card.classList.contains('locked')) {
                this.handleCardClick(card);
            }
        });

        // Обработка кнопок действий
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.mobile-action-button');
            if (button) {
                this.handleButtonClick(button, e);
            }
        });
    }

    setupTouchGestures() {
        let startY = 0;
        let startX = 0;

        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            startX = e.touches[0].clientX;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            // Предотвращаем bounce эффект на iOS
            if (e.target.closest('.mobile-content')) {
                const deltaY = e.touches[0].clientY - startY;
                const deltaX = e.touches[0].clientX - startX;
                
                // Горизонтальные свайпы для навигации
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                    this.handleSwipe(deltaX > 0 ? 'right' : 'left');
                }
            }
        }, { passive: true });
    }

    setupProgressAnimations() {
        // Анимация прогресс-баров при появлении в viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target.querySelector('.mobile-progress-fill');
                    if (progressBar) {
                        const width = progressBar.dataset.progress || '0';
                        setTimeout(() => {
                            progressBar.style.width = width + '%';
                        }, 200);
                    }
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('.mobile-progress-bar').forEach(bar => {
            observer.observe(bar);
        });
    }

    setupCardInteractions() {
        // Добавляем ripple эффект к карточкам
        document.querySelectorAll('.mobile-card').forEach(card => {
            card.addEventListener('touchstart', (e) => {
                this.createRipple(e, card);
            });
        });
    }

    setupSearchFunctionality() {
        const searchInput = document.querySelector('.mobile-search-input');
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value);
                }, 300);
            });
        }
    }

    setupFilterChips() {
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                chip.classList.toggle('active');
                this.updateFilters();
            });
        });
    }

    setupNavTabs() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Убираем активное состояние у всех табов
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                // Добавляем активное состояние к кликнутому табу
                tab.classList.add('active');
                
                // Обновляем контент
                this.updateTabContent(tab.dataset.tab);
            });
        });
    }

    handleCardClick(card) {
        // Добавляем визуальную обратную связь
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);

        // Получаем URL из data-атрибута или href
        const url = card.dataset.href || card.querySelector('a')?.href;
        if (url) {
            // НЕ используем setTimeout для навигации - это может вызывать проблемы
            // Вместо этого позволяем браузеру обработать клик естественно
            
            // Если есть ссылка внутри карточки, кликаем на неё
            const link = card.querySelector('a');
            if (link) {
                // Позволяем стандартному клику сработать
                return;
            }
            
            // Иначе переходим программно без задержки
            window.location.href = url;
        }
    }

    handleButtonClick(button, event) {
        // Создаем ripple эффект
        this.createRipple(event, button);
        
        // Добавляем анимацию нажатия
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);
    }

    createRipple(event, element) {
        const ripple = document.createElement('div');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = (event.touches ? event.touches[0].clientX : event.clientX) - rect.left - size / 2;
        const y = (event.touches ? event.touches[0].clientY : event.clientY) - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-expand 0.6s ease-out;
            pointer-events: none;
            z-index: 1000;
        `;

        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    handleSwipe(direction) {
        console.log('Swipe detected:', direction);
        // Здесь можно добавить логику для навигации свайпами
    }

    performSearch(query) {
        const cards = document.querySelectorAll('.mobile-card[data-searchable]');
        
        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            card.style.display = matches ? 'block' : 'none';
            
            if (matches) {
                card.classList.add('fade-in-up');
            }
        });
    }

    updateFilters() {
        const activeFilters = Array.from(document.querySelectorAll('.filter-chip.active'))
            .map(chip => chip.dataset.filter);
        
        const cards = document.querySelectorAll('.mobile-card[data-category]');
        
        cards.forEach(card => {
            const category = card.dataset.category;
            const shouldShow = activeFilters.length === 0 || activeFilters.includes(category);
            
            card.style.display = shouldShow ? 'block' : 'none';
        });
    }

    updateTabContent(tabName) {
        // Скрываем все секции контента
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        
        // Показываем нужную секцию
        const targetContent = document.querySelector(`[data-tab-content="${tabName}"]`);
        if (targetContent) {
            targetContent.style.display = 'block';
            targetContent.classList.add('fade-in-up');
        }
    }

    showLoadingState(element) {
        const loader = document.createElement('div');
        loader.className = 'loading-overlay';
        loader.innerHTML = '<div class="spinner"></div>';
        
        element.style.position = 'relative';
        element.appendChild(loader);
    }

    // Утилиты для работы с прогрессом
    updateProgress(elementId, percentage) {
        const progressBar = document.querySelector(`#${elementId} .mobile-progress-fill`);
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.dataset.progress = percentage;
        }
    }

    // Показ уведомлений
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `mobile-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">${message}</div>
            <button class="notification-close">&times;</button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое удаление через 3 секунды
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // Ручное закрытие
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
}

// Добавляем стили для анимаций и компонентов
if (!document.getElementById('mobile-app-styles')) {
    const style = document.createElement('style');
    style.id = 'mobile-app-styles';
    style.textContent = `
        @keyframes ripple-expand {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: inherit;
        }
        
        .spinner {
            width: 24px;
            height: 24px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .mobile-notification {
            position: fixed;
            top: calc(var(--header-height) + 1rem);
            left: 1rem;
            right: 1rem;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 12px;
            padding: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            z-index: 1000;
            animation: slideInNotification 0.3s ease-out;
        }
        
        .mobile-notification.success {
            border-left: 4px solid var(--success);
        }
        
        .mobile-notification.error {
            border-left: 4px solid var(--error);
        }
        
        .mobile-notification.info {
            border-left: 4px solid var(--primary);
        }
        
        @keyframes slideInNotification {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileApp();
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileApp;
}

// Мобильное приложение
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация темы
    if (window.themeController) {
        // Добавляем переключатель темы в мобильную навигацию
        const themeToggle = document.querySelector('.mobile-theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                window.themeController.toggleTheme();
            });
        }
    }

    // Мобильная навигация
    const menuToggle = document.querySelector('#menu-toggle');
    const sidebar = document.querySelector('#mobile-sidebar');
    const sidebarOverlay = document.querySelector('#sidebar-overlay');
    const closeSidebar = document.querySelector('#close-sidebar');

    if (menuToggle && sidebar && sidebarOverlay) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });

        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });

        if (closeSidebar) {
            closeSidebar.addEventListener('click', () => {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            });
        }

        // Свайп для закрытия меню
        let startX = 0;
        sidebar.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });

        sidebar.addEventListener('touchmove', (e) => {
            const currentX = e.touches[0].clientX;
            const diff = startX - currentX;
            
            if (diff > 50) { // Свайп влево
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // Уведомления
    const notificationToggle = document.querySelector('#notifications-toggle');
    if (notificationToggle) {
        notificationToggle.addEventListener('click', () => {
            showNotification('Уведомления пока недоступны', 'info');
        });
    }

    // Предотвращение двойного тапа для зума
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(event) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            event.preventDefault();
        }
        lastTouchEnd = now;
    }, false);

    // Обработка тач-событий
    document.addEventListener('touchstart', function() {}, { passive: true });
});

// Функция для показа уведомлений
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.querySelector('#notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="bi bi-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;

    container.appendChild(notification);

    // Автоматическое удаление
    setTimeout(() => {
        notification.style.animation = 'slideOutUp 0.3s ease-in-out';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, duration);
}

// Получение иконки для уведомления
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || icons.info;
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        getNotificationIcon
    };
} 