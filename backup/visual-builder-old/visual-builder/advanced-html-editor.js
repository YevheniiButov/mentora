/**
 * Advanced HTML Editor для Visual Builder
 * Продвинутый редактор HTML с возможностью импорта и редактирования любого HTML
 */

class AdvancedHTMLEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentEditingElement = null;
        this.init();
    }

    /**
     * Инициализация редактора
     */
    init() {
        console.info('🎨 Advanced HTML Editor инициализирован');
    }

    /**
     * Импорт любого HTML и превращение в редактируемые элементы
     */
    importHTML(htmlString) {
        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlString, 'text/html');
            
            // Делаем все элементы редактируемыми
            doc.body.querySelectorAll('*').forEach(element => {
                this.makeElementEditable(element);
            });
            
            return doc.body.innerHTML;
        } catch (error) {
            console.error('Ошибка импорта HTML:', error);
            this.vb.showNotification('Ошибка импорта HTML', 'error');
            return htmlString;
        }
    }

    /**
     * Превращение любого элемента в редактируемый
     */
    makeElementEditable(element) {
        try {
            // Сохраняем оригинальные стили
            const computedStyles = window.getComputedStyle(element);
            element.dataset.originalStyles = JSON.stringify({
                position: computedStyles.position,
                display: computedStyles.display,
                width: computedStyles.width,
                height: computedStyles.height,
                margin: computedStyles.margin,
                padding: computedStyles.padding,
                background: computedStyles.background,
                border: computedStyles.border,
                fontFamily: computedStyles.fontFamily,
                fontSize: computedStyles.fontSize,
                color: computedStyles.color
            });

            // Добавляем класс для редактирования
            element.classList.add('draggable-element');
            element.dataset.id = `imported_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            element.dataset.type = 'imported';
            
            // Добавляем контролы
            this.addEditingControls(element);
            
            // Делаем перетаскиваемым
            if (this.vb.setupElementEvents) {
                this.vb.setupElementEvents(element);
            }
            if (this.vb.addResizeHandles) {
                this.vb.addResizeHandles(element);
            }
            
            console.info('✅ Элемент сделан редактируемым:', element.tagName);
        } catch (error) {
            console.error('Ошибка создания редактируемого элемента:', error);
        }
    }

    /**
     * Добавление контролов редактирования
     */
    addEditingControls(element) {
        const controls = document.createElement('div');
        controls.className = 'element-controls';
        controls.innerHTML = `
            <div class="control-group">
                <button class="control-btn" onclick="visualBuilder.htmlEditor.editElementStyles(this)" title="Стили">
                    <i class="bi bi-palette"></i>
                </button>
                <button class="control-btn" onclick="visualBuilder.htmlEditor.editElementHTML(this)" title="HTML">
                    <i class="bi bi-code"></i>
                </button>
                <button class="control-btn" onclick="visualBuilder.htmlEditor.makeResponsive(this)" title="Адаптив">
                    <i class="bi bi-phone"></i>
                </button>
            </div>
            <div class="control-group">
                <button class="control-btn secondary" onclick="visualBuilder.duplicateElement(this)" title="Дублировать">
                    <i class="bi bi-files"></i>
                </button>
                <button class="control-btn danger" onclick="visualBuilder.deleteElement(this)" title="Удалить">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        element.appendChild(controls);
    }

    /**
     * Редактирование HTML элемента
     */
    editElementHTML(controlBtn) {
        const element = controlBtn.closest('.draggable-element');
        this.currentEditingElement = element;
        const modal = this.createHTMLEditorModal(element);
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'flex';
        });
    }

    /**
     * Модальное окно для редактирования HTML
     */
    createHTMLEditorModal(element) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay html-editor-overlay';
        modal.innerHTML = `
            <div class="modal html-editor-modal">
                <div class="modal-header">
                    <h3>
                        <i class="bi bi-code"></i>
                        Редактирование HTML
                    </h3>
                    <button class="btn btn-ghost" onclick="this.closest('.modal-overlay').remove()">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="html-editor-container">
                        <div class="editor-tabs">
                            <button class="tab-btn active" data-tab="html">
                                <i class="bi bi-code"></i> HTML
                            </button>
                            <button class="tab-btn" data-tab="css">
                                <i class="bi bi-palette"></i> CSS
                            </button>
                            <button class="tab-btn" data-tab="preview">
                                <i class="bi bi-eye"></i> Предпросмотр
                            </button>
                        </div>
                        <div class="editor-content">
                            <div class="tab-content active" data-tab="html">
                                <div class="editor-toolbar">
                                    <button class="btn btn-sm" onclick="visualBuilder.htmlEditor.formatHTML()">
                                        <i class="bi bi-indent"></i> Форматировать
                                    </button>
                                    <button class="btn btn-sm" onclick="visualBuilder.htmlEditor.validateHTML()">
                                        <i class="bi bi-check-circle"></i> Проверить
                                    </button>
                                </div>
                                <textarea class="html-textarea" rows="20" placeholder="Введите HTML код...">${this.escapeHTML(element.innerHTML)}</textarea>
                            </div>
                            <div class="tab-content" data-tab="css">
                                <div class="editor-toolbar">
                                    <button class="btn btn-sm" onclick="visualBuilder.htmlEditor.formatCSS()">
                                        <i class="bi bi-indent"></i> Форматировать
                                    </button>
                                    <button class="btn btn-sm" onclick="visualBuilder.htmlEditor.addCSSRule()">
                                        <i class="bi bi-plus"></i> Добавить правило
                                    </button>
                                </div>
                                <textarea class="css-textarea" rows="20" placeholder="Введите CSS стили...">${this.getElementCSS(element)}</textarea>
                            </div>
                            <div class="tab-content" data-tab="preview">
                                <div class="preview-toolbar">
                                    <button class="btn btn-sm" onclick="visualBuilder.htmlEditor.refreshPreview()">
                                        <i class="bi bi-arrow-clockwise"></i> Обновить
                                    </button>
                                    <select class="preview-device-select">
                                        <option value="desktop">Desktop</option>
                                        <option value="tablet">Tablet</option>
                                        <option value="mobile">Mobile</option>
                                    </select>
                                </div>
                                <div class="preview-container">
                                    <div class="preview-frame">
                                        <iframe class="preview-iframe"></iframe>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="footer-info">
                        <span class="element-info">
                            <i class="bi bi-tag"></i>
                            ${element.tagName.toLowerCase()}
                        </span>
                        <span class="element-id">
                            <i class="bi bi-hash"></i>
                            ${element.dataset.id}
                        </span>
                    </div>
                    <div class="footer-actions">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                            Отмена
                        </button>
                        <button class="btn btn-primary" onclick="visualBuilder.htmlEditor.applyHTMLChanges(this)">
                            <i class="bi bi-check"></i>
                            Применить
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Настраиваем переключение табов
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.onclick = () => this.switchTab(modal, btn.dataset.tab);
        });

        // Инициализируем предпросмотр
        this.initializePreview(modal);

        return modal;
    }

    /**
     * Переключение табов
     */
    switchTab(modal, tabName) {
        // Убираем активный класс со всех табов и контента
        modal.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        modal.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Добавляем активный класс выбранному табу и контенту
        modal.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        modal.querySelector(`.tab-content[data-tab="${tabName}"]`).classList.add('active');
        
        // Обновляем предпросмотр если переключились на него
        if (tabName === 'preview') {
            this.refreshPreview();
        }
    }

    /**
     * Инициализация предпросмотра
     */
    initializePreview(modal) {
        const iframe = modal.querySelector('.preview-iframe');
        const htmlTextarea = modal.querySelector('.html-textarea');
        const cssTextarea = modal.querySelector('.css-textarea');
        
        // Создаем HTML для предпросмотра
        const previewHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: 'Inter', sans-serif; line-height: 1.6; }
                    ${cssTextarea.value}
                </style>
            </head>
            <body>
                ${htmlTextarea.value}
            </body>
            </html>
        `;
        
        iframe.srcdoc = previewHTML;
    }

    /**
     * Обновление предпросмотра
     */
    refreshPreview() {
        const modal = document.querySelector('.html-editor-modal');
        if (!modal) return;
        
        const iframe = modal.querySelector('.preview-iframe');
        const htmlTextarea = modal.querySelector('.html-textarea');
        const cssTextarea = modal.querySelector('.css-textarea');
        
        const previewHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: 'Inter', sans-serif; line-height: 1.6; }
                    ${cssTextarea.value}
                </style>
            </head>
            <body>
                ${htmlTextarea.value}
            </body>
            </html>
        `;
        
        iframe.srcdoc = previewHTML;
    }

    /**
     * Получение CSS стилей элемента
     */
    getElementCSS(element) {
        try {
            const styles = window.getComputedStyle(element);
            const cssText = `
