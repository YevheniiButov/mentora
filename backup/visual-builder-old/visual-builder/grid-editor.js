/**
 * Grid Editor для Visual Builder
 * Визуальный редактор CSS Grid
 */

class GridEditor {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.currentElement = null;
        this.gridOverlay = null;
        this.gridLines = [];
        this.isEditing = false;
        this.init();
    }

    init() {
        console.info("🔲 Grid Editor инициализирован");
    }

    editGrid(element) {
        this.currentElement = element;
        this.isEditing = true;
        this.showGridPanel();
        this.createGridOverlay();
        this.analyzeCurrentGrid();
        console.info("🔲 Grid Editor открыт для элемента:", element.tagName);
    }

    showGridPanel() {
        const panel = this.createGridPanel();
        const propertiesPanel = document.getElementById("propertiesPanel");
        if (propertiesPanel) {
            propertiesPanel.innerHTML = "";
            propertiesPanel.appendChild(panel);
            propertiesPanel.classList.add("active");
            propertiesPanel.style.display = "flex";
        }
    }

    createGridPanel() {
        const panel = document.createElement("div");
        panel.className = "grid-editor-panel";
        panel.innerHTML = `
            <div class="grid-panel-header">
                <h3>
                    <i class="bi bi-grid-3x3"></i>
                    CSS Grid Editor
                </h3>
                <div class="grid-actions">
                    <button class="btn btn-sm" onclick="visualBuilder.gridEditor.toggleGridOverlay()" title="Показать/скрыть сетку">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm" onclick="visualBuilder.gridEditor.resetGrid()" title="Сбросить Grid">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                </div>
            </div>
            
            <div class="grid-settings">
                <div class="grid-section">
                    <h4>Основные настройки</h4>
                    <div class="grid-control">
                        <label>Display:</label>
                        <select class="grid-input" id="gridDisplay" onchange="visualBuilder.gridEditor.updateGridProperty(\"display\", this.value)">
                            <option value="grid">Grid</option>
                            <option value="inline-grid">Inline Grid</option>
                            <option value="block">Block</option>
                            <option value="flex">Flex</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid-section">
                    <h4>Колонки (grid-template-columns)</h4>
                    <div class="grid-control">
                        <label>Количество колонок:</label>
                        <input type="range" class="grid-range" id="gridColumns" min="1" max="12" value="3" 
                               onchange="visualBuilder.gridEditor.updateGridColumns(this.value)">
                        <span class="grid-value" id="gridColumnsValue">3</span>
                    </div>
                    <div class="grid-control">
                        <label>Размеры колонок:</label>
                        <input type="text" class="grid-input" id="gridTemplateColumns" 
                               placeholder="1fr 1fr 1fr" 
                               onchange="visualBuilder.gridEditor.updateGridProperty(\"grid-template-columns\", this.value)">
                    </div>
                    <div class="grid-presets">
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyColumnPreset(\"1fr 1fr 1fr\")">3 равные</button>
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyColumnPreset(\"1fr 2fr 1fr\")">1:2:1</button>
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyColumnPreset(\"repeat(12, 1fr)\")">12 колонок</button>
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyColumnPreset(\"200px 1fr 200px\")">Фиксированные</button>
                    </div>
                </div>
                
                <div class="grid-section">
                    <h4>Строки (grid-template-rows)</h4>
                    <div class="grid-control">
                        <label>Количество строк:</label>
                        <input type="range" class="grid-range" id="gridRows" min="1" max="12" value="3" 
                               onchange="visualBuilder.gridEditor.updateGridRows(this.value)">
                        <span class="grid-value" id="gridRowsValue">3</span>
                    </div>
                    <div class="grid-control">
                        <label>Размеры строк:</label>
                        <input type="text" class="grid-input" id="gridTemplateRows" 
                               placeholder="auto auto auto" 
                               onchange="visualBuilder.gridEditor.updateGridProperty(\"grid-template-rows\", this.value)">
                    </div>
                    <div class="grid-presets">
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyRowPreset(\"auto auto auto\")">Авто</button>
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyRowPreset(\"100px 1fr 100px\")">Фиксированные</button>
                        <button class="btn btn-sm" onclick="visualBuilder.gridEditor.applyRowPreset(\"repeat(3, minmax(100px, auto))\")">Минимум 100px</button>
                    </div>
                </div>
                
                <div class="grid-section">
                    <h4>Отступы (grid-gap)</h4>
                    <div class="grid-control">
                        <label>Отступы между элементами:</label>
                        <input type="text" class="grid-input" id="gridGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.gridEditor.updateGridProperty(\"grid-gap\", this.value)">
                    </div>
                    <div class="grid-control">
                        <label>Отступы по колонкам:</label>
                        <input type="text" class="grid-input" id="gridColumnGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.gridEditor.updateGridProperty(\"column-gap\", this.value)">
                    </div>
                    <div class="grid-control">
                        <label>Отступы по строкам:</label>
                        <input type="text" class="grid-input" id="gridRowGap" 
                               placeholder="20px" 
                               onchange="visualBuilder.gridEditor.updateGridProperty(\"row-gap\", this.value)">
                    </div>
                </div>
                
                <div class="grid-section">
                    <h4>Выравнивание</h4>
                    <div class="grid-control">
                        <label>По горизонтали (justify-items):</label>
                        <select class="grid-input" id="gridJustifyItems" onchange="visualBuilder.gridEditor.updateGridProperty(\"justify-items\", this.value)">
                            <option value="stretch">Stretch</option>
                            <option value="start">Start</option>
                            <option value="center">Center</option>
                            <option value="end">End</option>
                        </select>
                    </div>
                    <div class="grid-control">
                        <label>По вертикали (align-items):</label>
                        <select class="grid-input" id="gridAlignItems" onchange="visualBuilder.gridEditor.updateGridProperty(\"align-items\", this.value)">
                            <option value="stretch">Stretch</option>
                            <option value="start">Start</option>
                            <option value="center">Center</option>
                            <option value="end">End</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="grid-visualizer">
                <h4>Визуализация Grid</h4>
                <div class="grid-preview" id="gridPreview">
                    <!-- Grid preview будет создан динамически -->
                </div>
                <div class="grid-info">
                    <div class="grid-info-item">
                        <span class="info-label">Колонки:</span>
                        <span class="info-value" id="gridInfoColumns">3</span>
                    </div>
                    <div class="grid-info-item">
                        <span class="info-label">Строки:</span>
                        <span class="info-value" id="gridInfoRows">3</span>
                    </div>
                    <div class="grid-info-item">
                        <span class="info-label">Элементы:</span>
                        <span class="info-value" id="gridInfoItems">0</span>
                    </div>
                </div>
            </div>
        `;

        this.setupGridPanelEvents(panel);
        this.initializeGridValues();
        return panel;
    }

    setupGridPanelEvents(panel) {
        const gridColumns = panel.querySelector("#gridColumns");
        const gridColumnsValue = panel.querySelector("#gridColumnsValue");
        const gridRows = panel.querySelector("#gridRows");
        const gridRowsValue = panel.querySelector("#gridRowsValue");

        if (gridColumns && gridColumnsValue) {
            gridColumns.addEventListener("input", (e) => {
                gridColumnsValue.textContent = e.target.value;
                this.updateGridColumns(e.target.value);
            });
        }

        if (gridRows && gridRowsValue) {
            gridRows.addEventListener("input", (e) => {
                gridRowsValue.textContent = e.target.value;
                this.updateGridRows(e.target.value);
            });
        }
    }

    initializeGridValues() {
        if (!this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        
        const displaySelect = document.getElementById("gridDisplay");
        if (displaySelect) {
            displaySelect.value = styles.display;
        }

        const columnsInput = document.getElementById("gridTemplateColumns");
        if (columnsInput) {
            columnsInput.value = styles.gridTemplateColumns;
        }

        const rowsInput = document.getElementById("gridTemplateRows");
        if (rowsInput) {
            rowsInput.value = styles.gridTemplateRows;
        }

        const gapInput = document.getElementById("gridGap");
        if (gapInput) {
            gapInput.value = styles.gap;
        }

        const justifySelect = document.getElementById("gridJustifyItems");
        if (justifySelect) {
            justifySelect.value = styles.justifyItems;
        }

        const alignSelect = document.getElementById("gridAlignItems");
        if (alignSelect) {
            alignSelect.value = styles.alignItems;
        }

        this.updateGridVisualization();
    }

    updateGridProperty(property, value) {
        if (!this.currentElement) return;

        try {
            this.currentElement.style.setProperty(property, value);
            this.updateGridVisualization();
            this.updateGridOverlay();
            
            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }
            
            console.info(`✅ Grid свойство обновлено: ${property}: ${value}`);
        } catch (error) {
            console.error("Ошибка обновления Grid свойства:", error);
            this.vb.showNotification("Ошибка обновления Grid свойства", "error");
        }
    }

    updateGridColumns(count) {
        const columns = [];
        for (let i = 0; i < count; i++) {
            columns.push("1fr");
        }
        const value = columns.join(" ");
        this.updateGridProperty("grid-template-columns", value);
        
        const input = document.getElementById("gridTemplateColumns");
        if (input) {
            input.value = value;
        }
    }

    updateGridRows(count) {
        const rows = [];
        for (let i = 0; i < count; i++) {
            rows.push("auto");
        }
        const value = rows.join(" ");
        this.updateGridProperty("grid-template-rows", value);
        
        const input = document.getElementById("gridTemplateRows");
        if (input) {
            input.value = value;
        }
    }

    applyColumnPreset(preset) {
        this.updateGridProperty("grid-template-columns", preset);
        
        const input = document.getElementById("gridTemplateColumns");
        if (input) {
            input.value = preset;
        }
        
        const range = document.getElementById("gridColumns");
        const value = document.getElementById("gridColumnsValue");
        if (range && value) {
            const count = preset.split(" ").length;
            range.value = count;
            value.textContent = count;
        }
    }

    applyRowPreset(preset) {
        this.updateGridProperty("grid-template-rows", preset);
        
        const input = document.getElementById("gridTemplateRows");
        if (input) {
            input.value = preset;
        }
        
        const range = document.getElementById("gridRows");
        const value = document.getElementById("gridRowsValue");
        if (range && value) {
            const count = preset.split(" ").length;
            range.value = count;
            value.textContent = count;
        }
    }

    createGridOverlay() {
        if (this.gridOverlay) {
            this.gridOverlay.remove();
        }

        this.gridOverlay = document.createElement("div");
        this.gridOverlay.className = "grid-overlay";
        this.gridOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
            background: repeating-linear-gradient(
                90deg,
                rgba(0, 123, 255, 0.1) 0px,
                rgba(0, 123, 255, 0.1) 1px,
                transparent 1px,
                transparent calc(100% / var(--grid-columns, 3))
            ),
            repeating-linear-gradient(
                0deg,
                rgba(0, 123, 255, 0.1) 0px,
                rgba(0, 123, 255, 0.1) 1px,
                transparent 1px,
                transparent calc(100% / var(--grid-rows, 3))
            );
        `;

        if (this.currentElement) {
            this.currentElement.style.position = "relative";
            this.currentElement.appendChild(this.gridOverlay);
        }
    }

    updateGridOverlay() {
        if (!this.gridOverlay || !this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const columns = styles.gridTemplateColumns.split(" ").length;
        const rows = styles.gridTemplateRows.split(" ").length;

        this.gridOverlay.style.setProperty("--grid-columns", columns);
        this.gridOverlay.style.setProperty("--grid-rows", rows);
    }

    toggleGridOverlay() {
        if (this.gridOverlay) {
            this.gridOverlay.style.display = this.gridOverlay.style.display === "none" ? "block" : "none";
        }
    }

    analyzeCurrentGrid() {
        if (!this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const children = this.currentElement.children;
        
        let gridItems = 0;
        for (let i = 0; i < children.length; i++) {
            const child = children[i];
            if (child.classList.contains("draggable-element") || 
                child.classList.contains("imported-element")) {
                gridItems++;
            }
        }

        this.updateGridInfo(styles, gridItems);
    }

    updateGridInfo(styles, itemCount) {
        const columns = styles.gridTemplateColumns.split(" ").length;
        const rows = styles.gridTemplateRows.split(" ").length;

        const columnsInfo = document.getElementById("gridInfoColumns");
        const rowsInfo = document.getElementById("gridInfoRows");
        const itemsInfo = document.getElementById("gridInfoItems");

        if (columnsInfo) columnsInfo.textContent = columns;
        if (rowsInfo) rowsInfo.textContent = rows;
        if (itemsInfo) itemsInfo.textContent = itemCount;
    }

    updateGridVisualization() {
        const preview = document.getElementById("gridPreview");
        if (!preview || !this.currentElement) return;

        const styles = window.getComputedStyle(this.currentElement);
        const columns = styles.gridTemplateColumns.split(" ").length;
        const rows = styles.gridTemplateRows.split(" ").length;
        const gap = styles.gap || "0px";

        preview.innerHTML = "";
        preview.style.cssText = `
            display: grid;
            grid-template-columns: repeat(${columns}, 1fr);
            grid-template-rows: repeat(${rows}, 1fr);
            gap: ${gap};
            width: 100%;
            height: 200px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        `;

        for (let i = 0; i < columns * rows; i++) {
            const cell = document.createElement("div");
            cell.className = "grid-cell";
            cell.style.cssText = `
                background: rgba(0, 123, 255, 0.1);
                border: 1px solid rgba(0, 123, 255, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                color: #007bff;
            `;
            cell.textContent = `${i + 1}`;
            preview.appendChild(cell);
        }

        this.analyzeCurrentGrid();
    }

    resetGrid() {
        if (!this.currentElement) return;

        if (confirm("Вы уверены, что хотите сбросить все Grid настройки?")) {
            this.currentElement.style.removeProperty("display");
            this.currentElement.style.removeProperty("grid-template-columns");
            this.currentElement.style.removeProperty("grid-template-rows");
            this.currentElement.style.removeProperty("grid-gap");
            this.currentElement.style.removeProperty("justify-items");
            this.currentElement.style.removeProperty("align-items");

            this.initializeGridValues();

            if (this.gridOverlay) {
                this.gridOverlay.remove();
                this.gridOverlay = null;
            }

            if (this.vb.addToHistory) {
                this.vb.addToHistory();
            }

            this.vb.showNotification("Grid настройки сброшены", "success");
        }
    }

    close() {
        this.isEditing = false;
        this.currentElement = null;

        if (this.gridOverlay) {
            this.gridOverlay.remove();
            this.gridOverlay = null;
        }

        console.info("🔲 Grid Editor закрыт");
    }

    exportGridSettings() {
        if (!this.currentElement) return null;

        const styles = window.getComputedStyle(this.currentElement);
        return {
            display: styles.display,
            gridTemplateColumns: styles.gridTemplateColumns,
            gridTemplateRows: styles.gridTemplateRows,
            gap: styles.gap,
            justifyItems: styles.justifyItems,
            alignItems: styles.alignItems
        };
    }

    importGridSettings(settings) {
        if (!this.currentElement || !settings) return;

        Object.entries(settings).forEach(([property, value]) => {
            this.currentElement.style.setProperty(property, value);
        });

        this.initializeGridValues();
        this.updateGridVisualization();
        this.updateGridOverlay();
    }
}

if (typeof module !== "undefined" && module.exports) {
    module.exports = GridEditor;
}
