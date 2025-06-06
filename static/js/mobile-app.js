/**
 * Enhanced Mobile App Navigation System
 * Dental Academy Mobile Application
 */

class MobileApp {
    constructor() {
        this.isMenuOpen = false;
        this.isLanguageDropdownOpen = false;
        this.currentTheme = 'light';
        this.offlineMode = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTheme();
        this.setupServiceWorker();
        this.setupVibration();
    }
    
    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Боковое меню
        const menuToggle = document.getElementById('mobile-menu-toggle');
        const menuOverlay = document.getElementById('mobile-menu-overlay');
        const menuClose = document.getElementById('mobile-menu-close');
        
        if (menuToggle) {
            menuToggle.addEventListener('click', () => this.toggleMenu());
        }
        
        if (menuOverlay) {
            menuOverlay.addEventListener('click', (e) => {
                if (e.target === menuOverlay) {
                    this.closeMenu();
                }
            });
        }
        
        if (menuClose) {
            menuClose.addEventListener('click', () => this.closeMenu());
        }
        
        // Языковой селектор
        const langToggle = document.getElementById('mobile-language-toggle');
        const langDropdown = document.getElementById('mobile-language-dropdown');
        
        if (langToggle) {
            langToggle.addEventListener('click', () => this.toggleLanguageDropdown());
        }
        
