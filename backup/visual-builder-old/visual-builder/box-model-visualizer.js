/**
 * Box Model Visualizer - CSS Box Model Visualization
 * Визуализация CSS Box Model для элементов
 */

export class BoxModelVisualizer {
    constructor(styleEditor) {
        this.styleEditor = styleEditor;
        this.overlay = null;
        this.isVisible = false;
        this.currentElement = null;
        this.autoHideTimeout = null;
    }
    
    showBoxModel(element) {
        if (this.isVisible) {
            this.hideBoxModel();
        }
        
        this.currentElement = element;
        const rect = element.getBoundingClientRect();
        const computed = getComputedStyle(element);
        
        this.createOverlay(rect, computed);
        this.attachToDOM();
        this.isVisible = true;
        
        // Auto-hide after 5 seconds
        this.autoHideTimeout = setTimeout(() => this.hideBoxModel(), 5000);
        
        console.log('📦 Box Model показан для элемента:', element);
    }
    
    createOverlay(rect, computed) {
        this.overlay = document.createElement('div');
        this.overlay.className = 'box-model-overlay';
        this.overlay.innerHTML = this.generateBoxModelHTML(rect, computed);
        this.setupOverlayStyles(rect, computed);
        
        // Add click to hide
        this.overlay.addEventListener('click', () => this.hideBoxModel());
    }
    
