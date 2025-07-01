/**
 * Color System - Color Management and Palettes
 * Система управления цветами для Visual Builder
 */

export class ColorSystem {
    constructor(styleEditor) {
        this.styleEditor = styleEditor;
        this.palettes = new Map();
        this.customColors = new Set();
        this.colorHistory = [];
        this.currentPalette = 'dental';
        
        this.init();
    }
    
    init() {
        this.loadDefaultPalette();
        this.loadCustomColors();
        console.info('🎨 Color System готов');
    }
    
    loadDefaultPalette() {
        // Dental Academy brand colors
        const dentalPalette = {
            name: 'Dental Academy',
            colors: [
                { name: 'Primary', value: '#3ECDC1', category: 'brand' },
                { name: 'Secondary', value: '#6C5CE7', category: 'brand' },
                { name: 'Accent', value: '#FDCB6E', category: 'brand' },
                { name: 'Success', value: '#00D68F', category: 'status' },
                { name: 'Warning', value: '#FFC107', category: 'status' },
                { name: 'Error', value: '#FF3333', category: 'status' },
                { name: 'Info', value: '#17A2B8', category: 'status' }
            ]
        };
        
        // Medical colors palette
        const medicalPalette = {
            name: 'Medical',
            colors: [
                { name: 'Surgical Blue', value: '#1E88E5', category: 'medical' },
                { name: 'Dental White', value: '#F8F9FA', category: 'medical' },
                { name: 'Gum Pink', value: '#FFB6C1', category: 'medical' },
                { name: 'Bone White', value: '#FFF8DC', category: 'medical' },
                { name: 'Blood Red', value: '#DC143C', category: 'medical' },
                { name: 'Mint Green', value: '#98FB98', category: 'medical' }
            ]
        };
        
        // Neutral colors palette
        const neutralPalette = {
            name: 'Neutral',
            colors: [
                { name: 'Black', value: '#000000', category: 'neutral' },
                { name: 'Dark Gray', value: '#333333', category: 'neutral' },
                { name: 'Gray', value: '#666666', category: 'neutral' },
                { name: 'Light Gray', value: '#999999', category: 'neutral' },
                { name: 'Lighter Gray', value: '#CCCCCC', category: 'neutral' },
                { name: 'White', value: '#FFFFFF', category: 'neutral' }
            ]
        };
        
        this.palettes.set('dental', dentalPalette);
        this.palettes.set('medical', medicalPalette);
        this.palettes.set('neutral', neutralPalette);
    }
    
    loadCustomColors() {
        const saved = localStorage.getItem('customColors');
        if (saved) {
            try {
                this.customColors = new Set(JSON.parse(saved));
            } catch (error) {
                console.warn('Ошибка загрузки пользовательских цветов:', error);
                this.customColors = new Set();
            }
        }
    }
    
    addCustomColor(color) {
        if (this.isValidColor(color)) {
            this.customColors.add(color);
            this.saveCustomColors();
            this.updateColorUI();
            console.log('✅ Пользовательский цвет добавлен:', color);
        } else {
            console.warn('❌ Некорректный цвет:', color);
        }
    }
    
    removeCustomColor(color) {
        this.customColors.delete(color);
        this.saveCustomColors();
        this.updateColorUI();
    }
    
    saveCustomColors() {
        localStorage.setItem('customColors', JSON.stringify([...this.customColors]));
    }
    
    isValidColor(color) {
        // Test if color is valid by setting it on a test element
        const testEl = document.createElement('div');
        testEl.style.color = color;
        return testEl.style.color !== '';
    }
    
    applyColor(element, property, color) {
        // Add to history
        this.colorHistory.unshift(color);
        if (this.colorHistory.length > 20) {
            this.colorHistory.pop();
        }
        
        // Apply color through style editor
        this.styleEditor.updateStyle(property, color, element);
        
        console.log(`🎨 Цвет применен: ${property} = ${color}`);
    }
    
