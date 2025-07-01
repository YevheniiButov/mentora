// Inline JavaScript for GrapesJS Builder
// This file contains all the inline JavaScript from the template

// Глобальные переменные
window.pageId = window.pageId || null;
window.csrfToken = document.querySelector('[name=csrf-token]')?.content || '';

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Professional HTML Editor Loading...');
    
    // Скрыть загрузочный экран через 2 секунды
    setTimeout(() => {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.opacity = '0';
            setTimeout(() => loadingOverlay.style.display = 'none', 300);
        }
    }, 2000);
    
    // Проверить доступность библиотек
    console.log('📋 Checking libraries...');
    console.log('GrapesJS:', typeof grapesjs !== 'undefined' ? '✅' : '❌');
    console.log('THREE.js:', typeof THREE !== 'undefined' ? '✅' : '❌');
    console.log('CodeMirror:', typeof CodeMirror !== 'undefined' ? '✅' : '❌');
    
    // Инициализация редактора
    if (typeof initAdvancedEditor === 'function') {
        initAdvancedEditor();
    } else {
        console.error('❌ Advanced editor initialization function not found');
        // Fallback - инициализация базового редактора
        setTimeout(initFallbackEditor, 1000);
    }
});

// Fallback editor если основной не загрузился
function initFallbackEditor() {
    console.log('🔄 Initializing fallback editor...');
    
    if (typeof grapesjs === 'undefined') {
        console.error('❌ GrapesJS not available');
        const statusEl = document.getElementById('save-status');
        if (statusEl) statusEl.textContent = 'Error - GrapesJS not loaded';
        return;
    }
    
    // Базовая инициализация
    window.editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        storageManager: false,
        blockManager: {
            appendTo: '.gjs-blocks-c'
        },
        styleManager: {
            appendTo: '.gjs-sm-c'
        },
        layerManager: {
            appendTo: '.gjs-lm-c'
        }
    });
    
    // Базовые функции
    window.saveProject = function() {
        const data = {
            html: window.editor.getHtml(),
            css: window.editor.getCss()
        };
        localStorage.setItem('dental-editor-fallback', JSON.stringify(data));
        showNotification('Project saved to localStorage', 'success');
    };
    
    window.previewProject = function() {
        const html = window.editor.getHtml();
        const css = window.editor.getCss();
        const fullPage = '<!DOCTYPE html><html><head><style>' + css + '</style></head><body>' + html + '</body></html>';
        const previewFrame = document.getElementById('preview-frame');
        if (previewFrame) {
            previewFrame.srcdoc = fullPage;
        }
        const previewModal = document.getElementById('preview-modal');
        if (previewModal) {
            previewModal.style.display = 'block';
        }
    };
    
    // Загрузить базовый контент
    window.editor.setComponents(
        '<section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center;">' +
        '<h1 style="font-size: 3em; margin-bottom: 20px;">🦷 Dental Academy</h1>' +
        '<p style="font-size: 1.2em; margin-bottom: 30px;">Professional HTML Editor</p>' +
        '<a href="#" style="background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px;">Get Started</a>' +
        '</section>'
    );
    
    const statusEl = document.getElementById('save-status');
    if (statusEl) statusEl.textContent = 'Ready (Fallback Mode)';
    console.log('✅ Fallback editor initialized');
}

// Дополнительные функции
function loadTemplates() {
    const templatesGrid = document.getElementById('templates-grid');
    if (templatesGrid) {
        templatesGrid.innerHTML = 
            '<div class="template-item" onclick="loadTemplate(\'hero\')">' +
            '<div class="template-preview">🦷</div>' +
            '<h4>Hero Section</h4>' +
            '<p>Главная секция с градиентом</p>' +
            '</div>' +
            '<div class="template-item" onclick="loadTemplate(\'content\')">' +
            '<div class="template-preview">📝</div>' +
            '<h4>Content Block</h4>' +
            '<p>Блок с контентом</p>' +
            '</div>' +
            '<div class="template-item" onclick="loadTemplate(\'form\')">' +
            '<div class="template-preview">📋</div>' +
            '<h4>Contact Form</h4>' +
            '<p>Контактная форма</p>' +
            '</div>' +
            '<div class="template-item" onclick="loadTemplate(\'gallery\')">' +
            '<div class="template-preview">🖼️</div>' +
            '<h4>Image Gallery</h4>' +
            '<p>Галерея изображений</p>' +
            '</div>';
    }
}

