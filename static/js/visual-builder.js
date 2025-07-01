/**
 * Visual Page Builder - Improved JavaScript
 * Современный конструктор страниц для Dental Academy
 */

class VisualBuilder {
    constructor() {
        // Состояние приложения
        this.state = {
            theme: localStorage.getItem('vb-theme') || 'light',
            selectedElement: null,
            zoom: 1,
            gridSnap: false,
            previewMode: false
        };

        // История изменений
        this.history = {
            undoStack: [],
            redoStack: [],
            maxSteps: 50,
            isUndoRedoAction: false
        };

        // Счетчики
        this.counters = {
            element: 0,
            save: 0
        };

        // Настройки
        this.config = {
            autoSaveInterval: 30000, // 30 секунд
            notificationDuration: 3000,
            animationDuration: 300,
            maxFileSize: 10 * 1024 * 1024, // 10MB
            supportedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            supportedVideoTypes: ['video/mp4', 'video/webm', 'video/ogg']
        };

        // DOM элементы
        this.dom = {};

        // Инициализация
        this.init();
    }

    /**
     * Инициализация приложения
     */
    async init() {
        try {
            this.cacheDOMElements();
            this.setupTheme();
            this.setupEventListeners();
            this.setupDragAndDrop();
            this.setupKeyboardShortcuts();
            this.setupAutoSave();
            this.loadSavedContent();
            
            await this.initializeComponents();
            await this.initializeAdvancedStyleEditor();
            await this.initializeManagers();
            
            // Добавляем кнопки в toolbar
            this.addAdvancedStyleEditorButton();
            this.addFileBrowserButton();
            this.addHTMLButtons();
            
            // Загружаем настройки
            this.loadDragDropSettings();
            
            this.showNotification('Visual Builder успешно загружен', 'success');
            console.info('🎨 Visual Builder инициализирован');
        } catch (error) {
            console.error('❌ Ошибка инициализации Visual Builder:', error);
            this.showNotification('Ошибка инициализации приложения', 'error');
        }
    }

    /**
     * Инициализация компонентов
     */
    async initializeComponents() {
        try {
            // Инициализируем основные компоненты
            this.components = {
                text: new TextComponent(this),
                image: new ImageComponent(this),
                button: new ButtonComponent(this),
                video: new VideoComponent(this),
                form: new FormComponent(this),
                quiz: new QuizComponent(this),
                dentalChart: new DentalChartComponent(this)
            };
            
            console.info('🎨 Компоненты инициализированы');
        } catch (error) {
            console.error('❌ Ошибка инициализации компонентов:', error);
        }
    }

    /**
     * Инициализация Advanced Style Editor
     */
    async initializeAdvancedStyleEditor() {
        try {
            const { AdvancedStyleEditor } = await import('./visual-builder/advanced-style-editor.js');
            this.advancedStyleEditor = new AdvancedStyleEditor(this);
            
            // Добавляем кнопку в toolbar
            this.addAdvancedStyleEditorButton();
            
            console.info('🎨 Advanced Style Editor интегрирован');
        } catch (error) {
            console.error('❌ Ошибка инициализации Advanced Style Editor:', error);
        }
    }

    /**
     * Инициализация менеджеров
     */
    async initializeManagers() {
        try {
            // Media Manager
            const { MediaManager } = await import('./visual-builder/media-manager.js');
            this.mediaManager = new MediaManager(this);
            
            // Export Manager
            const { ExportManager } = await import('./visual-builder/export-manager.js');
            this.exportManager = new ExportManager(this);
            
            // Template Manager
            const { TemplateManager } = await import('./visual-builder/template-manager.js');
            this.templateManager = new TemplateManager(this);
            
            // File Browser
            const { FileBrowser } = await import('./visual-builder/file-browser.js');
            this.fileBrowser = new FileBrowser(this);
            
            // HTML Parser
            const { HTMLParser } = await import('./html-parser.js');
            this.htmlParser = new HTMLParser(this);
            
            // Visual Editor
            const { VisualEditor } = await import('./visual-editor.js');
            this.visualEditor = new VisualEditor(this);
            
            // Live Editor
            const { LiveEditor } = await import('./live-editor.js');
            this.liveEditor = new LiveEditor(this);
            
            // Component Library
            const { ComponentLibrary } = await import('./component-library.js');
            this.componentLibrary = new ComponentLibrary(this);
            
            // Drag & Drop Editor
            const { DragDropEditor } = await import('./drag-drop-editor.js');
            this.dragDropEditor = new DragDropEditor(this);
            
            // Undo/Redo Manager
            const { UndoRedoManager } = await import('./undo-redo-manager.js');
            this.undoRedoManager = new UndoRedoManager(this);
            
            // Keyboard Shortcuts Manager
            const { KeyboardShortcuts } = await import('./keyboard-shortcuts.js');
            this.keyboardShortcuts = new KeyboardShortcuts(this);
            
            // ПРОДВИНУТЫЕ РЕДАКТОРЫ
            // Advanced HTML Editor
            const { AdvancedHTMLEditor } = await import('./visual-builder/advanced-html-editor.js');
            this.htmlEditor = new AdvancedHTMLEditor(this);
            
            // Advanced Style Editor
            const { AdvancedStyleEditor } = await import('./visual-builder/advanced-style-editor.js');
            this.styleEditor = new AdvancedStyleEditor(this);
            
            // Responsive Design System
            const { ResponsiveDesign } = await import('./visual-builder/responsive-design.js');
            this.responsiveDesign = new ResponsiveDesign(this);
            
            console.info('🔧 Менеджеры инициализированы');
        } catch (error) {
            console.error('❌ Ошибка инициализации менеджеров:', error);
        }
    }

    /**
     * Добавление кнопки Advanced Style Editor в toolbar
     */
    addAdvancedStyleEditorButton() {
        const toolbarSection = this.dom.toolbar?.querySelector('.toolbar-section:last-child');
        if (toolbarSection) {
            const advancedBtn = document.createElement('button');
            advancedBtn.className = 'btn btn-secondary';
            advancedBtn.innerHTML = '<i class="bi bi-palette2"></i> Advanced';
            advancedBtn.title = 'Advanced Style Editor';
            advancedBtn.onclick = () => this.openAdvancedStyleEditor();
            
            // Вставляем перед последней кнопкой
            const lastBtn = toolbarSection.lastElementChild;
            if (lastBtn) {
                toolbarSection.insertBefore(advancedBtn, lastBtn);
            } else {
                toolbarSection.appendChild(advancedBtn);
            }
        }
    }

    /**
     * Добавление кнопки File Browser в toolbar
     */
    addFileBrowserButton() {
        const toolbarSection = this.dom.toolbar?.querySelector('.toolbar-section:last-child');
        if (toolbarSection) {
            const fileBrowserBtn = document.createElement('button');
            fileBrowserBtn.className = 'btn btn-secondary';
            fileBrowserBtn.innerHTML = '<i class="bi bi-folder2-open"></i> Files';
            fileBrowserBtn.title = 'File Browser';
            fileBrowserBtn.onclick = () => this.openFileBrowser();
            
            // Вставляем перед последней кнопкой
            const lastBtn = toolbarSection.lastElementChild;
            if (lastBtn) {
                toolbarSection.insertBefore(fileBrowserBtn, lastBtn);
            } else {
                toolbarSection.appendChild(fileBrowserBtn);
            }
        }
    }

