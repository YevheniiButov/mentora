/**
 * Mentora - Образовательная платформа
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация основных компонентов
    initializeNavigation();
    initializeThemeSystem();
    initializeAnimations();
    initializeMobileNavigation();
    
    // Обратная совместимость
    setupLegacyCompatibility();
    
    // Скрываем сплеш-скрин если он есть
    hideSplashScreen();
    
    console.log('Tandarts Navigation System initialized');
});

/**
 * Инициализация основной навигации
 */
function initializeNavigation() {
    const pathButtons = document.querySelectorAll('.learning-path-button');
    
    // Находим уже раскрытый раздел
    const expandedList = document.querySelector('.subject-list.expanded');
    if (expandedList) {
        const pathId = expandedList.id.replace('path-', '').replace('-subjects', '');
        const activePathButton = document.querySelector(`.learning-path-button[data-path="${pathId}"]`);
        if (activePathButton) {
            activePathButton.classList.add('active');
            activePathButton.setAttribute('aria-expanded', 'true');
        }
    }
    
    // Обработчики для кнопок разделов
    pathButtons.forEach(button => {
        button.addEventListener('click', function() {
            const pathId = this.getAttribute('data-path');
            const subjectList = document.getElementById(`path-${pathId}-subjects`);
            
            if (!subjectList) return;
            
            const isExpanded = subjectList.classList.contains('expanded');
            
            // Закрываем все остальные разделы
            document.querySelectorAll('.subject-list.expanded').forEach(list => {
                if (list.id !== `path-${pathId}-subjects`) {
                    list.classList.remove('expanded');
                    // Убираем активное состояние с соответствующей кнопки
                    const siblingButton = document.querySelector(`[data-path="${list.id.replace('path-', '').replace('-subjects', '')}"]`);
                    if (siblingButton) {
                        siblingButton.classList.remove('active');
                        siblingButton.setAttribute('aria-expanded', 'false');
                    }
                }
            });
            
            // Переключаем состояние текущего списка
            if (isExpanded) {
                subjectList.classList.remove('expanded');
                this.classList.remove('active');
                this.setAttribute('aria-expanded', 'false');
            } else {
                subjectList.classList.add('expanded');
                this.classList.add('active');
                this.setAttribute('aria-expanded', 'true');
                
                // Анимация появления элементов списка
                const subjectItems = subjectList.querySelectorAll('.subject-item');
                subjectItems.forEach((item, index) => {
                    item.style.animationDelay = `${index * 50}ms`;
                    item.classList.add('animate-slide-up');
                });
            }
        });
        
        // Добавляем поддержку клавиатуры
        button.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

/**
 * Система управления темами
 */
function initializeThemeSystem() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (!themeToggle) return;
    
    // Устанавливаем начальную иконку
    updateThemeIcon();
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Применяем новую тему
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Обновляем иконку
        updateThemeIcon();
        
        // Анимация переключения
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        
        // Создаем кастомное событие
        const themeChangeEvent = new CustomEvent('themeChanged', {
            detail: { theme: newTheme, previousTheme: currentTheme }
        });
        window.dispatchEvent(themeChangeEvent);
        
        // Показываем уведомление
        const message = newTheme === 'dark' ? 
            (window.AppConfig && getTranslation ? getTranslation('dark_theme_enabled') : 'Темная тема включена') :
            (window.AppConfig && getTranslation ? getTranslation('light_theme_enabled') : 'Светлая тема включена');
        
        showNotification(message, 'info', 2000);
    });
    
    function updateThemeIcon() {
        if (!themeIcon) return;
        const currentTheme = document.documentElement.getAttribute('data-theme');
        themeIcon.className = currentTheme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
    }
}

/**
 * Инициализация анимаций
 */
function initializeAnimations() {
    // Анимация прогресс-баров
    animateProgressBars();
    
    // Анимация карточек при появлении
    animateCards();
    
    // Анимация счетчиков
    animateCounters();
}

/**
 * Анимация прогресс-баров при прокрутке
 */
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar-fill, .progress-fill, .vp-progress-fill');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetWidth = entry.target.getAttribute('data-width') || entry.target.style.width;
                
                // Сохраняем и сбрасываем ширину
                if (!entry.target.hasAttribute('data-width')) {
                    entry.target.setAttribute('data-width', targetWidth);
                }
                
                entry.target.style.width = '0%';
                
                // Анимируем до целевой ширины
                setTimeout(() => {
                    entry.target.style.width = targetWidth;
                }, 100);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

