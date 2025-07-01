/**
 * Content Editor - Основной JavaScript файл
 * Полная функциональность для визуального редактора контента
 */

class ContentEditor {
    constructor() {
        this.currentPageId = null;
        this.contentData = { components: [] };
        this.history = [];
        this.historyIndex = -1;
        this.maxHistorySize = 50;
        this.autosaveInterval = null;
        this.autosaveEnabled = true;
        this.autosaveDelay = 30000; // 30 секунд
        this.isDirty = false;
        this.selectedComponent = null;
        this.draggedComponent = null;
        this.previewMode = false;
        
        // API endpoints
        this.endpoints = {
            save: '/content-editor/save',
            autosave: '/content-editor/autosave',
            preview: '/content-editor/preview',
            upload: '/content-editor/upload-media',
            templates: '/content-editor/templates',
            hierarchy: '/content-editor/hierarchy'
        };
        
        this.init();
    }

    /**
     * Инициализация редактора
     */
    init() {
        console.log('🚀 Initializing Content Editor...');
        
        this.initEventListeners();
        this.initDragAndDrop();
        this.initKeyboardShortcuts();
        this.initAutosave();
        this.initUndoRedo();
        this.initToolbar();
        this.initSidebar();
        this.initPropertiesPanel();
        this.initPreviewMode();
        this.loadExistingContent();
        
        console.log('✅ Content Editor initialized successfully!');
    }

