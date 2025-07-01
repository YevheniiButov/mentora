/**
 * CSS Variables Manager for GrapesJS
 * Система управления CSS переменными для GrapesJS
 * 
 * Manages CSS custom properties (variables) in the GrapesJS editor
 * Управляет CSS пользовательскими свойствами (переменными) в редакторе GrapesJS
 */

class CSSVariablesManager {
    constructor(editor) {
        this.editor = editor;
        this.variables = new Map();
        this.categories = new Map();
        this.defaults = new Map();
        this.panel = null;
        this.isInitialized = false;
        
        // Variable categories with bilingual labels
        // Категории переменных с двуязычными лейблами
        this.categoryDefinitions = {
            colors: {
                label: { en: 'Colors', ru: 'Цвета' },
                description: { en: 'Color variables for themes and components', ru: 'Цветовые переменные для тем и компонентов' },
                icon: '🎨'
            },
            spacing: {
                label: { en: 'Spacing', ru: 'Отступы' },
                description: { en: 'Margin, padding and layout spacing', ru: 'Отступы, поля и расстояние макета' },
                icon: '📏'
            },
            typography: {
                label: { en: 'Typography', ru: 'Типографика' },
                description: { en: 'Font sizes, weights and text styles', ru: 'Размеры шрифтов, веса и стили текста' },
                icon: '📝'
            },
            effects: {
                label: { en: 'Effects', ru: 'Эффекты' },
                description: { en: 'Shadows, borders and visual effects', ru: 'Тени, границы и визуальные эффекты' },
                icon: '✨'
            },
            layout: {
                label: { en: 'Layout', ru: 'Макет' },
                description: { en: 'Container sizes and layout dimensions', ru: 'Размеры контейнеров и размеры макета' },
                icon: '📐'
            },
            transitions: {
                label: { en: 'Transitions', ru: 'Переходы' },
                description: { en: 'Animation durations and timing functions', ru: 'Длительности анимаций и функции времени' },
                icon: '⏱️'
            }
        };
        
        this.init();
    }

    /**
     * Initialize the CSS Variables Manager
     * Инициализация менеджера CSS переменных
     */
    init() {
        if (this.isInitialized) return;
        
        this.loadProjectVariables();
        this.createVariableControls();
        this.setupEventListeners();
        
        this.isInitialized = true;
        console.log('🎨 CSS Variables Manager initialized');
    }

    /**
     * Load CSS variables from project stylesheets
     * Загрузка CSS переменных из таблиц стилей проекта
     */
    loadProjectVariables() {
        const styleSheets = Array.from(document.styleSheets);
        const cssRules = [];
        
        // Collect all CSS rules from stylesheets
        // Собираем все CSS правила из таблиц стилей
        styleSheets.forEach(sheet => {
            try {
                const rules = Array.from(sheet.cssRules || sheet.rules || []);
                cssRules.push(...rules);
            } catch (e) {
                // Skip external stylesheets that might be blocked by CORS
                // Пропускаем внешние таблицы стилей, которые могут быть заблокированы CORS
            }
        });

        // Extract CSS variables from rules
        // Извлекаем CSS переменные из правил
        cssRules.forEach(rule => {
            if (rule.style) {
                const cssText = rule.style.cssText;
                const variableMatches = cssText.match(/--[a-zA-Z0-9-]+:\s*([^;]+)/g);
                
                if (variableMatches) {
                    variableMatches.forEach(match => {
                        const [name, value] = match.split(':').map(s => s.trim());
                        const cleanValue = value.replace(/;$/, '');
                        
                        if (!this.variables.has(name)) {
                            this.variables.set(name, cleanValue);
                            this.defaults.set(name, cleanValue);
                            this.categorizeVariable(name, cleanValue);
                        }
                    });
                }
            }
        });

        // Also scan for variables in :root selector
        // Также сканируем переменные в селекторе :root
        const rootStyles = getComputedStyle(document.documentElement);
        for (let i = 0; i < rootStyles.length; i++) {
            const property = rootStyles[i];
            if (property.startsWith('--')) {
                const value = rootStyles.getPropertyValue(property);
                if (!this.variables.has(property)) {
                    this.variables.set(property, value);
                    this.defaults.set(property, value);
                    this.categorizeVariable(property, value);
                }
            }
        }

        console.log(`📊 Loaded ${this.variables.size} CSS variables`);
    }