/**
 * Анимация карточек при появлении
 */
function animateCards() {
    const cards = document.querySelectorAll('.module-card, .subject-card, .vp-card, .recommendation-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.classList.add('animate-slide-up');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    cards.forEach(card => {
        // Устанавливаем начальное состояние
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        observer.observe(card);
    });
}

/**
 * Анимация счетчиков
 */
function animateCounters() {
    const counters = document.querySelectorAll('.stat-value, .days-number, .circle-text');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateValue(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

/**
 * Анимация числового значения
 */
function animateValue(element) {
    const text = element.textContent;
    const number = parseInt(text.replace(/\D/g, ''));
    
    if (isNaN(number) || number === 0) return;
    
    const suffix = text.replace(number.toString(), '');
    const duration = 1000;
    const steps = 60;
    const stepValue = number / steps;
    let current = 0;
    
    const timer = setInterval(() => {
        current += stepValue;
        if (current >= number) {
            current = number;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current) + suffix;
    }, duration / steps);
}

/**
 * Мобильная навигация
 */
function initializeMobileNavigation() {
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
    
    mobileNavItems.forEach(item => {
        // Пропускаем элементы, которые уже являются ссылками
        if (item.tagName.toLowerCase() === 'a') return;
        
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const pathId = this.getAttribute('data-path');
            const category = this.getAttribute('data-category');
            
            if (pathId && window.AppConfig) {
                const url = `/${window.AppConfig.currentLanguage}/learning-map/path/${pathId}`;
                navigateWithLoading(url);
            }
        });
        
        // Добавляем эффект нажатия
        item.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        item.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Горизонтальная прокрутка для мобильной навигации
    const mobileNavContainer = document.querySelector('.mobile-nav-container');
    if (mobileNavContainer) {
        // Скрываем полосу прокрутки
        mobileNavContainer.style.scrollbarWidth = 'none';
        mobileNavContainer.style.msOverflowStyle = 'none';
        
        // Добавляем плавную прокрутку
        mobileNavContainer.style.scrollBehavior = 'smooth';
        
        // Автоматически прокручиваем к активному элементу
        const activeItem = mobileNavContainer.querySelector('.mobile-nav-item.active');
        if (activeItem) {
            setTimeout(() => {
                activeItem.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest', 
                    inline: 'center' 
                });
            }, 100);
        }
    }
}

/**
 * Навигация с индикатором загрузки
 */
function navigateWithLoading(url) {
    if (window.showLoading) {
        window.showLoading();
    }
    
    // Задержка для показа анимации загрузки
    setTimeout(() => {
        window.location.href = url;
    }, 200);
}

/**
 * Обратная совместимость со старым кодом
 */
function setupLegacyCompatibility() {
    // Функции для обратной совместимости
    window.startModule = function(moduleId) {
        if (!moduleId || !window.AppConfig) return;
        
        const url = `/${window.AppConfig.currentLanguage}/learning-map/module/${moduleId}/start`;
        navigateWithLoading(url);
    };
    
    window.showNotification = function(message, type = 'info', duration = 5000) {
        if (window.showFlashMessage) {
            window.showFlashMessage(type, message, duration);
        } else {
            // Fallback уведомление
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    };
    
    // Функция для получения переводов
    window.getTranslation = function(key, lang = null) {
        const currentLang = lang || (window.AppConfig && window.AppConfig.currentLanguage) || 'en';
        
        // Здесь можно добавить логику получения переводов
        // Пока возвращаем ключ как есть
        return key;
    };
}

/**
 * Скрытие сплеш-скрина
 */
function hideSplashScreen() {
    setTimeout(() => {
        const splashScreen = document.getElementById('splashScreen');
        if (splashScreen) {
            splashScreen.classList.add('hidden');
            
            setTimeout(() => {
                splashScreen.remove();
            }, 500);
        }
        
        // Добавляем класс loaded для анимации контента
        document.body.classList.add('loaded');
    }, 2000);
}

/**
 * Получение CSRF-токена
 */
function getCsrfToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : '';
}

/**
 * Инициализация карусели для мобильных устройств (legacy)
 */
function initMobileCarousel() {
    const container = document.querySelector('.carousel-container');
    const indicators = document.querySelectorAll('.carousel-indicators span');
    
    if (!container || !indicators.length) return;
    
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            container.style.transform = `translateX(-${index * (100/3)}%)`;
            
            indicators.forEach(ind => ind.classList.remove('active'));
            indicator.classList.add('active');
        });
    });
}

