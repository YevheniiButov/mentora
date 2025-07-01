/**
 * Modern Editor UI System
 * Современная система UI для редактора
 * Bilingual support: English/Russian
 * Поддержка двуязычия: Английский/Русский
 */

class ModernEditorUI {
    constructor(options = {}) {
        this.options = {
            defaultLanguage: 'en',
            defaultTheme: 'light',
            enableAnimations: true,
            enableKeyboardShortcuts: true,
            enableAutoSave: true,
            autoSaveInterval: 30000, // 30 seconds
            ...options
        };

        this.currentLanguage = this.options.defaultLanguage;
        this.currentTheme = this.options.defaultTheme;
        this.isInitialized = false;
        this.autoSaveTimer = null;
        this.contextMenus = new Map();
        this.modals = new Map();
        this.notifications = new Map();
        this.keyboardShortcuts = new Map();
        this.resizeObservers = new Map();

        // Translations
        this.translations = {
            en: {
                // Header
                'editor.title': 'Dental Academy Editor',
                'editor.save': 'Save',
                'editor.preview': 'Preview',
                'editor.deploy': 'Deploy',
                'editor.undo': 'Undo',
                'editor.redo': 'Redo',
                'editor.help': 'Help',
                'editor.settings': 'Settings',
                
                // Sidebar
                'sidebar.components': 'Components',
                'sidebar.styles': 'Styles',
                'sidebar.layers': 'Layers',
                'sidebar.blocks': 'Blocks',
                'sidebar.templates': 'Templates',
                'sidebar.assets': 'Assets',
                
                // Panels
                'panel.properties': 'Properties',
                'panel.styles': 'Styles',
                'panel.traits': 'Traits',
                'panel.layers': 'Layers',
                'panel.blocks': 'Blocks',
                'panel.devices': 'Devices',
                
                // Actions
                'action.save': 'Save Changes',
                'action.preview': 'Preview Template',
                'action.deploy': 'Deploy to Production',
                'action.undo': 'Undo Last Action',
                'action.redo': 'Redo Last Action',
                'action.help': 'Show Help',
                'action.settings': 'Open Settings',
                
                // Messages
                'message.saving': 'Saving...',
                'message.saved': 'Changes saved successfully',
                'message.error': 'An error occurred',
                'message.confirm': 'Are you sure?',
                'message.loading': 'Loading...',
                
                // Tooltips
                'tooltip.save': 'Save current changes',
                'tooltip.preview': 'Preview template',
                'tooltip.deploy': 'Deploy to production',
                'tooltip.undo': 'Undo last action',
                'tooltip.redo': 'Redo last action',
                'tooltip.help': 'Show help',
                'tooltip.settings': 'Open settings',
                'tooltip.theme': 'Toggle theme',
                'tooltip.language': 'Change language',
                
                // Settings
                'settings.title': 'Editor Settings',
                'settings.theme': 'Theme',
                'settings.language': 'Language',
                'settings.animations': 'Enable Animations',
                'settings.autoSave': 'Auto Save',
                'settings.keyboardShortcuts': 'Keyboard Shortcuts',
                'settings.accessibility': 'Accessibility',
                
                // Help
                'help.title': 'Editor Help',
                'help.shortcuts': 'Keyboard Shortcuts',
                'help.tour': 'Take Tour',
                'help.documentation': 'Documentation',
                
                // Notifications
                'notification.success': 'Success',
                'notification.warning': 'Warning',
                'notification.error': 'Error',
                'notification.info': 'Information'
            },
            ru: {
                // Header
                'editor.title': 'Редактор Dental Academy',
                'editor.save': 'Сохранить',
                'editor.preview': 'Предпросмотр',
                'editor.deploy': 'Развернуть',
                'editor.undo': 'Отменить',
                'editor.redo': 'Повторить',
                'editor.help': 'Помощь',
                'editor.settings': 'Настройки',
                
                // Sidebar
                'sidebar.components': 'Компоненты',
                'sidebar.styles': 'Стили',
                'sidebar.layers': 'Слои',
                'sidebar.blocks': 'Блоки',
                'sidebar.templates': 'Шаблоны',
                'sidebar.assets': 'Ресурсы',
                
                // Panels
                'panel.properties': 'Свойства',
                'panel.styles': 'Стили',
                'panel.traits': 'Характеристики',
                'panel.layers': 'Слои',
                'panel.blocks': 'Блоки',
                'panel.devices': 'Устройства',
                
                // Actions
                'action.save': 'Сохранить изменения',
                'action.preview': 'Предпросмотр шаблона',
                'action.deploy': 'Развернуть в продакшн',
                'action.undo': 'Отменить последнее действие',
                'action.redo': 'Повторить последнее действие',
                'action.help': 'Показать помощь',
                'action.settings': 'Открыть настройки',
                
                // Messages
                'message.saving': 'Сохранение...',
                'message.saved': 'Изменения сохранены успешно',
                'message.error': 'Произошла ошибка',
                'message.confirm': 'Вы уверены?',
                'message.loading': 'Загрузка...',
                
                // Tooltips
                'tooltip.save': 'Сохранить текущие изменения',
                'tooltip.preview': 'Предпросмотр шаблона',
                'tooltip.deploy': 'Развернуть в продакшн',
                'tooltip.undo': 'Отменить последнее действие',
                'tooltip.redo': 'Повторить последнее действие',
                'tooltip.help': 'Показать помощь',
                'tooltip.settings': 'Открыть настройки',
                'tooltip.theme': 'Переключить тему',
                'tooltip.language': 'Изменить язык',
                
                // Settings
                'settings.title': 'Настройки редактора',
                'settings.theme': 'Тема',
                'settings.language': 'Язык',
                'settings.animations': 'Включить анимации',
                'settings.autoSave': 'Автосохранение',
                'settings.keyboardShortcuts': 'Горячие клавиши',
                'settings.accessibility': 'Доступность',
                
                // Help
                'help.title': 'Помощь по редактору',
                'help.shortcuts': 'Горячие клавиши',
                'help.tour': 'Пройти тур',
                'help.documentation': 'Документация',
                
                // Notifications
                'notification.success': 'Успешно',
                'notification.warning': 'Предупреждение',
                'notification.error': 'Ошибка',
                'notification.info': 'Информация'
            }
        };

        this.init();
    }

