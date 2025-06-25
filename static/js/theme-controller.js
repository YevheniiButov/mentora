class ThemeController {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        this.init();
    }

    init() {
        // Устанавливаем начальную тему
        this.setTheme(this.theme);

        // Слушаем изменения системной темы
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (this.theme === 'system') {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });

        // Добавляем переключатель темы в DOM
        this.addThemeToggle();

        // Инициализируем эффекты скролла для стеклянной темы
        this.initGlassEffects();
    }

    setTheme(theme) {
        // Сохраняем выбор пользователя
        this.theme = theme;
        localStorage.setItem('theme', theme);

        // Применяем тему
        if (theme === 'system') {
            document.documentElement.setAttribute('data-theme', this.systemTheme);
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }

        // Обновляем иконку переключателя
        this.updateToggleIcon();

        // Уведомляем о изменении темы
        this.notifyThemeChange();
    }

    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    addThemeToggle() {
        // Создаем переключатель темы
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle';
        toggle.setAttribute('aria-label', 'Toggle theme');
        toggle.innerHTML = this.getToggleIcon();

        // Добавляем обработчик
        toggle.addEventListener('click', () => this.toggleTheme());

        // Добавляем в DOM
        const header = document.querySelector('.header');
        if (header) {
            header.appendChild(toggle);
        }
    }

    getToggleIcon() {
        return this.theme === 'light' 
            ? '<i class="bi bi-moon-fill"></i>'
            : '<i class="bi bi-sun-fill"></i>';
    }

    updateToggleIcon() {
        const toggle = document.querySelector('.theme-toggle');
        if (toggle) {
            toggle.innerHTML = this.getToggleIcon();
        }
    }

    notifyThemeChange() {
        // Создаем и отправляем событие
        const event = new CustomEvent('themechange', {
            detail: { theme: this.theme }
        });
        window.dispatchEvent(event);
    }

    initGlassEffects() {
        // Эффект скролла для стеклянной шапки
        this.initHeaderScrollEffect();
        
        // Дополнительные эффекты для стеклянной темы
        this.initGlassInteractions();
    }

    initHeaderScrollEffect() {
        let lastScrollY = window.scrollY;
        let isScrollingDown = false;
        
        const header = document.querySelector('.modern-header');
        if (!header) return;

        const handleScroll = () => {
            const currentScrollY = window.scrollY;
            isScrollingDown = currentScrollY > lastScrollY;
            
            // Добавляем класс 'scrolled' при скролле вниз
            if (currentScrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            
            // Дополнительные эффекты для градиентной темы
            const currentTheme = document.documentElement.getAttribute('data-theme');
            if (currentTheme === 'gradient') {
                this.applyGlassScrollEffects(header, currentScrollY, isScrollingDown);
            }
            
            lastScrollY = currentScrollY;
        };

        // Throttle функция для оптимизации
        let ticking = false;
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

    applyGlassScrollEffects(header, scrollY, isScrollingDown) {
        // Динамическое изменение прозрачности и размытия
        const maxScroll = 200;
        const scrollProgress = Math.min(scrollY / maxScroll, 1);
        
        // Увеличиваем эффект матового стекла при скролле
        const blurAmount = 20 + (scrollProgress * 10); // от 20px до 30px
        const opacity = 0.1 + (scrollProgress * 0.1); // от 0.1 до 0.2
        const saturation = 180 + (scrollProgress * 20); // от 180% до 200%
        
        header.style.setProperty('--glass-blur', `${blurAmount}px`);
        header.style.setProperty('--glass-opacity', opacity);
        header.style.setProperty('--glass-saturation', `${saturation}%`);
        
        // Применяем стили
        const glassStyle = `
            rgba(255, 255, 255, ${opacity}) !important
        `;
        const backdropStyle = `
            blur(${blurAmount}px) saturate(${saturation}%) !important
        `;
        
        header.style.background = glassStyle;
        header.style.backdropFilter = backdropStyle;
        header.style.webkitBackdropFilter = backdropStyle;
    }

    initGlassInteractions() {
        // Добавляем интерактивные эффекты для элементов навигации
        const navLinks = document.querySelectorAll('.modern-header .nav-link, .modern-header .btn');
        
        navLinks.forEach(link => {
            // Эффект пульсации при наведении
            link.addEventListener('mouseenter', (e) => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                if (currentTheme === 'gradient') {
                    this.addGlassRippleEffect(e.target);
                }
            });
        });
    }

    addGlassRippleEffect(element) {
        // Создаем эффект пульсации
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        
        const ripple = document.createElement('span');
        ripple.className = 'glass-ripple';
        ripple.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
            transform: translate(-50%, -50%);
            animation: glassRipple 0.6s ease-out;
            pointer-events: none;
            z-index: 1;
        `;
        
        element.appendChild(ripple);
        
        // Удаляем эффект после анимации
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
}

// Инициализация контроллера
document.addEventListener('DOMContentLoaded', () => {
    window.themeController = new ThemeController();
});

// Дополнительные стили для анимаций
const themeControllerStyles = `
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
const themeControllerStylesElement = document.createElement('style');
themeControllerStylesElement.textContent = themeControllerStyles;
document.head.appendChild(themeControllerStylesElement);

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeController;
} 