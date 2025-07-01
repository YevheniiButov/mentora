/**
 * Visual Builder Core - Dental Academy
 * Основной класс для управления Visual Builder
 */

class VisualBuilder {
    constructor(options = {}) {
        // Конфигурация
        this.config = {
            apiEndpoint: options.apiEndpoint || '/api/visual-builder',
            mediaEndpoint: options.mediaEndpoint || '/api/media',
            templatesEndpoint: options.templatesEndpoint || '/api/templates',
            currentPageId: options.currentPageId || null,
            currentUserId: options.currentUserId || null,
            csrfToken: options.csrfToken || '',
            autoSaveInterval: 30000, // 30 секунд
            debounceDelay: 1000,
            maxUndoSteps: 50,
            gridSize: 10,
            ...options
        };

        // Состояние приложения
        this.state = {
            theme: localStorage.getItem('vb-theme') || 'light',
            selectedElement: null,
            selectedElements: new Set(),
            draggedElement: null,
            resizeElement: null,
            zoom: 1,
            device: 'desktop',
            gridVisible: false,
            rulersVisible: false,
            snapToGrid: false,
            isLoading: false,
            isDragging: false,
            isResizing: false,
            showProperties: false,
            showLayers: true,
            lastSaved: null,
            hasChanges: false,
            currentPage: null
        };

        // История изменений
        this.history = {
            undoStack: [],
            redoStack: [],
            isUndoRedoAction: false
        };

        // Счетчики
        this.counters = {
            element: 0,
            save: 0
        };

        // DOM элементы
        this.dom = {};

        // Обработчики событий
        this.eventHandlers = new Map();

        // Менеджеры
        this.managers = {};

        // Инициализация
        this.init();
    }

    /**
     * Инициализация Visual Builder
     */
    async init() {
        try {
            console.info('🎨 Инициализация Visual Builder...');
            
            // Кэшируем DOM элементы
            this.cacheDOMElements();
            
            // Настраиваем тему
            this.setupTheme();
            
            // Настраиваем обработчики событий
            this.setupEventListeners();
            
            // Настраиваем drag & drop
            this.setupDragAndDrop();
            
            // Настраиваем горячие клавиши
            this.setupKeyboardShortcuts();
            
            // Инициализируем менеджеры
            await this.initializeManagers();
            
            // Настраиваем автосохранение
            this.setupAutoSave();
            
            // Загружаем сохраненный контент
            await this.loadSavedContent();
            
            // Обновляем UI
            this.updateUI();
            
            // Добавляем начальное состояние в историю
            this.addToHistory();
            
            this.showNotification('Visual Builder готов к работе!', 'success');
            console.info('✅ Visual Builder успешно инициализирован');
            
            this.initAdvancedFeatures();
            
        } catch (error) {
            console.error('❌ Ошибка инициализации Visual Builder:', error);
            this.showNotification('Ошибка инициализации приложения', 'error');
            throw error;
        }
    }

    /**
     * Кэширование DOM элементов
     */
    cacheDOMElements() {
        const selectors = {
            // Основные элементы
            builder: '.visual-builder',
            canvas: '#canvas',
            canvasContainer: '#canvasContainer',
            
            // Панели
            componentsSidebar: '#componentsSidebar',
            layersPanel: '#layersPanel',
            propertiesPanel: '#propertiesPanel',
            layersList: '#layersList',
            propertiesContent: '#propertiesContent',
            
            // Элементы управления
            themeIcon: '#theme-icon',
            undoBtn: '#undoBtn',
            redoBtn: '#redoBtn',
            zoomIndicator: '#zoomIndicator',
            pageInfo: '#pageInfo',
            lastSaved: '#lastSaved',
            
            // Поиск и фильтры
            componentSearch: '#componentSearch',
            componentsGrid: '#componentsGrid',
            
            // Overlays
            loadingOverlay: '#loadingOverlay',
            contextMenu: '#contextMenu',
            modalContainer: '#modalContainer',
            flashMessages: '#flashMessages'
        };

        this.dom = {};
        for (const [key, selector] of Object.entries(selectors)) {
            this.dom[key] = document.querySelector(selector);
            if (!this.dom[key] && ['builder', 'canvas'].includes(key)) {
                throw new Error(`Критически важный элемент не найден: ${selector}`);
            }
        }

        // Кэшируем коллекции элементов
        this.dom.componentItems = document.querySelectorAll('.component-item');
        this.dom.deviceButtons = document.querySelectorAll('[data-device]');
    }

    /**
     * Настройка темы
     */
    setupTheme() {
        this.applyTheme(this.state.theme);
    }

    /**
     * Применение темы
     */
    applyTheme(theme) {
        if (!['light', 'dark'].includes(theme)) {
            theme = 'light';
        }

        this.state.theme = theme;
        
        if (this.dom.builder) {
            this.dom.builder.setAttribute('data-theme', theme);
        }
        
        localStorage.setItem('vb-theme', theme);
        this.updateThemeIcon();
        
        // Уведомляем другие компоненты о смене темы
        this.emit('themeChanged', { theme });
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
            const iconClass = this.state.theme === 'light' ? 'bi-moon' : 'bi-sun';
            this.dom.themeIcon.className = `bi ${iconClass}`;
        }
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Глобальные обработчики
        document.addEventListener('click', this.handleGlobalClick.bind(this));
        document.addEventListener('keydown', this.handleGlobalKeydown.bind(this));
        document.addEventListener('contextmenu', this.handleContextMenu.bind(this));
        
        // Изменение размера окна
        window.addEventListener('resize', this.debounce(this.handleResize.bind(this), 250));
        