function loadVersions() {
    const versionsContainer = document.getElementById('versions-container');
    if (versionsContainer) {
        const savedVersions = JSON.parse(localStorage.getItem('dental-editor-versions') || '[]');
        if (savedVersions.length === 0) {
            versionsContainer.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">Нет сохраненных версий</p>';
        } else {
            versionsContainer.innerHTML = savedVersions.map((version, index) => 
                '<div class="version-item" onclick="loadVersion(' + index + ')">' +
                '<div class="version-info">' +
                '<h4>Версия ' + version.version + '</h4>' +
                '<p>' + new Date(version.timestamp).toLocaleString() + '</p>' +
                '</div>' +
                '</div>'
            ).join('');
        }
    }
}

function loadTemplate(templateName) {
    if (!window.editor) return;
    
    const templates = {
        hero: 
            '<section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center;">' +
            '<h1 style="font-size: 3em; margin-bottom: 20px;">🦷 Dental Academy</h1>' +
            '<p style="font-size: 1.2em; margin-bottom: 30px;">Professional Dental Education</p>' +
            '<a href="#" style="background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px;">Get Started</a>' +
            '</section>',
        content: 
            '<section style="padding: 60px 20px; background: white;">' +
            '<div style="max-width: 1200px; margin: 0 auto;">' +
            '<h2 style="text-align: center; margin-bottom: 40px;">Our Services</h2>' +
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">' +
            '<div style="text-align: center; padding: 20px;">' +
            '<div style="font-size: 3em; margin-bottom: 15px;">🦷</div>' +
            '<h3>Dental Care</h3>' +
            '<p>Professional dental care and treatment</p>' +
            '</div>' +
            '<div style="text-align: center; padding: 20px;">' +
            '<div style="font-size: 3em; margin-bottom: 15px;">💉</div>' +
            '<h3>Prevention</h3>' +
            '<p>Preventive dental care</p>' +
            '</div>' +
            '<div style="text-align: center; padding: 20px;">' +
            '<div style="font-size: 3em; margin-bottom: 15px;">🦷</div>' +
            '<h3>Education</h3>' +
            '<p>Dental education and training</p>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</section>',
        form: 
            '<section style="padding: 60px 20px; background: #f8f9fa;">' +
            '<div style="max-width: 600px; margin: 0 auto;">' +
            '<h2 style="text-align: center; margin-bottom: 40px;">Contact Us</h2>' +
            '<form style="display: grid; gap: 20px;">' +
            '<input type="text" placeholder="Your Name" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">' +
            '<input type="email" placeholder="Your Email" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">' +
            '<textarea placeholder="Your Message" rows="5" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;"></textarea>' +
            '<button type="submit" style="background: #667eea; color: white; padding: 15px; border: none; border-radius: 5px; cursor: pointer;">Send Message</button>' +
            '</form>' +
            '</div>' +
            '</section>',
        gallery: 
            '<section style="padding: 60px 20px; background: white;">' +
            '<div style="max-width: 1200px; margin: 0 auto;">' +
            '<h2 style="text-align: center; margin-bottom: 40px;">Our Gallery</h2>' +
            '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">' +
            '<div style="background: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">🖼️ Image 1</div>' +
            '<div style="background: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">🖼️ Image 2</div>' +
            '<div style="background: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">🖼️ Image 3</div>' +
            '<div style="background: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">🖼️ Image 4</div>' +
            '</div>' +
            '</div>' +
            '</section>'
    };
    
    if (templates[templateName]) {
        window.editor.addComponent(templates[templateName]);
        showNotification('Шаблон "' + templateName + '" загружен', 'success');
        window.closeTemplates();
    }
}

