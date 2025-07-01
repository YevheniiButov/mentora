// Enhanced GrapesJS Builder with Bilingual Support and Template Editing
// Professional HTML Editor for Dental Academy

// Глобальные переменные
window.pageId = window.pageId || null;
window.currentLanguage = localStorage.getItem('editor-language') || 
    (navigator.language.startsWith('ru') ? 'ru' : 'en');

// Функция получения CSRF токена
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
           document.querySelector('[name="csrf-token"]')?.value ||
           document.querySelector('input[name="csrf_token"]')?.value || '';
}

// Функция для авторизованных запросов
async function makeAuthenticatedRequest(url, options = {}) {
    const csrfToken = getCSRFToken();
    console.log('🔐 CSRF Token:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'Not found');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            ...options.headers
        },
        credentials: 'same-origin'
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        
        // Логируем статус ответа для отладки
        console.log(`📡 ${options.method || 'GET'} ${url} - Status: ${response.status}`);
        
        // Обрабатываем ошибки авторизации
        if (response.status === 401 || response.status === 403) {
            console.error('❌ Authentication error:', response.status);
            showNotification('Session expired. Please log in again.', 'error');
            
            // Редиректим на страницу логина
            setTimeout(() => {
                window.location.href = '/en/login?next=' + encodeURIComponent(window.location.pathname);
            }, 2000);
            
            throw new Error('Authentication failed');
        }
        
        return response;
    } catch (error) {
        console.error('❌ Request error:', error);
        throw error;
    }
}

// Двуязычные тексты
const translations = {
    en: {
        save: 'Save',
        preview: 'Preview',
        deploy: 'Deploy',
        load_template: 'Load Template',
        css_variables: 'CSS Variables',
        template_selector: 'Template Selector',
        language_switcher: 'Language',
        component_library: 'Components',
        dental_blocks: 'Dental Blocks',
        save_success: 'Template saved successfully',
        save_error: 'Error saving template',
        load_success: 'Template loaded successfully',
        load_error: 'Error loading template',
        preview_ready: 'Preview ready',
        deploy_success: 'Deployed to production',
        deploy_error: 'Deployment failed',
        hero_section: 'Hero Section',
        content_block: 'Content Block',
        contact_form: 'Contact Form',
        image_gallery: 'Image Gallery',
        dental_service: 'Dental Service',
        patient_testimonial: 'Patient Testimonial',
        appointment_form: 'Appointment Form',
        treatment_plan: 'Treatment Plan',
        primary_color: 'Primary Color',
        secondary_color: 'Secondary Color',
        accent_color: 'Accent Color',
        text_color: 'Text Color',
        background_color: 'Background Color',
        border_radius: 'Border Radius',
        close: 'Close',
        apply: 'Apply',
        cancel: 'Cancel',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        warning: 'Warning'
    },
    ru: {
        save: 'Сохранить',
        preview: 'Предпросмотр',
        deploy: 'Опубликовать',
        load_template: 'Загрузить шаблон',
        css_variables: 'CSS переменные',
        template_selector: 'Выбор шаблона',
        language_switcher: 'Язык',
        component_library: 'Компоненты',
        dental_blocks: 'Стоматологические блоки',
        save_success: 'Шаблон успешно сохранен',
        save_error: 'Ошибка сохранения шаблона',
        load_success: 'Шаблон успешно загружен',
        load_error: 'Ошибка загрузки шаблона',
        preview_ready: 'Предпросмотр готов',
        deploy_success: 'Опубликовано в продакшн',
        deploy_error: 'Ошибка публикации',
        hero_section: 'Главная секция',
        content_block: 'Блок контента',
        contact_form: 'Контактная форма',
        image_gallery: 'Галерея изображений',
        dental_service: 'Стоматологическая услуга',
        patient_testimonial: 'Отзыв пациента',
        appointment_form: 'Форма записи',
        treatment_plan: 'План лечения',
        primary_color: 'Основной цвет',
        secondary_color: 'Дополнительный цвет',
        accent_color: 'Акцентный цвет',
        text_color: 'Цвет текста',
        background_color: 'Цвет фона',
        border_radius: 'Радиус границ',
        close: 'Закрыть',
        apply: 'Применить',
        cancel: 'Отмена',
        loading: 'Загрузка...',
        error: 'Ошибка',
        success: 'Успешно',
        warning: 'Предупреждение'
    }
};

