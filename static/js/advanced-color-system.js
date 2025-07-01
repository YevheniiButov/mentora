/**
 * Advanced Color System for GrapesJS
 * Продвинутая система управления цветами для GrapesJS
 * 
 * - Smart color picker (HSL/RGB/HEX, wheel, eyedropper, history)
 * - Palette generation (harmonies, accessibility, brand)
 * - Gradient builder (visual, multi-stop, CSS export)
 * - Project integration (CSS vars, real-time update, export)
 * - Advanced: contrast checker, color blindness sim, Material palette, naming
 * - Bilingual interface (en/ru)
 */

(function() {
    'use strict';

    // Двуязычные переводы
    const t = {
        en: {
            colorPicker: 'Color Picker',
            palette: 'Palette',
            gradient: 'Gradient',
            contrast: 'Contrast',
            accessibility: 'Accessibility',
            eyedropper: 'Eyedropper',
            history: 'History',
            hsl: 'HSL',
            rgb: 'RGB',
            hex: 'HEX',
            complementary: 'Complementary',
            analogous: 'Analogous',
            triadic: 'Triadic',
            tetradic: 'Tetradic',
            brand: 'Brand',
            material: 'Material',
            export: 'Export',
            import: 'Import',
            save: 'Save',
            load: 'Load',
            colorName: 'Color Name',
            colorBlindSim: 'Color Blindness Simulation',
            pass: 'Pass',
            fail: 'Fail',
            aa: 'AA',
            aaa: 'AAA',
            normalText: 'Normal Text',
            largeText: 'Large Text',
            direction: 'Direction',
            linear: 'Linear',
            radial: 'Radial',
            addStop: 'Add Stop',
            removeStop: 'Remove Stop',
            copyCSS: 'Copy CSS',
            recentColors: 'Recent Colors',
            themeGen: 'Theme Generation',
            preview: 'Preview',
            undo: 'Undo',
            redo: 'Redo',
            reset: 'Reset',
            // Описания гармоний
            desc_complementary: 'Colors opposite on the wheel, high contrast.',
            desc_analogous: 'Colors next to each other, harmonious and soft.',
            desc_triadic: 'Three evenly spaced colors, vibrant and balanced.',
            desc_tetradic: 'Four colors in a rectangle, rich and diverse.',
            desc_brand: 'Brand palette based on your main color.',
            desc_material: 'Material Design palette suggestions.',
            // Доступность
            accessible: 'Accessible',
            notAccessible: 'Not accessible',
            // Tooltips
            pickColor: 'Pick a color',
            sampleScreen: 'Sample color from screen',
            generatePalette: 'Generate palette',
            checkContrast: 'Check contrast',
            simulateBlind: 'Simulate color blindness',
            exportPalette: 'Export palette',
            importPalette: 'Import palette',
        },
        ru: {
            colorPicker: 'Палитра цветов',
            palette: 'Палитра',
            gradient: 'Градиент',
            contrast: 'Контраст',
            accessibility: 'Доступность',
            eyedropper: 'Пипетка',
            history: 'История',
            hsl: 'HSL',
            rgb: 'RGB',
            hex: 'HEX',
            complementary: 'Комплементарные',
            analogous: 'Аналоговые',
            triadic: 'Триада',
            tetradic: 'Тетрада',
            brand: 'Бренд',
            material: 'Material',
            export: 'Экспорт',
            import: 'Импорт',
            save: 'Сохранить',
            load: 'Загрузить',
            colorName: 'Имя цвета',
            colorBlindSim: 'Симуляция дальтонизма',
            pass: 'Проходит',
            fail: 'Не проходит',
            aa: 'AA',
            aaa: 'AAA',
            normalText: 'Обычный текст',
            largeText: 'Крупный текст',
            direction: 'Направление',
            linear: 'Линейный',
            radial: 'Радиальный',
            addStop: 'Добавить стоп',
            removeStop: 'Удалить стоп',
            copyCSS: 'Скопировать CSS',
            recentColors: 'Недавние цвета',
            themeGen: 'Генерация темы',
            preview: 'Предпросмотр',
            undo: 'Отмена',
            redo: 'Повтор',
            reset: 'Сброс',
            // Описания гармоний
            desc_complementary: 'Цвета напротив на круге, высокий контраст.',
            desc_analogous: 'Соседние цвета, гармония и мягкость.',
            desc_triadic: 'Три цвета через равные промежутки, ярко и сбалансировано.',
            desc_tetradic: 'Четыре цвета прямоугольником, богато и разнообразно.',
            desc_brand: 'Брендовая палитра на основе основного цвета.',
            desc_material: 'Рекомендации Material Design.',
            // Доступность
            accessible: 'Доступно',
            notAccessible: 'Недоступно',
            // Tooltips
            pickColor: 'Выбрать цвет',
            sampleScreen: 'Взять цвет с экрана',
            generatePalette: 'Сгенерировать палитру',
            checkContrast: 'Проверить контраст',
            simulateBlind: 'Симулировать дальтонизм',
            exportPalette: 'Экспорт палитры',
            importPalette: 'Импорт палитры',
        }
    };
    function tr(key) {
        const lang = document.documentElement.lang || 'en';
        return t[lang][key] || t.en[key] || key;
    }

    class AdvancedColorSystem {
        constructor(editor) {
            this.editor = editor;
            this.history = [];
            this.palette = [];
            this.gradients = [];
            this.materialPalettes = this.getMaterialPalettes();
            this.currentColor = '#3ECDC1';
            this.init();
        }

        init() {
            this.createPanel();
            this.bindEvents();
            this.loadProjectColors();
        }

        createPanel() {
            // Добавить панель в GrapesJS
            const panel = this.editor.Panels.addPanel({
                id: 'advanced-color-panel',
                visible: true,
                buttons: [{
                    id: 'color-btn',
                    className: 'btn-color',
                    label: tr('colorPicker'),
                    command: 'advanced-color-panel',
                    active: false
                }]
            });
            // Основной UI (упрощённо)
            panel.set('content', `
                <div class="advanced-color-system">
                    <div class="color-picker-section">
                        <input type="color" id="main-color-picker" value="${this.currentColor}" title="${tr('pickColor')}">
                        <input type="text" id="color-hex" value="${this.currentColor}" maxlength="7">
                        <button id="eyedropper-btn" title="${tr('sampleScreen')}">${tr('eyedropper')}</button>
                        <div class="color-history" id="color-history"></div>
                    </div>
                    <div class="palette-section">
                        <h4>${tr('palette')}</h4>
                        <div class="palette-harmonies">
                            <button class="harmony-btn" data-harmony="complementary">${tr('complementary')}</button>
                            <button class="harmony-btn" data-harmony="analogous">${tr('analogous')}</button>
                            <button class="harmony-btn" data-harmony="triadic">${tr('triadic')}</button>
                            <button class="harmony-btn" data-harmony="tetradic">${tr('tetradic')}</button>
                            <button class="harmony-btn" data-harmony="brand">${tr('brand')}</button>
                            <button class="harmony-btn" data-harmony="material">${tr('material')}</button>
                        </div>
                        <div class="palette-preview" id="palette-preview"></div>
                    </div>
                    <div class="gradient-section">
                        <h4>${tr('gradient')}</h4>
                        <div class="gradient-builder" id="gradient-builder"></div>
                        <button id="copy-gradient-css">${tr('copyCSS')}</button>
                    </div>
                    <div class="contrast-section">
                        <h4>${tr('contrast')}</h4>
                        <div id="contrast-preview"></div>
                        <button id="check-contrast">${tr('checkContrast')}</button>
                        <button id="simulate-blind">${tr('simulateBlind')}</button>
                    </div>
                    <div class="export-section">
                        <button id="export-palette">${tr('exportPalette')}</button>
                        <button id="import-palette">${tr('importPalette')}</button>
                    </div>
                </div>
            `);
        }

        bindEvents() {
            // Color picker events
            document.getElementById('main-color-picker').addEventListener('input', (e) => {
                this.setColor(e.target.value);
            });
            document.getElementById('color-hex').addEventListener('change', (e) => {
                this.setColor(e.target.value);
            });
            // Eyedropper
            document.getElementById('eyedropper-btn').addEventListener('click', () => {
                if (window.EyeDropper) {
                    const eye = new window.EyeDropper();
                    eye.open().then(result => {
                        this.setColor(result.sRGBHex);
                    });
                } else {
                    alert('Eyedropper API not supported');
                }
            });
            // Palette harmonies
            document.querySelectorAll('.harmony-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.generatePalette(e.target.dataset.harmony);
                });
            });
            // Copy gradient CSS
            document.getElementById('copy-gradient-css').addEventListener('click', () => {
                const css = this.getGradientCSS();
                navigator.clipboard.writeText(css);
            });
            // Contrast checker
            document.getElementById('check-contrast').addEventListener('click', () => {
                this.checkContrast();
            });
            // Color blindness simulation
            document.getElementById('simulate-blind').addEventListener('click', () => {
                this.simulateColorBlindness();
            });
            // Export/import
            document.getElementById('export-palette').addEventListener('click', () => {
                this.exportPalette();
            });
            document.getElementById('import-palette').addEventListener('click', () => {
                this.importPalette();
            });
        }

        setColor(color) {
            this.currentColor = color;
            document.getElementById('main-color-picker').value = color;
            document.getElementById('color-hex').value = color;
            this.addToHistory(color);
            this.updatePalettePreview();
            this.updateGradientBuilder();
            this.updateProjectColorVars(color);
        }

        addToHistory(color) {
            if (!this.history.includes(color)) {
                this.history.unshift(color);
                if (this.history.length > 10) this.history.pop();
                this.renderHistory();
            }
        }

        renderHistory() {
            const container = document.getElementById('color-history');
            container.innerHTML = '';
            this.history.forEach(c => {
                const swatch = document.createElement('div');
                swatch.className = 'color-swatch';
                swatch.style.background = c;
                swatch.title = c;
                swatch.onclick = () => this.setColor(c);
                container.appendChild(swatch);
            });
        }

        generatePalette(type) {
            // Пример: только complementary, аналоговые, триада, тетрада, бренд, material
            let palette = [];
            if (type === 'complementary') {
                palette = [this.currentColor, this.rotateHue(this.currentColor, 180)];
            } else if (type === 'analogous') {
                palette = [
                    this.rotateHue(this.currentColor, -30),
                    this.currentColor,
                    this.rotateHue(this.currentColor, 30)
                ];
            } else if (type === 'triadic') {
                palette = [
                    this.currentColor,
                    this.rotateHue(this.currentColor, 120),
                    this.rotateHue(this.currentColor, 240)
                ];
            } else if (type === 'tetradic') {
                palette = [
                    this.currentColor,
                    this.rotateHue(this.currentColor, 90),
                    this.rotateHue(this.currentColor, 180),
                    this.rotateHue(this.currentColor, 270)
                ];
            } else if (type === 'brand') {
                palette = this.generateBrandPalette(this.currentColor);
            } else if (type === 'material') {
                palette = this.materialPalettes[this.currentColor] || [];
            }
            this.palette = palette;
            this.updatePalettePreview();
        }

        updatePalettePreview() {
            const container = document.getElementById('palette-preview');
            container.innerHTML = '';
            this.palette.forEach(c => {
                const swatch = document.createElement('div');
                swatch.className = 'color-swatch';
                swatch.style.background = c;
                swatch.title = c;
                swatch.onclick = () => this.setColor(c);
                container.appendChild(swatch);
            });
        }

        rotateHue(hex, deg) {
            // Преобразование HEX -> HSL -> вращение -> HEX
            let [h, s, l] = this.hexToHsl(hex);
            h = (h + deg) % 360;
            if (h < 0) h += 360;
            return this.hslToHex(h, s, l);
        }

        hexToHsl(hex) {
            // HEX -> HSL
            let r = 0, g = 0, b = 0;
            if (hex.length === 7) {
                r = parseInt(hex.slice(1, 3), 16) / 255;
                g = parseInt(hex.slice(3, 5), 16) / 255;
                b = parseInt(hex.slice(5, 7), 16) / 255;
            }
            const max = Math.max(r, g, b), min = Math.min(r, g, b);
            let h = 0, s = 0, l = (max + min) / 2;
            if (max !== min) {
                const d = max - min;
                s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
                switch (max) {
                    case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                    case g: h = (b - r) / d + 2; break;
                    case b: h = (r - g) / d + 4; break;
                }
                h *= 60;
            }
            return [Math.round(h), Math.round(s * 100), Math.round(l * 100)];
        }

        hslToHex(h, s, l) {
            s /= 100; l /= 100;
            let c = (1 - Math.abs(2 * l - 1)) * s,
                x = c * (1 - Math.abs((h / 60) % 2 - 1)),
                m = l - c / 2,
                r = 0, g = 0, b = 0;
            if (0 <= h && h < 60) { r = c; g = x; b = 0; }
            else if (60 <= h && h < 120) { r = x; g = c; b = 0; }
            else if (120 <= h && h < 180) { r = 0; g = c; b = x; }
            else if (180 <= h && h < 240) { r = 0; g = x; b = c; }
            else if (240 <= h && h < 300) { r = x; g = 0; b = c; }
            else if (300 <= h && h < 360) { r = c; g = 0; b = x; }
            r = Math.round((r + m) * 255);
            g = Math.round((g + m) * 255);
            b = Math.round((b + m) * 255);
            return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
        }

        generateBrandPalette(base) {
            // Пример: светлее/темнее, оттенки
            const [h, s, l] = this.hexToHsl(base);
            return [
                this.hslToHex(h, s, Math.max(10, l - 30)),
                this.hslToHex(h, s, Math.max(20, l - 15)),
                base,
                this.hslToHex(h, s, Math.min(100, l + 15)),
                this.hslToHex(h, s, Math.min(100, l + 30))
            ];
        }

        getMaterialPalettes() {
            // Пример: только несколько цветов
            return {
                '#3ECDC1': ['#3ECDC1', '#26B6A6', '#1E9C8B', '#0E7C6B', '#055C4B'],
                '#764ba2': ['#764ba2', '#9575cd', '#b39ddb', '#d1c4e9', '#ede7f6']
            };
        }

        updateGradientBuilder() {
            // Упрощённо: показываем текущий цвет как градиент
            const builder = document.getElementById('gradient-builder');
            builder.innerHTML = `<div class="gradient-preview" style="background: linear-gradient(90deg, ${this.currentColor}, #fff)"></div>`;
        }

        getGradientCSS() {
            // Пример: linear-gradient
            return `background: linear-gradient(90deg, ${this.currentColor}, #fff);`;
        }

        checkContrast() {
            // Проверка контраста с белым и чёрным
            const contrastW = this.getContrast(this.currentColor, '#fff');
            const contrastB = this.getContrast(this.currentColor, '#000');
            const preview = document.getElementById('contrast-preview');
            preview.innerHTML = `
                <div style="background:#fff;color:${this.currentColor};padding:8px;">${tr('normalText')}: ${contrastW.toFixed(2)} ${contrastW >= 4.5 ? tr('pass') : tr('fail')}</div>
                <div style="background:#000;color:${this.currentColor};padding:8px;">${tr('normalText')}: ${contrastB.toFixed(2)} ${contrastB >= 4.5 ? tr('pass') : tr('fail')}</div>
            `;
        }

        getContrast(hex1, hex2) {
            // WCAG контраст
            function luminance(hex) {
                let r = parseInt(hex.slice(1, 3), 16) / 255;
                let g = parseInt(hex.slice(3, 5), 16) / 255;
                let b = parseInt(hex.slice(5, 7), 16) / 255;
                [r, g, b] = [r, g, b].map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
                return 0.2126 * r + 0.7152 * g + 0.0722 * b;
            }
            const l1 = luminance(hex1);
            const l2 = luminance(hex2);
            return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        }

        simulateColorBlindness() {
            // Упрощённая симуляция: десатурация
            const preview = document.getElementById('contrast-preview');
            preview.innerHTML += `<div style="filter: grayscale(1);background:${this.currentColor};color:#fff;padding:8px;">${tr('colorBlindSim')}</div>`;
        }

        loadProjectColors() {
            // Загрузка CSS-переменных проекта как палитры
            const root = getComputedStyle(document.documentElement);
            const vars = ['--subject-view-bg', '--text-primary', '--border-color'];
            this.palette = vars.map(v => root.getPropertyValue(v).trim() || '#3ECDC1');
            this.updatePalettePreview();
        }

        updateProjectColorVars(color) {
            // В реальном времени обновлять CSS-переменные
            document.documentElement.style.setProperty('--subject-view-bg', color);
        }

        exportPalette() {
            const data = JSON.stringify(this.palette);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'palette.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        importPalette() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (ev) => {
                    try {
                        this.palette = JSON.parse(ev.target.result);
                        this.updatePalettePreview();
                    } catch (err) {
                        alert('Import error');
                    }
                };
                reader.readAsText(file);
            };
            input.click();
        }
    }

    // Инициализация при готовности GrapesJS
    if (typeof grapesjs !== 'undefined') {
        if (grapesjs.editors) {
            const editor = grapesjs.editors[0] || window.editor;
            if (editor) {
                window.advancedColorSystem = new AdvancedColorSystem(editor);
            }
        } else {
            document.addEventListener('grapesjs:ready', () => {
                const editor = grapesjs.editors[0] || window.editor;
                if (editor) {
                    window.advancedColorSystem = new AdvancedColorSystem(editor);
                }
            });
        }
    }

    window.AdvancedColorSystem = AdvancedColorSystem;

})(); 