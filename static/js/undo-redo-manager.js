/**
 * Undo/Redo Manager для Visual Builder
 * Продвинутая система отмены и повтора действий
 */

class UndoRedoManager {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.history = [];
        this.currentIndex = -1;
        this.maxHistory = 50;
        this.isUndoRedoAction = false;
        this.batchOperations = [];
        this.batchTimeout = null;
        this.batchDelay = 1000; // 1 секунда для группировки операций
        
        // Типы операций
        this.operationTypes = {
            ELEMENT_CREATE: 'element_create',
            ELEMENT_DELETE: 'element_delete',
            ELEMENT_MOVE: 'element_move',
            ELEMENT_DUPLICATE: 'element_duplicate',
            ELEMENT_EDIT: 'element_edit',
            ELEMENT_STYLE: 'element_style',
            ELEMENT_RESIZE: 'element_resize',
            ELEMENT_VISIBILITY: 'element_visibility',
            ELEMENT_ORDER: 'element_order',
            CONTENT_CHANGE: 'content_change',
            STYLE_CHANGE: 'style_change',
            LAYOUT_CHANGE: 'layout_change',
            BATCH_OPERATION: 'batch_operation',
            CANVAS_CLEAR: 'canvas_clear',
            CANVAS_LOAD: 'canvas_load'
        };
        
        // Настройки
        this.config = {
            autoSave: true,
            saveOnContentChange: true,
            saveOnStyleChange: true,
            saveOnLayoutChange: true,
            maxHistorySize: 50,
            batchTimeout: 1000,
            compressHistory: true,
            detailedLogging: false
        };
        
