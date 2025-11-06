/**
 * Mobile Enhancements for Mentora
 * Улучшения мобильного опыта
 */

class MobileEnhancements {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth > 768 && window.innerWidth <= 1024;
        this.init();
    }

    init() {
        this.setupMobileMenu();
        this.setupTouchEnhancements();
        this.setupScrollOptimizations();
        this.setupOrientationHandling();
        this.setupPerformanceOptimizations();
    }

    /**
     * Улучшенное мобильное меню
     * ОТКЛЮЧЕНО: Конфликтует с инициализацией в base.html
     */
    setupMobileMenu() {
        // Мобильное меню теперь инициализируется в base.html
        // Этот код отключен чтобы избежать конфликтов

        return;
        
        /* ОТКЛЮЧЕННЫЙ КОД - КОНФЛИКТУЕТ С BASE.HTML
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (!navbarToggler || !navbarCollapse) return;

        // Улучшенная анимация hamburger menu
        navbarToggler.addEventListener('click', () => {
            const isExpanded = navbarToggler.getAttribute('aria-expanded') === 'true';
            
            // Плавная анимация открытия/закрытия
            if (!isExpanded) {
                navbarCollapse.style.display = 'block';
                setTimeout(() => {
                    navbarCollapse.classList.add('show');
                }, 10);
            } else {
                navbarCollapse.classList.remove('show');
                setTimeout(() => {
                    navbarCollapse.style.display = 'none';
                }, 300);
            }
        });

        // Закрытие меню при клике вне его
        document.addEventListener('click', (e) => {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarToggler.setAttribute('aria-expanded', 'false');
                navbarCollapse.classList.remove('show');
            }
        });

        // Закрытие меню при клике на ссылку
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navbarToggler.setAttribute('aria-expanded', 'false');
                navbarCollapse.classList.remove('show');
            });
        });
        */
    }

    /**
     * Улучшения для touch взаимодействий
     */
    setupTouchEnhancements() {
        if (!this.isMobile) return;

        // Улучшенные touch targets
        const touchElements = document.querySelectorAll(`
            .learning-path-button,
            .subject-card,
            .module-card-compact,
            .step-card,
            .vp-card,
            .stat-card,
            .recommendation-item,
            .nav-link,
            .nav-button,
            .btn
        `);

        touchElements.forEach(element => {
            // Добавляем haptic feedback для iOS
            element.addEventListener('touchstart', () => {
                if (navigator.vibrate) {
                    navigator.vibrate(10);
                }
            });

            // Улучшенные active состояния
            element.addEventListener('touchstart', () => {
                element.style.transform = 'scale(0.98)';
            });

            element.addEventListener('touchend', () => {
                element.style.transform = '';
            });

            // Предотвращаем двойной тап для зума (кроме ссылок навигации)
            element.addEventListener('touchend', (e) => {
                // НЕ блокируем события для ссылок навигации
                if (element.tagName === 'A' || element.classList.contains('nav-link') || element.closest('.navbar-collapse')) {
                    return;
                }
                e.preventDefault();
            });
        });
    }

    /**
     * Оптимизации скролла
     */
    setupScrollOptimizations() {
        if (!this.isMobile) return;

        // Плавный скролл для мобильных
        const scrollElements = document.querySelectorAll(`
            .middle-column,
            .right-column,
            .navbar-collapse
        `);

        scrollElements.forEach(element => {
            element.style.webkitOverflowScrolling = 'touch';
            element.style.scrollBehavior = 'smooth';
        });

        // Оптимизация скролла для Learning Map
        const learningMapContainer = document.querySelector('.learning-map-container');
        if (learningMapContainer) {
            learningMapContainer.addEventListener('scroll', this.throttle(() => {
                // Оптимизация производительности при скролле
                requestAnimationFrame(() => {
                    // Дополнительные оптимизации если нужны
                });
            }, 16));
        }
    }

    /**
     * Обработка изменения ориентации
     */
    setupOrientationHandling() {
        window.addEventListener('orientationchange', () => {
            // Пересчитываем размеры после изменения ориентации
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });

        window.addEventListener('resize', this.throttle(() => {
            this.handleOrientationChange();
        }, 250));
    }

    handleOrientationChange() {
        const isLandscape = window.innerWidth > window.innerHeight;
        const learningMapContainer = document.querySelector('.learning-map-container');
        
        if (learningMapContainer) {
            if (isLandscape && this.isMobile) {
                learningMapContainer.style.marginTop = '60px';
                learningMapContainer.style.padding = '0.75rem';
            } else {
                learningMapContainer.style.marginTop = '80px';
                learningMapContainer.style.padding = '1rem';
            }
        }

        // Обновляем размеры мобильного меню
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse) {
            if (isLandscape && this.isMobile) {
                navbarCollapse.style.maxHeight = '60vh';
            } else {
                navbarCollapse.style.maxHeight = 'calc(100vh - 100%)';
            }
        }
    }

    /**
     * Оптимизации производительности
     */
    setupPerformanceOptimizations() {
        if (!this.isMobile) return;

        // Оптимизация анимаций для мобильных
        const animatedElements = document.querySelectorAll(`
            .learning-path-button,
            .subject-card,
            .module-card-compact,
            .step-card,
            .vp-card,
            .stat-card,
            .recommendation-item
        `);

        animatedElements.forEach(element => {
            element.style.willChange = 'transform';
            element.style.transform = 'translateZ(0)';
        });

        // Оптимизация изображений для мобильных
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (this.isMobile) {
                img.loading = 'lazy';
            }
        });
    }

    /**
     * Утилита для throttling
     */
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    /**
     * Улучшенная обработка ошибок
     */
    handleErrors() {
        window.addEventListener('error', (e) => {
            console.error('Mobile Enhancement Error:', e.error);
        });

        window.addEventListener('unhandledrejection', (e) => {
            console.error('Mobile Enhancement Promise Error:', e.reason);
        });
    }
}

