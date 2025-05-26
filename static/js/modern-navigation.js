/**
 * modern-navigation.js - Исправленная система навигации
 * Dental Academy - Образовательная платформа
 */

class ModernNavigationSystem {
    constructor() {
        this.currentLang = document.documentElement.lang || 'en';
        this.currentTheme = 'light';
        this.translations = {};
        this.isLoading = false;
        this.splashShown = false;
        
        this.init();
    }

    /**
     * Инициализация системы
     */
    init() {
        // Показываем сплеш только один раз за сессию
        this.checkAndShowSplash();
        
        this.loadSavedPreferences();
        this.setupEventListeners();
        this.setupSidebarNavigation();
        this.setupInteractiveCards();
        this.setupThemeSystem();
        this.setupScrollEffects();
        this.initializeAnimations();
        this.createModernBackground();
        
        // Загружаем переводы асинхронно
        this.loadTranslations();
    }

  
    /**
     * Создание современного анимированного фона
     */
    createModernBackground() {
        const container = document.querySelector('.learning-map-container');
        if (!container) return;

        container.style.position = 'relative';
        container.style.overflow = 'hidden';

        // Создаем фоновые элементы
        const backgroundHTML = `
            <div class="modern-background">
                <div class="bg-particles"></div>
                <div class="bg-waves"></div>
                <div class="bg-gradient"></div>
            </div>
        `;

        container.insertAdjacentHTML('afterbegin', backgroundHTML);

        // Добавляем стили для фона
        if (!document.getElementById('modern-background-styles')) {
            const bgStyles = document.createElement('style');
            bgStyles.id = 'modern-background-styles';
            bgStyles.textContent = `
                .modern-background {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: -1;
                    overflow: hidden;
                }
                
                .bg-gradient {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        radial-gradient(circle at 20% 20%, rgba(62, 205, 193, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(108, 92, 231, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 50% 50%, rgba(253, 203, 110, 0.05) 0%, transparent 50%);
                    animation: gradientShift 20s ease-in-out infinite;
                }
                
                .bg-particles {
                    position: absolute;
                    width: 100%;
                    height: 100%;
                    background-image: 
                        radial-gradient(2px 2px at 20px 30px, rgba(62, 205, 193, 0.3), transparent),
                        radial-gradient(2px 2px at 40px 70px, rgba(108, 92, 231, 0.3), transparent),
                        radial-gradient(1px 1px at 90px 40px, rgba(253, 203, 110, 0.3), transparent),
                        radial-gradient(1px 1px at 130px 80px, rgba(62, 205, 193, 0.2), transparent),
                        radial-gradient(2px 2px at 160px 30px, rgba(108, 92, 231, 0.2), transparent);
                    background-repeat: repeat;
                    background-size: 200px 200px;
                    animation: particlesFloat 30s linear infinite;
                }
                
                .bg-waves {
                    position: absolute;
                    width: 200%;
                    height: 200%;
                    background: 
                        linear-gradient(45deg, transparent 30%, rgba(62, 205, 193, 0.03) 50%, transparent 70%);
                    animation: wavesMove 25s linear infinite;
                }
                
                [data-theme="dark"] .bg-gradient {
                    background: 
                        radial-gradient(circle at 20% 20%, rgba(62, 205, 193, 0.05) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(108, 92, 231, 0.05) 0%, transparent 50%),
                        radial-gradient(circle at 50% 50%, rgba(253, 203, 110, 0.03) 0%, transparent 50%);
                }
                
                @keyframes gradientShift {
                    0%, 100% { transform: translate(0, 0) rotate(0deg); }
                    50% { transform: translate(-10px, -10px) rotate(1deg); }
                }
                
                @keyframes particlesFloat {
                    0% { transform: translate(0, 0); }
                    100% { transform: translate(-200px, -200px); }
                }
                
                @keyframes wavesMove {
                    0% { transform: translate(-50%, -50%) rotate(0deg); }
                    100% { transform: translate(-50%, -50%) rotate(360deg); }
                }
            `;
            document.head.appendChild(bgStyles);
        }
    }

    /**
     * Загрузка сохраненных предпочтений пользователя
     */
    loadSavedPreferences() {
        // Загружаем сохраненную тему
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
        
        // Загружаем сохраненный язык
        const savedLang = localStorage.getItem('language') || 'en';
        this.currentLang = savedLang;
    }