        this.init();
    }
    
    /**
     * Инициализация менеджера
     */
    init() {
        this.setupEventListeners();
        this.createInitialState();
        console.info('🔄 Undo/Redo Manager инициализирован');
    }
    
    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Отслеживаем изменения в contenteditable элементах
        document.addEventListener('input', this.handleContentChange.bind(this), true);
        
        // Отслеживаем изменения стилей
        const observer = new MutationObserver(this.handleDOMChanges.bind(this));
        observer.observe(this.visualBuilder.dom.canvas, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class', 'data-*']
        });
        
        // Горячие клавиши
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Автосохранение при потере фокуса
        document.addEventListener('blur', this.handleBlur.bind(this), true);
    }
    
    /**
     * Создание начального состояния
     */
    createInitialState() {
        const initialState = this.captureState('initial_state');
        this.saveState(initialState);
    }
    
    /**
     * Захват текущего состояния
     */
    captureState(operationType, details = {}) {
        const canvas = this.visualBuilder.dom.canvas;
        const elements = Array.from(canvas.querySelectorAll('.draggable-element')).map(element => {
            return {
                id: element.dataset.id,
                type: element.dataset.type,
                content: element.innerHTML,
                styles: this.getElementStyles(element),
                position: this.getElementPosition(element),
                classes: element.className,
                attributes: this.getElementAttributes(element)
            };
        });
        
        return {
            timestamp: Date.now(),
            operationType,
            details,
            elements,
            canvasStyles: this.getElementStyles(canvas),
            selectedElement: this.visualBuilder.state.selectedElement?.dataset.id || null,
            zoom: this.visualBuilder.state.zoom,
            gridSnap: this.visualBuilder.state.gridSnap
        };
    }
    
    /**
     * Получение стилей элемента
     */
    getElementStyles(element) {
        const computedStyles = window.getComputedStyle(element);
        const importantStyles = [
            'position', 'top', 'left', 'width', 'height',
            'margin', 'padding', 'border', 'background',
            'color', 'font-size', 'font-weight', 'text-align',
            'display', 'flex-direction', 'justify-content', 'align-items',
            'opacity', 'transform', 'z-index'
        ];
        
        const styles = {};
        importantStyles.forEach(property => {
            const value = computedStyles.getPropertyValue(property);
            if (value && value !== 'normal' && value !== 'none') {
                styles[property] = value;
            }
        });
        
        return styles;
    }
    
    /**
     * Получение позиции элемента
     */
    getElementPosition(element) {
        const rect = element.getBoundingClientRect();
        const canvasRect = this.visualBuilder.dom.canvas.getBoundingClientRect();
        
        return {
            x: rect.left - canvasRect.left,
            y: rect.top - canvasRect.top,
            width: rect.width,
            height: rect.height
        };
    }
    
    /**
     * Получение атрибутов элемента
     */
    getElementAttributes(element) {
        const attributes = {};
        for (let attr of element.attributes) {
            if (attr.name.startsWith('data-') || attr.name === 'class') {
                attributes[attr.name] = attr.value;
            }
        }
        return attributes;
    }
    
    /**
     * Сохранение состояния
     */
    saveState(state) {
        if (this.isUndoRedoAction) return;
        
        // Удаляем состояния после текущего индекса при новом действии
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }
        
        // Добавляем новое состояние
        this.history.push(state);
        this.currentIndex++;
        
        // Ограничиваем размер истории
        if (this.history.length > this.config.maxHistorySize) {
            this.history.shift();
            this.currentIndex--;
        }
        
        // Сжимаем историю если включено
        if (this.config.compressHistory) {
            this.compressHistory();
        }
        
        this.updateUI();
        this.logState('Состояние сохранено', state);
    }
    
    /**
     * Сохранение состояния с задержкой (для группировки операций)
     */
    saveStateDelayed(operationType, details = {}) {
        // Очищаем предыдущий таймер
        if (this.batchTimeout) {
            clearTimeout(this.batchTimeout);
        }
        
        // Добавляем операцию в пакет
        this.batchOperations.push({ operationType, details });
        
        // Устанавливаем новый таймер
        this.batchTimeout = setTimeout(() => {
            if (this.batchOperations.length > 0) {
                const state = this.captureState('batch_operation', {
                    operations: this.batchOperations
                });
                this.saveState(state);
                this.batchOperations = [];
            }
        }, this.config.batchTimeout);
    }
    
    /**
     * Отмена действия
     */
    undo() {
        if (this.canUndo()) {
            this.isUndoRedoAction = true;
            
            this.currentIndex--;
            const previousState = this.history[this.currentIndex];
            this.restoreState(previousState);
            
            this.isUndoRedoAction = false;
            this.updateUI();
            
            this.visualBuilder.showNotification('Действие отменено', 'info');
            this.logState('Отменено действие', previousState);
        }
    }
    
    /**
     * Повтор действия
     */
    redo() {
        if (this.canRedo()) {
            this.isUndoRedoAction = true;
            
            this.currentIndex++;
            const nextState = this.history[this.currentIndex];
            this.restoreState(nextState);
            
            this.isUndoRedoAction = false;
            this.updateUI();
            
            this.visualBuilder.showNotification('Действие повторено', 'info');
            this.logState('Повторено действие', nextState);
        }
    }
    
    /**
     * Восстановление состояния
     */
    restoreState(state) {
        const canvas = this.visualBuilder.dom.canvas;
        
        // Очищаем canvas
        canvas.innerHTML = '';
        
        // Восстанавливаем элементы
        state.elements.forEach(elementData => {
            const element = this.createElementFromState(elementData);
            if (element) {
                canvas.appendChild(element);
            }
        });
        
        // Восстанавливаем стили canvas
        this.applyStyles(canvas, state.canvasStyles);
        
        // Восстанавливаем выбранный элемент
        if (state.selectedElement) {
            const selectedElement = canvas.querySelector(`[data-id="${state.selectedElement}"]`);
            if (selectedElement) {
                this.visualBuilder.selectElement(selectedElement);
            }
        }
        
        // Восстанавливаем состояние приложения
        this.visualBuilder.state.zoom = state.zoom;
        this.visualBuilder.state.gridSnap = state.gridSnap;
        
        // Обновляем UI
        this.visualBuilder.updateLayersPanel();
        this.visualBuilder.updatePropertiesPanel();
        
        // Настраиваем обработчики для восстановленных элементов
        this.visualBuilder.setupExistingElements();
    }
    
    /**
     * Создание элемента из состояния
     */
    createElementFromState(elementData) {
        const element = document.createElement('div');
        element.className = `draggable-element element-${elementData.type}`;
        element.dataset.id = elementData.id;
        element.dataset.type = elementData.type;
        element.innerHTML = elementData.content;
        
        // Применяем стили
        this.applyStyles(element, elementData.styles);
        
        // Применяем классы
        if (elementData.classes) {
            element.className = elementData.classes;
        }
        
        // Применяем атрибуты
        Object.entries(elementData.attributes).forEach(([name, value]) => {
            element.setAttribute(name, value);
        });
        
        return element;
    }
    
    /**
     * Применение стилей к элементу
     */
    applyStyles(element, styles) {
        Object.entries(styles).forEach(([property, value]) => {
            element.style.setProperty(property, value);
        });
    }
    
    /**
     * Проверка возможности отмены
     */
    canUndo() {
        return this.currentIndex > 0;
    }
    
    /**
     * Проверка возможности повтора
     */
    canRedo() {
        return this.currentIndex < this.history.length - 1;
    }
    
    /**
     * Обновление UI
     */
    updateUI() {
        // Обновляем кнопки undo/redo
        const undoBtn = this.visualBuilder.dom.undoBtn;
        const redoBtn = this.visualBuilder.dom.redoBtn;
        
        if (undoBtn) {
            undoBtn.disabled = !this.canUndo();
        }
        
        if (redoBtn) {
            redoBtn.disabled = !this.canRedo();
        }
        
        // Обновляем индикатор истории
        this.updateHistoryIndicator();
    }
    
    /**
     * Обновление индикатора истории
     */
    updateHistoryIndicator() {
        const indicator = document.getElementById('historyIndicator');
        if (indicator) {
            const canUndo = this.canUndo();
            const canRedo = this.canRedo();
            
            indicator.innerHTML = `
                <div class="history-info">
                    <span class="history-count">${this.currentIndex + 1}/${this.history.length}</span>
                    <span class="history-status">
                        ${canUndo ? '🔄' : '⏹️'} ${canRedo ? '🔄' : '⏹️'}
                    </span>
                </div>
            `;
        }
    }
    
    /**
     * Обработка изменений контента
     */
    handleContentChange(event) {
        if (this.isUndoRedoAction) return;
        
        const target = event.target;
        if (target.closest('.draggable-element') && target.hasAttribute('contenteditable')) {
            this.saveStateDelayed(this.operationTypes.CONTENT_CHANGE, {
                elementId: target.closest('.draggable-element').dataset.id,
                property: 'content',
                value: target.innerHTML
            });
        }
    }
    
    /**
     * Обработка изменений DOM
     */
    handleDOMChanges(mutations) {
        if (this.isUndoRedoAction) return;
        
        mutations.forEach(mutation => {
            if (mutation.type === 'childList') {
                // Добавление/удаление элементов
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('draggable-element')) {
                        this.saveStateDelayed(this.operationTypes.ELEMENT_CREATE, {
                            elementId: node.dataset.id,
                            elementType: node.dataset.type
                        });
                    }
                });
                
                mutation.removedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('draggable-element')) {
                        this.saveStateDelayed(this.operationTypes.ELEMENT_DELETE, {
                            elementId: node.dataset.id,
                            elementType: node.dataset.type
                        });
                    }
                });
            } else if (mutation.type === 'attributes') {
                // Изменение атрибутов
                const element = mutation.target;
                if (element.classList.contains('draggable-element')) {
                    if (mutation.attributeName === 'style') {
                        this.saveStateDelayed(this.operationTypes.ELEMENT_STYLE, {
                            elementId: element.dataset.id,
                            property: 'style',
                            value: element.getAttribute('style')
                        });
                    } else if (mutation.attributeName === 'class') {
                        this.saveStateDelayed(this.operationTypes.ELEMENT_STYLE, {
                            elementId: element.dataset.id,
                            property: 'class',
                            value: element.getAttribute('class')
                        });
                    }
                }
            }
        });
    }
    
    /**
     * Обработка горячих клавиш
     */
    handleKeyboardShortcuts(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key.toLowerCase()) {
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
            }
        }
    }
    
    /**
     * Обработка потери фокуса
     */
    handleBlur(event) {
        if (this.config.autoSave && !this.isUndoRedoAction) {
            // Сохраняем состояние при потере фокуса
            setTimeout(() => {
                if (!this.batchTimeout) {
                    const state = this.captureState('blur_save');
                    this.saveState(state);
                }
            }, 100);
        }
    }
    
    /**
     * Сжатие истории
     */
    compressHistory() {
        if (this.history.length < this.config.maxHistorySize * 0.8) return;
        
        const compressedHistory = [];
        let i = 0;
        
        while (i < this.history.length) {
            const current = this.history[i];
            
            // Пропускаем незначительные изменения
            if (this.isMinorChange(current)) {
                i++;
                continue;
            }
            
            // Группируем похожие операции
            let similarCount = 1;
            while (i + similarCount < this.history.length && 
                   this.areSimilarOperations(current, this.history[i + similarCount])) {
                similarCount++;
            }
            
            if (similarCount > 1) {
                // Создаем сжатое состояние
                const compressedState = this.compressSimilarStates(
                    this.history.slice(i, i + similarCount)
                );
                compressedHistory.push(compressedState);
                i += similarCount;
            } else {
                compressedHistory.push(current);
                i++;
            }
        }
        
        this.history = compressedHistory;
        this.currentIndex = Math.min(this.currentIndex, this.history.length - 1);
    }
    
    /**
     * Проверка на незначительное изменение
     */
    isMinorChange(state) {
        return state.operationType === 'content_change' && 
               state.details.value && 
               state.details.value.length < 10;
    }
    
    /**
     * Проверка на похожие операции
     */
    areSimilarOperations(state1, state2) {
        return state1.operationType === state2.operationType &&
               state1.details.elementId === state2.details.elementId &&
               Math.abs(state1.timestamp - state2.timestamp) < 5000; // 5 секунд
    }
    
    /**
     * Сжатие похожих состояний
     */
    compressSimilarStates(states) {
        // Берем последнее состояние из группы
        return states[states.length - 1];
    }
    
    /**
     * Очистка истории
     */
    clearHistory() {
        this.history = [];
        this.currentIndex = -1;
        this.batchOperations = [];
        this.updateUI();
        this.visualBuilder.showNotification('История очищена', 'info');
    }
    
    /**
     * Экспорт истории
     */
    exportHistory() {
        const historyData = {
            timestamp: Date.now(),
            version: '1.0',
            history: this.history,
            currentIndex: this.currentIndex,
            config: this.config
        };
        
        const dataStr = JSON.stringify(historyData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `visual-builder-history-${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.visualBuilder.showNotification('История экспортирована', 'success');
    }
    
    /**
     * Импорт истории
     */
    importHistory(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const historyData = JSON.parse(e.target.result);
                
                if (historyData.version && historyData.history) {
                    this.history = historyData.history;
                    this.currentIndex = historyData.currentIndex || 0;
                    
                    if (historyData.config) {
                        Object.assign(this.config, historyData.config);
                    }
                    
                    this.updateUI();
                    this.visualBuilder.showNotification('История импортирована', 'success');
                } else {
                    throw new Error('Неверный формат файла истории');
                }
            } catch (error) {
                console.error('Ошибка импорта истории:', error);
                this.visualBuilder.showNotification('Ошибка импорта истории', 'error');
            }
        };
        reader.readAsText(file);
    }
    
    /**
     * Получение статистики истории
     */
    getHistoryStats() {
        const stats = {
            totalStates: this.history.length,
            currentIndex: this.currentIndex,
            canUndo: this.canUndo(),
            canRedo: this.canRedo(),
            operationTypes: {},
            memoryUsage: this.estimateMemoryUsage()
        };
        
        // Подсчитываем типы операций
        this.history.forEach(state => {
            const type = state.operationType;
            stats.operationTypes[type] = (stats.operationTypes[type] || 0) + 1;
        });
        
        return stats;
    }
    
    /**
     * Оценка использования памяти
     */
    estimateMemoryUsage() {
        const historyString = JSON.stringify(this.history);
        return historyString.length * 2; // Примерная оценка в байтах
    }
    
    /**
     * Логирование состояний
     */
    logState(message, state) {
        if (this.config.detailedLogging) {
            console.log(`🔄 ${message}:`, {
                operationType: state.operationType,
                timestamp: new Date(state.timestamp).toLocaleTimeString(),
                elementsCount: state.elements.length,
                details: state.details
            });
        }
    }
    
    /**
     * Получение конфигурации
     */
    getConfig() {
        return { ...this.config };
    }
    
    /**
     * Обновление конфигурации
     */
    updateConfig(newConfig) {
        Object.assign(this.config, newConfig);
        
        // Применяем изменения
        if (this.config.maxHistorySize < this.history.length) {
            this.history = this.history.slice(-this.config.maxHistorySize);
            this.currentIndex = Math.min(this.currentIndex, this.history.length - 1);
        }
        
        this.updateUI();
    }
    
    /**
     * Создание индикатора истории
     */
    createHistoryIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'historyIndicator';
        indicator.className = 'history-indicator';
        indicator.innerHTML = `
            <div class="history-info">
                <span class="history-count">1/1</span>
                <span class="history-status">⏹️ ⏹️</span>
            </div>
        `;
        
        return indicator;
    }
    
    /**
     * Показать панель истории
     */
    showHistoryPanel() {
        const stats = this.getHistoryStats();
        const historyHTML = this.generateHistoryHTML();
        
        const modal = document.createElement('div');
        modal.className = 'history-panel-modal';
        modal.innerHTML = `
            <div class="history-panel-content">
                <div class="history-panel-header">
                    <h3 class="history-panel-title">
                        <i class="bi bi-clock-history"></i>
                        История изменений
                    </h3>
                    <button class="history-panel-close" onclick="this.closest('.history-panel-modal').remove()">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="history-panel-body">
                    <div class="history-stats">
                        <div class="stat-item">
                            <span class="stat-label">Всего состояний:</span>
                            <span class="stat-value">${stats.totalStates}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Текущая позиция:</span>
                            <span class="stat-value">${stats.currentIndex + 1}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Использование памяти:</span>
                            <span class="stat-value">${(stats.memoryUsage / 1024).toFixed(1)} KB</span>
                        </div>
                    </div>
                    <div class="history-list">
                        ${historyHTML}
                    </div>
                </div>
                <div class="history-panel-footer">
                    <button class="btn btn-secondary" onclick="undoRedoManager.clearHistory()">
                        <i class="bi bi-trash"></i>
                        Очистить историю
                    </button>
                    <button class="btn btn-info" onclick="undoRedoManager.exportHistory()">
                        <i class="bi bi-download"></i>
                        Экспорт
                    </button>
                    <button class="btn btn-primary" onclick="this.closest('.history-panel-modal').remove()">
                        Закрыть
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'block';
        });
    }
    
    /**
     * Генерация HTML для истории
     */
    generateHistoryHTML() {
        if (this.history.length === 0) {
            return `
                <div class="history-empty">
                    <i class="bi bi-clock-history"></i>
                    <p>История пуста</p>
                </div>
            `;
        }
        
        return this.history.map((state, index) => {
            const isCurrent = index === this.currentIndex;
            const operationName = this.getOperationName(state.operationType);
            const time = new Date(state.timestamp).toLocaleTimeString();
            
            return `
                <div class="history-item ${isCurrent ? 'current' : ''}" 
                     onclick="undoRedoManager.goToState(${index})">
                    <div class="history-item-icon">
                        <i class="bi ${this.getOperationIcon(state.operationType)}"></i>
                    </div>
                    <div class="history-item-info">
                        <div class="history-item-title">${operationName}</div>
                        <div class="history-item-time">${time}</div>
                    </div>
                    <div class="history-item-status">
                        ${isCurrent ? '📍' : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    /**
     * Переход к определенному состоянию
     */
    goToState(index) {
        if (index >= 0 && index < this.history.length) {
            this.isUndoRedoAction = true;
            this.currentIndex = index;
            const state = this.history[index];
            this.restoreState(state);
            this.isUndoRedoAction = false;
            this.updateUI();
            
            this.visualBuilder.showNotification(`Переход к состоянию ${index + 1}`, 'info');
        }
    }
    
    /**
     * Получение названия операции
     */
    getOperationName(operationType) {
        const names = {
            'element_create': 'Создание элемента',
            'element_delete': 'Удаление элемента',
            'element_move': 'Перемещение элемента',
            'element_duplicate': 'Дублирование элемента',
            'element_edit': 'Редактирование элемента',
            'element_style': 'Изменение стилей',
            'element_resize': 'Изменение размера',
            'element_visibility': 'Изменение видимости',
            'element_order': 'Изменение порядка',
            'content_change': 'Изменение контента',
            'style_change': 'Изменение стилей',
            'layout_change': 'Изменение макета',
            'batch_operation': 'Группа операций',
            'canvas_clear': 'Очистка холста',
            'canvas_load': 'Загрузка холста',
            'initial_state': 'Начальное состояние',
            'blur_save': 'Автосохранение'
        };
        
        return names[operationType] || 'Неизвестная операция';
    }
    
    /**
     * Получение иконки операции
     */
    getOperationIcon(operationType) {
        const icons = {
            'element_create': 'bi-plus-circle',
            'element_delete': 'bi-trash',
            'element_move': 'bi-arrows-move',
            'element_duplicate': 'bi-files',
            'element_edit': 'bi-pencil',
            'element_style': 'bi-palette',
            'element_resize': 'bi-arrows-angle-expand',
            'element_visibility': 'bi-eye',
            'element_order': 'bi-list-ol',
            'content_change': 'bi-text-paragraph',
            'style_change': 'bi-palette2',
            'layout_change': 'bi-grid-3x3',
            'batch_operation': 'bi-collection',
            'canvas_clear': 'bi-trash3',
            'canvas_load': 'bi-folder2-open',
            'initial_state': 'bi-house',
            'blur_save': 'bi-save'
        };
        
        return icons[operationType] || 'bi-question-circle';
    }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UndoRedoManager;
} 