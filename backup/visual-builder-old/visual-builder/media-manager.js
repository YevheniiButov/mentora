/**
 * Media Manager - Media File Management
 * Управление медиафайлами для Visual Builder
 */

export class MediaManager {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.mediaLibrary = new Map();
        this.uploadQueue = [];
        this.isUploading = false;
        this.supportedTypes = {
            image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'],
            video: ['video/mp4', 'video/webm', 'video/ogg'],
            audio: ['audio/mp3', 'audio/wav', 'audio/ogg'],
            document: ['application/pdf', 'text/plain', 'application/msword']
        };
        this.maxFileSize = 50 * 1024 * 1024; // 50MB
        
        this.init();
    }
    
    init() {
        this.loadMediaLibrary();
        this.setupEventListeners();
        console.info('📁 Media Manager готов');
    }
    
    setupEventListeners() {
        // Drag & drop для медиафайлов
        document.addEventListener('dragover', this.handleDragOver.bind(this));
        document.addEventListener('drop', this.handleDrop.bind(this));
        
        // Обработка paste событий
        document.addEventListener('paste', this.handlePaste.bind(this));
    }
    
    handleDragOver(event) {
        if (this.hasMediaFiles(event.dataTransfer)) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'copy';
        }
    }
    
    handleDrop(event) {
        if (this.hasMediaFiles(event.dataTransfer)) {
            event.preventDefault();
            const files = Array.from(event.dataTransfer.files);
            this.processFiles(files);
        }
    }
    
    handlePaste(event) {
        const items = Array.from(event.clipboardData.items);
        const files = items
            .filter(item => item.kind === 'file')
            .map(item => item.getAsFile())
            .filter(file => file);
        
        if (files.length > 0) {
            this.processFiles(files);
        }
    }
    
    hasMediaFiles(dataTransfer) {
        return Array.from(dataTransfer.types).some(type => 
            type.startsWith('image/') || 
            type.startsWith('video/') || 
            type.startsWith('audio/')
        );
    }
    
    processFiles(files) {
        files.forEach(file => {
            if (this.validateFile(file)) {
                this.addToUploadQueue(file);
            }
        });
        
        if (this.uploadQueue.length > 0 && !this.isUploading) {
            this.processUploadQueue();
        }
    }
    
    validateFile(file) {
        // Проверка размера
        if (file.size > this.maxFileSize) {
            this.vb.showNotification(`Файл ${file.name} слишком большой (максимум 50MB)`, 'error');
            return false;
        }
        
        // Проверка типа
        const isValidType = Object.values(this.supportedTypes)
            .flat()
            .includes(file.type);
            
        if (!isValidType) {
            this.vb.showNotification(`Неподдерживаемый тип файла: ${file.type}`, 'error');
            return false;
        }
        
        return true;
    }
    
    addToUploadQueue(file) {
        this.uploadQueue.push({
            file,
            id: this.generateId(),
            status: 'pending',
            progress: 0
        });
        
        this.vb.showNotification(`Файл ${file.name} добавлен в очередь загрузки`, 'info');
    }
    
    async processUploadQueue() {
        if (this.isUploading || this.uploadQueue.length === 0) return;
        
        this.isUploading = true;
        
        while (this.uploadQueue.length > 0) {
            const item = this.uploadQueue[0];
            await this.uploadFile(item);
            this.uploadQueue.shift();
        }
        
        this.isUploading = false;
    }
    
    async uploadFile(item) {
        try {
            item.status = 'uploading';
            this.updateUploadProgress(item);
            
            const formData = new FormData();
            formData.append('file', item.file);
            formData.append('type', this.getFileType(item.file));
            
            const response = await fetch('/api/visual-builder/media/upload', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.vb.config.csrfToken
                },
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                item.status = 'completed';
                this.addToMediaLibrary(result.media);
                this.vb.showNotification(`Файл ${item.file.name} успешно загружен`, 'success');
            } else {
                throw new Error(result.message || 'Ошибка загрузки');
            }
            
        } catch (error) {
            item.status = 'error';
            this.vb.showNotification(`Ошибка загрузки ${item.file.name}: ${error.message}`, 'error');
            console.error('Upload error:', error);
        }
    }
    
    updateUploadProgress(item) {
        // Здесь можно добавить UI для отображения прогресса
        console.log(`Uploading ${item.file.name}: ${item.progress}%`);
    }
    
    getFileType(file) {
        if (this.supportedTypes.image.includes(file.type)) return 'image';
        if (this.supportedTypes.video.includes(file.type)) return 'video';
        if (this.supportedTypes.audio.includes(file.type)) return 'audio';
        if (this.supportedTypes.document.includes(file.type)) return 'document';
        return 'other';
    }
    
    addToMediaLibrary(mediaData) {
        this.mediaLibrary.set(mediaData.id, {
            ...mediaData,
            addedAt: new Date(),
            usageCount: 0
        });
        
        this.saveMediaLibrary();
        this.vb.emit('mediaAdded', mediaData);
    }
    
    removeFromMediaLibrary(mediaId) {
        if (this.mediaLibrary.has(mediaId)) {
            const media = this.mediaLibrary.get(mediaId);
            this.mediaLibrary.delete(mediaId);
            this.saveMediaLibrary();
            this.vb.emit('mediaRemoved', media);
            
            // Удаляем файл с сервера
            this.deleteMediaFile(mediaId);
        }
    }
    
    async deleteMediaFile(mediaId) {
        try {
            const response = await fetch(`/api/visual-builder/media/${mediaId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.vb.config.csrfToken
                }
            });
            
            if (!response.ok) {
                console.warn('Failed to delete media file from server');
            }
        } catch (error) {
            console.error('Error deleting media file:', error);
        }
    }
    
    getMediaById(id) {
        return this.mediaLibrary.get(id);
    }
    
    getMediaByType(type) {
        return Array.from(this.mediaLibrary.values())
            .filter(media => media.type === type);
    }
    
    searchMedia(query) {
        const searchTerm = query.toLowerCase();
        return Array.from(this.mediaLibrary.values())
            .filter(media => 
                media.name.toLowerCase().includes(searchTerm) ||
                media.tags?.some(tag => tag.toLowerCase().includes(searchTerm))
            );
    }
    
    loadMediaLibrary() {
        try {
            const saved = localStorage.getItem('vb-media-library');
            if (saved) {
                const data = JSON.parse(saved);
                data.forEach(item => {
                    this.mediaLibrary.set(item.id, item);
                });
            }
        } catch (error) {
            console.warn('Ошибка загрузки медиа библиотеки:', error);
        }
    }
    
    saveMediaLibrary() {
        try {
            const data = Array.from(this.mediaLibrary.values());
            localStorage.setItem('vb-media-library', JSON.stringify(data));
        } catch (error) {
            console.warn('Ошибка сохранения медиа библиотеки:', error);
        }
    }
    
    generateId() {
        return 'media_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    // UI методы
    openMediaLibrary() {
        this.createMediaLibraryModal();
    }
    
    createMediaLibraryModal() {
        const modal = document.createElement('div');
        modal.className = 'media-library-modal';
        modal.innerHTML = `
            <div class="media-library-content">
                <div class="media-library-header">
                    <h3>Медиа библиотека</h3>
                    <button class="close-btn" onclick="this.closest('.media-library-modal').remove()">×</button>
                </div>
                
                <div class="media-library-toolbar">
                    <input type="text" placeholder="Поиск медиафайлов..." class="media-search">
                    <select class="media-type-filter">
                        <option value="">Все типы</option>
                        <option value="image">Изображения</option>
                        <option value="video">Видео</option>
                        <option value="audio">Аудио</option>
                        <option value="document">Документы</option>
                    </select>
                    <button class="btn btn-primary" onclick="this.closest('.media-library-modal').querySelector('.file-input').click()">
                        <i class="bi bi-upload"></i> Загрузить
                    </button>
                    <input type="file" class="file-input" multiple style="display: none;" 
                           accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt">
                </div>
                
                <div class="media-library-grid">
                    ${this.renderMediaGrid()}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Обработчики событий
        const fileInput = modal.querySelector('.file-input');
        fileInput.addEventListener('change', (e) => {
            this.processFiles(Array.from(e.target.files));
        });
        
        const searchInput = modal.querySelector('.media-search');
        searchInput.addEventListener('input', (e) => {
            this.filterMediaGrid(e.target.value, modal);
        });
        
        const typeFilter = modal.querySelector('.media-type-filter');
        typeFilter.addEventListener('change', (e) => {
            this.filterMediaGrid(searchInput.value, modal, e.target.value);
        });
    }
    
    renderMediaGrid() {
        const media = Array.from(this.mediaLibrary.values());
        
        if (media.length === 0) {
            return `
                <div class="media-empty">
                    <i class="bi bi-images"></i>
                    <p>Медиа библиотека пуста</p>
                    <button class="btn btn-primary" onclick="this.closest('.media-library-modal').querySelector('.file-input').click()">
                        Загрузить файлы
                    </button>
                </div>
            `;
        }
        
        return media.map(item => `
            <div class="media-item" data-id="${item.id}" data-type="${item.type}">
                <div class="media-preview">
                    ${this.renderMediaPreview(item)}
                </div>
                <div class="media-info">
                    <div class="media-name">${item.name}</div>
                    <div class="media-meta">
                        <span class="media-size">${this.formatFileSize(item.size)}</span>
                        <span class="media-type">${item.type}</span>
                    </div>
                </div>
                <div class="media-actions">
                    <button class="btn btn-sm btn-primary" onclick="mediaManager.insertMedia('${item.id}')">
                        <i class="bi bi-plus"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="mediaManager.removeFromMediaLibrary('${item.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    renderMediaPreview(media) {
        switch (media.type) {
            case 'image':
                return `<img src="${media.url}" alt="${media.name}">`;
            case 'video':
                return `<video src="${media.url}" muted></video>`;
            case 'audio':
                return `<i class="bi bi-music-note"></i>`;
            case 'document':
                return `<i class="bi bi-file-earmark-text"></i>`;
            default:
                return `<i class="bi bi-file"></i>`;
        }
    }
    
    filterMediaGrid(searchTerm, modal, typeFilter = '') {
        const grid = modal.querySelector('.media-library-grid');
        const items = modal.querySelectorAll('.media-item');
        
        items.forEach(item => {
            const matchesSearch = item.querySelector('.media-name').textContent
                .toLowerCase().includes(searchTerm.toLowerCase());
            const matchesType = !typeFilter || item.dataset.type === typeFilter;
            
            item.style.display = matchesSearch && matchesType ? 'block' : 'none';
        });
    }
    
    insertMedia(mediaId) {
        const media = this.getMediaById(mediaId);
        if (!media) return;
        
        if (this.vb.state.selectedElement) {
            this.insertMediaIntoElement(media, this.vb.state.selectedElement);
        } else {
            this.createMediaElement(media);
        }
        
        // Закрываем модальное окно
        const modal = document.querySelector('.media-library-modal');
        if (modal) modal.remove();
    }
    
    insertMediaIntoElement(media, element) {
        const elementType = element.dataset.type;
        
        if (elementType === 'image' && media.type === 'image') {
            const imgContainer = element.querySelector('.image-placeholder') || element;
            imgContainer.innerHTML = `<img src="${media.url}" alt="${media.name}" style="max-width: 100%; height: auto;">`;
        } else if (elementType === 'video' && media.type === 'video') {
            const videoContainer = element.querySelector('.video-placeholder') || element;
            videoContainer.innerHTML = `
                <video controls style="max-width: 100%; height: auto;">
                    <source src="${media.url}" type="${media.mimeType}">
                    Ваш браузер не поддерживает видео.
                </video>
            `;
        }
        
        this.vb.addToHistory();
        this.vb.showNotification(`Медиафайл ${media.name} вставлен`, 'success');
    }
    
    createMediaElement(media) {
        let elementType = 'image';
        
        if (media.type === 'video') elementType = 'video';
        else if (media.type === 'audio') elementType = 'audio';
        
        const element = this.vb.createElement(elementType);
        if (element) {
            this.insertMediaIntoElement(media, element);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Статистика
    getMediaStats() {
        const media = Array.from(this.mediaLibrary.values());
        
        return {
            total: media.length,
            byType: {
                image: media.filter(m => m.type === 'image').length,
                video: media.filter(m => m.type === 'video').length,
                audio: media.filter(m => m.type === 'audio').length,
                document: media.filter(m => m.type === 'document').length
            },
            totalSize: media.reduce((sum, m) => sum + (m.size || 0), 0),
            mostUsed: media.sort((a, b) => (b.usageCount || 0) - (a.usageCount || 0)).slice(0, 5)
        };
    }
}