        // Закрытие языкового меню при клике вне его
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.mobile-language-selector')) {
                this.closeLanguageDropdown();
            }
        });
        
        // Переключатель темы (в хедере)
        const themeToggle = document.getElementById('mobile-theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Переключатель темы (в меню)
        const themeToggleMenu = document.getElementById('mobile-theme-toggle-menu');
        if (themeToggleMenu) {
            themeToggleMenu.addEventListener('click', () => this.toggleTheme());
        }
        
        // Оффлайн режим
        const offlineToggle = document.getElementById('mobile-offline-mode');
        if (offlineToggle) {
            offlineToggle.addEventListener('click', () => this.toggleOfflineMode());
        }
        
        // Haptic feedback для всех кнопок
        this.setupHapticFeedback();
        
        // Обработка свайпов
        this.setupSwipeGestures();
        
        // Обработка состояния сети
        this.setupNetworkStatus();
    }
    
    /**
     * Управление боковым меню
     */
    toggleMenu() {
        if (this.isMenuOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }
    
    openMenu() {
        const overlay = document.getElementById('mobile-menu-overlay');
        if (overlay) {
            overlay.style.display = 'block';
            // Force reflow
            overlay.offsetHeight;
            overlay.classList.add('show');
            this.isMenuOpen = true;
            
            // Блокируем скролл страницы
            document.body.style.overflow = 'hidden';
            
            this.vibrate(10); // Легкая вибрация
        }
    }
    
    closeMenu() {
        const overlay = document.getElementById('mobile-menu-overlay');
        if (overlay) {
            overlay.classList.remove('show');
            this.isMenuOpen = false;
            
            // Восстанавливаем скролл
            document.body.style.overflow = '';
            
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 200);
        }
    }
    
    /**
     * Управление языковым селектором
     */
    toggleLanguageDropdown() {
        if (this.isLanguageDropdownOpen) {
            this.closeLanguageDropdown();
        } else {
            this.openLanguageDropdown();
        }
    }
    
    openLanguageDropdown() {
        const dropdown = document.getElementById('mobile-language-dropdown');
        if (dropdown) {
            dropdown.classList.add('show');
            this.isLanguageDropdownOpen = true;
            this.vibrate(5);
        }
    }
    
    closeLanguageDropdown() {
        const dropdown = document.getElementById('mobile-language-dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
            this.isLanguageDropdownOpen = false;
        }
    }
    
    /**
     * Управление темой
     */
    setupTheme() {
        // Получаем сохраненную тему
        const savedTheme = localStorage.getItem('mobile-theme') || 'light';
        this.setTheme(savedTheme);
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        this.vibrate(10);
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('mobile-theme', theme);
        
        // Обновляем иконки переключателя темы
        const themeIcons = document.querySelectorAll('.theme-icon');
        const themeIndicator = document.getElementById('theme-indicator');
        
        themeIcons.forEach(icon => {
            if (theme === 'dark') {
                icon.className = 'bi bi-sun theme-icon';
            } else {
                icon.className = 'bi bi-moon theme-icon';
            }
        });
        
        if (themeIndicator) {
            themeIndicator.textContent = theme === 'dark' ? 'Dark' : 'Light';
        }
        
        // Обновляем цвет статус-бара
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.content = theme === 'dark' ? '#111827' : '#3ECDC1';
        }
    }
    
    /**
     * Управление оффлайн режимом
     */
    toggleOfflineMode() {
        this.offlineMode = !this.offlineMode;
        const status = document.querySelector('.mobile-offline-status');
        
        if (status) {
            status.textContent = this.offlineMode ? 'On' : 'Off';
            status.style.background = this.offlineMode ? '#10b981' : '#6b7280';
        }
        
        // Здесь можно добавить логику кэширования контента
        if (this.offlineMode) {
            this.cacheImportantContent();
        }
        
        this.vibrate(15);
    }
    
    /**
     * Кэширование контента для оффлайн режима
     */
    async cacheImportantContent() {
        try {
            if ('caches' in window) {
                const cache = await caches.open('dental-academy-v1');
                const urlsToCache = [
                    '/',
                    '/static/css/mobile/mobile-base.css',
                    '/static/js/mobile-app.js',
                    '/static/images/logo.png'
                ];
                
                await cache.addAll(urlsToCache);
                console.log('Content cached for offline use');
            }
        } catch (error) {
            console.error('Error caching content:', error);
        }
    }
    
    /**
     * Настройка Service Worker для PWA
     */
    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
    }
    
    /**
     * Настройка haptic feedback
     */
    setupHapticFeedback() {
        const hapticElements = document.querySelectorAll(
            '.mobile-nav-item, .mobile-header-action, .mobile-btn, .mobile-menu-item'
        );
        
        hapticElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                this.vibrate(5);
            });
        });
    }
    
    /**
     * Настройка свайп-жестов
     */
    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Swipe right to open menu (from left edge)
            if (deltaX > 100 && Math.abs(deltaY) < 100 && startX < 50) {
                this.openMenu();
            }
            
            // Swipe left to close menu
            if (deltaX < -100 && Math.abs(deltaY) < 100 && this.isMenuOpen) {
                this.closeMenu();
            }
        });
    }
    
    /**
     * Мониторинг состояния сети
     */
    setupNetworkStatus() {
        const updateNetworkStatus = () => {
            const indicator = document.querySelector('.mobile-network-indicator');
            if (indicator) {
                if (navigator.onLine) {
                    indicator.className = 'mobile-network-indicator online';
                    indicator.textContent = 'Online';
                } else {
                    indicator.className = 'mobile-network-indicator offline';
                    indicator.textContent = 'Offline';
                }
            }
        };
        
        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        updateNetworkStatus();
    }
    
    /**
     * Вибрация (если поддерживается)
     */
    vibrate(duration = 10) {
        if ('vibrate' in navigator) {
            navigator.vibrate(duration);
        }
    }
    
    /**
     * Показ уведомлений
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `mobile-toast mobile-toast-${type} show`;
        
        toast.innerHTML = `
            <div class="mobile-toast-content">
                <div class="mobile-toast-icon">
                    <i class="bi bi-${this.getToastIcon(type)}"></i>
                </div>
                <div class="mobile-toast-text">${message}</div>
            </div>
        `;
        
        const container = document.querySelector('.mobile-flash-messages') || document.body;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    /**
     * Утилиты для навигации
     */
    navigateTo(url) {
        // Добавляем loading индикатор
        this.showLoading();
        window.location.href = url;
    }
    
    showLoading() {
        const loader = document.querySelector('.mobile-loading');
        if (loader) {
            loader.style.display = 'flex';
        }
    }
    
    hideLoading() {
        const loader = document.querySelector('.mobile-loading');
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.mobileApp = new MobileApp();
    
    // Скрываем loader при загрузке
    setTimeout(() => {
        window.mobileApp.hideLoading();
    }, 500);
});

// Экспорт для использования в других скриптах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileApp;
} 