    /**
     * Categorize a CSS variable based on its name and value
     * Категоризация CSS переменной на основе её имени и значения
     */
    categorizeVariable(name, value) {
        const lowerName = name.toLowerCase();
        const lowerValue = value.toLowerCase();
        
        let category = 'other';
        
        // Color variables
        // Цветовые переменные
        if (lowerName.includes('color') || 
            lowerName.includes('bg') || 
            lowerName.includes('background') ||
            lowerName.includes('theme') ||
            lowerValue.includes('#') ||
            lowerValue.includes('rgb') ||
            lowerValue.includes('hsl') ||
            lowerValue.includes('linear-gradient') ||
            lowerValue.includes('radial-gradient')) {
            category = 'colors';
        }
        // Spacing variables
        // Переменные отступов
        else if (lowerName.includes('padding') || 
                 lowerName.includes('margin') || 
                 lowerName.includes('gap') ||
                 lowerName.includes('spacing')) {
            category = 'spacing';
        }
        // Typography variables
        // Типографические переменные
        else if (lowerName.includes('font') || 
                 lowerName.includes('text') || 
                 lowerName.includes('line-height')) {
            category = 'typography';
        }
        // Effect variables
        // Переменные эффектов
        else if (lowerName.includes('shadow') || 
                 lowerName.includes('border') || 
                 lowerName.includes('radius') ||
                 lowerName.includes('blur') ||
                 lowerName.includes('opacity')) {
            category = 'effects';
        }
        // Layout variables
        // Переменные макета
        else if (lowerName.includes('width') || 
                 lowerName.includes('height') || 
                 lowerName.includes('size') ||
                 lowerName.includes('container')) {
            category = 'layout';
        }
        // Transition variables
        // Переменные переходов
        else if (lowerName.includes('transition') || 
                 lowerName.includes('duration') || 
                 lowerName.includes('timing') ||
                 lowerName.includes('ease')) {
            category = 'transitions';
        }

        if (!this.categories.has(category)) {
            this.categories.set(category, []);
        }
        this.categories.get(category).push(name);
    }

    /**
     * Create variable controls in GrapesJS
     * Создание элементов управления переменными в GrapesJS
     */
    createVariableControls() {
        const panelManager = this.editor.Panels;
        
        // Create CSS Variables panel
        // Создаем панель CSS переменных
        this.panel = panelManager.addPanel({
            id: 'css-variables-panel',
            visible: true,
            resizable: {
                tc: true,
                cr: true,
                cl: true,
                bc: true,
            }
        });

        // Add panel header
        // Добавляем заголовок панели
        this.panel.set('appendContent', `
            <div class="css-variables-header">
                <h3 class="panel-title">
                    <span class="panel-icon">🎨</span>
                    <span class="panel-label" data-i18n="css-variables">CSS Variables</span>
                </h3>
                <div class="panel-actions">
                    <button class="btn-reset" title="Reset to defaults">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button class="btn-export" title="Export variables">
                        <i class="bi bi-download"></i>
                    </button>
                    <button class="btn-import" title="Import variables">
                        <i class="bi bi-upload"></i>
                    </button>
                </div>
            </div>
        `);

        // Create variable controls for each category
        // Создаем элементы управления переменными для каждой категории
        this.categories.forEach((variables, category) => {
            this.createCategorySection(category, variables);
        });

        // Add import input (hidden)
        // Добавляем скрытое поле импорта
        const importInput = document.createElement('input');
        importInput.type = 'file';
        importInput.accept = '.json';
        importInput.style.display = 'none';
        importInput.id = 'css-variables-import';
        document.body.appendChild(importInput);
    }

