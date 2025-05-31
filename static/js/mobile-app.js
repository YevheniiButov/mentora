// Mobile App Core JavaScript
// Базовая функциональность для мобильного приложения

class MobileApp {
    constructor() {
        this.isInitialized = false;
        this.config = window.MobileConfig || {};
        this.init();
    }

    init() {
        console.log('🚀 Initializing Mobile App...');
        
        this.setupEventListeners();
        this.setupNavigationHandlers();
        this.setupThemeToggle();
        this.setupToastSystem();
        this.setupMenuHandlers();
        
        this.isInitialized = true;
        console.log('✅ Mobile App initialized successfully');
    }

    setupEventListeners() {
        // Обработчики базовых событий
        document.addEventListener('DOMContentLoaded', () => {
            this.onDOMReady();
        });

        // Обработка изменения ориентации
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.handleOrientationChange(), 100);
        });

        // Обработка back button
        window.addEventListener('popstate', (event) => {
            this.handleBackButton(event);
        });
    }

    onDOMReady() {
        // Инициализация после загрузки DOM
        this.updateConnectionStatus();
        this.setupSwipeGestures();
        this.initLazyLoading();
    }

    setupNavigationHandlers() {
        // Мобильная навигация
        const navItems = document.querySelectorAll('.mobile-nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                this.handleNavigation(e, item);
            });
        });
    }

    setupThemeToggle() {
        const themeButtons = document.querySelectorAll('#mobile-theme-toggle, #mobile-theme-toggle-menu');
        
        themeButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.toggleTheme();
            });
        });

        // Устанавливаем начальную тему
        this.updateThemeIcons();
    }

    setupToastSystem() {
        // Система уведомлений
        this.toastContainer = this.createToastContainer();
    }

    setupMenuHandlers() {
        const menuToggle = document.getElementById('mobile-menu-toggle');
        const menuClose = document.getElementById('mobile-menu-close');
        const menuOverlay = document.getElementById('mobile-menu-overlay');

        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                this.openMenu();
            });
        }

        if (menuClose) {
            menuClose.addEventListener('click', () => {
                this.closeMenu();
            });
        }

        if (menuOverlay) {
            menuOverlay.addEventListener('click', (e) => {
                if (e.target === menuOverlay) {
                    this.closeMenu();
                }
            });
        }
    }

    // Навигация
    handleNavigation(event, item) {
        // Добавляем визуальный feedback
        item.style.transform = 'scale(0.95)';
        setTimeout(() => {
            item.style.transform = '';
        }, 150);

        // Обновляем активные состояния
        document.querySelectorAll('.mobile-nav-item').forEach(nav => {
            nav.classList.remove('active');
        });
        item.classList.add('active');
    }

    // Управление темой
    toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.updateThemeIcons();
        this.showToast(this.config.translations?.themeChanged || 'Theme changed', 'info');
    }

    updateThemeIcons() {
        const themeIcons = document.querySelectorAll('.theme-icon');
        const themeTexts = document.querySelectorAll('.theme-text');
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        
        themeIcons.forEach(icon => {
            icon.className = currentTheme === 'light' ? 'bi bi-moon theme-icon' : 'bi bi-sun theme-icon';
        });

        themeTexts.forEach(text => {
            text.textContent = currentTheme === 'light' ? 'Dark Mode' : 'Light Mode';
        });
    }

    // Меню
    openMenu() {
        const overlay = document.getElementById('mobile-menu-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
            setTimeout(() => {
                overlay.classList.add('show');
            }, 10);
        }
    }

    closeMenu() {
        const overlay = document.getElementById('mobile-menu-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 300);
        }
    }

    // Toast уведомления
    createToastContainer() {
        let container = document.getElementById('mobile-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'mobile-toast-container';
            container.className = 'mobile-toast-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `mobile-toast mobile-toast-${type}`;
        toast.innerHTML = `
            <div class="mobile-toast-content">
                <div class="mobile-toast-icon">
                    <i class="bi bi-${this.getToastIcon(type)}"></i>
                </div>
                <div class="mobile-toast-text">${message}</div>
            </div>
        `;
        
        toast.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            max-width: 300px;
            pointer-events: auto;
            transform: translateY(-20px);
            opacity: 0;
            transition: all 0.3s ease;
        `;

        this.toastContainer.appendChild(toast);

        // Анимация появления
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
            toast.style.opacity = '1';
        }, 100);

        // Удаление
        setTimeout(() => {
            toast.style.transform = 'translateY(-20px)';
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle-fill',
            'error': 'x-circle-fill',
            'warning': 'exclamation-triangle-fill',
            'info': 'info-circle-fill'
        };
        return icons[type] || 'info-circle-fill';
    }

    // Утилиты
    handleOrientationChange() {
        // Обработка изменения ориентации
        const overlay = document.getElementById('mobile-loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    handleBackButton(event) {
        // Обработка кнопки назад
        const overlay = document.getElementById('mobile-menu-overlay');
        if (overlay && overlay.classList.contains('show')) {
            event.preventDefault();
            this.closeMenu();
        }
    }

    updateConnectionStatus() {
        // Проверка подключения к интернету
        const updateStatus = () => {
            if (navigator.onLine) {
                this.hideConnectionError();
            } else {
                this.showConnectionError();
            }
        };

        window.addEventListener('online', updateStatus);
        window.addEventListener('offline', updateStatus);
        updateStatus();
    }

    showConnectionError() {
        this.showToast('Connection lost. Some features may not work.', 'warning', 5000);
    }

    hideConnectionError() {
        this.showToast('Connection restored', 'success', 2000);
    }

    setupSwipeGestures() {
        // Базовые свайп жесты (если понадобятся в будущем)
        let startX, startY;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;

            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const diffX = startX - endX;
            const diffY = startY - endY;

            // Обработка свайпов (можно расширить в будущем)
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    // Свайп влево
                } else {
                    // Свайп вправо
                }
            }
        });
    }

    initLazyLoading() {
        // Ленивая загрузка изображений
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback для старых браузеров
            images.forEach(img => {
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
            });
        }
    }

    // Публичные методы
    loading(show = true) {
        const overlay = document.getElementById('mobile-loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    refreshPage() {
        window.location.reload();
    }
}

// Инициализация при загрузке
if (typeof window !== 'undefined') {
    window.MobileApp = MobileApp;
    
    // Автоинициализация
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.mobileApp = new MobileApp();
        });
    } else {
        window.mobileApp = new MobileApp();
    }
}

// Экспорт для модульных систем
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileApp;
} 