/**
 * Advanced Style Editor для Visual Builder
 * Продвинутый редактор стилей с категориями и предпросмотром
 */

class AdvancedStyleEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentElement = null;
        this.styleHistory = [];
        this.init();
    }

    /**
     * Инициализация редактора
     */
    init() {
        console.info('🎨 Advanced Style Editor инициализирован');
    }

    /**
     * Открытие панели стилей
     */
    openStylePanel(element) {
        this.currentElement = element;
        const panel = this.createStylePanel();
        
        // Показываем панель справа
        const propertiesPanel = document.getElementById('propertiesPanel');
        if (propertiesPanel) {
            propertiesPanel.innerHTML = '';
            propertiesPanel.appendChild(panel);
            propertiesPanel.classList.add('active');
            propertiesPanel.style.display = 'flex';
        }
        
        console.info('🎨 Панель стилей открыта для элемента:', element.tagName);
    }

    /**
     * Создание панели стилей
     */
    createStylePanel() {
        const panel = document.createElement('div');
        panel.className = 'advanced-style-panel';
        panel.innerHTML = `
            <div class="style-panel-header">
                <h3>
                    <i class="bi bi-palette2"></i>
                    Редактор стилей
                </h3>
                <div class="style-actions">
                    <button class="btn btn-sm" onclick="visualBuilder.styleEditor.resetStyles()" title="Сбросить">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button class="btn btn-sm" onclick="visualBuilder.styleEditor.saveStylePreset()" title="Сохранить пресет">
                        <i class="bi bi-bookmark"></i>
                    </button>
                </div>
            </div>
            <div class="style-categories">
                ${this.createStyleCategory('layout', 'Макет', [
                    'display', 'position', 'top', 'left', 'right', 'bottom', 'width', 'height', 'z-index'
                ])}
                ${this.createStyleCategory('spacing', 'Отступы', [
                    'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
                    'padding-top', 'padding-right', 'padding-bottom', 'padding-left'
                ])}
                ${this.createStyleCategory('typography', 'Типографика', [
                    'font-family', 'font-size', 'font-weight', 'font-style', 'line-height', 
                    'color', 'text-align', 'text-decoration', 'text-transform', 'letter-spacing'
                ])}
                ${this.createStyleCategory('background', 'Фон', [
                    'background-color', 'background-image', 'background-size', 'background-position',
                    'background-repeat', 'background-attachment'
                ])}
                ${this.createStyleCategory('border', 'Границы', [
                    'border-width', 'border-style', 'border-color', 'border-radius',
                    'border-top', 'border-right', 'border-bottom', 'border-left'
                ])}
                ${this.createStyleCategory('effects', 'Эффекты', [
                    'box-shadow', 'opacity', 'transform', 'filter', 'transition', 'animation'
                ])}
                ${this.createStyleCategory('flexbox', 'Flexbox', [
                    'flex-direction', 'justify-content', 'align-items', 'flex-wrap',
                    'flex-grow', 'flex-shrink', 'flex-basis', 'align-self'
                ])}
                ${this.createStyleCategory('grid', 'Grid', [
                    'grid-template-columns', 'grid-template-rows', 'grid-gap',
                    'grid-column', 'grid-row', 'justify-items', 'align-items'
                ])}
            </div>
            <div class="style-presets">
                <h4>Пресеты стилей</h4>
                <div class="preset-grid">
                    ${this.createStylePresets()}
                </div>
            </div>
        `;

        // Добавляем обработчики
        this.setupStylePanelEvents(panel);

        return panel;
    }

    /**
     * Создание категории стилей
     */
    createStyleCategory(id, title, properties) {
        const currentStyles = window.getComputedStyle(this.currentElement);
        
        return `
            <div class="style-category" data-category="${id}">
                <h4 class="category-title" onclick="visualBuilder.styleEditor.toggleCategory('${id}')">
                    <i class="bi bi-chevron-down category-icon"></i>
                    ${title}
                </h4>
                <div class="category-content">
                    ${properties.map(property => `
                        <div class="style-control">
                            <label>${this.getPropertyLabel(property)}</label>
                            ${this.createPropertyInput(property, currentStyles.getPropertyValue(property))}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Создание инпута для свойства
     */
    createPropertyInput(property, currentValue) {
        const inputId = `style_${property.replace(/[^a-zA-Z0-9]/g, '_')}`;
        
        switch (property) {
            case 'color':
            case 'background-color':
            case 'border-color':
                return `
                    <div class="color-input-group">
                        <input type="color" class="style-input color-picker" 
                               id="${inputId}" data-property="${property}" 
                               value="${this.rgbToHex(currentValue)}">
                        <input type="text" class="style-input color-text" 
                               data-property="${property}" value="${currentValue}"
                               placeholder="auto">
                    </div>
                `;
            
            case 'font-family':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="Inter" ${currentValue.includes('Inter') ? 'selected' : ''}>Inter</option>
                        <option value="Arial" ${currentValue.includes('Arial') ? 'selected' : ''}>Arial</option>
                        <option value="Helvetica" ${currentValue.includes('Helvetica') ? 'selected' : ''}>Helvetica</option>
                        <option value="Georgia" ${currentValue.includes('Georgia') ? 'selected' : ''}>Georgia</option>
                        <option value="Times New Roman" ${currentValue.includes('Times') ? 'selected' : ''}>Times New Roman</option>
                        <option value="Roboto" ${currentValue.includes('Roboto') ? 'selected' : ''}>Roboto</option>
                        <option value="Open Sans" ${currentValue.includes('Open Sans') ? 'selected' : ''}>Open Sans</option>
                    </select>
                `;
            
            case 'display':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="block" ${currentValue === 'block' ? 'selected' : ''}>Block</option>
                        <option value="inline" ${currentValue === 'inline' ? 'selected' : ''}>Inline</option>
                        <option value="inline-block" ${currentValue === 'inline-block' ? 'selected' : ''}>Inline Block</option>
                        <option value="flex" ${currentValue === 'flex' ? 'selected' : ''}>Flex</option>
                        <option value="grid" ${currentValue === 'grid' ? 'selected' : ''}>Grid</option>
                        <option value="none" ${currentValue === 'none' ? 'selected' : ''}>None</option>
                    </select>
                `;
            
            case 'position':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="static" ${currentValue === 'static' ? 'selected' : ''}>Static</option>
                        <option value="relative" ${currentValue === 'relative' ? 'selected' : ''}>Relative</option>
                        <option value="absolute" ${currentValue === 'absolute' ? 'selected' : ''}>Absolute</option>
                        <option value="fixed" ${currentValue === 'fixed' ? 'selected' : ''}>Fixed</option>
                        <option value="sticky" ${currentValue === 'sticky' ? 'selected' : ''}>Sticky</option>
                    </select>
                `;
            
            case 'text-align':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="left" ${currentValue === 'left' ? 'selected' : ''}>Left</option>
                        <option value="center" ${currentValue === 'center' ? 'selected' : ''}>Center</option>
                        <option value="right" ${currentValue === 'right' ? 'selected' : ''}>Right</option>
                        <option value="justify" ${currentValue === 'justify' ? 'selected' : ''}>Justify</option>
                    </select>
                `;
            
            case 'font-weight':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="normal" ${currentValue === 'normal' ? 'selected' : ''}>Normal</option>
                        <option value="bold" ${currentValue === 'bold' ? 'selected' : ''}>Bold</option>
                        <option value="100" ${currentValue === '100' ? 'selected' : ''}>100</option>
                        <option value="200" ${currentValue === '200' ? 'selected' : ''}>200</option>
                        <option value="300" ${currentValue === '300' ? 'selected' : ''}>300</option>
                        <option value="400" ${currentValue === '400' ? 'selected' : ''}>400</option>
                        <option value="500" ${currentValue === '500' ? 'selected' : ''}>500</option>
                        <option value="600" ${currentValue === '600' ? 'selected' : ''}>600</option>
                        <option value="700" ${currentValue === '700' ? 'selected' : ''}>700</option>
                        <option value="800" ${currentValue === '800' ? 'selected' : ''}>800</option>
                        <option value="900" ${currentValue === '900' ? 'selected' : ''}>900</option>
                    </select>
                `;
            
            case 'border-style':
                return `
                    <select class="style-input" id="${inputId}" data-property="${property}">
                        <option value="none" ${currentValue === 'none' ? 'selected' : ''}>None</option>
                        <option value="solid" ${currentValue === 'solid' ? 'selected' : ''}>Solid</option>
                        <option value="dashed" ${currentValue === 'dashed' ? 'selected' : ''}>Dashed</option>
                        <option value="dotted" ${currentValue === 'dotted' ? 'selected' : ''}>Dotted</option>
                        <option value="double" ${currentValue === 'double' ? 'selected' : ''}>Double</option>
                        <option value="groove" ${currentValue === 'groove' ? 'selected' : ''}>Groove</option>
                        <option value="ridge" ${currentValue === 'ridge' ? 'selected' : ''}>Ridge</option>
                        <option value="inset" ${currentValue === 'inset' ? 'selected' : ''}>Inset</option>
                        <option value="outset" ${currentValue === 'outset' ? 'selected' : ''}>Outset</option>
                    </select>
                `;
            
            default:
                return `
                    <input type="text" class="style-input" 
                           id="${inputId}" data-property="${property}" 
                           value="${currentValue}" placeholder="auto">
                `;
        }
    }

    /**
     * Настройка событий панели стилей
     */
    setupStylePanelEvents(panel) {
        // Обработчики для всех инпутов
        panel.querySelectorAll('.style-input').forEach(input => {
            input.addEventListener('input', (e) => {
                this.updateElementStyle(e.target.dataset.property, e.target.value);
            });
            
            input.addEventListener('change', (e) => {
                this.saveToHistory(e.target.dataset.property, e.target.value);
            });
        });

        // Обработчики для цветовых пикеров
        panel.querySelectorAll('.color-picker').forEach(picker => {
            picker.addEventListener('change', (e) => {
                const textInput = panel.querySelector(`[data-property="${e.target.dataset.property}"].color-text`);
                if (textInput) {
                    textInput.value = e.target.value;
                }
            });
        });

        // Обработчики для текстовых полей цвета
        panel.querySelectorAll('.color-text').forEach(textInput => {
            textInput.addEventListener('input', (e) => {
                const picker = panel.querySelector(`[data-property="${e.target.dataset.property}"].color-picker`);
                if (picker && this.isValidColor(e.target.value)) {
                    picker.value = this.rgbToHex(e.target.value);
                }
            });
        });
    }

    /**
     * Обновление стиля элемента
     */
    updateElementStyle(property, value) {
        if (this.currentElement && property && value !== undefined) {
            this.currentElement.style.setProperty(property, value);
            
            // Обновляем предпросмотр если есть
            this.updateStylePreview();
            
            // Помечаем как измененный
            if (this.vb.markAsChanged) {
                this.vb.markAsChanged();
            }
        }
    }

    /**
     * Сохранение в историю стилей
     */
    saveToHistory(property, value) {
        this.styleHistory.push({
            property,
            value,
            timestamp: Date.now()
        });
        
        // Ограничиваем историю
        if (this.styleHistory.length > 50) {
            this.styleHistory.shift();
        }
    }

    /**
     * Переключение категории
     */
    toggleCategory(categoryId) {
        const category = document.querySelector(`[data-category="${categoryId}"]`);
        if (category) {
            const content = category.querySelector('.category-content');
            const icon = category.querySelector('.category-icon');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.classList.remove('bi-chevron-right');
                icon.classList.add('bi-chevron-down');
            } else {
                content.style.display = 'none';
                icon.classList.remove('bi-chevron-down');
                icon.classList.add('bi-chevron-right');
            }
        }
    }

    /**
     * Создание пресетов стилей
     */
    createStylePresets() {
        const presets = [
            {
                name: 'Карточка',
                styles: {
                    'background-color': '#ffffff',
                    'border': '1px solid #e5e7eb',
                    'border-radius': '8px',
                    'padding': '16px',
                    'box-shadow': '0 1px 3px rgba(0, 0, 0, 0.1)'
                }
            },
            {
                name: 'Кнопка',
                styles: {
                    'background-color': '#3b82f6',
                    'color': '#ffffff',
                    'border': 'none',
                    'border-radius': '6px',
                    'padding': '8px 16px',
                    'font-weight': '500',
                    'cursor': 'pointer'
                }
            },
            {
                name: 'Заголовок',
                styles: {
                    'font-size': '24px',
                    'font-weight': '600',
                    'color': '#1f2937',
                    'margin-bottom': '16px'
                }
            },
            {
                name: 'Текст',
                styles: {
                    'font-size': '16px',
                    'line-height': '1.6',
                    'color': '#374151'
                }
            },
            {
                name: 'Контейнер',
                styles: {
                    'max-width': '1200px',
                    'margin': '0 auto',
                    'padding': '0 16px'
                }
            },
            {
                name: 'Flex центр',
                styles: {
                    'display': 'flex',
                    'justify-content': 'center',
                    'align-items': 'center'
                }
            }
        ];
        
        return presets.map(preset => `
            <div class="style-preset" onclick="visualBuilder.styleEditor.applyPreset(${JSON.stringify(preset.styles).replace(/"/g, '&quot;')})">
                <div class="preset-preview" style="${Object.entries(preset.styles).map(([k, v]) => `${k}: ${v}`).join(';')}">
                    ${preset.name}
                </div>
                <div class="preset-name">${preset.name}</div>
            </div>
        `).join('');
    }

    /**
     * Применение пресета
     */
    applyPreset(styles) {
        if (!this.currentElement) return;
        
        Object.entries(styles).forEach(([property, value]) => {
            this.updateElementStyle(property, value);
        });
        
        this.vb.showNotification('Пресет применен', 'success');
    }

    /**
     * Сброс стилей
     */
    resetStyles() {
        if (!this.currentElement) return;
        
        if (confirm('Вы уверены, что хотите сбросить все стили элемента?')) {
            this.currentElement.removeAttribute('style');
            this.vb.showNotification('Стили сброшены', 'info');
            
            // Обновляем панель
            this.openStylePanel(this.currentElement);
        }
    }

    /**
     * Сохранение пресета стилей
     */
    saveStylePreset() {
        if (!this.currentElement) return;
        
        const name = prompt('Введите название пресета:');
        if (!name) return;
        
        const styles = {};
        const computedStyles = window.getComputedStyle(this.currentElement);
        
        // Собираем все примененные стили
        for (let i = 0; i < computedStyles.length; i++) {
            const property = computedStyles[i];
            const value = computedStyles.getPropertyValue(property);
            if (value && value !== 'initial' && value !== 'normal') {
                styles[property] = value;
            }
        }
        
        // Сохраняем в localStorage
        const presets = JSON.parse(localStorage.getItem('vb-style-presets') || '[]');
        presets.push({ name, styles });
        localStorage.setItem('vb-style-presets', JSON.stringify(presets));
        
        this.vb.showNotification('Пресет сохранен', 'success');
    }

    /**
     * Обновление предпросмотра стилей
     */
    updateStylePreview() {
        // Здесь можно добавить live preview изменений
        // Например, показывать мини-предпросмотр элемента
    }

    /**
     * Утилиты
     */
    getPropertyLabel(property) {
        const labels = {
            'margin-top': 'Верх',
            'margin-right': 'Право', 
            'margin-bottom': 'Низ',
            'margin-left': 'Лево',
            'padding-top': 'Верх',
            'padding-right': 'Право',
            'padding-bottom': 'Низ',
            'padding-left': 'Лево',
            'font-family': 'Шрифт',
            'font-size': 'Размер',
            'font-weight': 'Жирность',
            'font-style': 'Стиль',
            'line-height': 'Высота строки',
            'background-color': 'Цвет фона',
            'background-image': 'Фон изображение',
            'background-size': 'Размер фона',
            'background-position': 'Позиция фона',
            'border-width': 'Ширина границы',
            'border-style': 'Стиль границы',
            'border-color': 'Цвет границы',
            'border-radius': 'Скругление',
            'box-shadow': 'Тень',
            'opacity': 'Прозрачность',
            'transform': 'Трансформация',
            'transition': 'Переход',
            'z-index': 'Z-индекс',
            'display': 'Отображение',
            'position': 'Позиционирование',
            'justify-content': 'Выравнивание по главной оси',
            'align-items': 'Выравнивание по поперечной оси',
            'flex-direction': 'Направление flex',
            'flex-wrap': 'Перенос flex',
            'grid-template-columns': 'Колонки grid',
            'grid-template-rows': 'Строки grid',
            'grid-gap': 'Отступы grid'
        };
        return labels[property] || property;
    }

    rgbToHex(rgb) {
        if (rgb.startsWith('#')) return rgb;
        if (rgb === 'rgba(0, 0, 0, 0)' || rgb === 'transparent') return '#000000';
        
        const rgbMatch = rgb.match(/\d+/g);
        if (!rgbMatch) return '#000000';
        
        return '#' + rgbMatch.slice(0, 3)
            .map(x => parseInt(x).toString(16).padStart(2, '0'))
            .join('');
    }

    isValidColor(color) {
        const s = new Option().style;
        s.color = color;
        return s.color !== '';
    }

    /**
     * Получение всех стилей элемента
     */
    getAllStyles(element) {
        const styles = {};
        const computedStyles = window.getComputedStyle(element);
        
        for (let i = 0; i < computedStyles.length; i++) {
            const property = computedStyles[i];
            const value = computedStyles.getPropertyValue(property);
            if (value && value !== 'initial' && value !== 'normal') {
                styles[property] = value;
            }
        }
        
        return styles;
    }

    /**
     * Экспорт стилей в CSS
     */
    exportStyles(element) {
        const styles = this.getAllStyles(element);
        let css = '';
        
        Object.entries(styles).forEach(([property, value]) => {
            css += `    ${property}: ${value};\n`;
        });
        
        return css;
    }
}

// Экспорт класса
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedStyleEditor;
} 