    /**
     * Create a category section with variable controls
     * Создание секции категории с элементами управления переменными
     */
    createCategorySection(category, variables) {
        const categoryDef = this.categoryDefinitions[category] || {
            label: { en: category, ru: category },
            description: { en: '', ru: '' },
            icon: '📁'
        };

        const section = document.createElement('div');
        section.className = 'css-variables-category';
        section.innerHTML = `
            <div class="category-header" data-category="${category}">
                <div class="category-info">
                    <span class="category-icon">${categoryDef.icon}</span>
                    <div class="category-details">
                        <h4 class="category-title">${this.getLocalizedText(categoryDef.label)}</h4>
                        <p class="category-description">${this.getLocalizedText(categoryDef.description)}</p>
                    </div>
                </div>
                <button class="category-toggle" data-category="${category}">
                    <i class="bi bi-chevron-down"></i>
                </button>
            </div>
            <div class="category-content" data-category="${category}">
                ${variables.map(varName => this.createVariableControl(varName)).join('')}
            </div>
        `;

        this.panel.get('content').appendChild(section);
    }

    /**
     * Create a control for a single CSS variable
     * Создание элемента управления для одной CSS переменной
     */
    createVariableControl(varName) {
        const value = this.variables.get(varName);
        const isColor = this.isColorValue(value);
        const controlType = this.getControlType(varName, value);
        
        return `
            <div class="variable-control" data-variable="${varName}">
                <div class="variable-info">
                    <label class="variable-name">${varName}</label>
                    <div class="variable-preview">
                        ${isColor ? `<div class="color-preview" style="background: ${value}"></div>` : ''}
                        <span class="variable-value">${value}</span>
                    </div>
                </div>
                <div class="variable-input">
                    ${this.createInputElement(varName, value, controlType)}
                </div>
            </div>
        `;
    }

    /**
     * Create input element based on variable type
     * Создание элемента ввода на основе типа переменной
     */
    createInputElement(varName, value, controlType) {
        switch (controlType) {
            case 'color':
                return `<input type="color" value="${this.colorToHex(value)}" data-variable="${varName}">`;
            case 'range':
                const numericValue = this.extractNumericValue(value);
                return `
                    <input type="range" 
                           min="0" 
                           max="${this.getRangeMax(varName)}" 
                           value="${numericValue}" 
                           data-variable="${varName}">
                    <input type="number" 
                           value="${numericValue}" 
                           data-variable="${varName}">
                `;
            case 'select':
                return this.createSelectElement(varName, value);
            default:
                return `<input type="text" value="${value}" data-variable="${varName}">`;
        }
    }

    /**
     * Determine control type for a variable
     * Определение типа элемента управления для переменной
     */
    getControlType(varName, value) {
        const lowerName = varName.toLowerCase();
        const lowerValue = value.toLowerCase();
        
        if (this.isColorValue(value)) return 'color';
        if (lowerName.includes('font-weight')) return 'select';
        if (lowerName.includes('transition-timing')) return 'select';
        if (this.isNumericValue(value)) return 'range';
        
        return 'text';
    }