    /**
     * Добавление кнопок HTML файлов в toolbar
     */
    addHTMLButtons() {
        const toolbarSection = this.dom.toolbar?.querySelector('.toolbar-section:last-child');
        if (toolbarSection) {
            // Кнопка открытия HTML файла
            const openHTMLBtn = document.createElement('button');
            openHTMLBtn.className = 'btn btn-secondary';
            openHTMLBtn.innerHTML = '<i class="bi bi-file-earmark-code"></i> HTML';
            openHTMLBtn.title = 'Открыть HTML файл';
            openHTMLBtn.onclick = () => this.loadHTMLFileFromBrowser();
            
            // Кнопка импорта HTML
            const importHTMLBtn = document.createElement('button');
            importHTMLBtn.className = 'btn btn-secondary';
            importHTMLBtn.innerHTML = '<i class="bi bi-upload"></i> Импорт';
            importHTMLBtn.title = 'Импорт HTML';
            importHTMLBtn.onclick = () => this.importExistingHTML();
            
            // Кнопка экспорта в HTML
            const exportHTMLBtn = document.createElement('button');
            exportHTMLBtn.className = 'btn btn-secondary';
            exportHTMLBtn.innerHTML = '<i class="bi bi-code-slash"></i> Экспорт';
            exportHTMLBtn.title = 'Экспорт в HTML';
            exportHTMLBtn.onclick = () => this.exportCanvasToHTML();
            
            // Кнопка сохранения файла
            const saveFileBtn = document.createElement('button');
            saveFileBtn.className = 'btn btn-success';
            saveFileBtn.innerHTML = '<i class="bi bi-save"></i> Сохранить';
            saveFileBtn.title = 'Сохранить файл (Ctrl+S)';
            saveFileBtn.onclick = () => this.saveCurrentFile();
            
            // Кнопка истории сохранений
            const saveHistoryBtn = document.createElement('button');
            saveHistoryBtn.className = 'btn btn-info';
            saveHistoryBtn.innerHTML = '<i class="bi bi-clock-history"></i> История';
            saveHistoryBtn.title = 'История сохранений';
            saveHistoryBtn.onclick = () => this.showSaveHistory();
            
            // Кнопка Component Library
            const componentLibraryBtn = document.createElement('button');
            componentLibraryBtn.className = 'btn btn-primary';
            componentLibraryBtn.innerHTML = '<i class="bi bi-puzzle"></i> Компоненты';
            componentLibraryBtn.title = 'Библиотека компонентов';
            componentLibraryBtn.onclick = () => this.openComponentLibrary();
            
            // Кнопка Drag & Drop настроек
            const dragDropBtn = document.createElement('button');
            dragDropBtn.className = 'btn btn-warning';
            dragDropBtn.innerHTML = '<i class="bi bi-arrows-move"></i> Drag & Drop';
            dragDropBtn.title = 'Настройки Drag & Drop';
            dragDropBtn.onclick = () => this.openDragDropSettings();
            
            // Кнопка Undo/Redo истории
            const undoRedoHistoryBtn = document.createElement('button');
            undoRedoHistoryBtn.className = 'btn btn-dark';
            undoRedoHistoryBtn.innerHTML = '<i class="bi bi-arrow-clockwise"></i> История';
            undoRedoHistoryBtn.title = 'История изменений (Ctrl+Z/Y)';
            undoRedoHistoryBtn.onclick = () => this.openUndoRedoHistory();
            
            // Кнопка горячих клавиш
            const keyboardShortcutsBtn = document.createElement('button');
            keyboardShortcutsBtn.className = 'btn btn-info';
            keyboardShortcutsBtn.innerHTML = '<i class="bi bi-keyboard"></i> Клавиши';
            keyboardShortcutsBtn.title = 'Горячие клавиши (Ctrl+Shift+K)';
            keyboardShortcutsBtn.onclick = () => this.openKeyboardShortcuts();
            
            // Кнопка продвинутого HTML редактора
            const advancedHTMLBtn = document.createElement('button');
            advancedHTMLBtn.className = 'btn btn-primary';
            advancedHTMLBtn.innerHTML = '<i class="bi bi-code-square"></i> HTML Editor';
            advancedHTMLBtn.title = 'Продвинутый HTML редактор';
            advancedHTMLBtn.onclick = () => this.openAdvancedHTMLEditor();
            
            // Кнопка продвинутого редактора стилей
            const advancedStyleBtn = document.createElement('button');
            advancedStyleBtn.className = 'btn btn-primary';
            advancedStyleBtn.innerHTML = '<i class="bi bi-palette2"></i> Style Editor';
            advancedStyleBtn.title = 'Продвинутый редактор стилей';
            advancedStyleBtn.onclick = () => this.openAdvancedStyleEditor();
            
            // Кнопка адаптивного дизайна
            const responsiveBtn = document.createElement('button');
            responsiveBtn.className = 'btn btn-success';
            responsiveBtn.innerHTML = '<i class="bi bi-phone"></i> Responsive';
            responsiveBtn.title = 'Адаптивный дизайн';
            responsiveBtn.onclick = () => this.openResponsiveDesign();
            
            // Вставляем кнопки
            const lastBtn = toolbarSection.lastElementChild;
            if (lastBtn) {
                toolbarSection.insertBefore(responsiveBtn, lastBtn);
                toolbarSection.insertBefore(advancedStyleBtn, lastBtn);
                toolbarSection.insertBefore(advancedHTMLBtn, lastBtn);
                toolbarSection.insertBefore(keyboardShortcutsBtn, lastBtn);
                toolbarSection.insertBefore(undoRedoHistoryBtn, lastBtn);
                toolbarSection.insertBefore(dragDropBtn, lastBtn);
                toolbarSection.insertBefore(componentLibraryBtn, lastBtn);
                toolbarSection.insertBefore(saveHistoryBtn, lastBtn);
                toolbarSection.insertBefore(saveFileBtn, lastBtn);
                toolbarSection.insertBefore(exportHTMLBtn, lastBtn);
                toolbarSection.insertBefore(importHTMLBtn, lastBtn);
                toolbarSection.insertBefore(openHTMLBtn, lastBtn);
            } else {
                toolbarSection.appendChild(openHTMLBtn);
                toolbarSection.appendChild(importHTMLBtn);
                toolbarSection.appendChild(exportHTMLBtn);
                toolbarSection.appendChild(saveFileBtn);
                toolbarSection.appendChild(saveHistoryBtn);
                toolbarSection.appendChild(componentLibraryBtn);
                toolbarSection.appendChild(dragDropBtn);
                toolbarSection.appendChild(undoRedoHistoryBtn);
                toolbarSection.appendChild(keyboardShortcutsBtn);
                toolbarSection.appendChild(advancedHTMLBtn);
                toolbarSection.appendChild(advancedStyleBtn);
                toolbarSection.appendChild(responsiveBtn);
            }
        }
    }

    /**
     * Кэширование DOM элементов
     */
    cacheDOMElements() {
        this.dom = {
            builder: document.querySelector('.visual-builder'),
            canvas: document.getElementById('canvas'),
            layersList: document.getElementById('layers-list'),
            themeIcon: document.getElementById('theme-icon'),
            undoBtn: document.querySelector('[data-action="undo"]'),
            redoBtn: document.querySelector('[data-action="redo"]'),
            componentItems: document.querySelectorAll('.component-item'),
            toolbar: document.querySelector('.toolbar'),
            sidebar: document.querySelector('.sidebar'),
            layersPanel: document.querySelector('.layers-panel')
        };

        // Проверяем наличие обязательных элементов
        const required = ['builder', 'canvas'];
        const missing = required.filter(key => !this.dom[key]);
        
        if (missing.length > 0) {
            throw new Error(`Отсутствуют обязательные DOM элементы: ${missing.join(', ')}`);
        }
    }

    /**
     * Настройка темы
     */
    setupTheme() {
        this.applyTheme(this.state.theme);
        this.updateThemeIcon();
    }

    /**
     * Применение темы
     */
    applyTheme(theme) {
        if (!['light', 'dark'].includes(theme)) {
            theme = 'light';
        }

        this.state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('vb-theme', theme);
        this.updateThemeIcon();
    }

    /**
     * Переключение темы
     */
    toggleTheme() {
        const newTheme = this.state.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
        this.showNotification(`Тема изменена на ${newTheme === 'light' ? 'светлую' : 'темную'}`, 'info');
    }

