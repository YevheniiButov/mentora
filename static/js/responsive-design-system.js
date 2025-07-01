/**
 * Responsive Design System for GrapesJS
 * Система управления адаптивным дизайном для GrapesJS
 * 
 * Features:
 * - Breakpoint management with visual editor
 * - Device preview with frames
 * - Responsive style editor
 * - Layout tools for responsive design
 * - Bilingual interface (EN/RU)
 */

class ResponsiveDesignSystem {
    constructor(editor) {
        this.editor = editor;
        this.currentBreakpoint = 'desktop';
        this.breakpoints = {
            mobile: { width: 375, height: 667, name: 'Mobile', maxWidth: 768 },
            tablet: { width: 768, height: 1024, name: 'Tablet', minWidth: 769, maxWidth: 1024 },
            desktop: { width: 1200, height: 800, name: 'Desktop', minWidth: 1025 }
        };
        this.customBreakpoints = [];
        this.deviceFrames = {
            iphone: { width: 375, height: 812, frame: 'iphone-frame' },
            ipad: { width: 768, height: 1024, frame: 'ipad-frame' },
            desktop: { width: 1200, height: 800, frame: 'desktop-frame' }
        };
        this.currentDevice = 'desktop';
        this.orientation = 'portrait';
        
        this.translations = {
            en: {
                responsive: 'Responsive Design',
                breakpoints: 'Breakpoints',
                devices: 'Devices',
                preview: 'Preview',
                mobile: 'Mobile',
                tablet: 'Tablet',
                desktop: 'Desktop',
                portrait: 'Portrait',
                landscape: 'Landscape',
                addBreakpoint: 'Add Breakpoint',
                customBreakpoint: 'Custom Breakpoint',
                responsiveStyles: 'Responsive Styles',
                hideOnMobile: 'Hide on Mobile',
                showOnMobile: 'Show on Mobile',
                responsiveGrid: 'Responsive Grid',
                flexDirection: 'Flex Direction',
                elementOrder: 'Element Order',
                responsiveImages: 'Responsive Images',
                generateCSS: 'Generate CSS',
                exportResponsive: 'Export Responsive CSS',
                breakpointEditor: 'Breakpoint Editor',
                devicePreview: 'Device Preview',
                layoutTools: 'Layout Tools',
                styleEditor: 'Style Editor',
                width: 'Width',
                height: 'Height',
                minWidth: 'Min Width',
                maxWidth: 'Max Width',
                apply: 'Apply',
                cancel: 'Cancel',
                delete: 'Delete',
                save: 'Save',
                reset: 'Reset',
                responsiveTips: 'Responsive Tips',
                mobileFirst: 'Mobile-first approach',
                flexibleGrid: 'Use flexible grid systems',
                responsiveImages: 'Make images responsive',
                touchFriendly: 'Ensure touch-friendly interactions',
                performance: 'Optimize for performance',
                accessibility: 'Maintain accessibility'
            },
            ru: {
                responsive: 'Адаптивный дизайн',
                breakpoints: 'Точки перелома',
                devices: 'Устройства',
                preview: 'Предварительный просмотр',
                mobile: 'Мобильный',
                tablet: 'Планшет',
                desktop: 'Десктоп',
                portrait: 'Портретная',
                landscape: 'Ландшафтная',
                addBreakpoint: 'Добавить точку перелома',
                customBreakpoint: 'Пользовательская точка перелома',
                responsiveStyles: 'Адаптивные стили',
                hideOnMobile: 'Скрыть на мобильном',
                showOnMobile: 'Показать на мобильном',
                responsiveGrid: 'Адаптивная сетка',
                flexDirection: 'Направление Flex',
                elementOrder: 'Порядок элементов',
                responsiveImages: 'Адаптивные изображения',
                generateCSS: 'Сгенерировать CSS',
                exportResponsive: 'Экспорт адаптивного CSS',
                breakpointEditor: 'Редактор точек перелома',
                devicePreview: 'Предварительный просмотр устройств',
                layoutTools: 'Инструменты макета',
                styleEditor: 'Редактор стилей',
                width: 'Ширина',
                height: 'Высота',
                minWidth: 'Мин. ширина',
                maxWidth: 'Макс. ширина',
                apply: 'Применить',
                cancel: 'Отмена',
                delete: 'Удалить',
                save: 'Сохранить',
                reset: 'Сброс',
                responsiveTips: 'Советы по адаптивности',
                mobileFirst: 'Подход mobile-first',
                flexibleGrid: 'Используйте гибкие сетки',
                responsiveImages: 'Делайте изображения адаптивными',
                touchFriendly: 'Обеспечьте удобство касаний',
                performance: 'Оптимизируйте производительность',
                accessibility: 'Сохраняйте доступность'
            }
        };
        
        this.currentLang = 'en';
        this.init();
    }
    