/**
 * Класс для управления модальными окнами
 */
class ModalManager {
    constructor() {
        this.activeModal = null;
    }
    
    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        this.activeModal = modal;
        modal.style.display = 'flex';
        modal.classList.add('show');
        
        // Блокируем прокрутку фона
        document.body.style.overflow = 'hidden';
        
        // Фокус на первом интерактивном элементе
        const firstInput = modal.querySelector('input, button, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
    
    close(modalId = null) {
        const modal = modalId ? document.getElementById(modalId) : this.activeModal;
        if (!modal) return;
        
        modal.classList.remove('show');
        
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
            this.activeModal = null;
        }, 300);
    }
}

// Создаем глобальный экземпляр менеджера модальных окон
window.modalManager = new ModalManager();

/**
 * Обработчик ошибок JavaScript
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    
    // В режиме разработки показываем детали ошибки
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.error('Error details:', {
            message: e.message,
            filename: e.filename,
            lineno: e.lineno,
            colno: e.colno,
            error: e.error
        });
    }
});

/**
 * Обработчик unhandled promise rejections
 */
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    
    // Предотвращаем вывод ошибки в консоль браузера
    e.preventDefault();
});

/**
 * Утилиты для работы с DOM
 */
const DOMUtils = {
    // Ожидание загрузки элемента
    waitForElement: function(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            const observer = new MutationObserver((mutations, obs) => {
                const element = document.querySelector(selector);
                if (element) {
                    obs.disconnect();
                    resolve(element);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element ${selector} not found within ${timeout}ms`));
            }, timeout);
        });
    },
    
    // Плавная прокрутка к элементу
    scrollToElement: function(element, offset = 0) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        const headerHeight = document.querySelector('.site-header')?.offsetHeight || 70;
        const targetPosition = element.offsetTop - headerHeight - offset;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    },
    
    // Проверка видимости элемента
    isElementVisible: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Экспортируем утилиты в глобальную область видимости
window.DOMUtils = DOMUtils;

/**
 * Инициализация для конкретных страниц
 */
function initializePageSpecific() {
    const currentPage = window.location.pathname;
    
    // Инициализация для страницы subject_view
    if (currentPage.includes('subject') || currentPage.includes('learning-map')) {
        initializeSubjectView();
    }
    
    // Инициализация для страницы модуля
    if (currentPage.includes('module')) {
        initializeModuleView();
    }
    
    // Инициализация для страницы урока
    if (currentPage.includes('lesson')) {
        initializeLessonView();
    }
}

/**
 * Инициализация для страницы предметов
 */
function initializeSubjectView() {
    // Дополнительная логика для страницы предметов
    console.log('Subject view initialized');
}

/**
 * Инициализация для страницы модуля
 */
function initializeModuleView() {
    // Дополнительная логика для страницы модуля
    console.log('Module view initialized');
}

/**
 * Инициализация для страницы урока
 */
function initializeLessonView() {
    // Дополнительная логика для страницы урока
    console.log('Lesson view initialized');
}

// Запускаем инициализацию для конкретных страниц
document.addEventListener('DOMContentLoaded', initializePageSpecific);

// Debug режим
if (window.location.hostname === 'localhost' || window.location.search.includes('debug=true')) {
    window.TandartsDebug = {
        // Показать все скрытые элементы
        showAllElements: function() {
            document.querySelectorAll('.hidden, [style*="display: none"]').forEach(el => {
                el.style.display = 'block';
                el.style.opacity = '1';
                el.classList.remove('hidden');
            });
        },
        
        // Подсветить все кликабельные элементы
        highlightClickable: function() {
            document.querySelectorAll('button, a, [onclick], [data-bs-toggle]').forEach(el => {
                el.style.outline = '2px solid red';
            });
        },
        
        // Проверить переводы
        checkTranslations: function() {
            const untranslated = [];
            document.querySelectorAll('[data-translate]').forEach(el => {
                const key = el.getAttribute('data-translate');
                if (el.textContent === key) {
                    untranslated.push(key);
                }
            });
            console.log('Untranslated keys:', untranslated);
        },
        
        // Информация о производительности
        showPerformance: function() {
            if (window.performance) {
                const navigation = performance.getEntriesByType('navigation')[0];
                console.log('Page Load Time:', navigation.loadEventEnd - navigation.loadEventStart, 'ms');
                console.log('DOM Content Loaded:', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart, 'ms');
            }
        }
    };
    
    console.log('Debug mode enabled. Use window.TandartsDebug for debugging tools.');
}