// Функция перевода
function t(key) {
    return translations[window.currentLanguage]?.[key] || translations.en[key] || key;
}

// Функция переключения языка
function switchLanguage(lang) {
    window.currentLanguage = lang;
    localStorage.setItem('editor-language', lang);
    location.reload();
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Enhanced GrapesJS Editor Loading...');
    console.log('Language:', window.currentLanguage);
    
    // Скрыть загрузочный экран
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
    console.log('Monaco Editor:', typeof monaco !== 'undefined' ? '✅' : '❌');
    
    // Инициализация редактора
    if (typeof grapesjs !== 'undefined') {
        initEnhancedGrapesJS();
    } else {
        console.error('❌ GrapesJS not available');
        showNotification('GrapesJS library not loaded', 'error');
    }
});

// Основная инициализация GrapesJS
function initEnhancedGrapesJS() {
    console.log('🚀 Initializing Enhanced GrapesJS Editor...');
    
    // Проверяем контейнер
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
            
            // Storage Manager
            storageManager: {
                type: 'local',
                autosave: true,
                autoload: true,
                stepsBeforeSave: 1,
                id: 'dental-academy-editor'
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
            
            // Panels Configuration
            panels: {
                defaults: [
                    // Основные действия
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
                    // Устройства
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
            
            // Block Manager с Dental Academy блоками
            blockManager: {
                appendTo: '#blocks',
                blocks: [
                    // Базовые блоки
                    {
                        id: 'section',
                        label: t('content_block'),
                        attributes: { class: 'fa fa-square-o' },
                        content: `<section class="section">
                            <h2>${t('content_block')}</h2>
                            <div>This is a content block</div>
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
                    
                    // Dental Academy специфичные блоки
                    {
                        id: 'dental-hero',
                        label: t('hero_section'),
                        attributes: { class: 'fa fa-star' },
                        content: `<section class="dental-hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center;">
                            <h1 style="font-size: 3em; margin-bottom: 20px;">🦷 Dental Academy</h1>
                            <p style="font-size: 1.2em; margin-bottom: 30px;">Professional Dental Education</p>
                            <a href="#" style="background: rgba(255,255,255,0.2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px;">Get Started</a>
                        </section>`,
                    },
                    {
                        id: 'dental-service',
                        label: t('dental_service'),
                        attributes: { class: 'fa fa-medkit' },
                        content: `<div class="dental-service" style="text-align: center; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <div style="font-size: 3em; margin-bottom: 15px;">🦷</div>
                            <h3>Dental Care</h3>
                            <p>Professional dental care and treatment</p>
                            <button style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Learn More</button>
                        </div>`,
                    },
                    {
                        id: 'contact-form',
                        label: t('contact_form'),
                        attributes: { class: 'fa fa-envelope' },
                        content: `<section class="contact-form" style="padding: 60px 20px; background: #f8f9fa;">
                            <div style="max-width: 600px; margin: 0 auto;">
                                <h2 style="text-align: center; margin-bottom: 40px;">Contact Us</h2>
                                <form style="display: grid; gap: 20px;">
                                    <input type="text" placeholder="Your Name" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                                    <input type="email" placeholder="Your Email" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                                    <textarea placeholder="Your Message" rows="5" style="padding: 15px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                                    <button type="submit" style="background: #667eea; color: white; padding: 15px; border: none; border-radius: 5px; cursor: pointer;">Send Message</button>
                                </form>
                            </div>
                        </section>`,
                    },
                    {
                        id: 'patient-testimonial',
                        label: t('patient_testimonial'),
                        attributes: { class: 'fa fa-quote-left' },
                        content: `<div class="patient-testimonial" style="background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0;">
                            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                                <div style="width: 60px; height: 60px; background: #667eea; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5em; margin-right: 15px;">👤</div>
                                <div>
                                    <h4 style="margin: 0;">Patient Name</h4>
                                    <p style="margin: 0; color: #666;">Dental Patient</p>
                                </div>
                            </div>
                            <p style="font-style: italic; color: #555;">"Excellent dental care and professional service. Highly recommended!"</p>
                        </div>`,
                    }
                ]
            },
            
            // Layer Manager
            layerManager: {
                appendTo: '.layers-container'
            },
            
            // Style Manager с расширенными секциями
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
            
            // Canvas
            canvas: {
                styles: [
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'
                ],
                scripts: [
                    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'
                ]
            }
        });
        
        // Добавляем кастомные команды
        addCustomCommands();
        
        // Добавляем кастомные панели
        addCustomPanels();
        
        // Добавляем обработчики клавиатуры
        addKeyboardShortcuts();
        
        // Инициализируем API интеграцию
        initAPIIntegration();
        
        console.log('✅ Enhanced GrapesJS editor initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize GrapesJS:', error);
        showNotification('Failed to initialize editor', 'error');
    }
}

// Добавление кастомных команд
function addCustomCommands() {
    const editor = window.editor;
    
    // Команда загрузки шаблона
    editor.Commands.add('load-template', {
        run(editor, sender, options) {
            showTemplateSelector();
        }
    });
    
    // Команда сохранения шаблона
    editor.Commands.add('save-template', {
        run(editor, sender, options) {
            saveTemplate();
        }
    });
    
    // Команда предпросмотра
    editor.Commands.add('preview-template', {
        run(editor, sender, options) {
            previewTemplate();
        }
    });
    
    // Команда публикации
    editor.Commands.add('deploy-template', {
        run(editor, sender, options) {
            deployTemplate();
        }
    });
    
    // Команда переключения языка
    editor.Commands.add('switch-language', {
        run(editor, sender, options) {
            const newLang = window.currentLanguage === 'en' ? 'ru' : 'en';
            switchLanguage(newLang);
        }
    });
    
    // Команда редактора CSS переменных
    editor.Commands.add('css-variables', {
        run(editor, sender, options) {
            showCSSVariablesEditor();
        }
    });
}

// Добавление кастомных панелей
function addCustomPanels() {
    const editor = window.editor;
    
    // Панель с дополнительными кнопками
    const panel = editor.Panels.addPanel({
        id: 'custom-panel',
        visible: true,
        buttons: [
            {
                id: 'load-template-btn',
                className: 'btn-load-template',
                label: `<i class="fa fa-folder-open"></i> ${t('load_template')}`,
                command: 'load-template',
            },
            {
                id: 'save-template-btn',
                className: 'btn-save-template',
                label: `<i class="fa fa-save"></i> ${t('save')}`,
                command: 'save-template',
            },
            {
                id: 'preview-template-btn',
                className: 'btn-preview-template',
                label: `<i class="fa fa-eye"></i> ${t('preview')}`,
                command: 'preview-template',
            },
            {
                id: 'deploy-template-btn',
                className: 'btn-deploy-template',
                label: `<i class="fa fa-rocket"></i> ${t('deploy')}`,
                command: 'deploy-template',
            },
            {
                id: 'css-variables-btn',
                className: 'btn-css-variables',
                label: `<i class="fa fa-palette"></i> ${t('css_variables')}`,
                command: 'css-variables',
            },
            {
                id: 'language-switcher-btn',
                className: 'btn-language-switcher',
                label: `<i class="fa fa-globe"></i> ${window.currentLanguage.toUpperCase()}`,
                command: 'switch-language',
            }
        ]
    });
}

// Добавление горячих клавиш
function addKeyboardShortcuts() {
    const editor = window.editor;
    
    editor.on('keydown', (event) => {
        // Ctrl+S - Сохранение
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            saveTemplate();
        }
        
        // Ctrl+P - Предпросмотр
        if (event.ctrlKey && event.key === 'p') {
            event.preventDefault();
            previewTemplate();
        }
        
        // Ctrl+L - Загрузка шаблона
        if (event.ctrlKey && event.key === 'l') {
            event.preventDefault();
            showTemplateSelector();
        }
        
        // Ctrl+D - Публикация
        if (event.ctrlKey && event.key === 'd') {
            event.preventDefault();
            deployTemplate();
        }
    });
}

// Инициализация API интеграции
function initAPIIntegration() {
    // Проверяем доступность API с авторизацией
    makeAuthenticatedRequest('/api/content-editor/templates')
        .then(response => {
            if (response.ok) {
                console.log('✅ API integration ready');
            } else {
                console.warn('⚠️ API not available, using local storage');
            }
        })
        .catch(error => {
            console.warn('⚠️ API not available, using local storage');
        });
}

// Функция сохранения шаблона
async function saveTemplate() {
    const editor = window.editor;
    if (!editor) return;
    
    try {
        showNotification(t('loading'), 'info');
        
        const data = {
            html: editor.getHtml(),
            css: editor.getCss(),
            components: editor.getComponents(),
            page_id: window.pageId
        };
        
        const response = await makeAuthenticatedRequest('/api/content-editor/save', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(t('save_success'), 'success');
            console.log('Template saved:', result);
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        console.error('Save error:', error);
        showNotification(t('save_error'), 'error');
    }
}

// Функция предпросмотра шаблона
async function previewTemplate() {
    const editor = window.editor;
    if (!editor) return;
    
    try {
        showNotification(t('loading'), 'info');
        
        const data = {
            html: editor.getHtml(),
            css: editor.getCss(),
            page_id: window.pageId
        };
        
        const response = await makeAuthenticatedRequest('/api/content-editor/preview', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Открываем предпросмотр в новом окне
            const previewWindow = window.open('', '_blank');
            previewWindow.document.write(result.html);
            previewWindow.document.close();
            
            showNotification(t('preview_ready'), 'success');
        } else {
            throw new Error('Preview failed');
        }
    } catch (error) {
        console.error('Preview error:', error);
        showNotification(t('preview_error'), 'error');
    }
}

// Функция публикации шаблона
async function deployTemplate() {
    const editor = window.editor;
    if (!editor) return;
    
    if (!confirm('Are you sure you want to deploy to production?')) {
        return;
    }
    
    try {
        showNotification(t('loading'), 'info');
        
        const data = {
            html: editor.getHtml(),
            css: editor.getCss(),
            page_id: window.pageId
        };
        
        const response = await makeAuthenticatedRequest('/api/content-editor/deploy', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(t('deploy_success'), 'success');
            console.log('Template deployed:', result);
        } else {
            throw new Error('Deploy failed');
        }
    } catch (error) {
        console.error('Deploy error:', error);
        showNotification(t('deploy_error'), 'error');
    }
}

// Показ селектора шаблонов
async function showTemplateSelector() {
    const editor = window.editor;
    if (!editor) return;
    
    try {
        const response = await makeAuthenticatedRequest('/api/content-editor/templates');
        const templates = response.ok ? await response.json() : [];
        
        const modal = editor.Modal;
        const content = `
            <div style="padding: 20px;">
                <h3>${t('template_selector')}</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
                    ${templates.map(template => `
                        <div onclick="loadTemplateById('${template.id}')" style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; cursor: pointer; text-align: center;">
                            <div style="font-size: 2em; margin-bottom: 10px;">📄</div>
                            <h4>${template.name}</h4>
                            <p>${template.description || ''}</p>
                        </div>
                    `).join('')}
                </div>
                <div style="margin-top: 20px;">
                    <button onclick="closeModal()" style="background: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${t('close')}</button>
                </div>
            </div>
        `;
        
        modal.setTitle(t('template_selector'))
            .setContent(content)
            .open();
    } catch (error) {
        console.error('Template selector error:', error);
        showNotification('Error loading templates', 'error');
    }
}

// Загрузка шаблона по ID
async function loadTemplateById(templateId) {
    const editor = window.editor;
    if (!editor) return;
    
    try {
        showNotification(t('loading'), 'info');
        
        const response = await makeAuthenticatedRequest(`/api/content-editor/template/${templateId}`);
        
        if (response.ok) {
            const template = await response.json();
            
            // Парсим шаблон через API
            const parseResponse = await makeAuthenticatedRequest('/api/content-editor/parse', {
                method: 'POST',
                body: JSON.stringify({
                    template_content: template.content,
                    template_type: template.type
                })
            });
            
            if (parseResponse.ok) {
                const parsed = await parseResponse.json();
                
                // Загружаем в редактор
                editor.setComponents(parsed.html);
                editor.setStyle(parsed.css);
                
                showNotification(t('load_success'), 'success');
                window.editor.Modal.close();
            } else {
                throw new Error('Parse failed');
            }
        } else {
            throw new Error('Load failed');
        }
    } catch (error) {
        console.error('Load template error:', error);
        showNotification(t('load_error'), 'error');
    }
}

// Показ редактора CSS переменных
async function showCSSVariablesEditor() {
    const editor = window.editor;
    if (!editor) return;
    
    try {
        // Загружаем текущие CSS переменные
        const response = await makeAuthenticatedRequest('/api/content-editor/css-variables');
        let variables = {};
        
        if (response.ok) {
            const result = await response.json();
            variables = result.variables || {};
        }
        
        // Дефолтные значения
        const defaults = {
            '--primary-color': '#667eea',
            '--secondary-color': '#764ba2',
            '--accent-color': '#f093fb',
            '--text-color': '#333333',
            '--background-color': '#ffffff',
            '--border-radius': '5px'
        };
        
        // Объединяем с загруженными значениями
        const currentVars = { ...defaults, ...variables };
        
        const modal = editor.Modal;
        const content = `
            <div style="padding: 20px;">
                <h3>${t('css_variables')}</h3>
                <div style="display: grid; gap: 15px; margin-top: 20px;">
                    <div>
                        <label>${t('primary_color')}:</label>
                        <input type="color" id="primary-color" value="${currentVars['--primary-color']}" style="width: 100%; padding: 5px;">
                    </div>
                    <div>
                        <label>${t('secondary_color')}:</label>
                        <input type="color" id="secondary-color" value="${currentVars['--secondary-color']}" style="width: 100%; padding: 5px;">
                    </div>
                    <div>
                        <label>${t('accent_color')}:</label>
                        <input type="color" id="accent-color" value="${currentVars['--accent-color']}" style="width: 100%; padding: 5px;">
                    </div>
                    <div>
                        <label>${t('text_color')}:</label>
                        <input type="color" id="text-color" value="${currentVars['--text-color']}" style="width: 100%; padding: 5px;">
                    </div>
                    <div>
                        <label>${t('background_color')}:</label>
                        <input type="color" id="background-color" value="${currentVars['--background-color']}" style="width: 100%; padding: 5px;">
                    </div>
                    <div>
                        <label>${t('border_radius')}:</label>
                        <input type="range" id="border-radius" min="0" max="20" value="${parseInt(currentVars['--border-radius'])}" style="width: 100%;">
                        <span id="border-radius-value">${currentVars['--border-radius']}</span>
                    </div>
                </div>
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button onclick="applyCSSVariables()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${t('apply')}</button>
                    <button onclick="closeModal()" style="background: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${t('close')}</button>
                </div>
            </div>
        `;
        
        modal.setTitle(t('css_variables'))
            .setContent(content)
            .open();
        
        // Обновление значения border-radius
        document.getElementById('border-radius').addEventListener('input', function() {
            document.getElementById('border-radius-value').textContent = this.value + 'px';
        });
        
    } catch (error) {
        console.error('Error loading CSS variables:', error);
        showNotification('Error loading CSS variables', 'error');
    }
}

// Применение CSS переменных
async function applyCSSVariables() {
    const editor = window.editor;
    if (!editor) return;
    
    const variables = {
        '--primary-color': document.getElementById('primary-color').value,
        '--secondary-color': document.getElementById('secondary-color').value,
        '--accent-color': document.getElementById('accent-color').value,
        '--text-color': document.getElementById('text-color').value,
        '--background-color': document.getElementById('background-color').value,
        '--border-radius': document.getElementById('border-radius').value + 'px'
    };
    
    try {
        // Сохраняем переменные через API
        const response = await makeAuthenticatedRequest('/api/content-editor/css-variables', {
            method: 'PUT',
            body: JSON.stringify({ variables })
        });
        
        if (response.ok) {
            // Применяем переменные к редактору
            const css = Object.entries(variables)
                .map(([key, value]) => `${key}: ${value};`)
                .join('\n');
            
            editor.addStyle(`:root {\n${css}\n}`);
            showNotification('CSS variables applied and saved', 'success');
            window.editor.Modal.close();
        } else {
            throw new Error('Failed to save CSS variables');
        }
    } catch (error) {
        console.error('CSS variables error:', error);
        showNotification('Error saving CSS variables', 'error');
    }
}

// Глобальные функции для модальных окон
window.loadTemplateById = loadTemplateById;
window.applyCSSVariables = applyCSSVariables;
window.closeModal = function() {
    if (window.editor) {
        window.editor.Modal.close();
    }
};

// Функция показа уведомлений
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
        z-index: 10000;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    `;
    
    // Цвета для разных типов
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.background = colors[type] || colors.info;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Автоматическое скрытие
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Fallback функции для совместимости
window.saveProject = saveTemplate;
window.previewProject = previewTemplate;
window.loadTemplates = showTemplateSelector;

console.log('🎯 Enhanced GrapesJS Editor Ready!');
console.log('Features:');
console.log('- Bilingual interface (EN/RU)');
console.log('- Template editing with Jinja2 support');
console.log('- CSS Variables editor');
console.log('- API integration');
console.log('- Keyboard shortcuts');
console.log('- Dental Academy specific blocks');