    /**
     * Настройка системы тем
     */
    setupThemeSystem() {
        // Проверяем, инициализирована ли глобальная система тем
        if (window.themeSystem && window.themeSystem.isInitialized) {
            this.currentTheme = window.themeSystem.getCurrentTheme();
            return;
        }

        // Fallback: собственная инициализация
        this.initializeThemeSystem();
    }

    initializeThemeSystem() {
        // Применяем сохраненную тему
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.setTheme(savedTheme);
        } else {
            // Определяем системную тему
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.setTheme(prefersDark ? 'dark' : 'light');
        }

        // Добавляем обработчики переключения темы
        document.addEventListener('click', (e) => {
            const themeToggle = e.target.closest('.theme-toggle, .theme-toggle-inline, [onclick="toggleTheme()"]');
            if (themeToggle) {
                e.preventDefault();
                e.stopPropagation();
                this.toggleTheme();
            }
        });

        // Глобальная функция для совместимости
        window.toggleTheme = () => this.toggleTheme();
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${theme}`);
        localStorage.setItem('theme', theme);
        
        this.updateThemeIcon();
        this.emit('themeChanged', { theme });
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
        
        // Уведомление об изменении темы
        this.showNotification(
            newTheme === 'dark' ? 'Темная тема включена' : 'Светлая тема включена', 
            'info', 
            2000
        );
    }

    updateThemeIcon() {
        const toggles = document.querySelectorAll('.theme-toggle, .theme-toggle-inline, [onclick="toggleTheme()"]');
        
        toggles.forEach(toggle => {
            const icon = toggle.querySelector('.theme-icon, .fas, .bi, i');
            const text = toggle.querySelector('.theme-text');
            
            if (icon) {
                // Убираем старые классы
                icon.className = icon.className.replace(/fa-moon|fa-sun|bi-moon|bi-sun/g, '');
                
                if (this.currentTheme === 'dark') {
                    // Показываем иконку солнца для переключения на светлую тему
                    if (icon.classList.contains('fas')) {
                        icon.classList.add('fa-sun');
                    } else {
                        icon.classList.add('bi-sun');
                    }
                } else {
                    // Показываем иконку луны для переключения на темную тему
                    if (icon.classList.contains('fas')) {
                        icon.classList.add('fa-moon');
                    } else {
                        icon.classList.add('bi-moon');
                    }
                }
            }
            
            if (text) {
                text.textContent = this.currentTheme === 'dark' ? 'Светлая тема' : 'Темная тема';
            }
        });
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Мобильная навигация
        this.setupMobileNavigation();
        
        // Обработка карточек
        this.setupCardInteractions();
        
        // Глобальные клавиатурные сокращения
        this.setupKeyboardShortcuts();
    }

    /**
     * ИСПРАВЛЕННАЯ навигация в боковой панели
     */
    setupSidebarNavigation() {
        // Исправленные селекторы для кнопок навигации
        const navButtons = document.querySelectorAll('.learning-path-button');
        
        navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const category = button.getAttribute('data-category') || button.getAttribute('data-path');
                if (category) {
                    this.toggleNavSection(category, button);
                }
            });
        });

        // Обработка кликов по подразделам
        const subNavItems = document.querySelectorAll('.subject-item');
        subNavItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Не preventDefault для ссылок - позволяем переходить
                this.handleSubNavClick(item);
            });
        });

        // Проверяем текущую активную секцию и раскрываем её
        this.initializeActiveSection();
    }

    toggleNavSection(category, button) {
        // Находим соответствующий список предметов
        const subNav = document.getElementById(`path-${category}-subjects`) || 
                      document.querySelector(`[id*="${category}"]`) ||
                      button.nextElementSibling;
        
        if (!subNav) {
            console.warn(`SubNav not found for category: ${category}`);
            return;
        }
        
        const isExpanded = subNav.classList.contains('expanded');
        
        if (isExpanded) {
            this.collapseNavSection(category, button, subNav);
        } else {
            // Сначала сворачиваем все остальные секции
            this.collapseAllNavSections();
            this.expandNavSection(category, button, subNav);
        }
        
        // Сохраняем состояние
        this.saveNavState();
    }

    expandNavSection(category, button, subNav) {
        button.setAttribute('data-expanded', 'true');
        button.classList.add('active');
        subNav.classList.add('expanded');
        
        // Поворачиваем стрелочку
        const chevron = button.querySelector('.chevron-icon');
        if (chevron) {
            chevron.style.transform = 'rotate(90deg)';
        }
        
        // Анимация расширения
        subNav.style.maxHeight = '0px';
        subNav.style.opacity = '0';
        
        // Принудительный reflow
        subNav.offsetHeight;
        
        const scrollHeight = subNav.scrollHeight;
        subNav.style.maxHeight = scrollHeight + 'px';
        subNav.style.opacity = '1';
        
        // Убираем maxHeight после анимации для гибкости
        setTimeout(() => {
            if (subNav.classList.contains('expanded')) {
                subNav.style.maxHeight = 'none';
            }
        }, 300);
    }

    collapseNavSection(category, button, subNav) {
        button.setAttribute('data-expanded', 'false');
        button.classList.remove('active');
        
        // Поворачиваем стрелочку обратно
        const chevron = button.querySelector('.chevron-icon');
        if (chevron) {
            chevron.style.transform = 'rotate(0deg)';
        }
        
        // Анимация сворачивания
        subNav.style.maxHeight = subNav.scrollHeight + 'px';
        subNav.offsetHeight; // Принудительный reflow
        
        subNav.style.maxHeight = '0px';
        subNav.style.opacity = '0';
        
        setTimeout(() => {
            subNav.classList.remove('expanded');
        }, 300);
    }

    collapseAllNavSections() {
        const buttons = document.querySelectorAll('.learning-path-button');
        buttons.forEach(button => {
            const category = button.getAttribute('data-category') || button.getAttribute('data-path');
            const subNav = document.getElementById(`path-${category}-subjects`) || 
                          button.nextElementSibling;
            
            if (subNav && subNav.classList.contains('expanded')) {
                this.collapseNavSection(category, button, subNav);
            }
        });
    }

    initializeActiveSection() {
        // Находим активный предмет и раскрываем его категорию
        const activeSubject = document.querySelector('.subject-item.active');
        if (activeSubject) {
            const subjectList = activeSubject.closest('.subject-list');
            if (subjectList) {
                const pathButton = subjectList.previousElementSibling;
                if (pathButton && pathButton.classList.contains('learning-path-button')) {
                    const category = pathButton.getAttribute('data-category') || pathButton.getAttribute('data-path');
                    this.expandNavSection(category, pathButton, subjectList);
                }
            }
        }
    }

    handleSubNavClick(item) {
        // Убираем активный класс со всех элементов
        document.querySelectorAll('.subject-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Добавляем активный класс к выбранному элементу
        item.classList.add('active');
    }

    saveNavState() {
        const expandedSections = [];
        document.querySelectorAll('.learning-path-button[data-expanded="true"]').forEach(button => {
            const category = button.getAttribute('data-category') || button.getAttribute('data-path');
            if (category) {
                expandedSections.push(category);
            }
        });
        localStorage.setItem('expandedSections', JSON.stringify(expandedSections));
    }

    /**
     * ИСПРАВЛЕННЫЕ интерактивные карточки
     */
    setupInteractiveCards() {
        const interactiveCards = document.querySelectorAll('.interactive-card');
        
        interactiveCards.forEach(card => {
            // Делаем карточку фокусируемой
            if (!card.hasAttribute('tabindex')) {
                card.setAttribute('tabindex', '0');
            }
            
            // Добавляем ARIA атрибуты
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', 'Нажмите, чтобы перевернуть карточку с интересным фактом');
            
            // Обработчик клика
            const handleFlip = () => {
                card.classList.toggle('flipped');
                const isFlipped = card.classList.contains('flipped');
                card.setAttribute('aria-label', 
                    isFlipped ? 'Карточка перевернута. Нажмите, чтобы вернуть обратно' : 
                               'Нажмите, чтобы перевернуть карточку с интересным фактом'
                );
            };
            
            // Клик мышью
            card.addEventListener('click', handleFlip);
            
            // Клавиатурная навигация
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleFlip();
                }
            });
            
            // Hover эффекты
            card.addEventListener('mouseenter', () => {
                if (!card.classList.contains('flipped')) {
                    card.style.transform = 'translateY(-2px) scale(1.02)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                if (!card.classList.contains('flipped')) {
                    card.style.transform = '';
                }
            });
        });
    }

    /**
     * Взаимодействие с карточками
     */
    setupCardInteractions() {
        // Анимация наведения на карточки
        const cards = document.querySelectorAll('.card, .module-card, .subject-card, .recommendation-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.animateCardHover(card, true);
            });
            
            card.addEventListener('mouseleave', () => {
                this.animateCardHover(card, false);
            });
        });
    }

    animateCardHover(card, isHover) {
        if (isHover) {
            card.style.transform = 'translateY(-4px) scale(1.02)';
            card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        } else {
            card.style.transform = '';
        }
    }

    /**
     * Мобильная навигация
     */
    setupMobileNavigation() {
        const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
        
        mobileNavItems.forEach(item => {
            item.addEventListener('click', (e) => {
                // Не preventDefault для ссылок
                this.handleMobileNavClick(item);
            });
        });
    }

    handleMobileNavClick(item) {
        // Убираем активный класс со всех элементов
        document.querySelectorAll('.mobile-nav-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Добавляем активный класс к выбранному элементу
        item.classList.add('active');
        
        // Анимация нажатия
        item.style.transform = 'scale(0.95)';
        setTimeout(() => {
            item.style.transform = '';
        }, 150);
    }

    /**
     * Эффекты прокрутки
     */
    setupScrollEffects() {
        let lastScrollY = window.scrollY;
        let ticking = false;
        
        const handleScroll = () => {
            const currentScrollY = window.scrollY;
            const header = document.querySelector('.modern-header, .site-header');
            
            if (header) {
                if (currentScrollY > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            }
            
            lastScrollY = currentScrollY;
            ticking = false;
        };
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(handleScroll);
                ticking = true;
            }
        }, { passive: true });
    }

    /**
     * Инициализация анимаций
     */
    initializeAnimations() {
        // Добавляем класс loaded для триггера CSS анимаций
        setTimeout(() => {
            document.body.classList.add('loaded');
        }, 100);
        
        // Анимация появления элементов при скролле
        this.setupIntersectionObservers();
    }

    /**
     * Наблюдатели пересечений для анимаций
     */
    setupIntersectionObservers() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('animate-slide-up');
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }, index * 100);
                    
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        // Наблюдаем за элементами, которые должны анимироваться
        const animatedElements = document.querySelectorAll(
            '.card, .module-card, .subject-card, .stat-card, .recommendation-card, .vp-card'
        );
        animatedElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(element);
        });
    }

    /**
     * Клавиатурные сокращения
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + T для переключения темы
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 't') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // ESC для закрытия модальных окон
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    /**
     * Загрузка переводов (заглушка)
     */
    async loadTranslations() {
        // В реальном приложении здесь будет загрузка переводов
        this.translations = {};
    }

    /**
     * Утилитарные методы
     */
    closeAllModals() {
        const modals = document.querySelectorAll('.modal.show, .modal-overlay');
        modals.forEach(modal => {
            if (modal.classList.contains('modal') && window.bootstrap) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            } else {
                modal.remove();
            }
        });
    }

    showNotification(message, type = 'info', duration = 5000) {
        if (window.showFlashMessage) {
            window.showFlashMessage(type, message, duration);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    /**
     * Система событий
     */
    emit(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
    }

    on(eventName, callback) {
        document.addEventListener(eventName, callback);
    }
}

/**
 * Инициализация при загрузке DOM
 */
document.addEventListener('DOMContentLoaded', () => {
    // Создаем глобальный экземпляр системы навигации
    window.navigationSystem = new ModernNavigationSystem();
    
    // Экспорт глобальных функций для совместимости
    window.startModule = function(moduleId) {
        const currentLang = window.navigationSystem.currentLang;
        window.location.href = `/${currentLang}/learning-map/module/${moduleId}/start`;
    };
    
    window.navigateToCategory = function(categoryId) {
        const currentLang = window.navigationSystem.currentLang;
        window.location.href = `/${currentLang}/learning-map/category/${categoryId}`;
    };
    
    // Логирование для отладки
    console.log('🎓 Dental Academy: Modern Navigation System initialized');
    console.log('Current theme:', window.navigationSystem.currentTheme);
    console.log('Current language:', window.navigationSystem.currentLang);
});

// Глобальная конфигурация для совместимости
window.AppConfig = window.AppConfig || {
    currentLanguage: 'en',
    isAuthenticated: false,
    userId: null,
    csrfToken: ''
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Subject view page loaded');
    
    // Ждем инициализации системы навигации
    const waitForNavigation = () => {
        if (window.navigationSystem && window.navigationSystem.isInitialized) {
            console.log('✅ Navigation system ready');
            initializePageFeatures();
        } else {
            console.log('⏳ Waiting for navigation system...');
            setTimeout(waitForNavigation, 100);
        }
    };
    
    waitForNavigation();
    
    // Инициализируем функции страницы
    function initializePageFeatures() {
        // Функции навигации для совместимости
        window.navigateToCategory = function(categoryId) {
            const currentLang = window.AppConfig.currentLanguage;
            console.log(`🔗 Navigating to category: ${categoryId}`);
            window.location.href = `/${currentLang}/learning-map/category/${categoryId}`;
        };
        
        window.startModule = function(moduleId) {
            const currentLang = window.AppConfig.currentLanguage;
            console.log(`🎯 Starting module: ${moduleId}`);
            window.location.href = `/${currentLang}/learning-map/module/${moduleId}/start`;
        };
        
        // Инициализация модального окна экзамена
        setupExamDateModal();
        
        // Улучшенная обработка клавиатуры для карточек
        setupKeyboardNavigation();
        
        console.log('🎉 Page features initialized');
    }
    
    // Настройка модального окна для даты экзамена
    function setupExamDateModal() {
        const saveExamDateBtn = document.getElementById('saveExamDate');
        if (saveExamDateBtn) {
            saveExamDateBtn.addEventListener('click', function() {
                const examDateInput = document.getElementById('examDate');
                if (examDateInput && examDateInput.value) {
                    const examDate = new Date(examDateInput.value);
                    const formattedDate = examDate.toLocaleDateString(window.AppConfig.currentLanguage);
                    
                    // Показываем состояние загрузки
                    saveExamDateBtn.disabled = true;
                    saveExamDateBtn.textContent = 'Сохранение...';
                    
                    // Отправляем запрос на сервер
                    fetch(`/${window.AppConfig.currentLanguage}/api/save-exam-date`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': window.AppConfig.csrfToken
                        },
                        body: JSON.stringify({ 
                            examDate: examDateInput.value 
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Закрываем модальное окно
                            const modal = bootstrap.Modal.getInstance(document.getElementById('examDateModal'));
                            modal.hide();
                            
                            // Показываем уведомление
                            if (window.showFlashMessage) {
                                window.showFlashMessage('success', 'Дата экзамена сохранена');
                            }
                            
                            // Обновляем отображение даты на странице
                            const examDateDisplay = document.querySelector('.exam-date span');
                            if (examDateDisplay) {
                                examDateDisplay.textContent = formattedDate;
                            }
                        } else {
                            if (window.showFlashMessage) {
                                window.showFlashMessage('error', data.message || 'Ошибка при сохранении даты');
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        if (window.showFlashMessage) {
                            window.showFlashMessage('error', 'Ошибка сервера');
                        }
                    })
                    .finally(() => {
                        // Восстанавливаем состояние кнопки
                        saveExamDateBtn.disabled = false;
                        saveExamDateBtn.textContent = 'Сохранить';
                    });
                }
            });
        }
    }
    
    // Улучшенная клавиатурная навигация
    function setupKeyboardNavigation() {
        // Навигация по карточкам с клавиатуры
        document.addEventListener('keydown', function(e) {
            if (e.target.classList.contains('interactive-card')) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.target.click();
                }
            }
            
            // Быстрая навигация по путям обучения
            if (e.altKey && e.key >= '1' && e.key <= '7') {
                e.preventDefault();
                const pathId = parseInt(e.key);
                navigateToCategory(pathId);
            }
        });
    }
    
    // Анимация прогресс-баров при появлении в зоне видимости
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const progressObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressFills = entry.target.querySelectorAll('.progress-fill, .progress-bar-fill, .vp-progress-fill');
                progressFills.forEach(progressFill => {
                    const targetWidth = progressFill.style.width;
                    progressFill.style.width = '0%';
                    setTimeout(() => {
                        progressFill.style.width = targetWidth;
                    }, 100);
                });
                progressObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Наблюдаем за всеми элементами с прогресс-барами
    document.querySelectorAll('.progress-bar, .progress-bar-container, .vp-progress-bar, .module-card, .subject-card').forEach(element => {
        progressObserver.observe(element);
    });
    
    // Обработка ошибок JavaScript
    window.addEventListener('error', function(e) {
        console.error('❌ JavaScript error in subject_view:', e.error);
    });
    
    console.log('✅ Subject view scripts initialized');
});

// Функция для отладки состояния системы
window.debugNavigation = function() {
    console.log('🔍 Navigation Debug Info:');
    console.log('- Navigation System:', window.navigationSystem?.isInitialized ? '✅ Ready' : '❌ Not Ready');
    console.log('- Theme System:', window.themeSystem?.isInitialized ? '✅ Ready' : '❌ Not Ready');
    console.log('- Current Theme:', window.themeSystem?.getCurrentTheme() || 'Unknown');
    console.log('- Current Language:', window.AppConfig?.currentLanguage || 'Unknown');
    
    if (window.themeSystem) {
        console.log('- Theme Debug Info:', window.themeSystem.getDebugInfo());
    }
};