    init() {
        this.createResponsivePanel();
        this.createDeviceToolbar();
        this.createBreakpointEditor();
        this.createDevicePreview();
        this.createResponsiveStyleEditor();
        this.createLayoutTools();
        this.bindEvents();
        this.loadProjectBreakpoints();
    }
    
    t(key) {
        return this.translations[this.currentLang][key] || key;
    }
    
    setLanguage(lang) {
        this.currentLang = lang;
        this.updateUI();
    }
    
    createResponsivePanel() {
        const panel = this.editor.Panels.addPanel({
            id: 'responsive-panel',
            visible: true,
            buttons: [
                {
                    id: 'responsive-toggle',
                    className: 'btn-responsive',
                    command: 'responsive-toggle',
                    attributes: { title: this.t('responsive') }
                }
            ]
        });
        
        // Add responsive panel content
        const panelContent = `
            <div class="responsive-panel-content">
                <div class="responsive-tabs">
                    <button class="tab-btn active" data-tab="breakpoints">${this.t('breakpoints')}</button>
                    <button class="tab-btn" data-tab="devices">${this.t('devices')}</button>
                    <button class="tab-btn" data-tab="preview">${this.t('preview')}</button>
                    <button class="tab-btn" data-tab="styles">${this.t('responsiveStyles')}</button>
                    <button class="tab-btn" data-tab="layout">${this.t('layoutTools')}</button>
                </div>
                
                <div class="tab-content active" data-tab="breakpoints">
                    <div class="breakpoints-list">
                        ${this.renderBreakpointsList()}
                    </div>
                    <button class="btn-add-breakpoint">${this.t('addBreakpoint')}</button>
                </div>
                
                <div class="tab-content" data-tab="devices">
                    <div class="device-selector">
                        <div class="device-option" data-device="iphone">
                            <div class="device-icon iphone-icon"></div>
                            <span>iPhone</span>
                        </div>
                        <div class="device-option" data-device="ipad">
                            <div class="device-icon ipad-icon"></div>
                            <span>iPad</span>
                        </div>
                        <div class="device-option" data-device="desktop">
                            <div class="device-icon desktop-icon"></div>
                            <span>${this.t('desktop')}</span>
                        </div>
                    </div>
                    <div class="orientation-controls">
                        <button class="orientation-btn active" data-orientation="portrait">${this.t('portrait')}</button>
                        <button class="orientation-btn" data-orientation="landscape">${this.t('landscape')}</button>
                    </div>
                </div>
                
                <div class="tab-content" data-tab="preview">
                    <div class="device-preview-container">
                        <div class="device-frame" id="device-frame">
                            <div class="device-screen">
                                <iframe id="responsive-preview" src="about:blank"></iframe>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" data-tab="styles">
                    <div class="responsive-style-editor">
                        <div class="style-controls">
                            <label>
                                <input type="checkbox" id="hide-mobile"> ${this.t('hideOnMobile')}
                            </label>
                            <label>
                                <input type="checkbox" id="hide-tablet"> ${this.t('hideOnMobile').replace('Mobile', 'Tablet')}
                            </label>
                        </div>
                        <div class="responsive-typography">
                            <h4>${this.t('responsiveStyles')}</h4>
                            <div class="typography-controls">
                                <label>Font Size: <input type="range" id="font-size" min="12" max="48" value="16"></label>
                                <label>Line Height: <input type="range" id="line-height" min="1" max="2" step="0.1" value="1.5"></label>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-content" data-tab="layout">
                    <div class="layout-tools">
                        <div class="grid-controls">
                            <h4>${this.t('responsiveGrid')}</h4>
                            <label>Columns: <input type="number" id="grid-columns" min="1" max="12" value="12"></label>
                            <label>Gap: <input type="number" id="grid-gap" min="0" max="50" value="20"></label>
                        </div>
                        <div class="flex-controls">
                            <h4>${this.t('flexDirection')}</h4>
                            <select id="flex-direction">
                                <option value="row">Row</option>
                                <option value="column">Column</option>
                                <option value="row-reverse">Row Reverse</option>
                                <option value="column-reverse">Column Reverse</option>
                            </select>
                        </div>
                        <div class="order-controls">
                            <h4>${this.t('elementOrder')}</h4>
                            <label>Order: <input type="number" id="element-order" min="-10" max="10" value="0"></label>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        panel.set('content', panelContent);
    }
    
    renderBreakpointsList() {
        let html = '';
        
        Object.entries(this.breakpoints).forEach(([key, bp]) => {
            const isActive = this.currentBreakpoint === key;
            html += `
                <div class="breakpoint-item ${isActive ? 'active' : ''}" data-breakpoint="${key}">
                    <div class="breakpoint-info">
                        <span class="breakpoint-name">${bp.name}</span>
                        <span class="breakpoint-size">${bp.width}px</span>
                    </div>
                    <div class="breakpoint-actions">
                        <button class="btn-edit-breakpoint" title="Edit">✏️</button>
                        <button class="btn-delete-breakpoint" title="Delete">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        this.customBreakpoints.forEach((bp, index) => {
            html += `
                <div class="breakpoint-item custom" data-breakpoint="custom-${index}">
                    <div class="breakpoint-info">
                        <span class="breakpoint-name">${bp.name}</span>
                        <span class="breakpoint-size">${bp.width}px</span>
                    </div>
                    <div class="breakpoint-actions">
                        <button class="btn-edit-breakpoint" title="Edit">✏️</button>
                        <button class="btn-delete-breakpoint" title="Delete">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        return html;
    }
    
    createDeviceToolbar() {
        const toolbar = this.editor.Panels.addPanel({
            id: 'device-toolbar',
            visible: true,
            buttons: [
                {
                    id: 'device-mobile',
                    className: 'btn-device-mobile',
                    command: 'device-mobile',
                    attributes: { title: this.t('mobile') }
                },
                {
                    id: 'device-tablet',
                    className: 'btn-device-tablet',
                    command: 'device-tablet',
                    attributes: { title: this.t('tablet') }
                },
                {
                    id: 'device-desktop',
                    className: 'btn-device-desktop',
                    command: 'device-desktop',
                    attributes: { title: this.t('desktop') }
                }
            ]
        });
    }
    
    createBreakpointEditor() {
        const modal = this.editor.Modal;
        
        modal.setTitle(this.t('breakpointEditor'));
        modal.setContent(`
            <div class="breakpoint-editor">
                <div class="breakpoint-form">
                    <div class="form-group">
                        <label>${this.t('width')}:</label>
                        <input type="number" id="bp-width" min="320" max="1920" value="768">
                    </div>
                    <div class="form-group">
                        <label>${this.t('height')}:</label>
                        <input type="number" id="bp-height" min="480" max="1080" value="1024">
                    </div>
                    <div class="form-group">
                        <label>${this.t('minWidth')}:</label>
                        <input type="number" id="bp-min-width" min="0" max="1920" value="0">
                    </div>
                    <div class="form-group">
                        <label>${this.t('maxWidth')}:</label>
                        <input type="number" id="bp-max-width" min="0" max="1920" value="1024">
                    </div>
                    <div class="form-group">
                        <label>Name:</label>
                        <input type="text" id="bp-name" value="Custom Breakpoint">
                    </div>
                </div>
                <div class="breakpoint-preview">
                    <div class="preview-frame" id="breakpoint-preview">
                        <div class="preview-content"></div>
                    </div>
                </div>
                <div class="breakpoint-actions">
                    <button class="btn-apply">${this.t('apply')}</button>
                    <button class="btn-cancel">${this.t('cancel')}</button>
                </div>
            </div>
        `);
    }
    
    createDevicePreview() {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'device-preview';
        previewContainer.innerHTML = `
            <div class="device-frame ${this.deviceFrames[this.currentDevice].frame}">
                <div class="device-screen">
                    <iframe id="responsive-preview" src="about:blank"></iframe>
                </div>
            </div>
        `;
        
        document.body.appendChild(previewContainer);
    }
    
    createResponsiveStyleEditor() {
        const styleEditor = document.createElement('div');
        styleEditor.className = 'responsive-style-editor';
        styleEditor.innerHTML = `
            <div class="style-panel">
                <h3>${this.t('responsiveStyles')}</h3>
                <div class="style-controls">
                    <div class="control-group">
                        <label>${this.t('hideOnMobile')}</label>
                        <input type="checkbox" id="hide-mobile">
                    </div>
                    <div class="control-group">
                        <label>${this.t('hideOnMobile').replace('Mobile', 'Tablet')}</label>
                        <input type="checkbox" id="hide-tablet">
                    </div>
                    <div class="control-group">
                        <label>Font Size</label>
                        <input type="range" id="font-size" min="12" max="48" value="16">
                        <span class="value-display">16px</span>
                    </div>
                    <div class="control-group">
                        <label>Line Height</label>
                        <input type="range" id="line-height" min="1" max="2" step="0.1" value="1.5">
                        <span class="value-display">1.5</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    createLayoutTools() {
        const layoutTools = document.createElement('div');
        layoutTools.className = 'layout-tools';
        layoutTools.innerHTML = `
            <div class="layout-panel">
                <h3>${this.t('layoutTools')}</h3>
                <div class="grid-controls">
                    <h4>${this.t('responsiveGrid')}</h4>
                    <div class="control-group">
                        <label>Columns:</label>
                        <input type="number" id="grid-columns" min="1" max="12" value="12">
                    </div>
                    <div class="control-group">
                        <label>Gap:</label>
                        <input type="number" id="grid-gap" min="0" max="50" value="20">
                    </div>
                </div>
                <div class="flex-controls">
                    <h4>${this.t('flexDirection')}</h4>
                    <div class="control-group">
                        <select id="flex-direction">
                            <option value="row">Row</option>
                            <option value="column">Column</option>
                            <option value="row-reverse">Row Reverse</option>
                            <option value="column-reverse">Column Reverse</option>
                        </select>
                    </div>
                </div>
                <div class="order-controls">
                    <h4>${this.t('elementOrder')}</h4>
                    <div class="control-group">
                        <label>Order:</label>
                        <input type="number" id="element-order" min="-10" max="10" value="0">
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Breakpoint switching
        document.addEventListener('click', (e) => {
            if (e.target.closest('.breakpoint-item')) {
                const breakpoint = e.target.closest('.breakpoint-item').dataset.breakpoint;
                this.switchBreakpoint(breakpoint);
            }
        });
        
        // Device switching
        document.addEventListener('click', (e) => {
            if (e.target.closest('.device-option')) {
                const device = e.target.closest('.device-option').dataset.device;
                this.switchDevice(device);
            }
        });
        
        // Orientation switching
        document.addEventListener('click', (e) => {
            if (e.target.closest('.orientation-btn')) {
                const orientation = e.target.closest('.orientation-btn').dataset.orientation;
                this.switchOrientation(orientation);
            }
        });
        
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.closest('.tab-btn')) {
                const tab = e.target.closest('.tab-btn').dataset.tab;
                this.switchTab(tab);
            }
        });
        
        // Style controls
        document.addEventListener('input', (e) => {
            if (e.target.id === 'font-size') {
                this.updateFontSize(e.target.value);
            } else if (e.target.id === 'line-height') {
                this.updateLineHeight(e.target.value);
            } else if (e.target.id === 'grid-columns') {
                this.updateGridColumns(e.target.value);
            } else if (e.target.id === 'grid-gap') {
                this.updateGridGap(e.target.value);
            } else if (e.target.id === 'flex-direction') {
                this.updateFlexDirection(e.target.value);
            } else if (e.target.id === 'element-order') {
                this.updateElementOrder(e.target.value);
            }
        });
        
        // Visibility controls
        document.addEventListener('change', (e) => {
            if (e.target.id === 'hide-mobile') {
                this.toggleElementVisibility('mobile', e.target.checked);
            } else if (e.target.id === 'hide-tablet') {
                this.toggleElementVisibility('tablet', e.target.checked);
            }
        });
    }
    
    switchBreakpoint(breakpoint) {
        this.currentBreakpoint = breakpoint;
        this.updateBreakpointUI();
        this.applyBreakpointStyles();
        this.updatePreview();
    }
    
    switchDevice(device) {
        this.currentDevice = device;
        this.updateDeviceUI();
        this.updatePreview();
    }
    
    switchOrientation(orientation) {
        this.orientation = orientation;
        this.updateOrientationUI();
        this.updatePreview();
    }
    
    switchTab(tab) {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to selected tab and content
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        document.querySelector(`.tab-content[data-tab="${tab}"]`).classList.add('active');
    }
    
    updateBreakpointUI() {
        document.querySelectorAll('.breakpoint-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-breakpoint="${this.currentBreakpoint}"]`).classList.add('active');
    }
    
    updateDeviceUI() {
        document.querySelectorAll('.device-option').forEach(option => {
            option.classList.remove('active');
        });
        document.querySelector(`[data-device="${this.currentDevice}"]`).classList.add('active');
    }
    
    updateOrientationUI() {
        document.querySelectorAll('.orientation-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-orientation="${this.orientation}"]`).classList.add('active');
    }
    
    applyBreakpointStyles() {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        const breakpoint = this.breakpoints[this.currentBreakpoint];
        if (!breakpoint) return;
        
        // Apply responsive styles based on breakpoint
        const styles = selected.getStyle();
        const responsiveStyles = {};
        
        if (breakpoint.maxWidth) {
            responsiveStyles[`@media (max-width: ${breakpoint.maxWidth}px)`] = {
                ...styles
            };
        } else if (breakpoint.minWidth) {
            responsiveStyles[`@media (min-width: ${breakpoint.minWidth}px)`] = {
                ...styles
            };
        }
        
        selected.setStyle(responsiveStyles);
    }
    
    updatePreview() {
        const preview = document.getElementById('responsive-preview');
        if (!preview) return;
        
        const device = this.deviceFrames[this.currentDevice];
        const breakpoint = this.breakpoints[this.currentBreakpoint];
        
        // Update preview dimensions
        let width = device.width;
        let height = device.height;
        
        if (this.orientation === 'landscape') {
            [width, height] = [height, width];
        }
        
        preview.style.width = `${width}px`;
        preview.style.height = `${height}px`;
        
        // Update device frame
        const frame = document.querySelector('.device-frame');
        if (frame) {
            frame.className = `device-frame ${device.frame}`;
            if (this.orientation === 'landscape') {
                frame.classList.add('landscape');
            } else {
                frame.classList.remove('landscape');
            }
        }
        
        // Update preview content
        const html = this.editor.getHtml();
        const css = this.editor.getCss();
        
        const previewContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    ${css}
                    body { margin: 0; padding: 0; }
                </style>
            </head>
            <body>
                ${html}
            </body>
            </html>
        `;
        
        preview.srcdoc = previewContent;
    }
    
    updateFontSize(size) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 'font-size': `${size}px` });
        document.querySelector('#font-size + .value-display').textContent = `${size}px`;
    }
    
    updateLineHeight(height) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 'line-height': height });
        document.querySelector('#line-height + .value-display').textContent = height;
    }
    
    updateGridColumns(columns) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 
            'display': 'grid',
            'grid-template-columns': `repeat(${columns}, 1fr)`
        });
    }
    
    updateGridGap(gap) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 'gap': `${gap}px` });
    }
    
    updateFlexDirection(direction) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 
            'display': 'flex',
            'flex-direction': direction
        });
    }
    
    updateElementOrder(order) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        selected.setStyle({ 'order': order });
    }
    
    toggleElementVisibility(device, hide) {
        const selected = this.editor.getSelected();
        if (!selected) return;
        
        const breakpoint = this.breakpoints[device];
        if (!breakpoint) return;
        
        const mediaQuery = breakpoint.maxWidth ? 
            `@media (max-width: ${breakpoint.maxWidth}px)` :
            `@media (min-width: ${breakpoint.minWidth}px)`;
        
        const styles = selected.getStyle();
        const responsiveStyles = styles[mediaQuery] || {};
        
        if (hide) {
            responsiveStyles.display = 'none';
        } else {
            delete responsiveStyles.display;
        }
        
        styles[mediaQuery] = responsiveStyles;
        selected.setStyle(styles);
    }
    
    loadProjectBreakpoints() {
        // Load breakpoints from project CSS files
        const projectBreakpoints = this.extractBreakpointsFromCSS();
        this.customBreakpoints = projectBreakpoints;
        this.updateBreakpointsList();
    }
    
    extractBreakpointsFromCSS() {
        // Extract breakpoints from existing CSS files
        const breakpoints = [];
        
        // Common breakpoints found in the project
        const commonBreakpoints = [
            { width: 641, maxWidth: 768, name: 'Small Tablet' },
            { width: 769, minWidth: 769, maxWidth: 1024, name: 'Large Tablet' },
            { width: 1025, minWidth: 1025, name: 'Desktop' }
        ];
        
        return commonBreakpoints;
    }
    
    updateBreakpointsList() {
        const list = document.querySelector('.breakpoints-list');
        if (list) {
            list.innerHTML = this.renderBreakpointsList();
        }
    }
    
    generateResponsiveCSS() {
        const html = this.editor.getHtml();
        const css = this.editor.getCss();
        
        let responsiveCSS = '';
        
        // Generate CSS for each breakpoint
        Object.entries(this.breakpoints).forEach(([key, bp]) => {
            if (bp.maxWidth) {
                responsiveCSS += `
@media (max-width: ${bp.maxWidth}px) {
    /* ${bp.name} styles */
    ${this.generateBreakpointCSS(key)}
}
`;
            } else if (bp.minWidth) {
                responsiveCSS += `
@media (min-width: ${bp.minWidth}px) {
    /* ${bp.name} styles */
    ${this.generateBreakpointCSS(key)}
}
`;
            }
        });
        
        return responsiveCSS;
    }
    
    generateBreakpointCSS(breakpoint) {
        // Generate specific CSS for breakpoint
        const selected = this.editor.getSelected();
        if (!selected) return '';
        
        const styles = selected.getStyle();
        const breakpointStyles = styles[`@media (max-width: ${this.breakpoints[breakpoint].maxWidth}px)`] || {};
        
        let css = '';
        Object.entries(breakpointStyles).forEach(([property, value]) => {
            css += `    ${property}: ${value};\n`;
        });
        
        return css;
    }
    
    exportResponsiveCSS() {
        const responsiveCSS = this.generateResponsiveCSS();
        const blob = new Blob([responsiveCSS], { type: 'text/css' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'responsive-styles.css';
        a.click();
        
        URL.revokeObjectURL(url);
    }
    
    updateUI() {
        // Update all UI elements with current language
        this.updateBreakpointsList();
        this.updateDeviceUI();
        this.updateOrientationUI();
    }
}

// Add responsive design system to GrapesJS
if (typeof grapesjs !== 'undefined') {
    grapesjs.plugins.add('responsive-design-system', (editor, opts = {}) => {
        const responsiveSystem = new ResponsiveDesignSystem(editor);
        
        // Add commands
        editor.Commands.add('responsive-toggle', {
            run: (editor) => {
                const panel = editor.Panels.getPanel('responsive-panel');
                panel.set('visible', !panel.get('visible'));
            }
        });
        
        editor.Commands.add('device-mobile', {
            run: (editor) => {
                responsiveSystem.switchDevice('iphone');
            }
        });
        
        editor.Commands.add('device-tablet', {
            run: (editor) => {
                responsiveSystem.switchDevice('ipad');
            }
        });
        
        editor.Commands.add('device-desktop', {
            run: (editor) => {
                responsiveSystem.switchDevice('desktop');
            }
        });
        
        // Add responsive CSS
        const responsiveCSS = `
            .responsive-panel-content {
                padding: 15px;
                background: var(--bg-surface);
                border-radius: var(--border-radius);
            }
            
            .responsive-tabs {
                display: flex;
                border-bottom: 1px solid var(--border-color);
                margin-bottom: 15px;
            }
            
            .tab-btn {
                padding: 8px 16px;
                border: none;
                background: none;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                transition: all var(--transition-speed);
            }
            
            .tab-btn.active {
                border-bottom-color: var(--primary);
                color: var(--primary);
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .breakpoints-list {
                margin-bottom: 15px;
            }
            
            .breakpoint-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                margin-bottom: 5px;
                background: var(--bg-surface);
                border-radius: var(--border-radius);
                border: 1px solid var(--border-color);
                cursor: pointer;
                transition: all var(--transition-speed);
            }
            
            .breakpoint-item:hover {
                background: var(--bg-hover);
            }
            
            .breakpoint-item.active {
                border-color: var(--primary);
                background: var(--primary-color);
                color: white;
            }
            
            .breakpoint-info {
                display: flex;
                flex-direction: column;
            }
            
            .breakpoint-name {
                font-weight: bold;
            }
            
            .breakpoint-size {
                font-size: 0.8em;
                opacity: 0.8;
            }
            
            .breakpoint-actions {
                display: flex;
                gap: 5px;
            }
            
            .btn-add-breakpoint {
                width: 100%;
                padding: 10px;
                background: var(--primary);
                color: white;
                border: none;
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: all var(--transition-speed);
            }
            
            .btn-add-breakpoint:hover {
                background: var(--primary-dark);
            }
            
            .device-selector {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .device-option {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 15px;
                background: var(--bg-surface);
                border-radius: var(--border-radius);
                border: 1px solid var(--border-color);
                cursor: pointer;
                transition: all var(--transition-speed);
            }
            
            .device-option:hover {
                background: var(--bg-hover);
            }
            
            .device-option.active {
                border-color: var(--primary);
                background: var(--primary-color);
                color: white;
            }
            
            .device-icon {
                width: 40px;
                height: 40px;
                margin-bottom: 5px;
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
            }
            
            .iphone-icon {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>');
            }
            
            .ipad-icon {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M19 0H5c-1.1 0-2 .9-2 2v20c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V2c0-1.1-.9-2-2-2zm-5 22h-4v-1h4v1zm5.25-3H4.75V3h14.5v16z"/></svg>');
            }
            
            .desktop-icon {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H3V4h18v10z"/></svg>');
            }
            
            .orientation-controls {
                display: flex;
                gap: 10px;
            }
            
            .orientation-btn {
                flex: 1;
                padding: 8px;
                background: var(--bg-surface);
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: all var(--transition-speed);
            }
            
            .orientation-btn.active {
                background: var(--primary);
                color: white;
                border-color: var(--primary);
            }
            
            .device-preview-container {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 300px;
                background: var(--bg-surface);
                border-radius: var(--border-radius);
            }
            
            .device-frame {
                position: relative;
                background: #333;
                border-radius: 20px;
                padding: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            
            .device-frame.iphone-frame {
                width: 375px;
                height: 812px;
            }
            
            .device-frame.ipad-frame {
                width: 768px;
                height: 1024px;
            }
            
            .device-frame.desktop-frame {
                width: 1200px;
                height: 800px;
            }
            
            .device-frame.landscape {
                transform: rotate(90deg);
            }
            
            .device-screen {
                width: 100%;
                height: 100%;
                background: white;
                border-radius: 10px;
                overflow: hidden;
            }
            
            .device-screen iframe {
                width: 100%;
                height: 100%;
                border: none;
            }
            
            .responsive-style-editor {
                padding: 15px;
            }
            
            .style-controls {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .control-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .control-group label {
                min-width: 100px;
            }
            
            .control-group input[type="range"] {
                flex: 1;
            }
            
            .value-display {
                min-width: 40px;
                text-align: right;
                font-weight: bold;
            }
            
            .layout-tools {
                padding: 15px;
            }
            
            .grid-controls,
            .flex-controls,
            .order-controls {
                margin-bottom: 20px;
            }
            
            .grid-controls h4,
            .flex-controls h4,
            .order-controls h4 {
                margin-bottom: 10px;
                color: var(--text-primary);
            }
            
            .breakpoint-editor {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                padding: 20px;
            }
            
            .breakpoint-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            
            .form-group label {
                font-weight: bold;
            }
            
            .form-group input {
                padding: 8px;
                border: 1px solid var(--border-color);
                border-radius: var(--border-radius);
            }
            
            .breakpoint-preview {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .preview-frame {
                width: 200px;
                height: 150px;
                border: 2px solid var(--border-color);
                border-radius: var(--border-radius);
                position: relative;
            }
            
            .preview-content {
                width: 100%;
                height: 100%;
                background: var(--bg-surface);
                border-radius: calc(var(--border-radius) - 2px);
            }
            
            .breakpoint-actions {
                grid-column: 1 / -1;
                display: flex;
                gap: 10px;
                justify-content: flex-end;
            }
            
            .btn-apply,
            .btn-cancel {
                padding: 8px 16px;
                border: none;
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: all var(--transition-speed);
            }
            
            .btn-apply {
                background: var(--primary);
                color: white;
            }
            
            .btn-apply:hover {
                background: var(--primary-dark);
            }
            
            .btn-cancel {
                background: var(--bg-surface);
                border: 1px solid var(--border-color);
            }
            
            .btn-cancel:hover {
                background: var(--bg-hover);
            }
            
            /* Device toolbar buttons */
            .btn-device-mobile,
            .btn-device-tablet,
            .btn-device-desktop {
                width: 40px;
                height: 40px;
                border: none;
                border-radius: var(--border-radius);
                cursor: pointer;
                transition: all var(--transition-speed);
                background-size: 20px;
                background-repeat: no-repeat;
                background-position: center;
            }
            
            .btn-device-mobile {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>');
            }
            
            .btn-device-tablet {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M19 0H5c-1.1 0-2 .9-2 2v20c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V2c0-1.1-.9-2-2-2zm-5 22h-4v-1h4v1zm5.25-3H4.75V3h14.5v16z"/></svg>');
            }
            
            .btn-device-desktop {
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="currentColor" d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H3V4h18v10z"/></svg>');
            }
            
            .btn-device-mobile:hover,
            .btn-device-tablet:hover,
            .btn-device-desktop:hover {
                background-color: var(--bg-hover);
            }
            
            /* Responsive tips */
            .responsive-tips {
                margin-top: 20px;
                padding: 15px;
                background: var(--bg-surface);
                border-radius: var(--border-radius);
                border-left: 4px solid var(--primary);
            }
            
            .responsive-tips h4 {
                margin-bottom: 10px;
                color: var(--text-primary);
            }
            
            .responsive-tips ul {
                margin: 0;
                padding-left: 20px;
            }
            
            .responsive-tips li {
                margin-bottom: 5px;
                color: var(--text-secondary);
            }
        `;
        
        // Add CSS to editor
        editor.Css.addRules(responsiveCSS);
        
        // Initialize responsive system
        editor.on('load', () => {
            responsiveSystem.updatePreview();
        });
        
        // Update preview when content changes
        editor.on('component:selected', () => {
            responsiveSystem.updatePreview();
        });
        
        editor.on('component:update', () => {
            responsiveSystem.updatePreview();
        });
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResponsiveDesignSystem;
} 