/* Позиционирование */
position: ${styles.position};
top: ${styles.top};
left: ${styles.left};
width: ${styles.width};
height: ${styles.height};
z-index: ${styles.zIndex};

/* Отступы */
margin: ${styles.margin};
margin-top: ${styles.marginTop};
margin-right: ${styles.marginRight};
margin-bottom: ${styles.marginBottom};
margin-left: ${styles.marginLeft};

padding: ${styles.padding};
padding-top: ${styles.paddingTop};
padding-right: ${styles.paddingRight};
padding-bottom: ${styles.paddingBottom};
padding-left: ${styles.paddingLeft};

/* Фон и границы */
background: ${styles.background};
background-color: ${styles.backgroundColor};
background-image: ${styles.backgroundImage};
background-size: ${styles.backgroundSize};
background-position: ${styles.backgroundPosition};

border: ${styles.border};
border-width: ${styles.borderWidth};
border-style: ${styles.borderStyle};
border-color: ${styles.borderColor};
border-radius: ${styles.borderRadius};

/* Текст */
font-family: ${styles.fontFamily};
font-size: ${styles.fontSize};
font-weight: ${styles.fontWeight};
font-style: ${styles.fontStyle};
line-height: ${styles.lineHeight};
color: ${styles.color};
text-align: ${styles.textAlign};
text-decoration: ${styles.textDecoration};
text-transform: ${styles.textTransform};

