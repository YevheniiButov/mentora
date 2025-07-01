/**
 * Live Editor для Visual Builder
 * Живое редактирование с автосохранением
 */

class LiveEditor {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.isDirty = false;
        this.autoSaveTimer = null;
        this.currentFile = null;
        this.lastSavedContent = null;
        this.saveInProgress = false;
        
        // Настройки автосохранения
        this.config = {
            autoSaveDelay: 3000, // 3 секунды
            maxAutoSaveAttempts: 3,
            showSaveIndicator: true,
            backupBeforeSave: true
        };
        
        // Состояние
        this.state = {
            isEditing: false,
            hasUnsavedChanges: false,
            lastSaveTime: null,
            saveHistory: [],
            errorCount: 0
        };
        
        // DOM элементы
        this.dom = {};
        
        // Инициализация
        this.init();
    }

    /**
     * Инициализация Live Editor
     */
    init() {
        this.createSaveIndicator();
        this.setupLiveEditing();
        this.setupAutoSave();
        this.setupEventListeners();
        
        console.info('⚡ Live Editor инициализирован');
    }

    /**
     * Создание индикатора сохранения
     */
    createSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'save-indicator';
        indicator.id = 'saveIndicator';
        indicator.innerHTML = `
            <div class="save-indicator-content">
                <div class="save-status">
                    <i class="bi bi-check-circle-fill save-success" style="display: none;"></i>
                    <i class="bi bi-arrow-clockwise save-loading" style="display: none;"></i>
                    <i class="bi bi-exclamation-circle-fill save-error" style="display: none;"></i>
                    <span class="save-text">Сохранено</span>
                </div>
                <div class="save-time" id="saveTime"></div>
            </div>
        `;
        
        document.body.appendChild(indicator);
        this.dom.saveIndicator = indicator;
    }

    /**
     * Настройка живого редактирования
     */
    setupLiveEditing() {
        // Отслеживаем изменения в contenteditable элементах
        document.addEventListener('input', this.handleInputChange.bind(this));
        
        // Отслеживаем изменения в форме
        document.addEventListener('change', this.handleFormChange.bind(this));
        
        // Отслеживаем изменения в drag & drop
        document.addEventListener('drop', this.handleDropChange.bind(this));
        
        // Отслеживаем изменения в коде
        document.addEventListener('keyup', this.handleKeyChange.bind(this));
        
        console.info('📝 Живое редактирование настроено');
    }

    /**
     * Обработка изменений в input
     */
    handleInputChange(event) {
        const target = event.target;
        
        // Проверяем, является ли элемент редактируемым
        if (this.isEditableElement(target)) {
            this.markAsDirty();
            this.scheduleAutoSave();
            this.updateSaveIndicator('editing');
        }
    }

    /**
     * Обработка изменений в форме
     */
    handleFormChange(event) {
        const target = event.target;
        
        if (target.matches('input, textarea, select')) {
            this.markAsDirty();
            this.scheduleAutoSave();
            this.updateSaveIndicator('editing');
        }
    }

    /**
     * Обработка изменений при drop
     */
    handleDropChange(event) {
        if (event.target.closest('.draggable-element') || event.target.closest('.canvas')) {
            this.markAsDirty();
            this.scheduleAutoSave();
            this.updateSaveIndicator('editing');
        }
    }

    /**
     * Обработка изменений при нажатии клавиш
     */
    handleKeyChange(event) {
        const target = event.target;
        
        // Проверяем, является ли элемент редактируемым
        if (this.isEditableElement(target) || target.matches('.code-editor')) {
            this.markAsDirty();
            this.scheduleAutoSave();
            this.updateSaveIndicator('editing');
        }
    }

    /**
     * Проверка, является ли элемент редактируемым
     */
    isEditableElement(element) {
        return element.hasAttribute('contenteditable') || 
               element.classList.contains('editable-element') ||
               element.closest('.draggable-element') ||
               element.matches('input, textarea, select');
    }

    /**
     * Настройка автосохранения
     */
    setupAutoSave() {
        // Автосохранение каждые 30 секунд
        setInterval(() => {
            if (this.state.hasUnsavedChanges && !this.saveInProgress) {
                this.autoSave();
            }
        }, 30000);
        
        console.info('💾 Автосохранение настроено');
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Сохранение при закрытии страницы
        window.addEventListener('beforeunload', (event) => {
            if (this.state.hasUnsavedChanges) {
                event.preventDefault();
                event.returnValue = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?';
                return event.returnValue;
            }
        });

        // Сохранение при потере фокуса
        document.addEventListener('blur', () => {
            if (this.state.hasUnsavedChanges) {
                this.scheduleAutoSave();
            }
        }, true);

        // Горячие клавиши
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key.toLowerCase()) {
                    case 's':
                        event.preventDefault();
                        this.saveFile();
                        break;
                    case 'shift':
                        if (event.key === 'S') {
                            event.preventDefault();
                            this.saveFileAs();
                        }
                        break;
                }
            }
        });
    }

    /**
     * Отметка как измененный
     */
    markAsDirty() {
        this.isDirty = true;
        this.state.hasUnsavedChanges = true;
        this.updateSaveIndicator('dirty');
    }

    /**
     * Планирование автосохранения
     */
    scheduleAutoSave() {
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
        }
        
        this.autoSaveTimer = setTimeout(() => {
            this.autoSave();
        }, this.config.autoSaveDelay);
    }

    /**
     * Автосохранение
     */
    async autoSave() {
        if (this.saveInProgress || !this.state.hasUnsavedChanges) {
            return;
        }
        
        try {
            this.saveInProgress = true;
            this.updateSaveIndicator('saving');
            
            await this.saveFile(true); // true = автосохранение
            
            this.state.errorCount = 0;
            this.updateSaveIndicator('saved');
            
        } catch (error) {
            console.error('Ошибка автосохранения:', error);
            this.state.errorCount++;
            
            if (this.state.errorCount >= this.config.maxAutoSaveAttempts) {
                this.updateSaveIndicator('error');
                this.visualBuilder.showNotification('Ошибка автосохранения. Попробуйте сохранить вручную.', 'error');
            } else {
                this.updateSaveIndicator('retry');
                // Повторная попытка через 5 секунд
                setTimeout(() => this.autoSave(), 5000);
            }
        } finally {
            this.saveInProgress = false;
        }
    }

    /**
     * Сохранение файла
     */
    async saveFile(isAutoSave = false) {
        if (!this.currentFile) {
            throw new Error('Файл не выбран');
        }
        
        try {
            this.saveInProgress = true;
            this.updateSaveIndicator('saving');
            
            // Генерируем HTML контент
            const content = this.generateHTMLFromEditor();
            
            // Создаем резервную копию
            if (this.config.backupBeforeSave && this.lastSavedContent) {
                await this.createBackup();
            }
            
            // Отправляем на сервер
            const response = await fetch('/api/visual-builder/files/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                },
                body: JSON.stringify({
                    filepath: this.currentFile,
                    content: content,
                    isAutoSave: isAutoSave,
                    timestamp: Date.now()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.lastSavedContent = content;
                this.isDirty = false;
                this.state.hasUnsavedChanges = false;
                this.state.lastSaveTime = new Date();
                
                // Добавляем в историю сохранений
                this.addToSaveHistory({
                    timestamp: Date.now(),
                    filepath: this.currentFile,
                    isAutoSave: isAutoSave,
                    success: true
                });
                
                this.updateSaveIndicator('saved');
                
                if (!isAutoSave) {
                    this.visualBuilder.showNotification('Файл сохранен успешно', 'success');
                }
                
                console.info(`✅ Файл "${this.currentFile}" сохранен`);
                return data;
            } else {
                throw new Error(data.error || 'Ошибка сохранения файла');
            }
            
        } catch (error) {
            console.error('Ошибка сохранения файла:', error);
            this.updateSaveIndicator('error');
            this.visualBuilder.showNotification('Ошибка сохранения файла', 'error');
            throw error;
        } finally {
            this.saveInProgress = false;
        }
    }

    /**
     * Сохранение файла как
     */
    async saveFileAs() {
        const newPath = prompt('Введите новый путь к файлу:', this.currentFile);
        if (!newPath) return;
        
        const originalPath = this.currentFile;
        this.currentFile = newPath;
        
        try {
            await this.saveFile();
            this.visualBuilder.showNotification(`Файл сохранен как "${newPath}"`, 'success');
        } catch (error) {
            this.currentFile = originalPath;
            throw error;
        }
    }

    /**
     * Генерация HTML из редактора
     */
    generateHTMLFromEditor() {
        // Проверяем, какой режим активен
        if (this.visualBuilder.visualEditor && this.visualBuilder.visualEditor.state.mode === 'code') {
            // Режим кода - берем содержимое code editor
            return this.visualBuilder.visualEditor.dom.codeEditor.value;
        } else if (this.visualBuilder.visualEditor && this.visualBuilder.visualEditor.state.mode === 'split') {
            // Режим split - берем содержимое split code editor
            return this.visualBuilder.visualEditor.dom.splitCodeEditor.value;
        } else {
            // Визуальный режим - экспортируем canvas
            return this.visualBuilder.exportCanvasToHTML();
        }
    }

    /**
     * Создание резервной копии
     */
    async createBackup() {
        try {
            const backupPath = this.currentFile.replace('.html', `.backup.${Date.now()}.html`);
            
            const response = await fetch('/api/visual-builder/files/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                },
                body: JSON.stringify({
                    filepath: backupPath,
                    content: this.lastSavedContent,
                    isBackup: true
                })
            });
            
            if (response.ok) {
                console.info(`💾 Резервная копия создана: ${backupPath}`);
            }
        } catch (error) {
            console.warn('Не удалось создать резервную копию:', error);
        }
    }

    /**
     * Добавление в историю сохранений
     */
    addToSaveHistory(saveInfo) {
        this.state.saveHistory.push(saveInfo);
        
        // Ограничиваем историю
        if (this.state.saveHistory.length > 50) {
            this.state.saveHistory.shift();
        }
    }

    /**
     * Обновление индикатора сохранения
     */
    updateSaveIndicator(status) {
        if (!this.dom.saveIndicator) return;
        
        const indicator = this.dom.saveIndicator;
        const successIcon = indicator.querySelector('.save-success');
        const loadingIcon = indicator.querySelector('.save-loading');
        const errorIcon = indicator.querySelector('.save-error');
        const saveText = indicator.querySelector('.save-text');
        const saveTime = indicator.querySelector('#saveTime');
        
        // Скрываем все иконки
        successIcon.style.display = 'none';
        loadingIcon.style.display = 'none';
        errorIcon.style.display = 'none';
        
        // Убираем все классы
        indicator.className = 'save-indicator';
        
        switch (status) {
            case 'saved':
                successIcon.style.display = 'inline';
                saveText.textContent = 'Сохранено';
                indicator.classList.add('saved');
                if (this.state.lastSaveTime) {
                    saveTime.textContent = this.state.lastSaveTime.toLocaleTimeString();
                }
                break;
                
            case 'saving':
                loadingIcon.style.display = 'inline';
                saveText.textContent = 'Сохранение...';
                indicator.classList.add('saving');
                saveTime.textContent = '';
                break;
                
            case 'dirty':
                saveText.textContent = 'Не сохранено';
                indicator.classList.add('dirty');
                saveTime.textContent = '';
                break;
                
            case 'editing':
                saveText.textContent = 'Редактирование...';
                indicator.classList.add('editing');
                saveTime.textContent = '';
                break;
                
            case 'error':
                errorIcon.style.display = 'inline';
                saveText.textContent = 'Ошибка сохранения';
                indicator.classList.add('error');
                saveTime.textContent = '';
                break;
                
            case 'retry':
                loadingIcon.style.display = 'inline';
                saveText.textContent = 'Повторная попытка...';
                indicator.classList.add('retry');
                saveTime.textContent = '';
                break;
        }
        
        // Показываем индикатор
        indicator.style.display = 'block';
        
        // Скрываем через 3 секунды для успешного сохранения
        if (status === 'saved') {
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }

    /**
     * Установка текущего файла
     */
    setCurrentFile(filePath) {
        this.currentFile = filePath;
        this.lastSavedContent = null;
        this.isDirty = false;
        this.state.hasUnsavedChanges = false;
        this.state.errorCount = 0;
        
        console.info(`📁 Текущий файл: ${filePath}`);
    }

    /**
     * Проверка несохраненных изменений
     */
    hasUnsavedChanges() {
        return this.state.hasUnsavedChanges;
    }

    /**
     * Получение статистики сохранений
     */
    getSaveStats() {
        return {
            totalSaves: this.state.saveHistory.length,
            lastSaveTime: this.state.lastSaveTime,
            errorCount: this.state.errorCount,
            isDirty: this.isDirty,
            currentFile: this.currentFile
        };
    }

    /**
     * Очистка состояния
     */
    clear() {
        this.currentFile = null;
        this.lastSavedContent = null;
        this.isDirty = false;
        this.state.hasUnsavedChanges = false;
        this.state.errorCount = 0;
        this.state.saveHistory = [];
        
        if (this.autoSaveTimer) {
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = null;
        }
        
        this.updateSaveIndicator('saved');
    }

    /**
     * Принудительное сохранение
     */
    forceSave() {
        if (this.state.hasUnsavedChanges) {
            return this.saveFile();
        }
        return Promise.resolve();
    }
}

// Глобальные функции для обратной совместимости
let liveEditor;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        liveEditor = new LiveEditor(window.visualBuilder);
        window.liveEditor = liveEditor;
        console.info('⚡ Live Editor готов к использованию');
    }
}); 