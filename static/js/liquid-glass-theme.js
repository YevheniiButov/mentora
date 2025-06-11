/**
 * iOS 26 Liquid Glass Theme Controller
 * Управление темной темой с поддержкой Liquid Glass эффектов
 */

class LiquidGlassTheme {
    constructor() {
        this.THEME_KEY = 'liquid-glass-theme';
        this.ANIMATION_DURATION = 300;
        this.currentTheme = this.getCurrentTheme();
        this.isTransitioning = false;
        
        this.init();
    }
    
    init() {
        console.log('🌙 Initializing iOS 26 Liquid Glass Theme System...');
        
        // Применяем сохраненную тему
        this.applyTheme(this.currentTheme, false);
        
        // Настраиваем слушатели
        this.setupThemeToggle();
        this.setupSystemThemeListener();
        this.setupAnimationEnhancements();
        
        console.log('✅ Liquid Glass Theme System ready!');
    }
    
    getCurrentTheme() {
        // Проверяем сохраненную тему
        const savedTheme = localStorage.getItem(this.THEME_KEY);
        if (savedTheme && ['light', 'dark'].includes(savedTheme)) {
            return savedTheme;
        }
        
        // Возвращаем системную тему по умолчанию
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    applyTheme(theme, animated = true) {
        if (this.isTransitioning && animated) return;
        
        console.log(`🌙 Switching to ${theme} theme...`);
        
        if (animated) {
            this.isTransitioning = true;
            this.addTransitionEffect();
        }
        
        // Применяем тему
        document.documentElement.setAttribute('data-theme', theme);
        
        // Обновляем мета-тег для мобильных устройств
        this.updateThemeColor(theme);
        
        // Обновляем состояние переключателей
        this.updateThemeToggles(theme);
        
        // Запускаем специальные эффекты для темной темы
        if (theme === 'dark') {
            this.enableLiquidGlassEffects();
        } else {
            this.disableLiquidGlassEffects();
        }
        
        // Сохраняем настройку
        this.currentTheme = theme;
        localStorage.setItem(this.THEME_KEY, theme);
        
        // Уведомляем другие компоненты
        this.dispatchThemeChangeEvent(theme);
        
        if (animated) {
            setTimeout(() => {
                this.isTransitioning = false;
                this.removeTransitionEffect();
            }, this.ANIMATION_DURATION);
        }
    }
    
    addTransitionEffect() {
        // Добавляем класс для плавного перехода
        document.documentElement.classList.add('theme-transitioning');
        
        // Создаем эффект "liquid wave" для перехода
        const wave = document.createElement('div');
        wave.className = 'liquid-transition-wave';
        wave.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at center, 
                rgba(62, 205, 193, 0.1) 0%, 
                transparent 70%);
            pointer-events: none;
            z-index: 9999;
            opacity: 0;
            animation: liquidWave 0.6s ease-out forwards;
        `;
        
        // Добавляем CSS анимацию если её нет
        if (!document.querySelector('#liquid-wave-styles')) {
            const style = document.createElement('style');
            style.id = 'liquid-wave-styles';
            style.textContent = `
                @keyframes liquidWave {
                    0% { 
                        opacity: 0;
                        transform: scale(0);
                    }
                    50% { 
                        opacity: 1;
                        transform: scale(1.2);
                    }
                    100% { 
                        opacity: 0;
                        transform: scale(2);
                    }
                }
                
                .theme-transitioning * {
                    transition: background-color 0.3s ease, 
                               color 0.3s ease, 
                               border-color 0.3s ease,
                               box-shadow 0.3s ease !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(wave);
        
        // Удаляем эффект после анимации
        setTimeout(() => {
            if (wave.parentNode) {
                wave.parentNode.removeChild(wave);
            }
        }, 600);
    }
    
    removeTransitionEffect() {
        document.documentElement.classList.remove('theme-transitioning');
    }
    
    enableLiquidGlassEffects() {
        // Включаем специальные Liquid Glass эффекты для темной темы
        document.body.classList.add('liquid-glass-active');
        
        // Добавляем интерактивные эффекты свечения для карточек
        this.enhanceCards();
        
        // Добавляем эффекты движения для навигации
        this.enhanceNavigation();
        
        // Активируем частицы
        this.activateParticles();
    }
    
    disableLiquidGlassEffects() {
        document.body.classList.remove('liquid-glass-active');
        this.deactivateParticles();
    }
    
    enhanceCards() {
        const cards = document.querySelectorAll('.liquid-card, .mobile-card, .subject-card, .module-card');
        
        cards.forEach(card => {
            // Добавляем эффект следования курсора
            card.addEventListener('mousemove', this.handleCardMouseMove.bind(this));
            card.addEventListener('mouseleave', this.handleCardMouseLeave.bind(this));
        });
    }
    
    handleCardMouseMove(e) {
        if (this.currentTheme !== 'dark') return;
        
        const card = e.currentTarget;
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Создаем эффект света следующего за курсором
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;
        
        card.style.transform = `perspective(1000px) rotateY(${deltaX * 5}deg) rotateX(${-deltaY * 5}deg) translateZ(10px)`;
        
        // Добавляем светящееся пятно
        let glowSpot = card.querySelector('.liquid-glow-spot');
        if (!glowSpot) {
            glowSpot = document.createElement('div');
            glowSpot.className = 'liquid-glow-spot';
            glowSpot.style.cssText = `
                position: absolute;
                width: 200px;
                height: 200px;
                background: radial-gradient(circle, rgba(62, 205, 193, 0.3) 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
                z-index: 1;
            `;
            card.style.position = 'relative';
            card.appendChild(glowSpot);
        }
        
        glowSpot.style.left = (x - 100) + 'px';
        glowSpot.style.top = (y - 100) + 'px';
        glowSpot.style.opacity = '1';
    }
    
    handleCardMouseLeave(e) {
        const card = e.currentTarget;
        card.style.transform = '';
        
        const glowSpot = card.querySelector('.liquid-glow-spot');
        if (glowSpot) {
            glowSpot.style.opacity = '0';
        }
    }
    
    enhanceNavigation() {
        const navItems = document.querySelectorAll('.nav-item, .liquid-nav-item, .mobile-nav-item');
        
        navItems.forEach(item => {
            item.addEventListener('click', this.createRippleEffect.bind(this));
        });
    }
    
    createRippleEffect(e) {
        const element = e.currentTarget;
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(62, 205, 193, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: liquidRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 0;
        `;
        
        // Добавляем CSS для анимации волны
        if (!document.querySelector('#liquid-ripple-styles')) {
            const style = document.createElement('style');
            style.id = 'liquid-ripple-styles';
            style.textContent = `
                @keyframes liquidRipple {
                    to {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
    
    activateParticles() {
        // Создаем фоновые частицы для темной темы
        if (document.querySelector('.liquid-particles')) return;
        
        const particlesContainer = document.createElement('div');
        particlesContainer.className = 'liquid-particles';
        particlesContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        `;
        
        // Создаем частицы
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'liquid-particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(62, 205, 193, ${Math.random() * 0.3 + 0.1});
                border-radius: 50%;
                animation: liquidFloat ${Math.random() * 10 + 10}s linear infinite;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
            `;
            particlesContainer.appendChild(particle);
        }
        
        // Добавляем CSS для анимации частиц
        if (!document.querySelector('#liquid-particles-styles')) {
            const style = document.createElement('style');
            style.id = 'liquid-particles-styles';
            style.textContent = `
                @keyframes liquidFloat {
                    0%, 100% {
                        transform: translateY(0px) rotate(0deg);
                        opacity: 0;
                    }
                    10%, 90% {
                        opacity: 1;
                    }
                    50% {
                        transform: translateY(-20px) rotate(180deg);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(particlesContainer);
    }
    
    deactivateParticles() {
        const particles = document.querySelector('.liquid-particles');
        if (particles) {
            particles.remove();
        }
    }
    
    updateThemeColor(theme) {
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.content = theme === 'dark' ? '#1c1c1e' : '#3ECDC1';
        }
    }
    
    updateThemeToggles(theme) {
        const toggles = document.querySelectorAll('[data-theme-toggle], .theme-toggle, .theme-toggle-inline');
        toggles.forEach(toggle => {
            const icon = toggle.querySelector('.theme-icon, i');
            if (icon) {
                icon.className = `theme-icon bi ${theme === 'dark' ? 'bi-sun-fill' : 'bi-moon-fill'}`;
            }
        });
    }
    
    setupThemeToggle() {
        // Настраиваем все переключатели темы
        const toggles = document.querySelectorAll('[data-theme-toggle], .theme-toggle, .theme-toggle-inline');
        
        toggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        });
    }
    
    setupSystemThemeListener() {
        // Слушаем изменения системной темы для режима auto
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            if (this.currentTheme === 'auto') {
                this.applyTheme('auto', true);
            }
        });
    }
    
    setupAnimationEnhancements() {
        // Улучшаем стандартные анимации
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('liquid-animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        // Наблюдаем за карточками для анимации появления
        document.querySelectorAll('.liquid-card, .mobile-card, .subject-card').forEach(card => {
            observer.observe(card);
        });
    }
    
    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme, true);
    }
    
    setTheme(theme) {
        if (['light', 'dark'].includes(theme)) {
            this.applyTheme(theme, true);
        }
    }
    
    dispatchThemeChangeEvent(theme) {
        const event = new CustomEvent('themechange', {
            detail: { theme, isLiquidGlass: theme === 'dark' }
        });
        window.dispatchEvent(event);
    }
    
    // Публичные методы для API
    getTheme() {
        return this.currentTheme;
    }
    
    isDark() {
        return this.currentTheme === 'dark';
    }
    
    isLight() {
        return !this.isDark();
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.liquidGlassTheme = new LiquidGlassTheme();
});

// Экспортируем класс для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LiquidGlassTheme;
}

// Добавляем дополнительные CSS стили для анимаций
const additionalStyles = `
    .liquid-animate-in {
        animation: liquidSlideIn 0.6s ease-out forwards;
    }
    
    @keyframes liquidSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .liquid-glass-active .liquid-card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .liquid-glass-active .liquid-btn:hover {
        animation: liquidPulse 2s ease-in-out infinite;
    }
    
    @keyframes liquidPulse {
        0%, 100% {
            box-shadow: var(--shadow-lg);
        }
        50% {
            box-shadow: var(--shadow-xl), var(--glow-primary);
        }
    }
`;

// Добавляем стили в head
if (!document.querySelector('#liquid-glass-theme-styles')) {
    const style = document.createElement('style');
    style.id = 'liquid-glass-theme-styles';
    style.textContent = additionalStyles;
    document.head.appendChild(style);
} 