    /**
     * Обновление иконки темы
     */
    updateThemeIcon() {
        if (this.dom.themeIcon) {
            this.dom.themeIcon.textContent = this.state.theme === 'light' ? '🌙' : '☀️';
        }
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Глобальные обработчики
        document.addEventListener('click', this.handleGlobalClick.bind(this));
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        
        // Изменение размера окна
        window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
        
        // Предотвращение потери данных при закрытии
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));

        // Обработчики для canvas
        if (this.dom.canvas) {
            this.dom.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
        }
    }

    /**
     * Глобальный обработчик кликов
     */
    handleGlobalClick(event) {
        const target = event.target;

        // Снятие выделения при клике вне элементов
        if (!target.closest('.draggable-element') && !target.closest('.element-controls')) {
            this.deselectAllElements();
        }

        // Обработка кликов по кнопкам
        if (target.closest('[data-action]')) {
            const action = target.closest('[data-action]').dataset.action;
            this.handleAction(action, event);
        }
    }

    /**
     * Глобальный обработчик клавиатуры
     */
    handleGlobalKeydown(event) {
        // Горячие клавиши
        if (event.ctrlKey || event.metaKey) {
            switch (event.key.toLowerCase()) {
                case 's':
                    event.preventDefault();
                    this.savePage();
                    break;
                case 'z':
                    event.preventDefault();
                    if (event.shiftKey) {
                        this.redo();
                    } else {
                        this.undo();
                    }
                    break;
                case 'y':
                    event.preventDefault();
                    this.redo();
                    break;
                case 'd':
                    event.preventDefault();
                    if (this.state.selectedElement) {
                        this.duplicateElement(this.state.selectedElement);
                    }
                    break;
                case 'a':
                    if (event.target === this.dom.canvas) {
                        event.preventDefault();
                        this.selectAllElements();
                    }
                    break;
            }
        }

        // Другие клавиши
        switch (event.key) {
            case 'Delete':
            case 'Backspace':
                if (this.state.selectedElement && event.target === document.body) {
                    event.preventDefault();
                    this.deleteElement(this.state.selectedElement);
                }
                break;
            case 'Escape':
                this.deselectAllElements();
                break;
        }
    }

    /**
     * Обработчик изменения размера окна
     */
    handleResize() {
        this.updateCanvasSize();
    }

    /**
     * Обработчик перед закрытием страницы
     */
    handleBeforeUnload(event) {
        if (this.hasUnsavedChanges()) {
            const message = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
            event.returnValue = message;
            return message;
        }
    }

    /**
     * Обработчик действий
     */
    handleAction(action, event) {
        const actions = {
            'undo': () => this.undo(),
            'redo': () => this.redo(),
            'save': () => this.savePage(),
            'preview': () => this.previewPage(),
            'export': () => this.exportPage(),
            'clear': () => this.clearCanvas(),
            'zoom-in': () => this.zoomIn(),
            'zoom-out': () => this.zoomOut(),
            'zoom-reset': () => this.resetZoom(),
            'toggle-theme': () => this.toggleTheme(),
            'toggle-grid': () => this.toggleGrid(),
            'toggle-snap': () => this.toggleSnap()
        };

        if (actions[action]) {
            actions[action]();
        } else {
            console.warn(`Unknown action: ${action}`);
        }
    }

    /**
     * Настройка drag & drop
     */
    setupDragAndDrop() {
        // Настройка для компонентов
        this.dom.componentItems.forEach(item => {
            this.setupComponentDragAndDrop(item);
        });

        // Настройка для canvas
        this.setupCanvasDragAndDrop();
    }

    /**
     * Настройка drag & drop для компонентов
     */
    setupComponentDragAndDrop(item) {
        item.addEventListener('dragstart', (event) => {
            const componentType = item.dataset.type;
            event.dataTransfer.setData('text/plain', componentType);
            event.dataTransfer.effectAllowed = 'copy';
            
            item.style.opacity = '0.5';
            this.showNotification('Перетащите компонент на холст', 'info');
        });

        item.addEventListener('dragend', () => {
            item.style.opacity = '1';
        });

        // Поддержка клавиатуры
        item.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.createElement(item.dataset.type);
            }
        });
    }

    /**
     * Настройка drag & drop для canvas
     */
    setupCanvasDragAndDrop() {
        this.dom.canvas.addEventListener('dragover', (event) => {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'copy';
            this.highlightDropZone(event);
        });

        this.dom.canvas.addEventListener('dragleave', (event) => {
            if (!this.dom.canvas.contains(event.relatedTarget)) {
                this.clearDropZoneHighlight();
            }
        });

        this.dom.canvas.addEventListener('drop', (event) => {
            event.preventDefault();
            const componentType = event.dataTransfer.getData('text/plain');
            
            if (componentType) {
                const rect = this.dom.canvas.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                
                this.createElement(componentType, { x, y });
            }
            
            this.clearDropZoneHighlight();
        });
    }

    /**
     * Подсветка зоны drop
     */
    highlightDropZone(event) {
        this.dom.canvas.style.background = 'rgba(102, 126, 234, 0.05)';
        this.dom.canvas.style.borderColor = 'var(--primary)';
    }

    /**
     * Очистка подсветки зоны drop
     */
    clearDropZoneHighlight() {
        this.dom.canvas.style.background = '';
        this.dom.canvas.style.borderColor = '';
    }

    /**
     * Настройка горячих клавиш
     */
    setupKeyboardShortcuts() {
        // Инициализация происходит в initializeManagers
        // Здесь только логируем
        console.info('⌨️ Горячие клавиши настроены');
    }

    /**
     * Настройка автосохранения
     */
    setupAutoSave() {
        setInterval(() => {
            this.autoSave();
        }, this.config.autoSaveInterval);
    }

    /**
     * Автосохранение
     */
    autoSave() {
        try {
            const content = this.getCanvasContent();
            localStorage.setItem('vb-autosave', JSON.stringify({
                content,
                timestamp: Date.now(),
                version: '1.0'
            }));
        } catch (error) {
            console.warn('Ошибка автосохранения:', error);
        }
    }

    /**
     * Загрузка сохраненного контента
     */
    loadSavedContent() {
        try {
            const saved = localStorage.getItem('vb-autosave');
            if (saved) {
                const data = JSON.parse(saved);
                if (data.content && data.content.trim()) {
                    this.setCanvasContent(data.content);
                    console.info('📄 Загружен автосохраненный контент');
                }
            }
        } catch (error) {
            console.warn('Ошибка загрузки сохраненного контента:', error);
        }
    }

    /**
     * Проверка наличия контента на canvas
     */
    hasCanvasContent() {
        return this.dom.canvas.querySelectorAll('.draggable-element').length > 0;
    }

    /**
     * Показ пустого состояния
     */
    showEmptyState() {
        if (!this.dom.canvas.querySelector('.canvas-empty')) {
            this.dom.canvas.innerHTML = `
                <div class="canvas-empty">
                    <div class="canvas-empty-icon">🎨</div>
                    <div>
                        <h3>Начните создавать страницу</h3>
                        <p>Перетащите компоненты из левой панели сюда</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Настройка существующих элементов
     */
    setupExistingElements() {
        this.dom.canvas.querySelectorAll('.draggable-element').forEach(element => {
            this.setupElementEvents(element);
        });
    }

    /**
     * Создание элемента
     */
    createElement(type, options = {}) {
        try {
            // Удаляем пустое состояние
            const emptyState = this.dom.canvas.querySelector('.canvas-empty');
            if (emptyState) {
                emptyState.remove();
            }

            // Создаем элемент
            const element = document.createElement('div');
            element.className = `draggable-element element-${type}`;
            element.dataset.type = type;
            element.dataset.id = `element_${++this.counters.element}`;

            // Позиционирование
            if (options.x !== undefined && options.y !== undefined) {
                element.style.position = 'absolute';
                element.style.left = `${options.x}px`;
                element.style.top = `${options.y}px`;
            }

            // Контент элемента
            const content = this.getElementContent(type);
            element.innerHTML = content;

            // Добавляем на canvas
            this.dom.canvas.appendChild(element);

            // Настраиваем обработчики
            this.setupElementEvents(element);

            // Выделяем новый элемент
            this.selectElement(element);

            // Обновляем состояние
            this.addToHistory();
            this.updateLayersPanel();

            // Анимация появления
            element.style.opacity = '0';
            element.style.transform = 'scale(0.8)';
            
            requestAnimationFrame(() => {
                element.style.transition = 'all 0.3s ease';
                element.style.opacity = '1';
                element.style.transform = 'scale(1)';
            });

            this.showNotification(`Создан элемент: ${this.getElementName(type)}`, 'success');
            return element;

        } catch (error) {
            console.error('Ошибка создания элемента:', error);
            this.showNotification('Ошибка создания элемента', 'error');
            return null;
        }
    }

    /**
     * Получение контента элемента по типу
     */
    getElementContent(type) {
        const templates = {
            'text': this.getTextTemplate(),
            'image': this.getImageTemplate(),
            'button': this.getButtonTemplate(),
            'video': this.getVideoTemplate(),
            'quiz': this.getQuizTemplate(),
            'form': this.getFormTemplate(),
            'hero': this.getHeroTemplate(),
            'feature': this.getFeatureTemplate()
        };

        return templates[type] || templates['text'];
    }

    /**
     * Шаблоны элементов
     */
    getTextTemplate() {
        return `
            <div class="element-content">
                <div contenteditable="true">
                    <h2>Заголовок</h2>
                    <p>Введите ваш текст здесь. Этот блок можно редактировать, просто кликните и начните печатать.</p>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getImageTemplate() {
        return `
            <div class="element-content">
                <div class="image-placeholder" onclick="visualBuilder.selectImage(this)">
                    <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer;">
                        <div style="font-size: 2rem; margin-bottom: 1rem;">📷</div>
                        <div>Нажмите для добавления изображения</div>
                        <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">
                            Поддерживаются: JPG, PNG, GIF, WebP
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getButtonTemplate() {
        return `
            <div class="element-content">
                <div style="text-align: center;">
                    <button contenteditable="true" style="padding: 12px 24px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;">
                        Кнопка
                    </button>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getVideoTemplate() {
        return `
            <div class="element-content">
                <div class="video-placeholder" onclick="visualBuilder.selectVideo(this)">
                    <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer;">
                        <div style="font-size: 2rem; margin-bottom: 1rem;">🎥</div>
                        <div>Нажмите для добавления видео</div>
                        <div style="font-size: 0.875rem; color: #666; margin-top: 0.5rem;">
                            Введите URL или загрузите файл
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getQuizTemplate() {
        return `
            <div class="element-content">
                <h3 contenteditable="true" style="margin-bottom: 1rem;">Вопрос теста</h3>
                <div class="quiz-options">
                    <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                        <input type="radio" name="quiz_${this.counters.element}" style="margin-right: 0.5rem;">
                        <span contenteditable="true">Вариант ответа 1</span>
                    </label>
                    <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                        <input type="radio" name="quiz_${this.counters.element}" style="margin-right: 0.5rem;">
                        <span contenteditable="true">Вариант ответа 2</span>
                    </label>
                    <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                        <input type="radio" name="quiz_${this.counters.element}" style="margin-right: 0.5rem;">
                        <span contenteditable="true">Вариант ответа 3</span>
                    </label>
                </div>
                <button onclick="visualBuilder.addQuizOption(this)" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--secondary); color: white; border: none; border-radius: 4px; cursor: pointer;">
                    + Добавить вариант
                </button>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getFormTemplate() {
        return `
            <div class="element-content">
                <form style="max-width: 500px; margin: 0 auto;">
                    <h3 contenteditable="true" style="margin-bottom: 1rem;">Форма обратной связи</h3>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Имя:</label>
                        <input type="text" placeholder="Введите ваше имя" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Email:</label>
                        <input type="email" placeholder="your@email.com" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Сообщение:</label>
                        <textarea placeholder="Введите ваше сообщение" rows="4" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical;"></textarea>
                    </div>
                    <button type="submit" style="padding: 0.75rem 1.5rem; background: var(--primary); color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500;">
                        Отправить
                    </button>
                </form>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getHeroTemplate() {
        return `
            <div class="element-content">
                <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; border-radius: 12px;">
                    <h1 contenteditable="true" style="font-size: 3rem; margin-bottom: 1rem; font-weight: bold;">
                        Добро пожаловать
                    </h1>
                    <p contenteditable="true" style="font-size: 1.25rem; margin-bottom: 2rem; opacity: 0.9; max-width: 600px; margin-left: auto; margin-right: auto;">
                        Создайте потрясающую страницу с помощью нашего интуитивного конструктора. Начните прямо сейчас!
                    </p>
                    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                        <button style="padding: 1rem 2rem; background: white; color: var(--primary); border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;">
                            Начать работу
                        </button>
                        <button style="padding: 1rem 2rem; background: transparent; color: white; border: 2px solid white; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;">
                            Узнать больше
                        </button>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getFeatureTemplate() {
        return `
            <div class="element-content">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2 contenteditable="true" style="font-size: 2rem; margin-bottom: 1rem;">Наши преимущества</h2>
                    <p contenteditable="true" style="color: #666; font-size: 1.125rem;">Почему выбирают именно нас</p>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
                        <h3 contenteditable="true" style="margin-bottom: 1rem;">Быстро</h3>
                        <p contenteditable="true" style="color: #666; line-height: 1.6;">Молниеносная скорость работы и загрузки</p>
                    </div>
                    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
                        <h3 contenteditable="true" style="margin-bottom: 1rem;">Надежно</h3>
                        <p contenteditable="true" style="color: #666; line-height: 1.6;">Максимальная безопасность ваших данных</p>
                    </div>
                    <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">🎨</div>
                        <h3 contenteditable="true" style="margin-bottom: 1rem;">Красиво</h3>
                        <p contenteditable="true" style="color: #666; line-height: 1.6;">Современный и привлекательный дизайн</p>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    /**
     * Шаблон элементов управления
     */
    getControlsTemplate() {
        return `
            <div class="element-controls">
                <button class="control-btn" onclick="visualBuilder.moveElement(this, 'up')" title="Переместить вверх" aria-label="Переместить вверх">
                    ↑
                </button>
                <button class="control-btn secondary" onclick="visualBuilder.duplicateElement(this)" title="Дублировать" aria-label="Дублировать">
                    📋
                </button>
                <button class="control-btn danger" onclick="visualBuilder.deleteElement(this)" title="Удалить" aria-label="Удалить">
                    🗑️
                </button>
            </div>
        `;
    }

    /**
     * Получение имени элемента по типу
     */
    getElementName(type) {
        const names = {
            'text': 'Текстовый блок',
            'image': 'Изображение',
            'button': 'Кнопка',
            'video': 'Видео',
            'quiz': 'Тест',
            'form': 'Форма',
            'hero': 'Hero секция',
            'feature': 'Блок преимуществ'
        };
        return names[type] || 'Элемент';
    }

    /**
     * Настройка событий для элемента
     */
    setupElementEvents(element) {
        // Клик для выделения
        element.addEventListener('click', (event) => {
            event.stopPropagation();
            this.selectElement(element);
        });

        // Двойной клик для редактирования
        element.addEventListener('dblclick', (event) => {
            event.stopPropagation();
            this.editElement(element);
        });

        // Обработка изменений в contenteditable
        const editableElements = element.querySelectorAll('[contenteditable="true"]');
        editableElements.forEach(editable => {
            editable.addEventListener('input', this.debounce(() => {
                this.addToHistory();
            }, 1000));

            editable.addEventListener('blur', () => {
                this.addToHistory();
            });
        });

        // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Добавляем перетаскивание и изменение размера
        this.setupElementDrag(element);
        this.addResizeHandles(element);
    }

    /**
     * Выделение элемента
     */
    selectElement(element) {
        this.deselectAllElements();
        element.classList.add('selected');
        this.state.selectedElement = element;
        this.updateLayersPanel();
        this.updatePropertiesPanel();
        
        // Уведомляем Advanced Style Editor о выборе элемента
        if (this.advancedStyleEditor) {
            this.advancedStyleEditor.selectElement(element);
        }
        
        // Скроллим к элементу, если он не видим
        element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Снятие выделения со всех элементов
     */
    deselectAllElements() {
        this.dom.canvas.querySelectorAll('.draggable-element').forEach(el => {
            el.classList.remove('selected');
        });
        this.state.selectedElement = null;
        this.updateLayersPanel();
    }

    /**
     * Выделение всех элементов
     */
    selectAllElements() {
        const elements = this.dom.canvas.querySelectorAll('.draggable-element');
        elements.forEach(el => el.classList.add('selected'));
        this.showNotification(`Выделено элементов: ${elements.length}`, 'info');
    }

    /**
     * Редактирование элемента
     */
    editElement(element) {
        const editableElement = element.querySelector('[contenteditable="true"]');
        if (editableElement) {
            editableElement.focus();
            
            // Выделяем весь текст
            const range = document.createRange();
            range.selectNodeContents(editableElement);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    /**
     * Перемещение элемента
     */
    moveElement(button, direction) {
        const element = button.closest('.draggable-element');
        if (!element) return;

        const canvas = this.dom.canvas;
        
        if (direction === 'up' && element.previousElementSibling) {
            canvas.insertBefore(element, element.previousElementSibling);
        } else if (direction === 'down' && element.nextElementSibling) {
            canvas.insertBefore(element.nextElementSibling, element);
        }
        
        this.addToHistory();
        this.updateLayersPanel();
        this.showNotification(`Элемент перемещен ${direction === 'up' ? 'вверх' : 'вниз'}`, 'info');
    }

    /**
     * Дублирование элемента
     */
    duplicateElement(buttonOrElement) {
        const element = buttonOrElement.closest ? 
            buttonOrElement.closest('.draggable-element') : 
            buttonOrElement;
            
        if (!element) return;

        const clone = element.cloneNode(true);
        
        // Обновляем ID
        clone.dataset.id = `element_${++this.counters.element}`;
        
        // Сбрасываем состояние
        clone.classList.remove('selected');
        
        // Вставляем после оригинала
        element.parentNode.insertBefore(clone, element.nextSibling);
        
        // Настраиваем обработчики для клона
        this.setupElementEvents(clone);
        
        // Выделяем клон
        this.selectElement(clone);
        
        this.addToHistory();
        this.updateLayersPanel();
        this.showNotification('Элемент продублирован', 'success');
    }

    /**
     * Удаление элемента
     */
    deleteElement(buttonOrElement) {
        const element = buttonOrElement.closest ? 
            buttonOrElement.closest('.draggable-element') : 
            buttonOrElement;
            
        if (!element) return;

        // Подтверждение удаления
        if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
            return;
        }

        // Анимация удаления
        element.style.transition = 'all 0.3s ease';
        element.style.opacity = '0';
        element.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            element.remove();
            
            // Проверяем, нужно ли показать пустое состояние
            if (!this.hasCanvasContent()) {
                this.showEmptyState();
            }
            
            this.addToHistory();
            this.updateLayersPanel();
            this.showNotification('Элемент удален', 'warning');
        }, this.config.animationDuration);
    }

    /**
     * Обновление панели слоев
     */
    updateLayersPanel() {
        if (!this.dom.layersList) return;

        const elements = this.dom.canvas.querySelectorAll('.draggable-element');
        
        if (elements.length === 0) {
            this.dom.layersList.innerHTML = `
                <div style="text-align: center; color: var(--text-secondary); padding: 2rem; font-style: italic;">
                    Нет элементов
                </div>
            `;
            return;
        }

        this.dom.layersList.innerHTML = '';
        
        elements.forEach((element, index) => {
            const layerItem = this.createLayerItem(element, index);
            this.dom.layersList.appendChild(layerItem);
        });
    }

    /**
     * Создание элемента слоя
     */
    createLayerItem(element, index) {
        const layerItem = document.createElement('div');
        layerItem.className = 'layer-item';
        layerItem.dataset.elementIndex = index;
        
        if (element.classList.contains('selected')) {
            layerItem.classList.add('selected');
        }
        
        const elementType = element.dataset.type;
        const elementName = this.getElementName(elementType);
        
        layerItem.innerHTML = `
            <div class="layer-visibility">
                <input type="checkbox" checked onchange="visualBuilder.toggleElementVisibility(${index}, this.checked)" aria-label="Видимость слоя">
            </div>
            <div class="layer-info">
                <div class="layer-name">${elementName}</div>
                <div class="layer-type">${elementType}</div>
            </div>
            <div class="layer-actions">
                <button onclick="visualBuilder.selectLayerElement(${index})" title="Выбрать" aria-label="Выбрать элемент">👆</button>
                <button onclick="visualBuilder.moveLayerElement(${index}, 'up')" title="Вверх" aria-label="Переместить вверх">⬆️</button>
                <button onclick="visualBuilder.moveLayerElement(${index}, 'down')" title="Вниз" aria-label="Переместить вниз">⬇️</button>
            </div>
        `;
        
        // Обработчик клика по слою
        layerItem.addEventListener('click', () => {
            this.selectLayerElement(index);
        });
        
        return layerItem;
    }

    /**
     * Переключение видимости элемента
     */
    toggleElementVisibility(index, visible) {
        const elements = this.dom.canvas.querySelectorAll('.draggable-element');
        if (elements[index]) {
            elements[index].style.display = visible ? 'block' : 'none';
            this.addToHistory();
        }
    }

    /**
     * Выбор элемента из панели слоев
     */
    selectLayerElement(index) {
        const elements = this.dom.canvas.querySelectorAll('.draggable-element');
        if (elements[index]) {
            this.selectElement(elements[index]);
        }
    }

    /**
     * Перемещение элемента из панели слоев
     */
    moveLayerElement(index, direction) {
        const elements = this.dom.canvas.querySelectorAll('.draggable-element');
        const element = elements[index];
        
        if (!element) return;
        
        if (direction === 'up' && index > 0) {
            this.dom.canvas.insertBefore(element, elements[index - 1]);
        } else if (direction === 'down' && index < elements.length - 1) {
            this.dom.canvas.insertBefore(elements[index + 1], element);
        }
        
        this.addToHistory();
        this.updateLayersPanel();
    }

    /**
     * Управление историей изменений
     */
    addToHistory() {
        if (this.undoRedoManager) {
            this.undoRedoManager.saveStateDelayed('content_change');
        }
    }

    /**
     * Отмена действия
     */
    undo() {
        if (this.undoRedoManager) {
            this.undoRedoManager.undo();
        }
    }

    /**
     * Повтор действия
     */
    redo() {
        if (this.undoRedoManager) {
            this.undoRedoManager.redo();
        }
    }

    /**
     * Обновление кнопок отмены/повтора
     */
    updateUndoRedoButtons() {
        if (this.undoRedoManager) {
            this.undoRedoManager.updateUI();
        }
    }

    /**
     * Получение контента canvas
     */
    getCanvasContent() {
        return this.dom.canvas.innerHTML;
    }

    /**
     * Установка контента canvas
     */
    setCanvasContent(content) {
        this.dom.canvas.innerHTML = content;
        this.setupExistingElements();
        
        if (!this.hasCanvasContent()) {
            this.showEmptyState();
        }
    }

    /**
     * Очистка canvas
     */
    clearCanvas() {
        if (!confirm('Вы уверены, что хотите очистить холст? Все несохраненные изменения будут потеряны.')) {
            return;
        }

        this.showEmptyState();
        this.deselectAllElements();
        this.addToHistory();
        this.updateLayersPanel();
        this.showNotification('Холст очищен', 'warning');
    }

    /**
     * Сохранение страницы
     */
    savePage() {
        try {
            const content = this.getCanvasContent();
            const saveData = {
                content,
                timestamp: Date.now(),
                version: '1.0',
                saveNumber: ++this.counters.save
            };
            
            localStorage.setItem('vb-save', JSON.stringify(saveData));
            this.showNotification('Страница сохранена', 'success');
            
            console.info('💾 Страница сохранена:', saveData);
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showNotification('Ошибка сохранения страницы', 'error');
        }
    }

    /**
     * Предварительный просмотр
     */
    previewPage() {
        const content = this.getCanvasContent();
        
        // Очищаем контент от элементов редактирования
        const cleanContent = content
            .replace(/<div class="element-controls">[\s\S]*?<\/div>/g, '')
            .replace(/contenteditable="true"/g, '')
            .replace(/class="draggable-element[^"]*"/g, 'class="preview-element"')
            .replace(/onclick="[^"]*"/g, '');
        
        const previewWindow = window.open('', '_blank', 'width=1200,height=800');
        if (previewWindow) {
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html lang="ru">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Предварительный просмотр - Dental Academy</title>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                            line-height: 1.6; 
                            color: #333; 
                            background: #fff;
                        }
                        .preview-element { 
                            margin: 1rem 0; 
                            border: none !important; 
                            background: transparent !important;
                        }
                        .element-content { 
                            padding: 1rem; 
                        }
                        .preview-toolbar {
                            position: fixed;
                            top: 20px;
                            right: 20px;
                            background: #333;
                            color: white;
                            padding: 10px 20px;
                            border-radius: 8px;
                            z-index: 1000;
                            font-size: 14px;
                        }
                        .preview-toolbar button {
                            background: #007bff;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 4px;
                            cursor: pointer;
                            margin-left: 10px;
                        }
                    </style>
                </head>
                <body>
                    <div class="preview-toolbar">
                        📖 Предварительный просмотр
                        <button onclick="window.close()">Закрыть</button>
                    </div>
                    <div style="max-width: 1200px; margin: 0 auto; padding: 40px 20px;">
                        ${cleanContent}
                    </div>
                </body>
                </html>
            `);
            previewWindow.document.close();
        } else {
            this.showNotification('Не удалось открыть окно предпросмотра', 'error');
        }
    }

    /**
     * Экспорт страницы
     */
    exportPage() {
        try {
            const content = this.getCanvasContent();
            const cleanContent = content
                .replace(/<div class="element-controls">[\s\S]*?<\/div>/g, '')
                .replace(/contenteditable="true"/g, '')
                .replace(/onclick="[^"]*"/g, '');

            const html = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Экспортированная страница - Dental Academy</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
            line-height: 1.6; 
            color: #333; 
        }
        .draggable-element { margin: 1rem 0; }
        .element-content { padding: 1rem; }
    </style>
</head>
<body>
    <div style="max-width: 1200px; margin: 0 auto; padding: 20px;">
        ${cleanContent}
    </div>
</body>
</html>`;

            this.downloadFile(html, 'page.html', 'text/html');
            this.showNotification('Страница экспортирована', 'success');
        } catch (error) {
            console.error('Ошибка экспорта:', error);
            this.showNotification('Ошибка экспорта страницы', 'error');
        }
    }

    /**
     * Загрузка файла
     */
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }

    /**
     * Проверка несохраненных изменений
     */
    hasUnsavedChanges() {
        try {
            const currentContent = this.getCanvasContent();
            const saved = localStorage.getItem('vb-save');
            
            if (!saved) return true;
            
            const savedData = JSON.parse(saved);
            return currentContent !== savedData.content;
        } catch {
            return true;
        }
    }

    /**
     * Система уведомлений
     */
    showNotification(message, type = 'info', duration = null) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const titles = {
            success: 'Успешно',
            error: 'Ошибка',
            warning: 'Предупреждение',
            info: 'Информация'
        };
        
        notification.innerHTML = `
            <div class="notification-icon">${icons[type]}</div>
            <div class="notification-content">
                <div class="notification-title">${titles[type]}</div>
                <div class="notification-message">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Показываем уведомление
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });
        
        // Автоскрытие
        const hideTimeout = setTimeout(() => {
            this.hideNotification(notification);
        }, duration || this.config.notificationDuration);
        
        // Клик для скрытия
        notification.addEventListener('click', () => {
            clearTimeout(hideTimeout);
            this.hideNotification(notification);
        });
        
        return notification;
    }

    /**
     * Скрытие уведомления
     */
    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, this.config.animationDuration);
    }

    /**
     * Утилиты
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
     * Обновление размера canvas
     */
    updateCanvasSize() {
        // Реализация при необходимости
    }

    /**
     * Обработчик клика по canvas
     */
    handleCanvasClick(event) {
        // Если клик по пустому месту canvas
        if (event.target === this.dom.canvas) {
            this.deselectAllElements();
        }
    }

    // Дополнительные методы для работы с медиа
    
    /**
     * Выбор изображения
     */
    selectImage(placeholder) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = this.config.supportedImageTypes.join(',');
        
        input.onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                this.handleImageUpload(file, placeholder);
            }
        };
        
        input.click();
    }

    /**
     * Обработка загрузки изображения
     */
    handleImageUpload(file, placeholder) {
        // Проверка размера файла
        if (file.size > this.config.maxFileSize) {
            this.showNotification('Файл слишком большой. Максимальный размер: 10MB', 'error');
            return;
        }

        // Проверка типа файла
        if (!this.config.supportedImageTypes.includes(file.type)) {
            this.showNotification('Неподдерживаемый формат изображения', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            placeholder.innerHTML = `
                <img src="${e.target.result}" alt="Uploaded image" style="max-width: 100%; height: auto; border-radius: 8px;">
                <div style="margin-top: 10px; font-size: 0.875rem; color: #666;">
                    ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                </div>
            `;
            this.addToHistory();
            this.showNotification('Изображение загружено', 'success');
        };
        
        reader.onerror = () => {
            this.showNotification('Ошибка загрузки изображения', 'error');
        };
        
        reader.readAsDataURL(file);
    }

    /**
     * Выбор видео
     */
    selectVideo(placeholder) {
        const url = prompt('Введите URL видео (YouTube, Vimeo) или загрузите файл:');
        if (url) {
            this.handleVideoUrl(url, placeholder);
        } else {
            // Альтернативный способ - загрузка файла
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = this.config.supportedVideoTypes.join(',');
            
            input.onchange = (event) => {
                const file = event.target.files[0];
                if (file) {
                    this.handleVideoUpload(file, placeholder);
                }
            };
            
            input.click();
        }
    }

    /**
     * Обработка URL видео
     */
    handleVideoUrl(url, placeholder) {
        try {
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                const videoId = this.extractYouTubeId(url);
                if (videoId) {
                    placeholder.innerHTML = `
                        <iframe width="100%" height="315" src="https://www.youtube.com/embed/${videoId}" 
                                frameborder="0" allowfullscreen style="border-radius: 8px;"></iframe>
                    `;
                    this.addToHistory();
                    this.showNotification('YouTube видео добавлено', 'success');
                } else {
                    this.showNotification('Неверный URL YouTube', 'error');
                }
            } else if (url.includes('vimeo.com')) {
                const videoId = this.extractVimeoId(url);
                if (videoId) {
                    placeholder.innerHTML = `
                        <iframe width="100%" height="315" src="https://player.vimeo.com/video/${videoId}" 
                                frameborder="0" allowfullscreen style="border-radius: 8px;"></iframe>
                    `;
                    this.addToHistory();
                    this.showNotification('Vimeo видео добавлено', 'success');
                } else {
                    this.showNotification('Неверный URL Vimeo', 'error');
                }
            } else {
                // Прямая ссылка на видео
                placeholder.innerHTML = `
                    <video controls width="100%" style="border-radius: 8px;">
                        <source src="${url}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                `;
                this.addToHistory();
                this.showNotification('Видео добавлено', 'success');
            }
        } catch (error) {
            console.error('Ошибка обработки видео URL:', error);
            this.showNotification('Ошибка добавления видео', 'error');
        }
    }

    /**
     * Обработка загрузки видео файла
     */
    handleVideoUpload(file, placeholder) {
        if (file.size > this.config.maxFileSize) {
            this.showNotification('Файл слишком большой. Максимальный размер: 10MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            placeholder.innerHTML = `
                <video controls width="100%" style="border-radius: 8px;">
                    <source src="${e.target.result}" type="${file.type}">
                    Ваш браузер не поддерживает видео.
                </video>
                <div style="margin-top: 10px; font-size: 0.875rem; color: #666;">
                    ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                </div>
            `;
            this.addToHistory();
            this.showNotification('Видео загружено', 'success');
        };
        
        reader.readAsDataURL(file);
    }

    /**
     * Извлечение ID YouTube видео
     */
    extractYouTubeId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }

    /**
     * Извлечение ID Vimeo видео
     */
    extractVimeoId(url) {
        const regExp = /vimeo\.com\/([0-9]+)/;
        const match = url.match(regExp);
        return match ? match[1] : null;
    }

    /**
     * Добавление варианта ответа в тест
     */
    addQuizOption(button) {
        const quizElement = button.closest('.element-content');
        const optionsContainer = quizElement.querySelector('.quiz-options');
        const optionCount = optionsContainer.querySelectorAll('label').length + 1;
        const radioName = quizElement.querySelector('input[type="radio"]').name;
        
        const newOption = document.createElement('label');
        newOption.style.cssText = 'display: block; margin: 0.5rem 0; cursor: pointer;';
        newOption.innerHTML = `
            <input type="radio" name="${radioName}" style="margin-right: 0.5rem;">
            <span contenteditable="true">Вариант ответа ${optionCount}</span>
        `;
        
        optionsContainer.appendChild(newOption);
        this.addToHistory();
        this.showNotification('Вариант ответа добавлен', 'success');
    }

    /**
     * Открытие Advanced Style Editor
     */
    openAdvancedStyleEditor() {
        if (this.styleEditor) {
            if (this.state.selectedElement) {
                this.styleEditor.openStylePanel(this.state.selectedElement);
            } else {
                this.showNotification('Сначала выберите элемент для редактирования', 'warning');
            }
        } else {
            this.showNotification('Style Editor не загружен', 'error');
        }
    }

    /**
     * Открытие продвинутого HTML редактора
     */
    openAdvancedHTMLEditor() {
        if (this.htmlEditor) {
            // Если выбран элемент, редактируем его
            if (this.state.selectedElement) {
                this.htmlEditor.editElementHTML({ closest: () => this.state.selectedElement });
            } else {
                // Иначе показываем импорт HTML
                this.htmlEditor.importExistingHTML();
            }
        } else {
            this.showNotification('HTML Editor не загружен', 'error');
        }
    }

    /**
     * Открытие системы адаптивного дизайна
     */
    openResponsiveDesign() {
        if (this.responsiveDesign) {
            this.responsiveDesign.showResponsivePanel();
        } else {
            this.showNotification('Responsive Design не загружен', 'error');
        }
    }

    /**
     * Импорт существующего HTML
     */
    importExistingHTML() {
        if (this.htmlEditor) {
            this.htmlEditor.importExistingHTML();
        } else {
            this.showNotification('HTML Editor не загружен', 'error');
        }
    }

    /**
     * Редактирование стилей элемента
     */
    editElementStyles(controlBtn) {
        const element = controlBtn.closest('.draggable-element');
        if (this.styleEditor) {
            this.styleEditor.openStylePanel(element);
        } else {
            this.showNotification('Style Editor не загружен', 'error');
        }
    }

    /**
     * Редактирование HTML элемента
     */
    editElementHTML(controlBtn) {
        const element = controlBtn.closest('.draggable-element');
        if (this.htmlEditor) {
            this.htmlEditor.editElementHTML(controlBtn);
        } else {
            this.showNotification('HTML Editor не загружен', 'error');
        }
    }

    /**
     * Сделать элемент адаптивным
     */
    makeResponsive(controlBtn) {
        const element = controlBtn.closest('.draggable-element');
        if (this.responsiveDesign) {
            this.responsiveDesign.makeElementResponsive(element);
            this.showNotification('Элемент сделан адаптивным', 'success');
        } else {
            this.showNotification('Responsive Design не загружен', 'error');
        }
    }

    /**
     * Показать Box Model для выбранного элемента
     */
    showBoxModel() {
        if (this.state.selectedElement && this.advancedStyleEditor?.boxModel) {
            this.advancedStyleEditor.boxModel.showBoxModel(this.state.selectedElement);
        } else {
            this.showNotification('Сначала выберите элемент', 'warning');
        }
    }

    /**
     * Применение стилей к элементу
     */
    applyStylesToElement(element, styles) {
        if (!element || !styles) return;

        try {
            // Применяем CSS стили
            if (styles.css) {
                Object.assign(element.style, styles.css);
            }

            // Применяем CSS классы
            if (styles.classes) {
                element.className = styles.classes.join(' ');
            }

            // Применяем кастомные свойства
            if (styles.customProperties) {
                Object.entries(styles.customProperties).forEach(([property, value]) => {
                    element.style.setProperty(property, value);
                });
            }

            // Обновляем панель свойств
            this.updatePropertiesPanel();
            
            console.info('✅ Стили применены к элементу:', styles);
            
        } catch (error) {
            console.error('Ошибка применения стилей:', error);
            this.showNotification('Ошибка применения стилей', 'error');
        }
    }

    /**
     * Обновление панели свойств
     */
    updatePropertiesPanel() {
        const propertiesContent = document.getElementById('propertiesContent');
        if (!propertiesContent || !this.state.selectedElement) return;

        const element = this.state.selectedElement;
        const elementType = element.dataset.type;
        const elementName = this.getElementName(elementType);

        propertiesContent.innerHTML = `
            <div class="property-group">
                <h6 class="property-label">Элемент</h6>
                <p class="text-muted">${elementName} (${elementType})</p>
            </div>
            
            <div class="property-group">
                <h6 class="property-label">Основные стили</h6>
                <div class="property-row">
                    <div>
                        <label class="form-label">Ширина</label>
                        <input type="text" class="property-input" value="${element.style.width || ''}" 
                               onchange="visualBuilder.updateElementStyle('width', this.value)">
                    </div>
                    <div>
                        <label class="form-label">Высота</label>
                        <input type="text" class="property-input" value="${element.style.height || ''}" 
                               onchange="visualBuilder.updateElementStyle('height', this.value)">
                    </div>
                </div>
                <div class="property-row">
                    <div>
                        <label class="form-label">Отступ сверху</label>
                        <input type="text" class="property-input" value="${element.style.marginTop || ''}" 
                               onchange="visualBuilder.updateElementStyle('marginTop', this.value)">
                    </div>
                    <div>
                        <label class="form-label">Отступ снизу</label>
                        <input type="text" class="property-input" value="${element.style.marginBottom || ''}" 
                               onchange="visualBuilder.updateElementStyle('marginBottom', this.value)">
                    </div>
                </div>
            </div>
            
            <div class="property-group">
                <h6 class="property-label">Продвинутые настройки</h6>
                <button class="btn btn-primary btn-sm w-100" onclick="visualBuilder.openAdvancedStyleEditor()">
                    <i class="bi bi-palette2"></i>
                    Advanced Style Editor
                </button>
            </div>
        `;
    }

    /**
     * Обновление стиля элемента
     */
    updateElementStyle(property, value) {
        if (!this.state.selectedElement) return;
        
        this.state.selectedElement.style[property] = value;
        this.addToHistory();
        this.showNotification(`Стиль ${property} обновлен`, 'success');
    }

    /**
     * Открытие Media Manager
     */
    openMediaManager() {
        if (this.mediaManager) {
            this.mediaManager.openMediaLibrary();
        } else {
            this.showNotification('Media Manager не загружен', 'error');
        }
    }

    /**
     * Открытие Export Manager
     */
    openExportManager() {
        if (this.exportManager) {
            this.exportManager.openExportDialog();
        } else {
            this.showNotification('Export Manager не загружен', 'error');
        }
    }

    /**
     * Открытие Template Manager
     */
    openTemplateManager() {
        if (this.templateManager) {
            this.templateManager.openTemplateLibrary();
        } else {
            this.showNotification('Template Manager не загружен', 'error');
        }
    }

    /**
     * Открытие File Browser
     */
    openFileBrowser() {
        if (this.fileBrowser) {
            this.fileBrowser.open();
        } else {
            this.showNotification('File Browser не загружен', 'error');
        }
    }

    /**
     * Открытие HTML файла в Visual Editor
     */
    openHTMLFile(filePath) {
        if (this.visualEditor) {
            this.visualEditor.openFile(filePath);
        } else {
            this.showNotification('Visual Editor не загружен', 'error');
        }
    }

    /**
     * Парсинг HTML контента
     */
    parseHTMLContent(htmlContent, filename = '') {
        if (this.htmlParser) {
            const elements = this.htmlParser.parseHTMLToElements(htmlContent, filename);
            this.addElementsToCanvas(elements);
            this.showNotification(`HTML файл "${filename}" успешно распарсен`, 'success');
            return elements;
        } else {
            this.showNotification('HTML Parser не загружен', 'error');
            return [];
        }
    }

    /**
     * Добавление элементов на canvas
     */
    addElementsToCanvas(elements) {
        // Очищаем canvas
        this.dom.canvas.innerHTML = '';
        
        // Добавляем элементы
        elements.forEach(element => {
            this.dom.canvas.appendChild(element);
        });
        
        // Обновляем состояние
        this.updateLayersPanel();
        this.addToHistory();
        
        console.info(`✅ Добавлено ${elements.length} элементов на canvas`);
    }

    /**
     * Экспорт canvas в HTML
     */
    exportCanvasToHTML() {
        if (this.htmlParser) {
            const elements = this.dom.canvas.querySelectorAll('.draggable-element');
            const html = this.htmlParser.exportToHTML(elements);
            return html;
        } else {
            this.showNotification('HTML Parser не загружен', 'error');
            return '';
        }
    }

    /**
     * Загрузка HTML файла через File Browser
     */
    async loadHTMLFileFromBrowser() {
        if (this.fileBrowser) {
            // Открываем File Browser и ждем выбора файла
            this.fileBrowser.open();
            
            // Добавляем обработчик выбора файла
            this.fileBrowser.onFileSelect = (filePath) => {
                if (filePath.endsWith('.html') || filePath.endsWith('.htm')) {
                    this.openHTMLFile(filePath);
                } else {
                    this.showNotification('Выберите HTML файл', 'warning');
                }
            };
        } else {
            this.showNotification('File Browser не загружен', 'error');
        }
    }

    /**
     * Сохранение текущего файла
     */
    async saveCurrentFile() {
        if (this.liveEditor) {
            try {
                await this.liveEditor.saveFile();
                this.showNotification('Файл сохранен успешно', 'success');
            } catch (error) {
                console.error('Ошибка сохранения файла:', error);
                this.showNotification('Ошибка сохранения файла', 'error');
            }
        } else {
            this.showNotification('Live Editor не загружен', 'error');
        }
    }

    /**
     * Показать историю сохранений
     */
    showSaveHistory() {
        if (this.liveEditor) {
            const history = this.liveEditor.state.saveHistory;
            this.showSaveHistoryModal(history);
        } else {
            this.showNotification('Live Editor не загружен', 'error');
        }
    }

    /**
     * Показать модальное окно истории сохранений
     */
    showSaveHistoryModal(history) {
        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.className = 'save-history';
        modal.innerHTML = `
            <div class="save-history-header">
                <h3 class="save-history-title">
                    <i class="bi bi-clock-history"></i>
                    История сохранений
                </h3>
                <button class="save-history-close" onclick="this.closest('.save-history').remove()">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
            <div class="save-history-body">
                ${this.generateSaveHistoryHTML(history)}
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'block';
        });
    }

    /**
     * Генерация HTML для истории сохранений
     */
    generateSaveHistoryHTML(history) {
        if (!history || history.length === 0) {
            return `
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <i class="bi bi-clock-history" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>История сохранений пуста</p>
                </div>
            `;
        }
        
        return history.map(save => `
            <div class="save-history-item ${save.success ? 'success' : 'error'}">
                <div class="save-history-icon">
                    <i class="bi ${save.success ? 'bi-check-lg' : 'bi-x-lg'}"></i>
                </div>
                <div class="save-history-info">
                    <div class="save-history-file">${save.filepath || 'Неизвестный файл'}</div>
                    <div class="save-history-time">${new Date(save.timestamp).toLocaleString()}</div>
                </div>
                <div class="save-history-type">
                    ${save.isAutoSave ? 'Автосохранение' : 'Ручное сохранение'}
                </div>
            </div>
        `).join('');
    }

    /**
     * Установка текущего файла для редактирования
     */
    setCurrentFile(filePath) {
        if (this.liveEditor) {
            this.liveEditor.setCurrentFile(filePath);
            this.showNotification(`Открыт файл: ${filePath}`, 'info');
        }
    }

    /**
     * Проверка несохраненных изменений
     */
    hasUnsavedChanges() {
        if (this.liveEditor) {
            return this.liveEditor.hasUnsavedChanges();
        }
        return false;
    }

    /**
     * Принудительное сохранение всех изменений
     */
    async forceSaveAll() {
        if (this.liveEditor) {
            try {
                await this.liveEditor.forceSave();
                this.showNotification('Все изменения сохранены', 'success');
            } catch (error) {
                console.error('Ошибка принудительного сохранения:', error);
                this.showNotification('Ошибка сохранения изменений', 'error');
            }
        }
    }

    /**
     * Открытие Component Library
     */
    openComponentLibrary() {
        if (this.componentLibrary) {
            this.showComponentLibraryModal();
        } else {
            this.showNotification('Component Library не загружена', 'error');
        }
    }

    /**
     * Показать модальное окно Component Library
     */
    showComponentLibraryModal() {
        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.className = 'component-library-modal';
        modal.innerHTML = `
            <div class="component-library-content">
                <div class="component-library-header">
                    <h3 class="component-library-title">
                        <i class="bi bi-puzzle"></i>
                        Библиотека компонентов
                    </h3>
                    <button class="component-library-close" onclick="this.closest('.component-library-modal').remove()">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="component-library-controls">
                    <div class="component-search">
                        <input type="text" id="componentSearch" placeholder="Поиск компонентов...">
                    </div>
                    <div class="category-filter">
                        <select id="categoryFilter">
                            <option value="all">Все категории</option>
                            <option value="text">Текст</option>
                            <option value="media">Медиа</option>
                            <option value="interactive">Интерактивные</option>
                            <option value="layout">Макет</option>
                            <option value="dental">Стоматология</option>
                        </select>
                    </div>
                </div>
                <div class="component-grid" id="componentGrid">
                    <!-- Компоненты будут добавлены динамически -->
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'block';
        });
        
        // Инициализируем Component Library
        if (this.componentLibrary) {
            this.componentLibrary.renderComponentGrid();
        }
    }

    /**
     * Открытие настроек Drag & Drop
     */
    openDragDropSettings() {
        if (this.dragDropEditor) {
            this.showDragDropSettingsModal();
        } else {
            this.showNotification('Drag & Drop Editor не загружен', 'error');
        }
    }

    /**
     * Показать модальное окно настроек Drag & Drop
     */
    showDragDropSettingsModal() {
        const config = this.dragDropEditor.getConfig();
        
        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.className = 'drag-drop-settings-modal';
        modal.innerHTML = `
            <div class="drag-drop-settings-content">
                <div class="drag-drop-settings-header">
                    <h3 class="drag-drop-settings-title">
                        <i class="bi bi-arrows-move"></i>
                        Настройки Drag & Drop
                    </h3>
                    <button class="drag-drop-settings-close" onclick="this.closest('.drag-drop-settings-modal').remove()">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="drag-drop-settings-body">
                    <div class="settings-section">
                        <h4>Основные настройки</h4>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="dragPreview" ${config.dragPreview ? 'checked' : ''}>
                                Показывать превью при перетаскивании
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="dropZoneHighlight" ${config.dropZoneHighlight ? 'checked' : ''}>
                                Подсвечивать зоны drop
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="dropAnimation" ${config.dropAnimation ? 'checked' : ''}>
                                Анимация при drop
                            </label>
                        </div>
                    </div>
                    
                    <div class="settings-section">
                        <h4>Snap настройки</h4>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="snapToGrid" ${config.snapToGrid ? 'checked' : ''}>
                                Snap to grid
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="snapToElements" ${config.snapToElements ? 'checked' : ''}>
                                Snap к элементам
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                Порог snap (px):
                                <input type="range" id="snapThreshold" min="5" max="20" value="${config.snapThreshold}">
                                <span id="snapThresholdValue">${config.snapThreshold}</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="settings-section">
                        <h4>Множественное выделение</h4>
                        <div class="setting-item">
                            <label class="setting-label">
                                <input type="checkbox" id="multiSelect" ${config.multiSelect ? 'checked' : ''}>
                                Разрешить множественное выделение
                            </label>
                        </div>
                        <div class="setting-item">
                            <label class="setting-label">
                                Задержка drag (мс):
                                <input type="range" id="dragDelay" min="100" max="500" value="${config.dragDelay}">
                                <span id="dragDelayValue">${config.dragDelay}</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="settings-section">
                        <h4>Горячие клавиши</h4>
                        <div class="shortcuts-list">
                            <div class="shortcut-item">
                                <span class="shortcut-key">Shift</span>
                                <span class="shortcut-desc">Множественное выделение</span>
                            </div>
                            <div class="shortcut-item">
                                <span class="shortcut-key">Ctrl+G</span>
                                <span class="shortcut-desc">Переключить snap to grid</span>
                            </div>
                            <div class="shortcut-item">
                                <span class="shortcut-key">Escape</span>
                                <span class="shortcut-desc">Отменить перетаскивание</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="drag-drop-settings-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.drag-drop-settings-modal').remove()">
                        Отмена
                    </button>
                    <button class="btn btn-primary" onclick="visualBuilder.saveDragDropSettings()">
                        Сохранить настройки
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'block';
        });
        
        // Настраиваем обработчики для range inputs
        this.setupRangeInputs();
    }

    /**
     * Настройка range inputs
     */
    setupRangeInputs() {
        const snapThreshold = document.getElementById('snapThreshold');
        const snapThresholdValue = document.getElementById('snapThresholdValue');
        const dragDelay = document.getElementById('dragDelay');
        const dragDelayValue = document.getElementById('dragDelayValue');
        
        if (snapThreshold && snapThresholdValue) {
            snapThreshold.addEventListener('input', (e) => {
                snapThresholdValue.textContent = e.target.value;
            });
        }
        
        if (dragDelay && dragDelayValue) {
            dragDelay.addEventListener('input', (e) => {
                dragDelayValue.textContent = e.target.value;
            });
        }
    }

    /**
     * Сохранение настроек Drag & Drop
     */
    saveDragDropSettings() {
        if (!this.dragDropEditor) return;

        const newConfig = {
            dragPreview: document.getElementById('dragPreview')?.checked || false,
            dropZoneHighlight: document.getElementById('dropZoneHighlight')?.checked || false,
            dropAnimation: document.getElementById('dropAnimation')?.checked || false,
            snapToGrid: document.getElementById('snapToGrid')?.checked || false,
            snapToElements: document.getElementById('snapToElements')?.checked || false,
            multiSelect: document.getElementById('multiSelect')?.checked || false,
            snapThreshold: parseInt(document.getElementById('snapThreshold')?.value || '10'),
            dragDelay: parseInt(document.getElementById('dragDelay')?.value || '200')
        };

        this.dragDropEditor.updateConfig(newConfig);
        
        // Сохраняем в localStorage
        localStorage.setItem('vb-dragdrop-config', JSON.stringify(newConfig));
        
        this.showNotification('Настройки Drag & Drop сохранены', 'success');
        
        // Закрываем модальное окно
        const modal = document.querySelector('.drag-drop-settings-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Загрузка настроек Drag & Drop
     */
    loadDragDropSettings() {
        try {
            const saved = localStorage.getItem('vb-dragdrop-config');
            if (saved && this.dragDropEditor) {
                const config = JSON.parse(saved);
                this.dragDropEditor.updateConfig(config);
                console.info('⚙️ Настройки Drag & Drop загружены');
            }
        } catch (error) {
            console.warn('Ошибка загрузки настроек Drag & Drop:', error);
        }
    }

    /**
     * Открытие панели истории Undo/Redo
     */
    openUndoRedoHistory() {
        if (this.undoRedoManager) {
            this.undoRedoManager.showHistoryPanel();
        } else {
            this.showNotification('Undo/Redo Manager не загружен', 'error');
        }
    }

    /**
     * Открытие панели горячих клавиш
     */
    openKeyboardShortcuts() {
        if (this.keyboardShortcuts) {
            this.keyboardShortcuts.showShortcutsHelp();
        } else {
            this.showNotification('Keyboard Shortcuts Manager не загружен', 'error');
        }
    }

    /**
     * Настройка перетаскивания элемента
     */
    setupElementDrag(element) {
        let isDragging = false;
        let startX = 0;
        let startY = 0;
        let startLeft = 0;
        let startTop = 0;

        // Добавляем обработчик mousedown на элемент
        element.addEventListener('mousedown', (e) => {
            // Игнорируем клики по кнопкам управления
            if (e.target.closest('.element-controls button')) return;
            
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = parseInt(element.style.left) || 0;
            startTop = parseInt(element.style.top) || 0;

            element.classList.add('dragging');
            document.addEventListener('mousemove', handleDrag);
            document.addEventListener('mouseup', stopDrag);
            
            e.preventDefault();
        });

        const handleDrag = (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            let newLeft = startLeft + deltaX;
            let newTop = startTop + deltaY;

            // Snap to grid if enabled
            if (this.state.gridSnap) {
                const gridSize = 20;
                newLeft = Math.round(newLeft / gridSize) * gridSize;
                newTop = Math.round(newTop / gridSize) * gridSize;
            }

            element.style.left = `${newLeft}px`;
            element.style.top = `${newTop}px`;
        };

        const stopDrag = () => {
            if (!isDragging) return;
            
            isDragging = false;
            element.classList.remove('dragging');
            
            document.removeEventListener('mousemove', handleDrag);
            document.removeEventListener('mouseup', stopDrag);
            
            this.addToHistory();
        };
    }

    /**
     * Добавление handles для изменения размера
     */
    addResizeHandles(element) {
        // Проверяем, есть ли уже handles
        if (element.querySelector('.resize-handles')) return;

        const handles = document.createElement('div');
        handles.className = 'resize-handles';
        handles.innerHTML = `
            <div class="resize-handle nw" data-direction="nw"></div>
            <div class="resize-handle ne" data-direction="ne"></div>
            <div class="resize-handle sw" data-direction="sw"></div>
            <div class="resize-handle se" data-direction="se"></div>
            <div class="resize-handle n" data-direction="n"></div>
            <div class="resize-handle s" data-direction="s"></div>
            <div class="resize-handle w" data-direction="w"></div>
            <div class="resize-handle e" data-direction="e"></div>
        `;
        
        element.appendChild(handles);
        
        // Настраиваем обработчики resize
        this.setupResizeHandlers(element, handles);
    }

    /**
     * Настройка обработчиков изменения размера
     */
    setupResizeHandlers(element, handles) {
        let isResizing = false;
        let startX = 0;
        let startY = 0;
        let startWidth = 0;
        let startHeight = 0;
        let startLeft = 0;
        let startTop = 0;
        let direction = '';

        const startResize = (e) => {
            if (!e.target.classList.contains('resize-handle')) return;
            
            isResizing = true;
            direction = e.target.dataset.direction;
            
            const rect = element.getBoundingClientRect();
            startX = e.clientX;
            startY = e.clientY;
            startWidth = rect.width;
            startHeight = rect.height;
            startLeft = parseInt(element.style.left) || 0;
            startTop = parseInt(element.style.top) || 0;

            element.classList.add('resizing');
            
            document.addEventListener('mousemove', handleResize);
            document.addEventListener('mouseup', stopResize);
            
            e.preventDefault();
            e.stopPropagation();
        };

        const handleResize = (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            let newWidth = startWidth;
            let newHeight = startHeight;
            let newLeft = startLeft;
            let newTop = startTop;

            // Рассчитываем новые размеры в зависимости от направления
            switch (direction) {
                case 'se': // Правый нижний угол
                    newWidth = Math.max(50, startWidth + deltaX);
                    newHeight = Math.max(30, startHeight + deltaY);
                    break;
                case 'sw': // Левый нижний угол
                    newWidth = Math.max(50, startWidth - deltaX);
                    newHeight = Math.max(30, startHeight + deltaY);
                    newLeft = startLeft + deltaX;
                    break;
                case 'ne': // Правый верхний угол
                    newWidth = Math.max(50, startWidth + deltaX);
                    newHeight = Math.max(30, startHeight - deltaY);
                    newTop = startTop + deltaY;
                    break;
                case 'nw': // Левый верхний угол
                    newWidth = Math.max(50, startWidth - deltaX);
                    newHeight = Math.max(30, startHeight - deltaY);
                    newLeft = startLeft + deltaX;
                    newTop = startTop + deltaY;
                    break;
                case 'e': // Правая сторона
                    newWidth = Math.max(50, startWidth + deltaX);
                    break;
                case 'w': // Левая сторона
                    newWidth = Math.max(50, startWidth - deltaX);
                    newLeft = startLeft + deltaX;
                    break;
                case 's': // Нижняя сторона
                    newHeight = Math.max(30, startHeight + deltaY);
                    break;
                case 'n': // Верхняя сторона
                    newHeight = Math.max(30, startHeight - deltaY);
                    newTop = startTop + deltaY;
                    break;
            }

            // Применяем новые размеры и позицию
            element.style.width = `${newWidth}px`;
            element.style.height = `${newHeight}px`;
            element.style.left = `${newLeft}px`;
            element.style.top = `${newTop}px`;
        };

        const stopResize = () => {
            if (!isResizing) return;
            
            isResizing = false;
            element.classList.remove('resizing');
            
            document.removeEventListener('mousemove', handleResize);
            document.removeEventListener('mouseup', stopResize);
            
            this.addToHistory();
        };

        // Добавляем обработчики на все handles
        handles.querySelectorAll('.resize-handle').forEach(handle => {
            handle.addEventListener('mousedown', startResize);
        });
    }
}

// Глобальные функции для обратной совместимости
let visualBuilder;

// Функции управления темой
function toggleTheme() {
    if (visualBuilder) {
        visualBuilder.toggleTheme();
    }
}

// Функции управления элементами
function moveElement(button, direction) {
    if (visualBuilder) {
        visualBuilder.moveElement(button, direction);
    }
}

function duplicateElement(button) {
    if (visualBuilder) {
        visualBuilder.duplicateElement(button);
    }
}

function deleteElement(button) {
    if (visualBuilder) {
        visualBuilder.deleteElement(button);
    }
}

// Функции управления холстом
function clearCanvas() {
    if (visualBuilder) {
        visualBuilder.clearCanvas();
    }
}

function savePage() {
    if (visualBuilder) {
        visualBuilder.savePage();
    }
}

function previewPage() {
    if (visualBuilder) {
        visualBuilder.previewPage();
    }
}

function exportPage() {
    if (visualBuilder) {
        visualBuilder.exportPage();
    }
}

// Функции истории
function undo() {
    if (visualBuilder) {
        visualBuilder.undo();
    }
}

function redo() {
    if (visualBuilder) {
        visualBuilder.redo();
    }
}

// Функции зума
function zoomIn() {
    if (visualBuilder) {
        visualBuilder.showNotification('Увеличение масштаба', 'info');
    }
}

function zoomOut() {
    if (visualBuilder) {
        visualBuilder.showNotification('Уменьшение масштаба', 'info');
    }
}

function resetZoom() {
    if (visualBuilder) {
        visualBuilder.showNotification('Масштаб сброшен', 'info');
    }
}

// Функции слоев
function toggleElementVisibility(index, visible) {
    if (visualBuilder) {
        visualBuilder.toggleElementVisibility(index, visible);
    }
}

function selectLayerElement(index) {
    if (visualBuilder) {
        visualBuilder.selectLayerElement(index);
    }
}

function moveLayerElement(index, direction) {
    if (visualBuilder) {
        visualBuilder.moveLayerElement(index, direction);
    }
}

function toggleLayersPanel() {
    const panel = document.querySelector('.layers-panel');
    const content = document.getElementById('layers-content');
    
    if (content) {
        content.style.display = content.style.display === 'none' ? 'block' : 'none';
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.info('🚀 Инициализация Visual Builder...');
        visualBuilder = new VisualBuilder();
        
        // Делаем объект доступным глобально для отладки
        window.visualBuilder = visualBuilder;
        
        console.info('✅ Visual Builder успешно инициализирован');
    } catch (error) {
        console.error('❌ Критическая ошибка инициализации:', error);
        
        // Показываем пользователю сообщение об ошибке
        const errorMessage = document.createElement('div');
        errorMessage.innerHTML = `
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                        background: #fee; border: 1px solid #fcc; border-radius: 8px; 
                        padding: 20px; max-width: 400px; text-align: center; z-index: 10000;">
                <h3 style="color: #c33; margin-bottom: 10px;">⚠️ Ошибка загрузки</h3>
                <p style="margin-bottom: 15px;">Visual Builder не смог загрузиться. Проверьте консоль для деталей.</p>
                <button onclick="location.reload()" style="background: #c33; color: white; border: none; 
                                padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    Перезагрузить страницу
                </button>
            </div>
        `;
        document.body.appendChild(errorMessage);
    }
});