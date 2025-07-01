/**
 * Drag & Drop Editor для Visual Builder
 * Продвинутая система перетаскивания с визуальными подсказками
 */

class DragDropEditor {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.isDragging = false;
        this.dragElement = null;
        this.dropZones = [];
        this.selectedElements = [];
        this.dragOffset = { x: 0, y: 0 };
        this.snapToGrid = true;
        this.gridSize = 20;
        this.multiSelectMode = false;
        
        // Состояние drag & drop
        this.state = {
            isDragging: false,
            dragType: null, // 'component', 'element', 'multi'
            dragData: null,
            dropTarget: null,
            dragPreview: null,
            snapLines: { horizontal: [], vertical: [] }
        };
        
        // Настройки
        this.config = {
            snapThreshold: 10,
            dropZoneHighlight: true,
            dragPreview: true,
            snapToGrid: true,
            snapToElements: true,
            multiSelect: true,
            dragDelay: 200,
            dropAnimation: true
        };
        
        // Инициализация
        this.init();
    }

    /**
     * Инициализация Drag & Drop Editor
     */
    init() {
        this.setupEventListeners();
        this.createDropZones();
        this.setupKeyboardShortcuts();
        
        console.info('🎯 Drag & Drop Editor инициализирован');
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Глобальные обработчики
        document.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        // Drag & Drop события
        document.addEventListener('dragstart', this.handleDragStart.bind(this));
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('dragleave', this.handleDragLeave.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));
        document.addEventListener('dragend', this.handleDragEnd.bind(this));
        
        // Клавиатурные события
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
        
        // События canvas
        const canvas = document.getElementById('canvas');
        if (canvas) {
            canvas.addEventListener('click', this.handleCanvasClick.bind(this));
            canvas.addEventListener('dblclick', this.handleCanvasDoubleClick.bind(this));
        }
    }

    /**
     * Создание зон drop
     */
    createDropZones() {
        const canvas = document.getElementById('canvas');
        if (!canvas) return;

        // Основная зона drop на canvas
        this.addDropZone(canvas, {
            type: 'canvas',
            accept: ['component', 'element'],
            highlight: true,
            snapToGrid: true
        });

        // Зоны drop для контейнеров
        this.createContainerDropZones();
    }

    /**
     * Создание зон drop для контейнеров
     */
    createContainerDropZones() {
        const containers = document.querySelectorAll('.editable-container, .editable-section, .editable-grid');
        
        containers.forEach(container => {
            this.addDropZone(container, {
                type: 'container',
                accept: ['component', 'element'],
                highlight: true,
                snapToGrid: false,
                insertMode: 'append'
            });
        });
    }

    /**
     * Добавление зоны drop
     */
    addDropZone(element, options = {}) {
        const dropZone = {
            element,
            type: options.type || 'general',
            accept: options.accept || ['component', 'element'],
            highlight: options.highlight !== false,
            snapToGrid: options.snapToGrid !== false,
            insertMode: options.insertMode || 'replace',
            active: false
        };

        this.dropZones.push(dropZone);
        
        // Добавляем CSS классы
        element.classList.add('drop-zone');
        element.setAttribute('data-drop-type', dropZone.type);
        
        return dropZone;
    }

    /**
     * Обработчик начала перетаскивания
     */
    handleDragStart(event) {
        const target = event.target;
        
        // Определяем тип перетаскивания
        if (target.closest('.component-item')) {
            this.startComponentDrag(event, target);
        } else if (target.closest('.draggable-element')) {
            this.startElementDrag(event, target);
        } else if (target.closest('.selected-element')) {
            this.startMultiDrag(event);
        }
    }

    /**
     * Начало перетаскивания компонента
     */
    startComponentDrag(event, element) {
        const componentKey = element.dataset.componentKey;
        if (!componentKey) return;

        this.state.dragType = 'component';
        this.state.dragData = { componentKey };
        this.state.isDragging = true;
        
        // Создаем превью для перетаскивания
        this.createDragPreview(event, element);
        
        // Устанавливаем данные для transfer
        event.dataTransfer.setData('text/plain', JSON.stringify({
            type: 'component',
            componentKey: componentKey
        }));
        event.dataTransfer.effectAllowed = 'copy';
        
        // Добавляем классы
        element.classList.add('dragging');
        
        console.info(`🎯 Начато перетаскивание компонента: ${componentKey}`);
    }

    /**
     * Начало перетаскивания элемента
     */
    startElementDrag(event, element) {
        // Проверяем, не является ли элемент частью выделения
        if (this.selectedElements.length > 1 && this.selectedElements.includes(element)) {
            this.startMultiDrag(event);
            return;
        }

        this.state.dragType = 'element';
        this.state.dragData = { element };
        this.state.isDragging = true;
        
        // Вычисляем смещение курсора относительно элемента
        const rect = element.getBoundingClientRect();
        this.dragOffset = {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
        
        // Создаем превью
        this.createDragPreview(event, element);
        
        // Добавляем классы
        element.classList.add('dragging');
        
        console.info('🎯 Начато перетаскивание элемента');
    }

    /**
     * Начало множественного перетаскивания
     */
    startMultiDrag(event) {
        if (this.selectedElements.length <= 1) return;

        this.state.dragType = 'multi';
        this.state.dragData = { elements: [...this.selectedElements] };
        this.state.isDragging = true;
        
        // Создаем превью для всех выбранных элементов
        this.createMultiDragPreview(event);
        
        console.info(`🎯 Начато множественное перетаскивание ${this.selectedElements.length} элементов`);
    }

    /**
     * Создание превью для перетаскивания
     */
    createDragPreview(event, element) {
        if (!this.config.dragPreview) return;

        const preview = element.cloneNode(true);
        preview.classList.add('drag-preview');
        preview.style.position = 'fixed';
        preview.style.pointerEvents = 'none';
        preview.style.zIndex = '10000';
        preview.style.opacity = '0.8';
        preview.style.transform = 'rotate(5deg) scale(0.9)';
        
        document.body.appendChild(preview);
        this.state.dragPreview = preview;
        
        // Позиционируем превью
        this.updateDragPreviewPosition(event);
    }

    /**
     * Создание превью для множественного перетаскивания
     */
    createMultiDragPreview(event) {
        if (!this.config.dragPreview) return;

        const preview = document.createElement('div');
        preview.className = 'multi-drag-preview';
        preview.innerHTML = `
            <div class="multi-drag-count">${this.selectedElements.length}</div>
            <div class="multi-drag-label">элементов</div>
        `;
        preview.style.position = 'fixed';
        preview.style.pointerEvents = 'none';
        preview.style.zIndex = '10000';
        
        document.body.appendChild(preview);
        this.state.dragPreview = preview;
        
        this.updateDragPreviewPosition(event);
    }

    /**
     * Обновление позиции превью
     */
    updateDragPreviewPosition(event) {
        if (!this.state.dragPreview) return;

        const preview = this.state.dragPreview;
        const offset = this.state.dragType === 'element' ? this.dragOffset : { x: 0, y: 0 };
        
        preview.style.left = `${event.clientX - offset.x}px`;
        preview.style.top = `${event.clientY - offset.y}px`;
    }

    /**
     * Обработчик перетаскивания
     */
    handleDragOver(event) {
        event.preventDefault();
        
        if (!this.state.isDragging) return;

        // Обновляем позицию превью
        this.updateDragPreviewPosition(event);
        
        // Находим зону drop
        const dropZone = this.findDropZone(event.target);
        if (dropZone) {
            this.highlightDropZone(dropZone, true);
            this.state.dropTarget = dropZone;
        } else {
            this.clearDropZoneHighlights();
            this.state.dropTarget = null;
        }
        
        // Показываем snap lines
        if (this.config.snapToElements) {
            this.showSnapLines(event);
        }
    }

    /**
     * Обработчик выхода из зоны drop
     */
    handleDragLeave(event) {
        if (!this.state.isDragging) return;

        const dropZone = this.findDropZone(event.target);
        if (dropZone && !dropZone.element.contains(event.relatedTarget)) {
            this.highlightDropZone(dropZone, false);
        }
    }

    /**
     * Обработчик drop
     */
    handleDrop(event) {
        event.preventDefault();
        
        if (!this.state.isDragging) return;

        const dropZone = this.findDropZone(event.target);
        if (!dropZone) return;

        try {
            // Выполняем drop в зависимости от типа
            switch (this.state.dragType) {
                case 'component':
                    this.handleComponentDrop(event, dropZone);
                    break;
                case 'element':
                    this.handleElementDrop(event, dropZone);
                    break;
                case 'multi':
                    this.handleMultiDrop(event, dropZone);
                    break;
            }
            
            console.info('✅ Drop выполнен успешно');
        } catch (error) {
            console.error('❌ Ошибка при drop:', error);
            this.visualBuilder?.showNotification('Ошибка при добавлении элемента', 'error');
        }
        
        // Очищаем состояние
        this.clearDragState();
    }

    /**
     * Обработка drop компонента
     */
    handleComponentDrop(event, dropZone) {
        const componentKey = this.state.dragData.componentKey;
        if (!componentKey) return;

        // Получаем компонент из библиотеки
        const component = this.visualBuilder?.componentLibrary?.getComponent(componentKey);
        if (!component) return;

        // Создаем элемент компонента
        const element = this.createComponentElement(component);
        
        // Позиционируем элемент
        this.positionElementInDropZone(element, event, dropZone);
        
        // Добавляем в drop zone
        this.insertElementInDropZone(element, dropZone);
        
        // Уведомляем Visual Builder
        if (this.visualBuilder) {
            this.visualBuilder.addToHistory();
            this.visualBuilder.updateLayersPanel();
        }
    }

    /**
     * Обработка drop элемента
     */
    handleElementDrop(event, dropZone) {
        const element = this.state.dragData.element;
        if (!element) return;

        // Позиционируем элемент
        this.positionElementInDropZone(element, event, dropZone);
        
        // Перемещаем элемент в новую зону
        this.moveElementToDropZone(element, dropZone);
        
        // Уведомляем Visual Builder
        if (this.visualBuilder) {
            this.visualBuilder.addToHistory();
            this.visualBuilder.updateLayersPanel();
        }
    }

    /**
     * Обработка множественного drop
     */
    handleMultiDrop(event, dropZone) {
        const elements = this.state.dragData.elements;
        if (!elements || elements.length === 0) return;

        // Перемещаем все элементы
        elements.forEach(element => {
            this.positionElementInDropZone(element, event, dropZone);
            this.moveElementToDropZone(element, dropZone);
        });
        
        // Уведомляем Visual Builder
        if (this.visualBuilder) {
            this.visualBuilder.addToHistory();
            this.visualBuilder.updateLayersPanel();
        }
    }

    /**
     * Создание элемента компонента
     */
    createComponentElement(component) {
        const element = document.createElement('div');
        element.className = 'draggable-element';
        element.dataset.componentType = component.category;
        element.dataset.componentId = `component_${Date.now()}`;
        
        // Добавляем содержимое
        element.innerHTML = component.template;
        
        // Применяем стили
        Object.assign(element.style, component.defaultStyles);
        
        return element;
    }

    /**
     * Позиционирование элемента в зоне drop
     */
    positionElementInDropZone(element, event, dropZone) {
        const dropRect = dropZone.element.getBoundingClientRect();
        const canvasRect = document.getElementById('canvas')?.getBoundingClientRect();
        
        if (!canvasRect) return;

        // Вычисляем позицию относительно canvas
        let x = event.clientX - canvasRect.left;
        let y = event.clientY - canvasRect.top;
        
        // Применяем snap to grid
        if (dropZone.snapToGrid && this.config.snapToGrid) {
            x = Math.round(x / this.gridSize) * this.gridSize;
            y = Math.round(y / this.gridSize) * this.gridSize;
        }
        
        // Устанавливаем позицию
        element.style.position = 'absolute';
        element.style.left = `${x}px`;
        element.style.top = `${y}px`;
    }

    /**
     * Вставка элемента в зону drop
     */
    insertElementInDropZone(element, dropZone) {
        switch (dropZone.insertMode) {
            case 'append':
                dropZone.element.appendChild(element);
                break;
            case 'prepend':
                dropZone.element.insertBefore(element, dropZone.element.firstChild);
                break;
            case 'replace':
                dropZone.element.innerHTML = '';
                dropZone.element.appendChild(element);
                break;
            default:
                dropZone.element.appendChild(element);
        }
    }

    /**
     * Перемещение элемента в зону drop
     */
    moveElementToDropZone(element, dropZone) {
        dropZone.element.appendChild(element);
    }

    /**
     * Поиск зоны drop
     */
    findDropZone(target) {
        const dropZoneElement = target.closest('.drop-zone');
        if (!dropZoneElement) return null;

        return this.dropZones.find(zone => zone.element === dropZoneElement);
    }

    /**
     * Подсветка зоны drop
     */
    highlightDropZone(dropZone, highlight) {
        if (!dropZone.highlight) return;

        dropZone.active = highlight;
        
        if (highlight) {
            dropZone.element.classList.add('drop-zone-active');
        } else {
            dropZone.element.classList.remove('drop-zone-active');
        }
    }

    /**
     * Очистка подсветки зон drop
     */
    clearDropZoneHighlights() {
        this.dropZones.forEach(zone => {
            this.highlightDropZone(zone, false);
        });
    }

    /**
     * Показ snap lines
     */
    showSnapLines(event) {
        // Очищаем предыдущие snap lines
        this.clearSnapLines();
        
        const canvas = document.getElementById('canvas');
        if (!canvas) return;

        const canvasRect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - canvasRect.left;
        const mouseY = event.clientY - canvasRect.top;
        
        // Находим ближайшие элементы для snap
        const elements = canvas.querySelectorAll('.draggable-element:not(.dragging)');
        
        elements.forEach(element => {
            const elementRect = element.getBoundingClientRect();
            const elementLeft = elementRect.left - canvasRect.left;
            const elementTop = elementRect.top - canvasRect.top;
            const elementRight = elementLeft + elementRect.width;
            const elementBottom = elementTop + elementRect.height;
            
            // Проверяем горизонтальные snap lines
            if (Math.abs(mouseY - elementTop) < this.config.snapThreshold) {
                this.createSnapLine('horizontal', elementTop);
            }
            if (Math.abs(mouseY - elementBottom) < this.config.snapThreshold) {
                this.createSnapLine('horizontal', elementBottom);
            }
            
            // Проверяем вертикальные snap lines
            if (Math.abs(mouseX - elementLeft) < this.config.snapThreshold) {
                this.createSnapLine('vertical', elementLeft);
            }
            if (Math.abs(mouseX - elementRight) < this.config.snapThreshold) {
                this.createSnapLine('vertical', elementRight);
            }
        });
    }

    /**
     * Создание snap line
     */
    createSnapLine(direction, position) {
        const line = document.createElement('div');
        line.className = `snap-line snap-line-${direction}`;
        line.style.position = 'absolute';
        line.style.backgroundColor = '#3ECDC1';
        line.style.zIndex = '9999';
        line.style.pointerEvents = 'none';
        
        if (direction === 'horizontal') {
            line.style.left = '0';
            line.style.top = `${position}px`;
            line.style.width = '100%';
            line.style.height = '2px';
        } else {
            line.style.top = '0';
            line.style.left = `${position}px`;
            line.style.width = '2px';
            line.style.height = '100%';
        }
        
        const canvas = document.getElementById('canvas');
        if (canvas) {
            canvas.appendChild(line);
            this.state.snapLines[direction].push(line);
        }
    }

    /**
     * Очистка snap lines
     */
    clearSnapLines() {
        Object.values(this.state.snapLines).flat().forEach(line => {
            if (line.parentNode) {
                line.parentNode.removeChild(line);
            }
        });
        
        this.state.snapLines = { horizontal: [], vertical: [] };
    }

    /**
     * Обработчик окончания перетаскивания
     */
    handleDragEnd(event) {
        this.clearDragState();
    }

    /**
     * Очистка состояния перетаскивания
     */
    clearDragState() {
        // Убираем классы
        document.querySelectorAll('.dragging').forEach(el => {
            el.classList.remove('dragging');
        });
        
        // Удаляем превью
        if (this.state.dragPreview) {
            this.state.dragPreview.remove();
            this.state.dragPreview = null;
        }
        
        // Очищаем подсветку
        this.clearDropZoneHighlights();
        this.clearSnapLines();
        
        // Сбрасываем состояние
        this.state = {
            isDragging: false,
            dragType: null,
            dragData: null,
            dropTarget: null,
            dragPreview: null,
            snapLines: { horizontal: [], vertical: [] }
        };
    }

    /**
     * Обработчики мыши
     */
    handleMouseDown(event) {
        // Логика для множественного выделения
        if (event.ctrlKey || event.metaKey) {
            this.multiSelectMode = true;
        }
    }

    handleMouseMove(event) {
        // Обновляем позицию превью при перетаскивании
        if (this.state.isDragging && this.state.dragPreview) {
            this.updateDragPreviewPosition(event);
        }
    }

    handleMouseUp(event) {
        this.multiSelectMode = false;
    }

    /**
     * Обработчики клавиатуры
     */
    handleKeyDown(event) {
        switch (event.key) {
            case 'Escape':
                if (this.state.isDragging) {
                    this.cancelDrag();
                }
                break;
            case 'Shift':
                this.multiSelectMode = true;
                break;
            case 'g':
                if (event.ctrlKey || event.metaKey) {
                    this.toggleSnapToGrid();
                }
                break;
        }
    }

    handleKeyUp(event) {
        if (event.key === 'Shift') {
            this.multiSelectMode = false;
        }
    }

    /**
     * Обработчики canvas
     */
    handleCanvasClick(event) {
        // Логика выделения элементов
        const element = event.target.closest('.draggable-element');
        if (element) {
            this.selectElement(element, this.multiSelectMode);
        } else {
            this.clearSelection();
        }
    }

    handleCanvasDoubleClick(event) {
        // Логика редактирования элементов
        const element = event.target.closest('.draggable-element');
        if (element) {
            this.editElement(element);
        }
    }

    /**
     * Выделение элемента
     */
    selectElement(element, multiSelect = false) {
        if (!multiSelect) {
            this.clearSelection();
        }
        
        if (!this.selectedElements.includes(element)) {
            this.selectedElements.push(element);
            element.classList.add('selected-element');
        }
    }

    /**
     * Очистка выделения
     */
    clearSelection() {
        this.selectedElements.forEach(element => {
            element.classList.remove('selected-element');
        });
        this.selectedElements = [];
    }

    /**
     * Редактирование элемента
     */
    editElement(element) {
        const editableElement = element.querySelector('[contenteditable="true"]');
        if (editableElement) {
            editableElement.focus();
            const range = document.createRange();
            range.selectNodeContents(editableElement);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    /**
     * Отмена перетаскивания
     */
    cancelDrag() {
        this.clearDragState();
        console.info('❌ Перетаскивание отменено');
    }

    /**
     * Переключение snap to grid
     */
    toggleSnapToGrid() {
        this.config.snapToGrid = !this.config.snapToGrid;
        this.visualBuilder?.showNotification(
            `Snap to grid ${this.config.snapToGrid ? 'включен' : 'выключен'}`,
            'info'
        );
    }

    /**
     * Настройка горячих клавиш
     */
    setupKeyboardShortcuts() {
        // Уже реализовано в handleKeyDown
        console.info('⌨️ Горячие клавиши Drag & Drop настроены');
    }

    /**
     * Получение состояния
     */
    getState() {
        return this.state;
    }

    /**
     * Получение конфигурации
     */
    getConfig() {
        return this.config;
    }

    /**
     * Обновление конфигурации
     */
    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
    }
}

// Глобальный экземпляр
let dragDropEditor;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        dragDropEditor = new DragDropEditor(window.visualBuilder);
        window.dragDropEditor = dragDropEditor;
        console.info('🎯 Drag & Drop Editor готова к использованию');
    }
}); 