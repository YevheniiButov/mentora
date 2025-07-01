/**
 * Universal HTML Editor для Visual Builder
 * Система импорта и редактирования существующего HTML
 */

class UniversalHTMLEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentEditingElement = null;
        this.importedElements = new Map();
        this.init();
    }

    init() {
        console.info("🌐 Universal HTML Editor инициализирован");
    }

    importHTML(htmlContent) {
        try {
            console.info("📥 Импорт HTML контента...");
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, "text/html");
            const editableElements = this.convertToEditableElements(doc.body);
            this.addElementsToCanvas(editableElements);
            this.vb.showNotification("HTML успешно импортирован", "success");
            return editableElements;
        } catch (error) {
            console.error("❌ Ошибка импорта HTML:", error);
            this.vb.showNotification("Ошибка импорта HTML: " + error.message, "error");
            return [];
        }
    }

    convertToEditableElements(container) {
        const editableElements = [];
        container.querySelectorAll("*").forEach(element => {
            try {
                const editableElement = this.makeEditable(element);
                if (editableElement) {
                    editableElements.push(editableElement);
                }
            } catch (error) {
                console.warn("Ошибка конвертации элемента:", element.tagName, error);
            }
        });
        console.info(`✅ Конвертировано ${editableElements.length} элементов`);
        return editableElements;
    }

    makeEditable(element) {
        if (this.isServiceElement(element)) {
            return null;
        }

        try {
            this.preserveStyles(element);
            element.classList.add("draggable-element", "imported-element");
            element.dataset.id = `imported_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            element.dataset.type = "imported";
            element.dataset.originalTag = element.tagName.toLowerCase();
            this.addControls(element);
            this.setupElementInteractions(element);
            
            this.importedElements.set(element.dataset.id, {
                element: element,
                originalHTML: element.outerHTML,
                originalStyles: element.dataset.originalStyles
            });
            
            return element;
        } catch (error) {
            console.error("Ошибка создания редактируемого элемента:", error);
            return null;
        }
    }

    preserveStyles(element) {
        try {
            const computedStyles = window.getComputedStyle(element);
            const stylesToPreserve = {
                position: computedStyles.position,
                width: computedStyles.width,
                height: computedStyles.height,
                margin: computedStyles.margin,
                padding: computedStyles.padding,
                fontFamily: computedStyles.fontFamily,
                fontSize: computedStyles.fontSize,
                color: computedStyles.color,
                backgroundColor: computedStyles.backgroundColor,
                border: computedStyles.border,
                display: computedStyles.display
            };
            element.dataset.originalStyles = JSON.stringify(stylesToPreserve);
        } catch (error) {
            console.warn("Ошибка сохранения стилей:", error);
        }
    }

    addControls(element) {
        const existingControls = element.querySelector(".element-controls");
        if (existingControls) {
            existingControls.remove();
        }

        const controls = document.createElement("div");
        controls.className = "element-controls";
        controls.innerHTML = `
            <div class="control-group">
                <button class="control-btn" onclick="visualBuilder.universalHTMLEditor.editElementStyles(this)" title="Стили">
                    <i class="bi bi-palette"></i>
                </button>
                <button class="control-btn" onclick="visualBuilder.universalHTMLEditor.editElementHTML(this)" title="HTML">
                    <i class="bi bi-code"></i>
                </button>
                <button class="control-btn" onclick="visualBuilder.universalHTMLEditor.editElementCSS(this)" title="CSS">
                    <i class="bi bi-brush"></i>
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

    setupElementInteractions(element) {
        if (this.vb.setupElementEvents) {
            this.vb.setupElementEvents(element);
        }
        if (this.vb.addResizeHandles) {
            this.vb.addResizeHandles(element);
        }
        this.addDragHandle(element);
    }

    addDragHandle(element) {
        const dragHandle = document.createElement("div");
        dragHandle.className = "drag-handle";
        dragHandle.innerHTML = "<i class=\"bi bi-grip-vertical\"></i>";
        dragHandle.title = "Перетащить элемент";
        element.appendChild(dragHandle);
    }

    isServiceElement(element) {
        const serviceTags = ["script", "style", "meta", "link", "title", "head"];
        const serviceClasses = ["element-controls", "drag-handle", "resize-handles"];
        
        return serviceTags.includes(element.tagName.toLowerCase()) ||
               serviceClasses.some(cls => element.classList.contains(cls)) ||
               element.closest(".element-controls, .drag-handle, .resize-handles");
    }

    addElementsToCanvas(elements) {
        if (!this.vb.dom.canvas) {
            console.error("Canvas не найден");
            return;
        }

        const emptyState = this.vb.dom.canvas.querySelector(".canvas-empty");
        if (emptyState) {
            emptyState.remove();
        }

        elements.forEach(element => {
            this.vb.dom.canvas.appendChild(element);
        });

        if (this.vb.updateLayersPanel) {
            this.vb.updateLayersPanel();
        }
        if (this.vb.addToHistory) {
            this.vb.addToHistory();
        }
    }

    editElementStyles(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        if (this.vb.advancedCSSEditor) {
            this.vb.advancedCSSEditor.openStylePanel(element);
        } else {
            this.vb.showNotification("CSS Editor не загружен", "error");
        }
    }

    editElementHTML(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        this.currentEditingElement = element;
        this.showHTMLEditor(element);
    }

    editElementCSS(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        if (this.vb.advancedCSSEditor) {
            this.vb.advancedCSSEditor.editElementCSS(element);
        } else {
            this.vb.showNotification("CSS Editor не загружен", "error");
        }
    }

    editGrid(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        if (this.vb.gridEditor) {
            this.vb.gridEditor.editGrid(element);
        } else {
            this.vb.showNotification("Grid Editor не загружен", "error");
        }
    }

    editFlexbox(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        if (this.vb.flexboxEditor) {
            this.vb.flexboxEditor.editFlexbox(element);
        } else {
            this.vb.showNotification("Flexbox Editor не загружен", "error");
        }
    }

    makeResponsive(controlBtn) {
        const element = controlBtn.closest(".draggable-element");
        if (this.vb.responsiveDesign) {
            this.vb.responsiveDesign.makeElementResponsive(element);
            this.vb.showNotification("Элемент сделан адаптивным", "success");
        } else {
            this.vb.showNotification("Responsive Design не загружен", "error");
        }
    }

    showHTMLEditor(element) {
        const modal = this.createHTMLEditorModal(element);
        document.body.appendChild(modal);
        requestAnimationFrame(() => {
            modal.style.display = "flex";
        });
    }

    createHTMLEditorModal(element) {
        const modal = document.createElement("div");
        modal.className = "modal-overlay universal-html-editor-overlay";
        modal.innerHTML = `
            <div class="modal universal-html-editor-modal">
                <div class="modal-header">
                    <h3>
                        <i class="bi bi-code"></i>
                        Редактирование HTML
                    </h3>
                    <button class="btn btn-ghost" onclick="this.closest(\".modal-overlay\").remove()">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="modal-body">
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
                                <button class="btn btn-sm" onclick="visualBuilder.universalHTMLEditor.formatHTML()">
                                    <i class="bi bi-indent"></i> Форматировать
                                </button>
                                <button class="btn btn-sm" onclick="visualBuilder.universalHTMLEditor.validateHTML()">
                                    <i class="bi bi-check-circle"></i> Проверить
                                </button>
                            </div>
                            <textarea class="html-textarea" rows="20" placeholder="Введите HTML код...">${this.escapeHTML(element.innerHTML)}</textarea>
                        </div>
                        <div class="tab-content" data-tab="css">
                            <div class="editor-toolbar">
                                <button class="btn btn-sm" onclick="visualBuilder.universalHTMLEditor.formatCSS()">
                                    <i class="bi bi-indent"></i> Форматировать
                                </button>
                                <button class="btn btn-sm" onclick="visualBuilder.universalHTMLEditor.addCSSRule()">
                                    <i class="bi bi-plus"></i> Добавить правило
                                </button>
                            </div>
                            <textarea class="css-textarea" rows="20" placeholder="Введите CSS стили...">${this.getElementCSS(element)}</textarea>
                        </div>
                        <div class="tab-content" data-tab="preview">
                            <div class="preview-toolbar">
                                <button class="btn btn-sm" onclick="visualBuilder.universalHTMLEditor.refreshPreview()">
                                    <i class="bi bi-arrow-clockwise"></i> Обновить
                                </button>
                            </div>
                            <div class="preview-container">
                                <div class="preview-frame">
                                    <iframe class="preview-iframe"></iframe>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest(\".modal-overlay\").remove()">
                        Отмена
                    </button>
                    <button class="btn btn-primary" onclick="visualBuilder.universalHTMLEditor.applyChanges(this)">
                        Применить изменения
                    </button>
                </div>
            </div>
        `;

        this.setupHTMLEditorEvents(modal, element);
        return modal;
    }

    setupHTMLEditorEvents(modal, element) {
        const tabBtns = modal.querySelectorAll(".tab-btn");
        const tabContents = modal.querySelectorAll(".tab-content");
        
        tabBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                const tabName = btn.dataset.tab;
                tabBtns.forEach(b => b.classList.remove("active"));
                tabContents.forEach(c => c.classList.remove("active"));
                btn.classList.add("active");
                modal.querySelector(`[data-tab="${tabName}"]`).classList.add("active");
                
                if (tabName === "preview") {
                    this.initializePreview(modal, element);
                }
            });
        });
    }

    initializePreview(modal, element) {
        const iframe = modal.querySelector(".preview-iframe");
        const htmlTextarea = modal.querySelector(".html-textarea");
        const cssTextarea = modal.querySelector(".css-textarea");
        
        const html = htmlTextarea.value;
        const css = cssTextarea.value;
        
        const previewHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    ${css}
                </style>
            </head>
            <body>
                ${html}
            </body>
            </html>
        `;
        
        iframe.srcdoc = previewHTML;
    }

    refreshPreview() {
        const modal = document.querySelector(".universal-html-editor-overlay");
        if (modal) {
            const element = this.currentEditingElement;
            this.initializePreview(modal, element);
        }
    }

    getElementCSS(element) {
        const styles = window.getComputedStyle(element);
        let css = "";
        
        const cssProperties = [
            "position", "top", "left", "right", "bottom", "z-index",
            "width", "height", "min-width", "min-height", "max-width", "max-height",
            "margin", "padding", "border", "border-radius",
            "background", "background-color", "background-image",
            "font-family", "font-size", "font-weight", "color", "text-align",
            "display", "flex-direction", "justify-content", "align-items",
            "grid-template-columns", "grid-template-rows", "grid-gap",
            "box-shadow", "opacity", "transform", "transition"
        ];
        
        cssProperties.forEach(property => {
            const value = styles.getPropertyValue(property);
            if (value && value !== "initial" && value !== "normal") {
                css += `${property}: ${value};
`;
            }
        });
        
        return css;
    }

    applyChanges(btn) {
        const modal = btn.closest(".modal-overlay");
        const htmlTextarea = modal.querySelector(".html-textarea");
        const cssTextarea = modal.querySelector(".css-textarea");
        
        if (this.currentEditingElement) {
            this.currentEditingElement.innerHTML = this.unescapeHTML(htmlTextarea.value);
            this.applyCSSToElement(this.currentEditingElement, cssTextarea.value);
            
            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }
            if (this.vb.updateLayersPanel) {
                this.vb.updateLayersPanel();
            }
            
            this.vb.showNotification("Изменения применены", "success");
        }
        
        modal.remove();
    }

    applyCSSToElement(element, cssText) {
        try {
            const style = document.createElement("style");
            style.textContent = cssText;
            document.head.appendChild(style);
            
            const rules = style.sheet.cssRules;
            for (let i = 0; i < rules.length; i++) {
                const rule = rules[i];
                if (rule.selectorText) {
                    for (let j = 0; j < rule.style.length; j++) {
                        const property = rule.style[j];
                        const value = rule.style.getPropertyValue(property);
                        element.style.setProperty(property, value);
                    }
                }
            }
            
            document.head.removeChild(style);
        } catch (error) {
            console.error("Ошибка применения CSS:", error);
            this.vb.showNotification("Ошибка применения CSS", "error");
        }
    }

    formatHTML() {
        const modal = document.querySelector(".universal-html-editor-overlay");
        if (modal) {
            const textarea = modal.querySelector(".html-textarea");
            try {
                const formatted = this.formatHTMLCode(textarea.value);
                textarea.value = formatted;
                this.vb.showNotification("HTML отформатирован", "success");
            } catch (error) {
                this.vb.showNotification("Ошибка форматирования HTML", "error");
            }
        }
    }

    formatCSS() {
        const modal = document.querySelector(".universal-html-editor-overlay");
        if (modal) {
            const textarea = modal.querySelector(".css-textarea");
            try {
                const formatted = this.formatCSSCode(textarea.value);
                textarea.value = formatted;
                this.vb.showNotification("CSS отформатирован", "success");
            } catch (error) {
                this.vb.showNotification("Ошибка форматирования CSS", "error");
            }
        }
    }

    validateHTML() {
        const modal = document.querySelector(".universal-html-editor-overlay");
        if (modal) {
            const textarea = modal.querySelector(".html-textarea");
            try {
                const parser = new DOMParser();
                const doc = parser.parseFromString(textarea.value, "text/html");
                
                const errors = doc.querySelectorAll("parsererror");
                if (errors.length > 0) {
                    this.vb.showNotification("HTML содержит ошибки", "error");
                } else {
                    this.vb.showNotification("HTML валиден", "success");
                }
            } catch (error) {
                this.vb.showNotification("Ошибка валидации HTML", "error");
            }
        }
    }

    addCSSRule() {
        const modal = document.querySelector(".universal-html-editor-overlay");
        if (modal) {
            const textarea = modal.querySelector(".css-textarea");
            const newRule = "
/* Новое правило */
.element {
    
}
";
            textarea.value += newRule;
            textarea.focus();
            textarea.setSelectionRange(
                textarea.value.indexOf("/* Новое правило */"),
                textarea.value.length
            );
        }
    }

    formatHTMLCode(html) {
        return html
            .replace(/>\s*</g, ">
<")
            .replace(/
\s*
/g, "
")
            .trim();
    }

    formatCSSCode(css) {
        return css
            .replace(/\s*{\s*/g, " {
    ")
            .replace(/\s*}\s*/g, "
}
")
            .replace(/;\s*/g, ";
    ")
            .replace(/
\s*}/g, "
}");
    }

    escapeHTML(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    unescapeHTML(text) {
        const div = document.createElement("div");
        div.innerHTML = text;
        return div.textContent;
    }

    exportToCleanHTML() {
        const elements = this.vb.dom.canvas.querySelectorAll(".draggable-element");
        let html = "";
        
        elements.forEach(element => {
            const clone = element.cloneNode(true);
            const controls = clone.querySelector(".element-controls");
            if (controls) {
                controls.remove();
            }
            
            const handles = clone.querySelector(".resize-handles");
            if (handles) {
                handles.remove();
            }
            
            const dragHandle = clone.querySelector(".drag-handle");
            if (dragHandle) {
                dragHandle.remove();
            }
            
            clone.classList.remove("draggable-element", "selected", "dragging", "imported-element");
            html += clone.outerHTML + "
";
        });
        
        return html;
    }

    importHTMLFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const htmlContent = e.target.result;
                    const elements = this.importHTML(htmlContent);
                    resolve(elements);
                } catch (error) {
                    reject(error);
                }
            };
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    exportToHTMLFile(filename = "page.html") {
        const html = this.exportToCleanHTML();
        this.vb.downloadFile(html, filename, "text/html");
        this.vb.showNotification("HTML файл экспортирован", "success");
    }
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = UniversalHTMLEditor;
}
