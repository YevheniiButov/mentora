/**
 * Advanced CSS Editor для Visual Builder
 * Продвинутый редактор CSS с визуальными инструментами
 */

class AdvancedCSSEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentElement = null;
        this.styleSheet = null;
        this.styleHistory = [];
        this.currentRule = null;
        this.init();
    }

    init() {
        console.info("🎨 Advanced CSS Editor инициализирован");
        this.createStyleSheet();
    }

    createStyleSheet() {
        const style = document.createElement("style");
        style.id = "advanced-css-editor-styles";
        style.textContent = "/* Advanced CSS Editor Styles */";
        document.head.appendChild(style);
        this.styleSheet = style.sheet;
    }

    editCSS(selector, property, value) {
        try {
            let rule = this.findRule(selector);
            if (!rule) {
                rule = this.addRule(selector);
            }
            rule.style.setProperty(property, value);
            this.updatePreview();
            this.saveToHistory(selector, property, value);
            console.info(`✅ CSS обновлен: ${selector} { ${property}: ${value}; }`);
        } catch (error) {
            console.error("Ошибка редактирования CSS:", error);
            this.vb.showNotification("Ошибка редактирования CSS", "error");
        }
    }

    findRule(selector) {
        for (let i = 0; i < this.styleSheet.cssRules.length; i++) {
            const rule = this.styleSheet.cssRules[i];
            if (rule.selectorText === selector) {
                return rule;
            }
        }
        return null;
    }

    addRule(selector) {
        const index = this.styleSheet.cssRules.length;
        this.styleSheet.insertRule(`${selector} {}`, index);
        return this.styleSheet.cssRules[index];
    }

    deleteRule(selector) {
        for (let i = 0; i < this.styleSheet.cssRules.length; i++) {
            const rule = this.styleSheet.cssRules[i];
            if (rule.selectorText === selector) {
                this.styleSheet.deleteRule(i);
                break;
            }
        }
    }

    updatePreview() {
        if (this.currentElement) {
            this.applyStylesToElement(this.currentElement);
        }
    }

    applyStylesToElement(element) {
        const selector = this.getElementSelector(element);
        const rule = this.findRule(selector);
        
        if (rule) {
            for (let i = 0; i < rule.style.length; i++) {
                const property = rule.style[i];
                const value = rule.style.getPropertyValue(property);
                element.style.setProperty(property, value);
            }
        }
    }

    getElementSelector(element) {
        if (element.id) {
            return `#${element.id}`;
        } else if (element.className) {
            return `.${element.className.split(" ").join(".")}`;
        } else {
            return element.tagName.toLowerCase();
        }
    }

    saveToHistory(selector, property, value) {
        this.styleHistory.push({
            selector,
            property,
            value,
            timestamp: Date.now()
        });

        if (this.styleHistory.length > 100) {
            this.styleHistory.shift();
        }
    }

    openStylePanel(element) {
        this.currentElement = element;
        const panel = this.createStylePanel();
        
        const propertiesPanel = document.getElementById("propertiesPanel");
        if (propertiesPanel) {
            propertiesPanel.innerHTML = "";
            propertiesPanel.appendChild(panel);
            propertiesPanel.classList.add("active");
            propertiesPanel.style.display = "flex";
        }
        
        console.info("🎨 Панель CSS стилей открыта для элемента:", element.tagName);
    }

    createStylePanel() {
        const panel = document.createElement("div");
        panel.className = "advanced-css-panel";
        panel.innerHTML = `
            <div class="css-panel-header">
                <h3>
                    <i class="bi bi-palette2"></i>
                    CSS Редактор
                </h3>
                <div class="css-actions">
                    <button class="btn btn-sm" onclick="visualBuilder.advancedCSSEditor.resetStyles()" title="Сбросить">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button class="btn btn-sm" onclick="visualBuilder.advancedCSSEditor.saveStylePreset()" title="Сохранить пресет">
                        <i class="bi bi-bookmark"></i>
                    </button>
                </div>
            </div>
            <div class="css-categories">
                ${this.createCSSCategory("layout", "Макет", [
                    "display", "position", "top", "left", "right", "bottom", "width", "height", "z-index"
                ])}
                ${this.createCSSCategory("spacing", "Отступы", [
                    "margin-top", "margin-right", "margin-bottom", "margin-left",
                    "padding-top", "padding-right", "padding-bottom", "padding-left"
                ])}
                ${this.createCSSCategory("typography", "Типографика", [
                    "font-family", "font-size", "font-weight", "font-style", "line-height", 
                    "color", "text-align", "text-decoration", "text-transform", "letter-spacing"
                ])}
                ${this.createCSSCategory("background", "Фон", [
                    "background-color", "background-image", "background-size", "background-position",
                    "background-repeat", "background-attachment"
                ])}
                ${this.createCSSCategory("border", "Границы", [
                    "border-width", "border-style", "border-color", "border-radius",
                    "border-top", "border-right", "border-bottom", "border-left"
                ])}
                ${this.createCSSCategory("effects", "Эффекты", [
                    "box-shadow", "opacity", "transform", "filter", "transition", "animation"
                ])}
                ${this.createCSSCategory("flexbox", "Flexbox", [
                    "flex-direction", "justify-content", "align-items", "flex-wrap",
                    "flex-grow", "flex-shrink", "flex-basis", "align-self"
                ])}
                ${this.createCSSCategory("grid", "Grid", [
                    "grid-template-columns", "grid-template-rows", "grid-gap",
                    "grid-column", "grid-row", "justify-items", "align-items"
                ])}
            </div>
            <div class="css-presets">
                <h4>Пресеты стилей</h4>
                <div class="preset-grid">
                    ${this.createCSSPresets()}
                </div>
            </div>
            <div class="css-code-editor">
                <h4>CSS Код</h4>
                <textarea class="css-code-textarea" rows="10" placeholder="Введите CSS код...">${this.getCurrentElementCSS()}</textarea>
                <div class="css-code-actions">
                    <button class="btn btn-sm" onclick="visualBuilder.advancedCSSEditor.applyCSSCode()">
                        <i class="bi bi-check"></i> Применить
                    </button>
                    <button class="btn btn-sm" onclick="visualBuilder.advancedCSSEditor.formatCSSCode()">
                        <i class="bi bi-indent"></i> Форматировать
                    </button>
                </div>
            </div>
        `;

        this.setupCSSPanelEvents(panel);
        return panel;
    }

    createCSSCategory(id, title, properties) {
        const currentStyles = window.getComputedStyle(this.currentElement);
        
        return `
            <div class="css-category" data-category="${id}">
                <h4 class="category-title" onclick="visualBuilder.advancedCSSEditor.toggleCSSCategory(\"${id}\")">
                    <i class="bi bi-chevron-down category-icon"></i>
                    ${title}
                </h4>
                <div class="category-content">
                    ${properties.map(property => `
                        <div class="css-control">
                            <label>${this.getCSSPropertyLabel(property)}</label>
                            ${this.createCSSPropertyInput(property, currentStyles.getPropertyValue(property))}
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    createCSSPropertyInput(property, currentValue) {
        const inputId = `css_${property.replace(/[^a-zA-Z0-9]/g, "_")}`;
        
        switch (property) {
            case "color":
            case "background-color":
            case "border-color":
                return `
                    <div class="color-input-group">
                        <input type="color" class="css-input color-picker" 
                               id="${inputId}" data-property="${property}" 
                               value="${this.rgbToHex(currentValue)}">
                        <input type="text" class="css-input color-text" 
                               data-property="${property}" value="${currentValue}"
                               placeholder="auto">
                    </div>
                `;
            
            case "font-family":
                return `
                    <select class="css-input" id="${inputId}" data-property="${property}">
                        <option value="Inter" ${currentValue.includes("Inter") ? "selected" : ""}>Inter</option>
                        <option value="Arial" ${currentValue.includes("Arial") ? "selected" : ""}>Arial</option>
                        <option value="Helvetica" ${currentValue.includes("Helvetica") ? "selected" : ""}>Helvetica</option>
                        <option value="Georgia" ${currentValue.includes("Georgia") ? "selected" : ""}>Georgia</option>
                        <option value="Times New Roman" ${currentValue.includes("Times") ? "selected" : ""}>Times New Roman</option>
                        <option value="Roboto" ${currentValue.includes("Roboto") ? "selected" : ""}>Roboto</option>
                        <option value="Open Sans" ${currentValue.includes("Open Sans") ? "selected" : ""}>Open Sans</option>
                    </select>
                `;
            
            case "display":
                return `
                    <select class="css-input" id="${inputId}" data-property="${property}">
                        <option value="block" ${currentValue === "block" ? "selected" : ""}>Block</option>
                        <option value="inline" ${currentValue === "inline" ? "selected" : ""}>Inline</option>
                        <option value="inline-block" ${currentValue === "inline-block" ? "selected" : ""}>Inline Block</option>
                        <option value="flex" ${currentValue === "flex" ? "selected" : ""}>Flex</option>
                        <option value="grid" ${currentValue === "grid" ? "selected" : ""}>Grid</option>
                        <option value="none" ${currentValue === "none" ? "selected" : ""}>None</option>
                    </select>
                `;
            
            case "position":
                return `
                    <select class="css-input" id="${inputId}" data-property="${property}">
                        <option value="static" ${currentValue === "static" ? "selected" : ""}>Static</option>
                        <option value="relative" ${currentValue === "relative" ? "selected" : ""}>Relative</option>
                        <option value="absolute" ${currentValue === "absolute" ? "selected" : ""}>Absolute</option>
                        <option value="fixed" ${currentValue === "fixed" ? "selected" : ""}>Fixed</option>
                        <option value="sticky" ${currentValue === "sticky" ? "selected" : ""}>Sticky</option>
                    </select>
                `;
            
            case "text-align":
                return `
                    <select class="css-input" id="${inputId}" data-property="${property}">
                        <option value="left" ${currentValue === "left" ? "selected" : ""}>Left</option>
                        <option value="center" ${currentValue === "center" ? "selected" : ""}>Center</option>
                        <option value="right" ${currentValue === "right" ? "selected" : ""}>Right</option>
                        <option value="justify" ${currentValue === "justify" ? "selected" : ""}>Justify</option>
                    </select>
                `;
            
            case "font-weight":
                return `
                    <select class="css-input" id="${inputId}" data-property="${property}">
                        <option value="normal" ${currentValue === "normal" ? "selected" : ""}>Normal</option>
                        <option value="bold" ${currentValue === "bold" ? "selected" : ""}>Bold</option>
                        <option value="100" ${currentValue === "100" ? "selected" : ""}>100</option>
                        <option value="200" ${currentValue === "200" ? "selected" : ""}>200</option>
                        <option value="300" ${currentValue === "300" ? "selected" : ""}>300</option>
                        <option value="400" ${currentValue === "400" ? "selected" : ""}>400</option>
                        <option value="500" ${currentValue === "500" ? "selected" : ""}>500</option>
                        <option value="600" ${currentValue === "600" ? "selected" : ""}>600</option>
                        <option value="700" ${currentValue === "700" ? "selected" : ""}>700</option>
                        <option value="800" ${currentValue === "800" ? "selected" : ""}>800</option>
                        <option value="900" ${currentValue === "900" ? "selected" : ""}>900</option>
                    </select>
                `;
            
            default:
                return `
                    <input type="text" class="css-input" id="${inputId}" 
                           data-property="${property}" value="${currentValue}"
                           placeholder="auto">
                `;
        }
    }

    setupCSSPanelEvents(panel) {
        panel.querySelectorAll(".css-input").forEach(input => {
            input.addEventListener("change", (e) => {
                const property = e.target.dataset.property;
                const value = e.target.value;
                this.updateElementCSS(property, value);
            });

            input.addEventListener("input", (e) => {
                const property = e.target.dataset.property;
                const value = e.target.value;
                this.updateElementCSS(property, value);
            });
        });

        panel.querySelectorAll(".color-picker").forEach(picker => {
            picker.addEventListener("change", (e) => {
                const property = e.target.dataset.property;
                const value = e.target.value;
                const textInput = panel.querySelector(`[data-property="${property}"].color-text`);
                if (textInput) {
                    textInput.value = value;
                }
                this.updateElementCSS(property, value);
            });
        });

        panel.querySelectorAll(".color-text").forEach(textInput => {
            textInput.addEventListener("change", (e) => {
                const property = e.target.dataset.property;
                const value = e.target.value;
                const picker = panel.querySelector(`[data-property="${property}"].color-picker`);
                if (picker && this.isValidColor(value)) {
                    picker.value = value;
                }
                this.updateElementCSS(property, value);
            });
        });
    }

    updateElementCSS(property, value) {
        if (!this.currentElement) return;

        try {
            this.currentElement.style.setProperty(property, value);
            this.saveToHistory(this.getElementSelector(this.currentElement), property, value);
            this.updateCSSCode();
        } catch (error) {
            console.error("Ошибка обновления CSS:", error);
        }
    }

    updateCSSCode() {
        const textarea = document.querySelector(".css-code-textarea");
        if (textarea) {
            textarea.value = this.getCurrentElementCSS();
        }
    }

    getCurrentElementCSS() {
        if (!this.currentElement) return "";

        const selector = this.getElementSelector(this.currentElement);
        const styles = this.currentElement.style;
        let css = `${selector} {
`;
        
        for (let i = 0; i < styles.length; i++) {
            const property = styles[i];
            const value = styles.getPropertyValue(property);
            if (value) {
                css += `    ${property}: ${value};
`;
            }
        }
        
        css += "}";
        return css;
    }

    applyCSSCode() {
        const textarea = document.querySelector(".css-code-textarea");
        if (!textarea || !this.currentElement) return;

        try {
            const cssText = textarea.value;
            const selector = this.getElementSelector(this.currentElement);
            
            this.deleteRule(selector);
            const rule = this.addRule(selector);
            
            const cssProperties = this.parseCSSCode(cssText);
            Object.entries(cssProperties).forEach(([property, value]) => {
                rule.style.setProperty(property, value);
                this.currentElement.style.setProperty(property, value);
            });
            
            this.vb.showNotification("CSS код применен", "success");
        } catch (error) {
            console.error("Ошибка применения CSS кода:", error);
            this.vb.showNotification("Ошибка применения CSS кода", "error");
        }
    }

    parseCSSCode(cssText) {
        const properties = {};
        const ruleMatch = cssText.match(/\{([^}]+)\}/);
        
        if (ruleMatch) {
            const ruleContent = ruleMatch[1];
            const propertyMatches = ruleContent.match(/([^:]+):\s*([^;]+);/g);
            
            if (propertyMatches) {
                propertyMatches.forEach(match => {
                    const [property, value] = match.split(":").map(s => s.trim());
                    properties[property] = value.replace(";", "").trim();
                });
            }
        }
        
        return properties;
    }

    formatCSSCode() {
        const textarea = document.querySelector(".css-code-textarea");
        if (!textarea) return;

        try {
            const formatted = this.formatCSSText(textarea.value);
            textarea.value = formatted;
            this.vb.showNotification("CSS код отформатирован", "success");
        } catch (error) {
            this.vb.showNotification("Ошибка форматирования CSS", "error");
        }
    }

    formatCSSText(css) {
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
}")
            .trim();
    }

    toggleCSSCategory(categoryId) {
        const category = document.querySelector(`[data-category="${categoryId}"]`);
        if (category) {
            const content = category.querySelector(".category-content");
            const icon = category.querySelector(".category-icon");
            
            if (content.style.display === "none") {
                content.style.display = "block";
                icon.classList.remove("bi-chevron-right");
                icon.classList.add("bi-chevron-down");
            } else {
                content.style.display = "none";
                icon.classList.remove("bi-chevron-down");
                icon.classList.add("bi-chevron-right");
            }
        }
    }

    createCSSPresets() {
        const presets = [
            {
                name: "Карточка",
                styles: {
                    "background-color": "#ffffff",
                    "border": "1px solid #e0e0e0",
                    "border-radius": "8px",
                    "padding": "16px",
                    "box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
                }
            },
            {
                name: "Кнопка",
                styles: {
                    "background-color": "#007bff",
                    "color": "#ffffff",
                    "border": "none",
                    "border-radius": "4px",
                    "padding": "8px 16px",
                    "font-weight": "500",
                    "cursor": "pointer"
                }
            },
            {
                name: "Заголовок",
                styles: {
                    "font-size": "24px",
                    "font-weight": "bold",
                    "color": "#333333",
                    "margin-bottom": "16px"
                }
            },
            {
                name: "Контейнер",
                styles: {
                    "max-width": "1200px",
                    "margin": "0 auto",
                    "padding": "20px"
                }
            }
        ];

        return presets.map(preset => `
            <div class="css-preset" onclick="visualBuilder.advancedCSSEditor.applyCSSPreset(${JSON.stringify(preset.styles)})">
                <div class="preset-name">${preset.name}</div>
                <div class="preset-preview"></div>
            </div>
        `).join("");
    }

    applyCSSPreset(styles) {
        if (!this.currentElement) return;

        Object.entries(styles).forEach(([property, value]) => {
            this.updateElementCSS(property, value);
        });

        this.vb.showNotification("CSS пресет применен", "success");
    }

    resetStyles() {
        if (!this.currentElement) return;

        if (confirm("Вы уверены, что хотите сбросить все стили элемента?")) {
            this.currentElement.removeAttribute("style");
            this.updateCSSCode();
            this.vb.showNotification("Стили сброшены", "success");
        }
    }

    saveStylePreset() {
        if (!this.currentElement) return;

        const name = prompt("Введите название пресета:");
        if (!name) return;

        const styles = {};
        const computedStyles = window.getComputedStyle(this.currentElement);
        
        for (let i = 0; i < computedStyles.length; i++) {
            const property = computedStyles[i];
            const value = computedStyles.getPropertyValue(property);
            if (value && value !== "initial" && value !== "normal") {
                styles[property] = value;
            }
        }

        const presets = JSON.parse(localStorage.getItem("css-presets") || "[]");
        presets.push({ name, styles });
        localStorage.setItem("css-presets", JSON.stringify(presets));

        this.vb.showNotification("Пресет сохранен", "success");
    }

    getCSSPropertyLabel(property) {
        const labels = {
            "display": "Отображение",
            "position": "Позиционирование",
            "width": "Ширина",
            "height": "Высота",
            "margin": "Внешний отступ",
            "padding": "Внутренний отступ",
            "font-family": "Шрифт",
            "font-size": "Размер шрифта",
            "font-weight": "Жирность шрифта",
            "color": "Цвет текста",
            "background-color": "Цвет фона",
            "border": "Граница",
            "border-radius": "Скругление углов",
            "box-shadow": "Тень",
            "opacity": "Прозрачность",
            "transform": "Трансформация",
            "transition": "Переход",
            "flex-direction": "Направление Flex",
            "justify-content": "Выравнивание по главной оси",
            "align-items": "Выравнивание по поперечной оси",
            "grid-template-columns": "Колонки Grid",
            "grid-template-rows": "Строки Grid",
            "grid-gap": "Отступы Grid"
        };

        return labels[property] || property;
    }

    rgbToHex(rgb) {
        if (!rgb || rgb === "rgba(0, 0, 0, 0)" || rgb === "transparent") {
            return "#000000";
        }

        const rgbMatch = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
        if (rgbMatch) {
            const r = parseInt(rgbMatch[1]);
            const g = parseInt(rgbMatch[2]);
            const b = parseInt(rgbMatch[3]);
            return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
        }

        return rgb;
    }

    isValidColor(color) {
        const s = new Option().style;
        s.color = color;
        return s.color !== "";
    }

    editElementCSS(element) {
        this.currentElement = element;
        this.openStylePanel(element);
    }

    editGrid(element) {
        if (this.vb.gridEditor) {
            this.vb.gridEditor.editGrid(element);
        } else {
            this.vb.showNotification("Grid Editor не загружен", "error");
        }
    }

    editFlexbox(element) {
        if (this.vb.flexboxEditor) {
            this.vb.flexboxEditor.editFlexbox(element);
        } else {
            this.vb.showNotification("Flexbox Editor не загружен", "error");
        }
    }

    exportStyles(element) {
        const styles = {};
        const computedStyles = window.getComputedStyle(element);
        
        for (let i = 0; i < computedStyles.length; i++) {
            const property = computedStyles[i];
            const value = computedStyles.getPropertyValue(property);
            if (value && value !== "initial" && value !== "normal") {
                styles[property] = value;
            }
        }

        return styles;
    }

    importStyles(element, styles) {
        Object.entries(styles).forEach(([property, value]) => {
            element.style.setProperty(property, value);
        });
    }
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = AdvancedCSSEditor;
}