function loadVersion(index) {
    const savedVersions = JSON.parse(localStorage.getItem('dental-editor-versions') || '[]');
    if (savedVersions[index] && window.editor) {
        window.editor.setComponents(savedVersions[index].html);
        window.editor.setStyle(savedVersions[index].css);
        showNotification('Версия ' + savedVersions[index].version + ' загружена', 'success');
        window.closeVersions();
    }
}

function deleteVersion(index) {
    const savedVersions = JSON.parse(localStorage.getItem('dental-editor-versions') || '[]');
    savedVersions.splice(index, 1);
    localStorage.setItem('dental-editor-versions', JSON.stringify(savedVersions));
    loadVersions();
    showNotification('Версия удалена', 'info');
}

// Обработчик загрузки файлов
document.addEventListener('DOMContentLoaded', function() {
    const assetUpload = document.getElementById('asset-upload');
    if (assetUpload) {
        assetUpload.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 0) {
                Array.from(files).forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const assetGrid = document.getElementById('assets-grid');
                        if (assetGrid) {
                            const assetItem = document.createElement('div');
                            assetItem.className = 'asset-item';
                            assetItem.innerHTML = 
                                '<div class="asset-preview">' +
                                (file.type.startsWith('image/') ? '<img src="' + e.target.result + '" alt="' + file.name + '">' : '📄 ' + file.name) +
                                '</div>' +
                                '<div class="asset-info">' +
                                '<span>' + file.name + '</span>' +
                                '<small>' + (file.size / 1024).toFixed(1) + ' KB</small>' +
                                '</div>';
                            assetItem.onclick = () => addAssetToPage(e.target.result, file.name, file.type);
                            assetGrid.appendChild(assetItem);
                        }
                    };
                    reader.readAsDataURL(file);
                });
                showNotification(files.length + ' файл(ов) загружено', 'success');
            }
        });
    }
});

function addAssetToPage(src, name, type) {
    if (window.editor) {
        if (type.startsWith('image/')) {
            window.editor.addComponent('<img src="' + src + '" alt="' + name + '" style="max-width: 100%; height: auto;">');
        } else {
            window.editor.addComponent('<a href="' + src + '" download="' + name + '" style="display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">📄 ' + name + '</a>');
        }
        showNotification('Ассет "' + name + '" добавлен на страницу', 'success');
    }
}

// Обработчик 3D моделей
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.model-item').forEach(item => {
        item.addEventListener('click', function() {
            const modelName = this.dataset.model;
            window.currentModel = modelName;
            
            // Показать модальное окно с 3D моделью
            const modal = document.getElementById('model-viewer-modal');
            if (modal) {
                modal.style.display = 'block';
                
                // Инициализировать Three.js сцены если еще не инициализирована
                if (typeof THREE !== 'undefined' && !window.currentScene) {
                    init3DScene(modelName);
                }
            }
        });
    });
});

function init3DScene(modelName) {
    const container = document.getElementById('3d-viewer');
    if (!container) return;
    
    // Создать сцену
    window.currentScene = new THREE.Scene();
    window.currentScene.background = new THREE.Color(0xf0f0f0);
    
    // Создать камеру
    window.currentCamera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    window.currentCamera.position.z = 5;
    
    // Создать рендерер
    window.currentRenderer = new THREE.WebGLRenderer({ antialias: true });
    window.currentRenderer.setSize(container.clientWidth, container.clientHeight);
    container.innerHTML = '';
    container.appendChild(window.currentRenderer.domElement);
    
    // Создать геометрию зуба (простая замена для 3D модели)
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshPhongMaterial({ 
        color: 0xffffff,
        transparent: true,
        opacity: 0.8
    });
    const tooth = new THREE.Mesh(geometry, material);
    window.currentScene.add(tooth);
    
    // Добавить освещение
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 5, 5);
    window.currentScene.add(light);
    
    const ambientLight = new THREE.AmbientLight(0x404040);
    window.currentScene.add(ambientLight);
    
    // Рендеринг
    window.currentRenderer.render(window.currentScene, window.currentCamera);
    
    // Добавить OrbitControls если доступны
    if (typeof THREE.OrbitControls !== 'undefined') {
        const controls = new THREE.OrbitControls(window.currentCamera, window.currentRenderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            window.currentRenderer.render(window.currentScene, window.currentCamera);
        }
        animate();
    }
}