    generateBoxModelHTML(rect, computed) {
        const margin = this.extractSpacing(computed, 'margin');
        const border = this.extractSpacing(computed, 'border', 'Width');
        const padding = this.extractSpacing(computed, 'padding');
        
        const contentWidth = Math.round(rect.width - border.left - border.right - padding.left - padding.right);
        const contentHeight = Math.round(rect.height - border.top - border.bottom - padding.top - padding.bottom);
        
        return `
            <div class="box-model-margin">
                <div class="spacing-label margin-label">margin</div>
                <div class="spacing-values margin-values">
                    <span class="top">${margin.top}px</span>
                    <span class="right">${margin.right}px</span>
                    <span class="bottom">${margin.bottom}px</span>
                    <span class="left">${margin.left}px</span>
                </div>
                
                <div class="box-model-border">
                    <div class="spacing-label border-label">border</div>
                    <div class="spacing-values border-values">
                        <span class="top">${border.top}px</span>
                        <span class="right">${border.right}px</span>
                        <span class="bottom">${border.bottom}px</span>
                        <span class="left">${border.left}px</span>
                    </div>
                    
                    <div class="box-model-padding">
                        <div class="spacing-label padding-label">padding</div>
                        <div class="spacing-values padding-values">
                            <span class="top">${padding.top}px</span>
                            <span class="right">${padding.right}px</span>
                            <span class="bottom">${padding.bottom}px</span>
                            <span class="left">${padding.left}px</span>
                        </div>
                        
                        <div class="box-model-content">
                            <div class="content-size">
                                ${contentWidth} × ${contentHeight}
                            </div>
                            <div class="content-label">content</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    extractSpacing(computed, type, suffix = '') {
        return {
            top: parseInt(computed[`${type}Top${suffix}`]) || 0,
            right: parseInt(computed[`${type}Right${suffix}`]) || 0,
            bottom: parseInt(computed[`${type}Bottom${suffix}`]) || 0,
            left: parseInt(computed[`${type}Left${suffix}`]) || 0
        };
    }
    
    setupOverlayStyles(rect, computed) {
        const margin = this.extractSpacing(computed, 'margin');
        
        Object.assign(this.overlay.style, {
            position: 'fixed',
            top: `${rect.top - margin.top}px`,
            left: `${rect.left - margin.left}px`,
            width: `${rect.width + margin.left + margin.right}px`,
            height: `${rect.height + margin.top + margin.bottom}px`,
            pointerEvents: 'none',
            zIndex: '10000',
            fontFamily: 'Monaco, Menlo, Ubuntu Mono, monospace',
            fontSize: '11px',
            color: '#333',
            cursor: 'pointer'
        });
    }
    
    attachToDOM() {
        document.body.appendChild(this.overlay);
        
        // Add styles if not already added
        if (!document.getElementById('box-model-styles')) {
            this.addStyles();
        }
    }
    
    addStyles() {
        const style = document.createElement('style');
        style.id = 'box-model-styles';
        style.textContent = `
            .box-model-overlay {
                position: fixed;
                pointer-events: none;
                z-index: 10000;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 11px;
                color: #333;
                cursor: pointer;
            }
            
            .box-model-margin {
                background: rgba(255, 165, 0, 0.3);
                border: 1px dashed rgba(255, 165, 0, 0.8);
                position: relative;
                width: 100%;
                height: 100%;
            }
            
            .box-model-border {
                background: rgba(255, 255, 0, 0.3);
                border: 1px dashed rgba(255, 255, 0, 0.8);
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
            
            .box-model-padding {
                background: rgba(0, 255, 0, 0.3);
                border: 1px dashed rgba(0, 255, 0, 0.8);
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
            
            .box-model-content {
                background: rgba(0, 0, 255, 0.3);
                border: 1px dashed rgba(0, 0, 255, 0.8);
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .spacing-label {
                position: absolute;
                background: rgba(255, 255, 255, 0.95);
                padding: 2px 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
                border: 1px solid rgba(0, 0, 0, 0.2);
            }
            
            .margin-label { 
                top: 2px; 
                left: 2px; 
                color: #ff6b00; 
                background: rgba(255, 165, 0, 0.9);
            }
            
            .border-label { 
                top: 2px; 
                left: 50%; 
                transform: translateX(-50%); 
                color: #b8860b; 
                background: rgba(255, 255, 0, 0.9);
            }
            
            .padding-label { 
                bottom: 2px; 
                left: 2px; 
                color: #228b22; 
                background: rgba(0, 255, 0, 0.9);
            }
            
            .spacing-values {
                position: absolute;
                width: 100%;
                height: 100%;
            }
            
            .spacing-values span {
                position: absolute;
                background: rgba(255, 255, 255, 0.95);
                padding: 1px 4px;
                border-radius: 2px;
                font-size: 9px;
                font-weight: bold;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
            
            .spacing-values .top { 
                top: -12px; 
                left: 50%; 
                transform: translateX(-50%); 
            }
            
            .spacing-values .bottom { 
                bottom: -12px; 
                left: 50%; 
                transform: translateX(-50%); 
            }
            
            .spacing-values .left { 
                left: -25px; 
                top: 50%; 
                transform: translateY(-50%); 
            }
            
            .spacing-values .right { 
                right: -25px; 
                top: 50%; 
                transform: translateY(-50%); 
            }
            
            .content-size {
                background: rgba(255, 255, 255, 0.95);
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                color: #0066cc;
                border: 1px solid #0066cc;
                margin-bottom: 2px;
            }
            
            .content-label {
                background: rgba(255, 255, 255, 0.95);
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
                color: #0066cc;
                border: 1px solid #0066cc;
            }
            
            .box-model-overlay:hover {
                pointer-events: all;
            }
        `;
        document.head.appendChild(style);
    }
    
    hideBoxModel() {
        if (this.autoHideTimeout) {
            clearTimeout(this.autoHideTimeout);
            this.autoHideTimeout = null;
        }
        
        if (this.overlay && this.overlay.parentNode) {
            this.overlay.parentNode.removeChild(this.overlay);
        }
        this.overlay = null;
        this.isVisible = false;
        this.currentElement = null;
        
        console.log('📦 Box Model скрыт');
    }
    
    toggleBoxModel(element) {
        if (this.isVisible) {
            this.hideBoxModel();
        } else {
            this.showBoxModel(element);
        }
    }
    
    updateBoxModel() {
        if (this.isVisible && this.currentElement) {
            this.showBoxModel(this.currentElement);
        }
    }
} 