/**
 * Template Manager - Page Templates System
 * Система управления шаблонами страниц для Visual Builder
 */

export class TemplateManager {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.templates = new Map();
        this.categories = new Map();
        this.favorites = new Set();
        this.recentTemplates = [];
        this.maxRecentTemplates = 10;
        
        this.init();
    }
    
    init() {
        this.loadTemplates();
        this.loadUserPreferences();
        this.setupEventListeners();
        console.info('📋 Template Manager готов');
    }
    
    setupEventListeners() {
        // Обработка горячих клавиш для шаблонов
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.openTemplateLibrary();
            }
        });
    }
    
    loadTemplates() {
        // Загружаем встроенные шаблоны
        this.loadBuiltinTemplates();
        
        // Загружаем пользовательские шаблоны
        this.loadUserTemplates();
        
        // Загружаем шаблоны с сервера
        this.loadServerTemplates();
    }
    
    loadBuiltinTemplates() {
        const builtinTemplates = [
            {
                id: 'blank',
                name: 'Пустая страница',
                description: 'Начните с чистого листа',
                category: 'basic',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkZGRkZGIiBzdHJva2U9IiNFRUVFRUUiLz4KPHN2ZyB4PSIxMDAiIHk9Ijc1IiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0iI0NDQ0NDQyI+CjxwYXRoIGQ9Ik0yMCAxMEwxMCAyMEwyMCAzMEwzMCAyMEwyMCAxMFoiLz4KPC9zdmc+Cjwvc3ZnPgo=',
                content: '<div class="canvas-empty"><div class="canvas-empty-icon">🎨</div><div class="canvas-empty-content"><h3>Начните создавать страницу</h3><p>Перетащите компоненты из левой панели сюда</p></div></div>',
                tags: ['пустая', 'базовая', 'начало'],
                author: 'Dental Academy',
                version: '1.0',
                isBuiltin: true
            },
            {
                id: 'hero-landing',
                name: 'Hero Landing Page',
                description: 'Современная landing страница с hero секцией',
                category: 'landing',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjM0VDREMxIi8+Cjx0ZXh0IHg9IjEwMCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkhlcm8gTGFuZGluZzwvdGV4dD4KPC9zdmc+Cg==',
                content: `
                    <div class="draggable-element element-hero" data-type="hero">
                        <div class="element-content">
                            <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #3ECDC1 0%, #6C5CE7 100%); color: white; border-radius: 12px;">
                                <h1 contenteditable="true" style="font-size: 3rem; margin-bottom: 1rem; font-weight: bold;">Добро пожаловать в Dental Academy</h1>
                                <p contenteditable="true" style="font-size: 1.25rem; margin-bottom: 2rem; opacity: 0.9; max-width: 600px; margin-left: auto; margin-right: auto;">Современное образование в области стоматологии. Изучайте, практикуйтесь, развивайтесь.</p>
                                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                                    <button style="padding: 1rem 2rem; background: white; color: #3ECDC1; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">Начать обучение</button>
                                    <button style="padding: 1rem 2rem; background: transparent; color: white; border: 2px solid white; border-radius: 8px; font-weight: 600; cursor: pointer;">Узнать больше</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="draggable-element element-feature" data-type="feature">
                        <div class="element-content">
                            <div style="text-align: center; margin: 2rem 0;">
                                <h2 contenteditable="true" style="font-size: 2rem; margin-bottom: 1rem;">Наши преимущества</h2>
                                <p contenteditable="true" style="color: #666; font-size: 1.125rem;">Почему выбирают Dental Academy</p>
                            </div>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">
                                <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
                                    <h3 contenteditable="true" style="margin-bottom: 1rem;">Экспертное обучение</h3>
                                    <p contenteditable="true" style="color: #666; line-height: 1.6;">Курсы от ведущих специалистов в области стоматологии</p>
                                </div>
                                <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">💻</div>
                                    <h3 contenteditable="true" style="margin-bottom: 1rem;">Интерактивные материалы</h3>
                                    <p contenteditable="true" style="color: #666; line-height: 1.6;">Современные технологии обучения и практические задания</p>
                                </div>
                                <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                                    <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
                                    <h3 contenteditable="true" style="margin-bottom: 1rem;">Доступность</h3>
                                    <p contenteditable="true" style="color: #666; line-height: 1.6;">Учитесь в любое время и с любого устройства</p>
                                </div>
                            </div>
                        </div>
                    </div>
                `,
                tags: ['landing', 'hero', 'современный', 'градиент'],
                author: 'Dental Academy',
                version: '1.0',
                isBuiltin: true
            },
            {
                id: 'dental-education',
                name: 'Образовательная страница',
                description: 'Страница для образовательного контента по стоматологии',
                category: 'education',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjMDBENjhGIi8+Cjx0ZXh0IHg9IjEwMCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPk9idXplbmllPC90ZXh0Pgo8L3N2Zz4K',
                content: `
                    <div class="draggable-element element-text" data-type="text">
                        <div class="element-content">
                            <div contenteditable="true">
                                <h1>Анатомия зубов человека</h1>
                                <p>Изучение анатомии зубов является фундаментальной основой для понимания стоматологических процедур и диагностики заболеваний полости рта.</p>
                            </div>
                        </div>
                    </div>
                    <div class="draggable-element element-image" data-type="image">
                        <div class="element-content">
                            <div class="image-placeholder" onclick="visualBuilder.selectImage(this)">
                                <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer;">
                                    <div style="font-size: 2rem; margin-bottom: 1rem;">🦷</div>
                                    <div>Добавьте изображение анатомии зубов</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="draggable-element element-quiz" data-type="quiz">
                        <div class="element-content">
                            <h3 contenteditable="true" style="margin-bottom: 1rem;">Проверьте свои знания</h3>
                            <div class="quiz-options">
                                <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                                    <input type="radio" name="quiz_1" style="margin-right: 0.5rem;">
                                    <span contenteditable="true">Сколько зубов у взрослого человека?</span>
                                </label>
                                <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                                    <input type="radio" name="quiz_1" style="margin-right: 0.5rem;">
                                    <span contenteditable="true">Какая часть зуба находится над десной?</span>
                                </label>
                                <label style="display: block; margin: 0.5rem 0; cursor: pointer;">
                                    <input type="radio" name="quiz_1" style="margin-right: 0.5rem;">
                                    <span contenteditable="true">Как называется твердая ткань, покрывающая коронку зуба?</span>
                                </label>
                            </div>
                        </div>
                    </div>
                `,
                tags: ['образование', 'анатомия', 'зубы', 'тест'],
                author: 'Dental Academy',
                version: '1.0',
                isBuiltin: true
            },
            {
                id: 'contact-form',
                name: 'Контактная форма',
                description: 'Страница с формой обратной связи',
                category: 'forms',
                thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkZDNTA3Ii8+Cjx0ZXh0IHg9IjEwMCIgeT0iNzUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkZvcm1hPC90ZXh0Pgo8L3N2Zz4K',
                content: `
                    <div class="draggable-element element-text" data-type="text">
                        <div class="element-content">
                            <div contenteditable="true">
                                <h1>Свяжитесь с нами</h1>
                                <p>У вас есть вопросы? Заполните форму ниже, и мы свяжемся с вами в ближайшее время.</p>
                            </div>
                        </div>
                    </div>
                    <div class="draggable-element element-form" data-type="form">
                        <div class="element-content">
                            <form style="max-width: 500px; margin: 0 auto;">
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Имя:</label>
                                    <input type="text" class="template-name-input" placeholder="Введите ваше имя" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Email:</label>
                                    <input type="email" placeholder="your@email.com" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Тема:</label>
                                    <select style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                                        <option>Общие вопросы</option>
                                        <option>Техническая поддержка</option>
                                        <option>Партнерство</option>
                                        <option>Другое</option>
                                    </select>
                                </div>
                                <div style="margin-bottom: 1rem;">
                                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Сообщение:</label>
                                    <textarea placeholder="Введите ваше сообщение" rows="4" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical;"></textarea>
                                </div>
                                <button type="submit" style="padding: 0.75rem 1.5rem; background: #3ECDC1; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; width: 100%;">Отправить сообщение</button>
                            </form>
                        </div>
                    </div>
                `,
                tags: ['форма', 'контакт', 'обратная связь', 'сообщение'],
                author: 'Dental Academy',
                version: '1.0',
                isBuiltin: true
            }
        ];
        
        builtinTemplates.forEach(template => {
            this.templates.set(template.id, template);
        });
        
        // Создаем категории
        this.createCategories();
    }
    
    createCategories() {
        const categoryData = [
            { id: 'basic', name: 'Базовые', icon: 'bi-file-earmark', color: '#6c757d' },
            { id: 'landing', name: 'Landing Pages', icon: 'bi-rocket', color: '#3ECDC1' },
            { id: 'education', name: 'Образование', icon: 'bi-book', color: '#00D68F' },
            { id: 'forms', name: 'Формы', icon: 'bi-card-text', color: '#FFC107' },
            { id: 'medical', name: 'Медицинские', icon: 'bi-heart-pulse', color: '#FF3333' },
            { id: 'user', name: 'Пользовательские', icon: 'bi-person', color: '#6C5CE7' }
        ];
        
        categoryData.forEach(category => {
            this.categories.set(category.id, category);
        });
    }
    
    async loadUserTemplates() {
        try {
            const saved = localStorage.getItem('vb-user-templates');
            if (saved) {
                const userTemplates = JSON.parse(saved);
                userTemplates.forEach(template => {
                    template.isUserTemplate = true;
                    this.templates.set(template.id, template);
                });
            }
        } catch (error) {
            console.warn('Ошибка загрузки пользовательских шаблонов:', error);
        }
    }
    
    async loadServerTemplates() {
        try {
            const response = await fetch('/api/visual-builder/templates', {
                headers: {
                    'X-CSRFToken': this.vb.config.csrfToken
                }
            });
            
            if (response.ok) {
                const serverTemplates = await response.json();
                serverTemplates.forEach(template => {
                    template.isServerTemplate = true;
                    this.templates.set(template.id, template);
                });
            }
        } catch (error) {
            console.warn('Ошибка загрузки серверных шаблонов:', error);
        }
    }
    
    loadUserPreferences() {
        try {
            const saved = localStorage.getItem('vb-template-preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.favorites = new Set(preferences.favorites || []);
                this.recentTemplates = preferences.recent || [];
            }
        } catch (error) {
            console.warn('Ошибка загрузки предпочтений шаблонов:', error);
        }
    }
    
    saveUserPreferences() {
        try {
            const preferences = {
                favorites: Array.from(this.favorites),
                recent: this.recentTemplates
            };
            localStorage.setItem('vb-template-preferences', JSON.stringify(preferences));
        } catch (error) {
            console.warn('Ошибка сохранения предпочтений шаблонов:', error);
        }
    }
    
    // Основные методы
    getTemplate(id) {
        return this.templates.get(id);
    }
    
    getTemplatesByCategory(category) {
        return Array.from(this.templates.values())
            .filter(template => template.category === category);
    }
    
    getFavoriteTemplates() {
        return Array.from(this.templates.values())
            .filter(template => this.favorites.has(template.id));
    }
    
    getRecentTemplates() {
        return this.recentTemplates
            .map(id => this.templates.get(id))
            .filter(template => template);
    }
    
    searchTemplates(query) {
        const searchTerm = query.toLowerCase();
        return Array.from(this.templates.values())
            .filter(template => 
                template.name.toLowerCase().includes(searchTerm) ||
                template.description.toLowerCase().includes(searchTerm) ||
                template.tags.some(tag => tag.toLowerCase().includes(searchTerm))
            );
    }
    
    applyTemplate(templateId) {
        const template = this.getTemplate(templateId);
        if (!template) {
            this.vb.showNotification('Шаблон не найден', 'error');
            return false;
        }
        
        try {
            // Очищаем canvas
            this.vb.dom.canvas.innerHTML = '';
            
            // Применяем контент шаблона
            this.vb.dom.canvas.innerHTML = template.content;
            
            // Настраиваем элементы
            this.vb.setupExistingElements();
            
            // Обновляем состояние
            this.vb.addToHistory();
            this.vb.updateLayersPanel();
            
            // Добавляем в недавние
            this.addToRecent(templateId);
            
            this.vb.showNotification(`Шаблон "${template.name}" применен`, 'success');
            return true;
            
        } catch (error) {
            console.error('Ошибка применения шаблона:', error);
            this.vb.showNotification('Ошибка применения шаблона', 'error');
            return false;
        }
    }
    
    saveAsTemplate(name, description = '', category = 'user') {
        try {
            const content = this.vb.getCanvasContent();
            const template = {
                id: 'user_' + Date.now(),
                name,
                description,
                category,
                thumbnail: this.generateThumbnail(),
                content,
                tags: this.extractTags(content),
                author: 'Пользователь',
                version: '1.0',
                isUserTemplate: true,
                createdAt: new Date().toISOString()
            };
            
            this.templates.set(template.id, template);
            this.saveUserTemplates();
            
            this.vb.showNotification(`Шаблон "${name}" сохранен`, 'success');
            return template;
            
        } catch (error) {
            console.error('Ошибка сохранения шаблона:', error);
            this.vb.showNotification('Ошибка сохранения шаблона', 'error');
            return null;
        }
    }
    
    deleteTemplate(templateId) {
        const template = this.getTemplate(templateId);
        if (!template) return false;
        
        if (template.isBuiltin) {
            this.vb.showNotification('Нельзя удалить встроенный шаблон', 'warning');
            return false;
        }
        
        if (confirm(`Вы уверены, что хотите удалить шаблон "${template.name}"?`)) {
            this.templates.delete(templateId);
            this.favorites.delete(templateId);
            this.recentTemplates = this.recentTemplates.filter(id => id !== templateId);
            
            this.saveUserTemplates();
            this.saveUserPreferences();
            
            this.vb.showNotification(`Шаблон "${template.name}" удален`, 'success');
            return true;
        }
        
        return false;
    }
    
    toggleFavorite(templateId) {
        if (this.favorites.has(templateId)) {
            this.favorites.delete(templateId);
            this.vb.showNotification('Удалено из избранного', 'info');
        } else {
            this.favorites.add(templateId);
            this.vb.showNotification('Добавлено в избранное', 'success');
        }
        
        this.saveUserPreferences();
    }
    
    addToRecent(templateId) {
        // Удаляем из недавних если уже есть
        this.recentTemplates = this.recentTemplates.filter(id => id !== templateId);
        
        // Добавляем в начало
        this.recentTemplates.unshift(templateId);
        
        // Ограничиваем количество
        if (this.recentTemplates.length > this.maxRecentTemplates) {
            this.recentTemplates = this.recentTemplates.slice(0, this.maxRecentTemplates);
        }
        
        this.saveUserPreferences();
    }
    
    saveUserTemplates() {
        try {
            const userTemplates = Array.from(this.templates.values())
                .filter(template => template.isUserTemplate);
            
            localStorage.setItem('vb-user-templates', JSON.stringify(userTemplates));
        } catch (error) {
            console.warn('Ошибка сохранения пользовательских шаблонов:', error);
        }
    }
    
    generateThumbnail() {
        // Простая генерация thumbnail на основе контента
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkZGRkZGIiBzdHJva2U9IiNFRUVFRUUiLz4KPHN2ZyB4PSIxMDAiIHk9Ijc1IiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0iIzZDNzU3RCI+CjxwYXRoIGQ9Ik0yMCAxMEwxMCAyMEwyMCAzMEwzMCAyMEwyMCAxMFoiLz4KPC9zdmc+Cjwvc3ZnPgo=';
    }
    
    extractTags(content) {
        // Простое извлечение тегов из контента
        const tags = [];
        const text = content.toLowerCase();
        
        if (text.includes('зуб') || text.includes('стоматолог')) tags.push('стоматология');
        if (text.includes('форма') || text.includes('input')) tags.push('форма');
        if (text.includes('тест') || text.includes('quiz')) tags.push('тест');
        if (text.includes('изображение') || text.includes('img')) tags.push('изображение');
        if (text.includes('видео') || text.includes('video')) tags.push('видео');
        
        return tags.length > 0 ? tags : ['пользовательский'];
    }
    
    // UI методы
    openTemplateLibrary() {
        this.createTemplateModal();
    }
    
    createTemplateModal() {
        const modal = document.createElement('div');
        modal.className = 'template-modal';
        modal.innerHTML = `
            <div class="template-content">
                <div class="template-header">
                    <h3>Библиотека шаблонов</h3>
                    <button class="close-btn" onclick="this.closest('.template-modal').remove()">×</button>
                </div>
                
                <div class="template-body">
                    <div class="template-toolbar">
                        <div class="search-group">
                            <input type="text" class="template-search" placeholder="Поиск шаблонов...">
                        </div>
                        <div class="filter-group">
                            <select class="category-filter">
                                <option value="">Все категории</option>
                                ${Array.from(this.categories.values()).map(cat => 
                                    `<option value="${cat.id}">${cat.name}</option>`
                                ).join('')}
                            </select>
                        </div>
                        <div class="view-group">
                            <button class="btn btn-sm btn-primary" onclick="templateManager.saveCurrentAsTemplate()">
                                <i class="bi bi-save"></i> Сохранить как шаблон
                            </button>
                        </div>
                    </div>
                    
                    <div class="template-tabs">
                        <button class="tab-btn active" data-tab="all">Все шаблоны</button>
                        <button class="tab-btn" data-tab="favorites">Избранное</button>
                        <button class="tab-btn" data-tab="recent">Недавние</button>
                        <button class="tab-btn" data-tab="user">Мои шаблоны</button>
                    </div>
                    
                    <div class="template-grid" id="templateGrid">
                        ${this.renderTemplateGrid()}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Обработчики событий
        this.setupTemplateModalHandlers(modal);
    }
    
    setupTemplateModalHandlers(modal) {
        // Поиск
        const searchInput = modal.querySelector('.template-search');
        searchInput.addEventListener('input', (e) => {
            this.filterTemplates(e.target.value, modal);
        });
        
        // Фильтр по категории
        const categoryFilter = modal.querySelector('.category-filter');
        categoryFilter.addEventListener('change', (e) => {
            this.filterTemplates(searchInput.value, modal, e.target.value);
        });
        
        // Табы
        modal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const tab = btn.dataset.tab;
                this.showTemplateTab(tab, modal);
            });
        });
    }
    
    renderTemplateGrid(templates = null) {
        if (!templates) {
            templates = Array.from(this.templates.values());
        }
        
        if (templates.length === 0) {
            return `
                <div class="template-empty">
                    <i class="bi bi-collection"></i>
                    <p>Шаблоны не найдены</p>
                </div>
            `;
        }
        
        return templates.map(template => `
            <div class="template-item" data-id="${template.id}" data-category="${template.category}">
                <div class="template-thumbnail">
                    <img src="${template.thumbnail}" alt="${template.name}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkZGRkZGIiBzdHJva2U9IiNFRUVFRUUiLz4KPC9zdmc+Cg=='">
                    <div class="template-overlay">
                        <button class="btn btn-sm btn-primary" onclick="templateManager.applyTemplate('${template.id}')">
                            <i class="bi bi-check"></i> Применить
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="templateManager.previewTemplate('${template.id}')">
                            <i class="bi bi-eye"></i> Просмотр
                        </button>
                    </div>
                </div>
                <div class="template-info">
                    <div class="template-name">${template.name}</div>
                    <div class="template-desc">${template.description}</div>
                    <div class="template-meta">
                        <span class="template-category">${this.categories.get(template.category)?.name || 'Другое'}</span>
                        <span class="template-author">${template.author}</span>
                    </div>
                    <div class="template-actions">
                        <button class="btn btn-sm btn-ghost" onclick="templateManager.toggleFavorite('${template.id}')" title="${this.favorites.has(template.id) ? 'Удалить из избранного' : 'Добавить в избранное'}">
                            <i class="bi ${this.favorites.has(template.id) ? 'bi-heart-fill' : 'bi-heart'}"></i>
                        </button>
                        ${template.isUserTemplate ? `
                            <button class="btn btn-sm btn-ghost" onclick="templateManager.deleteTemplate('${template.id}')" title="Удалить">
                                <i class="bi bi-trash"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    filterTemplates(searchTerm, modal, categoryFilter = '') {
        const grid = modal.querySelector('#templateGrid');
        const items = modal.querySelectorAll('.template-item');
        
        items.forEach(item => {
            const matchesSearch = item.querySelector('.template-name').textContent
                .toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.querySelector('.template-desc').textContent
                .toLowerCase().includes(searchTerm.toLowerCase());
            const matchesCategory = !categoryFilter || item.dataset.category === categoryFilter;
            
            item.style.display = matchesSearch && matchesCategory ? 'block' : 'none';
        });
    }
    
    showTemplateTab(tab, modal) {
        const grid = modal.querySelector('#templateGrid');
        let templates = [];
        
        switch (tab) {
            case 'favorites':
                templates = this.getFavoriteTemplates();
                break;
            case 'recent':
                templates = this.getRecentTemplates();
                break;
            case 'user':
                templates = Array.from(this.templates.values())
                    .filter(template => template.isUserTemplate);
                break;
            default:
                templates = Array.from(this.templates.values());
        }
        
        grid.innerHTML = this.renderTemplateGrid(templates);
    }
    
    saveCurrentAsTemplate() {
        const modal = document.createElement('div');
        modal.className = 'save-template-modal';
        modal.innerHTML = `
            <div class="save-template-content">
                <div class="save-template-header">
                    <h4>Сохранить как шаблон</h4>
                    <button class="close-btn" onclick="this.closest('.save-template-modal').remove()">×</button>
                </div>
                <div class="save-template-body">
                    <div class="form-group">
                        <label>Название шаблона:</label>
                        <input type="text" class="template-name-input" placeholder="Введите название">
                    </div>
                    <div class="form-group">
                        <label>Описание:</label>
                        <textarea class="template-desc-input" placeholder="Краткое описание шаблона"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Категория:</label>
                        <select class="template-category-input">
                            ${Array.from(this.categories.values()).map(cat => 
                                `<option value="${cat.id}">${cat.name}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>
                <div class="save-template-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.save-template-modal').remove()">Отмена</button>
                    <button class="btn btn-primary" onclick="templateManager.saveTemplateFromModal(this.closest('.save-template-modal'))">Сохранить</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    saveTemplateFromModal(modal) {
        const name = modal.querySelector('.template-name-input').value.trim();
        const description = modal.querySelector('.template-desc-input').value.trim();
        const category = modal.querySelector('.template-category-input').value;
        
        if (!name) {
            this.vb.showNotification('Введите название шаблона', 'warning');
            return;
        }
        
        const template = this.saveAsTemplate(name, description, category);
        if (template) {
            modal.remove();
            
            // Обновляем библиотеку шаблонов
            const templateModal = document.querySelector('.template-modal');
            if (templateModal) {
                const grid = templateModal.querySelector('#templateGrid');
                grid.innerHTML = this.renderTemplateGrid();
            }
        }
    }
    
    previewTemplate(templateId) {
        const template = this.getTemplate(templateId);
        if (!template) return;
        
        const modal = document.createElement('div');
        modal.className = 'template-preview-modal';
        modal.innerHTML = `
            <div class="template-preview-content">
                <div class="template-preview-header">
                    <h4>${template.name}</h4>
                    <button class="close-btn" onclick="this.closest('.template-preview-modal').remove()">×</button>
                </div>
                <div class="template-preview-body">
                    <div class="template-preview-info">
                        <p><strong>Описание:</strong> ${template.description}</p>
                        <p><strong>Категория:</strong> ${this.categories.get(template.category)?.name || 'Другое'}</p>
                        <p><strong>Автор:</strong> ${template.author}</p>
                        <p><strong>Версия:</strong> ${template.version}</p>
                    </div>
                    <div class="template-preview-content">
                        <h5>Предварительный просмотр:</h5>
                        <div class="preview-container">
                            ${template.content}
                        </div>
                    </div>
                </div>
                <div class="template-preview-footer">
                    <button class="btn btn-primary" onclick="templateManager.applyTemplate('${templateId}'); this.closest('.template-preview-modal').remove();">
                        <i class="bi bi-check"></i> Применить шаблон
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    // Статистика
    getTemplateStats() {
        const templates = Array.from(this.templates.values());
        
        return {
            total: templates.length,
            byCategory: Object.fromEntries(
                Array.from(this.categories.keys()).map(cat => [
                    cat,
                    templates.filter(t => t.category === cat).length
                ])
            ),
            favorites: this.favorites.size,
            userTemplates: templates.filter(t => t.isUserTemplate).length,
            mostUsed: this.getMostUsedTemplate()
        };
    }
    
    getMostUsedTemplate() {
        if (this.recentTemplates.length === 0) return null;
        
        const usageCount = {};
        this.recentTemplates.forEach(id => {
            usageCount[id] = (usageCount[id] || 0) + 1;
        });
        
        const mostUsed = Object.entries(usageCount)
            .sort(([,a], [,b]) => b - a)[0];
            
        return mostUsed ? this.getTemplate(mostUsed[0]) : null;
    }
}