/**
 * Mobile Navigation System
 * Обеспечивает плавные переходы и единообразную навигацию
 */
class MobileNavigation {
    constructor() {
        this.currentPage = window.location.pathname;
        this.isTransitioning = false;
        this.init();
    }
    
    init() {
        console.log('🚀 Mobile Navigation - инициализация...');
        
        // Основные функции
        this.setupBottomNavigation();
        this.setupPageTransitions();
        this.setupBackButton();
        this.setupThemeToggle();
        this.setupProfileMenu();
        
        // Предзагрузка ключевых страниц
        this.preloadPages();
        
        // Обновляем активную навигацию
        this.updateActiveNavigation();
        
        console.log('✅ Mobile Navigation - готово!');
    }
    
    setupBottomNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const targetUrl = item.getAttribute('href');
                const targetPage = item.getAttribute('data-page');
                
                // НЕ блокируем переходы на внешние страницы (AI, и т.д.)
                if (targetUrl && (targetUrl.includes('/ai-assistant') || targetUrl.includes('/ai/') || 
                    targetUrl.includes('/virtual-patient') || targetUrl.includes('/admin'))) {
                    // Позволяем стандартный переход
                    return;
                }
                
                // НЕ блокируем стандартную навигацию - это может вызывать проблемы
                // e.preventDefault();
                
                if (this.isTransitioning) {
                    e.preventDefault();
                    return;
                }
                
                // Проверяем, не на той ли странице уже находимся
                if (targetUrl && this.isCurrentPage(targetUrl)) {
                    e.preventDefault();
                    return;
                }
                
                // Добавляем визуальную обратную связь, но НЕ блокируем переход
                this.addVisualFeedback(item);
                