    /**
     * Инициализация обработчиков событий
     */
    initEventListeners() {
        // Обработка изменений в компонентах
        document.addEventListener('input', (e) => {
            if (e.target.closest('.content-block')) {
                this.markAsDirty();
                this.updateComponentData(e.target.closest('.content-block'));
            }
        });

        // Обработка фокуса на компонентах
        document.addEventListener('focusin', (e) => {
            const block = e.target.closest('.content-block');
            if (block) {
                this.selectComponent(block);
            }
        });

        // Обработка клика вне компонентов
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.content-block') && !e.target.closest('.toolbar-button')) {
                this.deselectAllComponents();
            }
        });

        // Обработка изменений в свойствах
        document.addEventListener('change', (e) => {
            if (e.target.closest('.properties-content')) {
                this.updateComponentProperties(e.target);
            }
        });

        // Обработка загрузки файлов
        document.addEventListener('change', (e) => {
            if (e.target.type === 'file') {
                this.handleFileUpload(e.target);
            }
        });

        // Обработка перетаскивания файлов
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length > 0) {
                this.handleFileDrop(e);
            }
        });

        // Обработка изменения размера окна
        window.addEventListener('resize', this.debounce(() => {
            this.updatePreviewSize();
        }, 250));

        // Обработка ухода со страницы
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = 'У вас есть несохраненные изменения. Продолжить?';
                return e.returnValue;
            }
        });
    }

    /**
     * Инициализация Drag & Drop
     */
    initDragAndDrop() {
        const workspaceArea = document.getElementById('workspaceArea');
        const componentItems = document.querySelectorAll('.component-item');

        // Drag start для компонентов
        componentItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                this.draggedComponent = {
                    type: item.dataset.component,
                    element: item
                };
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'copy';
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
                this.draggedComponent = null;
            });
        });

        // Drop zone обработчики
        if (workspaceArea) {
            workspaceArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'copy';
                workspaceArea.classList.add('drag-over');
            });

            workspaceArea.addEventListener('dragleave', (e) => {
                if (!workspaceArea.contains(e.relatedTarget)) {
                    workspaceArea.classList.remove('drag-over');
                }
            });

            workspaceArea.addEventListener('drop', (e) => {
                e.preventDefault();
                workspaceArea.classList.remove('drag-over');
                
                if (this.draggedComponent) {
                    this.addComponent(this.draggedComponent.type);
                }
            });
        }

        // Drag & Drop для переупорядочивания компонентов
        this.initComponentReordering();
    }

    /**
     * Инициализация переупорядочивания компонентов
     */
    initComponentReordering() {
        const workspaceArea = document.getElementById('workspaceArea');
        
        if (!workspaceArea) return;

        // Sortable для компонентов
        new Sortable(workspaceArea, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onStart: (evt) => {
                evt.item.classList.add('dragging');
            },
            onEnd: (evt) => {
                evt.item.classList.remove('dragging');
                this.updateComponentOrder();
                this.markAsDirty();
            }
        });
    }

    /**
     * Инициализация горячих клавиш
     */
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S - Сохранение
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveContent();
            }

            // Ctrl+Z - Отмена
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                this.undo();
            }

            // Ctrl+Y - Повтор
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                this.redo();
            }

            // Ctrl+P - Предпросмотр
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                this.togglePreview();
            }

            // Delete - Удаление компонента
            if (e.key === 'Delete' && this.selectedComponent) {
                e.preventDefault();
                this.deleteComponent(this.selectedComponent);
            }

            // Escape - Отмена выбора
            if (e.key === 'Escape') {
                this.deselectAllComponents();
            }
        });
    }

    /**
     * Инициализация автосохранения
     */
    initAutosave() {
        if (this.autosaveEnabled) {
            this.autosaveInterval = setInterval(() => {
                if (this.isDirty && this.currentPageId) {
                    this.autosaveContent();
                }
            }, this.autosaveDelay);
        }
    }

    /**
     * Инициализация системы Undo/Redo
     */
    initUndoRedo() {
        this.saveToHistory();
    }

    /**
     * Инициализация панели инструментов
     */
    initToolbar() {
        const toolbar = document.querySelector('.content-editor-toolbar');
        if (!toolbar) return;

        // Кнопка сохранения
        const saveBtn = toolbar.querySelector('[data-action="save"]');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveContent());
        }

        // Кнопка публикации
        const publishBtn = toolbar.querySelector('[data-action="publish"]');
        if (publishBtn) {
            publishBtn.addEventListener('click', () => this.publishContent());
        }

        // Кнопка предпросмотра
        const previewBtn = toolbar.querySelector('[data-action="preview"]');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => this.togglePreview());
        }

        // Переключатель автосохранения
        const autosaveToggle = toolbar.querySelector('#autosaveToggle');
        if (autosaveToggle) {
            autosaveToggle.addEventListener('change', (e) => {
                this.autosaveEnabled = e.target.checked;
                if (this.autosaveEnabled) {
                    this.initAutosave();
                } else {
                    clearInterval(this.autosaveInterval);
                }
            });
        }

        // Выбор шаблона
        const templateSelect = toolbar.querySelector('#templateSelect');
        if (templateSelect) {
            templateSelect.addEventListener('change', (e) => {
                this.loadTemplate(e.target.value);
            });
        }
    }

    /**
     * Инициализация боковой панели
     */
    initSidebar() {
        const sidebar = document.querySelector('.content-editor-sidebar');
        if (!sidebar) return;

        // Переключатель сворачивания
        const toggleBtn = sidebar.querySelector('.sidebar-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
            });
        }

        // Переключение вкладок
        const tabs = sidebar.querySelectorAll('.nav-link');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const target = tab.getAttribute('data-bs-target');
                this.switchSidebarTab(target);
            });
        });
    }

    /**
     * Инициализация панели свойств
     */
    initPropertiesPanel() {
        const propertiesPanel = document.querySelector('.content-editor-properties');
        if (!propertiesPanel) return;

        // Обработка изменений свойств
        const inputs = propertiesPanel.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateComponentProperties(e.target);
            });
        });
    }

    /**
     * Инициализация режима предпросмотра
     */
    initPreviewMode() {
        const previewTab = document.querySelector('[data-bs-target="#preview"]');
        if (previewTab) {
            previewTab.addEventListener('click', () => {
                this.updatePreview();
            });
        }
    }

    /**
     * Загрузка существующего контента
     */
    loadExistingContent() {
        const urlParams = new URLSearchParams(window.location.search);
        const pageId = urlParams.get('page_id');
        const templateId = urlParams.get('template_id');

        if (pageId) {
            this.loadPage(pageId);
        } else if (templateId) {
            this.loadTemplate(templateId);
        } else {
            this.createNewPage();
        }
    }

    /**
     * Добавление компонента
     */
    addComponent(type) {
        const componentId = 'component_' + Date.now();
        const component = this.createComponentElement(type, componentId);
        
        const workspaceArea = document.getElementById('workspaceArea');
        if (workspaceArea) {
            // Удаляем placeholder если это первый компонент
            const placeholder = workspaceArea.querySelector('.drop-zone');
            if (placeholder) {
                placeholder.remove();
            }
            
            workspaceArea.appendChild(component);
        }

        this.contentData.components.push({
            id: componentId,
            type: type,
            content: this.getDefaultContent(type),
            properties: this.getDefaultProperties(type)
        });

        this.markAsDirty();
        this.saveToHistory();
        this.selectComponent(component);
        
        this.showNotification(`Компонент "${this.getComponentName(type)}" добавлен`, 'success');
    }

    /**
     * Создание элемента компонента
     */
    createComponentElement(type, id) {
        const component = document.createElement('div');
        component.className = 'content-block';
        component.dataset.componentId = id;
        component.dataset.type = type;

        const header = this.createComponentHeader(type, id);
        const content = this.createComponentContent(type, id);

        component.appendChild(header);
        component.appendChild(content);

        return component;
    }

    /**
     * Создание заголовка компонента
     */
    createComponentHeader(type, id) {
        const header = document.createElement('div');
        header.className = 'block-header';

        const typeInfo = document.createElement('div');
        typeInfo.className = 'block-type';
        typeInfo.innerHTML = `
            <i class="bi bi-${this.getComponentIcon(type)}"></i>
            <span>${this.getComponentName(type)}</span>
        `;

        const actions = document.createElement('div');
        actions.className = 'block-actions';
        actions.innerHTML = `
            <button class="block-action" onclick="contentEditor.duplicateComponent('${id}')" title="Дублировать">
                <i class="bi bi-files"></i>
            </button>
            <button class="block-action danger" onclick="contentEditor.deleteComponent('${id}')" title="Удалить">
                <i class="bi bi-trash"></i>
            </button>
        `;

        header.appendChild(typeInfo);
        header.appendChild(actions);

        return header;
    }

    /**
     * Создание содержимого компонента
     */
    createComponentContent(type, id) {
        const content = document.createElement('div');
        content.className = 'block-content';

        switch (type) {
            case 'text':
                content.contentEditable = true;
                content.innerHTML = '<p>Введите текст здесь...</p>';
                break;
            case 'heading':
                content.contentEditable = true;
                content.innerHTML = '<h2>Заголовок</h2>';
                break;
            case 'image':
                content.innerHTML = `
                    <div class="image-upload-area" onclick="contentEditor.triggerImageUpload('${id}')">
                        <i class="bi bi-image"></i>
                        <p>Кликните для загрузки изображения</p>
                        <input type="file" class="d-none" accept="image/*" data-component-id="${id}">
                    </div>
                `;
                break;
            case 'video':
                content.innerHTML = `
                    <div class="video-upload-area" onclick="contentEditor.triggerVideoUpload('${id}')">
                        <i class="bi bi-play-circle"></i>
                        <p>Кликните для загрузки видео</p>
                        <input type="file" class="d-none" accept="video/*" data-component-id="${id}">
                    </div>
                `;
                break;
            case 'button':
                content.contentEditable = true;
                content.innerHTML = '<button class="component-button">Кнопка</button>';
                break;
            case 'table':
                content.innerHTML = `
                    <div class="table-builder">
                        <h4>Конструктор таблицы</h4>
                        <button class="btn btn-sm btn-primary" onclick="contentEditor.addTableRow('${id}')">
                            Добавить строку
                        </button>
                    </div>
                `;
                break;
            case 'code':
                content.innerHTML = `
                    <div class="code-editor">
                        <select class="form-select form-select-sm mb-2">
                            <option value="html">HTML</option>
                            <option value="css">CSS</option>
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                        </select>
                        <textarea class="form-control" rows="6" placeholder="Введите код..."></textarea>
                    </div>
                `;
                break;
            case 'card':
                content.innerHTML = `
                    <div class="card-content">
                        <h3>Заголовок карточки</h3>
                        <p>Содержимое карточки</p>
                    </div>
                `;
                break;
            case 'divider':
                content.innerHTML = '<hr class="component-divider">';
                break;
            default:
                content.innerHTML = '<p>Неизвестный тип компонента</p>';
        }

        return content;
    }

    /**
     * Выбор компонента
     */
    selectComponent(component) {
        this.deselectAllComponents();
        component.classList.add('selected');
        this.selectedComponent = component;
        this.updatePropertiesPanel(component);
    }

    /**
     * Отмена выбора всех компонентов
     */
    deselectAllComponents() {
        document.querySelectorAll('.content-block.selected').forEach(block => {
            block.classList.remove('selected');
        });
        this.selectedComponent = null;
        this.hidePropertiesPanel();
    }

    /**
     * Обновление панели свойств
     */
    updatePropertiesPanel(component) {
        const propertiesPanel = document.querySelector('.content-editor-properties');
        if (!propertiesPanel) return;

        const componentId = component.dataset.componentId;
        const componentType = component.dataset.type;
        const componentData = this.contentData.components.find(c => c.id === componentId);

        if (!componentData) return;

        const propertiesContent = propertiesPanel.querySelector('.properties-content');
        propertiesContent.innerHTML = this.generatePropertiesHTML(componentType, componentData);

        // Добавляем обработчики событий
        const inputs = propertiesContent.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.updateComponentProperty(componentId, e.target.name, e.target.value);
            });
        });
    }

    /**
     * Скрытие панели свойств
     */
    hidePropertiesPanel() {
        const propertiesPanel = document.querySelector('.content-editor-properties');
        if (propertiesPanel) {
            const propertiesContent = propertiesPanel.querySelector('.properties-content');
            propertiesContent.innerHTML = '<p class="text-muted">Выберите компонент для редактирования свойств</p>';
        }
    }

    /**
     * Генерация HTML для свойств компонента
     */
    generatePropertiesHTML(type, data) {
        const component = window.editorComponents?.getComponent(type);
        if (!component || !component.properties) {
            return '<p>Свойства недоступны для этого компонента</p>';
        }

        let html = '<div class="properties-panel">';
        
        component.properties.forEach(property => {
            const value = data.properties[property.name] || property.defaultValue || '';
            html += `
                <div class="property-item">
                    <label class="property-label">${property.label}</label>
                    ${this.generatePropertyInput(property, value)}
                </div>
            `;
        });
        
        html += '</div>';
        return html;
    }

    /**
     * Генерация поля ввода для свойства
     */
    generatePropertyInput(property, value) {
        switch (property.type) {
            case 'text':
                return `<input type="text" class="property-input" name="${property.name}" value="${value}" placeholder="${property.placeholder || ''}">`;
            
            case 'textarea':
                return `<textarea class="property-textarea" name="${property.name}" rows="3" placeholder="${property.placeholder || ''}">${value}</textarea>`;
            
            case 'select':
                const options = property.options.map(opt => 
                    `<option value="${opt.value}" ${value === opt.value ? 'selected' : ''}>${opt.label}</option>`
                ).join('');
                return `<select class="property-select" name="${property.name}">${options}</select>`;
            
            case 'color':
                return `<input type="color" class="property-color" name="${property.name}" value="${value || '#000000'}">`;
            
            case 'checkbox':
                return `<div class="property-checkbox">
                    <input type="checkbox" name="${property.name}" ${value ? 'checked' : ''}>
                    <span>${property.label}</span>
                </div>`;
            
            default:
                return `<input type="text" class="property-input" name="${property.name}" value="${value}">`;
        }
    }

    /**
     * Обновление свойства компонента
     */
    updateComponentProperty(componentId, propertyName, value) {
        const component = this.contentData.components.find(c => c.id === componentId);
        if (component) {
            component.properties[propertyName] = value;
            this.markAsDirty();
            this.updateComponentDisplay(componentId);
        }
    }

    /**
     * Обновление отображения компонента
     */
    updateComponentDisplay(componentId) {
        const componentElement = document.querySelector(`[data-component-id="${componentId}"]`);
        if (!componentElement) return;

        const component = this.contentData.components.find(c => c.id === componentId);
        if (!component) return;

        // Обновляем отображение в зависимости от типа компонента
        const componentConfig = window.editorComponents?.getComponent(component.type);
        if (componentConfig && componentConfig.render) {
            const renderedContent = componentConfig.render(component);
            const contentArea = componentElement.querySelector('.block-content');
            if (contentArea) {
                contentArea.innerHTML = renderedContent;
            }
        }
    }

    /**
     * Сохранение контента
     */
    async saveContent() {
        try {
            this.updateContentData();
            
            const response = await this.apiCall(this.endpoints.save, {
                page_id: this.currentPageId,
                content_data: this.contentData,
                title: document.getElementById('pageTitle')?.value || 'Новая страница',
                status: document.getElementById('pageStatus')?.value || 'draft'
            });

            if (response.success) {
                this.isDirty = false;
                this.showNotification('Контент успешно сохранен', 'success');
                return response;
            } else {
                throw new Error(response.error || 'Ошибка сохранения');
            }
        } catch (error) {
            console.error('Error saving content:', error);
            this.showNotification('Ошибка сохранения: ' + error.message, 'error');
            throw error;
        }
    }

    /**
     * Автосохранение
     */
    async autosaveContent() {
        try {
            this.updateContentData();
            
            const response = await this.apiCall(this.endpoints.autosave, {
                page_id: this.currentPageId,
                content_data: this.contentData
            });

            if (response.success) {
                this.isDirty = false;
                console.log('✅ Content autosaved');
            }
        } catch (error) {
            console.error('Error autosaving content:', error);
        }
    }

    /**
     * Публикация контента
     */
    async publishContent() {
        try {
            await this.saveContent();
            
            const response = await this.apiCall(this.endpoints.save, {
                page_id: this.currentPageId,
                content_data: this.contentData,
                status: 'published'
            });

            if (response.success) {
                this.showNotification('Контент успешно опубликован', 'success');
                return response;
            } else {
                throw new Error(response.error || 'Ошибка публикации');
            }
        } catch (error) {
            console.error('Error publishing content:', error);
            this.showNotification('Ошибка публикации: ' + error.message, 'error');
            throw error;
        }
    }

    /**
     * Загрузка страницы
     */
    async loadPage(pageId) {
        try {
            const response = await this.apiCall(`/content-editor/page/${pageId}`, 'GET');
            
            if (response.success) {
                this.currentPageId = pageId;
                this.contentData = response.data.content_data || { components: [] };
                this.renderContent();
                this.showNotification('Страница загружена', 'success');
            } else {
                throw new Error(response.error || 'Ошибка загрузки страницы');
            }
        } catch (error) {
            console.error('Error loading page:', error);
            this.showNotification('Ошибка загрузки страницы: ' + error.message, 'error');
        }
    }

    /**
     * Загрузка шаблона
     */
    async loadTemplate(templateId) {
        try {
            const response = await this.apiCall(`/content-editor/template/${templateId}`, 'GET');
            
            if (response.success) {
                this.contentData = response.data.content_data || { components: [] };
                this.renderContent();
                this.showNotification('Шаблон загружен', 'success');
            } else {
                throw new Error(response.error || 'Ошибка загрузки шаблона');
            }
        } catch (error) {
            console.error('Error loading template:', error);
            this.showNotification('Ошибка загрузки шаблона: ' + error.message, 'error');
        }
    }

    /**
     * Создание новой страницы
     */
    createNewPage() {
        this.contentData = { components: [] };
        this.currentPageId = null;
        this.renderContent();
        this.showNotification('Создана новая страница', 'info');
    }

    /**
     * Рендеринг контента
     */
    renderContent() {
        const workspaceArea = document.getElementById('workspaceArea');
        if (!workspaceArea) return;

        workspaceArea.innerHTML = '';

        if (this.contentData.components.length === 0) {
            workspaceArea.innerHTML = `
                <div class="drop-zone">
                    <i class="bi bi-plus-circle"></i>
                    <p>Перетащите компоненты сюда или выберите из панели</p>
                </div>
            `;
        } else {
            this.contentData.components.forEach(componentData => {
                const component = this.createComponentElement(componentData.type, componentData.id);
                workspaceArea.appendChild(component);
            });
        }
    }

    /**
     * Обновление данных контента
     */
    updateContentData() {
        const workspaceArea = document.getElementById('workspaceArea');
        if (!workspaceArea) return;

        this.contentData.components = [];
        
        workspaceArea.querySelectorAll('.content-block').forEach(block => {
            const componentId = block.dataset.componentId;
            const componentType = block.dataset.type;
            const content = block.querySelector('.block-content').innerHTML;
            
            this.contentData.components.push({
                id: componentId,
                type: componentType,
                content: content,
                properties: this.getComponentProperties(componentId)
            });
        });
    }

    /**
     * Получение свойств компонента
     */
    getComponentProperties(componentId) {
        const component = this.contentData.components.find(c => c.id === componentId);
        return component ? component.properties : {};
    }

    /**
     * Обновление данных компонента
     */
    updateComponentData(componentElement) {
        const componentId = componentElement.dataset.componentId;
        const component = this.contentData.components.find(c => c.id === componentId);
        
        if (component) {
            component.content = componentElement.querySelector('.block-content').innerHTML;
        }
    }

    /**
     * Обновление свойств компонента
     */
    updateComponentProperties(input) {
        const componentId = this.selectedComponent?.dataset.componentId;
        if (!componentId) return;

        const propertyName = input.name;
        const value = input.type === 'checkbox' ? input.checked : input.value;
        
        this.updateComponentProperty(componentId, propertyName, value);
    }

    /**
     * Удаление компонента
     */
    deleteComponent(componentId) {
        if (typeof componentId === 'string') {
            const component = document.querySelector(`[data-component-id="${componentId}"]`);
            if (component) {
                component.remove();
            }
        } else if (componentId && componentId.dataset.componentId) {
            componentId.remove();
        }

        this.markAsDirty();
        this.saveToHistory();
        this.deselectAllComponents();
        this.showNotification('Компонент удален', 'info');
    }

    /**
     * Дублирование компонента
     */
    duplicateComponent(componentId) {
        const originalComponent = this.contentData.components.find(c => c.id === componentId);
        if (!originalComponent) return;

        const newComponentId = 'component_' + Date.now();
        const duplicatedComponent = {
            ...originalComponent,
            id: newComponentId,
            content: originalComponent.content
        };

        this.contentData.components.push(duplicatedComponent);
        
        const newComponentElement = this.createComponentElement(duplicatedComponent.type, newComponentId);
        const originalElement = document.querySelector(`[data-component-id="${componentId}"]`);
        
        if (originalElement && originalElement.parentNode) {
            originalElement.parentNode.insertBefore(newComponentElement, originalElement.nextSibling);
        }

        this.markAsDirty();
        this.saveToHistory();
        this.showNotification('Компонент продублирован', 'success');
    }

    /**
     * Переключение вкладки боковой панели
     */
    switchSidebarTab(target) {
        const tabs = document.querySelectorAll('.nav-link');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => tab.classList.remove('active'));
        contents.forEach(content => content.classList.remove('active'));

        const activeTab = document.querySelector(`[data-bs-target="${target}"]`);
        const activeContent = document.querySelector(target);

        if (activeTab) activeTab.classList.add('active');
        if (activeContent) activeContent.classList.add('active');
    }

    /**
     * Переключение режима предпросмотра
     */
    togglePreview() {
        this.previewMode = !this.previewMode;
        
        const workspaceArea = document.getElementById('workspaceArea');
        const previewArea = document.getElementById('previewArea');
        
        if (this.previewMode) {
            workspaceArea.style.display = 'none';
            previewArea.style.display = 'block';
            this.updatePreview();
        } else {
            workspaceArea.style.display = 'block';
            previewArea.style.display = 'none';
        }
    }

    /**
     * Обновление предпросмотра
     */
    updatePreview() {
        const previewArea = document.getElementById('previewArea');
        if (!previewArea) return;

        this.updateContentData();
        
        let previewHTML = '';
        this.contentData.components.forEach(component => {
            const componentConfig = window.editorComponents?.getComponent(component.type);
            if (componentConfig && componentConfig.render) {
                previewHTML += componentConfig.render(component);
            } else {
                previewHTML += component.content;
            }
        });

        previewArea.innerHTML = previewHTML;
    }

    /**
     * Обновление размера предпросмотра
     */
    updatePreviewSize() {
        const previewArea = document.getElementById('previewArea');
        if (!previewArea) return;

        // Адаптивный размер для разных устройств
        const width = window.innerWidth;
        if (width < 768) {
            previewArea.style.width = '100%';
        } else if (width < 1024) {
            previewArea.style.width = '768px';
        } else {
            previewArea.style.width = '1024px';
        }
    }

    /**
     * Загрузка файлов
     */
    async handleFileUpload(input) {
        const file = input.files[0];
        if (!file) return;

        const componentId = input.dataset.componentId;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('component_id', componentId);

        try {
            const response = await fetch(this.endpoints.upload, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.updateComponentProperty(componentId, 'src', result.url);
                this.showNotification('Файл успешно загружен', 'success');
            } else {
                throw new Error(result.error || 'Ошибка загрузки файла');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showNotification('Ошибка загрузки файла: ' + error.message, 'error');
        }
    }

    /**
     * Обработка перетаскивания файлов
     */
    handleFileDrop(e) {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files);
        
        files.forEach(file => {
            const input = document.createElement('input');
            input.type = 'file';
            input.files = e.dataTransfer;
            this.handleFileUpload(input);
        });
    }

    /**
     * Запуск загрузки изображения
     */
    triggerImageUpload(componentId) {
        const input = document.querySelector(`input[data-component-id="${componentId}"]`);
        if (input) {
            input.click();
        }
    }

    /**
     * Запуск загрузки видео
     */
    triggerVideoUpload(componentId) {
        const input = document.querySelector(`input[data-component-id="${componentId}"]`);
        if (input) {
            input.click();
        }
    }

    /**
     * Система Undo/Redo
     */
    saveToHistory() {
        // Удаляем все записи после текущего индекса
        this.history = this.history.slice(0, this.historyIndex + 1);
        
        // Добавляем новое состояние
        this.history.push(JSON.stringify(this.contentData));
        this.historyIndex++;
        
        // Ограничиваем размер истории
        if (this.history.length > this.maxHistorySize) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.contentData = JSON.parse(this.history[this.historyIndex]);
            this.renderContent();
            this.showNotification('Отменено', 'info');
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.contentData = JSON.parse(this.history[this.historyIndex]);
            this.renderContent();
            this.showNotification('Повторено', 'info');
        }
    }

    /**
     * Пометить как измененный
     */
    markAsDirty() {
        this.isDirty = true;
        this.updateSaveStatus();
    }

    /**
     * Обновление статуса сохранения
     */
    updateSaveStatus() {
        const saveStatus = document.querySelector('.save-status');
        if (saveStatus) {
            saveStatus.textContent = this.isDirty ? 'Не сохранено' : 'Сохранено';
            saveStatus.className = `save-status ${this.isDirty ? 'unsaved' : 'saved'}`;
        }
    }

    /**
     * API вызовы
     */
    async apiCall(url, method = 'POST', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return response.json();
    }

    /**
     * Получение CSRF токена
     */
    getCsrfToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    /**
     * Показ уведомлений
     */
    showNotification(message, type = 'info') {
        // Используем существующую систему уведомлений
        if (window.showNotification) {
            window.showNotification(message, type);
        } else if (window.AdminUnified && window.AdminUnified.showNotification) {
            window.AdminUnified.showNotification(message, type);
        } else {
            // Fallback уведомление
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
            notification.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                min-width: 300px;
                max-width: 500px;
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 5000);
        }
    }

    /**
     * Утилиты
     */
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

    getComponentName(type) {
        const component = window.editorComponents?.getComponent(type);
        return component ? component.name : 'Неизвестный компонент';
    }

    getComponentIcon(type) {
        const component = window.editorComponents?.getComponent(type);
        return component ? component.icon : 'question-circle';
    }

    getDefaultContent(type) {
        const component = window.editorComponents?.getComponent(type);
        return component ? component.defaultContent : '';
    }

    getDefaultProperties(type) {
        const component = window.editorComponents?.getComponent(type);
        return component ? { ...component.defaultProperties } : {};
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.contentEditor = new ContentEditor();
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ContentEditor;
} 