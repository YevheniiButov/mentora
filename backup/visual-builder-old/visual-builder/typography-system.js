/**
 * Typography System - Font Management
 * Система управления типографикой для Visual Builder
 */

export class TypographySystem {
    constructor(styleEditor) {
        this.styleEditor = styleEditor;
        this.fonts = new Map();
        this.fontCategories = new Map();
        this.currentFont = null;
        this.fontHistory = [];
        
        this.init();
    }
    
    init() {
        this.loadSystemFonts();
        this.loadWebFonts();
        this.loadCustomFonts();
        console.info('📝 Typography System готов');
    }
    
    loadSystemFonts() {
        const systemFonts = {
            'Sans-serif': [
                { name: 'Inter', value: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif', category: 'system' },
                { name: 'Arial', value: 'Arial, sans-serif', category: 'system' },
                { name: 'Helvetica', value: 'Helvetica, Arial, sans-serif', category: 'system' },
                { name: 'Verdana', value: 'Verdana, Geneva, sans-serif', category: 'system' },
                { name: 'Tahoma', value: 'Tahoma, Geneva, sans-serif', category: 'system' }
            ],
            'Serif': [
                { name: 'Times New Roman', value: 'Times New Roman, Times, serif', category: 'system' },
                { name: 'Georgia', value: 'Georgia, Times, serif', category: 'system' },
                { name: 'Palatino', value: 'Palatino, Palatino Linotype, serif', category: 'system' },
                { name: 'Garamond', value: 'Garamond, serif', category: 'system' }
            ],
            'Monospace': [
                { name: 'Courier New', value: 'Courier New, Courier, monospace', category: 'system' },
                { name: 'Monaco', value: 'Monaco, Menlo, monospace', category: 'system' },
                { name: 'Consolas', value: 'Consolas, monaco, monospace', category: 'system' },
                { name: 'Lucida Console', value: 'Lucida Console, Monaco, monospace', category: 'system' }
            ]
        };
        
        Object.entries(systemFonts).forEach(([category, fonts]) => {
            this.fontCategories.set(category, fonts);
            fonts.forEach(font => {
                this.fonts.set(font.name, font);
            });
        });
    }
    
    loadWebFonts() {
        const webFonts = {
            'Google Fonts': [
                { name: 'Roboto', value: 'Roboto, sans-serif', category: 'web', url: 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap' },
                { name: 'Open Sans', value: 'Open Sans, sans-serif', category: 'web', url: 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap' },
                { name: 'Lato', value: 'Lato, sans-serif', category: 'web', url: 'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap' },
                { name: 'Poppins', value: 'Poppins, sans-serif', category: 'web', url: 'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap' },
                { name: 'Montserrat', value: 'Montserrat, sans-serif', category: 'web', url: 'https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap' }
            ],
            'Medical': [
                { name: 'Source Sans Pro', value: 'Source Sans Pro, sans-serif', category: 'medical', url: 'https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap' },
                { name: 'Nunito', value: 'Nunito, sans-serif', category: 'medical', url: 'https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap' },
                { name: 'Quicksand', value: 'Quicksand, sans-serif', category: 'medical', url: 'https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap' }
            ]
        };
        
        Object.entries(webFonts).forEach(([category, fonts]) => {
            this.fontCategories.set(category, fonts);
            fonts.forEach(font => {
                this.fonts.set(font.name, font);
            });
        });
    }
    
    loadCustomFonts() {
        const saved = localStorage.getItem('customFonts');
        if (saved) {
            try {
                const customFonts = JSON.parse(saved);
                customFonts.forEach(font => {
                    this.fonts.set(font.name, font);
                });
                
                if (customFonts.length > 0) {
                    this.fontCategories.set('Custom', customFonts);
                }
            } catch (error) {
                console.warn('Ошибка загрузки пользовательских шрифтов:', error);
            }
        }
    }
    
    addCustomFont(name, value, category = 'custom') {
        const font = { name, value, category };
        this.fonts.set(name, font);
        
        // Add to custom category
        if (!this.fontCategories.has('Custom')) {
            this.fontCategories.set('Custom', []);
        }
        this.fontCategories.get('Custom').push(font);
        
        this.saveCustomFonts();
        console.log('✅ Пользовательский шрифт добавлен:', name);
    }
    
    removeCustomFont(name) {
        this.fonts.delete(name);
        
        // Remove from custom category
        if (this.fontCategories.has('Custom')) {
            const customFonts = this.fontCategories.get('Custom');
            const index = customFonts.findIndex(font => font.name === name);
            if (index !== -1) {
                customFonts.splice(index, 1);
            }
        }
        
        this.saveCustomFonts();
    }
    
    saveCustomFonts() {
        const customFonts = this.fontCategories.get('Custom') || [];
        localStorage.setItem('customFonts', JSON.stringify(customFonts));
    }
    
    applyFont(element, fontName) {
        const font = this.fonts.get(fontName);
        if (!font) {
            console.warn('❌ Шрифт не найден:', fontName);
            return;
        }
        
        // Load web font if needed
        if (font.url && !document.querySelector(`link[href="${font.url}"]`)) {
            this.loadWebFont(font.url);
        }
        
        // Add to history
        this.fontHistory.unshift(fontName);
        if (this.fontHistory.length > 10) {
            this.fontHistory.pop();
        }
        
        // Apply font through style editor
        this.styleEditor.updateStyle('fontFamily', font.value, element);
        
        console.log(`📝 Шрифт применен: ${fontName}`);
    }
    
    loadWebFont(url) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        document.head.appendChild(link);
    }
    
    getFont(name) {
        return this.fonts.get(name);
    }
    
    getAllFonts() {
        return Array.from(this.fonts.values());
    }
    
    getFontsByCategory(category) {
        return this.fontCategories.get(category) || [];
    }
    
    getFontCategories() {
        return Array.from(this.fontCategories.keys());
    }
    
    getFontHistory() {
        return [...this.fontHistory];
    }
    
    createFontSelect(element = null) {
        const select = document.createElement('select');
        select.className = 'font-select';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Выберите шрифт';
        select.appendChild(defaultOption);
        
        // Add fonts by category
        this.getFontCategories().forEach(category => {
            const fonts = this.getFontsByCategory(category);
            
            if (fonts.length > 0) {
                // Add category header
                const categoryOption = document.createElement('option');
                categoryOption.disabled = true;
                categoryOption.textContent = `--- ${category} ---`;
                select.appendChild(categoryOption);
                
                // Add fonts in category
                fonts.forEach(font => {
                    const option = document.createElement('option');
                    option.value = font.name;
                    option.textContent = font.name;
                    option.style.fontFamily = font.value;
                    select.appendChild(option);
                });
            }
        });
        
        select.addEventListener('change', (e) => {
            const fontName = e.target.value;
            if (fontName) {
                this.applyFont(element, fontName);
            }
        });
        
        return select;
    }
    
    createFontPreview(fontName, text = 'AaBbCcDd') {
        const preview = document.createElement('div');
        preview.className = 'font-preview';
        
        const font = this.fonts.get(fontName);
        if (font) {
            preview.style.fontFamily = font.value;
            preview.textContent = text;
        }
        
        return preview;
    }
    
    // Typography utilities
    getFontSizeScale() {
        return {
            'xs': '0.75rem',
            'sm': '0.875rem',
            'base': '1rem',
            'lg': '1.125rem',
            'xl': '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
            '5xl': '3rem',
            '6xl': '3.75rem'
        };
    }
    
    getFontWeightScale() {
        return {
            'light': '300',
            'normal': '400',
            'medium': '500',
            'semibold': '600',
            'bold': '700',
            'extrabold': '800',
            'black': '900'
        };
    }
    
    getLineHeightScale() {
        return {
            'tight': '1.25',
            'snug': '1.375',
            'normal': '1.5',
            'relaxed': '1.625',
            'loose': '2'
        };
    }
    
    applyTypography(element, options = {}) {
        const {
            fontFamily,
            fontSize,
            fontWeight,
            lineHeight,
            letterSpacing,
            textAlign,
            textTransform,
            textDecoration
        } = options;
        
        if (fontFamily) {
            this.applyFont(element, fontFamily);
        }
        
        if (fontSize) {
            this.styleEditor.updateStyle('fontSize', fontSize, element);
        }
        
        if (fontWeight) {
            this.styleEditor.updateStyle('fontWeight', fontWeight, element);
        }
        
        if (lineHeight) {
            this.styleEditor.updateStyle('lineHeight', lineHeight, element);
        }
        
        if (letterSpacing) {
            this.styleEditor.updateStyle('letterSpacing', letterSpacing, element);
        }
        
        if (textAlign) {
            this.styleEditor.updateStyle('textAlign', textAlign, element);
        }
        
        if (textTransform) {
            this.styleEditor.updateStyle('textTransform', textTransform, element);
        }
        
        if (textDecoration) {
            this.styleEditor.updateStyle('textDecoration', textDecoration, element);
        }
    }
    
    updateTypographyUI() {
        // This will be called when we add the UI
        console.log('📝 Typography UI обновлен');
    }
} 