// Utility функция для уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'notification ' + type;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Переключение табов
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.panel-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const target = this.dataset.tab;
            const parent = this.closest('.editor-left, .editor-right');
            
            parent.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
            parent.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            const targetPane = parent.querySelector('#' + target + '-tab');
            if (targetPane) targetPane.classList.add('active');
        });
    });
});

// Переключение устройств
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.device-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.device-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            if (window.editor) {
                const device = this.dataset.device;
                window.editor.setDevice(device);
            }
        });
    });
});

// Горячие клавиши
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 's':
                e.preventDefault();
                if (window.savePage) window.savePage();
                break;
            case 'p':
                e.preventDefault();
                if (window.previewPage) window.previewPage();
                break;
            case 'z':
                e.preventDefault();
                if (e.shiftKey) {
                    if (window.redo) window.redo();
                } else {
                    if (window.undo) window.undo();
                }
                break;
        }
    }
    
    if (e.key === 'Escape') {
        window.closePreview();
        window.closeTemplates();
        window.closeVersions();
        window.closeModelViewer();
    }
});

console.log(
    '🚀 Professional HTML Editor Initializing...\n' +
    '==========================================\n' +
    'Features:\n' +
    '- Full GrapesJS editor with all panels\n' +
    '- 3D dental models with Three.js\n' +
    '- Template system\n' +
    '- Version control\n' +
    '- Advanced components\n' +
    '- Professional UI/UX\n\n' +
    '🎯 Ready for professional web development!'
);

// Инициализация GrapesJS
function initGrapesJS() {
    console.log('🚀 Professional HTML Editor Initializing...');
    console.log('==========================================');
    console.log('Features:');
    console.log('- Full GrapesJS editor with all panels');
    console.log('- 3D dental models with Three.js');
    console.log('- Template system');
    console.log('- Version control');
    console.log('- Advanced components');
    console.log('- Professional UI/UX');
    console.log('');
    console.log('🎯 Ready for professional web development!');
    
    // Проверяем, что DOM готов
    if (!document.body) {
        console.warn('⚠️ Body not ready, waiting...');
        setTimeout(initGrapesJS, 100);
        return;
    }
    
    // Проверяем, что контейнер существует
    const container = document.getElementById('gjs');
    if (!container) {
        console.error('❌ GrapesJS container not found');
        return;
    }
    
    try {
        // Инициализируем GrapesJS с расширенными настройками
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
                    {
                        id: 'panel-devices',
                        el: '.panel__devices',
                        buttons: [
                            {
                                id: 'device-desktop',
                                label: '<i class="fa fa-desktop"></i>',
                                command: 'set-device-desktop',
                                active: true,
                                togglable: false,
                            },
                            {
                                id: 'device-tablet',
                                label: '<i class="fa fa-tablet"></i>',
                                command: 'set-device-tablet',
                                togglable: false,
                            },
                            {
                                id: 'device-mobile',
                                label: '<i class="fa fa-mobile"></i>',
                                command: 'set-device-mobile',
                                togglable: false,
                            }
                        ],
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
        
        console.log('✅ Fallback editor initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize GrapesJS:', error);
    }
}

// Инициализация при загрузке DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGrapesJS);
} else {
    initGrapesJS();
} 