    /**
     * Check if value is a color
     * Проверка, является ли значение цветом
     */
    isColorValue(value) {
        const colorPatterns = [
            /^#[0-9A-Fa-f]{3,6}$/,
            /^rgb\(/,
            /^rgba\(/,
            /^hsl\(/,
            /^hsla\(/,
            /^linear-gradient\(/,
            /^radial-gradient\(/
        ];
        
        return colorPatterns.some(pattern => pattern.test(value));
    }

    /**
     * Check if value is numeric
     * Проверка, является ли значение числовым
     */
    isNumericValue(value) {
        return /^\d+(\.\d+)?(px|em|rem|%|vh|vw)?$/.test(value);
    }

    /**
     * Extract numeric value from CSS value
     * Извлечение числового значения из CSS значения
     */
    extractNumericValue(value) {
        const match = value.match(/^(\d+(\.\d+)?)/);
        return match ? parseFloat(match[1]) : 0;
    }

    /**
     * Get maximum value for range input
     * Получение максимального значения для range input
     */
    getRangeMax(varName) {
        const lowerName = varName.toLowerCase();
        
        if (lowerName.includes('font-size')) return 100;
        if (lowerName.includes('line-height')) return 3;
        if (lowerName.includes('opacity')) return 1;
        if (lowerName.includes('border-radius')) return 50;
        if (lowerName.includes('shadow')) return 50;
        
        return 100;
    }

    /**
     * Convert color value to hex
     * Преобразование цветового значения в hex
     */
    colorToHex(color) {
        if (color.startsWith('#')) return color;
        
        // Create temporary element to convert color
        // Создаем временный элемент для преобразования цвета
        const temp = document.createElement('div');
        temp.style.color = color;
        document.body.appendChild(temp);
        
        const computed = getComputedStyle(temp).color;
        document.body.removeChild(temp);
        
        // Convert rgb to hex
        // Преобразуем rgb в hex
        const rgb = computed.match(/\d+/g);
        if (rgb && rgb.length >= 3) {
            const r = parseInt(rgb[0]).toString(16).padStart(2, '0');
            const g = parseInt(rgb[1]).toString(16).padStart(2, '0');
            const b = parseInt(rgb[2]).toString(16).padStart(2, '0');
            return `#${r}${g}${b}`;
        }
        
        return '#000000';
    }

    /**
     * Create select element for predefined values
     * Создание select элемента для предопределенных значений
     */
    createSelectElement(varName, value) {
        const lowerName = varName.toLowerCase();
        
        if (lowerName.includes('font-weight')) {
            const weights = ['100', '200', '300', '400', '500', '600', '700', '800', '900'];
            return `
                <select data-variable="${varName}">
                    ${weights.map(weight => 
                        `<option value="${weight}" ${weight === value ? 'selected' : ''}>${weight}</option>`
                    ).join('')}
                </select>
            `;
        }
        
        if (lowerName.includes('transition-timing')) {
            const timings = ['ease', 'linear', 'ease-in', 'ease-out', 'ease-in-out', 'cubic-bezier(0.4, 0, 0.2, 1)'];
            return `
                <select data-variable="${varName}">
                    ${timings.map(timing => 
                        `<option value="${timing}" ${timing === value ? 'selected' : ''}>${timing}</option>`
                    ).join('')}
                </select>
            `;
        }
        
        return `<input type="text" value="${value}" data-variable="${varName}">`;
    }

    /**
     * Set up event listeners for variable controls
     * Настройка обработчиков событий для элементов управления переменными
     */
    setupEventListeners() {
        const panel = this.panel.get('content');
        
        // Variable input changes
        // Изменения ввода переменных
        panel.addEventListener('input', (e) => {
            if (e.target.hasAttribute('data-variable')) {
                const varName = e.target.getAttribute('data-variable');
                let value = e.target.value;
                
                // Add units for range inputs
                // Добавляем единицы для range inputs
                if (e.target.type === 'range' || e.target.type === 'number') {
                    const originalValue = this.variables.get(varName);
                    const unit = this.extractUnit(originalValue);
                    value = value + unit;
                }
                
                this.updateVariable(varName, value);
            }
        });

        // Category toggle
        // Переключение категорий
        panel.addEventListener('click', (e) => {
            if (e.target.closest('.category-toggle')) {
                const category = e.target.closest('.category-toggle').getAttribute('data-category');
                this.toggleCategory(category);
            }
        });

        // Panel actions
        // Действия панели
        panel.addEventListener('click', (e) => {
            if (e.target.closest('.btn-reset')) {
                this.resetToDefaults();
            } else if (e.target.closest('.btn-export')) {
                this.exportVariables();
            } else if (e.target.closest('.btn-import')) {
                document.getElementById('css-variables-import').click();
            }
        });

        // Import file handling
        // Обработка импорта файла
        document.getElementById('css-variables-import').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                this.importVariables(file);
            }
        });
    }

    /**
     * Extract unit from CSS value
     * Извлечение единицы из CSS значения
     */
    extractUnit(value) {
        const match = value.match(/[a-z%]+$/);
        return match ? match[0] : '';
    }

    /**
     * Toggle category visibility
     * Переключение видимости категории
     */
    toggleCategory(category) {
        const content = this.panel.get('content').querySelector(`[data-category="${category}"]`);
        const toggle = content.previousElementSibling.querySelector('.category-toggle i');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            toggle.className = 'bi bi-chevron-down';
        } else {
            content.style.display = 'none';
            toggle.className = 'bi bi-chevron-right';
        }
    }

    /**
     * Update CSS variable in real-time
     * Обновление CSS переменной в реальном времени
     */
    updateVariable(name, value) {
        this.variables.set(name, value);
        
        // Update CSS custom property
        // Обновляем CSS пользовательское свойство
        document.documentElement.style.setProperty(name, value);
        
        // Update preview in editor
        // Обновляем предварительный просмотр в редакторе
        this.editor.refresh();
        
        // Update variable display
        // Обновляем отображение переменной
        const preview = this.panel.get('content').querySelector(`[data-variable="${name}"] .variable-value`);
        if (preview) {
            preview.textContent = value;
        }
        
        // Update color preview
        // Обновляем предварительный просмотр цвета
        if (this.isColorValue(value)) {
            const colorPreview = this.panel.get('content').querySelector(`[data-variable="${name}"] .color-preview`);
            if (colorPreview) {
                colorPreview.style.background = value;
            }
        }
        
        // Trigger change event for undo/redo
        // Запускаем событие изменения для undo/redo
        this.editor.trigger('css-variable:change', { name, value });
    }

    /**
     * Export current variable values
     * Экспорт текущих значений переменных
     */
    exportVariables() {
        const data = {
            variables: Object.fromEntries(this.variables),
            categories: Object.fromEntries(this.categories),
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `css-variables-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    /**
     * Import variables from file
     * Импорт переменных из файла
     */
    importVariables(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (data.variables) {
                    Object.entries(data.variables).forEach(([name, value]) => {
                        this.updateVariable(name, value);
                        
                        // Update input value
                        // Обновляем значение ввода
                        const input = this.panel.get('content').querySelector(`[data-variable="${name}"] input, [data-variable="${name}"] select`);
                        if (input) {
                            if (input.type === 'color') {
                                input.value = this.colorToHex(value);
                            } else if (input.type === 'range' || input.type === 'number') {
                                input.value = this.extractNumericValue(value);
                            } else {
                                input.value = value;
                            }
                        }
                    });
                    
                    console.log('✅ CSS variables imported successfully');
                }
            } catch (error) {
                console.error('❌ Error importing CSS variables:', error);
            }
        };
        reader.readAsText(file);
    }

    /**
     * Reset variables to default values
     * Сброс переменных к значениям по умолчанию
     */
    resetToDefaults() {
        if (confirm(this.getLocalizedText({
            en: 'Are you sure you want to reset all variables to their default values?',
            ru: 'Вы уверены, что хотите сбросить все переменные к значениям по умолчанию?'
        }))) {
            this.defaults.forEach((value, name) => {
                this.updateVariable(name, value);
                
                // Update input value
                // Обновляем значение ввода
                const input = this.panel.get('content').querySelector(`[data-variable="${name}"] input, [data-variable="${name}"] select`);
                if (input) {
                    if (input.type === 'color') {
                        input.value = this.colorToHex(value);
                    } else if (input.type === 'range' || input.type === 'number') {
                        input.value = this.extractNumericValue(value);
                    } else {
                        input.value = value;
                    }
                }
            });
            
            console.log('🔄 CSS variables reset to defaults');
        }
    }

    /**
     * Get localized text
     * Получение локализованного текста
     */
    getLocalizedText(textObj, fallback = '') {
        const lang = document.documentElement.lang || 
                   document.querySelector('meta[name="language"]')?.content ||
                   'en';
        return textObj[lang] || textObj.en || fallback;
    }

    /**
     * Get all variables
     * Получение всех переменных
     */
    getVariables() {
        return Object.fromEntries(this.variables);
    }

    /**
     * Get variables by category
     * Получение переменных по категории
     */
    getVariablesByCategory(category) {
        return this.categories.get(category) || [];
    }

    /**
     * Destroy the manager
     * Уничтожение менеджера
     */
    destroy() {
        if (this.panel) {
            this.editor.Panels.remove(this.panel);
        }
        
        const importInput = document.getElementById('css-variables-import');
        if (importInput) {
            document.body.removeChild(importInput);
        }
        
        this.isInitialized = false;
    }
}

// Add CSS styles for the variables panel
// Добавляем CSS стили для панели переменных
const cssVariablesStyles = `
    .css-variables-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        border-bottom: 1px solid var(--border-color, #e2e8f0);
        background: var(--bg-primary, #ffffff);
    }
    
    .panel-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #1e293b);
    }
    
    .panel-icon {
        font-size: 1.25rem;
    }
    
    .panel-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .panel-actions button {
        background: none;
        border: 1px solid var(--border-color, #e2e8f0);
        border-radius: var(--radius-md, 6px);
        padding: 0.375rem;
        cursor: pointer;
        transition: all var(--transition-normal, 0.2s ease);
        color: var(--text-secondary, #64748b);
    }
    
    .panel-actions button:hover {
        background: var(--bg-secondary, #f8fafc);
        color: var(--text-primary, #1e293b);
    }
    
    .css-variables-category {
        border-bottom: 1px solid var(--border-color, #e2e8f0);
    }
    
    .category-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        cursor: pointer;
        background: var(--bg-secondary, #f8fafc);
        transition: background var(--transition-normal, 0.2s ease);
    }
    
    .category-header:hover {
        background: var(--bg-hover, #f1f5f9);
    }
    
    .category-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .category-icon {
        font-size: 1.5rem;
    }
    
    .category-title {
        margin: 0;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary, #1e293b);
    }
    
    .category-description {
        margin: 0;
        font-size: 0.75rem;
        color: var(--text-secondary, #64748b);
    }
    
    .category-toggle {
        background: none;
        border: none;
        cursor: pointer;
        color: var(--text-secondary, #64748b);
        transition: color var(--transition-normal, 0.2s ease);
    }
    
    .category-toggle:hover {
        color: var(--text-primary, #1e293b);
    }
    
    .category-content {
        padding: 1rem;
        background: var(--bg-primary, #ffffff);
    }
    
    .variable-control {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        padding: 0.75rem;
        border: 1px solid var(--border-color, #e2e8f0);
        border-radius: var(--radius-md, 6px);
        margin-bottom: 0.5rem;
        background: var(--bg-primary, #ffffff);
    }
    
    .variable-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .variable-name {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-primary, #1e293b);
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    }
    
    .variable-preview {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .color-preview {
        width: 16px;
        height: 16px;
        border-radius: var(--radius-sm, 4px);
        border: 1px solid var(--border-color, #e2e8f0);
    }
    
    .variable-value {
        font-size: 0.75rem;
        color: var(--text-secondary, #64748b);
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    }
    
    .variable-input {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .variable-input input,
    .variable-input select {
        flex: 1;
        padding: 0.375rem 0.5rem;
        border: 1px solid var(--border-color, #e2e8f0);
        border-radius: var(--radius-sm, 4px);
        font-size: 0.75rem;
        background: var(--bg-primary, #ffffff);
        color: var(--text-primary, #1e293b);
    }
    
    .variable-input input:focus,
    .variable-input select:focus {
        outline: none;
        border-color: var(--primary-color, #3ECDC1);
        box-shadow: 0 0 0 2px rgba(62, 205, 193, 0.1);
    }
    
    .variable-input input[type="color"] {
        width: 40px;
        height: 32px;
        padding: 0;
        border: none;
        border-radius: var(--radius-sm, 4px);
        cursor: pointer;
    }
    
    .variable-input input[type="range"] {
        flex: 1;
        height: 4px;
        background: var(--bg-secondary, #f1f5f9);
        border-radius: var(--radius-full, 9999px);
        outline: none;
        cursor: pointer;
    }
    
    .variable-input input[type="range"]::-webkit-slider-thumb {
        appearance: none;
        width: 16px;
        height: 16px;
        background: var(--primary-color, #3ECDC1);
        border-radius: 50%;
        cursor: pointer;
    }
    
    .variable-input input[type="number"] {
        width: 60px;
        text-align: center;
    }
`;

// Inject styles into document
// Внедряем стили в документ
const styleSheet = document.createElement('style');
styleSheet.textContent = cssVariablesStyles;
document.head.appendChild(styleSheet);

// Export for use in other scripts
// Экспорт для использования в других скриптах
window.CSSVariablesManager = CSSVariablesManager;

// Auto-initialize when GrapesJS is ready
// Автоматическая инициализация когда GrapesJS готов
if (typeof grapesjs !== 'undefined') {
    if (grapesjs.editors) {
        // GrapesJS is already loaded
        // GrapesJS уже загружен
        grapesjs.editors.forEach(editor => {
            editor.CSSVariablesManager = new CSSVariablesManager(editor);
        });
    } else {
        // Wait for GrapesJS to load
        // Ждем загрузки GrapesJS
        document.addEventListener('grapesjs:ready', () => {
            grapesjs.editors.forEach(editor => {
                editor.CSSVariablesManager = new CSSVariablesManager(editor);
            });
        });
    }
} 