/**
 * Visual Builder Components
 * Управление компонентами и их шаблонами
 */

class ComponentManager {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.templates = new Map();
        this.customComponents = new Map();
        
        this.init();
    }

    async init() {
        await this.loadTemplates();
        this.setupComponentInteractions();
        console.info('🧩 Component Manager инициализирован');
    }

    /**
     * Загрузка всех шаблонов компонентов
     */
    async loadTemplates() {
        // Базовые компоненты
        this.templates.set('text', {
            name: 'Текст',
            category: 'basic',
            template: this.getTextTemplate(),
            icon: 'bi-type',
            description: 'Редактируемый текстовый блок'
        });

        this.templates.set('heading', {
            name: 'Заголовок', 
            category: 'basic',
            template: this.getHeadingTemplate(),
            icon: 'bi-type-h1',
            description: 'Заголовки H1-H6'
        });

        this.templates.set('image', {
            name: 'Изображение',
            category: 'media',
            template: this.getImageTemplate(),
            icon: 'bi-image',
            description: 'Загрузка и отображение изображений'
        });

        this.templates.set('button', {
            name: 'Кнопка',
            category: 'interactive',
            template: this.getButtonTemplate(),
            icon: 'bi-ui-radios',
            description: 'Интерактивная кнопка'
        });

        this.templates.set('video', {
            name: 'Видео',
            category: 'media',
            template: this.getVideoTemplate(),
            icon: 'bi-play-circle',
            description: 'Встраивание видео'
        });

        this.templates.set('quiz', {
            name: 'Тест',
            category: 'interactive',
            template: this.getQuizTemplate(),
            icon: 'bi-question-circle',
            description: 'Интерактивный тест'
        });

        this.templates.set('form', {
            name: 'Форма',
            category: 'interactive',
            template: this.getFormTemplate(),
            icon: 'bi-card-text',
            description: 'Форма обратной связи'
        });

        this.templates.set('dental-chart', {
            name: 'Зубная формула',
            category: 'medical',
            template: this.getDentalChartTemplate(),
            icon: 'bi-diagram-3',
            description: 'Интерактивная зубная формула'
        });

        this.templates.set('hero', {
            name: 'Hero секция',
            category: 'blocks',
            template: this.getHeroTemplate(),
            icon: 'bi-stars',
            description: 'Главный блок страницы'
        });

        // Загружаем пользовательские компоненты
        await this.loadCustomComponents();
    }

    /**
     * Загрузка пользовательских компонентов
     */
    async loadCustomComponents() {
        try {
            const response = await fetch(`${this.vb.config.apiEndpoint}/components`, {
                headers: {
                    'X-CSRFToken': this.vb.config.csrfToken
                }
            });
            
            if (response.ok) {
                const customComponents = await response.json();
                customComponents.forEach(component => {
                    this.customComponents.set(component.id, component);
                });
            }
        } catch (error) {
            console.warn('⚠️ Ошибка загрузки пользовательских компонентов:', error);
        }
    }

    /**
     * Настройка взаимодействий с компонентами
     */
    setupComponentInteractions() {
        // Обработчики для специальных компонентов
        document.addEventListener('click', (e) => {
            // Зубная формула
            if (e.target.closest('.tooth')) {
                this.handleToothClick(e.target.closest('.tooth'));
            }
            
            // Аккордеон
            if (e.target.closest('.accordion-header')) {
                this.handleAccordionClick(e.target.closest('.accordion-header'));
            }
            
            // Вкладки
            if (e.target.closest('.tab-button')) {
                this.handleTabClick(e.target.closest('.tab-button'));
            }
            
            // Флэшкарта
            if (e.target.closest('.flashcard-inner')) {
                this.handleFlashcardClick(e.target.closest('.flashcard-inner'));
            }
        });
    }

    /**
     * Обработчик клика по зубу
     */
    handleToothClick(tooth) {
        const states = ['healthy', 'caries', 'filled', 'missing'];
        const currentState = tooth.dataset.state || 'healthy';
        const currentIndex = states.indexOf(currentState);
        const nextIndex = (currentIndex + 1) % states.length;
        const nextState = states[nextIndex];
        
        tooth.dataset.state = nextState;
        tooth.className = `tooth ${nextState}`;
        
        // Добавляем в историю
        this.vb.addToHistory();
        this.vb.markAsChanged();
    }

    /**
     * Обработчик клика по аккордеону
     */
    handleAccordionClick(header) {
        const content = header.nextElementSibling;
        const icon = header.querySelector('.accordion-icon');
        const isOpen = content.classList.contains('active');
        
        if (isOpen) {
            content.classList.remove('active');
            if (icon) icon.textContent = '▼';
        } else {
            content.classList.add('active');
            if (icon) icon.textContent = '▲';
        }
    }

    /**
     * Обработчик клика по вкладке
     */
    handleTabClick(button) {
        const tabsContainer = button.closest('.component-tabs');
        const tabIndex = Array.from(button.parentNode.children).indexOf(button);
        
        // Убираем активность со всех кнопок и контента
        tabsContainer.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove('active'));
        tabsContainer.querySelectorAll('.tab-content').forEach(content => 
            content.classList.remove('active'));
        
        // Активируем выбранную вкладку
        button.classList.add('active');
        const targetContent = tabsContainer.querySelectorAll('.tab-content')[tabIndex];
        if (targetContent) {
            targetContent.classList.add('active');
        }
    }

    /**
     * Обработчик клика по флэшкарте
     */
    handleFlashcardClick(flashcard) {
        flashcard.classList.toggle('flipped');
    }

    /**
     * Получение шаблона компонента
     */
    getTemplate(type) {
        if (this.templates.has(type)) {
            return this.templates.get(type).template;
        }
        
        if (this.customComponents.has(type)) {
            return this.customComponents.get(type).template;
        }
        
        return this.templates.get('text').template;
    }

    /**
     * Шаблоны компонентов
     */
    getTextTemplate() {
        return `
            <div class="element-content">
                <div contenteditable="true" class="text-editor" data-placeholder="Введите текст...">
                    <p>Введите ваш текст здесь. Используйте <strong>жирный</strong>, <em>курсив</em> и другое форматирование.</p>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getHeadingTemplate() {
        return `
            <div class="element-content">
                <h2 contenteditable="true" class="heading-editor" data-placeholder="Заголовок...">
                    Заголовок страницы
                </h2>
                <div class="heading-controls">
                    <select onchange="this.parentNode.previousElementSibling.tagName = this.value.toUpperCase(); this.parentNode.previousElementSibling.className = 'heading-editor ' + this.value;">
                        <option value="h1">H1</option>
                        <option value="h2" selected>H2</option>
                        <option value="h3">H3</option>
                        <option value="h4">H4</option>
                        <option value="h5">H5</option>
                        <option value="h6">H6</option>
                    </select>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getImageTemplate() {
        return `
            <div class="element-content">
                <div class="image-container">
                    <div class="image-placeholder" onclick="visualBuilder.managers.media?.selectImage(this)">
                        <div class="placeholder-content">
                            <i class="bi bi-image placeholder-icon"></i>
                            <h4>Добавить изображение</h4>
                            <p>Нажмите для выбора файла или перетащите сюда</p>
                            <div class="supported-formats">
                                <span class="format-badge">JPG</span>
                                <span class="format-badge">PNG</span>
                                <span class="format-badge">GIF</span>
                                <span class="format-badge">WebP</span>
                            </div>
                            <small>Максимальный размер: 10MB</small>
                        </div>
                    </div>
                    <div class="image-options" style="display: none;">
                        <label>
                            <input type="text" placeholder="Alt текст" class="alt-text-input">
                        </label>
                        <label>
                            <input type="text" placeholder="Подпись" class="caption-input">
                        </label>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getButtonTemplate() {
        return `
            <div class="element-content">
                <div class="button-container">
                    <button class="custom-button btn-primary" contenteditable="true" data-placeholder="Текст кнопки...">
                        Нажмите меня
                    </button>
                    <div class="button-options">
                        <select class="button-style" onchange="this.parentNode.previousElementSibling.className = 'custom-button ' + this.value;">
                            <option value="btn-primary">Основная</option>
                            <option value="btn-secondary">Вторичная</option>
                            <option value="btn-success">Успех</option>
                            <option value="btn-warning">Предупреждение</option>
                            <option value="btn-danger">Опасность</option>
                            <option value="btn-outline-primary">Контурная</option>
                        </select>
                        <select class="button-size" onchange="this.parentNode.previousElementSibling.classList.toggle('btn-lg', this.value === 'large'); this.parentNode.previousElementSibling.classList.toggle('btn-sm', this.value === 'small');">
                            <option value="normal">Обычная</option>
                            <option value="small">Маленькая</option>
                            <option value="large">Большая</option>
                        </select>
                        <input type="text" placeholder="Ссылка (URL)" class="button-link">
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getVideoTemplate() {
        return `
            <div class="element-content">
                <div class="video-container">
                    <div class="video-placeholder" onclick="visualBuilder.managers.media?.selectVideo(this)">
                        <div class="placeholder-content">
                            <i class="bi bi-play-circle placeholder-icon"></i>
                            <h4>Добавить видео</h4>
                            <p>YouTube, Vimeo или загрузить файл</p>
                            <div class="video-options">
                                <button class="btn btn-secondary btn-sm" onclick="visualBuilder.managers.media?.addYouTube(this)">
                                    <i class="bi bi-youtube"></i> YouTube
                                </button>
                                <button class="btn btn-secondary btn-sm" onclick="visualBuilder.managers.media?.addVimeo(this)">
                                    <i class="bi bi-vimeo"></i> Vimeo
                                </button>
                                <button class="btn btn-secondary btn-sm" onclick="visualBuilder.managers.media?.uploadVideo(this)">
                                    <i class="bi bi-upload"></i> Загрузить
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getQuizTemplate() {
        return `
            <div class="element-content">
                <div class="quiz-container">
                    <h3 contenteditable="true" class="quiz-question" data-placeholder="Вопрос теста...">
                        Вопрос теста
                    </h3>
                    <div class="quiz-options">
                        <div class="quiz-option">
                            <label class="quiz-label">
                                <input type="radio" name="quiz_${Date.now()}" value="1">
                                <span contenteditable="true" data-placeholder="Вариант ответа...">Вариант ответа 1</span>
                                <button class="option-correct-btn" onclick="this.parentNode.parentNode.classList.toggle('correct')" title="Отметить как правильный">
                                    <i class="bi bi-check-circle"></i>
                                </button>
                                <button class="option-remove-btn" onclick="this.parentNode.parentNode.remove()" title="Удалить вариант">
                                    <i class="bi bi-x-circle"></i>
                                </button>
                            </label>
                        </div>
                        <div class="quiz-option">
                            <label class="quiz-label">
                                <input type="radio" name="quiz_${Date.now()}" value="2">
                                <span contenteditable="true" data-placeholder="Вариант ответа...">Вариант ответа 2</span>
                                <button class="option-correct-btn" onclick="this.parentNode.parentNode.classList.toggle('correct')" title="Отметить как правильный">
                                    <i class="bi bi-check-circle"></i>
                                </button>
                                <button class="option-remove-btn" onclick="this.parentNode.parentNode.remove()" title="Удалить вариант">
                                    <i class="bi bi-x-circle"></i>
                                </button>
                            </label>
                        </div>
                    </div>
                    <div class="quiz-controls">
                        <button class="btn btn-secondary btn-sm" onclick="visualBuilder.addQuizOption(this)">
                            <i class="bi bi-plus"></i> Добавить вариант
                        </button>
                        <label class="quiz-setting">
                            <input type="checkbox"> Множественный выбор
                        </label>
                        <label class="quiz-setting">
                            <input type="checkbox"> Обязательный вопрос
                        </label>
                    </div>
                    <div class="quiz-explanation" style="display: none;">
                        <label>Объяснение (показывается после ответа):</label>
                        <textarea contenteditable="true" placeholder="Объяснение правильного ответа..."></textarea>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getFormTemplate() {
        return `
            <div class="element-content">
                <div class="form-container">
                    <h3 contenteditable="true" data-placeholder="Заголовок формы...">Форма обратной связи</h3>
                    <form class="custom-form">
                        <div class="form-field">
                            <label contenteditable="true">Имя *</label>
                            <input type="text" placeholder="Введите ваше имя" required>
                        </div>
                        <div class="form-field">
                            <label contenteditable="true">Email *</label>
                            <input type="email" placeholder="your@email.com" required>
                        </div>
                        <div class="form-field">
                            <label contenteditable="true">Сообщение</label>
                            <textarea placeholder="Введите ваше сообщение" rows="4"></textarea>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary">Отправить</button>
                            <button type="reset" class="btn btn-secondary">Очистить</button>
                        </div>
                    </form>
                    <div class="form-builder">
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'text')">
                            <i class="bi bi-input-cursor-text"></i> Текст
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'email')">
                            <i class="bi bi-envelope"></i> Email
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'textarea')">
                            <i class="bi bi-textarea"></i> Область текста
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'select')">
                            <i class="bi bi-menu-button-wide"></i> Выпадающий список
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'checkbox')">
                            <i class="bi bi-check-square"></i> Чекбокс
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualBuilder.addFormField(this, 'radio')">
                            <i class="bi bi-radioactive"></i> Радио кнопки
                        </button>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getDentalChartTemplate() {
        return `
            <div class="element-content">
                <div class="dental-chart-container">
                    <h3 contenteditable="true" data-placeholder="Заголовок...">Зубная формула пациента</h3>
                    <div class="dental-chart">
                        <div class="chart-info">
                            <div class="patient-info">
                                <input type="text" placeholder="Имя пациента" class="patient-name">
                                <input type="date" class="visit-date">
                            </div>
                        </div>
                        <div class="teeth-container">
                            <div class="teeth-row upper-jaw">
                                <div class="jaw-label">Верхняя челюсть</div>
                                <div class="teeth-grid">
                                    ${Array.from({length: 16}, (_, i) => `
                                        <div class="tooth healthy" data-number="${18 - i}" data-state="healthy" title="Зуб ${18 - i}">
                                            <span class="tooth-number">${18 - i}</span>
                                            <div class="tooth-surface" data-surface="occlusal"></div>
                                            <div class="tooth-surface" data-surface="buccal"></div>
                                            <div class="tooth-surface" data-surface="lingual"></div>
                                            <div class="tooth-surface" data-surface="mesial"></div>
                                            <div class="tooth-surface" data-surface="distal"></div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="teeth-row lower-jaw">
                                <div class="jaw-label">Нижняя челюсть</div>
                                <div class="teeth-grid">
                                    ${Array.from({length: 16}, (_, i) => `
                                        <div class="tooth healthy" data-number="${i + 31}" data-state="healthy" title="Зуб ${i + 31}">
                                            <span class="tooth-number">${i + 31}</span>
                                            <div class="tooth-surface" data-surface="occlusal"></div>
                                            <div class="tooth-surface" data-surface="buccal"></div>
                                            <div class="tooth-surface" data-surface="lingual"></div>
                                            <div class="tooth-surface" data-surface="mesial"></div>
                                            <div class="tooth-surface" data-surface="distal"></div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        <div class="chart-tools">
                            <div class="tool-group">
                                <h4>Состояние зуба:</h4>
                                <button class="tool-btn active" data-state="healthy" title="Здоровый зуб">
                                    <div class="tool-color healthy"></div>
                                    Здоровый
                                </button>
                                <button class="tool-btn" data-state="caries" title="Кариес">
                                    <div class="tool-color caries"></div>
                                    Кариес
                                </button>
                                <button class="tool-btn" data-state="filled" title="Пломба">
                                    <div class="tool-color filled"></div>
                                    Пломба
                                </button>
                                <button class="tool-btn" data-state="crown" title="Коронка">
                                    <div class="tool-color crown"></div>
                                    Коронка
                                </button>
                                <button class="tool-btn" data-state="missing" title="Отсутствует">
                                    <div class="tool-color missing"></div>
                                    Отсутствует
                                </button>
                                <button class="tool-btn" data-state="implant" title="Имплант">
                                    <div class="tool-color implant"></div>
                                    Имплант
                                </button>
                            </div>
                            <div class="tool-group">
                                <button class="btn btn-sm btn-secondary" onclick="visualBuilder.clearDentalChart(this)">
                                    <i class="bi bi-arrow-clockwise"></i> Сбросить
                                </button>
                                <button class="btn btn-sm btn-primary" onclick="visualBuilder.generateDentalReport(this)">
                                    <i class="bi bi-file-earmark-text"></i> Генерировать отчет
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    getHeroTemplate() {
        return `
            <div class="element-content">
                <div class="hero-section">
                    <div class="hero-background">
                        <div class="hero-overlay"></div>
                        <div class="hero-pattern"></div>
                    </div>
                    <div class="hero-content">
                        <div class="hero-badge">
                            <span contenteditable="true" data-placeholder="Бейдж...">🎓 Dental Academy</span>
                        </div>
                        <h1 class="hero-title" contenteditable="true" data-placeholder="Главный заголовок...">
                            Изучайте стоматологию с профессионалами
                        </h1>
                        <p class="hero-subtitle" contenteditable="true" data-placeholder="Подзаголовок...">
                            Получите качественное образование, практические навыки и сертификацию в области стоматологии с помощью наших интерактивных курсов и экспертного сопровождения.
                        </p>
                        <div class="hero-actions">
                            <button class="btn btn-primary btn-lg hero-cta">
                                <i class="bi bi-play-circle"></i>
                                <span contenteditable="true">Начать обучение</span>
                            </button>
                            <button class="btn btn-outline-light btn-lg hero-secondary">
                                <i class="bi bi-info-circle"></i>
                                <span contenteditable="true">Узнать больше</span>
                            </button>
                        </div>
                        <div class="hero-stats">
                            <div class="stat-item">
                                <div class="stat-number" contenteditable="true">1000+</div>
                                <div class="stat-label" contenteditable="true">Студентов</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number" contenteditable="true">50+</div>
                                <div class="stat-label" contenteditable="true">Курсов</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-number" contenteditable="true">98%</div>
                                <div class="stat-label" contenteditable="true">Успешности</div>
                            </div>
                        </div>
                    </div>
                    <div class="hero-media">
                        <div class="media-placeholder" onclick="visualBuilder.managers.media?.selectHeroMedia(this)">
                            <i class="bi bi-image"></i>
                            <span>Добавить изображение/видео</span>
                        </div>
                    </div>
                </div>
            </div>
            ${this.getControlsTemplate()}
        `;
    }

    /**
     * Шаблон элементов управления
     */
    getControlsTemplate() {
        return `
            <div class="element-controls">
                <div class="control-group">
                    <button class="control-btn" onclick="visualBuilder.moveElement(this, 'up')" title="Переместить вверх">
                        <i class="bi bi-arrow-up"></i>
                    </button>
                    <button class="control-btn" onclick="visualBuilder.moveElement(this, 'down')" title="Переместить вниз">
                        <i class="bi bi-arrow-down"></i>
                    </button>
                </div>
                <div class="control-group">
                    <button class="control-btn secondary" onclick="visualBuilder.duplicateElement(this)" title="Дублировать">
                        <i class="bi bi-files"></i>
                    </button>
                    <button class="control-btn warning" onclick="visualBuilder.editElement(this)" title="Редактировать">
                        <i class="bi bi-pencil"></i>
                    </button>
                </div>
                <div class="control-group">
                    <button class="control-btn" onclick="visualBuilder.toggleElementVisibility(this)" title="Скрыть/Показать">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="control-btn danger" onclick="visualBuilder.deleteElement(this)" title="Удалить">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Сохранение пользовательского компонента
     */
    async saveCustomComponent(element, name, description) {
        try {
            const template = element.outerHTML;
            const componentData = {
                name,
                description,
                template,
                category: 'custom',
                type: `custom_${Date.now()}`,
                userId: this.vb.config.currentUserId
            };

            const response = await fetch(`${this.vb.config.apiEndpoint}/components`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.vb.config.csrfToken
                },
                body: JSON.stringify(componentData)
            });

            if (response.ok) {
                const savedComponent = await response.json();
                this.customComponents.set(savedComponent.id, savedComponent);
                this.vb.showNotification('Компонент сохранен в библиотеку', 'success');
                return savedComponent;
            } else {
                throw new Error('Ошибка сохранения компонента');
            }
        } catch (error) {
            console.error('❌ Ошибка сохранения компонента:', error);
            this.vb.showNotification('Ошибка сохранения компонента', 'error');
        }
    }

    /**
     * Удаление пользовательского компонента
     */
    async deleteCustomComponent(componentId) {
        try {
            const response = await fetch(`${this.vb.config.apiEndpoint}/components/${componentId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.vb.config.csrfToken
                }
            });

            if (response.ok) {
                this.customComponents.delete(componentId);
                this.vb.showNotification('Компонент удален', 'success');
                return true;
            } else {
                throw new Error('Ошибка удаления компонента');
            }
        } catch (error) {
            console.error('❌ Ошибка удаления компонента:', error);
            this.vb.showNotification('Ошибка удаления компонента', 'error');
            return false;
        }
    }

    /**
     * Экспорт компонента
     */
    exportComponent(element) {
        const componentData = {
            type: element.dataset.type,
            content: element.innerHTML,
            styles: this.extractElementStyles(element),
            timestamp: Date.now()
        };

        const blob = new Blob([JSON.stringify(componentData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `component-${element.dataset.type}-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.vb.showNotification('Компонент экспортирован', 'success');
    }

    /**
     * Импорт компонента
     */
    async importComponent(file) {
        try {
            const text = await file.text();
            const componentData = JSON.parse(text);
            
            // Создаем элемент из импортированных данных
            const element = await this.vb.createElement(componentData.type);
            if (element && componentData.content) {
                element.innerHTML = componentData.content;
                
                // Применяем стили если есть
                if (componentData.styles) {
                    this.applyElementStyles(element, componentData.styles);
                }
                
                this.vb.setupElementEvents(element);
                this.vb.showNotification('Компонент импортирован', 'success');
            }
        } catch (error) {
            console.error('❌ Ошибка импорта компонента:', error);
            this.vb.showNotification('Ошибка импорта компонента', 'error');
        }
    }

    /**
     * Извлечение стилей элемента
     */
    extractElementStyles(element) {
        const computedStyles = window.getComputedStyle(element);
        const relevantStyles = [
            'width', 'height', 'margin', 'padding', 'background', 'border',
            'border-radius', 'box-shadow', 'transform', 'position', 'z-index'
        ];
        
        const styles = {};
        relevantStyles.forEach(property => {
            styles[property] = computedStyles.getPropertyValue(property);
        });
        
        return styles;
    }

    /**
     * Применение стилей к элементу
     */
    applyElementStyles(element, styles) {
        Object.entries(styles).forEach(([property, value]) => {
            if (value && value !== 'none' && value !== 'auto') {
                element.style.setProperty(property, value);
            }
        });
    }
}

// Дополнительные утилиты для работы с компонентами

/**
 * Утилиты для работы с зубной формулой
 */
class DentalChartUtils {
    static getToothByNumber(chart, number) {
        return chart.querySelector(`[data-number="${number}"]`);
    }

    static setToothState(tooth, state) {
        tooth.dataset.state = state;
        tooth.className = `tooth ${state}`;
    }

    static getChartData(chart) {
        const teeth = chart.querySelectorAll('.tooth');
        const data = {};
        
        teeth.forEach(tooth => {
            data[tooth.dataset.number] = tooth.dataset.state || 'healthy';
        });
        
        return data;
    }

    static generateReport(chart) {
        const data = this.getChartData(chart);
        const stats = this.calculateStats(data);
        
        return {
            patientName: chart.querySelector('.patient-name')?.value || 'Пациент',
            date: chart.querySelector('.visit-date')?.value || new Date().toISOString().split('T')[0],
            teethData: data,
            statistics: stats,
            recommendations: this.generateRecommendations(stats)
        };
    }

    static calculateStats(data) {
        const total = Object.keys(data).length;
        const states = {};
        
        Object.values(data).forEach(state => {
            states[state] = (states[state] || 0) + 1;
        });
        
        return {
            total,
            healthy: states.healthy || 0,
            caries: states.caries || 0,
            filled: states.filled || 0,
            missing: states.missing || 0,
            crown: states.crown || 0,
            implant: states.implant || 0,
            healthPercentage: Math.round(((states.healthy || 0) / total) * 100)
        };
    }

    static generateRecommendations(stats) {
        const recommendations = [];
        
        if (stats.caries > 0) {
            recommendations.push(`Необходимо лечение ${stats.caries} зубов с кариесом`);
        }
        
        if (stats.missing > 0) {
            recommendations.push(`Рекомендуется протезирование ${stats.missing} отсутствующих зубов`);
        }
        
        if (stats.healthPercentage < 70) {
            recommendations.push('Требуется комплексное лечение');
        } else if (stats.healthPercentage > 90) {
            recommendations.push('Отличное состояние полости рта');
        }
        
        recommendations.push('Регулярная профилактика каждые 6 месяцев');
        
        return recommendations;
    }
}

// Экспорт для глобального использования
window.ComponentManager = ComponentManager;
window.DentalChartUtils = DentalChartUtils;