        // Предотвращение потери данных
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));

        // Обработчики для canvas
        if (this.dom.canvas) {
            this.dom.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
            this.dom.canvas.addEventListener('dragover', this.handleCanvasDragOver.bind(this));
            this.dom.canvas.addEventListener('drop', this.handleCanvasDrop.bind(this));
        }

        // Поиск компонентов
        if (this.dom.componentSearch) {
            this.dom.componentSearch.addEventListener('input', 
                this.debounce(this.handleComponentSearch.bind(this), 300));
        }

        // Переключение устройств
        this.dom.deviceButtons.forEach(btn => {
            btn.addEventListener('click', this.handleDeviceChange.bind(this));
        });

        // Обработчики для панелей
        this.setupPanelEventListeners();
    }

    /**
     * Настройка обработчиков для панелей
     */
    setupPanelEventListeners() {
        // Resizer для панелей
        this.setupPanelResizers();
        
        // Drag & Drop для слоев
        if (this.dom.layersList) {
            this.setupLayersDragAndDrop();
        }
    }

    /**
     * Настройка изменения размера панелей
     */
    setupPanelResizers() {
        const panels = [this.dom.componentsSidebar, this.dom.layersPanel, this.dom.propertiesPanel];
        
        panels.forEach(panel => {
            if (!panel) return;
            
            const resizer = document.createElement('div');
            resizer.className = 'panel-resizer';
            resizer.style.cssText = `
                position: absolute;
                top: 0;
                ${panel.classList.contains('sidebar') ? 'right' : 'left'}: 0;
                width: 4px;
                height: 100%;
                cursor: col-resize;
                background: transparent;
                z-index: 10;
            `;
            
            panel.style.position = 'relative';
            panel.appendChild(resizer);
            
            this.setupPanelResizer(panel, resizer);
        });
    }

    /**
     * Настройка конкретного resizer'а
     */
    setupPanelResizer(panel, resizer) {
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        const startResize = (e) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = panel.offsetWidth;
            
            document.addEventListener('mousemove', doResize);
            document.addEventListener('mouseup', stopResize);
            
            panel.style.userSelect = 'none';
            document.body.style.cursor = 'col-resize';
        };

        const doResize = (e) => {
            if (!isResizing) return;
            
            const deltaX = e.clientX - startX;
            const isLeftPanel = panel.classList.contains('sidebar');
            const newWidth = isLeftPanel ? startWidth + deltaX : startWidth - deltaX;
            
            const minWidth = parseInt(getComputedStyle(panel).getPropertyValue('--panel-min-width')) || 240;
            const maxWidth = window.innerWidth * 0.4;
            
            const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
            panel.style.width = `${clampedWidth}px`;
        };

        const stopResize = () => {
            isResizing = false;
            
            document.removeEventListener('mousemove', doResize);
            document.removeEventListener('mouseup', stopResize);
            
            panel.style.userSelect = '';
            document.body.style.cursor = '';
        };

        resizer.addEventListener('mousedown', startResize);
    }

    /**
     * Глобальный обработчик кликов
     */
    handleGlobalClick(event) {
        const target = event.target;

        // Скрываем контекстное меню
        this.hideContextMenu();

        // Снятие выделения при клике вне элементов
        if (!target.closest('.draggable-element') && 
            !target.closest('.element-controls') &&
            !target.closest('.properties-panel') &&
            !target.closest('.context-menu')) {
            this.deselectAllElements();
        }

        // Обработка кликов по кнопкам с data-action
        const actionButton = target.closest('[data-action]');
        if (actionButton) {
            const action = actionButton.dataset.action;
            this.handleAction(action, event);
        }
    }

    /**
     * Глобальный обработчик клавиатуры
     */
    handleGlobalKeydown(event) {
        // Игнорируем если фокус в input/textarea
        if (event.target.matches('input, textarea, [contenteditable="true"]')) {
            return;
        }

        // Горячие клавиши с Ctrl/Cmd
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
                case 'c':
                    if (this.state.selectedElement) {
                        event.preventDefault();
                        this.copyElement();
                    }
                    break;
                case 'v':
                    event.preventDefault();
                    this.pasteElement();
                    break;
            }
        }

        // Другие клавиши
        switch (event.key) {
            case 'Delete':
            case 'Backspace':
                if (this.state.selectedElement) {
                    event.preventDefault();
                    this.deleteElement(this.state.selectedElement);
                }
                break;
            case 'Escape':
                this.deselectAllElements();
                this.hideContextMenu();
                this.closeModals();
                break;
            case 'Tab':
                if (this.state.selectedElement) {
                    event.preventDefault();
                    this.selectNextElement(event.shiftKey);
                }
                break;
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                if (this.state.selectedElement) {
                    event.preventDefault();
                    this.moveElementWithKeys(event.key, event.shiftKey);
                }
                break;
        }
    }

    /**
     * Обработчик контекстного меню
     */
    handleContextMenu(event) {
        const element = event.target.closest('.draggable-element');
        if (element && this.dom.contextMenu) {
            event.preventDefault();
            this.showContextMenu(event.clientX, event.clientY, element);
        }
    }

    /**
     * Показ контекстного меню
     */
    showContextMenu(x, y, element) {
        if (!this.dom.contextMenu) return;

        this.selectElement(element);
        
        this.dom.contextMenu.style.display = 'block';
        this.dom.contextMenu.style.left = `${x}px`;
        this.dom.contextMenu.style.top = `${y}px`;

        // Обработчики для пунктов меню
        const menuItems = this.dom.contextMenu.querySelectorAll('.context-menu-item');
        menuItems.forEach(item => {
            item.onclick = (e) => {
                e.stopPropagation();
                const action = item.dataset.action;
                this.handleContextMenuAction(action, element);
                this.hideContextMenu();
            };
        });

        // Позиционирование в пределах экрана
        const rect = this.dom.contextMenu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            this.dom.contextMenu.style.left = `${x - rect.width}px`;
        }
        if (rect.bottom > window.innerHeight) {
            this.dom.contextMenu.style.top = `${y - rect.height}px`;
        }
    }

    /**
     * Скрытие контекстного меню
     */
    hideContextMenu() {
        if (this.dom.contextMenu) {
            this.dom.contextMenu.style.display = 'none';
        }
    }

    /**
     * Обработчик действий контекстного меню
     */
    handleContextMenuAction(action, element) {
        switch (action) {
            case 'copy':
                this.copyElement(element);
                break;
            case 'duplicate':
                this.duplicateElement(element);
                break;
            case 'edit':
                this.editElement(element);
                break;
            case 'move-up':
                this.moveElement(element, 'up');
                break;
            case 'move-down':
                this.moveElement(element, 'down');
                break;
            case 'delete':
                this.deleteElement(element);
                break;
        }
    }

    /**
     * Обработчик изменения размера окна
     */
    handleResize() {
        this.updateCanvasSize();
        this.updatePanelSizes();
    }

    /**
     * Обработчик перед закрытием страницы
     */
    handleBeforeUnload(event) {
        if (this.state.hasChanges) {
            const message = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
            event.returnValue = message;
            return message;
        }
    }

    /**
     * Обработчик клика по canvas
     */
    handleCanvasClick(event) {
        if (event.target === this.dom.canvas || event.target.closest('.canvas-empty')) {
            this.deselectAllElements();
        }
    }

    /**
     * Обработчик поиска компонентов
     */
    handleComponentSearch(event) {
        const query = event.target.value.toLowerCase();
        this.filterComponents(query);
    }

    /**
     * Фильтрация компонентов
     */
    filterComponents(query) {
        if (!this.dom.componentItems) return;

        this.dom.componentItems.forEach(item => {
            const name = item.querySelector('h4')?.textContent.toLowerCase() || '';
            const description = item.querySelector('p')?.textContent.toLowerCase() || '';
            const type = item.dataset.type || '';
            
            const matches = name.includes(query) || 
                          description.includes(query) || 
                          type.includes(query);
            
            item.style.display = matches ? 'flex' : 'none';
        });

        // Скрываем пустые категории
        const categories = this.dom.componentsGrid?.querySelectorAll('.component-category');
        categories?.forEach(category => {
            const visibleItems = category.querySelectorAll('.component-item[style*="flex"]').length;
            const hasVisibleItems = category.querySelectorAll('.component-item:not([style*="none"])').length > 0;
            category.style.display = hasVisibleItems ? 'block' : 'none';
        });
    }

    /**
     * Обработчик смены устройства
     */
    handleDeviceChange(event) {
        const device = event.target.dataset.device;
        if (device) {
            this.setDevice(device);
        }
    }

    /**
     * Установка устройства для предпросмотра
     */
    setDevice(device) {
        this.state.device = device;
        
        if (this.dom.canvas) {
            this.dom.canvas.setAttribute('data-device', device);
        }

        // Обновляем активную кнопку
        this.dom.deviceButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.device === device);
        });

        this.showNotification(`Переключено на ${this.getDeviceName(device)}`, 'info');
    }

    /**
     * Получение названия устройства
     */
    getDeviceName(device) {
        const names = {
            desktop: 'Десктоп',
            tablet: 'Планшет', 
            mobile: 'Мобильный'
        };
        return names[device] || device;
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
            this.state.isDragging = true;
            
            this.showNotification('Перетащите компонент на холст', 'info', 2000);
        });

        item.addEventListener('dragend', () => {
            item.style.opacity = '1';
            this.state.isDragging = false;
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
        if (!this.dom.canvas) return;

        this.dom.canvas.addEventListener('dragover', this.handleCanvasDragOver.bind(this));
        this.dom.canvas.addEventListener('dragleave', this.handleCanvasDragLeave.bind(this));
        this.dom.canvas.addEventListener('drop', this.handleCanvasDrop.bind(this));
    }

    /**
     * Обработчик dragover для canvas
     */
    handleCanvasDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
        
        if (!this.state.isDragging) return;
        
        this.dom.canvas.style.backgroundColor = 'rgba(62, 205, 193, 0.05)';
        this.dom.canvas.style.borderColor = 'var(--primary)';
    }

    /**
     * Обработчик dragleave для canvas
     */
    handleCanvasDragLeave(event) {
        if (!this.dom.canvas.contains(event.relatedTarget)) {
            this.clearCanvasHighlight();
        }
    }

    /**
     * Обработчик drop для canvas
     */
    handleCanvasDrop(event) {
        event.preventDefault();
        
        const componentType = event.dataTransfer.getData('text/plain');
        if (componentType) {
            const rect = this.dom.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            this.createElement(componentType, { x, y });
        }
        
        this.clearCanvasHighlight();
    }

    /**
     * Очистка подсветки canvas
     */
    clearCanvasHighlight() {
        if (this.dom.canvas) {
            this.dom.canvas.style.backgroundColor = '';
            this.dom.canvas.style.borderColor = '';
        }
    }

    /**
     * Настройка горячих клавиш
     */
    setupKeyboardShortcuts() {
        // Регистрируем горячие клавиши
        this.shortcuts = {
            'ctrl+s': () => this.savePage(),
            'ctrl+z': () => this.undo(),
            'ctrl+shift+z': () => this.redo(),
            'ctrl+y': () => this.redo(),
            'ctrl+d': () => this.duplicateElement(this.state.selectedElement),
            'ctrl+a': () => this.selectAllElements(),
            'ctrl+c': () => this.copyElement(),
            'ctrl+v': () => this.pasteElement(),
            'delete': () => this.deleteElement(this.state.selectedElement),
            'escape': () => this.deselectAllElements(),
        };

        console.info('⌨️ Горячие клавиши настроены');
    }

    /**
     * Инициализация менеджеров
     */
    async initializeManagers() {
        // Инициализируем менеджеры если они доступны
        if (window.MediaManager) {
            this.managers.media = new MediaManager(this);
        }
        
        if (window.ExportManager) {
            this.managers.export = new ExportManager(this);
        }
        
        if (window.TemplateManager) {
            this.managers.template = new TemplateManager(this);
        }

        // Инициализируем новые редакторы
        if (window.UniversalHTMLEditor) {
            this.managers.htmlEditor = new UniversalHTMLEditor(this);
        }
        
        if (window.AdvancedCSSEditor) {
            this.managers.cssEditor = new AdvancedCSSEditor(this);
        }
        
        if (window.GridEditor) {
            this.managers.gridEditor = new GridEditor(this);
        }
        
        if (window.FlexboxEditor) {
            this.managers.flexboxEditor = new FlexboxEditor(this);
        }

        console.info('📦 Менеджеры инициализированы');
    }

    /**
     * Настройка автосохранения
     */
    setupAutoSave() {
        setInterval(() => {
            if (this.state.hasChanges) {
                this.autoSave();
            }
        }, this.config.autoSaveInterval);

        console.info('💾 Автосохранение настроено');
    }

    /**
     * Автосохранение
     */
    async autoSave() {
        try {
            const content = this.getCanvasContent();
            const saveData = {
                content,
                timestamp: Date.now(),
                pageId: this.config.currentPageId,
                userId: this.config.currentUserId
            };
            
            localStorage.setItem('vb-autosave', JSON.stringify(saveData));
            
            if (this.dom.lastSaved) {
                this.dom.lastSaved.textContent = `Автосохранение: ${new Date().toLocaleTimeString()}`;
            }
            
            console.log('💾 Автосохранение выполнено');
        } catch (error) {
            console.warn('⚠️ Ошибка автосохранения:', error);
        }
    }

    /**
     * Загрузка сохраненного контента
     */
    async loadSavedContent() {
        try {
            // Сначала пытаемся загрузить конкретную страницу
            if (this.config.currentPageId) {
                await this.loadPage(this.config.currentPageId);
                return;
            }
            
            // Иначе загружаем автосохранение
            const saved = localStorage.getItem('vb-autosave');
            if (saved) {
                const data = JSON.parse(saved);
                if (data.content && data.content.trim()) {
                    this.setCanvasContent(data.content);
                    console.info('📄 Загружен автосохраненный контент');
                    this.showNotification('Загружен автосохраненный контент', 'info');
                }
            }
        } catch (error) {
            console.warn('⚠️ Ошибка загрузки сохраненного контента:', error);
        }
    }

    /**
     * Обновление UI
     */
    updateUI() {
        this.updateLayersPanel();
        this.updatePropertiesPanel();
        this.updateUndoRedoButtons();
        this.updatePageInfo();
    }

    /**
     * Обновление информации о странице
     */
    updatePageInfo() {
        if (this.dom.pageInfo) {
            const elementsCount = this.dom.canvas?.querySelectorAll('.draggable-element').length || 0;
            this.dom.pageInfo.textContent = `Элементов: ${elementsCount}`;
        }
    }

    /**
     * Создание элемента
     */
    async createElement(type, options = {}) {
        try {
            // Показываем загрузку для сложных элементов
            if (['dental-chart', 'case-study', 'xray-viewer'].includes(type)) {
                this.showLoading();
            }

            // Удаляем пустое состояние
            const emptyState = this.dom.canvas?.querySelector('.canvas-empty');
            if (emptyState) {
                emptyState.remove();
            }

            // Создаем элемент
            const element = document.createElement('div');
            element.className = `draggable-element element-${type} animate-fade-in`;
            element.dataset.type = type;
            element.dataset.id = `element_${++this.counters.element}`;

            // Позиционирование
            if (options.x !== undefined && options.y !== undefined) {
                element.style.position = 'relative';
                element.style.left = `${Math.max(0, options.x - 150)}px`;
                element.style.top = `${Math.max(0, options.y - 50)}px`;
            }

            // Получаем контент элемента
            const content = await this.getElementContent(type);
            element.innerHTML = content;

            // Добавляем на canvas
            this.dom.canvas?.appendChild(element);

            // Настраиваем обработчики
            this.setupElementEvents(element);
            this.addResizeHandles(element);

            // Выделяем новый элемент
            this.selectElement(element);

            // Обновляем состояние
            this.addToHistory();
            this.updateUI();
            this.markAsChanged();

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
            console.error('❌ Ошибка создания элемента:', error);
            this.showNotification('Ошибка создания элемента', 'error');
            return null;
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Получение контента элемента
     */
    async getElementContent(type) {
        // Импортируем шаблоны компонентов
        if (!this.componentTemplates) {
            await this.loadComponentTemplates();
        }

        const template = this.componentTemplates[type] || this.componentTemplates['text'];
        return template;
    }

    /**
     * Загрузка шаблонов компонентов
     */
    async loadComponentTemplates() {
        // Базовые шаблоны встроены, но можно загружать и с сервера
        this.componentTemplates = {
            'text': this.getTextTemplate(),
            'heading': this.getHeadingTemplate(),
            'image': this.getImageTemplate(),
            'button': this.getButtonTemplate(),
            'video': this.getVideoTemplate(),
            'audio': this.getAudioTemplate(),
            'gallery': this.getGalleryTemplate(),
            'quiz': this.getQuizTemplate(),
            'form': this.getFormTemplate(),
            'accordion': this.getAccordionTemplate(),
            'tabs': this.getTabsTemplate(),
            'flashcard': this.getFlashcardTemplate(),
            'container': this.getContainerTemplate(),
            'grid': this.getGridTemplate(),
            'columns': this.getColumnsTemplate(),
            'divider': this.getDividerTemplate(),
            'dental-chart': this.getDentalChartTemplate(),
            'case-study': this.getCaseStudyTemplate(),
            'xray-viewer': this.getXrayViewerTemplate(),
            'hero': this.getHeroTemplate(),
            'feature': this.getFeatureTemplate(),
            'testimonial': this.getTestimonialTemplate(),
            'cta': this.getCtaTemplate()
        };
    }

    /**
     * Базовые шаблоны элементов
     */
    getTextTemplate() {
        return `
            <div class="element-content">
                <div contenteditable="true" data-placeholder="Введите текст...">
                    <p>Введите ваш текст здесь. Этот блок можно редактировать, просто кликните и начните печатать.</p>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getHeadingTemplate() {
        return `
            <div class="element-content">
                <h2 contenteditable="true" data-placeholder="Заголовок...">Заголовок</h2>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getImageTemplate() {
        return `
            <div class="element-content">
                <div class="image-placeholder" onclick="visualBuilder.selectImage(this)">
                    <div class="placeholder-content">
                        <i class="bi bi-image"></i>
                        <h4>Добавить изображение</h4>
                        <p>Нажмите для выбора файла</p>
                        <small>JPG, PNG, GIF, WebP до 10MB</small>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getButtonTemplate() {
        return `
            <div class="element-content">
                <div class="button-wrapper">
                    <button class="custom-button" contenteditable="true" data-placeholder="Текст кнопки...">
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
                    <div class="placeholder-content">
                        <i class="bi bi-play-circle"></i>
                        <h4>Добавить видео</h4>
                        <p>YouTube, Vimeo или загрузить файл</p>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getHeroTemplate() {
        return `
            <div class="element-content">
                <div class="hero-section">
                    <div class="hero-content">
                        <h1 contenteditable="true" data-placeholder="Главный заголовок...">
                            Добро пожаловать в Dental Academy
                        </h1>
                        <p contenteditable="true" data-placeholder="Описание...">
                            Изучайте стоматологию с лучшими специалистами и современными методиками
                        </p>
                        <div class="hero-actions">
                            <button class="btn btn-primary btn-lg">Начать обучение</button>
                            <button class="btn btn-secondary btn-lg">Узнать больше</button>
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getDentalChartTemplate() {
        return `
            <div class="element-content">
                <div class="dental-chart-container">
                    <h3 contenteditable="true">Зубная формула</h3>
                    <div class="dental-chart">
                        <div class="teeth-row upper">
                            ${Array.from({length: 16}, (_, i) => `
                                <div class="tooth" data-number="${i + 1}" onclick="visualBuilder.toggleTooth(this)">
                                    <span class="tooth-number">${i + 1}</span>
                                </div>
                            `).join('')}
                        </div>
                        <div class="teeth-row lower">
                            ${Array.from({length: 16}, (_, i) => `
                                <div class="tooth" data-number="${i + 17}" onclick="visualBuilder.toggleTooth(this)">
                                    <span class="tooth-number">${i + 17}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item">
                            <div class="legend-color healthy"></div>
                            <span>Здоровый</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color caries"></div>
                            <span>Кариес</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color filled"></div>
                            <span>Пломба</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color missing"></div>
                            <span>Отсутствует</span>
                        </div>
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
                <button class="control-btn" onclick="visualBuilder.moveElement(this, 'up')" title="Переместить вверх">
                    <i class="bi bi-arrow-up"></i>
                </button>
                <button class="control-btn secondary" onclick="visualBuilder.duplicateElement(this)" title="Дублировать">
                    <i class="bi bi-files"></i>
                </button>
                <button class="control-btn warning" onclick="visualBuilder.editElement(this)" title="Редактировать">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="control-btn danger" onclick="visualBuilder.deleteElement(this)" title="Удалить">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
    }

    /**
     * Получение имени элемента
     */
    getElementName(type) {
        const names = {
            'text': 'Текстовый блок',
            'heading': 'Заголовок',
            'image': 'Изображение',
            'button': 'Кнопка',
            'video': 'Видео',
            'audio': 'Аудио',
            'gallery': 'Галерея',
            'quiz': 'Тест',
            'form': 'Форма',
            'accordion': 'Аккордеон',
            'tabs': 'Вкладки',
            'flashcard': 'Флэшкарта',
            'container': 'Контейнер',
            'grid': 'Сетка',
            'columns': 'Колонки',
            'divider': 'Разделитель',
            'dental-chart': 'Зубная формула',
            'case-study': 'Клинический случай',
            'xray-viewer': 'Рентген просмотр',
            'hero': 'Hero секция',
            'feature': 'Преимущества',
            'testimonial': 'Отзывы',
            'cta': 'Призыв к действию'
        };
        return names[type] || 'Элемент';
    }

    /**
     * Настройка событий элемента
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
                this.markAsChanged();
            }, this.config.debounceDelay));

            editable.addEventListener('blur', () => {
                this.addToHistory();
                this.markAsChanged();
            });

            // Placeholder functionality
            this.setupPlaceholder(editable);
        });

        // Drag functionality
        this.setupElementDrag(element);
    }

    /**
     * Настройка placeholder для contenteditable
     */
    setupPlaceholder(element) {
        const placeholder = element.dataset.placeholder;
        if (!placeholder) return;

        const updatePlaceholder = () => {
            if (element.textContent.trim() === '') {
                element.classList.add('empty');
                if (!element.dataset.originalContent) {
                    element.dataset.originalContent = element.innerHTML;
                }
                element.innerHTML = `<span class="placeholder">${placeholder}</span>`;
            } else {
                element.classList.remove('empty');
            }
        };

        element.addEventListener('focus', () => {
            if (element.classList.contains('empty')) {
                element.innerHTML = element.dataset.originalContent || '';
                element.classList.remove('empty');
            }
        });

        element.addEventListener('blur', updatePlaceholder);
        updatePlaceholder();
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

        const dragHandle = element.querySelector('.element-controls');
        if (!dragHandle) return;

        dragHandle.addEventListener('mousedown', (e) => {
            if (e.target.closest('button')) return;
            
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
            if (this.state.snapToGrid) {
                newLeft = Math.round(newLeft / this.config.gridSize) * this.config.gridSize;
                newTop = Math.round(newTop / this.config.gridSize) * this.config.gridSize;
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
            this.markAsChanged();
        };
    }

    /**
     * Добавление handles для изменения размера
     */
    addResizeHandles(element) {
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

            this.state.isResizing = true;
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

            // Snap to grid if enabled
            if (this.state.snapToGrid) {
                newWidth = Math.round(newWidth / this.config.gridSize) * this.config.gridSize;
                newHeight = Math.round(newHeight / this.config.gridSize) * this.config.gridSize;
                newLeft = Math.round(newLeft / this.config.gridSize) * this.config.gridSize;
                newTop = Math.round(newTop / this.config.gridSize) * this.config.gridSize;
            }

            // Применяем новые размеры
            element.style.width = `${newWidth}px`;
            element.style.height = `${newHeight}px`;
            element.style.left = `${newLeft}px`;
            element.style.top = `${newTop}px`;
        };

        const stopResize = () => {
            if (!isResizing) return;
            
            isResizing = false;
            this.state.isResizing = false;
            element.classList.remove('resizing');
            
            document.removeEventListener('mousemove', handleResize);
            document.removeEventListener('mouseup', stopResize);
            
            this.addToHistory();
            this.markAsChanged();
            this.updatePropertiesPanel();
        };

        handles.addEventListener('mousedown', startResize);
    }

    // Продолжение следует в следующем сообщении...
    
    /**
     * Системы управления - будут дополнены
     */
    
    // Управление выделением
    selectElement(element) {
        this.deselectAllElements();
        element.classList.add('selected');
        this.state.selectedElement = element;
        this.updateUI();
        
        // Скроллим к элементу если нужно
        element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    deselectAllElements() {
        this.dom.canvas?.querySelectorAll('.draggable-element').forEach(el => {
            el.classList.remove('selected');
        });
        this.state.selectedElement = null;
        this.state.selectedElements.clear();
        this.updateUI();
    }

    // Утилиты
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

    emit(eventName, data) {
        const event = new CustomEvent(`vb:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    showLoading() {
        if (this.dom.loadingOverlay) {
            this.dom.loadingOverlay.style.display = 'flex';
        }
        this.state.isLoading = true;
    }

    hideLoading() {
        if (this.dom.loadingOverlay) {
            this.dom.loadingOverlay.style.display = 'none';
        }
        this.state.isLoading = false;
    }

    markAsChanged() {
        this.state.hasChanges = true;
    }

    // Заглушки для методов, которые будут реализованы полностью
    addToHistory() { /* TODO: Implement history management */ }
    updateLayersPanel() { /* TODO: Implement layers panel */ }
    updatePropertiesPanel() { /* TODO: Implement properties panel */ }
    updateUndoRedoButtons() { /* TODO: Implement undo/redo */ }
    getCanvasContent() { return this.dom.canvas?.innerHTML || ''; }
    setCanvasContent(content) { if (this.dom.canvas) this.dom.canvas.innerHTML = content; }
    showNotification(message, type = 'info', duration = 3000) { 
        console.info(`[${type.toUpperCase()}] ${message}`); 
    }
    
    // API методы (заглушки)
    async savePage() { console.info('💾 Saving page...'); }
    async loadPage(pageId) { console.info(`📄 Loading page ${pageId}...`); }
    async exportPage() { console.info('📤 Exporting page...'); }
    
    // Плагины и расширения
    undo() { console.info('↩️ Undo'); }
    redo() { console.info('↪️ Redo'); }
    duplicateElement(element) { console.info('📋 Duplicate element'); }
    deleteElement(element) { console.info('🗑️ Delete element'); }
    editElement(element) { console.info('✏️ Edit element'); }
    moveElement(element, direction) { console.info(`⬆️ Move element ${direction}`); }

    // ===== API МЕТОДЫ =====
    
    /**
     * Сохранение страницы на сервер
     */
    async savePage() {
        try {
            this.showLoading();
            
            const contentData = this.getCanvasContent();
            const pageData = {
                title: this.state.currentPage?.title || 'Новая страница',
                content_data: {
                    elements: this.extractElementsFromCanvas(),
                    settings: this.getPageSettings()
                },
                page_settings: this.getPageSettings(),
                language: 'ru',
                template_id: this.state.currentPage?.template_id || null
            };
            
            // Если у нас есть ID страницы, добавляем его
            if (this.state.currentPage?.id) {
                pageData.page_id = this.state.currentPage.id;
            }
            
            const response = await fetch(this.config.apiEndpoint + '/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: JSON.stringify(pageData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.currentPage = {
                    id: result.page_id,
                    title: pageData.title,
                    slug: result.page_slug,
                    template_id: pageData.template_id
                };
                this.state.hasChanges = false;
                this.state.lastSaved = new Date();
                this.updatePageInfo();
                this.showNotification('Страница сохранена успешно', 'success');
                this.emit('pageSaved', result);
            } else {
                throw new Error(result.error || 'Ошибка сохранения');
            }
            
        } catch (error) {
            console.error('Ошибка сохранения страницы:', error);
            this.showNotification(`Ошибка сохранения: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Загрузка страницы с сервера
     */
    async loadPage(pageId = null) {
        try {
            this.showLoading();
            
            const targetPageId = pageId || this.config.currentPageId;
            if (!targetPageId) {
                throw new Error('ID страницы не указан');
            }
            
            const response = await fetch(`${this.config.apiEndpoint}/load/${targetPageId}`, {
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.state.currentPage = result.page;
                this.loadPageContent(result.page.content_data);
                this.updatePageInfo();
                this.showNotification('Страница загружена успешно', 'success');
                this.emit('pageLoaded', result.page);
            } else {
                throw new Error(result.error || 'Ошибка загрузки');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки страницы:', error);
            this.showNotification(`Ошибка загрузки: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Загрузка списка страниц
     */
    async loadPagesList() {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/pages`, {
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                return result.pages;
            } else {
                throw new Error(result.error || 'Ошибка загрузки списка страниц');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки списка страниц:', error);
            this.showNotification(`Ошибка загрузки списка: ${error.message}`, 'error');
            return [];
        }
    }
    
    /**
     * Удаление страницы
     */
    async deletePage(pageId) {
        try {
            if (!confirm('Вы уверены, что хотите удалить эту страницу?')) {
                return false;
            }
            
            this.showLoading();
            
            const response = await fetch(`${this.config.apiEndpoint}/pages/${pageId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Страница удалена успешно', 'success');
                this.emit('pageDeleted', pageId);
                return true;
            } else {
                throw new Error(result.error || 'Ошибка удаления');
            }
            
        } catch (error) {
            console.error('Ошибка удаления страницы:', error);
            this.showNotification(`Ошибка удаления: ${error.message}`, 'error');
            return false;
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Публикация страницы
     */
    async publishPage(pageId) {
        try {
            this.showLoading();
            
            const response = await fetch(`${this.config.apiEndpoint}/pages/${pageId}/publish`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Страница опубликована успешно', 'success');
                this.emit('pagePublished', pageId);
                return true;
            } else {
                throw new Error(result.error || 'Ошибка публикации');
            }
            
        } catch (error) {
            console.error('Ошибка публикации страницы:', error);
            this.showNotification(`Ошибка публикации: ${error.message}`, 'error');
            return false;
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Экспорт страницы
     */
    async exportPage(format = 'html') {
        try {
            if (!this.state.currentPage?.id) {
                throw new Error('Нет активной страницы для экспорта');
            }
            
            this.showLoading();
            
            const response = await fetch(`${this.config.apiEndpoint}/export/${this.state.currentPage.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.config.csrfToken
                },
                body: JSON.stringify({ format })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Скачиваем файл
                this.downloadFile(result.content, result.filename, format);
                this.showNotification('Страница экспортирована успешно', 'success');
                this.emit('pageExported', { format, filename: result.filename });
            } else {
                throw new Error(result.error || 'Ошибка экспорта');
            }
            
        } catch (error) {
            console.error('Ошибка экспорта страницы:', error);
            this.showNotification(`Ошибка экспорта: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    /**
     * Загрузка медиа файла
     */
    async uploadMedia(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.config.apiEndpoint}/media/upload`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                },
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('Файл загружен успешно', 'success');
                this.emit('mediaUploaded', result.media);
                return result.media;
            } else {
                throw new Error(result.error || 'Ошибка загрузки файла');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки медиа:', error);
            this.showNotification(`Ошибка загрузки: ${error.message}`, 'error');
            return null;
        }
    }
    
    /**
     * Загрузка медиа библиотеки
     */
    async loadMediaLibrary() {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/media`, {
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                return result.media;
            } else {
                throw new Error(result.error || 'Ошибка загрузки медиа библиотеки');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки медиа библиотеки:', error);
            this.showNotification(`Ошибка загрузки медиа: ${error.message}`, 'error');
            return [];
        }
    }
    
    /**
     * Загрузка шаблонов
     */
    async loadTemplates() {
        try {
            const response = await fetch(`${this.config.apiEndpoint}/templates`, {
                headers: {
                    'X-CSRFToken': this.config.csrfToken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                return result.templates;
            } else {
                throw new Error(result.error || 'Ошибка загрузки шаблонов');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки шаблонов:', error);
            this.showNotification(`Ошибка загрузки шаблонов: ${error.message}`, 'error');
            return [];
        }
    }
    
    // ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    
    /**
     * Извлечение элементов из canvas
     */
    extractElementsFromCanvas() {
        const elements = [];
        const canvasElements = this.dom.canvas?.querySelectorAll('.draggable-element') || [];
        
        canvasElements.forEach((element, index) => {
            const elementData = {
                id: element.dataset.id || `element_${index}`,
                type: element.dataset.type || 'text',
                content: this.extractElementContent(element),
                position: this.extractElementPosition(element),
                styles: this.extractElementStyles(element)
            };
            elements.push(elementData);
        });
        
        return elements;
    }
    
    /**
     * Извлечение контента элемента
     */
    extractElementContent(element) {
        const contentElement = element.querySelector('.element-content');
        if (!contentElement) return {};
        
        const type = element.dataset.type;
        
        switch (type) {
            case 'text':
            case 'heading':
                return {
                    text: contentElement.textContent || contentElement.innerHTML
                };
            case 'image':
                const img = contentElement.querySelector('img');
                return {
                    src: img?.src || '',
                    alt: img?.alt || ''
                };
            case 'video':
                const iframe = contentElement.querySelector('iframe');
                return {
                    src: iframe?.src || ''
                };
            case 'hero':
                return {
                    title: contentElement.querySelector('h1')?.textContent || '',
                    subtitle: contentElement.querySelector('p')?.textContent || '',
                    button_text: contentElement.querySelector('button')?.textContent || ''
                };
            case 'feature':
                return {
                    title1: contentElement.querySelector('.feature-item:nth-child(1) h3')?.textContent || '',
                    description1: contentElement.querySelector('.feature-item:nth-child(1) p')?.textContent || '',
                    title2: contentElement.querySelector('.feature-item:nth-child(2) h3')?.textContent || '',
                    description2: contentElement.querySelector('.feature-item:nth-child(2) p')?.textContent || '',
                    title3: contentElement.querySelector('.feature-item:nth-child(3) h3')?.textContent || '',
                    description3: contentElement.querySelector('.feature-item:nth-child(3) p')?.textContent || ''
                };
            default:
                return {
                    text: contentElement.textContent || contentElement.innerHTML
                };
        }
    }
    
    /**
     * Извлечение позиции элемента
     */
    extractElementPosition(element) {
        const rect = element.getBoundingClientRect();
        const canvasRect = this.dom.canvas?.getBoundingClientRect();
        
        if (!canvasRect) return { x: 0, y: 0 };
        
        return {
            x: rect.left - canvasRect.left,
            y: rect.top - canvasRect.top
        };
    }
    
    /**
     * Извлечение стилей элемента
     */
    extractElementStyles(element) {
        const computedStyle = window.getComputedStyle(element);
        return {
            width: computedStyle.width,
            height: computedStyle.height,
            backgroundColor: computedStyle.backgroundColor,
            color: computedStyle.color,
            fontSize: computedStyle.fontSize,
            fontWeight: computedStyle.fontWeight,
            textAlign: computedStyle.textAlign,
            padding: computedStyle.padding,
            margin: computedStyle.margin,
            border: computedStyle.border,
            borderRadius: computedStyle.borderRadius
        };
    }
    
    /**
     * Загрузка контента страницы в canvas
     */
    loadPageContent(contentData) {
        if (!contentData || !contentData.elements) return;
        
        // Очищаем canvas
        this.dom.canvas.innerHTML = '';
        
        // Загружаем элементы
        contentData.elements.forEach(elementData => {
            this.createElementFromData(elementData);
        });
        
        // Применяем настройки страницы
        if (contentData.settings) {
            this.applyPageSettings(contentData.settings);
        }
    }
    
    /**
     * Создание элемента из данных
     */
    async createElementFromData(elementData) {
        const element = await this.createElement(elementData.type, {
            x: elementData.position?.x || 0,
            y: elementData.position?.y || 0
        });
        
        if (element && elementData.content) {
            this.applyElementContent(element, elementData.content);
        }
        
        if (element && elementData.styles) {
            this.applyElementStyles(element, elementData.styles);
        }
    }
    
    /**
     * Применение контента к элементу
     */
    applyElementContent(element, content) {
        const contentElement = element.querySelector('.element-content');
        if (!contentElement) return;
        
        const type = element.dataset.type;
        
        switch (type) {
            case 'text':
            case 'heading':
                contentElement.innerHTML = content.text || '';
                break;
            case 'image':
                if (content.src) {
                    contentElement.innerHTML = `<img src="${content.src}" alt="${content.alt || ''}">`;
                }
                break;
            case 'video':
                if (content.src) {
                    contentElement.innerHTML = `<iframe src="${content.src}" frameborder="0" allowfullscreen></iframe>`;
                }
                break;
            // Добавьте другие типы по необходимости
        }
    }
    
    /**
     * Применение стилей к элементу
     */
    applyElementStyles(element, styles) {
        Object.entries(styles).forEach(([property, value]) => {
            if (value && value !== 'auto' && value !== 'normal') {
                element.style[property] = value;
            }
        });
    }
    
    /**
     * Получение настроек страницы
     */
    getPageSettings() {
        return {
            theme: this.state.theme,
            device: this.state.device,
            gridVisible: this.state.gridVisible,
            rulersVisible: this.state.rulersVisible,
            snapToGrid: this.state.snapToGrid,
            zoom: this.state.zoom
        };
    }
    
    /**
     * Применение настроек страницы
     */
    applyPageSettings(settings) {
        if (settings.theme) {
            this.applyTheme(settings.theme);
        }
        if (settings.device) {
            this.setDevice(settings.device);
        }
        if (settings.gridVisible !== undefined) {
            this.state.gridVisible = settings.gridVisible;
        }
        if (settings.rulersVisible !== undefined) {
            this.state.rulersVisible = settings.rulersVisible;
        }
        if (settings.snapToGrid !== undefined) {
            this.state.snapToGrid = settings.snapToGrid;
        }
        if (settings.zoom) {
            this.state.zoom = settings.zoom;
        }
        
        this.updateUI();
    }
    
    /**
     * Скачивание файла
     */
    downloadFile(content, filename, format) {
        let mimeType = 'text/html';
        if (format === 'json') {
            mimeType = 'application/json';
            content = JSON.stringify(content, null, 2);
        }
        
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
     * Обновление информации о странице
     */
    updatePageInfo() {
        const pageInfo = this.dom.pageInfo;
        if (!pageInfo) return;
        
        if (this.state.currentPage) {
            pageInfo.textContent = `${this.state.currentPage.title} (${this.state.currentPage.slug})`;
        } else {
            pageInfo.textContent = 'Новая страница';
        }
        
        const lastSaved = this.dom.lastSaved;
        if (lastSaved) {
            if (this.state.lastSaved) {
                lastSaved.textContent = `Автосохранение: ${this.state.lastSaved.toLocaleTimeString()}`;
            } else {
                lastSaved.textContent = 'Автосохранение: выключено';
            }
        }
    }

    initAdvancedFeatures() {
        // Инициализируем продвинутые редакторы
        if (window.AdvancedStyleEditor) {
            this.advancedStyleEditor = new window.AdvancedStyleEditor(this);
        }
        
        if (window.ResponsiveDesign) {
            this.responsiveDesign = new window.ResponsiveDesign(this);
        }
        
        // Добавляем методы для работы с новыми редакторами
        this.setupAdvancedEditorMethods();
        
        console.info('🚀 Продвинутые возможности инициализированы');
    }
    
    /**
     * Настройка методов для работы с продвинутыми редакторами
     */
    setupAdvancedEditorMethods() {
        // Методы для работы с HTML редактором
        this.openHTMLEditor = (element = null) => {
            if (this.managers.htmlEditor) {
                this.managers.htmlEditor.open(element);
            } else {
                this.showNotification('HTML редактор не доступен', 'warning');
            }
        };
        
        // Методы для работы с CSS редактором
        this.openCSSEditor = (element = null) => {
            if (this.managers.cssEditor) {
                this.managers.cssEditor.open(element);
            } else {
                this.showNotification('CSS редактор не доступен', 'warning');
            }
        };
        
        // Методы для работы с Grid редактором
        this.openGridEditor = (element = null) => {
            if (this.managers.gridEditor) {
                this.managers.gridEditor.open(element);
            } else {
                this.showNotification('Grid редактор не доступен', 'warning');
            }
        };
        
        // Методы для работы с Flexbox редактором
        this.openFlexboxEditor = (element = null) => {
            if (this.managers.flexboxEditor) {
                this.managers.flexboxEditor.open(element);
            } else {
                this.showNotification('Flexbox редактор не доступен', 'warning');
            }
        };
        
        // Метод для импорта HTML
        this.importHTML = (htmlContent) => {
            if (this.managers.htmlEditor) {
                return this.managers.htmlEditor.importHTML(htmlContent);
            }
            return false;
        };
        
        // Метод для экспорта HTML
        this.exportHTML = () => {
            if (this.managers.htmlEditor) {
                return this.managers.htmlEditor.exportHTML();
            }
            return this.getCanvasContent();
        };
    }
}

// Экспорт для использования
window.VisualBuilder = VisualBuilder;

// Автоинициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    console.info('🚀 DOM загружен, готов к инициализации Visual Builder');
});