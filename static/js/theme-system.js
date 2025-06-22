/* ===== ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ THEME-SYSTEM.JS ===== */
/* static/js/theme-system.js */

(function() {
    'use strict';
    
    // Предотвращаем множественную инициализацию
    if (window.ThemeSystemInitialized) {
        console.log('ℹ️ Theme system already initialized');
        return;
    }
    
    class RobustThemeSystem {
        constructor() {
            this.storageKey = 'theme';
            this.currentTheme = null;
            this.isInitialized = false;
            this.isTransitioning = false;
            
            // Инициализация
            this.initialize();
        }
        
        initialize() {
            try {
                console.log('🎨 Initializing theme system...');
                
                // Определяем начальную тему
                this.currentTheme = this.detectTheme();
                
                // Применяем тему
                this.applyTheme(this.currentTheme, false);
                
                // Настраиваем глобальные функции
                this.setupGlobalFunctions();
                
                // Настраиваем наблюдатель системной темы
                this.setupSystemThemeWatcher();
                
                this.isInitialized = true;
                console.log('✅ Theme system initialized successfully');
                
            } catch (error) {
                console.error('❌ Error initializing theme system:', error);
                this.fallbackInitialization();
            }
        }
        
        detectTheme() {
            // 1. Проверяем localStorage
            const savedTheme = localStorage.getItem(this.storageKey);
            if (savedTheme === 'light' || savedTheme === 'dark') {
                console.log('💾 Using saved theme:', savedTheme);
                return savedTheme;
            }
            
            // 2. Проверяем текущий DOM атрибут
            const domTheme = document.documentElement.getAttribute('data-theme');
            if (domTheme === 'light' || domTheme === 'dark') {
                console.log('🌐 Using DOM theme:', domTheme);
                return domTheme;
            }
            
            // 3. Проверяем системные предпочтения
            try {
                if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    console.log('🌙 Using system dark theme');
                    return 'dark';
                }
            } catch (e) {
                console.warn('⚠️ Could not detect system theme preference');
            }
            
            console.log('☀️ Defaulting to light theme');
            return 'light';
        }
        
        applyTheme(theme, skipValidation = false) {
            if (!skipValidation && theme !== 'light' && theme !== 'dark') {
                console.warn(`⚠️ Invalid theme: ${theme}, defaulting to light`);
                theme = 'light';
            }
            
            console.log(`🎨 Applying theme: ${theme}`);
            
            try {
                // Применяем к document (основной способ)
                document.documentElement.setAttribute('data-theme', theme);
                
                // Обновляем body классы для совместимости со старыми стилями
                document.body.classList.remove('theme-light', 'theme-dark');
                document.body.classList.add(`theme-${theme}`);
                
                // Сохраняем текущую тему
                this.currentTheme = theme;
                
                // Сохраняем в localStorage
                localStorage.setItem(this.storageKey, theme);
                
                // Обновляем кнопки переключения
                this.updateToggleButtons(theme);
                
                // Уведомляем другие системы
                this.dispatchThemeEvent(theme);
                
                console.log(`✅ Theme successfully applied: ${theme}`);
                return theme;
                
            } catch (error) {
                console.error('❌ Error applying theme:', error);
                return this.currentTheme;
            }
        }
        
        toggleTheme() {
            const currentTheme = this.getCurrentTheme();
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            console.log(`🔄 Toggling theme: ${currentTheme} → ${newTheme}`);
            
            const result = this.applyTheme(newTheme);
            
            // Показываем уведомление
            this.showThemeNotification(newTheme);
            
            return result;
        }
        
        getCurrentTheme() {
            // Проверяем DOM как источник истины
            const domTheme = document.documentElement.getAttribute('data-theme');
            if (domTheme === 'light' || domTheme === 'dark') {
                this.currentTheme = domTheme;
                return domTheme;
            }
            
            return this.currentTheme;
        }
        
        updateToggleButtons(theme) {
            try {
                // Расширенный список селекторов для поиска кнопок
                const selectors = [
                    '.theme-toggle',
                    '.theme-toggle-inline',
                    '[data-theme-toggle]',
                    '[onclick*="toggleTheme"]',
                    'button[class*="theme"]',
                    '.theme-btn',
                    '[aria-label*="тем"]',
                    '[aria-label*="theme"]'
                ];
                
                const buttons = document.querySelectorAll(selectors.join(', '));
                console.log(`🔄 Updating ${buttons.length} theme toggle buttons`);
                
                if (buttons.length === 0) {
                    console.warn('⚠️ No theme toggle buttons found');
                    return;
                }
                
                buttons.forEach((button, index) => {
                    try {
                        this.updateSingleButton(button, theme, index);
                    } catch (error) {
                        console.warn(`⚠️ Error updating button ${index}:`, error);
                    }
                });
                
            } catch (error) {
                console.error('❌ Error updating toggle buttons:', error);
            }
        }
        
        updateSingleButton(button, theme, index = 0) {
            const icon = button.querySelector('i, .icon, .theme-icon, [class*="icon"], .fas, .bi');
            const text = button.querySelector('.theme-text, span:not([class*="icon"]), .text');
            
            // Определяем следующую тему (что покажет кнопка)
            const nextTheme = theme === 'dark' ? 'light' : 'dark';
            
            // Обновляем иконку
            if (icon) {
                // Сохраняем основные классы, удаляем только классы иконок
                const baseClasses = icon.className
                    .replace(/\b(fa-moon|fa-sun|bi-moon|bi-sun|moon|sun)\b/gi, '')
                    .replace(/\s+/g, ' ')
                    .trim();
                
                icon.className = baseClasses;
                
                // Добавляем правильную иконку
                if (nextTheme === 'light') {
                    if (baseClasses.includes('fa')) {
                        icon.classList.add('fa-sun');
                    } else {
                        icon.classList.add('bi-sun');
                    }
                } else {
                    if (baseClasses.includes('fa')) {
                        icon.classList.add('fa-moon');
                    } else {
                        icon.classList.add('bi-moon');
                    }
                }
            }
            
            // Обновляем текст
            if (text) {
                const newText = nextTheme === 'light' ? 'Светлая тема' : 'Темная тема';
                text.textContent = newText;
            }
            
            // Обновляем ARIA атрибуты для доступности
            const ariaLabel = `Переключить на ${nextTheme === 'light' ? 'светлую' : 'темную'} тему`;
            button.setAttribute('aria-label', ariaLabel);
            
            // Обновляем aria-pressed для кнопок
            if (button.tagName === 'BUTTON' || button.getAttribute('role') === 'button') {
                button.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
            }
            
            console.log(`✅ Updated button ${index}: ${theme} theme, next: ${nextTheme}`);
        }
        
        setupEventDelegation() {
            console.log('🔗 Setting up event delegation for theme toggles');
            
            // Используем единый обработчик событий через делегирование
            document.addEventListener('click', (e) => {
                // Проверяем, кликнули ли по кнопке переключения темы
                const themeButton = e.target.closest([
                    '.theme-toggle',
                    '.theme-toggle-inline',
                    '[data-theme-toggle]',
                    '[onclick*="toggleTheme"]',
                    'button[class*="theme"]',
                    '.theme-btn'
                ].join(', '));
                
                if (themeButton) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log('🖱️ Theme toggle button clicked:', themeButton.className || themeButton.tagName);
                    
                    // Добавляем визуальный эффект
                    this.addClickEffect(themeButton);
                    
                    // Переключаем тему
                    this.toggleTheme();
                }
            }, true); // Используем capturing phase для надежности
            
            // Клавиатурные сокращения
            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 't') {
                    e.preventDefault();
                    console.log('⌨️ Theme toggle via keyboard shortcut');
                    this.toggleTheme();
                }
            });
        }
        
        setupGlobalFunctions() {
            console.log('🌐 Setting up global functions');
            
            // Основная глобальная функция для обратной совместимости
            window.toggleTheme = () => {
                console.log('🌐 Global toggleTheme() called');
                return this.toggleTheme();
            };
            
            // Объект themeSystem для совместимости с другими скриптами
            window.themeSystem = {
                getCurrentTheme: () => this.getCurrentTheme(),
                setTheme: (theme) => this.applyTheme(theme),
                toggleTheme: () => this.toggleTheme(),
                isInitialized: true,
                
                // Дополнительные методы для совместимости
                isDark: () => this.getCurrentTheme() === 'dark',
                isLight: () => this.getCurrentTheme() === 'light',
                
                // Методы для отладки
                getDebugInfo: () => ({
                    currentTheme: this.getCurrentTheme(),
                    isInitialized: this.isInitialized,
                    savedTheme: localStorage.getItem(this.storageKey),
                    buttonsCount: document.querySelectorAll('.theme-toggle, .theme-toggle-inline, [data-theme-toggle]').length
                })
            };
            
            // Класс для возможности создания новых экземпляров
            window.ThemeSystem = RobustThemeSystem;
            
            console.log('✅ Global functions ready');
        }
        
        setupSystemThemeWatcher() {
            try {
                if (window.matchMedia) {
                    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
                    
                    const handleSystemChange = (e) => {
                        // Применяем системную тему только если пользователь не выбирал вручную
                        const hasManualChoice = localStorage.getItem(this.storageKey);
                        if (!hasManualChoice) {
                            const systemTheme = e.matches ? 'dark' : 'light';
                            console.log(`🔄 Auto-switching to system theme: ${systemTheme}`);
                            this.applyTheme(systemTheme);
                        }
                    };
                    
                    if (mediaQuery.addEventListener) {
                        mediaQuery.addEventListener('change', handleSystemChange);
                    } else {
                        mediaQuery.addListener(handleSystemChange);
                    }
                    
                    console.log('👁️ System theme watcher enabled');
                }
            } catch (error) {
                console.warn('⚠️ Could not setup system theme watcher:', error);
            }
        }
        
        addClickEffect(button) {
            try {
                button.style.transform = 'scale(0.95)';
                button.style.transition = 'transform 0.1s ease';
                
                setTimeout(() => {
                    button.style.transform = '';
                    setTimeout(() => {
                        button.style.transition = '';
                    }, 100);
                }, 150);
            } catch (error) {
                console.warn('⚠️ Could not add click effect:', error);
            }
        }
        
        dispatchThemeEvent(theme) {
            try {
                const event = new CustomEvent('themeChanged', {
                    detail: { 
                        theme: theme,
                        timestamp: Date.now(),
                        source: 'RobustThemeSystem'
                    },
                    bubbles: true
                });
                document.dispatchEvent(event);
                
                // Дополнительные события для совместимости
                ['themeChange', 'theme-changed', 'themeUpdated'].forEach(eventName => {
                    const compatEvent = new CustomEvent(eventName, {
                        detail: { theme },
                        bubbles: true
                    });
                    document.dispatchEvent(compatEvent);
                });
                
            } catch (error) {
                console.warn('⚠️ Could not dispatch theme event:', error);
            }
        }
        
        showThemeNotification(theme) {
            const message = theme === 'dark' ? '🌙 Темная тема включена' : '☀️ Светлая тема включена';
            
            try {
                // Пытаемся использовать доступные системы уведомлений
                if (window.showFlashMessage) {
                    window.showFlashMessage('info', message, 2000);
                } else if (window.navigationSystem && window.navigationSystem.showNotification) {
                    window.navigationSystem.showNotification(message, 'info', 2000);
                } else {
                    console.log(`📢 ${message}`);
                }
            } catch (error) {
                console.log(`📢 ${message}`);
            }
        }
        
        fallbackInitialization() {
            console.log('🆘 Attempting fallback initialization');
            
            try {
                // Минимальная функциональность
                const theme = localStorage.getItem(this.storageKey) || 'light';
                document.documentElement.setAttribute('data-theme', theme);
                
                window.toggleTheme = () => {
                    const current = document.documentElement.getAttribute('data-theme') || 'light';
                    const newTheme = current === 'light' ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', newTheme);
                    localStorage.setItem(this.storageKey, newTheme);
                    console.log(`🔄 Fallback toggle: ${current} → ${newTheme}`);
                    return newTheme;
                };
                
                console.log('✅ Fallback initialization successful');
            } catch (error) {
                console.error('❌ Fallback initialization failed:', error);
            }
        }
    }
    
    // Функция инициализации с защитой от ошибок
    function initializeThemeSystem() {
        try {
            if (!window.themeSystemInstance) {
                window.themeSystemInstance = new RobustThemeSystem();
                window.ThemeSystemInitialized = true;
                console.log('🎉 Theme system fully initialized and ready!');
            }
        } catch (error) {
            console.error('❌ Critical error in theme system initialization:', error);
            // Последняя попытка - базовая функциональность
            window.toggleTheme = () => {
                const current = document.documentElement.getAttribute('data-theme') || 'light';
                const newTheme = current === 'light' ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                return newTheme;
            };
        }
    }
    
    // Инициализация с множественными точками входа
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeThemeSystem);
    } else {
        initializeThemeSystem();
    }
    
    // Резервная инициализация
    window.addEventListener('load', () => {
        if (!window.ThemeSystemInitialized) {
            console.log('🔄 Backup theme system initialization');
            initializeThemeSystem();
        }
    });
    
    console.log('🎨 Theme system script loaded successfully');
    
})();

