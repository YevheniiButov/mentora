/**
 * File Explorer с визуальным редактором GrapesJS
 * Для Content Editor
 */

console.log('🔧 file-explorer.js loading...');

class FileExplorer {
    constructor(options = {}) {
        console.log('🔧 FileExplorer constructor called');
        this.options = {
            apiBase: '/api/content-editor',
            modalId: 'fileExplorerModal',
            ...options
        };
        
        this.currentPath = '';
        this.visualEditor = null;
        this.currentFile = null; // Текущий редактируемый файл
        this.apiBase = this.options.apiBase;
        
        // Инициализация Enhanced File Loader
        this.fileLoader = null;
        
        console.log('🔧 FileExplorer constructor - window.currentLang:', window.currentLang);
        console.log('🔧 FileExplorer constructor - apiBase:', this.apiBase);
        
        this.init();
        this.initializeFileLoader();
    }
    
    init() {
        console.log('🔧 File Explorer initializing...');
        
        this.createModal();
        this.setupEventListeners();
        
        console.log('✅ File Explorer initialized');
    }
    
    // Инициализация Enhanced File Loader
    initializeFileLoader() {
        console.log('🔧 Initializing Enhanced File Loader...');
        
        const initLoader = () => {
            if (window.editor && window.editor.Canvas && window.EnhancedFileLoader) {
                try {
                    this.fileLoader = new window.EnhancedFileLoader(window.editor);
                    console.log('✅ Enhanced File Loader initialized in FileExplorer');
                    return true;
                } catch (error) {
                    console.error('❌ Error creating EnhancedFileLoader:', error);
                    return false;
                }
            }
            return false;
        };
        
        // Пытаемся инициализировать сразу
        if (!initLoader()) {
            // Если не получилось, ждем готовности
            const checkInterval = setInterval(() => {
                if (initLoader()) {
                    clearInterval(checkInterval);
                }
            }, 100);
            
            // Таймаут через 10 секунд
            setTimeout(() => {
                clearInterval(checkInterval);
                console.warn('⚠️ EnhancedFileLoader initialization timeout in FileExplorer');
            }, 10000);
        }
    }
    
