/**
 * File Browser для Visual Builder
 * Навигация по HTML файлам проекта
 */

class FileBrowser {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.currentPath = '/templates/';
        this.supportedFiles = ['.html', '.htm', '.css', '.js'];
        this.currentFile = null;
        this.fileTree = [];
        this.isOpen = false;
        
        // DOM элементы
        this.dom = {};
        
        // Состояние
        this.state = {
            expandedFolders: new Set(),
            selectedFile: null,
            searchQuery: '',
            viewMode: 'tree' // tree, list, grid
        };
        
        this.init();
    }

    /**
     * Инициализация File Browser
     */
    init() {
        this.createFileBrowserUI();
        this.setupEventListeners();
        this.loadProjectFiles();
        
        console.info('📁 File Browser инициализирован');
    }

    /**
     * Создание UI File Browser
     */
    createFileBrowserUI() {
        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.className = 'file-browser-modal';
        modal.id = 'fileBrowserModal';
        modal.innerHTML = `
            <div class="file-browser-content">
                <div class="file-browser-header">
                    <div class="file-browser-title">
                        <i class="bi bi-folder2-open"></i>
                        <span>File Browser</span>
                    </div>
                    <div class="file-browser-actions">
                        <button class="btn btn-sm btn-secondary" onclick="fileBrowser.toggleViewMode()" title="Переключить вид">
                            <i class="bi bi-grid"></i>
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="fileBrowser.refresh()" title="Обновить">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                        <button class="btn btn-sm btn-ghost" onclick="fileBrowser.close()" title="Закрыть">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                </div>
                
                <div class="file-browser-toolbar">
                    <div class="file-browser-search">
                        <input type="text" placeholder="Поиск файлов..." id="fileSearch">
                        <i class="bi bi-search"></i>
                    </div>
                    <div class="file-browser-filters">
                        <select id="fileTypeFilter">
                            <option value="">Все файлы</option>
                            <option value=".html">HTML</option>
                            <option value=".css">CSS</option>
                            <option value=".js">JavaScript</option>
                        </select>
                    </div>
                </div>
                
                <div class="file-browser-body">
                    <div class="file-browser-sidebar">
                        <div class="file-browser-breadcrumb" id="fileBreadcrumb">
                            <span class="breadcrumb-item active">/</span>
                        </div>
                        <div class="file-browser-tree" id="fileTree">
                            <div class="loading-spinner">
                                <i class="bi bi-arrow-clockwise"></i>
                                Загрузка файлов...
                            </div>
                        </div>
                    </div>
                    
                    <div class="file-browser-main">
                        <div class="file-browser-preview" id="filePreview">
                            <div class="preview-placeholder">
                                <i class="bi bi-file-earmark-text"></i>
                                <p>Выберите файл для предпросмотра</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="file-browser-footer">
                    <div class="file-info" id="fileInfo">
                        <span>Файлов: 0</span>
                    </div>
                    <div class="file-actions">
                        <button class="btn btn-primary" onclick="fileBrowser.openSelectedFile()" disabled id="openFileBtn">
                            <i class="bi bi-folder2-open"></i>
                            Открыть
                        </button>
                        <button class="btn btn-secondary" onclick="fileBrowser.editSelectedFile()" disabled id="editFileBtn">
                            <i class="bi bi-pencil"></i>
                            Редактировать
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Кэшируем DOM элементы
        this.dom = {
            modal: modal,
            tree: modal.querySelector('#fileTree'),
            preview: modal.querySelector('#filePreview'),
            search: modal.querySelector('#fileSearch'),
            typeFilter: modal.querySelector('#fileTypeFilter'),
            breadcrumb: modal.querySelector('#fileBreadcrumb'),
            fileInfo: modal.querySelector('#fileInfo'),
            openFileBtn: modal.querySelector('#openFileBtn'),
            editFileBtn: modal.querySelector('#editFileBtn')
        };
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Поиск файлов
        this.dom.search.addEventListener('input', this.debounce((e) => {
            this.state.searchQuery = e.target.value;
            this.filterFiles();
        }, 300));

        // Фильтр по типу файлов
        this.dom.typeFilter.addEventListener('change', (e) => {
            this.filterFiles();
        });

        // Клик по модальному окну
        this.dom.modal.addEventListener('click', (e) => {
            if (e.target === this.dom.modal) {
                this.close();
            }
        });

        // Горячие клавиши
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            
            if (e.key === 'Escape') {
                this.close();
            } else if (e.key === 'Enter' && this.state.selectedFile) {
                this.openSelectedFile();
            }
        });
    }

    /**
     * Загрузка файлов проекта
     */
    async loadProjectFiles() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/visual-builder/files/list', {
                headers: {
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.fileTree = data.files;
                this.renderFileTree();
                this.updateFileInfo();
            } else {
                throw new Error(data.error || 'Ошибка загрузки файлов');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки файлов:', error);
            this.showError('Ошибка загрузки файлов: ' + error.message);
        }
    }

    /**
     * Отображение дерева файлов
     */
    renderFileTree() {
        if (!this.fileTree || this.fileTree.length === 0) {
            this.dom.tree.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-folder-x"></i>
                    <p>Файлы не найдены</p>
                </div>
            `;
            return;
        }

        const filteredFiles = this.filterFileTree(this.fileTree);
        this.dom.tree.innerHTML = this.generateFileTreeHTML(filteredFiles);
        
        // Настраиваем обработчики для файлов и папок
        this.setupFileTreeEventListeners();
    }

    /**
     * Фильтрация дерева файлов
     */
    filterFileTree(files) {
        if (!this.state.searchQuery && !this.state.typeFilter) {
            return files;
        }

        return files.filter(file => {
            // Фильтр по поиску
            if (this.state.searchQuery) {
                const query = this.state.searchQuery.toLowerCase();
                if (!file.name.toLowerCase().includes(query) && 
                    !file.path.toLowerCase().includes(query)) {
                    return false;
                }
            }

            // Фильтр по типу файла
            if (this.state.typeFilter) {
                const extension = this.getFileExtension(file.name);
                if (extension !== this.state.typeFilter) {
                    return false;
                }
            }

            return true;
        });
    }

    /**
     * Генерация HTML для дерева файлов
     */
    generateFileTreeHTML(files) {
        if (this.state.viewMode === 'grid') {
            return this.generateGridViewHTML(files);
        } else if (this.state.viewMode === 'list') {
            return this.generateListViewHTML(files);
        } else {
            return this.generateTreeViewHTML(files);
        }
    }

    /**
     * Генерация древовидного представления
     */
    generateTreeViewHTML(files) {
        const groupedFiles = this.groupFilesByDirectory(files);
        
        let html = '<div class="file-tree">';
        
        for (const [directory, fileList] of Object.entries(groupedFiles)) {
            const isExpanded = this.state.expandedFolders.has(directory);
            
            html += `
                <div class="folder-item" data-path="${directory}">
                    <div class="folder-header ${isExpanded ? 'expanded' : ''}" onclick="fileBrowser.toggleFolder('${directory}')">
                        <i class="bi bi-chevron-right folder-icon"></i>
                        <i class="bi bi-folder2"></i>
                        <span class="folder-name">${this.getFolderName(directory)}</span>
                        <span class="file-count">(${fileList.length})</span>
                    </div>
                    <div class="folder-content" style="display: ${isExpanded ? 'block' : 'none'}">
                        ${fileList.map(file => this.generateFileItemHTML(file)).join('')}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Генерация списка файлов
     */
    generateListViewHTML(files) {
        let html = '<div class="file-list">';
        
        files.forEach(file => {
            html += this.generateFileItemHTML(file);
        });
        
        html += '</div>';
        return html;
    }

    /**
     * Генерация сетки файлов
     */
    generateGridViewHTML(files) {
        let html = '<div class="file-grid">';
        
        files.forEach(file => {
            html += `
                <div class="file-grid-item" data-file="${file.path}">
                    <div class="file-icon">
                        <i class="bi ${this.getFileIcon(file.name)}"></i>
                    </div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-path">${file.path}</div>
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    /**
     * Генерация HTML для элемента файла
     */
    generateFileItemHTML(file) {
        const isSelected = this.state.selectedFile === file.path;
        const fileIcon = this.getFileIcon(file.name);
        const fileSize = this.formatFileSize(file.size);
        
        return `
            <div class="file-item ${isSelected ? 'selected' : ''}" 
                 data-file="${file.path}" 
                 onclick="fileBrowser.selectFile('${file.path}')"
                 ondblclick="fileBrowser.openFile('${file.path}')">
                <div class="file-icon">
                    <i class="bi ${fileIcon}"></i>
                </div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">
                        <span class="file-size">${fileSize}</span>
                        <span class="file-date">${this.formatDate(file.modified)}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-sm btn-ghost" onclick="fileBrowser.previewFile('${file.path}')" title="Предпросмотр">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-ghost" onclick="fileBrowser.editFile('${file.path}')" title="Редактировать">
                        <i class="bi bi-pencil"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Группировка файлов по директориям
     */
    groupFilesByDirectory(files) {
        const grouped = {};
        
        files.forEach(file => {
            const directory = this.getDirectory(file.path);
            if (!grouped[directory]) {
                grouped[directory] = [];
            }
            grouped[directory].push(file);
        });
        
        return grouped;
    }

    /**
     * Настройка обработчиков для дерева файлов
     */
    setupFileTreeEventListeners() {
        // Обработчики для файлов
        this.dom.tree.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const filePath = item.dataset.file;
                this.selectFile(filePath);
            });
            
            item.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                const filePath = item.dataset.file;
                this.openFile(filePath);
            });
        });

        // Обработчики для папок
        this.dom.tree.querySelectorAll('.folder-header').forEach(header => {
            header.addEventListener('click', (e) => {
                e.stopPropagation();
                const folderPath = header.closest('.folder-item').dataset.path;
                this.toggleFolder(folderPath);
            });
        });
    }

    /**
     * Выбор файла
     */
    selectFile(filePath) {
        // Убираем предыдущее выделение
        this.dom.tree.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Выделяем новый файл
        const fileItem = this.dom.tree.querySelector(`[data-file="${filePath}"]`);
        if (fileItem) {
            fileItem.classList.add('selected');
        }
        
        this.state.selectedFile = filePath;
        this.updateFileActions();
        this.previewFile(filePath);
    }

    /**
     * Открытие файла
     */
    async openFile(filePath) {
        try {
            this.showLoading();
            
            const response = await fetch(`/api/visual-builder/files/open`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                },
                body: JSON.stringify({ filepath: filePath })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentFile = filePath;
                this.close();
                
                // Уведомляем Visual Builder об открытии файла
                this.visualBuilder.emit('fileOpened', {
                    filepath: filePath,
                    content: data.content,
                    type: data.type
                });
                
                this.visualBuilder.showNotification(`Файл открыт: ${this.getFileName(filePath)}`, 'success');
            } else {
                throw new Error(data.error || 'Ошибка открытия файла');
            }
            
        } catch (error) {
            console.error('Ошибка открытия файла:', error);
            this.showError('Ошибка открытия файла: ' + error.message);
        }
    }

    /**
     * Предпросмотр файла
     */
    async previewFile(filePath) {
        try {
            const response = await fetch(`/api/visual-builder/files/preview`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                },
                body: JSON.stringify({ filepath: filePath })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showFilePreview(data.content, data.type, filePath);
            } else {
                throw new Error(data.error || 'Ошибка предпросмотра');
            }
            
        } catch (error) {
            console.error('Ошибка предпросмотра файла:', error);
            this.showError('Ошибка предпросмотра: ' + error.message);
        }
    }

    /**
     * Отображение предпросмотра файла
     */
    showFilePreview(content, type, filePath) {
        const fileName = this.getFileName(filePath);
        
        if (type === 'html') {
            this.dom.preview.innerHTML = `
                <div class="preview-header">
                    <h4>${fileName}</h4>
                    <div class="preview-actions">
                        <button class="btn btn-sm btn-secondary" onclick="fileBrowser.openFile('${filePath}')">
                            <i class="bi bi-folder2-open"></i>
                            Открыть
                        </button>
                    </div>
                </div>
                <div class="preview-content">
                    <iframe src="data:text/html;charset=utf-8,${encodeURIComponent(content)}" 
                            frameborder="0" width="100%" height="400"></iframe>
                </div>
            `;
        } else if (type === 'css' || type === 'js') {
            this.dom.preview.innerHTML = `
                <div class="preview-header">
                    <h4>${fileName}</h4>
                    <div class="preview-actions">
                        <button class="btn btn-sm btn-secondary" onclick="fileBrowser.openFile('${filePath}')">
                            <i class="bi bi-folder2-open"></i>
                            Открыть
                        </button>
                    </div>
                </div>
                <div class="preview-content">
                    <pre><code class="language-${type}">${this.escapeHtml(content)}</code></pre>
                </div>
            `;
        } else {
            this.dom.preview.innerHTML = `
                <div class="preview-placeholder">
                    <i class="bi bi-file-earmark-text"></i>
                    <p>Предпросмотр недоступен для этого типа файла</p>
                </div>
            `;
        }
    }

    /**
     * Переключение папки
     */
    toggleFolder(folderPath) {
        const folderItem = this.dom.tree.querySelector(`[data-path="${folderPath}"]`);
        const folderHeader = folderItem.querySelector('.folder-header');
        const folderContent = folderItem.querySelector('.folder-content');
        
        if (this.state.expandedFolders.has(folderPath)) {
            // Сворачиваем папку
            this.state.expandedFolders.delete(folderPath);
            folderHeader.classList.remove('expanded');
            folderContent.style.display = 'none';
        } else {
            // Разворачиваем папку
            this.state.expandedFolders.add(folderPath);
            folderHeader.classList.add('expanded');
            folderContent.style.display = 'block';
        }
    }

    /**
     * Переключение режима отображения
     */
    toggleViewMode() {
        const modes = ['tree', 'list', 'grid'];
        const currentIndex = modes.indexOf(this.state.viewMode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.state.viewMode = modes[nextIndex];
        
        this.renderFileTree();
    }

    /**
     * Фильтрация файлов
     */
    filterFiles() {
        this.renderFileTree();
    }

    /**
     * Обновление информации о файлах
     */
    updateFileInfo() {
        const totalFiles = this.fileTree.length;
        const filteredFiles = this.filterFileTree(this.fileTree).length;
        
        this.dom.fileInfo.innerHTML = `
            <span>Файлов: ${filteredFiles}${totalFiles !== filteredFiles ? ` из ${totalFiles}` : ''}</span>
        `;
    }

    /**
     * Обновление кнопок действий
     */
    updateFileActions() {
        const hasSelection = !!this.state.selectedFile;
        
        this.dom.openFileBtn.disabled = !hasSelection;
        this.dom.editFileBtn.disabled = !hasSelection;
    }

    /**
     * Открытие выбранного файла
     */
    openSelectedFile() {
        if (this.state.selectedFile) {
            this.openFile(this.state.selectedFile);
        }
    }

    /**
     * Редактирование выбранного файла
     */
    editSelectedFile() {
        if (this.state.selectedFile) {
            this.editFile(this.state.selectedFile);
        }
    }

    /**
     * Редактирование файла
     */
    editFile(filePath) {
        // Пока что просто открываем файл
        this.openFile(filePath);
    }

    /**
     * Обновление файлов
     */
    refresh() {
        this.loadProjectFiles();
    }

    /**
     * Открытие File Browser
     */
    open() {
        this.isOpen = true;
        this.dom.modal.style.display = 'flex';
        this.loadProjectFiles();
        
        // Фокус на поиск
        setTimeout(() => {
            this.dom.search.focus();
        }, 100);
    }

    /**
     * Закрытие File Browser
     */
    close() {
        this.isOpen = false;
        this.dom.modal.style.display = 'none';
        this.state.selectedFile = null;
    }

    /**
     * Показать загрузку
     */
    showLoading() {
        this.dom.tree.innerHTML = `
            <div class="loading-spinner">
                <i class="bi bi-arrow-clockwise"></i>
                Загрузка...
            </div>
        `;
    }

    /**
     * Показать ошибку
     */
    showError(message) {
        this.dom.tree.innerHTML = `
            <div class="error-state">
                <i class="bi bi-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Утилиты
     */
    getFileExtension(filename) {
        return filename.substring(filename.lastIndexOf('.')).toLowerCase();
    }

    getFileIcon(filename) {
        const ext = this.getFileExtension(filename);
        const iconMap = {
            '.html': 'bi-file-earmark-text',
            '.htm': 'bi-file-earmark-text',
            '.css': 'bi-file-earmark-css',
            '.js': 'bi-file-earmark-code',
            '.json': 'bi-file-earmark-code',
            '.xml': 'bi-file-earmark-code',
            '.txt': 'bi-file-earmark-text',
            '.md': 'bi-file-earmark-text'
        };
        return iconMap[ext] || 'bi-file-earmark';
    }

    getFileName(filepath) {
        return filepath.split('/').pop();
    }

    getDirectory(filepath) {
        const parts = filepath.split('/');
        parts.pop();
        return parts.join('/') || '/';
    }

    getFolderName(directory) {
        return directory.split('/').pop() || 'Root';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Глобальные функции для обратной совместимости
let fileBrowser;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        fileBrowser = new FileBrowser(window.visualBuilder);
        window.fileBrowser = fileBrowser;
    }
}); 