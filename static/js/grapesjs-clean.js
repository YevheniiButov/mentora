// ===============================================
// CLEAN GRAPESJS INITIALIZATION
// ===============================================

// Глобальные переменные
let editor = null;
let isInitialized = false;

// Конфигурация
const CONFIG = {
    autosave: {
        enabled: true,
        interval: 30000 // 30 секунд
    },
    storage: {
        type: 'local',
        autosave: true,
        autoload: true,
        stepsBeforeSave: 1
    }
};

// ===============================================
// UTILITY FUNCTIONS
// ===============================================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateStatus(message) {
    const statusEl = document.querySelector('.editor-status');
    if (statusEl) {
        statusEl.textContent = message;
    }
}

// ===============================================
// DEPENDENCY CHECK
// ===============================================

function checkDependencies() {
    console.log('🔍 Checking dependencies...');
    
    // Проверяем GrapesJS
    if (typeof grapesjs === 'undefined') {
        console.error('❌ GrapesJS not loaded');
        showNotification('GrapesJS library not loaded', 'danger');
        return false;
    }
    
    // Проверяем Bootstrap (для модальных окон)
    if (typeof bootstrap === 'undefined') {
        console.warn('⚠️ Bootstrap not loaded (modal functionality may not work)');
    }
    
    console.log('✅ Dependencies check passed');
    return true;
}

// ===============================================
// DOM ELEMENTS CHECK
// ===============================================

function checkDOMElements() {
    console.log('🔍 Checking DOM elements...');
    
    const requiredElements = [
        '#gjs',
        '.blocks-container',
        '.styles-container',
        '.layers-container',
        '.traits-container'
    ];
    
    const missingElements = [];
    
    for (let selector of requiredElements) {
        const element = document.querySelector(selector);
        if (!element) {
            missingElements.push(selector);
            console.error(`❌ Required element not found: ${selector}`);
        }
    }
    
    if (missingElements.length > 0) {
        showNotification(`Missing DOM elements: ${missingElements.join(', ')}`, 'danger');
        return false;
    }
    
    console.log('✅ All DOM elements found');
    return true;
}

// ===============================================
// GRAPESJS INITIALIZATION
// ===============================================