/* Эффекты */
box-shadow: ${styles.boxShadow};
opacity: ${styles.opacity};
transform: ${styles.transform};
filter: ${styles.filter};
transition: ${styles.transition};

/* Flexbox */
display: ${styles.display};
flex-direction: ${styles.flexDirection};
justify-content: ${styles.justifyContent};
align-items: ${styles.alignItems};
flex-wrap: ${styles.flexWrap};

/* Grid */
grid-template-columns: ${styles.gridTemplateColumns};
grid-template-rows: ${styles.gridTemplateRows};
grid-gap: ${styles.gridGap};
            `.trim();
            
            return cssText;
        } catch (error) {
            console.error('Ошибка получения CSS:', error);
            return '/* Ошибка получения стилей */';
        }
    }

    /**
     * Применение изменений HTML
     */
    applyHTMLChanges(btn) {
        try {
            const modal = btn.closest('.modal-overlay');
            const htmlTextarea = modal.querySelector('.html-textarea');
            const cssTextarea = modal.querySelector('.css-textarea');
            
            const element = this.currentEditingElement;
            if (!element) {
                this.vb.showNotification('Элемент не найден', 'error');
                return;
            }
            
            // Применяем HTML
            element.innerHTML = this.unescapeHTML(htmlTextarea.value);
            
            // Применяем CSS
            this.applyCSSToElement(element, cssTextarea.value);
            
            // Переустанавливаем события
            if (this.vb.setupElementEvents) {
                this.vb.setupElementEvents(element);
            }
            if (this.vb.addResizeHandles) {
                this.vb.addResizeHandles(element);
            }
            
            // Добавляем в историю
            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }
            
            // Обновляем UI
            if (this.vb.updateLayersPanel) {
                this.vb.updateLayersPanel();
            }
            
            modal.remove();
            this.vb.showNotification('HTML изменения применены', 'success');
            
            console.info('✅ HTML изменения применены к элементу:', element.tagName);
        } catch (error) {
            console.error('Ошибка применения HTML изменений:', error);
            this.vb.showNotification('Ошибка применения изменений', 'error');
        }
    }

    /**
     * Применение CSS к элементу
     */
    applyCSSToElement(element, cssText) {
        try {
            const rules = cssText.split(';').filter(rule => rule.trim());
            
            rules.forEach(rule => {
                const [property, value] = rule.split(':').map(s => s.trim());
                if (property && value && value !== 'undefined' && value !== 'null') {
                    element.style.setProperty(property, value);
                }
            });
            
            console.info('✅ CSS применен к элементу:', element.tagName);
        } catch (error) {
            console.error('Ошибка применения CSS:', error);
        }
    }

    /**
     * Форматирование HTML
     */
    formatHTML() {
        const modal = document.querySelector('.html-editor-modal');
        if (!modal) return;
        
        const textarea = modal.querySelector('.html-textarea');
        try {
            // Простое форматирование HTML
            let html = textarea.value;
            html = html.replace(/></g, '>\n<');
            html = html.replace(/\n\s*\n/g, '\n');
            textarea.value = html;
            
            this.vb.showNotification('HTML отформатирован', 'success');
        } catch (error) {
            console.error('Ошибка форматирования HTML:', error);
            this.vb.showNotification('Ошибка форматирования', 'error');
        }
    }

    /**
     * Форматирование CSS
     */
    formatCSS() {
        const modal = document.querySelector('.html-editor-modal');
        if (!modal) return;
        
        const textarea = modal.querySelector('.css-textarea');
        try {
            let css = textarea.value;
            css = css.replace(/;/g, ';\n');
            css = css.replace(/\n\s*\n/g, '\n');
            textarea.value = css;
            
            this.vb.showNotification('CSS отформатирован', 'success');
        } catch (error) {
            console.error('Ошибка форматирования CSS:', error);
            this.vb.showNotification('Ошибка форматирования', 'error');
        }
    }

    /**
     * Валидация HTML
     */
    validateHTML() {
        const modal = document.querySelector('.html-editor-modal');
        if (!modal) return;
        
        const textarea = modal.querySelector('.html-textarea');
        const html = textarea.value;
        
        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            const errors = [];
            if (doc.querySelector('parsererror')) {
                errors.push('Ошибка парсинга HTML');
            }
            
            // Проверяем незакрытые теги
            const openTags = (html.match(/<[^/][^>]*>/g) || []).length;
            const closeTags = (html.match(/<\/[^>]*>/g) || []).length;
            
            if (openTags !== closeTags) {
                errors.push('Несбалансированные теги');
            }
            
            if (errors.length === 0) {
                this.vb.showNotification('HTML валиден', 'success');
            } else {
                this.vb.showNotification(`Ошибки: ${errors.join(', ')}`, 'warning');
            }
        } catch (error) {
            console.error('Ошибка валидации HTML:', error);
            this.vb.showNotification('Ошибка валидации', 'error');
        }
    }

    /**
     * Добавление CSS правила
     */
    addCSSRule() {
        const modal = document.querySelector('.html-editor-modal');
        if (!modal) return;
        
        const textarea = modal.querySelector('.css-textarea');
        const newRule = `
