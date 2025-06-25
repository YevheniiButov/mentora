// app-init.js - Инициализация всех компонентов страницы
class AppInitializer {
    constructor() {
        this.components = [];
        this.init();
    }
    
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
        });
    }
    
    initializeComponents() {
        // Инициализация анимации телефона
        this.initHeroAnimation();
        
        // Можно добавить другие компоненты
        // this.initThemeToggle();
        // this.initMobileMenu();
    }
    
    initHeroAnimation() {
        const phoneContainer = document.querySelector('.device-mockup');
        if (phoneContainer && typeof HeroPhoneAnimation !== 'undefined') {
            try {
                const heroAnimation = new HeroPhoneAnimation();
                // Сохраняем экземпляр глобально для доступа из других скриптов
                window.heroPhoneAnimation = heroAnimation;
                this.components.push(heroAnimation);
                console.log('✅ Hero phone animation initialized');
            } catch (error) {
                console.error('❌ Error initializing hero animation:', error);
                // Graceful degradation - показываем статичный первый экран
                this.showHeroFallback();
            }
        } else {
            console.log('ℹ️ Hero phone elements not found, skipping animation');
        }
    }
    
    showHeroFallback() {
        // Показываем первый экран статично если анимация не работает
        const screens = document.querySelectorAll('.screen-content');
        const indicators = document.querySelectorAll('.indicator');
        
        if (screens.length > 0) {
            screens[0].style.display = 'block';
            screens[0].style.opacity = '1';
        }
        
        if (indicators.length > 0) {
            indicators[0].classList.add('active');
        }
        
        console.log('🔄 Hero animation fallback applied');
    }
    
    // Метод для очистки компонентов при необходимости
    destroy() {
        this.components.forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        console.log('🧹 App components destroyed');
    }
}

// Автоматическая инициализация
new AppInitializer(); 