    /**
     * Initialize the editor UI
     * Инициализация UI редактора
     */
    init() {
        if (this.isInitialized) return;

        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.setupResizeHandles();
        this.setupContextMenus();
        this.setupAutoSave();
        this.setupAccessibility();
        this.applyTheme(this.currentTheme);
        this.applyLanguage(this.currentLanguage);

        this.isInitialized = true;
        this.showNotification('info', this.t('message.loading'), 'Editor initialized successfully');
    }

    /**
     * Setup event listeners
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Theme toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="toggle-theme"]')) {
                this.toggleTheme();
            }
        });

        // Language toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="toggle-language"]')) {
                this.toggleLanguage();
            }
        });

        // Settings modal
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="open-settings"]')) {
                this.openSettings();
            }
        });

        // Help modal
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="open-help"]')) {
                this.openHelp();
            }
        });

        // Close modals
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-close, .modal-overlay')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });

        // Context menu
        document.addEventListener('contextmenu', (e) => {
            if (e.target.closest('.editor-main')) {
                e.preventDefault();
                this.showContextMenu(e);
            }
        });

        // Close context menus
        document.addEventListener('click', () => {
            this.closeAllContextMenus();
        });

        // Window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Before unload
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = this.t('message.confirm');
            }
        });
    }

    /**
     * Setup keyboard shortcuts
     * Настройка горячих клавиш
     */
    setupKeyboardShortcuts() {
        if (!this.options.enableKeyboardShortcuts) return;

        const shortcuts = {
            'ctrl+s': () => this.save(),
            'ctrl+z': () => this.undo(),
            'ctrl+y': () => this.redo(),
            'ctrl+shift+z': () => this.redo(),
            'ctrl+p': () => this.preview(),
            'ctrl+d': () => this.deploy(),
            'f1': () => this.openHelp(),
            'escape': () => this.closeAllModals(),
            'ctrl+,': () => this.openSettings()
        };

        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);
            const action = shortcuts[key];
            