/* Новое правило */
.new-rule {
    /* Добавьте стили здесь */
}
        `;
        
        textarea.value += newRule;
        this.vb.showNotification('CSS правило добавлено', 'info');
    }

    /**
     * Утилиты
     */
    escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    unescapeHTML(text) {
        const div = document.createElement('div');
        div.innerHTML = text;
        return div.textContent;
    }

    /**
     * Импорт HTML со страницы
     */
    importExistingHTML() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.html,.htm';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const htmlContent = this.importHTML(e.target.result);
                        if (this.vb.setCanvasContent) {
                            this.vb.setCanvasContent(htmlContent);
                        }
                        if (this.vb.updateLayersPanel) {
                            this.vb.updateLayersPanel();
                        }
                        this.vb.showNotification('HTML импортирован и готов к редактированию', 'success');
                    } catch (error) {
                        console.error('Ошибка импорта файла:', error);
                        this.vb.showNotification('Ошибка импорта HTML файла', 'error');
                    }
                };
                reader.readAsText(file);
            }
        };
        
        input.click();
    }

    /**
     * Экспорт HTML
     */
    exportHTML() {
        const elements = this.vb.dom.canvas.querySelectorAll('.draggable-element');
        let html = '';
        
        elements.forEach(element => {
            // Убираем контролы редактирования
            const clone = element.cloneNode(true);
            const controls = clone.querySelector('.element-controls');
            if (controls) {
                controls.remove();
            }
            
            // Убираем resize handles
            const handles = clone.querySelector('.resize-handles');
            if (handles) {
                handles.remove();
            }
            
            // Убираем классы редактирования
            clone.classList.remove('draggable-element', 'selected', 'dragging');
            
            html += clone.outerHTML + '\n';
        });
        
        return html;
    }
}

// Экспорт класса
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedHTMLEditor;
} 