                // Обновляем активную навигацию без блокировки перехода
                this.updateActiveNavigationFor(targetPage);
            });
            
            // Добавляем тактильную обратную связь
            this.addHapticFeedback(item);
        });
    }
    
    isCurrentPage(url) {
        const currentPath = window.location.pathname;
        return currentPath === url || currentPath.includes(url.split('/').pop());
    }
    
    navigateToPage(url, page) {
        console.log(`📱 Переход на: ${url} (${page})`);
        
        this.isTransitioning = true;
        
        // Обновляем активную навигацию
        this.updateActiveNavigationFor(page);
        
        // Анимация перехода
        this.animatePageTransition(() => {
            // Загружаем новую страницу
            this.loadPage(url);
        });
    }
    
    updateActiveNavigation() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            item.classList.remove('active');
            
            const itemHref = item.getAttribute('href');
            const itemPage = item.getAttribute('data-page');
            
            // Логика определения активной страницы
            if (this.isActivePageFor(currentPath, itemPage, itemHref)) {
                item.classList.add('active');
            }
        });
    }
    
    isActivePageFor(currentPath, page, href) {
        // Специальная логика для каждой страницы
        switch(page) {
            case 'home':
                return currentPath.includes('/mobile') && !currentPath.includes('/learning') 
                       && !currentPath.includes('/tests') && !currentPath.includes('/virtual-patient');
            case 'learning':
                return currentPath.includes('/learning') || currentPath.includes('/subject') 
                       || currentPath.includes('/lesson') || currentPath.includes('/module');
            case 'tests':
                return currentPath.includes('/tests') || currentPath.includes('/test');
            case 'patients':
                return currentPath.includes('/virtual-patient');
            case 'ai':
                return currentPath.includes('/ai');
            default:
                return currentPath === href;
        }
    }
    
    updateActiveNavigationFor(page) {
        // Убираем активный класс у всех
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Добавляем активный класс к текущей
        const activeItem = document.querySelector(`[data-page="${page}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
    
    animatePageTransition(callback) {
        const content = document.getElementById('mainContent');
        
        if (!content) {
            callback();
            return;
        }
        
        // Анимация исчезновения
        content.style.transform = 'translateX(-100%)';
        content.style.opacity = '0';
        
        setTimeout(() => {
            callback();
        }, 300);
    }
    
    loadPage(url) {
        // Простое перенаправление (можно заменить на AJAX загрузку)
        window.location.href = url;
    }
    
    setupPageTransitions() {
        // Восстанавливаем контент при возврате
        const content = document.getElementById('mainContent');
        if (content) {
            content.style.transform = 'translateX(0)';
            content.style.opacity = '1';
        }
    }
    
    setupBackButton() {
        const backBtn = document.querySelector('.back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', (e) => {
                // Проверяем есть ли у кнопки href
                const href = backBtn.getAttribute('href');
                if (href && href !== '#') {
                    // Позволяем стандартную навигацию по href
                    return;
                }
                
                // Только если нет href или он пустой - делаем preventDefault
                e.preventDefault();
                this.goBack();
            });
            
            this.addHapticFeedback(backBtn);
        }
    }
    
    goBack() {
        console.log('⬅️ Возврат назад');
        
        // Определяем куда возвращаться
        const currentPath = window.location.pathname;
        
        if (currentPath.includes('/lesson/') || currentPath.includes('/module/')) {
            // Из урока/модуля - в карту обучения
            const lang = this.extractLangFromPath(currentPath);
            window.location.href = `/${lang}/mobile/learning`;
        } else if (currentPath.includes('/subject/')) {
            // Из предмета - в карту обучения
            const lang = this.extractLangFromPath(currentPath);
            window.location.href = `/${lang}/mobile/learning`;
        } else {
            // По умолчанию - браузерная история
            window.history.back();
        }
    }
    
    extractLangFromPath(path) {
        const parts = path.split('/');
        return parts[1] || 'en';
    }
    
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
            
            this.addHapticFeedback(themeToggle);
        }
        
        // Применяем сохраненную тему
        const savedTheme = localStorage.getItem('mobile_theme') || 'light';
        this.applyTheme(savedTheme);
    }
    
    toggleTheme() {
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        this.applyTheme(newTheme);
        localStorage.setItem('mobile_theme', newTheme);
        
        console.log(`🎨 Тема изменена: ${currentTheme} → ${newTheme}`);
    }
    
    applyTheme(theme) {
        document.body.setAttribute('data-theme', theme);
        
        // Обновляем мета-тег цвета браузера
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', 
                theme === 'dark' ? '#0f172a' : '#1a1a2e'
            );
        }
    }
    
    setupProfileMenu() {
        const profileMenu = document.getElementById('profileMenu');
        if (profileMenu) {
            profileMenu.addEventListener('click', () => {
                this.showProfileMenu();
            });
            
            this.addHapticFeedback(profileMenu);
        }
    }
    
    showProfileMenu() {
        // Простое меню (можно расширить)
        const currentLang = this.extractLangFromPath(window.location.pathname);
        const isAuthenticated = document.querySelector('.nav-item') !== null; // Примерная проверка
        
        if (isAuthenticated) {
            window.location.href = `/${currentLang}/mobile/profile`;
        } else {
            window.location.href = `/${currentLang}/mobile/auth/login`;
        }
    }
    
    preloadPages() {
        const currentLang = this.extractLangFromPath(window.location.pathname);
        
        // Ключевые страницы для предзагрузки
        const keyPages = [
            `/${currentLang}/mobile/learning`,
            `/${currentLang}/mobile/tests`, 
            `/${currentLang}/virtual-patient`,
            `/${currentLang}/ai-assistant`
        ];
        
        keyPages.forEach(page => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = page;
            document.head.appendChild(link);
        });
        
        console.log('🔄 Предзагрузка страниц запущена');
    }
    
    addHapticFeedback(element) {
        element.addEventListener('touchstart', () => {
            // Тактильная обратная связь для поддерживающих устройств
            // Проверяем что было взаимодействие с пользователем
            if (navigator.vibrate && document.hasStoredUserActivation) {
                navigator.vibrate(50);
            }
            
            // Добавляем визуальную обратную связь
            element.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                element.style.transform = '';
            }, 150);
        }, { passive: true });
    }
    
    addVisualFeedback(element) {
        // Добавляем визуальный эффект нажатия
        element.style.transform = 'scale(0.95)';
        element.style.opacity = '0.8';
        
        setTimeout(() => {
            element.style.transform = '';
            element.style.opacity = '';
        }, 150);
    }
}

// Глобальная функция для кнопки назад (для совместимости)
function goBack() {
    if (window.mobileNav) {
        window.mobileNav.goBack();
    } else {
        window.history.back();
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    window.mobileNav = new MobileNavigation();
});

// Обновляем навигацию при возврате через браузер
window.addEventListener('popstate', () => {
    if (window.mobileNav) {
        setTimeout(() => {
            window.mobileNav.updateActiveNavigation();
        }, 100);
    }
});

console.log('📱 Navigation.js загружен'); 