            if (action) {
                e.preventDefault();
                action();
            }
        });
    }

    /**
     * Setup resize handles
     * Настройка элементов изменения размера
     */
    setupResizeHandles() {
        const handles = document.querySelectorAll('.resize-handle');
        
        handles.forEach(handle => {
            let isResizing = false;
            let startX, startWidth;

            handle.addEventListener('mousedown', (e) => {
                isResizing = true;
                startX = e.clientX;
                startWidth = this.getPanelWidth(handle);
                
                document.body.style.cursor = 'col-resize';
                document.body.style.userSelect = 'none';
                
                e.preventDefault();
            });

            document.addEventListener('mousemove', (e) => {
                if (!isResizing) return;
                
                const deltaX = e.clientX - startX;
                const newWidth = startWidth + deltaX;
                
                this.resizePanel(handle, newWidth);
            });

            document.addEventListener('mouseup', () => {
                if (isResizing) {
                    isResizing = false;
                    document.body.style.cursor = '';
                    document.body.style.userSelect = '';
                }
            });
        });
    }

    /**
     * Setup context menus
     * Настройка контекстных меню
     */
    setupContextMenus() {
        // Default context menu for canvas
        this.registerContextMenu('canvas', [
            { label: this.t('action.undo'), action: () => this.undo(), icon: '↶' },
            { label: this.t('action.redo'), action: () => this.redo(), icon: '↷' },
            { type: 'separator' },
            { label: this.t('action.save'), action: () => this.save(), icon: '💾' },
            { label: this.t('action.preview'), action: () => this.preview(), icon: '👁️' },
            { label: this.t('action.deploy'), action: () => this.deploy(), icon: '🚀' }
        ]);
    }

    /**
     * Setup auto save
     * Настройка автосохранения
     */
    setupAutoSave() {
        if (!this.options.enableAutoSave) return;

        this.autoSaveTimer = setInterval(() => {
            if (this.hasUnsavedChanges()) {
                this.autoSave();
            }
        }, this.options.autoSaveInterval);
    }

    /**
     * Setup accessibility features
     * Настройка функций доступности
     */
    setupAccessibility() {
        // Focus management
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
        });

        // Screen reader announcements
        this.setupScreenReaderAnnouncements();

        // High contrast mode detection
        this.setupHighContrastMode();
    }

    /**
     * Get key combination
     * Получение комбинации клавиш
     */
    getKeyCombo(e) {
        const keys = [];
        
        if (e.ctrlKey || e.metaKey) keys.push('ctrl');
        if (e.shiftKey) keys.push('shift');
        if (e.altKey) keys.push('alt');
        
        if (e.key !== 'Control' && e.key !== 'Shift' && e.key !== 'Alt') {
            keys.push(e.key.toLowerCase());
        }
        
        return keys.join('+');
    }

    /**
     * Get panel width
     * Получение ширины панели
     */
    getPanelWidth(handle) {
        const panel = handle.previousElementSibling || handle.nextElementSibling;
        return panel.offsetWidth;
    }

    /**
     * Resize panel
     * Изменение размера панели
     */
    resizePanel(handle, width) {
        const panel = handle.previousElementSibling || handle.nextElementSibling;
        const minWidth = 200;
        const maxWidth = window.innerWidth * 0.5;
        
        width = Math.max(minWidth, Math.min(maxWidth, width));
        panel.style.width = `${width}px`;
    }

    /**
     * Register context menu
     * Регистрация контекстного меню
     */
    registerContextMenu(id, items) {
        this.contextMenus.set(id, items);
    }

    /**
     * Show context menu
     * Показать контекстное меню
     */
    showContextMenu(e) {
        this.closeAllContextMenus();
        
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.style.left = `${e.clientX}px`;
        menu.style.top = `${e.clientY}px`;
        
        const items = this.contextMenus.get('canvas') || [];
        
        items.forEach(item => {
            if (item.type === 'separator') {
                const separator = document.createElement('div');
                separator.className = 'context-menu-separator';
                menu.appendChild(separator);
            } else {
                const menuItem = document.createElement('div');
                menuItem.className = 'context-menu-item';
                menuItem.innerHTML = `
                    <span class="context-menu-icon">${item.icon || ''}</span>
                    <span class="context-menu-label">${item.label}</span>
                `;
                menuItem.addEventListener('click', () => {
                    item.action();
                    this.closeAllContextMenus();
                });
                menu.appendChild(menuItem);
            }
        });
        
        document.body.appendChild(menu);
        
        // Close menu when clicking outside
        setTimeout(() => {
            document.addEventListener('click', () => this.closeAllContextMenus(), { once: true });
        }, 0);
    }

    /**
     * Close all context menus
     * Закрыть все контекстные меню
     */
    closeAllContextMenus() {
        document.querySelectorAll('.context-menu').forEach(menu => {
            menu.remove();
        });
    }

    /**
     * Show notification
     * Показать уведомление
     */
    showNotification(type, title, message, duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-header">
                <strong>${title}</strong>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">${message}</div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
        
        return notification;
    }

    /**
     * Create modal
     * Создать модальное окно
     */
    createModal(id, title, content, buttons = []) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">${title}</h2>
                    <button class="modal-close">×</button>
                </div>
                <div class="modal-body">${content}</div>
                ${buttons.length ? `
                    <div class="modal-footer">
                        ${buttons.map(btn => `
                            <button class="btn ${btn.class || 'btn-secondary'}" data-action="${btn.action}">
                                ${btn.label}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        this.modals.set(id, modal);
        
        // Setup event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal(modal);
        });
        
        buttons.forEach(btn => {
            modal.querySelector(`[data-action="${btn.action}"]`).addEventListener('click', () => {
                if (btn.handler) btn.handler();
                if (btn.close !== false) this.closeModal(modal);
            });
        });
        
        return modal;
    }

    /**
     * Close modal
     * Закрыть модальное окно
     */
    closeModal(modal) {
        if (modal && modal.parentElement) {
            modal.remove();
        }
    }

    /**
     * Close all modals
     * Закрыть все модальные окна
     */
    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            this.closeModal(modal);
        });
    }

    /**
     * Toggle theme
     * Переключить тему
     */
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        this.saveSettings();
    }

    /**
     * Apply theme
     * Применить тему
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
    }

    /**
     * Toggle language
     * Переключить язык
     */
    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'ru' : 'en';
        this.applyLanguage(this.currentLanguage);
        this.saveSettings();
    }

    /**
     * Apply language
     * Применить язык
     */
    applyLanguage(language) {
        document.documentElement.setAttribute('lang', language);
        document.documentElement.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
        this.currentLanguage = language;
        this.updateUIText();
    }

    /**
     * Update UI text
     * Обновить текст интерфейса
     */
    updateUIText() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.t(key);
        });
        
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
    }

    /**
     * Translate text
     * Перевод текста
     */
    t(key) {
        return this.translations[this.currentLanguage]?.[key] || 
               this.translations.en[key] || 
               key;
    }

    /**
     * Open settings modal
     * Открыть модальное окно настроек
     */
    openSettings() {
        const content = `
            <div class="settings-grid">
                <div class="form-group">
                    <label class="form-label">${this.t('settings.theme')}</label>
                    <select class="form-select" id="theme-select">
                        <option value="light" ${this.currentTheme === 'light' ? 'selected' : ''}>Light</option>
                        <option value="dark" ${this.currentTheme === 'dark' ? 'selected' : ''}>Dark</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">${this.t('settings.language')}</label>
                    <select class="form-select" id="language-select">
                        <option value="en" ${this.currentLanguage === 'en' ? 'selected' : ''}>English</option>
                        <option value="ru" ${this.currentLanguage === 'ru' ? 'selected' : ''}>Русский</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-checkbox">
                        <input type="checkbox" id="animations-toggle" ${this.options.enableAnimations ? 'checked' : ''}>
                        ${this.t('settings.animations')}
                    </label>
                </div>
                <div class="form-group">
                    <label class="form-checkbox">
                        <input type="checkbox" id="auto-save-toggle" ${this.options.enableAutoSave ? 'checked' : ''}>
                        ${this.t('settings.autoSave')}
                    </label>
                </div>
            </div>
        `;

        this.createModal('settings', this.t('settings.title'), content, [
            {
                label: this.t('editor.save'),
                class: 'btn-primary',
                action: 'save-settings',
                handler: () => this.saveSettings()
            },
            {
                label: this.t('editor.cancel'),
                class: 'btn-secondary',
                action: 'cancel-settings',
                handler: () => {}
            }
        ]);
    }

    /**
     * Open help modal
     * Открыть модальное окно помощи
     */
    openHelp() {
        const content = `
            <div class="help-content">
                <h3>${this.t('help.shortcuts')}</h3>
                <div class="shortcuts-grid">
                    <div class="shortcut-item">
                        <kbd>Ctrl+S</kbd>
                        <span>${this.t('action.save')}</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl+Z</kbd>
                        <span>${this.t('action.undo')}</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl+Y</kbd>
                        <span>${this.t('action.redo')}</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl+P</kbd>
                        <span>${this.t('action.preview')}</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>F1</kbd>
                        <span>${this.t('action.help')}</span>
                    </div>
                </div>
            </div>
        `;

        this.createModal('help', this.t('help.title'), content, [
            {
                label: this.t('help.tour'),
                class: 'btn-primary',
                action: 'start-tour',
                handler: () => this.startTour()
            },
            {
                label: this.t('editor.close'),
                class: 'btn-secondary',
                action: 'close-help',
                handler: () => {}
            }
        ]);
    }

    /**
     * Save settings
     * Сохранить настройки
     */
    saveSettings() {
        const theme = document.getElementById('theme-select')?.value || this.currentTheme;
        const language = document.getElementById('language-select')?.value || this.currentLanguage;
        const animations = document.getElementById('animations-toggle')?.checked || false;
        const autoSave = document.getElementById('auto-save-toggle')?.checked || false;

        this.applyTheme(theme);
        this.applyLanguage(language);
        this.options.enableAnimations = animations;
        this.options.enableAutoSave = autoSave;

        localStorage.setItem('editor-settings', JSON.stringify({
            theme,
            language,
            animations,
            autoSave
        }));

        this.showNotification('success', this.t('notification.success'), 'Settings saved successfully');
    }

    /**
     * Load settings
     * Загрузить настройки
     */
    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('editor-settings') || '{}');
            
            if (settings.theme) this.applyTheme(settings.theme);
            if (settings.language) this.applyLanguage(settings.language);
            if (settings.animations !== undefined) this.options.enableAnimations = settings.animations;
            if (settings.autoSave !== undefined) this.options.enableAutoSave = settings.autoSave;
        } catch (error) {
            console.warn('Failed to load settings:', error);
        }
    }

    /**
     * Start onboarding tour
     * Начать обучающий тур
     */
    startTour() {
        // Implementation for onboarding tour
        this.showNotification('info', 'Tour', 'Onboarding tour will be implemented here');
    }

    /**
     * Save changes
     * Сохранить изменения
     */
    save() {
        this.showNotification('info', this.t('message.saving'), 'Saving changes...');
        
        // Simulate save operation
        setTimeout(() => {
            this.showNotification('success', this.t('notification.success'), this.t('message.saved'));
        }, 1000);
    }

    /**
     * Auto save
     * Автосохранение
     */
    autoSave() {
        // Implementation for auto save
        console.log('Auto saving...');
    }

    /**
     * Preview template
     * Предпросмотр шаблона
     */
    preview() {
        this.showNotification('info', 'Preview', 'Opening preview...');
    }

    /**
     * Deploy template
     * Развернуть шаблон
     */
    deploy() {
        this.showNotification('info', 'Deploy', 'Deploying template...');
    }

    /**
     * Undo action
     * Отменить действие
     */
    undo() {
        // Implementation for undo
        this.showNotification('info', 'Undo', 'Undoing last action...');
    }

    /**
     * Redo action
     * Повторить действие
     */
    redo() {
        // Implementation for redo
        this.showNotification('info', 'Redo', 'Redoing last action...');
    }

    /**
     * Check for unsaved changes
     * Проверить наличие несохраненных изменений
     */
    hasUnsavedChanges() {
        // Implementation to check for unsaved changes
        return false;
    }

    /**
     * Handle resize
     * Обработка изменения размера
     */
    handleResize() {
        // Implementation for resize handling
        console.log('Window resized');
    }

    /**
     * Handle tab navigation
     * Обработка навигации по Tab
     */
    handleTabNavigation(e) {
        // Implementation for tab navigation
    }

    /**
     * Setup screen reader announcements
     * Настройка объявлений для экранного диктора
     */
    setupScreenReaderAnnouncements() {
        // Implementation for screen reader support
    }

    /**
     * Setup high contrast mode
     * Настройка режима высокой контрастности
     */
    setupHighContrastMode() {
        // Implementation for high contrast mode
    }

    /**
     * Debounce function
     * Функция debounce
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Destroy the editor UI
     * Уничтожить UI редактора
     */
    destroy() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
        }
        
        this.closeAllModals();
        this.closeAllContextMenus();
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeydown);
        document.removeEventListener('resize', this.handleResize);
        
        this.isInitialized = false;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.modernEditorUI = new ModernEditorUI({
        defaultLanguage: document.documentElement.lang || 'en',
        defaultTheme: 'light',
        enableAnimations: true,
        enableKeyboardShortcuts: true,
        enableAutoSave: true,
        autoSaveInterval: 30000
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernEditorUI;
} 