function initCleanGrapesJS() {
    console.log('🚀 Initializing Clean GrapesJS...');
    
    // Проверяем, не инициализирован ли уже редактор
    if (isInitialized) {
        console.log('✅ Editor already initialized');
        return;
    }
    
    // Проверяем зависимости
    if (!checkDependencies()) {
        return;
    }
    
    // Проверяем DOM элементы
    if (!checkDOMElements()) {
        return;
    }
    
    try {
        // Инициализируем GrapesJS
        editor = grapesjs.init({
            container: '#gjs',
            height: '100%',
            width: 'auto',
            
            // Storage Manager
            storageManager: {
                type: CONFIG.storage.type,
                autosave: CONFIG.storage.autosave,
                autoload: CONFIG.storage.autoload,
                stepsBeforeSave: CONFIG.storage.stepsBeforeSave
            },
            
            // Device Manager
            deviceManager: {
                devices: [
                    {
                        name: 'Desktop',
                        width: '',
                    },
                    {
                        name: 'Tablet',
                        width: '768px',
                        widthMedia: '992px',
                    },
                    {
                        name: 'Mobile',
                        width: '320px',
                        widthMedia: '480px',
                    }
                ]
            },
            
            // Block Manager
            blockManager: {
                appendTo: '.blocks-container',
                blocks: [
                    {
                        id: 'section',
                        label: 'Section',
                        attributes: { class: 'fa fa-square-o' },
                        content: `<section class="section">
                            <h2>This is a section</h2>
                            <div>This is a box</div>
                        </section>`,
                    },
                    {
                        id: 'text',
                        label: 'Text',
                        attributes: { class: 'fa fa-text-width' },
                        content: '<div data-gjs-type="text">Insert your text here</div>',
                    },
                    {
                        id: 'image',
                        label: 'Image',
                        attributes: { class: 'fa fa-image' },
                        content: { type: 'image' },
                        activate: true,
                    },
                    {
                        id: 'button',
                        label: 'Button',
                        attributes: { class: 'fa fa-square' },
                        content: '<button class="btn btn-primary">Click me</button>',
                    },
                    {
                        id: 'div',
                        label: 'Div',
                        attributes: { class: 'fa fa-square-o' },
                        content: '<div style="padding: 20px; border: 1px solid #ccc;"><p>Div content</p></div>',
                    }
                ]
            },
            
            // Layer Manager
            layerManager: {
                appendTo: '.layers-container'
            },
            
            // Style Manager
            styleManager: {
                appendTo: '.styles-container',
                sectors: [
                    {
                        name: 'Dimension',
                        open: false,
                        buildProps: ['width', 'min-height', 'padding'],
                        properties: [
                            {
                                type: 'integer',
                                name: 'Width',
                                property: 'width',
                                units: ['px', '%'],
                                defaults: 'auto',
                                min: 0,
                            }
                        ]
                    },
                    {
                        name: 'Typography',
                        open: false,
                        buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-align', 'text-decoration', 'text-shadow'],
                        properties: [
                            { name: 'Font', property: 'font-family' },
                            { name: 'Weight', property: 'font-weight' },
                            { name: 'Font color', property: 'color' }
                        ]
                    },
                    {
                        name: 'Decorations',
                        open: false,
                        buildProps: ['border-radius-c', 'background-color', 'border-radius', 'border', 'box-shadow', 'background'],
                        properties: [
                            { name: 'Border radius', property: 'border-radius' },
                            { name: 'Background', property: 'background' }
                        ]
                    }
                ]
            },
            
            // Trait Manager
            traitManager: {
                appendTo: '.traits-container'
            },
            
            // Panels
            panels: {
                defaults: [
                    {
                        id: 'basic-actions',
                        el: '.panel__basic-actions',
                        buttons: [
                            {
                                id: 'visibility',
                                active: true,
                                className: 'btn-toggle-borders',
                                label: '<u>B</u>',
                                command: 'sw-visibility',
                            },
                            {
                                id: 'export',
                                className: 'btn-open-export',
                                label: 'Exp',
                                command: 'export-template',
                                context: 'export-template',
                            },
                            {
                                id: 'show-json',
                                className: 'btn-show-json',
                                label: 'JSON',
                                context: 'show-json',
                                command(editor) {
                                    editor.Modal.setTitle('Components JSON')
                                        .setContent(`<textarea style="width:100%; height: 250px;">
                                        ${JSON.stringify(editor.getComponents(), null, 2)}
                                    </textarea>`)
                                        .open();
                                },
                            }
                        ],
                    },
                ]
            },
            
            // Плагины (пока пусто, чтобы избежать конфликтов)
            plugins: [],
            pluginsOpts: {}
        });
        
        // Настраиваем события
        setupEditorEvents();
        
        // Настраиваем автосохранение
        if (CONFIG.autosave.enabled) {
            setupAutoSave();
        }
        
        isInitialized = true;
        updateStatus('Editor ready');
        showNotification('GrapesJS initialized successfully!', 'success');
        
        console.log('✅ Clean GrapesJS initialized successfully');
        
    } catch (error) {
        console.error('❌ GrapesJS initialization failed:', error);
        showNotification('Failed to initialize editor: ' + error.message, 'danger');
        updateStatus('Initialization failed');
    }
}

// ===============================================
// EDITOR EVENTS
// ===============================================

function setupEditorEvents() {
    if (!editor) return;
    
    // Component selection events
    editor.on('component:selected', (component) => {
        console.log('Component selected:', component);
    });
    
    // Content change events
    editor.on('component:add component:remove component:update', () => {
        updateStatus('Modified');
        window.hasUnsavedChanges = true;
    });
    
    // Device change events
    editor.on('change:device', () => {
        const device = editor.getDevice();
        console.log('Device changed to:', device);
    });
    
    console.log('✅ Editor events configured');
}

// ===============================================
// AUTO SAVE
// ===============================================

