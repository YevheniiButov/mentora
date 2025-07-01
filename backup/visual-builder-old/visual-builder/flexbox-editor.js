/**
 * Flexbox Editor для Visual Builder
 * Визуальный редактор CSS Flexbox
 */

class FlexboxEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentElement = null;
        this.flexOverlay = null;
        this.isEditing = false;
        this.init();
    }

    /**
     * Инициализация редактора
     */
    init() {
        console.info('📦 Flexbox Editor инициализирован');
    }

    /**
     * Редактирование Flexbox элемента
     */
    editFlexbox(element) {
        this.currentElement = element;
        this.isEditing = true;
        
        // Показываем панель Flexbox редактора
        this.showFlexboxPanel();
        
        // Создаем визуальный overlay
        this.createFlexboxOverlay();
        
        // Анализируем текущий Flexbox
        this.analyzeCurrentFlexbox();
        
        console.info('📦 Flexbox Editor открыт для элемента:', element.tagName);
    }

    /**
     * Показать панель Flexbox редактора
     */
    showFlexboxPanel() {
        const panel = this.createFlexboxPanel();
        
        // Показываем панель справа
        const propertiesPanel = document.getElementById('propertiesPanel');
        if (propertiesPanel) {
            propertiesPanel.innerHTML = '';
            propertiesPanel.appendChild(panel);
            propertiesPanel.classList.add('active');
            propertiesPanel.style.display = 'flex';
        }
    }

    /**
     * Создание панели Flexbox редактора
     */
    createFlexboxPanel() {
        const panel = document.createElement('div');
        panel.className = 'flexbox-editor-panel';
        panel.innerHTML = `
            <div class="flexbox-panel-header">
                <h3>
                    <i class="bi bi-arrows-expand"></i>
                    CSS Flexbox Editor
                </h3>
                <div class="flexbox-actions">
                    <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.toggleFlexboxOverlay()" title="Показать/скрыть оси">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.resetFlexbox()" title="Сбросить Flexbox">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                </div>
            </div>
            
            <div class="flexbox-settings">
                <div class="flexbox-section">
                    <h4>Основные настройки</h4>
                    <div class="flexbox-control">
                        <label>Display:</label>
                        <select class="flexbox-input" id="flexboxDisplay" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('display', this.value)">
                            <option value="flex">Flex</option>
                            <option value="inline-flex">Inline Flex</option>
                            <option value="block">Block</option>
                            <option value="grid">Grid</option>
                        </select>
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Направление (flex-direction)</h4>
                    <div class="flexbox-control">
                        <label>Направление flex-контейнера:</label>
                        <select class="flexbox-input" id="flexDirection" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('flex-direction', this.value)">
                            <option value="row">Row (горизонтально)</option>
                            <option value="row-reverse">Row Reverse (горизонтально в обратном порядке)</option>
                            <option value="column">Column (вертикально)</option>
                            <option value="column-reverse">Column Reverse (вертикально в обратном порядке)</option>
                        </select>
                    </div>
                    <div class="flexbox-preview-direction" id="flexDirectionPreview">
                        <!-- Визуализация направления -->
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Перенос (flex-wrap)</h4>
                    <div class="flexbox-control">
                        <label>Перенос элементов:</label>
                        <select class="flexbox-input" id="flexWrap" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('flex-wrap', this.value)">
                            <option value="nowrap">No Wrap (без переноса)</option>
                            <option value="wrap">Wrap (с переносом)</option>
                            <option value="wrap-reverse">Wrap Reverse (с переносом в обратном порядке)</option>
                        </select>
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Выравнивание по главной оси (justify-content)</h4>
                    <div class="flexbox-control">
                        <label>Выравнивание по главной оси:</label>
                        <select class="flexbox-input" id="justifyContent" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('justify-content', this.value)">
                            <option value="flex-start">Flex Start (в начале)</option>
                            <option value="flex-end">Flex End (в конце)</option>
                            <option value="center">Center (по центру)</option>
                            <option value="space-between">Space Between (между элементами)</option>
                            <option value="space-around">Space Around (вокруг элементов)</option>
                            <option value="space-evenly">Space Evenly (равномерно)</option>
                        </select>
                    </div>
                    <div class="flexbox-preview-justify" id="justifyContentPreview">
                        <!-- Визуализация justify-content -->
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Выравнивание по поперечной оси (align-items)</h4>
                    <div class="flexbox-control">
                        <label>Выравнивание по поперечной оси:</label>
                        <select class="flexbox-input" id="alignItems" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('align-items', this.value)">
                            <option value="stretch">Stretch (растянуть)</option>
                            <option value="flex-start">Flex Start (в начале)</option>
                            <option value="flex-end">Flex End (в конце)</option>
                            <option value="center">Center (по центру)</option>
                            <option value="baseline">Baseline (по базовой линии)</option>
                        </select>
                    </div>
                    <div class="flexbox-preview-align" id="alignItemsPreview">
                        <!-- Визуализация align-items -->
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Выравнивание строк (align-content)</h4>
                    <div class="flexbox-control">
                        <label>Выравнивание строк (при flex-wrap: wrap):</label>
                        <select class="flexbox-input" id="alignContent" onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('align-content', this.value)">
                            <option value="stretch">Stretch (растянуть)</option>
                            <option value="flex-start">Flex Start (в начале)</option>
                            <option value="flex-end">Flex End (в конце)</option>
                            <option value="center">Center (по центру)</option>
                            <option value="space-between">Space Between (между строками)</option>
                            <option value="space-around">Space Around (вокруг строк)</option>
                        </select>
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Отступы (gap)</h4>
                    <div class="flexbox-control">
                        <label>Отступы между элементами:</label>
                        <input type="text" class="flexbox-input" id="flexboxGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('gap', this.value)">
                    </div>
                    <div class="flexbox-control">
                        <label>Отступы по строкам:</label>
                        <input type="text" class="flexbox-input" id="flexboxRowGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('row-gap', this.value)">
                    </div>
                    <div class="flexbox-control">
                        <label>Отступы по колонкам:</label>
                        <input type="text" class="flexbox-input" id="flexboxColumnGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.flexboxEditor.updateFlexboxProperty('column-gap', this.value)">
                    </div>
                </div>
                
                <div class="flexbox-section">
                    <h4>Пресеты Flexbox</h4>
                    <div class="flexbox-presets">
                        <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.applyFlexboxPreset('center')">
                            <i class="bi bi-arrows-move"></i> Центрирование
                        </button>
                        <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.applyFlexboxPreset('space-between')">
                            <i class="bi bi-arrows-expand"></i> Распределение
                        </button>
                        <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.applyFlexboxPreset('column')">
                            <i class="bi bi-arrow-down"></i> Вертикальный
                        </button>
                        <button class="btn btn-sm" onclick="visualBuilder.flexboxEditor.applyFlexboxPreset('responsive')">
                            <i class="bi bi-phone"></i> Адаптивный
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="flexbox-visualizer">
                <h4>Визуализация Flexbox</h4>
                <div class="flexbox-preview" id="flexboxPreview">
                    <!-- Flexbox preview будет создан динамически -->
                </div>
                <div class="flexbox-info">
                    <div class="flexbox-info-item">
                        <span class="info-label">Направление:</span>
                        <span class="info-value" id="flexboxInfoDirection">row</span>
                    </div>
                    <div class="flexbox-info-item">
                        <span class="info-label">Перенос:</span>
                        <span class="info-value" id="flexboxInfoWrap">nowrap</span>
                    </div>
                    <div class="flexbox-info-item">
                        <span class="info-label">Элементы:</span>
                        <span class="info-value" id="flexboxInfoItems">0</span>
                    </div>
                </div>
            </div>
        `;

        // Настраиваем обработчики
        this.setupFlexboxPanelEvents(panel);
        
        // Инициализируем значения
        this.initializeFlexboxValues();

        return panel;
    }

    /**
     * Настройка событий Flexbox панели
     */
    setupFlexboxPanelEvents(panel) {
        // Обработчики для всех select элементов
        panel.querySelectorAll('.flexbox-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const property = e.target.id;
                const value = e.target.value;
                this.updateFlexboxProperty(property, value);
            });
        });
    }

    /**
     * Инициализация значений Flexbox
     */
    initializeFlexboxValues() {
        if (!this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        
        // Display
        const displaySelect = document.getElementById('flexboxDisplay');
        if (displaySelect) {
            displaySelect.value = styles.display;
        }

        // Flex direction
        const directionSelect = document.getElementById('flexDirection');
        if (directionSelect) {
            directionSelect.value = styles.flexDirection;
        }

        // Flex wrap
        const wrapSelect = document.getElementById('flexWrap');
        if (wrapSelect) {
            wrapSelect.value = styles.flexWrap;
        }

        // Justify content
        const justifySelect = document.getElementById('justifyContent');
        if (justifySelect) {
            justifySelect.value = styles.justifyContent;
        }

        // Align items
        const alignSelect = document.getElementById('alignItems');
        if (alignSelect) {
            alignSelect.value = styles.alignItems;
        }

        // Align content
        const alignContentSelect = document.getElementById('alignContent');
        if (alignContentSelect) {
            alignContentSelect.value = styles.alignContent;
        }

        // Gap
        const gapInput = document.getElementById('flexboxGap');
        if (gapInput) {
            gapInput.value = styles.gap;
        }

        // Обновляем визуализацию
        this.updateFlexboxVisualization();
    }

    /**
     * Обновление свойства Flexbox
     */
    updateFlexboxProperty(property, value) {
        if (!this.currentElement) return;

        try {
            // Преобразуем ID в CSS свойство
            const cssProperty = this.getCSSPropertyFromId(property);
            
            this.currentElement.style.setProperty(cssProperty, value);
            
            // Обновляем визуализацию
            this.updateFlexboxVisualization();
            
            // Обновляем overlay
            this.updateFlexboxOverlay();
            
            // Сохраняем в историю
            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }
            
            console.info(`✅ Flexbox свойство обновлено: ${cssProperty}: ${value}`);
            
        } catch (error) {
            console.error('Ошибка обновления Flexbox свойства:', error);
            this.vb.showNotification('Ошибка обновления Flexbox свойства', 'error');
        }
    }

    /**
     * Получение CSS свойства из ID элемента
     */
    getCSSPropertyFromId(id) {
        const propertyMap = {
            'flexboxDisplay': 'display',
            'flexDirection': 'flex-direction',
            'flexWrap': 'flex-wrap',
            'justifyContent': 'justify-content',
            'alignItems': 'align-items',
            'alignContent': 'align-content',
            'flexboxGap': 'gap',
            'flexboxRowGap': 'row-gap',
            'flexboxColumnGap': 'column-gap'
        };
        
        return propertyMap[id] || id;
    }

    /**
     * Создание визуального overlay для Flexbox
     */
    createFlexboxOverlay() {
        if (this.flexOverlay) {
            this.flexOverlay.remove();
        }

        this.flexOverlay = document.createElement('div');
        this.flexOverlay.className = 'flexbox-overlay';
        this.flexOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
            border: 2px dashed rgba(255, 193, 7, 0.6);
            background: rgba(255, 193, 7, 0.05);
        `;

        // Добавляем оси
        this.addFlexboxAxes();

        if (this.currentElement) {
            this.currentElement.style.position = 'relative';
            this.currentElement.appendChild(this.flexOverlay);
        }
    }

    /**
     * Добавление осей Flexbox
     */
    addFlexboxAxes() {
        if (!this.flexOverlay) return;

        // Главная ось
        const mainAxis = document.createElement('div');
        mainAxis.className = 'flexbox-main-axis';
        mainAxis.style.cssText = `
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
            transform: translateY(-50%);
            z-index: 1001;
        `;

        // Поперечная ось
        const crossAxis = document.createElement('div');
        crossAxis.className = 'flexbox-cross-axis';
        crossAxis.style.cssText = `
            position: absolute;
            top: 0;
            left: 50%;
            width: 2px;
            height: 100%;
            background: linear-gradient(180deg, #2196f3 0%, #1976d2 100%);
            transform: translateX(-50%);
            z-index: 1001;
        `;

        this.flexOverlay.appendChild(mainAxis);
        this.flexOverlay.appendChild(crossAxis);
    }

    /**
     * Обновление Flexbox overlay
     */
    updateFlexboxOverlay() {
        if (!this.flexOverlay || !this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const direction = styles.flexDirection;

        // Обновляем оси в зависимости от направления
        const mainAxis = this.flexOverlay.querySelector('.flexbox-main-axis');
        const crossAxis = this.flexOverlay.querySelector('.flexbox-cross-axis');

        if (mainAxis && crossAxis) {
            if (direction === 'column' || direction === 'column-reverse') {
                // Вертикальное направление
                mainAxis.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 50%;
                    width: 2px;
                    height: 100%;
                    background: linear-gradient(180deg, #ffc107 0%, #ff9800 100%);
                    transform: translateX(-50%);
                    z-index: 1001;
                `;
                
                crossAxis.style.cssText = `
                    position: absolute;
                    top: 50%;
                    left: 0;
                    width: 100%;
                    height: 2px;
                    background: linear-gradient(90deg, #2196f3 0%, #1976d2 100%);
                    transform: translateY(-50%);
                    z-index: 1001;
                `;
            } else {
                // Горизонтальное направление
                mainAxis.style.cssText = `
                    position: absolute;
                    top: 50%;
                    left: 0;
                    width: 100%;
                    height: 2px;
                    background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
                    transform: translateY(-50%);
                    z-index: 1001;
                `;
                
                crossAxis.style.cssText = `
                    position: absolute;
                    top: 0;
                    left: 50%;
                    width: 2px;
                    height: 100%;
                    background: linear-gradient(180deg, #2196f3 0%, #1976d2 100%);
                    transform: translateX(-50%);
                    z-index: 1001;
                `;
            }
        }
    }

    /**
     * Переключение видимости Flexbox overlay
     */
    toggleFlexboxOverlay() {
        if (this.flexOverlay) {
            this.flexOverlay.style.display = this.flexOverlay.style.display === 'none' ? 'block' : 'none';
        }
    }

    /**
     * Анализ текущего Flexbox
     */
    analyzeCurrentFlexbox() {
        if (!this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const children = this.currentElement.children;
        
        // Подсчитываем элементы
        let flexItems = 0;
        for (let i = 0; i < children.length; i++) {
            const child = children[i];
            if (child.classList.contains('draggable-element') || 
                child.classList.contains('imported-element')) {
                flexItems++;
            }
        }

        // Обновляем информацию
        this.updateFlexboxInfo(styles, flexItems);
    }

    /**
     * Обновление информации о Flexbox
     */
    updateFlexboxInfo(styles, itemCount) {
        const directionInfo = document.getElementById('flexboxInfoDirection');
        const wrapInfo = document.getElementById('flexboxInfoWrap');
        const itemsInfo = document.getElementById('flexboxInfoItems');

        if (directionInfo) directionInfo.textContent = styles.flexDirection;
        if (wrapInfo) wrapInfo.textContent = styles.flexWrap;
        if (itemsInfo) itemsInfo.textContent = itemCount;
    }

    /**
     * Обновление визуализации Flexbox
     */
    updateFlexboxVisualization() {
        const preview = document.getElementById('flexboxPreview');
        if (!preview || !this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const direction = styles.flexDirection;
        const wrap = styles.flexWrap;
        const justify = styles.justifyContent;
        const align = styles.alignItems;
        const gap = styles.gap || '0px';

        // Создаем визуализацию
        preview.innerHTML = '';
        preview.style.cssText = `
            display: flex;
            flex-direction: ${direction};
            flex-wrap: ${wrap};
            justify-content: ${justify};
            align-items: ${align};
            gap: ${gap};
            width: 100%;
            height: 200px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
        `;

        // Добавляем элементы
        const itemCount = this.getFlexboxItemCount();
        for (let i = 0; i < itemCount; i++) {
            const item = document.createElement('div');
            item.className = 'flexbox-item';
            item.style.cssText = `
                background: rgba(33, 150, 243, 0.8);
                border: 1px solid #1976d2;
                border-radius: 4px;
                padding: 10px;
                min-width: 60px;
                min-height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: white;
                font-weight: bold;
            `;
            item.textContent = `${i + 1}`;
            preview.appendChild(item);
        }

        // Обновляем информацию
        this.analyzeCurrentFlexbox();
    }

    /**
     * Получение количества элементов Flexbox
     */
    getFlexboxItemCount() {
        if (!this.currentElement) return 3;

        const children = this.currentElement.children;
        let count = 0;
        
        for (let i = 0; i < children.length; i++) {
            const child = children[i];
            if (child.classList.contains('draggable-element') || 
                child.classList.contains('imported-element')) {
                count++;
            }
        }
        
        return Math.max(count, 3); // Минимум 3 элемента для демонстрации
    }

    /**
     * Применение пресета Flexbox
     */
    applyFlexboxPreset(preset) {
        if (!this.currentElement) return;

        const presets = {
            'center': {
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center'
            },
            'space-between': {
                'display': 'flex',
                'justify-content': 'space-between',
                'align-items': 'center'
            },
            'column': {
                'display': 'flex',
                'flex-direction': 'column',
                'justify-content': 'flex-start',
                'align-items': 'center'
            },
            'responsive': {
                'display': 'flex',
                'flex-wrap': 'wrap',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'gap': '20px'
            }
        };

        const selectedPreset = presets[preset];
        if (selectedPreset) {
            Object.entries(selectedPreset).forEach(([property, value]) => {
                this.currentElement.style.setProperty(property, value);
            });

            // Обновляем панель
            this.initializeFlexboxValues();

            this.vb.showNotification(`Пресет "${preset}" применен`, 'success');
        }
    }

    /**
     * Сброс Flexbox
     */
    resetFlexbox() {
        if (!this.currentElement) return;

        if (confirm('Вы уверены, что хотите сбросить все Flexbox настройки?')) {
            this.currentElement.style.removeProperty('display');
            this.currentElement.style.removeProperty('flex-direction');
            this.currentElement.style.removeProperty('flex-wrap');
            this.currentElement.style.removeProperty('justify-content');
            this.currentElement.style.removeProperty('align-items');
            this.currentElement.style.removeProperty('align-content');
            this.currentElement.style.removeProperty('gap');
            this.currentElement.style.removeProperty('row-gap');
            this.currentElement.style.removeProperty('column-gap');

            // Обновляем панель
            this.initializeFlexboxValues();

            // Удаляем overlay
            if (this.flexOverlay) {
                this.flexOverlay.remove();
                this.flexOverlay = null;
            }

            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }

            this.vb.showNotification('Flexbox настройки сброшены', 'success');
        }
    }

    /**
     * Закрытие Flexbox редактора
     */
    close() {
        this.isEditing = false;
        this.currentElement = null;

        // Удаляем overlay
        if (this.flexOverlay) {
            this.flexOverlay.remove();
            this.flexOverlay = null;
        }

        console.info('📦 Flexbox Editor закрыт');
    }

    /**
     * Экспорт Flexbox настроек
     */
    exportFlexboxSettings() {
        if (!this.currentElement) return null;

        const styles = window.getComputedStyle(this.currentElement);
        return {
            display: styles.display,
            flexDirection: styles.flexDirection,
            flexWrap: styles.flexWrap,
            justifyContent: styles.justifyContent,
            alignItems: styles.alignItems,
            alignContent: styles.alignContent,
            gap: styles.gap,
            rowGap: styles.rowGap,
            columnGap: styles.columnGap
        };
    }

    /**
     * Импорт Flexbox настроек
     */
    importFlexboxSettings(settings) {
        if (!this.currentElement || !settings) return;

        Object.entries(settings).forEach(([property, value]) => {
            this.currentElement.style.setProperty(property, value);
        });

        this.initializeFlexboxValues();
        this.updateFlexboxVisualization();
        this.updateFlexboxOverlay();
    }
}

// Экспорт класса
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlexboxEditor;
} 