/**
 * Инициализация улучшений при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', () => {
    // Инициализируем улучшения
    const mobileEnhancements = new MobileEnhancements();
    
    // Обработка ошибок
    mobileEnhancements.handleErrors();
    
    // Добавляем в глобальную область для отладки
    window.mobileEnhancements = mobileEnhancements;
});

/**
 * Дополнительные улучшения для Learning Map
 */
class LearningMapMobileEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupLearningMapOptimizations();
        this.setupCardInteractions();
        this.setupProgressIndicators();
    }

    /**
     * Оптимизации для Learning Map на мобильных
     */
    setupLearningMapOptimizations() {
        const learningMapContainer = document.querySelector('.learning-map-container');
        if (!learningMapContainer) return;

        // Оптимизация layout для мобильных
        if (window.innerWidth <= 768) {
            learningMapContainer.style.gridTemplateColumns = '1fr';
            learningMapContainer.style.gap = '1rem';
        }

        // Улучшенная обработка скролла
        learningMapContainer.addEventListener('scroll', this.throttle(() => {
            // Оптимизация производительности
            requestAnimationFrame(() => {
                // Дополнительные оптимизации
            });
        }, 16));
    }

    /**
     * Улучшенные взаимодействия с карточками
     */
    setupCardInteractions() {
        const cards = document.querySelectorAll(`
            .learning-path-button,
            .subject-card,
            .module-card-compact
        `);

        cards.forEach(card => {
            // Улучшенные hover эффекты для touch
            card.addEventListener('touchstart', () => {
                card.style.transform = 'scale(0.98)';
                card.style.transition = 'transform 0.1s ease';
            });

            card.addEventListener('touchend', () => {
                card.style.transform = '';
                card.style.transition = 'transform 0.2s ease';
            });

            // Улучшенная доступность
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });
    }

    /**
     * Улучшенные индикаторы прогресса
     */
    setupProgressIndicators() {
        const progressBars = document.querySelectorAll('.progress-bar-fill');
        
        progressBars.forEach(bar => {
            // Анимация прогресса для мобильных
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const progress = bar.style.width || '0%';
                        bar.style.transition = 'width 1s ease';
                        bar.style.width = progress;
                    }
                });
            });

            observer.observe(bar);
        });
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
}

class BigInfoMobileEnhancements {
    constructor() {
        this.init();
    }

    init() {
        this.setupBigInfoNavigation();
        this.setupMobileOptimizations();
    }

    setupBigInfoNavigation() {
        const navButtons = document.querySelectorAll('.nav-button');
        
        if (navButtons.length === 0) return;

        navButtons.forEach(button => {
            // Улучшенные touch interactions для мобильных устройств
            button.addEventListener('touchstart', (e) => {
                e.preventDefault();
                button.style.transform = 'scale(0.95)';
                
                // Haptic feedback
                if (navigator.vibrate) {
                    navigator.vibrate(10);
                }
            });

            button.addEventListener('touchend', (e) => {
                // НЕ блокируем события для ссылок навигации
                if (button.tagName === 'A' || button.classList.contains('nav-link') || button.closest('.navbar-collapse')) {
                    button.style.transform = '';
                    return;
                }
                
                e.preventDefault();
                button.style.transform = '';
                
                // Небольшая задержка для лучшего UX
                setTimeout(() => {
                    button.click();
                }, 50);
            });

            // Улучшенная доступность с клавиатуры
            button.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    button.click();
                }
            });
        });
    }

    setupMobileOptimizations() {
        // Адаптация для мобильных устройств
        if (window.innerWidth <= 768) {
            const navButtonsContainer = document.querySelector('.nav-buttons');
            if (navButtonsContainer) {
                // Добавляем горизонтальную прокрутку для кнопок на мобильных
                navButtonsContainer.style.overflowX = 'auto';
                navButtonsContainer.style.webkitOverflowScrolling = 'touch';
                navButtonsContainer.style.scrollbarWidth = 'none';
                navButtonsContainer.style.msOverflowStyle = 'none';
                
                // Скрываем scrollbar
                const style = document.createElement('style');
                style.textContent = `
                    .nav-buttons::-webkit-scrollbar {
                        display: none;
                    }
                `;
                document.head.appendChild(style);
            }

            // Улучшаем отступы для мобильных
            const contentSections = document.querySelectorAll('.content-section');
            contentSections.forEach(section => {
                section.style.padding = '1rem';
            });
        }
    }
}

// Инициализация улучшений для Learning Map
if (document.querySelector('.learning-map-container')) {
    document.addEventListener('DOMContentLoaded', () => {
        new LearningMapMobileEnhancements();
    });
}

// Инициализация улучшений для BIG Info страницы
if (document.querySelector('.nav-button')) {
    document.addEventListener('DOMContentLoaded', () => {
        new BigInfoMobileEnhancements();
    });
}
