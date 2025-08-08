/**
 * Glass Effects Controller для стеклянной темы
 * Добавляет эффекты матового стекла, анимации скролла и интерактивность
 */

class GlassEffects {
    constructor() {
        this.isActive = false;
        this.header = null;
        this.lastScrollY = 0;
        this.init();
    }

    init() {
        // Ждем загрузки DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.header = document.querySelector('.modern-header');
        
        // Инициализируем эффекты
        this.initHeaderScrollEffect();
        this.initGlassInteractions();
        this.initThemeWatcher();
        
        // console.log('🌈 Glass Effects инициализированы');
    }

    initThemeWatcher() {
        // Слушаем изменения темы
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    const theme = document.documentElement.getAttribute('data-theme');
                    this.isActive = theme === 'gradient';
                    
                    if (this.isActive) {
                        this.activateGlassEffects();
                    } else {
                        this.deactivateGlassEffects();
                    }
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });

        // Проверяем текущую тему
        const currentTheme = document.documentElement.getAttribute('data-theme');
        this.isActive = currentTheme === 'gradient';
    }

    initHeaderScrollEffect() {
        if (!this.header) return;

        let ticking = false;

        const handleScroll = () => {
            if (!this.isActive) return;

            const currentScrollY = window.scrollY;
            const isScrollingDown = currentScrollY > this.lastScrollY;
            
            // Добавляем класс при скролле
            if (currentScrollY > 50) {
                this.header.classList.add('scrolled');
            } else {
                this.header.classList.remove('scrolled');
            }
            
            // Применяем динамические эффекты стекла
            this.applyDynamicGlassEffect(currentScrollY);
            
            this.lastScrollY = currentScrollY;
        };

        const throttledScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', throttledScroll, { passive: true });
    }

    applyDynamicGlassEffect(scrollY) {
        if (!this.header || !this.isActive) return;

        const maxScroll = 300;
        const scrollProgress = Math.min(scrollY / maxScroll, 1);
        
        // Динамические значения для эффекта стекла
        const blurAmount = 20 + (scrollProgress * 15); // 20px -> 35px
        const opacity = 0.1 + (scrollProgress * 0.15); // 0.1 -> 0.25
        const saturation = 180 + (scrollProgress * 40); // 180% -> 220%
        
        // Применяем через CSS переменные
        this.header.style.setProperty('--dynamic-blur', `${blurAmount}px`);
        this.header.style.setProperty('--dynamic-opacity', opacity.toString());
        this.header.style.setProperty('--dynamic-saturation', `${saturation}%`);
    }

    initGlassInteractions() {
        // Делегируем события на document для динамически добавляемых элементов
        document.addEventListener('mouseenter', (e) => {
            if (!this.isActive || !e.target || typeof e.target.closest !== 'function') return;
            
            const element = e.target.closest('.modern-header .nav-link, .modern-header .btn, .modern-header .dropdown-toggle');
            if (element) {
                this.addGlassRippleEffect(element, e);
            }
        }, true);

        document.addEventListener('click', (e) => {
            if (!this.isActive || !e.target || typeof e.target.closest !== 'function') return;
            
            const element = e.target.closest('.modern-header .nav-link, .modern-header .btn');
            if (element) {
                this.addGlassClickEffect(element, e);
            }
        }, true);
    }

    addGlassRippleEffect(element, event) {
        // Эффект пульсации при наведении
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.className = 'glass-hover-ripple';
        ripple.style.cssText = `
            position: absolute;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
            transform: scale(0);
            animation: glassHoverRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 1;
        `;
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

    addGlassClickEffect(element, event) {
        // Эффект при клике
        const rect = element.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const clickRipple = document.createElement('div');
        clickRipple.className = 'glass-click-ripple';
        clickRipple.style.cssText = `
            position: absolute;
            left: ${x}px;
            top: ${y}px;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: rgba(255,255,255,0.6);
            transform: scale(0);
            animation: glassClickRipple 0.4s ease-out;
            pointer-events: none;
            z-index: 2;
        `;
        
        element.appendChild(clickRipple);
        
        setTimeout(() => {
            if (clickRipple.parentNode) {
                clickRipple.parentNode.removeChild(clickRipple);
            }
        }, 400);
    }

    activateGlassEffects() {
        // console.log('🌈 Активированы эффекты стекла');
        if (this.header) {
            this.header.classList.add('glass-active');
        }
    }

    deactivateGlassEffects() {
        // console.log('🌈 Деактивированы эффекты стекла');
        if (this.header) {
            this.header.classList.remove('glass-active', 'scrolled');
            // Сбрасываем CSS переменные
            this.header.style.removeProperty('--dynamic-blur');
            this.header.style.removeProperty('--dynamic-opacity');
            this.header.style.removeProperty('--dynamic-saturation');
        }
    }
}

// Создаем дополнительные CSS анимации
const glassAnimations = `
@keyframes glassHoverRipple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(1);
        opacity: 0;
    }
}

@keyframes glassClickRipple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(20);
        opacity: 0;
    }
}

/* Стили для активного состояния стекла */
.modern-header.glass-active {
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
`;

// Добавляем стили
const glassEffectsStyle = document.createElement('style');
glassEffectsStyle.textContent = glassAnimations;
document.head.appendChild(glassEffectsStyle);

// Автоинициализация
window.glassEffects = new GlassEffects();

// Экспорт для модульных систем
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GlassEffects;
} 