function setupAutoSave() {
    if (!editor) return;
    
    setInterval(() => {
        if (window.hasUnsavedChanges) {
            saveProject();
        }
    }, CONFIG.autosave.interval);
    
    console.log('✅ Auto-save configured');
}

// ===============================================
// PROJECT OPERATIONS
// ===============================================

function saveProject() {
    if (!editor) {
        showNotification('Editor not initialized', 'warning');
        return;
    }
    
    try {
        const projectData = {
            html: editor.getHtml(),
            css: editor.getCss(),
            components: editor.getComponents(),
            timestamp: new Date().toISOString()
        };
        
        // Сохраняем в localStorage
        localStorage.setItem('grapesjs-project', JSON.stringify(projectData));
        
        window.hasUnsavedChanges = false;
        updateStatus('Saved');
        showNotification('Project saved successfully!', 'success');
        
        console.log('✅ Project saved');
        
    } catch (error) {
        console.error('❌ Save failed:', error);
        showNotification('Failed to save project: ' + error.message, 'danger');
    }
}

function loadProject() {
    if (!editor) {
        showNotification('Editor not initialized', 'warning');
        return;
    }
    
    try {
        const projectData = localStorage.getItem('grapesjs-project');
        if (!projectData) {
            showNotification('No saved project found', 'info');
            return;
        }
        
        const data = JSON.parse(projectData);
        
        if (data.html) {
            editor.setComponents(data.html);
        }
        if (data.css) {
            editor.setStyle(data.css);
        }
        
        window.hasUnsavedChanges = false;
        updateStatus('Loaded');
        showNotification('Project loaded successfully!', 'success');
        
        console.log('✅ Project loaded');
        
    } catch (error) {
        console.error('❌ Load failed:', error);
        showNotification('Failed to load project: ' + error.message, 'danger');
    }
}

function previewProject() {
    if (!editor) {
        showNotification('Editor not initialized', 'warning');
        return;
    }
    
    try {
        const html = editor.getHtml();
        const css = editor.getCss();
        const fullPage = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Preview</title>
                <style>${css}</style>
            </head>
            <body>${html}</body>
            </html>
        `;
        
        const previewFrame = document.getElementById('previewFrame');
        if (previewFrame) {
            previewFrame.srcdoc = fullPage;
        }
        
        const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
        previewModal.show();
        
        console.log('✅ Preview opened');
        
    } catch (error) {
        console.error('❌ Preview failed:', error);
        showNotification('Failed to open preview: ' + error.message, 'danger');
    }
}

function exportProject() {
    if (!editor) {
        showNotification('Editor not initialized', 'warning');
        return;
    }
    
    try {
        const html = editor.getHtml();
        const css = editor.getCss();
        
        const fullPage = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Exported Page</title>
    <style>${css}</style>
</head>
<body>${html}</body>
</html>`;
        
        const blob = new Blob([fullPage], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'exported-page.html';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showNotification('Project exported successfully!', 'success');
        console.log('✅ Project exported');
        
    } catch (error) {
        console.error('❌ Export failed:', error);
        showNotification('Failed to export project: ' + error.message, 'danger');
    }
}

// ===============================================
// GLOBAL FUNCTIONS (для onclick в HTML)
// ===============================================

window.saveProject = saveProject;
window.loadProject = loadProject;
window.previewProject = previewProject;
window.exportProject = exportProject;

// ===============================================
// INITIALIZATION
// ===============================================

// Ждем загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, initializing GrapesJS...');
    
    // Небольшая задержка для полной загрузки всех ресурсов
    setTimeout(() => {
        initCleanGrapesJS();
    }, 100);
});

console.log(`
🚀 Clean GrapesJS Module Loaded!
================================
Version: 1.0.0 - Clean Edition
Status: Ready for initialization

📋 Features:
- Clean GrapesJS integration
- Dependency checking
- DOM element validation
- Auto-save functionality
- Project save/load
- Preview functionality
- Export functionality
- Error handling

🎯 Will initialize automatically when DOM is ready
`); 