/**
 * Keyboard Shortcuts Manager для Visual Builder
 * Система горячих клавиш с настройками и конфликтами
 */

class KeyboardShortcuts {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.isEnabled = true;
        this.isRecording = false;
        this.recordingCallback = null;
        
        // Стандартные горячие клавиши
        this.defaultShortcuts = {
            // Файловые операции
            'Ctrl+S': {
                action: () => this.visualBuilder.savePage(),
                description: 'Сохранить страницу',
                category: 'file',
                global: true
            },
            'Ctrl+O': {
                action: () => this.visualBuilder.loadHTMLFileFromBrowser(),
                description: 'Открыть HTML файл',
                category: 'file',
                global: true
            },
            'Ctrl+Shift+S': {
                action: () => this.visualBuilder.exportCanvasToHTML(),
                description: 'Экспорт в HTML',
                category: 'file',
                global: true
            },
            
            // История изменений
            'Ctrl+Z': {
                action: () => this.visualBuilder.undo(),
                description: 'Отменить действие',
                category: 'history',
                global: true
            },
            'Ctrl+Y': {
                action: () => this.visualBuilder.redo(),
                description: 'Повторить действие',
                category: 'history',
                global: true
            },
            'Ctrl+Shift+Z': {
                action: () => this.visualBuilder.redo(),
                description: 'Повторить действие (альтернатива)',
                category: 'history',
                global: true
            },
            
            // Элементы
            'Delete': {
                action: () => this.deleteSelectedElements(),
                description: 'Удалить выбранные элементы',
                category: 'elements',
                global: false
            },
            'Backspace': {
                action: () => this.deleteSelectedElements(),
                description: 'Удалить выбранные элементы',
                category: 'elements',
                global: false
            },
            'Ctrl+D': {
                action: () => this.duplicateSelectedElements(),
                description: 'Дублировать элементы',
                category: 'elements',
                global: false
            },
            'Ctrl+A': {
                action: () => this.selectAllElements(),
                description: 'Выбрать все элементы',
                category: 'elements',
                global: false
            },
            'Escape': {
                action: () => this.deselectAllElements(),
                description: 'Снять выделение',
                category: 'elements',
                global: false
            },
            
            // Редактирование
            'Ctrl+C': {
                action: () => this.copySelectedElements(),
                description: 'Копировать элементы',
                category: 'edit',
                global: false
            },
            'Ctrl+V': {
                action: () => this.pasteElements(),
                description: 'Вставить элементы',
                category: 'edit',
                global: false
            },
            'Ctrl+X': {
                action: () => this.cutSelectedElements(),
                description: 'Вырезать элементы',
                category: 'edit',
                global: false
            },
            
            // Навигация
            'Ctrl+Tab': {
                action: () => this.switchToNextPanel(),
                description: 'Следующая панель',
                category: 'navigation',
                global: false
            },
            'Ctrl+Shift+Tab': {
                action: () => this.switchToPreviousPanel(),
                description: 'Предыдущая панель',
                category: 'navigation',
                global: false
            },
            
            // Масштаб
            'Ctrl+Plus': {
                action: () => this.zoomIn(),
                description: 'Увеличить масштаб',
                category: 'view',
                global: false
            },
            'Ctrl+Minus': {
                action: () => this.zoomOut(),
                description: 'Уменьшить масштаб',
                category: 'view',
                global: false
            },
            'Ctrl+0': {
                action: () => this.resetZoom(),
                description: 'Сбросить масштаб',
                category: 'view',
                global: false
            },
            
            // Инструменты
            'F1': {
                action: () => this.showHelp(),
                description: 'Показать справку',
                category: 'tools',
                global: true
            },
            'F2': {
                action: () => this.renameSelectedElement(),
                description: 'Переименовать элемент',
                category: 'tools',
                global: false
            },
            'F5': {
                action: () => this.refreshCanvas(),
                description: 'Обновить холст',
                category: 'tools',
                global: false
            },
            'Ctrl+F': {
                action: () => this.showSearch(),
                description: 'Поиск элементов',
                category: 'tools',
                global: false
            },
            
            // Предварительный просмотр
            'F12': {
                action: () => this.visualBuilder.previewPage(),
                description: 'Предварительный просмотр',
                category: 'preview',
                global: true
            },
            'Ctrl+Shift+P': {
                action: () => this.visualBuilder.previewPage(),
                description: 'Предварительный просмотр',
                category: 'preview',
                global: true
            },
            
            // Настройки
            'Ctrl+,': {
                action: () => this.showSettings(),
                description: 'Настройки',
                category: 'settings',
                global: true
            },
            'Ctrl+Shift+K': {
                action: () => this.showShortcutsHelp(),
                description: 'Справка по горячим клавишам',
                category: 'settings',
                global: true
            }
        };
        
