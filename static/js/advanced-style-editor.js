/**
 * Advanced Style Editor for GrapesJS
 * Продвинутый редактор стилей для GrapesJS
 * 
 * Extends GrapesJS with professional styling capabilities
 * Расширяет GrapesJS профессиональными возможностями стилизации
 */

(function() {
    'use strict';

    // Language support
    const translations = {
        en: {
            animation: 'Animation',
            layout: 'Layout',
            typography: 'Typography',
            effects: 'Effects',
            duration: 'Duration',
            delay: 'Delay',
            easing: 'Easing',
            hover: 'Hover Effects',
            scroll: 'Scroll Animations',
            keyframes: 'Keyframes',
            flexbox: 'Flexbox',
            grid: 'Grid',
            position: 'Position',
            zIndex: 'Z-Index',
            fontPairing: 'Font Pairing',
            textShadow: 'Text Shadow',
            lineHeight: 'Line Height',
            letterSpacing: 'Letter Spacing',
            boxShadow: 'Box Shadow',
            borderRadius: 'Border Radius',
            backdropFilter: 'Backdrop Filter',
            gradient: 'Gradient',
            preview: 'Preview',
            presets: 'Presets',
            export: 'Export',
            import: 'Import',
            undo: 'Undo',
            redo: 'Redo',
            reset: 'Reset'
        },
        ru: {
            animation: 'Анимации',
            layout: 'Расположение',
            typography: 'Типографика',
            effects: 'Эффекты',
            duration: 'Длительность',
            delay: 'Задержка',
            easing: 'Плавность',
            hover: 'Эффекты при наведении',
            scroll: 'Анимации при прокрутке',
            keyframes: 'Ключевые кадры',
            flexbox: 'Flexbox',
            grid: 'Сетка',
            position: 'Позиция',
            zIndex: 'Z-индекс',
            fontPairing: 'Парные шрифты',
            textShadow: 'Тень текста',
            lineHeight: 'Высота строки',
            letterSpacing: 'Межбуквенный интервал',
            boxShadow: 'Тень блока',
            borderRadius: 'Радиус границ',
            backdropFilter: 'Фоновая фильтрация',
            gradient: 'Градиент',
            preview: 'Предпросмотр',
            presets: 'Пресеты',
            export: 'Экспорт',
            import: 'Импорт',
            undo: 'Отменить',
            redo: 'Повторить',
            reset: 'Сброс'
        }
    };

    // Helper function to get current language
    function getCurrentLanguage() {
        return document.documentElement.lang || 'en';
    }

    // Helper function to get localized text
    function getLocalizedText(key) {
        const lang = getCurrentLanguage();
        return translations[lang]?.[key] || translations.en[key] || key;
    }

    class AdvancedStyleEditor {
        constructor(editor) {
            this.editor = editor;
            this.currentComponent = null;
            this.history = [];
            this.historyIndex = -1;
            this.maxHistory = 50;
            
            this.init();
        }

        init() {
            this.createPanels();
            this.bindEvents();
            this.loadPresets();
        }

        createPanels() {
            // Animation Panel
            this.createAnimationPanel();
            
            // Layout Panel
            this.createLayoutPanel();
            
            // Typography Panel
            this.createTypographyPanel();
            
            // Effects Panel
            this.createEffectsPanel();
        }

        createAnimationPanel() {
            const panel = this.editor.Panels.addPanel({
                id: 'animation-panel',
                visible: true,
                buttons: [{
                    id: 'animation-btn',
                    className: 'btn-animation',
                    label: getLocalizedText('animation'),
                    command: 'animation-panel',
                    active: false
                }]
            });

            const animationView = `
                <div class="animation-panel">
                    <div class="panel-section">
                        <h4>${getLocalizedText('animation')}</h4>
                        
                        <div class="control-group">
                            <label>${getLocalizedText('duration')}</label>
                            <input type="range" id="anim-duration" min="0" max="5" step="0.1" value="0.3">
                            <span class="value-display">0.3s</span>
                        </div>
                        
                        <div class="control-group">
                            <label>${getLocalizedText('delay')}</label>
                            <input type="range" id="anim-delay" min="0" max="2" step="0.1" value="0">
                            <span class="value-display">0s</span>
                        </div>
                        
                        <div class="control-group">
                            <label>${getLocalizedText('easing')}</label>
                            <select id="anim-easing">
                                <option value="ease">ease</option>
                                <option value="linear">linear</option>
                                <option value="ease-in">ease-in</option>
                                <option value="ease-out">ease-out</option>
                                <option value="ease-in-out">ease-in-out</option>
                                <option value="cubic-bezier(0.68, -0.55, 0.265, 1.55)">bounce</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('hover')}</h4>
                        <div class="hover-effects">
                            <button class="hover-preset" data-effect="scale">Scale</button>
                            <button class="hover-preset" data-effect="rotate">Rotate</button>
                            <button class="hover-preset" data-effect="glow">Glow</button>
                            <button class="hover-preset" data-effect="slide">Slide</button>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('keyframes')}</h4>
                        <div class="keyframe-builder">
                            <div class="keyframe-point" data-time="0%">
                                <span class="time">0%</span>
                                <div class="properties">
                                    <input type="text" placeholder="opacity: 0" class="keyframe-prop">
                                </div>
                            </div>
                            <div class="keyframe-point" data-time="100%">
                                <span class="time">100%</span>
                                <div class="properties">
                                    <input type="text" placeholder="opacity: 1" class="keyframe-prop">
                                </div>
                            </div>
                            <button class="add-keyframe">+ Add Keyframe</button>
                        </div>
                    </div>
                </div>
            `;

            panel.set('content', animationView);
        }

        createLayoutPanel() {
            const panel = this.editor.Panels.addPanel({
                id: 'layout-panel',
                visible: true,
                buttons: [{
                    id: 'layout-btn',
                    className: 'btn-layout',
                    label: getLocalizedText('layout'),
                    command: 'layout-panel',
                    active: false
                }]
            });

            const layoutView = `
                <div class="layout-panel">
                    <div class="panel-section">
                        <h4>${getLocalizedText('flexbox')}</h4>
                        <div class="flexbox-editor">
                            <div class="flex-preview">
                                <div class="flex-container" id="flex-preview">
                                    <div class="flex-item">1</div>
                                    <div class="flex-item">2</div>
                                    <div class="flex-item">3</div>
                                </div>
                            </div>
                            <div class="flex-controls">
                                <label>Direction:</label>
                                <select id="flex-direction">
                                    <option value="row">Row</option>
                                    <option value="column">Column</option>
                                    <option value="row-reverse">Row Reverse</option>
                                    <option value="column-reverse">Column Reverse</option>
                                </select>
                                
                                <label>Justify:</label>
                                <select id="flex-justify">
                                    <option value="flex-start">Start</option>
                                    <option value="center">Center</option>
                                    <option value="flex-end">End</option>
                                    <option value="space-between">Space Between</option>
                                    <option value="space-around">Space Around</option>
                                </select>
                                
                                <label>Align:</label>
                                <select id="flex-align">
                                    <option value="stretch">Stretch</option>
                                    <option value="flex-start">Start</option>
                                    <option value="center">Center</option>
                                    <option value="flex-end">End</option>
                                    <option value="baseline">Baseline</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('grid')}</h4>
                        <div class="grid-builder">
                            <div class="grid-preview" id="grid-preview">
                                <div class="grid-item">1</div>
                                <div class="grid-item">2</div>
                                <div class="grid-item">3</div>
                                <div class="grid-item">4</div>
                            </div>
                            <div class="grid-controls">
                                <label>Columns:</label>
                                <input type="number" id="grid-columns" min="1" max="12" value="3">
                                
                                <label>Rows:</label>
                                <input type="number" id="grid-rows" min="1" max="12" value="2">
                                
                                <label>Gap:</label>
                                <input type="range" id="grid-gap" min="0" max="50" value="10">
                                <span class="value-display">10px</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('position')}</h4>
                        <div class="position-controls">
                            <label>Type:</label>
                            <select id="position-type">
                                <option value="static">Static</option>
                                <option value="relative">Relative</option>
                                <option value="absolute">Absolute</option>
                                <option value="fixed">Fixed</option>
                                <option value="sticky">Sticky</option>
                            </select>
                            
                            <div class="position-values">
                                <label>Top:</label>
                                <input type="number" id="pos-top" placeholder="0">
                                
                                <label>Right:</label>
                                <input type="number" id="pos-right" placeholder="0">
                                
                                <label>Bottom:</label>
                                <input type="number" id="pos-bottom" placeholder="0">
                                
                                <label>Left:</label>
                                <input type="number" id="pos-left" placeholder="0">
                            </div>
                            
                            <label>${getLocalizedText('zIndex')}:</label>
                            <input type="number" id="z-index" placeholder="0">
                        </div>
                    </div>
                </div>
            `;

            panel.set('content', layoutView);
        }

        createTypographyPanel() {
            const panel = this.editor.Panels.addPanel({
                id: 'typography-panel',
                visible: true,
                buttons: [{
                    id: 'typography-btn',
                    className: 'btn-typography',
                    label: getLocalizedText('typography'),
                    command: 'typography-panel',
                    active: false
                }]
            });

            const typographyView = `
                <div class="typography-panel">
                    <div class="panel-section">
                        <h4>${getLocalizedText('fontPairing')}</h4>
                        <div class="font-pairing">
                            <div class="font-pair" data-pair="modern">
                                <div class="font-preview">
                                    <span class="font-primary">Heading</span>
                                    <span class="font-secondary">Body text</span>
                                </div>
                                <div class="font-info">
                                    <strong>Inter + Roboto</strong>
                                    <small>Modern & Clean</small>
                                </div>
                            </div>
                            <div class="font-pair" data-pair="classic">
                                <div class="font-preview">
                                    <span class="font-primary">Heading</span>
                                    <span class="font-secondary">Body text</span>
                                </div>
                                <div class="font-info">
                                    <strong>Playfair + Source Sans</strong>
                                    <small>Classic & Elegant</small>
                                </div>
                            </div>
                            <div class="font-pair" data-pair="minimal">
                                <div class="font-preview">
                                    <span class="font-primary">Heading</span>
                                    <span class="font-secondary">Body text</span>
                                </div>
                                <div class="font-info">
                                    <strong>Montserrat + Open Sans</strong>
                                    <small>Minimal & Readable</small>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('textShadow')}</h4>
                        <div class="text-shadow-builder">
                            <div class="shadow-preview" id="text-shadow-preview">
                                Sample Text
                            </div>
                            <div class="shadow-controls">
                                <label>X Offset:</label>
                                <input type="range" id="text-shadow-x" min="-20" max="20" value="2">
                                <span class="value-display">2px</span>
                                
                                <label>Y Offset:</label>
                                <input type="range" id="text-shadow-y" min="-20" max="20" value="2">
                                <span class="value-display">2px</span>
                                
                                <label>Blur:</label>
                                <input type="range" id="text-shadow-blur" min="0" max="20" value="4">
                                <span class="value-display">4px</span>
                                
                                <label>Color:</label>
                                <input type="color" id="text-shadow-color" value="#000000">
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('lineHeight')} & ${getLocalizedText('letterSpacing')}</h4>
                        <div class="text-spacing">
                            <div class="control-group">
                                <label>${getLocalizedText('lineHeight')}:</label>
                                <input type="range" id="line-height" min="0.8" max="3" step="0.1" value="1.5">
                                <span class="value-display">1.5</span>
                            </div>
                            
                            <div class="control-group">
                                <label>${getLocalizedText('letterSpacing')}:</label>
                                <input type="range" id="letter-spacing" min="-2" max="10" step="0.5" value="0">
                                <span class="value-display">0px</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            panel.set('content', typographyView);
        }

        createEffectsPanel() {
            const panel = this.editor.Panels.addPanel({
                id: 'effects-panel',
                visible: true,
                buttons: [{
                    id: 'effects-btn',
                    className: 'btn-effects',
                    label: getLocalizedText('effects'),
                    command: 'effects-panel',
                    active: false
                }]
            });

            const effectsView = `
                <div class="effects-panel">
                    <div class="panel-section">
                        <h4>${getLocalizedText('boxShadow')}</h4>
                        <div class="box-shadow-builder">
                            <div class="shadow-preview" id="box-shadow-preview">
                                <div class="shadow-box">Preview Box</div>
                            </div>
                            <div class="shadow-controls">
                                <label>X Offset:</label>
                                <input type="range" id="box-shadow-x" min="-50" max="50" value="0">
                                <span class="value-display">0px</span>
                                
                                <label>Y Offset:</label>
                                <input type="range" id="box-shadow-y" min="-50" max="50" value="10">
                                <span class="value-display">10px</span>
                                
                                <label>Blur:</label>
                                <input type="range" id="box-shadow-blur" min="0" max="100" value="20">
                                <span class="value-display">20px</span>
                                
                                <label>Spread:</label>
                                <input type="range" id="box-shadow-spread" min="-50" max="50" value="0">
                                <span class="value-display">0px</span>
                                
                                <label>Color:</label>
                                <input type="color" id="box-shadow-color" value="#000000">
                                
                                <label>Opacity:</label>
                                <input type="range" id="box-shadow-opacity" min="0" max="1" step="0.1" value="0.3">
                                <span class="value-display">30%</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('borderRadius')}</h4>
                        <div class="border-radius-controls">
                            <div class="radius-preview" id="radius-preview">
                                <div class="radius-box">Radius Preview</div>
                            </div>
                            <div class="radius-inputs">
                                <label>Top Left:</label>
                                <input type="range" id="radius-tl" min="0" max="100" value="0">
                                <span class="value-display">0px</span>
                                
                                <label>Top Right:</label>
                                <input type="range" id="radius-tr" min="0" max="100" value="0">
                                <span class="value-display">0px</span>
                                
                                <label>Bottom Right:</label>
                                <input type="range" id="radius-br" min="0" max="100" value="0">
                                <span class="value-display">0px</span>
                                
                                <label>Bottom Left:</label>
                                <input type="range" id="radius-bl" min="0" max="100" value="0">
                                <span class="value-display">0px</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('backdropFilter')}</h4>
                        <div class="backdrop-filter-controls">
                            <div class="filter-preview" id="filter-preview">
                                <div class="filter-content">Backdrop Filter Preview</div>
                            </div>
                            <div class="filter-options">
                                <label>Blur:</label>
                                <input type="range" id="backdrop-blur" min="0" max="50" value="10">
                                <span class="value-display">10px</span>
                                
                                <label>Brightness:</label>
                                <input type="range" id="backdrop-brightness" min="0" max="200" value="100">
                                <span class="value-display">100%</span>
                                
                                <label>Contrast:</label>
                                <input type="range" id="backdrop-contrast" min="0" max="200" value="100">
                                <span class="value-display">100%</span>
                                
                                <label>Saturate:</label>
                                <input type="range" id="backdrop-saturate" min="0" max="200" value="100">
                                <span class="value-display">100%</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="panel-section">
                        <h4>${getLocalizedText('gradient')}</h4>
                        <div class="gradient-editor">
                            <div class="gradient-preview" id="gradient-preview"></div>
                            <div class="gradient-controls">
                                <label>Type:</label>
                                <select id="gradient-type">
                                    <option value="linear">Linear</option>
                                    <option value="radial">Radial</option>
                                    <option value="conic">Conic</option>
                                </select>
                                
                                <label>Direction:</label>
                                <select id="gradient-direction">
                                    <option value="to right">To Right</option>
                                    <option value="to bottom">To Bottom</option>
                                    <option value="45deg">45°</option>
                                    <option value="90deg">90°</option>
                                    <option value="135deg">135°</option>
                                </select>
                                
                                <div class="gradient-stops">
                                    <div class="gradient-stop" data-stop="0">
                                        <input type="color" value="#ff0000">
                                        <input type="range" min="0" max="100" value="0">
                                        <span class="stop-position">0%</span>
                                    </div>
                                    <div class="gradient-stop" data-stop="1">
                                        <input type="color" value="#0000ff">
                                        <input type="range" min="0" max="100" value="100">
                                        <span class="stop-position">100%</span>
                                    </div>
                                </div>
                                
                                <button class="add-stop">+ Add Stop</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            panel.set('content', effectsView);
        }

        bindEvents() {
            // Animation events
            this.bindAnimationEvents();
            
            // Layout events
            this.bindLayoutEvents();
            
            // Typography events
            this.bindTypographyEvents();
            
            // Effects events
            this.bindEffectsEvents();
            
            // Global events
            this.bindGlobalEvents();
        }

        bindAnimationEvents() {
            // Duration control
            const durationInput = document.getElementById('anim-duration');
            if (durationInput) {
                durationInput.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + 's';
                    this.updateStyle('transition-duration', value + 's');
                });
            }

            // Delay control
            const delayInput = document.getElementById('anim-delay');
            if (delayInput) {
                delayInput.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + 's';
                    this.updateStyle('transition-delay', value + 's');
                });
            }

            // Easing control
            const easingSelect = document.getElementById('anim-easing');
            if (easingSelect) {
                easingSelect.addEventListener('change', (e) => {
                    this.updateStyle('transition-timing-function', e.target.value);
                });
            }

            // Hover effects
            document.querySelectorAll('.hover-preset').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const effect = e.target.dataset.effect;
                    this.applyHoverEffect(effect);
                });
            });
        }

        bindLayoutEvents() {
            // Flexbox controls
            const flexDirection = document.getElementById('flex-direction');
            if (flexDirection) {
                flexDirection.addEventListener('change', (e) => {
                    this.updateStyle('flex-direction', e.target.value);
                    this.updateFlexPreview();
                });
            }

            const flexJustify = document.getElementById('flex-justify');
            if (flexJustify) {
                flexJustify.addEventListener('change', (e) => {
                    this.updateStyle('justify-content', e.target.value);
                    this.updateFlexPreview();
                });
            }

            const flexAlign = document.getElementById('flex-align');
            if (flexAlign) {
                flexAlign.addEventListener('change', (e) => {
                    this.updateStyle('align-items', e.target.value);
                    this.updateFlexPreview();
                });
            }

            // Grid controls
            const gridColumns = document.getElementById('grid-columns');
            if (gridColumns) {
                gridColumns.addEventListener('input', (e) => {
                    this.updateStyle('grid-template-columns', `repeat(${e.target.value}, 1fr)`);
                    this.updateGridPreview();
                });
            }

            const gridGap = document.getElementById('grid-gap');
            if (gridGap) {
                gridGap.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + 'px';
                    this.updateStyle('gap', value + 'px');
                    this.updateGridPreview();
                });
            }

            // Position controls
            const positionType = document.getElementById('position-type');
            if (positionType) {
                positionType.addEventListener('change', (e) => {
                    this.updateStyle('position', e.target.value);
                });
            }

            ['pos-top', 'pos-right', 'pos-bottom', 'pos-left'].forEach(id => {
                const input = document.getElementById(id);
                if (input) {
                    input.addEventListener('input', (e) => {
                        const property = id.replace('pos-', '');
                        this.updateStyle(property, e.target.value + 'px');
                    });
                }
            });

            const zIndex = document.getElementById('z-index');
            if (zIndex) {
                zIndex.addEventListener('input', (e) => {
                    this.updateStyle('z-index', e.target.value);
                });
            }
        }

        bindTypographyEvents() {
            // Font pairing
            document.querySelectorAll('.font-pair').forEach(pair => {
                pair.addEventListener('click', (e) => {
                    const pairType = e.currentTarget.dataset.pair;
                    this.applyFontPairing(pairType);
                });
            });

            // Text shadow
            ['text-shadow-x', 'text-shadow-y', 'text-shadow-blur'].forEach(id => {
                const input = document.getElementById(id);
                if (input) {
                    input.addEventListener('input', (e) => {
                        this.updateTextShadow();
                    });
                }
            });

            const textShadowColor = document.getElementById('text-shadow-color');
            if (textShadowColor) {
                textShadowColor.addEventListener('change', (e) => {
                    this.updateTextShadow();
                });
            }

            // Line height and letter spacing
            const lineHeight = document.getElementById('line-height');
            if (lineHeight) {
                lineHeight.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value;
                    this.updateStyle('line-height', value);
                });
            }

            const letterSpacing = document.getElementById('letter-spacing');
            if (letterSpacing) {
                letterSpacing.addEventListener('input', (e) => {
                    const value = e.target.value;
                    e.target.nextElementSibling.textContent = value + 'px';
                    this.updateStyle('letter-spacing', value + 'px');
                });
            }
        }

        bindEffectsEvents() {
            // Box shadow
            ['box-shadow-x', 'box-shadow-y', 'box-shadow-blur', 'box-shadow-spread'].forEach(id => {
                const input = document.getElementById(id);
                if (input) {
                    input.addEventListener('input', (e) => {
                        this.updateBoxShadow();
                    });
                }
            });

            const boxShadowColor = document.getElementById('box-shadow-color');
            if (boxShadowColor) {
                boxShadowColor.addEventListener('change', (e) => {
                    this.updateBoxShadow();
                });
            }

            const boxShadowOpacity = document.getElementById('box-shadow-opacity');
            if (boxShadowOpacity) {
                boxShadowOpacity.addEventListener('input', (e) => {
                    const value = Math.round(e.target.value * 100);
                    e.target.nextElementSibling.textContent = value + '%';
                    this.updateBoxShadow();
                });
            }

            // Border radius
            ['radius-tl', 'radius-tr', 'radius-br', 'radius-bl'].forEach(id => {
                const input = document.getElementById(id);
                if (input) {
                    input.addEventListener('input', (e) => {
                        this.updateBorderRadius();
                    });
                }
            });

            // Backdrop filter
            ['backdrop-blur', 'backdrop-brightness', 'backdrop-contrast', 'backdrop-saturate'].forEach(id => {
                const input = document.getElementById(id);
                if (input) {
                    input.addEventListener('input', (e) => {
                        this.updateBackdropFilter();
                    });
                }
            });

            // Gradient
            const gradientType = document.getElementById('gradient-type');
            if (gradientType) {
                gradientType.addEventListener('change', (e) => {
                    this.updateGradient();
                });
            }

            const gradientDirection = document.getElementById('gradient-direction');
            if (gradientDirection) {
                gradientDirection.addEventListener('change', (e) => {
                    this.updateGradient();
                });
            }
        }

        bindGlobalEvents() {
            // Component selection
            this.editor.on('component:selected', (component) => {
                this.currentComponent = component;
                this.loadComponentStyles();
            });

            // Undo/Redo
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    if (e.key === 'z' && !e.shiftKey) {
                        e.preventDefault();
                        this.undo();
                    } else if (e.key === 'z' && e.shiftKey) {
                        e.preventDefault();
                        this.redo();
                    }
                }
            });
        }

        updateStyle(property, value) {
            if (!this.currentComponent) return;

            const style = this.currentComponent.getStyle();
            const oldValue = style[property];
            
            // Add to history
            this.addToHistory(property, oldValue, value);
            
            // Update style
            this.currentComponent.setStyle({ [property]: value });
            
            // Update editor
            this.editor.refresh();
        }

        addToHistory(property, oldValue, newValue) {
            // Remove future history if we're not at the end
            if (this.historyIndex < this.history.length - 1) {
                this.history = this.history.slice(0, this.historyIndex + 1);
            }
            
            // Add new change
            this.history.push({
                property,
                oldValue,
                newValue,
                timestamp: Date.now()
            });
            
            // Limit history size
            if (this.history.length > this.maxHistory) {
                this.history.shift();
            }
            
            this.historyIndex = this.history.length - 1;
        }

        undo() {
            if (this.historyIndex >= 0) {
                const change = this.history[this.historyIndex];
                this.currentComponent.setStyle({ [change.property]: change.oldValue });
                this.historyIndex--;
                this.editor.refresh();
            }
        }

        redo() {
            if (this.historyIndex < this.history.length - 1) {
                this.historyIndex++;
                const change = this.history[this.historyIndex];
                this.currentComponent.setStyle({ [change.property]: change.newValue });
                this.editor.refresh();
            }
        }

        loadComponentStyles() {
            if (!this.currentComponent) return;
            
            const style = this.currentComponent.getStyle();
            
            // Update animation controls
            if (style['transition-duration']) {
                const duration = parseFloat(style['transition-duration']);
                const durationInput = document.getElementById('anim-duration');
                if (durationInput) {
                    durationInput.value = duration;
                    durationInput.nextElementSibling.textContent = duration + 's';
                }
            }
            
            // Update other controls based on current styles
            this.updateAllPreviews();
        }

        updateAllPreviews() {
            this.updateFlexPreview();
            this.updateGridPreview();
            this.updateTextShadow();
            this.updateBoxShadow();
            this.updateBorderRadius();
            this.updateBackdropFilter();
            this.updateGradient();
        }

        updateFlexPreview() {
            const preview = document.getElementById('flex-preview');
            if (!preview) return;
            
            const direction = document.getElementById('flex-direction')?.value || 'row';
            const justify = document.getElementById('flex-justify')?.value || 'flex-start';
            const align = document.getElementById('flex-align')?.value || 'stretch';
            
            preview.style.flexDirection = direction;
            preview.style.justifyContent = justify;
            preview.style.alignItems = align;
        }

        updateGridPreview() {
            const preview = document.getElementById('grid-preview');
            if (!preview) return;
            
            const columns = document.getElementById('grid-columns')?.value || 3;
            const gap = document.getElementById('grid-gap')?.value || 10;
            
            preview.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
            preview.style.gap = gap + 'px';
        }

        updateTextShadow() {
            const preview = document.getElementById('text-shadow-preview');
            if (!preview) return;
            
            const x = document.getElementById('text-shadow-x')?.value || 0;
            const y = document.getElementById('text-shadow-y')?.value || 0;
            const blur = document.getElementById('text-shadow-blur')?.value || 0;
            const color = document.getElementById('text-shadow-color')?.value || '#000000';
            
            preview.style.textShadow = `${x}px ${y}px ${blur}px ${color}`;
        }

        updateBoxShadow() {
            const preview = document.getElementById('box-shadow-preview');
            if (!preview) return;
            
            const x = document.getElementById('box-shadow-x')?.value || 0;
            const y = document.getElementById('box-shadow-y')?.value || 0;
            const blur = document.getElementById('box-shadow-blur')?.value || 0;
            const spread = document.getElementById('box-shadow-spread')?.value || 0;
            const color = document.getElementById('box-shadow-color')?.value || '#000000';
            const opacity = document.getElementById('box-shadow-opacity')?.value || 0.3;
            
            const rgbaColor = this.hexToRgba(color, opacity);
            preview.style.boxShadow = `${x}px ${y}px ${blur}px ${spread}px ${rgbaColor}`;
        }

        updateBorderRadius() {
            const preview = document.getElementById('radius-preview');
            if (!preview) return;
            
            const tl = document.getElementById('radius-tl')?.value || 0;
            const tr = document.getElementById('radius-tr')?.value || 0;
            const br = document.getElementById('radius-br')?.value || 0;
            const bl = document.getElementById('radius-bl')?.value || 0;
            
            preview.style.borderRadius = `${tl}px ${tr}px ${br}px ${bl}px`;
        }

        updateBackdropFilter() {
            const preview = document.getElementById('filter-preview');
            if (!preview) return;
            
            const blur = document.getElementById('backdrop-blur')?.value || 0;
            const brightness = document.getElementById('backdrop-brightness')?.value || 100;
            const contrast = document.getElementById('backdrop-contrast')?.value || 100;
            const saturate = document.getElementById('backdrop-saturate')?.value || 100;
            
            preview.style.backdropFilter = `blur(${blur}px) brightness(${brightness}%) contrast(${contrast}%) saturate(${saturate}%)`;
        }

        updateGradient() {
            const preview = document.getElementById('gradient-preview');
            if (!preview) return;
            
            const type = document.getElementById('gradient-type')?.value || 'linear';
            const direction = document.getElementById('gradient-direction')?.value || 'to right';
            
            // Get gradient stops
            const stops = [];
            document.querySelectorAll('.gradient-stop').forEach(stop => {
                const color = stop.querySelector('input[type="color"]').value;
                const position = stop.querySelector('input[type="range"]').value;
                stops.push(`${color} ${position}%`);
            });
            
            if (type === 'linear') {
                preview.style.background = `linear-gradient(${direction}, ${stops.join(', ')})`;
            } else if (type === 'radial') {
                preview.style.background = `radial-gradient(circle, ${stops.join(', ')})`;
            }
        }

        applyHoverEffect(effect) {
            if (!this.currentComponent) return;
            
            const effects = {
                scale: 'transform: scale(1.1);',
                rotate: 'transform: rotate(5deg);',
                glow: 'box-shadow: 0 0 20px rgba(0,0,0,0.3);',
                slide: 'transform: translateX(10px);'
            };
            
            const hoverStyle = effects[effect] || '';
            this.currentComponent.setStyle({ ':hover': hoverStyle });
            this.editor.refresh();
        }

        applyFontPairing(pairType) {
            if (!this.currentComponent) return;
            
            const pairings = {
                modern: {
                    'font-family': '"Inter", sans-serif',
                    'font-weight': '400'
                },
                classic: {
                    'font-family': '"Playfair Display", serif',
                    'font-weight': '400'
                },
                minimal: {
                    'font-family': '"Montserrat", sans-serif',
                    'font-weight': '300'
                }
            };
            
            const pairing = pairings[pairType];
            if (pairing) {
                Object.entries(pairing).forEach(([property, value]) => {
                    this.updateStyle(property, value);
                });
            }
        }

        hexToRgba(hex, alpha) {
            const r = parseInt(hex.slice(1, 3), 16);
            const g = parseInt(hex.slice(3, 5), 16);
            const b = parseInt(hex.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }

        loadPresets() {
            // Load common presets for quick access
            this.presets = {
                animations: {
                    fadeIn: { 'opacity': '0', 'animation': 'fadeIn 0.5s ease-in forwards' },
                    slideIn: { 'transform': 'translateX(-100%)', 'animation': 'slideIn 0.5s ease-out forwards' },
                    bounce: { 'animation': 'bounce 0.6s ease-in-out' }
                },
                effects: {
                    glass: { 'backdrop-filter': 'blur(10px)', 'background': 'rgba(255,255,255,0.1)' },
                    shadow: { 'box-shadow': '0 10px 25px rgba(0,0,0,0.15)' },
                    gradient: { 'background': 'linear-gradient(45deg, #3ECDC1, #2bb8ad)' }
                }
            };
        }

        exportStyles() {
            if (!this.currentComponent) return;
            
            const styles = this.currentComponent.getStyle();
            const dataStr = JSON.stringify(styles, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = 'component-styles.json';
            link.click();
        }

        importStyles(file) {
            if (!this.currentComponent) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const styles = JSON.parse(e.target.result);
                    this.currentComponent.setStyle(styles);
                    this.editor.refresh();
                } catch (error) {
                    console.error('Error importing styles:', error);
                }
            };
            reader.readAsText(file);
        }
    }

    // Initialize when GrapesJS is ready
    if (typeof grapesjs !== 'undefined') {
        if (grapesjs.editors) {
            // GrapesJS is already loaded
            const editor = grapesjs.editors[0] || window.editor;
            if (editor) {
                window.advancedStyleEditor = new AdvancedStyleEditor(editor);
            }
        } else {
            // Wait for GrapesJS to load
            document.addEventListener('grapesjs:ready', () => {
                const editor = grapesjs.editors[0] || window.editor;
                if (editor) {
                    window.advancedStyleEditor = new AdvancedStyleEditor(editor);
                }
            });
        }
    }

    // Export for use in other scripts
    window.AdvancedStyleEditor = AdvancedStyleEditor;

})(); 