    generateColorVariations(baseColor) {
        const variations = [];
        const steps = [-40, -20, 0, 20, 40];
        
        steps.forEach(step => {
            const variation = this.adjustColorBrightness(baseColor, step);
            variations.push(variation);
        });
        
        return variations;
    }
    
    adjustColorBrightness(hex, percent) {
        // Convert hex to RGB
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        
        // Adjust brightness
        const factor = 1 + (percent / 100);
        const newR = Math.min(255, Math.max(0, Math.round(r * factor)));
        const newG = Math.min(255, Math.max(0, Math.round(g * factor)));
        const newB = Math.min(255, Math.max(0, Math.round(b * factor)));
        
        // Convert back to hex
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }
    
    getContrastColor(backgroundColor) {
        // Convert hex to RGB
        const r = parseInt(backgroundColor.slice(1, 3), 16);
        const g = parseInt(backgroundColor.slice(3, 5), 16);
        const b = parseInt(backgroundColor.slice(5, 7), 16);
        
        // Calculate luminance
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
        
        // Return black or white based on luminance
        return luminance > 0.5 ? '#000000' : '#FFFFFF';
    }
    
    getPalette(name) {
        return this.palettes.get(name) || this.palettes.get('dental');
    }
    
    getAllPalettes() {
        return Array.from(this.palettes.values());
    }
    
    getPaletteNames() {
        return Array.from(this.palettes.keys());
    }
    
    setCurrentPalette(name) {
        if (this.palettes.has(name)) {
            this.currentPalette = name;
            this.updateColorUI();
            console.log('🎨 Палитра изменена на:', name);
        }
    }
    
    getCurrentPalette() {
        return this.palettes.get(this.currentPalette);
    }
    
    getColorHistory() {
        return [...this.colorHistory];
    }
    
    getCustomColors() {
        return [...this.customColors];
    }
    
    createColorPicker(property, element = null) {
        const picker = document.createElement('input');
        picker.type = 'color';
        picker.className = 'color-picker';
        picker.dataset.property = property;
        
        picker.addEventListener('change', (e) => {
            const color = e.target.value;
            this.applyColor(element, property, color);
        });
        
        return picker;
    }
    
    createColorPalette(property, element = null) {
        const palette = document.createElement('div');
        palette.className = 'color-palette';
        
        const currentPalette = this.getCurrentPalette();
        
        currentPalette.colors.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'color-swatch';
            swatch.style.backgroundColor = color.value;
            swatch.title = color.name;
            
            swatch.addEventListener('click', () => {
                this.applyColor(element, property, color.value);
            });
            
            palette.appendChild(swatch);
        });
        
        return palette;
    }
    
    updateColorUI() {
        // This will be called when we add the UI
        // For now, just log the update
        console.log('🎨 Color UI обновлен');
    }
    
    // Utility methods
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
    
    rgbToHex(r, g, b) {
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }
    
    hslToHex(h, s, l) {
        s /= 100;
        l /= 100;
        
        const c = (1 - Math.abs(2 * l - 1)) * s;
        const x = c * (1 - Math.abs((h / 60) % 2 - 1));
        const m = l - c / 2;
        let r = 0, g = 0, b = 0;
        
        if (0 <= h && h < 60) {
            r = c; g = x; b = 0;
        } else if (60 <= h && h < 120) {
            r = x; g = c; b = 0;
        } else if (120 <= h && h < 180) {
            r = 0; g = c; b = x;
        } else if (180 <= h && h < 240) {
            r = 0; g = x; b = c;
        } else if (240 <= h && h < 300) {
            r = x; g = 0; b = c;
        } else if (300 <= h && h < 360) {
            r = c; g = 0; b = x;
        }
        
        return this.rgbToHex(Math.round((r + m) * 255), Math.round((g + m) * 255), Math.round((b + m) * 255));
    }
} 