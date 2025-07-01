/**
 * Simple GrapesJS Editor - Упрощенная версия без проблемных функций
 * Обеспечивает стабильную работу базового редактора
 */

console.log('🚀 Loading Simple GrapesJS Editor...');

// Простая инициализация GrapesJS
function initSimpleEditor() {
    console.log('🚀 Initializing Simple GrapesJS Editor...');
    
    // Проверяем, что DOM готов
    if (!document.body) {
        console.warn('⚠️ Body not ready, waiting...');
        setTimeout(initSimpleEditor, 100);
        return;
    }
    
    // Проверяем, что контейнер существует
    const container = document.getElementById('gjs');
    if (!container) {
        console.error('❌ GrapesJS container not found');
        return;
    }
    
    try {
        // Инициализируем GrapesJS с базовыми настройками
        window.editor = grapesjs.init({
            container: '#gjs',
            height: '100%',
            width: 'auto',
            storageManager: {
                type: 'local',
                autosave: true,
                autoload: true,
                stepsBeforeSave: 1
            },
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
            blockManager: {
                appendTo: '#blocks',
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
                    }
                ]
            },
            layerManager: {
                appendTo: '.layers-container'
            },
            styleManager: {
                appendTo: '.styles-container',
                sectors: [{
                    name: 'Dimension',
                    open: false,
                    buildProps: ['width', 'min-height', 'padding'],
                    properties: [
                        {
                            type: 'integer',
                            name: 'The width',
                            property: 'width',
                            units: ['px', '%'],
                            defaults: 'auto',
                            min: 0,
                        }
                    ]
                }, {
                    name: 'Typography',
                    open: false,
                    buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-align', 'text-decoration', 'text-shadow'],
                    properties: [
                        { name: 'Font', property: 'font-family' },
                        { name: 'Weight', property: 'font-weight' },
                        { name: 'Font color', property: 'color' }
                    ]
                }, {
                    name: 'Decorations',
                    open: false,
                    buildProps: ['border-radius-c', 'background-color', 'border-radius', 'border', 'box-shadow', 'background'],
                    properties: [
                        { name: 'Border radius', property: 'border-radius' },
                        { name: 'Background', property: 'background' }
                    ]
                }]
            },
            traitManager: {
                appendTo: '.traits-container'
            },
            canvas: {
                styles: [
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'
                ],
                scripts: [
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'
                ]
            }
        });
        
        console.log('✅ Simple GrapesJS editor initialized successfully!');
        
        // Добавляем базовые функции
        setupBasicFunctions();
        
    } catch (error) {
        console.error('❌ Failed to initialize GrapesJS:', error);
    }
}

// Базовые функции редактора
function setupBasicFunctions() {
    if (!window.editor) return;
    
    // Функция сохранения
    window.savePage = async function() {
        try {
            const html = window.editor.getHtml();
            const css = window.editor.getCss();
            
            console.log('💾 Saving page...');
            console.log('HTML:', html);
            console.log('CSS:', css);
            
            // Здесь можно добавить сохранение на сервер
            showNotification('Page saved successfully!', 'success');
            
        } catch (error) {
            console.error('❌ Save failed:', error);
            showNotification('Save failed: ' + error.message, 'error');
        }
    };
    
    // Функция предпросмотра
    window.previewPage = function() {
        try {
            const html = window.editor.getHtml();
            const css = window.editor.getCss();
            
            const previewWindow = window.open('', '_blank');
            previewWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Preview</title>
                    <style>${css}</style>
                </head>
                <body>${html}</body>
                </html>
            `);
            previewWindow.document.close();
            
            showNotification('Preview opened in new window', 'info');
            
        } catch (error) {
            console.error('❌ Preview failed:', error);
            showNotification('Preview failed: ' + error.message, 'error');
        }
    };
    
    // Функция экспорта
    window.exportPage = function() {
        try {
            const html = window.editor.getHtml();
            const css = window.editor.getCss();
            
            const fullHtml = `<!DOCTYPE html>
<html>
<head>
    <title>Exported Page</title>
    <style>${css}</style>
</head>
<body>${html}</body>
</html>`;
            
            const blob = new Blob([fullHtml], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'page.html';
            a.click();
            
            URL.revokeObjectURL(url);
            
            showNotification('Page exported successfully!', 'success');
            
        } catch (error) {
            console.error('❌ Export failed:', error);
            showNotification('Export failed: ' + error.message, 'error');
        }
    };
    
    console.log('✅ Basic functions setup completed');
}

// Функция уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Автоматическое удаление через 5 секунд
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Инициализация при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSimpleEditor);
} else {
    initSimpleEditor();
}

console.log('✅ Simple Editor Module Loaded!'); 