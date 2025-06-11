class LiquidGlassThemeController {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.isTransitioning = false;
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme, false);
        this.setupEventListeners();
        this.initializeAnimations();
        this.updateMetaThemeColor();
    }

    setupEventListeners() {
        // Переключатель темы
        const themeToggle = document.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
                this.setTheme(newTheme);
            });
        }

        // Автоматическое переключение по системным настройкам
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                if (!this.getStoredTheme()) {
                    this.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }

        // Меню
        this.setupMenuEvents();
        
        // Уведомления
        this.setupNotificationEvents();
    }

    setupMenuEvents() {
        const menuToggle = document.querySelector('#menu-toggle');
        const sidebar = document.querySelector('#mobile-sidebar');
        const sidebarOverlay = document.querySelector('#sidebar-overlay');
        const closeSidebar = document.querySelector('#close-sidebar');

        if (menuToggle && sidebar && sidebarOverlay) {
            menuToggle.addEventListener('click', () => {
                this.toggleSidebar(true);
            });

            sidebarOverlay.addEventListener('click', () => {
                this.toggleSidebar(false);
            });

            if (closeSidebar) {
                closeSidebar.addEventListener('click', () => {
                    this.toggleSidebar(false);
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
                    this.toggleSidebar(false);
                }
            });
        }
    }

    setupNotificationEvents() {
        const notificationToggle = document.querySelector('#notifications-toggle');
        if (notificationToggle) {
            notificationToggle.addEventListener('click', () => {
                this.showNotification('Уведомления пока недоступны', 'info');
            });
        }
    }

    toggleSidebar(show) {
        const sidebar = document.querySelector('#mobile-sidebar');
        const overlay = document.querySelector('#sidebar-overlay');

        if (sidebar && overlay) {
            if (show) {
                sidebar.classList.add('active');
                overlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    }

    setTheme(theme) {
        if (this.isTransitioning) return;
        
        this.isTransitioning = true;
        this.currentTheme = theme;
        this.applyTheme(theme, true);
        this.storeTheme(theme);
        this.triggerThemeChangeEvent(theme);
        
        setTimeout(() => {
            this.isTransitioning = false;
        }, 300);
    }

    applyTheme(theme, animated = true) {
        if (animated) {
            document.body.classList.add('theme-transitioning');
        }

        document.documentElement.setAttribute('data-theme', theme);
        this.updateMetaThemeColor();
        
        // Обновляем переключатель
        const themeToggle = document.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.setAttribute('aria-label', 
                theme === 'dark' ? 'Переключить на светлую тему' : 'Переключить на темную тему'
            );
        }

        if (animated) {
            setTimeout(() => {
                document.body.classList.remove('theme-transitioning');
            }, 300);
        }
    }

    updateMetaThemeColor() {
        const metaThemeColor = document.querySelector('#theme-color-meta');
        if (metaThemeColor) {
            metaThemeColor.content = this.currentTheme === 'dark' ? '#1c1c1e' : '#3ECDC1';
        }
    }

    initializeAnimations() {
        // Intersection Observer для анимаций
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Наблюдаем за элементами с glass эффектами
        document.querySelectorAll('.glass-card').forEach(el => {
            observer.observe(el);
        });
    }

    showNotification(message, type = 'info', duration = 3000) {
        const container = document.querySelector('#notification-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi bi-${this.getNotificationIcon(type)}"></i>
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

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    getStoredTheme() {
        return localStorage.getItem('dental-academy-theme');
    }

    getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    storeTheme(theme) {
        localStorage.setItem('dental-academy-theme', theme);
    }

    triggerThemeChangeEvent(theme) {
        window.dispatchEvent(new CustomEvent('themeChange', { 
            detail: { theme } 
        }));
    }
}

// Дополнительные стили для анимаций
const additionalStyles = `
@keyframes slideOutUp {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(-100%);
        opacity: 0;
    }
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.notification-content i {
    font-size: 18px;
}
`;

// Добавляем стили
const style = document.createElement('style');
style.textContent = additionalStyles;
document.head.appendChild(style);

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    window.themeController = new LiquidGlassThemeController();
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LiquidGlassThemeController;
} 