    createModal() {
        console.log('🔧 Creating modal...');
        // Удаляем существующий модал если есть
        const existingModal = document.getElementById(this.options.modalId);
        if (existingModal) {
            existingModal.remove();
        }
        
        const modalHTML = `
            <div class="modal fade file-explorer-modal" id="${this.options.modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-folder-open me-2"></i>
                                Файловый проводник
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Breadcrumbs навигация -->
                            <div class="path-breadcrumbs">
                                <nav aria-label="breadcrumb">
                                    <ol class="breadcrumb mb-0">
                                        <li class="breadcrumb-item">
                                            <a href="#" data-path="">Корневая папка</a>
                                        </li>
                                    </ol>
                                </nav>
                            </div>
                            
                            <!-- Основной контейнер файлов -->
                            <div class="file-list">
                                <div class="loading-spinner">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    <p>Загрузка файлов...</p>
                                </div>
                            </div>
                            
                            <!-- Контейнер для предпросмотра -->
                            <div class="file-preview" style="display: none;">
                                <div class="preview-header">
                                    <h6>Предпросмотр файла</h6>
                                </div>
                                <pre><code></code></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById(this.options.modalId);
        console.log('🔧 Modal created:', this.modal);
    }
    
    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Обработчик клика по breadcrumbs
        this.modal.addEventListener('click', (e) => {
            if (e.target.matches('.breadcrumb-item a')) {
                e.preventDefault();
                const path = e.target.dataset.path || '';
                this.navigateTo(path);
            }
        });
        
        // Обработчик клика по файлам
        this.modal.addEventListener('click', (e) => {
            const fileItem = e.target.closest('.file-item');
            if (!fileItem) return;
            
            const path = fileItem.dataset.path;
            if (!path) return;
            
            if (e.target.closest('.file-actions')) {
                return; // Не обрабатываем клики по кнопкам действий
            }
            
            // Если это папка - переходим в неё
            if (fileItem.classList.contains('directory')) {
                this.navigateTo(path);
            } else {
                            // Если это HTML файл - загружаем в существующий редактор
            const extension = path.toLowerCase().split('.').pop();
            if (extension === 'html' || extension === 'htm') {
                this.loadFileInEditor(path);
            } else {
                // Для других файлов показываем предпросмотр
                this.previewFile(path);
            }
            }
        });
    }
    
    open() {
        console.log('🔧 Opening File Explorer...');
        
        if (typeof bootstrap === 'undefined') {
            console.error('❌ Bootstrap not loaded');
            alert('Bootstrap не загружен. Проверьте подключение скриптов.');
            return;
        }
        
        const modal = new bootstrap.Modal(this.modal);
        modal.show();
        
        // Загружаем корневую папку
        this.navigateTo('');
    }
    
    close() {
        const modal = bootstrap.Modal.getInstance(this.modal);
        if (modal) {
            modal.hide();
        }
    }
    
    async navigateTo(path) {
        console.log('🔧 Navigating to:', path);
        this.currentPath = path;
        
        try {
            await this.loadCurrentPath();
            this.updateBreadcrumbs();
        } catch (error) {
            console.error('❌ Navigation error:', error);
            this.showNotification('Ошибка навигации: ' + error.message, 'error');
        }
    }
    
    async loadCurrentPath() {
        const fileList = this.modal.querySelector('.file-list');
        
        // Показываем спиннер загрузки
        fileList.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Загрузка файлов...</p>
            </div>
        `;
        
        try {
            console.log('🔧 FileExplorer - Making request to:', `${this.apiBase}/file-explorer?path=${this.currentPath}`);
            
            const response = await fetch(`${this.apiBase}/file-explorer?path=${this.currentPath}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.displayFiles(data.files);
            } else {
                throw new Error(data.error || 'Failed to load files');
            }
            
        } catch (error) {
            console.error('Error loading files:', error);
            fileList.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <p class="text-danger">Ошибка загрузки файлов</p>
                    <p class="text-muted">${error.message}</p>
                </div>
            `;
        }
    }
    
    displayFiles(files) {
        const fileList = this.modal.querySelector('.file-list');
        if (!fileList) return;

        if (!files || files.length === 0) {
            fileList.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Папка пуста</p>
                </div>
            `;
            return;
        }

        // Сортируем: сначала папки, потом файлы
        const sortedFiles = files.sort((a, b) => {
            if (a.type === 'directory' && b.type === 'file') return -1;
            if (a.type === 'file' && b.type === 'directory') return 1;
            return a.name.localeCompare(b.name);
        });

        let filesHtml = '<div class="file-grid">';
        
        sortedFiles.forEach(file => {
            const isHTML = file.extension === '.html' || file.extension === '.htm';
            const isEditable = file.editable;
            
            filesHtml += `
                <div class="file-item ${file.type}" data-path="${file.path}">
                    <div class="file-icon">
                        ${this.getFileIcon(file)}
                    </div>
                    <div class="file-info">
                        <div class="file-name" title="${file.name}">${file.name}</div>
                        ${file.size ? `<div class="file-size">${this.formatFileSize(file.size)}</div>` : ''}
                    </div>
                    <div class="file-actions">
                        ${isHTML ? `
                            <button class="btn btn-sm btn-primary me-1" 
                                    onclick="window.fileExplorer.openVisualEditor('${file.path}')"
                                    title="Визуальное редактирование">
                                <i class="fas fa-palette"></i>
                            </button>
                            <button class="btn btn-sm btn-info me-1" 
                                    onclick="window.fileExplorer.previewFullPage('${file.path}')"
                                    title="Предпросмотр страницы">
                                <i class="fas fa-external-link-alt"></i>
                            </button>
                        ` : ''}
                        ${isEditable ? `
                            <button class="btn btn-sm btn-outline-secondary me-1" 
                                    onclick="window.fileExplorer.editTextFile('${file.path}')"
                                    title="Текстовое редактирование">
                                <i class="fas fa-code"></i>
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="window.fileExplorer.deleteFile('${file.path}')"
                                title="Удалить">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        filesHtml += '</div>';
        fileList.innerHTML = filesHtml;
    }
    
    getFileIcon(file) {
        if (file.type === 'directory') {
            return '<i class="fas fa-folder"></i>';
        }
        
        const extension = file.extension?.toLowerCase();
        switch (extension) {
            case '.html':
            case '.htm':
                return '<i class="fas fa-file-code"></i>';
            case '.css':
                return '<i class="fas fa-file-code"></i>';
            case '.js':
                return '<i class="fas fa-file-code"></i>';
            case '.json':
                return '<i class="fas fa-file-code"></i>';
            case '.png':
            case '.jpg':
            case '.jpeg':
            case '.gif':
            case '.svg':
                return '<i class="fas fa-file-image"></i>';
            default:
                return '<i class="fas fa-file"></i>';
        }
    }
    
    formatFileSize(bytes) {
        if (!bytes) return '';
        
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    updateBreadcrumbs() {
        const breadcrumb = this.modal.querySelector('.breadcrumb');
        const pathParts = this.currentPath.split('/').filter(part => part);
        
        let breadcrumbHTML = `
            <li class="breadcrumb-item">
                <a href="#" data-path="">Корневая папка</a>
            </li>
        `;
        
        let currentPath = '';
        pathParts.forEach((part, index) => {
            currentPath += (currentPath ? '/' : '') + part;
            const isLast = index === pathParts.length - 1;
            
            breadcrumbHTML += `
                <li class="breadcrumb-item ${isLast ? 'active' : ''}">
                    ${isLast ? part : `<a href="#" data-path="${currentPath}">${part}</a>`}
                </li>
            `;
        });
        
        breadcrumb.innerHTML = breadcrumbHTML;
    }
    
    async previewFile(path) {
        console.log('🔧 Previewing file:', path);
        
        try {
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(path)}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // ИСПРАВЛЕНО: Открываем предварительный просмотр БЕЗ document.write
                const previewWindow = window.open('', '_blank');
                this.writeToPreviewWindow(previewWindow, data.content);
            } else {
                throw new Error(data.error || 'Failed to load template');
            }
            
        } catch (error) {
            console.error('Error previewing file:', error);
            this.showNotification('Ошибка предпросмотра: ' + error.message, 'error');
        }
    }
    
    async loadFile(path) {
        console.log('🔧 Loading file:', path);
        
        try {
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(path)}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && this.editor) {
                // Загружаем шаблон в редактор
                this.editor.setComponents('');
                this.editor.setStyle('');
                
                if (data.content) {
                    this.editor.setComponents(data.content);
                }
                
                // Закрываем проводник
                this.close();
                
                // Показываем уведомление
                this.showNotification('Шаблон успешно загружен', 'success');
                
                // Обновляем UI
                const selectedTemplate = document.getElementById('selected-template');
                if (selectedTemplate) {
                    selectedTemplate.textContent = path.split('/').pop();
                }
            } else {
                throw new Error(data.error || 'Failed to load template');
            }
            
        } catch (error) {
            console.error('Error loading file:', error);
            this.showNotification('Ошибка загрузки: ' + error.message, 'error');
        }
    }
    
    // Загрузить файл в существующий редактор enhanced-editor
    async loadFileInEditor(path) {
        console.log('🔧 Loading file with enhanced loader:', path);
        
        try {
            // Проверяем доступность Enhanced File Loader
            if (!this.fileLoader) {
                console.warn('⚠️ Enhanced File Loader not ready, falling back to basic loading');
                return this.loadFileInEditorBasic(path);
            }
            
            // Загружаем файл через Enhanced File Loader
            const result = await this.fileLoader.loadFile(path);
            
            if (result.success) {
                // Успешная загрузка
                this.showNotification('Файл успешно загружен в редактор', 'success');
                
                // Обновляем UI селектора шаблонов
                this.updateTemplateSelector(path);
                
                // Закрываем FileExplorer
                this.close();
                
                // Включаем кнопки управления редактором
                this.enableEditorControls();
                
                console.log('✅ File loaded successfully via Enhanced File Loader');
                
            } else {
                throw new Error(result.error || 'Failed to load file');
            }
            
        } catch (error) {
            console.error('❌ Error loading file via Enhanced File Loader:', error);
            this.showNotification(`Ошибка загрузки: ${error.message}`, 'error');
            
            // Fallback к базовой загрузке
            console.log('🔄 Falling back to basic file loading...');
            try {
                await this.loadFileInEditorBasic(path);
            } catch (fallbackError) {
                console.error('❌ Fallback loading also failed:', fallbackError);
                this.showNotification('Критическая ошибка загрузки файла', 'error');
            }
        }
    }
    
    // Fallback метод для базовой загрузки файлов
    async loadFileInEditorBasic(path) {
        console.log('🔧 Basic file loading for:', path);
        
        try {
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(path)}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && window.editor) {
                // Базовая загрузка без обработки стилей
                const { bodyHtml, cssContent } = this.parseBasicHTML(data.content);
                
                // Очищаем редактор
                window.editor.setComponents('');
                window.editor.setStyle('');
                
                // Загружаем контент
                if (bodyHtml) {
                    window.editor.setComponents(bodyHtml);
                }
                if (cssContent) {
                    window.editor.setStyle(cssContent);
                }
                
                this.showNotification('Файл загружен (базовый режим)', 'warning');
                this.close();
                
            } else {
                throw new Error(data.error || 'Failed to load template');
            }
            
        } catch (error) {
            console.error('❌ Basic loading failed:', error);
            throw error;
        }
    }
    
    // НОВОЕ: Очистка Jinja2 синтаксиса из HTML (аналогично ExternalCSSLoader)
    cleanJinjaFromHTML(htmlContent) {
        return htmlContent
            // Заменяем url_for на реальные пути ПЕРЕД парсингом DOM
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename\s*=\s*['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename=['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            // Убираем другие Jinja2 конструкции
            .replace(/\{\%\s*.*?\s*\%\}/g, '')
            .replace(/\{\{\s*[^}]*\s*\}\}/g, '')
            // Очищаем условные блоки
            .replace(/\{\%\s*if\s+.*?\%\}[\s\S]*?\{\%\s*endif\s*\%\}/g, '')
            .replace(/\{\%\s*for\s+.*?\%\}[\s\S]*?\{\%\s*endfor\s*\%\}/g, '')
            // Удаляем пустые атрибуты, которые могли остаться после удаления Jinja2
            .replace(/href\s*=\s*["']\s*["']/g, 'href="#"')
            .replace(/src\s*=\s*["']\s*["']/g, 'src="#"')
            .replace(/action\s*=\s*["']\s*["']/g, 'action="#"');
    }
    
    // Метод для базового парсинга HTML
    parseBasicHTML(htmlContent) {
        const cleanedHtml = this.cleanJinjaFromHTML(htmlContent);
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleanedHtml, 'text/html');
        
        let cssContent = '';
        let bodyHtml = '';
        
        // Извлекаем CSS из style тегов
        const styleTags = doc.querySelectorAll('style');
        styleTags.forEach(style => {
            cssContent += style.textContent + '\n';
        });
        
        // Извлекаем содержимое body
        if (doc.body) {
            bodyHtml = doc.body.innerHTML;
        }
        
        return { bodyHtml, cssContent };
    }
    
    // Метод для обновления селектора шаблонов
    updateTemplateSelector(path) {
        const selectedTemplate = document.getElementById('selected-template');
        if (selectedTemplate) {
            const fileName = path.split('/').pop();
            selectedTemplate.textContent = fileName;
            selectedTemplate.title = path; // Полный путь в tooltip
        }
        
        // Обновляем заголовок редактора если есть
        const editorTitle = document.querySelector('.editor-title');
        if (editorTitle) {
            editorTitle.textContent = `Редактор: ${path}`;
        }
    }
    
    // Метод для включения кнопок управления
    enableEditorControls() {
        const controlButtons = [
            'save-btn',
            'preview-btn', 
            'undo-btn',
            'redo-btn',
            'clear-btn'
        ];
        
        controlButtons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = false;
                btn.classList.remove('disabled');
            }
        });
        
        // Обновляем статус
        this.updateEditorStatus('ready', 'Файл загружен - готов к редактированию');
    }
    
    // Метод для обновления статуса редактора
    updateEditorStatus(type, message) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            // Убираем все классы статуса
            statusDot.classList.remove('loading', 'ready', 'error', 'saving');
            
            // Добавляем новый статус
            statusDot.classList.add(type);
            statusText.textContent = message;
        }
    }
    
    // Открыть визуальный редактор (GrapesJS)
    async openVisualEditor(filePath) {
        try {
            console.log('🎨 Opening visual editor for:', filePath);
            
            // Загружаем содержимое файла
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(filePath)}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            // Закрываем File Explorer
            this.close();
            
            // Открываем новое окно/модал с GrapesJS
            this.openGrapesJSEditor(filePath, data.content, { name: filePath.split('/').pop() });
            
        } catch (error) {
            console.error('❌ Error opening visual editor:', error);
            alert(`Ошибка открытия редактора: ${error.message}`);
        }
    }
    
    // Создать и инициализировать GrapesJS редактор
    openGrapesJSEditor(filePath, htmlContent, fileInfo) {
        // Создаем полноэкранный модал для редактора
        const editorModal = document.createElement('div');
        editorModal.className = 'modal fade';
        editorModal.id = 'visualEditorModal';
        editorModal.setAttribute('data-bs-backdrop', 'static');
        editorModal.innerHTML = `
            <div class="modal-dialog modal-fullscreen">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-palette me-2"></i>
                            Визуальный редактор - ${fileInfo.name}
                        </h5>
                        <div class="header-actions">
                            <button class="btn btn-light btn-sm me-2" id="save-visual-changes">
                                <i class="fas fa-save"></i> Сохранить
                            </button>
                            <button class="btn btn-light btn-sm me-2" id="preview-page">
                                <i class="fas fa-eye"></i> Предпросмотр
                            </button>
                            <button class="btn btn-outline-light btn-sm" data-bs-dismiss="modal">
                                <i class="fas fa-times"></i> Закрыть
                            </button>
                        </div>
                    </div>
                    <div class="modal-body p-0">
                        <div id="visual-editor-container" style="height: calc(100vh - 120px);"></div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(editorModal);
        
        // Показываем модал
        const modal = new bootstrap.Modal(editorModal);
        modal.show();
        
        // Инициализируем GrapesJS после показа модала
        setTimeout(async () => {
            await this.initGrapesJS(filePath, htmlContent, fileInfo);
        }, 500);
        
        // Удаляем модал при закрытии
        editorModal.addEventListener('hidden.bs.modal', () => {
            if (this.visualEditor) {
                this.visualEditor.destroy();
                this.visualEditor = null;
            }
            editorModal.remove();
        });
    }
    
    // Инициализация GrapesJS
    async initGrapesJS(filePath, htmlContent, fileInfo) {
        const container = document.getElementById('visual-editor-container');
        if (!container) {
            console.error('❌ Visual editor container not found');
            return;
        }
        
        // ИСПРАВЛЕНО: Используем полный парсинг HTML для извлечения внешних ресурсов
        const { bodyHtml, cssContent, externalStyles, externalScripts } = this.parseFullHTMLContent(htmlContent);
        
        this.visualEditor = grapesjs.init({
            container: '#visual-editor-container',
            width: '100%',
            height: '100%',
            
            // Отключаем локальное хранение
            storageManager: false,
            
            // Настройки панелей
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
                                label: '<i class="fas fa-border-style"></i>',
                                command: 'sw-visibility',
                            },
                            {
                                id: 'export',
                                className: 'btn-open-export',
                                label: '<i class="fas fa-code"></i>',
                                command: 'export-template',
                                context: 'export-template',
                            },
                            {
                                id: 'show-json',
                                className: 'btn-show-json',
                                label: '<i class="fas fa-file-code"></i>',
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
                                label: '<i class="fas fa-desktop"></i>',
                                command: 'set-device-desktop',
                                active: true,
                            },
                            {
                                id: 'device-tablet',
                                label: '<i class="fas fa-tablet-alt"></i>',
                                command: 'set-device-tablet',
                            },
                            {
                                id: 'device-mobile',
                                label: '<i class="fas fa-mobile-alt"></i>',
                                command: 'set-device-mobile',
                            },
                        ],
                    },
                ]
            },
            
            // Менеджер устройств
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
                        widthMedia: '768px',
                    },
                ]
            },
            
            // Менеджер блоков
            blockManager: {
                appendTo: '.blocks-container',
                blocks: [
                    {
                        id: 'section',
                        label: 'Section',
                        content: `<section class="section">
                            <div class="container">
                                <div class="row">
                                    <div class="col">
                                        <h2>New Section</h2>
                                        <p>Start editing this section...</p>
                                    </div>
                                </div>
                            </div>
                        </section>`,
                        category: 'Layout',
                        media: '<i class="fas fa-square"></i>'
                    },
                    {
                        id: 'text',
                        label: 'Text',
                        content: '<div data-gjs-type="text">Insert your text here</div>',
                        category: 'Basic',
                        media: '<i class="fas fa-font"></i>'
                    },
                    {
                        id: 'image',
                        label: 'Image',
                        content: { type: 'image' },
                        category: 'Basic',
                        media: '<i class="fas fa-image"></i>'
                    },
                    {
                        id: 'button',
                        label: 'Button',
                        content: '<a class="btn btn-primary">Click me</a>',
                        category: 'Basic',
                        media: '<i class="fas fa-hand-pointer"></i>'
                    },
                    {
                        id: 'dental-hero',
                        label: 'Dental Hero',
                        content: `
                            <section class="hero-section bg-primary text-white py-5">
                                <div class="container">
                                    <div class="row align-items-center">
                                        <div class="col-md-6">
                                            <h1 class="display-4 fw-bold">Ваша улыбка - наша забота</h1>
                                            <p class="lead">Современная стоматология с индивидуальным подходом</p>
                                            <a href="#" class="btn btn-light btn-lg">Записаться на прием</a>
                                        </div>
                                        <div class="col-md-6">
                                            <img src="/static/images/dental-hero.jpg" class="img-fluid rounded" alt="Стоматология">
                                        </div>
                                    </div>
                                </div>
                            </section>
                        `,
                        category: 'Dental',
                        media: '<i class="fas fa-tooth"></i>'
                    },
                    {
                        id: 'services-grid',
                        label: 'Services Grid',
                        content: `
                            <section class="services-section py-5">
                                <div class="container">
                                    <h2 class="text-center mb-5">Наши услуги</h2>
                                    <div class="row">
                                        <div class="col-md-4 mb-4">
                                            <div class="service-card text-center p-4 border rounded">
                                                <i class="fas fa-tooth fa-3x text-primary mb-3"></i>
                                                <h4>Лечение кариеса</h4>
                                                <p>Современные методы лечения кариеса</p>
                                            </div>
                                        </div>
                                        <div class="col-md-4 mb-4">
                                            <div class="service-card text-center p-4 border rounded">
                                                <i class="fas fa-smile fa-3x text-primary mb-3"></i>
                                                <h4>Отбеливание</h4>
                                                <p>Профессиональное отбеливание зубов</p>
                                            </div>
                                        </div>
                                        <div class="col-md-4 mb-4">
                                            <div class="service-card text-center p-4 border rounded">
                                                <i class="fas fa-user-md fa-3x text-primary mb-3"></i>
                                                <h4>Консультация</h4>
                                                <p>Бесплатная консультация специалиста</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </section>
                        `,
                        category: 'Dental',
                        media: '<i class="fas fa-th"></i>'
                    }
                ]
            },
            
            // Менеджер стилей
            styleManager: {
                appendTo: '.styles-container',
            },
            
            // Менеджер слоев
            layerManager: {
                appendTo: '.layers-container'
            },
            
            // Настройки Canvas
            canvas: {
                styles: [
                    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
                    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
                ],
                scripts: [
                    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'
                ]
            }
        });
        
        // Загружаем контент
        this.visualEditor.setComponents(bodyHtml);
        this.visualEditor.setStyle(cssContent);
        
        // ИСПРАВЛЕНО: Загружаем внешние ресурсы через ExternalCSSLoader
        if (externalStyles.length > 0 || externalScripts.length > 0) {
            console.log('🔧 Loading external resources:', { styles: externalStyles.length, scripts: externalScripts.length });
            await this.loadExternalResources(this.visualEditor, externalStyles, externalScripts);
        }
        
        // Настраиваем команды устройств
        this.setupDeviceCommands();
        
        // Настраиваем события сохранения
        this.setupSaveEvents(filePath, fileInfo);
        
        console.log('✅ GrapesJS Visual Editor initialized');
    }
    
    // Парсинг HTML контента
    parseHTMLContent(htmlContent) {
        // Создаем временный DOM элемент для парсинга
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        
        // Извлекаем CSS из style тегов и link тегов
        let cssContent = '';
        
        // Внутренние стили
        const styleTags = doc.querySelectorAll('style');
        styleTags.forEach(style => {
            cssContent += style.textContent + '\n';
        });
        
        // Извлекаем содержимое body
        const bodyContent = doc.body ? doc.body.innerHTML : htmlContent;
        
        return {
            bodyHtml: bodyContent,
            cssContent: cssContent
        };
    }
    
    // Полный парсинг HTML контента с поддержкой всех ресурсов
    parseFullHTMLContent(htmlContent) {
        // ИСПРАВЛЕНО: Используем улучшенную очистку Jinja2 синтаксиса
        const cleanedHtml = this.cleanJinjaFromHTML(htmlContent);
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleanedHtml, 'text/html');
        
        // Извлекаем CSS из style тегов
        let cssContent = '';
        const styleTags = doc.querySelectorAll('style');
        styleTags.forEach(style => {
            cssContent += style.textContent + '\n';
        });
        
        // Извлекаем JavaScript из script тегов
        let jsContent = '';
        const scriptTags = doc.querySelectorAll('script');
        scriptTags.forEach(script => {
            if (script.textContent.trim()) {
                jsContent += script.textContent + '\n';
            }
        });
        
        // Извлекаем внешние стили (link теги)
        const externalStyles = [];
        const linkTags = doc.querySelectorAll('link[rel="stylesheet"]');
        linkTags.forEach(link => {
            const href = link.href;
            // Проверяем, что это валидный URL, а не Jinja2 шаблон
            if (href && 
                !href.includes('{{') && 
                !href.includes('}}') && 
                !href.includes('url_for') &&
                !href.includes('%7B%7B') && // URL-encoded {{ 
                !href.includes('%7D%7D') && // URL-encoded }}
                href !== '#' &&
                href !== window.location.href) {
                // Дополнительная проверка на валидность URL
                try {
                    new URL(href);
                    externalStyles.push(href);
                } catch (e) {
                    console.warn('⚠️ Skipping invalid CSS URL:', href);
                }
            } else {
                console.warn('⚠️ Skipping Jinja2 template or invalid URL in CSS:', href);
            }
        });
        
        // Извлекаем внешние скрипты
        const externalScripts = [];
        const externalScriptTags = doc.querySelectorAll('script[src]');
        externalScriptTags.forEach(script => {
            const src = script.src;
            // Проверяем, что это валидный URL, а не Jinja2 шаблон
            if (src && 
                !src.includes('{{') && 
                !src.includes('}}') &&
                !src.includes('%7B%7B') && // URL-encoded {{ 
                !src.includes('%7D%7D') && // URL-encoded }}
                src !== '#' &&
                src !== window.location.href) {
                externalScripts.push(src);
            } else {
                console.warn('⚠️ Skipping Jinja2 template or invalid URL in script:', src);
            }
        });
        
        // Извлекаем содержимое body
        const bodyContent = doc.body ? doc.body.innerHTML : htmlContent;
        
        return {
            bodyHtml: bodyContent,
            cssContent: cssContent,
            jsContent: jsContent,
            externalStyles: externalStyles,
            externalScripts: externalScripts
        };
    }
    
    // Загрузка внешних ресурсов в canvas редактора
    async loadExternalResources(editor, externalStyles, externalScripts) {
        // ИСПРАВЛЕНО: Используем ExternalCSSLoader для правильной обработки URL
        if (externalStyles.length > 0) {
            console.log('🎨 Loading external styles through ExternalCSSLoader...');
            
            try {
                // Создаем экземпляр ExternalCSSLoader если не существует
                if (!window.ExternalCSSLoader) {
                    console.warn('⚠️ ExternalCSSLoader not available, falling back to basic loading');
                    this.loadExternalResourcesBasic(editor, externalStyles, externalScripts);
                    return;
                }
                
                const cssLoader = new window.ExternalCSSLoader(editor);
                
                // Создаем HTML с CSS ссылками для обработки
                const cssHTML = externalStyles.map(url => `<link rel="stylesheet" href="${url}">`).join('\n');
                
                // Загружаем CSS через ExternalCSSLoader
                await cssLoader.loadExternalCSSFromHTML(cssHTML);
                
                console.log('✅ External CSS loaded through ExternalCSSLoader');
                
            } catch (error) {
                console.warn('⚠️ ExternalCSSLoader failed, falling back to basic loading:', error);
                this.loadExternalResourcesBasic(editor, externalStyles, externalScripts);
            }
        }
        
        // Добавляем внешние скрипты в canvas
        this.loadExternalScripts(editor, externalScripts);
    }
    
    // Базовая загрузка внешних ресурсов (fallback)
    loadExternalResourcesBasic(editor, externalStyles, externalScripts) {
        // Добавляем внешние стили в canvas
        if (externalStyles.length > 0) {
            try {
                const canvas = editor.Canvas.getFrameEl();
                if (canvas && canvas.contentDocument) {
                    const canvasDoc = canvas.contentDocument;
                    const head = canvasDoc.head;
                    
                    externalStyles.forEach(styleUrl => {
                        // Проверяем, что это валидный URL, а не Jinja2 шаблон
                        if (styleUrl && 
                            !styleUrl.includes('{{') && 
                            !styleUrl.includes('}}') &&
                            !styleUrl.includes('%7B%7B') && // URL-encoded {{ 
                            !styleUrl.includes('%7D%7D') && // URL-encoded }}
                            styleUrl !== '#' &&
                            styleUrl !== window.location.href) {
                            
                            const link = canvasDoc.createElement('link');
                            link.rel = 'stylesheet';
                            link.href = styleUrl;
                            link.onload = () => console.log('✅ External CSS loaded in canvas:', styleUrl);
                            link.onerror = () => console.warn('❌ Failed to load external CSS in canvas:', styleUrl);
                            head.appendChild(link);
                        } else {
                            console.warn('⚠️ Skipping invalid style URL in editor:', styleUrl);
                        }
                    });
                }
            } catch (error) {
                console.warn('⚠️ Could not load external styles:', error);
            }
        }
        
        // Добавляем внешние скрипты в canvas
        this.loadExternalScripts(editor, externalScripts);
    }
    
    // Загрузка внешних скриптов в canvas редактора
    loadExternalScripts(editor, externalScripts) {
        if (externalScripts.length > 0) {
            try {
                const canvas = editor.Canvas.getFrameEl();
                if (canvas && canvas.contentDocument) {
                    const canvasDoc = canvas.contentDocument;
                    const body = canvasDoc.body;
                    
                    externalScripts.forEach(scriptUrl => {
                        // Проверяем, что это валидный URL, а не Jinja2 шаблон
                        if (scriptUrl && 
                            !scriptUrl.includes('{{') && 
                            !scriptUrl.includes('}}') &&
                            !scriptUrl.includes('%7B%7B') && // URL-encoded {{ 
                            !scriptUrl.includes('%7D%7D') && // URL-encoded }}
                            scriptUrl !== '#' &&
                            scriptUrl !== window.location.href) {
                            
                            // ИСПРАВЛЕНО: Безопасная загрузка скриптов БЕЗ document.write
                            const script = canvasDoc.createElement('script');
                            script.src = scriptUrl;
                            script.onload = () => console.log('✅ External script loaded in canvas:', scriptUrl);
                            script.onerror = () => console.warn('❌ Failed to load external script in canvas:', scriptUrl);
                            body.appendChild(script);
                        } else {
                            console.warn('⚠️ Skipping invalid script URL in editor:', scriptUrl);
                        }
                    });
                }
            } catch (error) {
                console.warn('⚠️ Could not load external scripts:', error);
            }
        }
    }
    
    // Загрузка JavaScript в редактор
    loadJavaScript(editor, jsContent) {
        if (!jsContent.trim()) return;
        
        try {
            // Создаем временный script тег для выполнения JavaScript
            const scriptElement = document.createElement('script');
            scriptElement.textContent = jsContent;
            
            // Добавляем в canvas редактора
            const canvas = editor.Canvas.getFrameEl();
            if (canvas && canvas.contentDocument) {
                const canvasDoc = canvas.contentDocument;
                const canvasScript = canvasDoc.createElement('script');
                canvasScript.textContent = jsContent;
                canvasDoc.body.appendChild(canvasScript);
            }
            
            console.log('✅ JavaScript loaded in editor');
        } catch (error) {
            console.warn('⚠️ Warning: Could not load JavaScript in editor:', error);
        }
    }
    
    // Настройка команд устройств
    setupDeviceCommands() {
        this.visualEditor.Commands.add('set-device-desktop', {
            run: editor => editor.setDevice('Desktop')
        });
        this.visualEditor.Commands.add('set-device-tablet', {
            run: editor => editor.setDevice('Tablet')
        });
        this.visualEditor.Commands.add('set-device-mobile', {
            run: editor => editor.setDevice('Mobile')
        });
    }
    
    // Настройка событий сохранения
    setupSaveEvents(filePath, fileInfo) {
        const saveBtn = document.getElementById('save-visual-changes');
        const previewBtn = document.getElementById('preview-page');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveVisualChanges(filePath, fileInfo);
            });
        }
        
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewVisualChanges();
            });
        }
    }
    
    // Сохранение изменений из визуального редактора
    async saveVisualChanges(filePath, fileInfo) {
        if (!this.visualEditor) return;
        
        try {
            const saveBtn = document.getElementById('save-visual-changes');
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
            saveBtn.disabled = true;
            
            // Получаем HTML и CSS из редактора
            const htmlComponents = this.visualEditor.getHtml();
            const cssStyles = this.visualEditor.getCss();
            
            // Формируем полный HTML документ
            const fullHTML = this.buildFullHTML(htmlComponents, cssStyles, fileInfo);
            
            // Сохраняем через API
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(filePath)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ content: fullHTML })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            // Показываем успешное сообщение
            this.showNotification('Изменения сохранены успешно!', 'success');
            
            console.log('✅ Visual changes saved successfully');
            
        } catch (error) {
            console.error('❌ Error saving visual changes:', error);
            this.showNotification(`Ошибка сохранения: ${error.message}`, 'error');
        } finally {
            const saveBtn = document.getElementById('save-visual-changes');
            if (saveBtn) {
                saveBtn.innerHTML = '<i class="fas fa-save"></i> Сохранить';
                saveBtn.disabled = false;
            }
        }
    }
    
    // Формирование полного HTML документа с поддержкой всех ресурсов
    buildFullHTML(htmlComponents, cssStyles, fileInfo) {
        // Получаем текущие внешние ресурсы из редактора
        const editor = window.editor;
        const externalStyles = editor?.getConfig()?.canvas?.styles || [];
        const externalScripts = editor?.getConfig()?.canvas?.scripts || [];
        
        // Фильтруем валидные URL (исключаем Jinja2 шаблоны)
        const validStyles = externalStyles.filter(style => 
            style && !style.includes('{{') && !style.includes('}}')
        );
        const validScripts = externalScripts.filter(script => 
            script && !script.includes('{{') && !script.includes('}}')
        );
        
        // Формируем внешние стили
        const externalStylesHTML = validStyles
            .map(style => `<link href="${style}" rel="stylesheet">`)
            .join('\n    ');
        
        // ИСПРАВЛЕНО: Формируем внешние скрипты с безопасной загрузкой
        const externalScriptsHTML = validScripts
            .map(script => `<script src="${script}" async></script>`)
            .join('\n    ');
        
        return `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${fileInfo.name.replace('.html', '')}</title>
    
    <!-- External Styles -->
    ${externalStylesHTML}
    
    <!-- Custom Styles -->
    <style>
${cssStyles}
    </style>
</head>
<body>
${htmlComponents}

    <!-- External Scripts -->
    ${externalScriptsHTML}
</body>
</html>`;
    }
    
    // Предпросмотр изменений
    previewVisualChanges() {
        if (!this.visualEditor) return;
        
        const htmlComponents = this.visualEditor.getHtml();
        const cssStyles = this.visualEditor.getCss();
        
        const previewHTML = this.buildFullHTML(htmlComponents, cssStyles, { name: 'Preview' });
        
        // ИСПРАВЛЕНО: Используем безопасный способ БЕЗ document.write
        const previewWindow = window.open('', '_blank');
        this.writeToPreviewWindow(previewWindow, previewHTML);
    }
    
    // Полный предпросмотр страницы (с оригинальными стилями)
    async previewFullPage(filePath) {
        try {
            // Загружаем содержимое файла
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(filePath)}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            // ИСПРАВЛЕНО: Используем безопасный способ БЕЗ document.write
            const previewWindow = window.open('', '_blank');
            this.writeToPreviewWindow(previewWindow, data.content);
            
        } catch (error) {
            console.error('❌ Error previewing page:', error);
            alert(`Ошибка предпросмотра: ${error.message}`);
        }
    }
    
    // Редактирование в текстовом режиме
    async editTextFile(filePath) {
        // Можно интегрировать с существующим текстовым редактором
        // или открыть в модальном окне с CodeMirror/Monaco Editor
        console.log('📝 Opening text editor for:', filePath);
        alert('Текстовый редактор будет добавлен в следующем обновлении');
    }
    
    // Удаление файла
    async deleteFile(filePath) {
        if (!confirm(`Вы уверены, что хотите удалить файл: ${filePath}?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(filePath)}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            // Обновляем список файлов
            this.loadCurrentPath();
            
            this.showNotification('Файл удален успешно', 'success');
            
        } catch (error) {
            console.error('❌ Error deleting file:', error);
            this.showNotification(`Ошибка удаления: ${error.message}`, 'error');
        }
    }
    
    // Показ уведомлений
    showNotification(message, type = 'info') {
        // Создаем уведомление в стиле Bootstrap
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    // НОВОЕ: Безопасная запись HTML в preview окно БЕЗ document.write
    writeToPreviewWindow(previewWindow, htmlContent) {
        try {
            // Метод 1: Использование data URL (самый безопасный)
            const dataURL = 'data:text/html;charset=utf-8,' + encodeURIComponent(htmlContent);
            previewWindow.location.href = dataURL;
            console.log('✅ Preview window updated using data URL (no document.write)');
            return;
        } catch (error) {
            console.warn('⚠️ Data URL method failed, trying innerHTML:', error);
        }
        
        try {
            // Метод 2: Попытка использовать innerHTML
            if (previewWindow && previewWindow.document) {
                previewWindow.document.open();
                previewWindow.document.close();
                
                // Создаем новый HTML документ
                const newDoc = previewWindow.document.implementation.createHTMLDocument('Preview');
                newDoc.documentElement.innerHTML = htmlContent;
                
                // Заменяем содержимое окна
                previewWindow.document.replaceChild(
                    previewWindow.document.importNode(newDoc.documentElement, true),
                    previewWindow.document.documentElement
                );
                
                console.log('✅ Preview window updated safely with innerHTML');
                return;
            }
        } catch (error) {
            console.warn('⚠️ innerHTML method failed:', error);
        }
        
        // Последний fallback - document.write (только если все остальное не работает)
        try {
            console.warn('⚠️ Using document.write as last resort');
            previewWindow.document.open();
            previewWindow.document.write(htmlContent);
            previewWindow.document.close();
        } catch (error) {
            console.error('❌ All preview methods failed:', error);
        }
    }
    
    // Сохранить изменения из enhanced-editor
    async saveEnhancedEditorChanges(filePath) {
        const editor = window.editor;
        if (!editor) {
            this.showNotification('Редактор не найден', 'error');
            return;
        }
        
        try {
            // Получаем HTML и CSS из редактора
            const htmlComponents = editor.getHtml();
            const cssStyles = editor.getCss();
            
            // Формируем полный HTML документ
            const fullHTML = this.buildFullHTML(htmlComponents, cssStyles, { name: filePath.split('/').pop() });
            
            // Сохраняем через API
            const response = await fetch(`${this.apiBase}/template-content/${encodeURIComponent(filePath)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ content: fullHTML })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message);
            }
            
            this.showNotification('Изменения сохранены успешно!', 'success');
            console.log('✅ Enhanced editor changes saved successfully');
            
        } catch (error) {
            console.error('❌ Error saving enhanced editor changes:', error);
            this.showNotification(`Ошибка сохранения: ${error.message}`, 'error');
        }
    }
}

console.log('🔧 FileExplorer class defined');

// Создаем глобальный экземпляр FileExplorer
window.fileExplorer = new FileExplorer();

// Делаем метод сохранения доступным глобально
window.saveCurrentFile = () => {
    if (window.fileExplorer && window.fileExplorer.currentFile) {
        window.fileExplorer.saveEnhancedEditorChanges(window.fileExplorer.currentFile);
    } else {
        console.warn('⚠️ No file is currently loaded for saving');
    }
};

console.log('✅ FileExplorer class loaded and global instance created');