// Стили для плавного переключения тем
if (!document.getElementById('theme-system-styles')) {
    const style = document.createElement('style');
    style.id = 'theme-system-styles';
    style.textContent = `
        /* Плавные переходы при смене темы */
        :root {
            --theme-transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }
        
        * {
            transition: var(--theme-transition);
        }
        
        /* Исключения для интерактивных элементов */
        .interactive-card,
        .card:hover,
        .module-card:hover,
        .subject-card:hover,
        [class*="hover"]:hover {
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                        box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                        var(--theme-transition) !important;
        }
        
        /* Стили для кнопок переключения темы */
        .theme-toggle,
        .theme-toggle-inline,
        [data-theme-toggle] {
            transition: all 0.2s ease !important;
        }
        
        .theme-toggle:hover,
        .theme-toggle-inline:hover,
        [data-theme-toggle]:hover {
            transform: scale(1.05);
        }
        
        /* Фокус для доступности */
        .theme-toggle:focus-visible,
        .theme-toggle-inline:focus-visible,
        [data-theme-toggle]:focus-visible {
            outline: 2px solid var(--primary-500, #3ECDC1);
            outline-offset: 2px;
        }
        
        /* Отключение анимаций для людей с ограниченными возможностями */
        @media (prefers-reduced-motion: reduce) {
            * {
                transition: none !important;
                animation: none !important;
            }
        }
    `;
    document.head.appendChild(style);
}
