/**
 * Component Library для Visual Builder
 * Библиотека базовых компонентов с drag & drop
 */

class ComponentLibrary {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.components = {};
        this.categories = {};
        this.searchTerm = '';
        this.selectedCategory = 'all';
        
        // Инициализация
        this.init();
    }

    /**
     * Инициализация библиотеки компонентов
     */
    init() {
        this.defineBasicComponents();
        this.defineCategories();
        this.setupEventListeners();
        
        console.info('📚 Component Library инициализирована');
    }

    /**
     * Определение базовых компонентов
     */
    defineBasicComponents() {
        this.components = {
            // Текстовые компоненты
            text: {
                name: 'Текстовый блок',
                category: 'text',
                icon: 'bi-text-paragraph',
                description: 'Обычный текст с форматированием',
                template: '<p class="editable-text" contenteditable="true">Введите текст здесь...</p>',
                defaultStyles: {
                    fontSize: '16px',
                    lineHeight: '1.6',
                    color: '#333333',
                    margin: '1rem 0'
                }
            },
            
            heading: {
                name: 'Заголовок',
                category: 'text',
                icon: 'bi-type-h1',
                description: 'Заголовки H1-H6',
                template: '<h2 class="editable-heading" contenteditable="true">Заголовок</h2>',
                defaultStyles: {
                    fontSize: '2rem',
                    fontWeight: '600',
                    color: '#1a1a1a',
                    margin: '1.5rem 0 1rem 0'
                }
            },
            
            paragraph: {
                name: 'Параграф',
                category: 'text',
                icon: 'bi-text-paragraph',
                description: 'Параграф текста',
                template: '<p class="editable-paragraph" contenteditable="true">Введите текст параграфа здесь...</p>',
                defaultStyles: {
                    fontSize: '16px',
                    lineHeight: '1.7',
                    color: '#4a4a4a',
                    margin: '1rem 0'
                }
            },
            
            list: {
                name: 'Список',
                category: 'text',
                icon: 'bi-list-ul',
                description: 'Маркированный или нумерованный список',
                template: `
                    <ul class="editable-list">
                        <li contenteditable="true">Элемент списка 1</li>
                        <li contenteditable="true">Элемент списка 2</li>
                        <li contenteditable="true">Элемент списка 3</li>
                    </ul>
                `,
                defaultStyles: {
                    fontSize: '16px',
                    lineHeight: '1.6',
                    margin: '1rem 0',
                    paddingLeft: '1.5rem'
                }
            },

            // Медиа компоненты
            image: {
                name: 'Изображение',
                category: 'media',
                icon: 'bi-image',
                description: 'Загрузка и отображение изображений',
                template: `
                    <div class="editable-image-container">
                        <img class="editable-image" src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDIwMCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik02MCA3NUgxNDBNNzUgNjBWOTAiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+" alt="Placeholder" style="max-width: 100%; height: auto; border-radius: 8px; cursor: pointer;" onclick="componentLibrary.selectImage(this)">
                        <div class="image-placeholder-text">Нажмите для загрузки изображения</div>
                    </div>
                `,
                defaultStyles: {
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '8px',
                    margin: '1rem 0'
                }
            },
            
            video: {
                name: 'Видео',
                category: 'media',
                icon: 'bi-play-circle',
                description: 'Встраивание видео контента',
                template: `
                    <div class="editable-video-container">
                        <div class="video-placeholder" onclick="componentLibrary.selectVideo(this)">
                            <i class="bi bi-play-circle" style="font-size: 3rem; color: #666;"></i>
                            <p>Нажмите для добавления видео</p>
                        </div>
                    </div>
                `,
                defaultStyles: {
                    width: '100%',
                    maxWidth: '600px',
                    margin: '1rem 0'
                }
            },
            
            audio: {
                name: 'Аудио',
                category: 'media',
                icon: 'bi-music-note',
                description: 'Аудио плеер',
                template: `
                    <div class="editable-audio-container">
                        <audio controls class="editable-audio">
                            <source src="" type="audio/mpeg">
                            Ваш браузер не поддерживает аудио.
                        </audio>
                    </div>
                `,
                defaultStyles: {
                    width: '100%',
                    maxWidth: '400px',
                    margin: '1rem 0'
                }
            },

            // Интерактивные компоненты
            button: {
                name: 'Кнопка',
                category: 'interactive',
                icon: 'bi-box-arrow-up-right',
                description: 'Интерактивная кнопка',
                template: '<button class="editable-button" contenteditable="true">Кнопка</button>',
                defaultStyles: {
                    padding: '12px 24px',
                    backgroundColor: '#3ECDC1',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: '500',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                }
            },
            
            link: {
                name: 'Ссылка',
                category: 'interactive',
                icon: 'bi-link-45deg',
                description: 'Гиперссылка',
                template: '<a href="#" class="editable-link" contenteditable="true">Ссылка</a>',
                defaultStyles: {
                    color: '#3ECDC1',
                    textDecoration: 'underline',
                    fontSize: '16px',
                    cursor: 'pointer'
                }
            },
            
            form: {
                name: 'Форма',
                category: 'interactive',
                icon: 'bi-input-cursor-text',
                description: 'Форма обратной связи',
                template: `
                    <form class="editable-form">
                        <div class="form-group">
                            <label>Имя:</label>
                            <input type="text" placeholder="Введите ваше имя">
                        </div>
                        <div class="form-group">
                            <label>Email:</label>
                            <input type="email" placeholder="your@email.com">
                        </div>
                        <div class="form-group">
                            <label>Сообщение:</label>
                            <textarea placeholder="Введите ваше сообщение" rows="4"></textarea>
                        </div>
                        <button type="submit">Отправить</button>
                    </form>
                `,
                defaultStyles: {
                    maxWidth: '500px',
                    margin: '1rem 0',
                    padding: '1rem'
                }
            },

            // Контейнеры
            container: {
                name: 'Контейнер',
                category: 'layout',
                icon: 'bi-box',
                description: 'Контейнер для группировки элементов',
                template: '<div class="editable-container"><!-- Перетащите элементы сюда --></div>',
                defaultStyles: {
                    padding: '1rem',
                    border: '2px dashed #ddd',
                    borderRadius: '8px',
                    minHeight: '100px',
                    backgroundColor: '#f8f9fa'
                }
            },
            
            section: {
                name: 'Секция',
                category: 'layout',
                icon: 'bi-layers',
                description: 'Секция страницы',
                template: '<section class="editable-section"><!-- Содержимое секции --></section>',
                defaultStyles: {
                    padding: '2rem 0',
                    margin: '1rem 0',
                    backgroundColor: 'transparent'
                }
            },
            
            grid: {
                name: 'Сетка',
                category: 'layout',
                icon: 'bi-grid-3x3-gap',
                description: 'CSS Grid контейнер',
                template: `
                    <div class="editable-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                        <div class="grid-item">Элемент 1</div>
                        <div class="grid-item">Элемент 2</div>
                        <div class="grid-item">Элемент 3</div>
                    </div>
                `,
                defaultStyles: {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '1rem',
                    margin: '1rem 0'
                }
            },

            // Специальные компоненты для Dental Academy
            dentalChart: {
                name: 'Зубная карта',
                category: 'dental',
                icon: 'bi-tooth',
                description: 'Интерактивная зубная карта',
                template: `
                    <div class="editable-dental-chart">
                        <h3>Зубная карта</h3>
                        <div class="dental-chart-container">
                            <!-- Зубная карта будет добавлена динамически -->
                        </div>
                    </div>
                `,
                defaultStyles: {
                    padding: '1rem',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    backgroundColor: 'white'
                }
            },
            
            quiz: {
                name: 'Тест',
                category: 'dental',
                icon: 'bi-question-circle',
                description: 'Интерактивный тест',
                template: `
                    <div class="editable-quiz">
                        <h3 contenteditable="true">Вопрос теста</h3>
                        <div class="quiz-options">
                            <label><input type="radio" name="quiz"> <span contenteditable="true">Вариант 1</span></label>
                            <label><input type="radio" name="quiz"> <span contenteditable="true">Вариант 2</span></label>
                            <label><input type="radio" name="quiz"> <span contenteditable="true">Вариант 3</span></label>
                        </div>
                    </div>
                `,
                defaultStyles: {
                    padding: '1rem',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa'
                }
            },
            
            caseStudy: {
                name: 'Клинический случай',
                category: 'dental',
                icon: 'bi-file-earmark-text',
                description: 'Описание клинического случая',
                template: `
                    <div class="editable-case-study">
                        <h3 contenteditable="true">Клинический случай</h3>
                        <div class="case-content" contenteditable="true">
                            <p>Описание случая...</p>
                            <h4>Диагноз:</h4>
                            <p>Диагноз пациента...</p>
                            <h4>Лечение:</h4>
                            <p>План лечения...</p>
                        </div>
                    </div>
                `,
                defaultStyles: {
                    padding: '1.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    backgroundColor: 'white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }
            }
        };
    }

    /**
     * Определение категорий компонентов
     */
    defineCategories() {
        this.categories = {
            all: {
                name: 'Все компоненты',
                icon: 'bi-collection',
                color: '#6c757d'
            },
            text: {
                name: 'Текст',
                icon: 'bi-text-paragraph',
                color: '#3ECDC1'
            },
            media: {
                name: 'Медиа',
                icon: 'bi-image',
                color: '#6C5CE7'
            },
            interactive: {
                name: 'Интерактивные',
                icon: 'bi-cursor',
                color: '#FDCB6E'
            },
            layout: {
                name: 'Макет',
                icon: 'bi-grid-3x3-gap',
                color: '#00D68F'
            },
            dental: {
                name: 'Стоматология',
                icon: 'bi-tooth',
                color: '#FF7675'
            }
        };
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Поиск компонентов
        const searchInput = document.getElementById('componentSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.toLowerCase();
                this.filterComponents();
            });
        }

        // Фильтр по категориям
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.selectedCategory = e.target.value;
                this.filterComponents();
            });
        }
    }

    /**
     * Фильтрация компонентов
     */
    filterComponents() {
        const componentGrid = document.getElementById('componentGrid');
        if (!componentGrid) return;

        const filteredComponents = Object.entries(this.components).filter(([key, component]) => {
            const matchesSearch = component.name.toLowerCase().includes(this.searchTerm) ||
                                component.description.toLowerCase().includes(this.searchTerm);
            const matchesCategory = this.selectedCategory === 'all' || component.category === this.selectedCategory;
            
            return matchesSearch && matchesCategory;
        });

        this.renderComponentGrid(filteredComponents);
    }

    /**
     * Рендеринг сетки компонентов
     */
    renderComponentGrid(components = null) {
        const componentGrid = document.getElementById('componentGrid');
        if (!componentGrid) return;

        const componentsToRender = components || Object.entries(this.components);
        
        componentGrid.innerHTML = componentsToRender.map(([key, component]) => `
            <div class="component-item" 
                 draggable="true" 
                 data-component-key="${key}"
                 data-component-type="${component.category}">
                <div class="component-icon" style="background: ${this.categories[component.category]?.color || '#6c757d'}">
                    <i class="${component.icon}"></i>
                </div>
                <div class="component-info">
                    <h4>${component.name}</h4>
                    <p>${component.description}</p>
                </div>
                <div class="component-actions">
                    <button class="btn btn-sm btn-primary" onclick="componentLibrary.addComponent('${key}')">
                        <i class="bi bi-plus"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // Настройка drag & drop для компонентов
        this.setupDragAndDrop();
    }

    /**
     * Настройка drag & drop
     */
    setupDragAndDrop() {
        const componentItems = document.querySelectorAll('.component-item');
        
        componentItems.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', item.dataset.componentKey);
                e.dataTransfer.effectAllowed = 'copy';
                item.classList.add('dragging');
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
            });
        });

        // Настройка drop zone на canvas
        const canvas = document.getElementById('canvas');
        if (canvas) {
            canvas.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'copy';
                canvas.classList.add('drag-over');
            });

            canvas.addEventListener('dragleave', (e) => {
                if (!canvas.contains(e.relatedTarget)) {
                    canvas.classList.remove('drag-over');
                }
            });

            canvas.addEventListener('drop', (e) => {
                e.preventDefault();
                canvas.classList.remove('drag-over');
                
                const componentKey = e.dataTransfer.getData('text/plain');
                if (componentKey) {
                    this.addComponentToCanvas(componentKey, e.clientX, e.clientY);
                }
            });
        }
    }

    /**
     * Добавление компонента на canvas
     */
    addComponentToCanvas(componentKey, x, y) {
        const component = this.components[componentKey];
        if (!component) return;

        // Создаем элемент
        const element = document.createElement('div');
        element.className = 'draggable-element';
        element.dataset.componentType = componentKey;
        element.dataset.componentId = `component_${Date.now()}`;
        
        // Добавляем содержимое
        element.innerHTML = component.template;
        
        // Применяем стили
        Object.assign(element.style, component.defaultStyles);
        
        // Позиционируем относительно canvas
        const canvas = document.getElementById('canvas');
        if (canvas) {
            const canvasRect = canvas.getBoundingClientRect();
            const relativeX = x - canvasRect.left;
            const relativeY = y - canvasRect.top;
            
            element.style.position = 'absolute';
            element.style.left = `${relativeX}px`;
            element.style.top = `${relativeY}px`;
            
            canvas.appendChild(element);
        }

        // Настраиваем обработчики для нового элемента
        this.setupElementHandlers(element);
        
        // Уведомляем Visual Builder
        if (this.visualBuilder) {
            this.visualBuilder.addToHistory();
            this.visualBuilder.updateLayersPanel();
        }

        console.info(`✅ Компонент "${component.name}" добавлен на canvas`);
    }

    /**
     * Настройка обработчиков для элемента
     */
    setupElementHandlers(element) {
        // Клик для выделения
        element.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectElement(element);
        });

        // Двойной клик для редактирования
        element.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            this.editElement(element);
        });

        // Обработка изменений в contenteditable
        const editableElements = element.querySelectorAll('[contenteditable="true"]');
        editableElements.forEach(editable => {
            editable.addEventListener('input', () => {
                if (this.visualBuilder) {
                    this.visualBuilder.addToHistory();
                }
            });
        });
    }

    /**
     * Выделение элемента
     */
    selectElement(element) {
        // Снимаем выделение со всех элементов
        document.querySelectorAll('.draggable-element').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Выделяем текущий элемент
        element.classList.add('selected');
        
        // Уведомляем Visual Builder
        if (this.visualBuilder) {
            this.visualBuilder.state.selectedElement = element;
            this.visualBuilder.updatePropertiesPanel();
        }
    }

    /**
     * Редактирование элемента
     */
    editElement(element) {
        const editableElement = element.querySelector('[contenteditable="true"]');
        if (editableElement) {
            editableElement.focus();
            
            // Выделяем весь текст
            const range = document.createRange();
            range.selectNodeContents(editableElement);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }

    /**
     * Добавление компонента (программно)
     */
    addComponent(componentKey) {
        const canvas = document.getElementById('canvas');
        if (!canvas) return;

        // Добавляем в центр canvas
        const canvasRect = canvas.getBoundingClientRect();
        const centerX = canvasRect.width / 2;
        const centerY = canvasRect.height / 2;
        
        this.addComponentToCanvas(componentKey, centerX, centerY);
    }

    /**
     * Выбор изображения
     */
    selectImage(imgElement) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imgElement.src = e.target.result;
                    imgElement.alt = file.name;
                    
                    // Убираем placeholder текст
                    const placeholderText = imgElement.parentElement.querySelector('.image-placeholder-text');
                    if (placeholderText) {
                        placeholderText.style.display = 'none';
                    }
                    
                    if (this.visualBuilder) {
                        this.visualBuilder.addToHistory();
                    }
                };
                reader.readAsDataURL(file);
            }
        };
        
        input.click();
    }

    /**
     * Выбор видео
     */
    selectVideo(container) {
        const url = prompt('Введите URL видео (YouTube, Vimeo) или загрузите файл:');
        if (url) {
            if (url.includes('youtube.com') || url.includes('youtu.be')) {
                const videoId = this.extractYouTubeId(url);
                if (videoId) {
                    container.innerHTML = `
                        <iframe width="100%" height="315" 
                                src="https://www.youtube.com/embed/${videoId}" 
                                frameborder="0" allowfullscreen></iframe>
                    `;
                }
            } else if (url.includes('vimeo.com')) {
                const videoId = this.extractVimeoId(url);
                if (videoId) {
                    container.innerHTML = `
                        <iframe width="100%" height="315" 
                                src="https://player.vimeo.com/video/${videoId}" 
                                frameborder="0" allowfullscreen></iframe>
                    `;
                }
            } else {
                container.innerHTML = `
                    <video controls width="100%">
                        <source src="${url}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                `;
            }
            
            if (this.visualBuilder) {
                this.visualBuilder.addToHistory();
            }
        }
    }

    /**
     * Извлечение ID YouTube видео
     */
    extractYouTubeId(url) {
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
        const match = url.match(regExp);
        return (match && match[2].length === 11) ? match[2] : null;
    }

    /**
     * Извлечение ID Vimeo видео
     */
    extractVimeoId(url) {
        const regExp = /vimeo\.com\/([0-9]+)/;
        const match = url.match(regExp);
        return match ? match[1] : null;
    }

    /**
     * Получение компонента по ключу
     */
    getComponent(key) {
        return this.components[key];
    }

    /**
     * Получение всех компонентов
     */
    getAllComponents() {
        return this.components;
    }

    /**
     * Получение компонентов по категории
     */
    getComponentsByCategory(category) {
        return Object.entries(this.components).filter(([key, component]) => 
            component.category === category
        );
    }

    /**
     * Поиск компонентов
     */
    searchComponents(query) {
        const searchTerm = query.toLowerCase();
        return Object.entries(this.components).filter(([key, component]) => 
            component.name.toLowerCase().includes(searchTerm) ||
            component.description.toLowerCase().includes(searchTerm)
        );
    }
}

// Глобальный экземпляр
let componentLibrary;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        componentLibrary = new ComponentLibrary(window.visualBuilder);
        window.componentLibrary = componentLibrary;
        console.info('📚 Component Library готова к использованию');
    }
}); 