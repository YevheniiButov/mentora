/**
 * Responsive Design System для Visual Builder
 * Система адаптивного дизайна с поддержкой различных устройств
 */

class ResponsiveDesign {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.breakpoints = {
            mobile: 480,
            tablet: 768,
            desktop: 1024,
            wide: 1440
        };
        this.currentBreakpoint = 'desktop';
        this.deviceFrames = {
            mobile: { width: 375, height: 667, name: 'Mobile' },
            tablet: { width: 768, height: 1024, name: 'Tablet' },
            desktop: { width: 1200, height: 800, name: 'Desktop' },
            wide: { width: 1440, height: 900, name: 'Wide' }
        };
        this.init();
    }

    /**
     * Инициализация системы
     */
    init() {
        console.info('📱 Responsive Design System инициализирован');
        this.setupDeviceSwitcher();
        this.setupResponsiveControls();
    }

    /**
     * Настройка переключателя устройств
     */
    setupDeviceSwitcher() {
        const deviceSwitcher = document.createElement('div');
        deviceSwitcher.className = 'device-switcher';
        deviceSwitcher.innerHTML = `
            <div class="device-switcher-header">
                <h4>Устройства</h4>
                <button class="btn btn-sm" onclick="visualBuilder.responsiveDesign.showResponsiveSettings()">
                    <i class="bi bi-gear"></i>
                </button>
            </div>
            <div class="device-buttons">
                <button class="device-btn active" data-device="desktop" onclick="visualBuilder.responsiveDesign.switchDevice('desktop')">
                    <i class="bi bi-laptop"></i>
                    <span>Desktop</span>
                </button>
                <button class="device-btn" data-device="tablet" onclick="visualBuilder.responsiveDesign.switchDevice('tablet')">
                    <i class="bi bi-tablet"></i>
                    <span>Tablet</span>
                </button>
                <button class="device-btn" data-device="mobile" onclick="visualBuilder.responsiveDesign.switchDevice('mobile')">
                    <i class="bi bi-phone"></i>
                    <span>Mobile</span>
                </button>
                <button class="device-btn" data-device="wide" onclick="visualBuilder.responsiveDesign.switchDevice('wide')">
                    <i class="bi bi-display"></i>
                    <span>Wide</span>
                </button>
            </div>
        `;

        // Добавляем в toolbar
        const toolbar = document.querySelector('.toolbar');
        if (toolbar) {
            const responsiveSection = document.createElement('div');
            responsiveSection.className = 'toolbar-section';
            responsiveSection.appendChild(deviceSwitcher);
            toolbar.appendChild(responsiveSection);
        }
    }

    /**
     * Настройка адаптивных контролов
     */
    setupResponsiveControls() {
        // Добавляем кнопку адаптивных настроек в панель свойств
        const propertiesPanel = document.getElementById('propertiesPanel');
        if (propertiesPanel) {
            const responsiveBtn = document.createElement('button');
            responsiveBtn.className = 'btn btn-primary btn-sm w-100';
            responsiveBtn.innerHTML = '<i class="bi bi-phone"></i> Адаптивные настройки';
            responsiveBtn.onclick = () => this.showResponsivePanel();
            propertiesPanel.appendChild(responsiveBtn);
        }
    }

    /**
     * Переключение устройства
     */
    switchDevice(device) {
        if (!this.breakpoints[device]) return;
        
        this.currentBreakpoint = device;
        this.updateCanvasSize(device);
        this.showDeviceFrame(device);
        this.updateToolbar(device);
        this.applyDeviceStyles(device);
        
        console.info(`📱 Переключено на устройство: ${device}`);
        this.vb.showNotification(`Переключено на ${this.deviceFrames[device].name}`, 'info');
    }

    /**
     * Обновление размера canvas
     */
    updateCanvasSize(device) {
        const canvas = this.vb.dom.canvas;
        if (!canvas) return;
        
        const frame = this.deviceFrames[device];
        canvas.style.width = `${frame.width}px`;
        canvas.style.maxWidth = `${frame.width}px`;
        canvas.style.height = 'auto';
        canvas.setAttribute('data-device', device);
        
        // Добавляем рамку устройства
        this.addDeviceFrame(canvas, device);
    }

    /**
     * Добавление рамки устройства
     */
    addDeviceFrame(canvas, device) {
        // Убираем старую рамку
        const oldFrame = canvas.parentElement.querySelector('.device-frame');
        if (oldFrame) {
            oldFrame.remove();
        }
        
        const frame = this.deviceFrames[device];
        const deviceFrame = document.createElement('div');
        deviceFrame.className = 'device-frame';
        deviceFrame.innerHTML = `
            <div class="device-frame-header">
                <span class="device-name">${frame.name}</span>
                <span class="device-size">${frame.width}×${frame.height}</span>
            </div>
        `;
        
        // Вставляем рамку перед canvas
        canvas.parentElement.insertBefore(deviceFrame, canvas);
    }

    /**
     * Показ рамки устройства
     */
    showDeviceFrame(device) {
        const frame = this.deviceFrames[device];
        const canvas = this.vb.dom.canvas;
        
        if (canvas) {
            canvas.style.border = '2px solid #e5e7eb';
            canvas.style.borderRadius = device === 'mobile' ? '20px' : '8px';
            canvas.style.margin = '0 auto';
        }
    }

    /**
     * Обновление toolbar
     */
    updateToolbar(device) {
        // Обновляем активную кнопку устройства
        document.querySelectorAll('.device-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-device="${device}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    /**
     * Сохранение стилей для устройства
     */
    saveStyleForDevice(element, property, value, device) {
        if (!element.dataset.responsiveStyles) {
            element.dataset.responsiveStyles = '{}';
        }
        
        const styles = JSON.parse(element.dataset.responsiveStyles);
        if (!styles[device]) styles[device] = {};
        styles[device][property] = value;
        
        element.dataset.responsiveStyles = JSON.stringify(styles);
        
        // Применяем стиль если текущее устройство
        if (device === this.currentBreakpoint) {
            element.style.setProperty(property, value);
        }
        
        console.info(`💾 Стиль сохранен для ${device}: ${property} = ${value}`);
    }

    /**
     * Применение стилей для устройства
     */
    applyDeviceStyles(device) {
        const elements = this.vb.dom.canvas.querySelectorAll('[data-responsive-styles]');
        
        elements.forEach(element => {
            const styles = JSON.parse(element.dataset.responsiveStyles || '{}');
            const deviceStyles = styles[device] || {};
            
            Object.entries(deviceStyles).forEach(([property, value]) => {
                element.style.setProperty(property, value);
            });
        });
        
        console.info(`📱 Применены стили для ${device}`);
    }

    /**
     * Показ панели адаптивных настроек
     */
    showResponsivePanel() {
        const modal = this.createResponsiveModal();
        document.body.appendChild(modal);
        
        requestAnimationFrame(() => {
            modal.style.display = 'flex';
        });
    }

    /**
     * Создание модального окна адаптивных настроек
     */
    createResponsiveModal() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay responsive-modal';
        modal.innerHTML = `
            <div class="modal responsive-settings-modal">
                <div class="modal-header">
                    <h3>
                        <i class="bi bi-phone"></i>
                        Адаптивные настройки
                    </h3>
                    <button class="btn btn-ghost" onclick="this.closest('.modal-overlay').remove()">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="responsive-settings">
                        <div class="device-settings">
                            <h4>Настройки устройств</h4>
                            ${Object.entries(this.deviceFrames).map(([device, frame]) => `
                                <div class="device-setting">
                                    <div class="device-info">
                                        <i class="bi bi-${this.getDeviceIcon(device)}"></i>
                                        <span>${frame.name}</span>
                                    </div>
                                    <div class="device-inputs">
                                        <input type="number" value="${frame.width}" 
                                               onchange="visualBuilder.responsiveDesign.updateDeviceSize('${device}', 'width', this.value)"
                                               placeholder="Ширина">
                                        <span>×</span>
                                        <input type="number" value="${frame.height}"
                                               onchange="visualBuilder.responsiveDesign.updateDeviceSize('${device}', 'height', this.value)"
                                               placeholder="Высота">
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="breakpoint-settings">
                            <h4>Точки перелома</h4>
                            ${Object.entries(this.breakpoints).map(([device, breakpoint]) => `
                                <div class="breakpoint-setting">
                                    <label>${this.getDeviceName(device)}:</label>
                                    <input type="number" value="${breakpoint}"
                                           onchange="visualBuilder.responsiveDesign.updateBreakpoint('${device}', this.value)"
                                           placeholder="px">
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="responsive-actions">
                            <h4>Действия</h4>
                            <div class="action-buttons">
                                <button class="btn btn-primary" onclick="visualBuilder.responsiveDesign.makeAllResponsive()">
                                    <i class="bi bi-phone"></i>
                                    Сделать все адаптивными
                                </button>
                                <button class="btn btn-secondary" onclick="visualBuilder.responsiveDesign.exportResponsiveCSS()">
                                    <i class="bi bi-code"></i>
                                    Экспорт CSS
                                </button>
                                <button class="btn btn-warning" onclick="visualBuilder.responsiveDesign.resetResponsive()">
                                    <i class="bi bi-arrow-clockwise"></i>
                                    Сбросить
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    /**
     * Обновление размера устройства
     */
    updateDeviceSize(device, dimension, value) {
        if (this.deviceFrames[device]) {
            this.deviceFrames[device][dimension] = parseInt(value);
            
            // Обновляем canvas если это текущее устройство
            if (device === this.currentBreakpoint) {
                this.updateCanvasSize(device);
            }
            
            this.vb.showNotification(`Размер ${device} обновлен`, 'success');
        }
    }

    /**
     * Обновление точки перелома
     */
    updateBreakpoint(device, value) {
        this.breakpoints[device] = parseInt(value);
        this.vb.showNotification(`Точка перелома ${device} обновлена`, 'success');
    }

    /**
     * Сделать все элементы адаптивными
     */
    makeAllResponsive() {
        const elements = this.vb.dom.canvas.querySelectorAll('.draggable-element');
        
        elements.forEach(element => {
            this.makeElementResponsive(element);
        });
        
        this.vb.showNotification(`${elements.length} элементов сделаны адаптивными`, 'success');
    }

    /**
     * Сделать элемент адаптивным
     */
    makeElementResponsive(element) {
        const computedStyles = window.getComputedStyle(element);
        const responsiveStyles = {};
        
        // Сохраняем текущие стили для всех устройств
        Object.keys(this.breakpoints).forEach(device => {
            responsiveStyles[device] = {
                'font-size': this.getResponsiveFontSize(computedStyles.fontSize, device),
                'padding': this.getResponsivePadding(computedStyles.padding, device),
                'margin': this.getResponsiveMargin(computedStyles.margin, device)
            };
        });
        
        element.dataset.responsiveStyles = JSON.stringify(responsiveStyles);
        element.classList.add('responsive-element');
        
        console.info('📱 Элемент сделан адаптивным:', element.tagName);
    }

    /**
     * Получение адаптивного размера шрифта
     */
    getResponsiveFontSize(baseSize, device) {
        const base = parseInt(baseSize);
        const multipliers = {
            mobile: 0.8,
            tablet: 0.9,
            desktop: 1,
            wide: 1.1
        };
        
        return `${Math.round(base * multipliers[device])}px`;
    }

    /**
     * Получение адаптивных отступов
     */
    getResponsivePadding(basePadding, device) {
        const base = parseInt(basePadding) || 16;
        const multipliers = {
            mobile: 0.5,
            tablet: 0.75,
            desktop: 1,
            wide: 1.25
        };
        
        return `${Math.round(base * multipliers[device])}px`;
    }

    /**
     * Получение адаптивных внешних отступов
     */
    getResponsiveMargin(baseMargin, device) {
        const base = parseInt(baseMargin) || 16;
        const multipliers = {
            mobile: 0.5,
            tablet: 0.75,
            desktop: 1,
            wide: 1.25
        };
        
        return `${Math.round(base * multipliers[device])}px`;
    }

    /**
     * Экспорт адаптивного CSS
     */
    exportResponsiveCSS() {
        const elements = this.vb.dom.canvas.querySelectorAll('[data-responsive-styles]');
        let css = '/* Адаптивные стили */\n\n';
        
        Object.entries(this.breakpoints).forEach(([device, breakpoint]) => {
            css += `/* ${this.getDeviceName(device)} (${breakpoint}px) */\n`;
            css += `@media (max-width: ${breakpoint}px) {\n`;
            
            elements.forEach(element => {
                const styles = JSON.parse(element.dataset.responsiveStyles || '{}');
                const deviceStyles = styles[device] || {};
                
                if (Object.keys(deviceStyles).length > 0) {
                    css += `  ${element.tagName.toLowerCase()}[data-id="${element.dataset.id}"] {\n`;
                    Object.entries(deviceStyles).forEach(([property, value]) => {
                        css += `    ${property}: ${value};\n`;
                    });
                    css += `  }\n`;
                }
            });
            
            css += `}\n\n`;
        });
        
        // Скачиваем файл
        const blob = new Blob([css], { type: 'text/css' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'responsive-styles.css';
        a.click();
        URL.revokeObjectURL(url);
        
        this.vb.showNotification('CSS экспортирован', 'success');
    }

    /**
     * Сброс адаптивных настроек
     */
    resetResponsive() {
        if (confirm('Вы уверены, что хотите сбросить все адаптивные настройки?')) {
            const elements = this.vb.dom.canvas.querySelectorAll('[data-responsive-styles]');
            elements.forEach(element => {
                element.removeAttribute('data-responsive-styles');
                element.classList.remove('responsive-element');
            });
            
            this.vb.showNotification('Адаптивные настройки сброшены', 'info');
        }
    }

    /**
     * Утилиты
     */
    getDeviceIcon(device) {
        const icons = {
            mobile: 'phone',
            tablet: 'tablet',
            desktop: 'laptop',
            wide: 'display'
        };
        return icons[device] || 'device';
    }

    getDeviceName(device) {
        const names = {
            mobile: 'Mobile',
            tablet: 'Tablet',
            desktop: 'Desktop',
            wide: 'Wide'
        };
        return names[device] || device;
    }

    /**
     * Получение текущего устройства
     */
    getCurrentDevice() {
        return this.currentBreakpoint;
    }

    /**
     * Проверка, является ли элемент адаптивным
     */
    isElementResponsive(element) {
        return element.hasAttribute('data-responsive-styles');
    }

    /**
     * Получение стилей для устройства
     */
    getElementStylesForDevice(element, device) {
        if (!this.isElementResponsive(element)) return {};
        
        const styles = JSON.parse(element.dataset.responsiveStyles || '{}');
        return styles[device] || {};
    }
}

// Экспорт класса
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResponsiveDesign;
} 