        // Загружаем пользовательские настройки
        this.shortcuts = this.loadUserShortcuts();
        
        // Инициализация
        this.init();
    }
    
    /**
     * Инициализация системы горячих клавиш
     */
    init() {
        this.setupEventListeners();
        this.loadSettings();
        console.info('⌨️ Keyboard Shortcuts инициализированы');
    }
    
    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Глобальные обработчики
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        document.addEventListener('keyup', this.handleKeyup.bind(this));
        
        // Обработчики для фокуса
        document.addEventListener('focusin', this.handleFocusIn.bind(this));
        document.addEventListener('focusout', this.handleFocusOut.bind(this));
        
        // Обработчики для модальных окон
        document.addEventListener('modal:open', this.disableShortcuts.bind(this));
        document.addEventListener('modal:close', this.enableShortcuts.bind(this));
    }
    
    /**
     * Обработчик нажатия клавиш
     */
    handleKeydown(event) {
        if (!this.isEnabled || this.isRecording) {
            return;
        }
        
        // Проверяем, не находится ли фокус в поле ввода
        if (this.isInputFocused(event.target)) {
            return;
        }
        
        const key = this.getKeyCombination(event);
        const shortcut = this.shortcuts[key];
        
        if (shortcut) {
            event.preventDefault();
            event.stopPropagation();
            
            try {
                // Выполняем действие
                shortcut.action();
                
                // Показываем визуальную обратную связь
                this.showShortcutFeedback(key, shortcut.description);
                
                // Логируем использование
                this.logShortcutUsage(key);
                
            } catch (error) {
                console.error('Ошибка выполнения горячей клавиши:', error);
                this.visualBuilder.showNotification('Ошибка выполнения действия', 'error');
            }
        }
    }
    
    /**
     * Обработчик отпускания клавиш
     */
    handleKeyup(event) {
        // Обработка для записи новых горячих клавиш
        if (this.isRecording && this.recordingCallback) {
            const key = this.getKeyCombination(event);
            if (key && key !== 'Escape') {
                this.recordingCallback(key);
            }
            this.stopRecording();
        }
    }
    
    /**
     * Обработчик получения фокуса
     */
    handleFocusIn(event) {
        // Отключаем некоторые горячие клавиши при фокусе на полях ввода
        if (this.isInputFocused(event.target)) {
            this.disableInputShortcuts();
        }
    }
    
    /**
     * Обработчик потери фокуса
     */
    handleFocusOut(event) {
        // Включаем горячие клавиши обратно
        this.enableInputShortcuts();
    }
    
    /**
     * Получение комбинации клавиш
     */
    getKeyCombination(event) {
        const keys = [];
        
        if (event.ctrlKey || event.metaKey) keys.push('Ctrl');
        if (event.shiftKey) keys.push('Shift');
        if (event.altKey) keys.push('Alt');
        
        // Обработка специальных клавиш
        let key = event.key;
        switch (key) {
            case ' ':
                key = 'Space';
                break;
            case 'ArrowUp':
                key = 'Up';
                break;
            case 'ArrowDown':
                key = 'Down';
                break;
            case 'ArrowLeft':
                key = 'Left';
                break;
            case 'ArrowRight':
                key = 'Right';
                break;
            case 'Enter':
                key = 'Enter';
                break;
            case 'Tab':
                key = 'Tab';
                break;
            case 'Escape':
                key = 'Escape';
                break;
            case 'Delete':
                key = 'Delete';
                break;
            case 'Backspace':
                key = 'Backspace';
                break;
            case 'Home':
                key = 'Home';
                break;
            case 'End':
                key = 'End';
                break;
            case 'PageUp':
                key = 'PageUp';
                break;
            case 'PageDown':
                key = 'PageDown';
                break;
            case 'Insert':
                key = 'Insert';
                break;
            case 'F1':
            case 'F2':
            case 'F3':
            case 'F4':
            case 'F5':
            case 'F6':
            case 'F7':
            case 'F8':
            case 'F9':
            case 'F10':
            case 'F11':
            case 'F12':
                key = key;
                break;
            default:
                // Для обычных клавиш
                if (key.length === 1) {
                    key = key.toUpperCase();
                }
        }
        
        keys.push(key);
        return keys.join('+');
    }
    
    /**
     * Проверка фокуса на поле ввода
     */
    isInputFocused(element) {
        const inputTypes = ['input', 'textarea', 'select'];
        const contentEditable = element.contentEditable === 'true';
        
        return inputTypes.includes(element.tagName.toLowerCase()) || 
               contentEditable ||
               element.closest('[contenteditable="true"]');
    }
    
    /**
     * Отключение горячих клавиш для полей ввода
     */
    disableInputShortcuts() {
        // Отключаем только те горячие клавиши, которые могут конфликтовать
        const inputShortcuts = ['Ctrl+A', 'Ctrl+C', 'Ctrl+V', 'Ctrl+X', 'Ctrl+Z', 'Ctrl+Y'];
        this.disabledForInput = inputShortcuts;
    }
    
    /**
     * Включение горячих клавиш обратно
     */
    enableInputShortcuts() {
        this.disabledForInput = [];
    }
    
    /**
     * Отключение всех горячих клавиш
     */
    disableShortcuts() {
        this.isEnabled = false;
    }
    
    /**
     * Включение горячих клавиш
     */
    enableShortcuts() {
        this.isEnabled = true;
    }
    
    /**
     * Показать визуальную обратную связь
     */
    showShortcutFeedback(key, description) {
        const feedback = document.createElement('div');
        feedback.className = 'shortcut-feedback';
        feedback.innerHTML = `
            <div class="shortcut-feedback-content">
                <div class="shortcut-feedback-key">${key}</div>
                <div class="shortcut-feedback-desc">${description}</div>
            </div>
        `;
        
        document.body.appendChild(feedback);
        
        // Показываем анимацию
        requestAnimationFrame(() => {
            feedback.classList.add('show');
        });
        
        // Скрываем через 2 секунды
        setTimeout(() => {
            feedback.classList.remove('show');
            setTimeout(() => {
                if (feedback.parentNode) {
                    feedback.parentNode.removeChild(feedback);
                }
            }, 300);
        }, 2000);
    }
    
    /**
     * Логирование использования горячих клавиш
     */
    logShortcutUsage(key) {
        // Сохраняем статистику использования
        const stats = JSON.parse(localStorage.getItem('vb-shortcut-stats') || '{}');
        stats[key] = (stats[key] || 0) + 1;
        localStorage.setItem('vb-shortcut-stats', JSON.stringify(stats));
    }
    
    /**
     * Начать запись новой горячей клавиши
     */
    startRecording(callback) {
        this.isRecording = true;
        this.recordingCallback = callback;
        
        // Показываем индикатор записи
        this.showRecordingIndicator();
    }
    
    /**
     * Остановить запись
     */
    stopRecording() {
        this.isRecording = false;
        this.recordingCallback = null;
        
        // Скрываем индикатор записи
        this.hideRecordingIndicator();
    }
    
    /**
     * Показать индикатор записи
     */
    showRecordingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'shortcut-recording-indicator';
        indicator.innerHTML = `
            <div class="recording-content">
                <div class="recording-icon">🎙️</div>
                <div class="recording-text">Нажмите комбинацию клавиш...</div>
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        requestAnimationFrame(() => {
            indicator.classList.add('show');
        });
    }
    
    /**
     * Скрыть индикатор записи
     */
    hideRecordingIndicator() {
        const indicator = document.querySelector('.shortcut-recording-indicator');
        if (indicator) {
            indicator.classList.remove('show');
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }
    }
    
    /**
     * Загрузить пользовательские настройки
     */
    loadUserShortcuts() {
        try {
            const saved = localStorage.getItem('vb-keyboard-shortcuts');
            if (saved) {
                const userShortcuts = JSON.parse(saved);
                return { ...this.defaultShortcuts, ...userShortcuts };
            }
        } catch (error) {
            console.warn('Ошибка загрузки пользовательских горячих клавиш:', error);
        }
        
        return { ...this.defaultShortcuts };
    }
    
    /**
     * Сохранить пользовательские настройки
     */
    saveUserShortcuts() {
        try {
            localStorage.setItem('vb-keyboard-shortcuts', JSON.stringify(this.shortcuts));
            console.info('💾 Пользовательские горячие клавиши сохранены');
        } catch (error) {
            console.error('Ошибка сохранения горячих клавиш:', error);
        }
    }
    
    /**
     * Сбросить к настройкам по умолчанию
     */
    resetToDefaults() {
        this.shortcuts = { ...this.defaultShortcuts };
        this.saveUserShortcuts();
        this.visualBuilder.showNotification('Горячие клавиши сброшены к настройкам по умолчанию', 'info');
    }
    
    /**
     * Добавить новую горячую клавишу
     */
    addShortcut(key, action, description, category = 'custom') {
        this.shortcuts[key] = {
            action,
            description,
            category,
            global: false
        };
        this.saveUserShortcuts();
    }
    
    /**
     * Удалить горячую клавишу
     */
    removeShortcut(key) {
        if (this.shortcuts[key] && this.shortcuts[key].category === 'custom') {
            delete this.shortcuts[key];
            this.saveUserShortcuts();
            return true;
        }
        return false;
    }
    
    /**
     * Проверить конфликты горячих клавиш
     */
    checkConflicts() {
        const conflicts = [];
        const keys = Object.keys(this.shortcuts);
        
        for (let i = 0; i < keys.length; i++) {
            for (let j = i + 1; j < keys.length; j++) {
                if (keys[i] === keys[j]) {
                    conflicts.push({
                        key: keys[i],
                        shortcut1: this.shortcuts[keys[i]],
                        shortcut2: this.shortcuts[keys[j]]
                    });
                }
            }
        }
        
        return conflicts;
    }
    
    /**
     * Получить статистику использования
     */
    getUsageStats() {
        try {
            return JSON.parse(localStorage.getItem('vb-shortcut-stats') || '{}');
        } catch {
            return {};
        }
    }
    
    /**
     * Показать справку по горячим клавишам
     */
    showShortcutsHelp() {
        this.showShortcutsModal();
    }
    
    /**
     * Показать модальное окно с горячими клавишами
     */
    showShortcutsModal() {
        const modal = document.createElement('div');
        modal.className = 'keyboard-shortcuts-modal';
        modal.innerHTML = `
            <div class="keyboard-shortcuts-content">
                <div class="keyboard-shortcuts-header">
                    <h3 class="keyboard-shortcuts-title">
                        <i class="bi bi-keyboard"></i>
                        Горячие клавиши
                    </h3>
                    <button class="keyboard-shortcuts-close" onclick="this.closest('.keyboard-shortcuts-modal').remove()">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <div class="keyboard-shortcuts-body">
                    <div class="shortcuts-toolbar">
                        <div class="shortcuts-search">
                            <input type="text" id="shortcutsSearch" placeholder="Поиск горячих клавиш...">
                        </div>
                        <div class="shortcuts-actions">
                            <button class="btn btn-secondary btn-sm" onclick="visualBuilder.keyboardShortcuts.resetToDefaults()">
                                <i class="bi bi-arrow-clockwise"></i>
                                Сбросить
                            </button>
                            <button class="btn btn-primary btn-sm" onclick="visualBuilder.keyboardShortcuts.exportShortcuts()">
                                <i class="bi bi-download"></i>
                                Экспорт
                            </button>
                            <button class="btn btn-success btn-sm" onclick="visualBuilder.keyboardShortcuts.importShortcuts()">
                                <i class="bi bi-upload"></i>
                                Импорт
                            </button>
                        </div>
                    </div>
                    <div class="shortcuts-content" id="shortcutsContent">
                        ${this.generateShortcutsHTML()}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Показываем модальное окно
        requestAnimationFrame(() => {
            modal.style.display = 'block';
        });
        
        // Настраиваем поиск
        this.setupShortcutsSearch();
    }
    
    /**
     * Генерация HTML для горячих клавиш
     */
    generateShortcutsHTML() {
        const categories = {
            file: { name: 'Файлы', icon: '📁' },
            history: { name: 'История', icon: '⏮️' },
            elements: { name: 'Элементы', icon: '🧩' },
            edit: { name: 'Редактирование', icon: '✏️' },
            navigation: { name: 'Навигация', icon: '🧭' },
            view: { name: 'Вид', icon: '👁️' },
            tools: { name: 'Инструменты', icon: '🔧' },
            preview: { name: 'Предпросмотр', icon: '👀' },
            settings: { name: 'Настройки', icon: '⚙️' },
            custom: { name: 'Пользовательские', icon: '🎨' }
        };
        
        let html = '';
        
        Object.entries(categories).forEach(([categoryKey, category]) => {
            const categoryShortcuts = Object.entries(this.shortcuts)
                .filter(([key, shortcut]) => shortcut.category === categoryKey)
                .sort((a, b) => a[1].description.localeCompare(b[1].description));
            
            if (categoryShortcuts.length > 0) {
                html += `
                    <div class="shortcuts-category" data-category="${categoryKey}">
                        <h4 class="category-title">
                            ${category.icon} ${category.name}
                        </h4>
                        <div class="shortcuts-list">
                            ${categoryShortcuts.map(([key, shortcut]) => `
                                <div class="shortcut-item" data-key="${key}">
                                    <div class="shortcut-key">${key}</div>
                                    <div class="shortcut-desc">${shortcut.description}</div>
                                    <div class="shortcut-actions">
                                        ${shortcut.category === 'custom' ? `
                                            <button class="btn btn-sm btn-danger" onclick="visualBuilder.keyboardShortcuts.removeShortcut('${key}')">
                                                <i class="bi bi-trash"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        });
        
        return html;
    }
    
    /**
     * Настройка поиска по горячим клавишам
     */
    setupShortcutsSearch() {
        const searchInput = document.getElementById('shortcutsSearch');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const items = document.querySelectorAll('.shortcut-item');
                
                items.forEach(item => {
                    const key = item.querySelector('.shortcut-key').textContent.toLowerCase();
                    const desc = item.querySelector('.shortcut-desc').textContent.toLowerCase();
                    
                    if (key.includes(query) || desc.includes(query)) {
                        item.style.display = 'flex';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        }
    }
    
    /**
     * Экспорт горячих клавиш
     */
    exportShortcuts() {
        const data = {
            shortcuts: this.shortcuts,
            stats: this.getUsageStats(),
            exportDate: new Date().toISOString(),
            version: '1.0'
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `visual-builder-shortcuts-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.visualBuilder.showNotification('Горячие клавиши экспортированы', 'success');
    }
    
    /**
     * Импорт горячих клавиш
     */
    importShortcuts() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    try {
                        const data = JSON.parse(e.target.result);
                        if (data.shortcuts) {
                            this.shortcuts = { ...this.defaultShortcuts, ...data.shortcuts };
                            this.saveUserShortcuts();
                            this.visualBuilder.showNotification('Горячие клавиши импортированы', 'success');
                            
                            // Обновляем модальное окно
                            const content = document.getElementById('shortcutsContent');
                            if (content) {
                                content.innerHTML = this.generateShortcutsHTML();
                            }
                        }
                    } catch (error) {
                        this.visualBuilder.showNotification('Ошибка импорта файла', 'error');
                    }
                };
                reader.readAsText(file);
            }
        };
        
        input.click();
    }
    
    // Методы для выполнения действий
    
    /**
     * Удалить выбранные элементы
     */
    deleteSelectedElements() {
        const selectedElements = this.visualBuilder.dom.canvas.querySelectorAll('.draggable-element.selected');
        if (selectedElements.length > 0) {
            selectedElements.forEach(element => {
                this.visualBuilder.deleteElement(element);
            });
        } else {
            this.visualBuilder.showNotification('Нет выбранных элементов для удаления', 'warning');
        }
    }
    
    /**
     * Дублировать выбранные элементы
     */
    duplicateSelectedElements() {
        const selectedElements = this.visualBuilder.dom.canvas.querySelectorAll('.draggable-element.selected');
        if (selectedElements.length > 0) {
            selectedElements.forEach(element => {
                this.visualBuilder.duplicateElement(element);
            });
        } else {
            this.visualBuilder.showNotification('Нет выбранных элементов для дублирования', 'warning');
        }
    }
    
    /**
     * Выбрать все элементы
     */
    selectAllElements() {
        this.visualBuilder.selectAllElements();
    }
    
    /**
     * Снять выделение со всех элементов
     */
    deselectAllElements() {
        this.visualBuilder.deselectAllElements();
    }
    
    /**
     * Копировать выбранные элементы
     */
    copySelectedElements() {
        const selectedElements = this.visualBuilder.dom.canvas.querySelectorAll('.draggable-element.selected');
        if (selectedElements.length > 0) {
            // Реализация копирования в буфер обмена
            this.visualBuilder.showNotification('Копирование элементов', 'info');
        } else {
            this.visualBuilder.showNotification('Нет выбранных элементов для копирования', 'warning');
        }
    }
    
    /**
     * Вставить элементы
     */
    pasteElements() {
        // Реализация вставки из буфера обмена
        this.visualBuilder.showNotification('Вставка элементов', 'info');
    }
    
    /**
     * Вырезать выбранные элементы
     */
    cutSelectedElements() {
        const selectedElements = this.visualBuilder.dom.canvas.querySelectorAll('.draggable-element.selected');
        if (selectedElements.length > 0) {
            this.copySelectedElements();
            this.deleteSelectedElements();
        } else {
            this.visualBuilder.showNotification('Нет выбранных элементов для вырезания', 'warning');
        }
    }
    
    /**
     * Переключиться на следующую панель
     */
    switchToNextPanel() {
        // Реализация переключения панелей
        this.visualBuilder.showNotification('Переключение панели', 'info');
    }
    
    /**
     * Переключиться на предыдущую панель
     */
    switchToPreviousPanel() {
        // Реализация переключения панелей
        this.visualBuilder.showNotification('Переключение панели', 'info');
    }
    
    /**
     * Увеличить масштаб
     */
    zoomIn() {
        this.visualBuilder.showNotification('Увеличение масштаба', 'info');
    }
    
    /**
     * Уменьшить масштаб
     */
    zoomOut() {
        this.visualBuilder.showNotification('Уменьшение масштаба', 'info');
    }
    
    /**
     * Сбросить масштаб
     */
    resetZoom() {
        this.visualBuilder.showNotification('Сброс масштаба', 'info');
    }
    
    /**
     * Показать справку
     */
    showHelp() {
        this.visualBuilder.showNotification('Открытие справки', 'info');
    }
    
    /**
     * Переименовать выбранный элемент
     */
    renameSelectedElement() {
        if (this.visualBuilder.state.selectedElement) {
            const newName = prompt('Введите новое имя элемента:');
            if (newName) {
                this.visualBuilder.state.selectedElement.dataset.name = newName;
                this.visualBuilder.updateLayersPanel();
                this.visualBuilder.showNotification('Элемент переименован', 'success');
            }
        } else {
            this.visualBuilder.showNotification('Сначала выберите элемент', 'warning');
        }
    }
    
    /**
     * Обновить холст
     */
    refreshCanvas() {
        this.visualBuilder.updateLayersPanel();
        this.visualBuilder.showNotification('Холст обновлен', 'success');
    }
    
    /**
     * Показать поиск
     */
    showSearch() {
        this.visualBuilder.showNotification('Открытие поиска', 'info');
    }
    
    /**
     * Показать настройки
     */
    showSettings() {
        this.visualBuilder.showNotification('Открытие настроек', 'info');
    }
    
    /**
     * Загрузить настройки
     */
    loadSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('vb-keyboard-settings') || '{}');
            this.isEnabled = settings.enabled !== false;
        } catch (error) {
            console.warn('Ошибка загрузки настроек горячих клавиш:', error);
        }
    }
    
    /**
     * Сохранить настройки
     */
    saveSettings() {
        try {
            const settings = {
                enabled: this.isEnabled
            };
            localStorage.setItem('vb-keyboard-settings', JSON.stringify(settings));
        } catch (error) {
            console.error('Ошибка сохранения настроек горячих клавиш:', error);
        }
    }
}

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeyboardShortcuts;
} 