/**
 * Visual Editor для HTML файлов
 * Интеграция HTML Parser с Visual Builder
 */

class VisualEditor {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.htmlParser = null;
        this.currentFile = null;
        this.isEditing = false;
        this.originalContent = null;
        
        // Состояние редактора
        this.state = {
            mode: 'visual', // visual, code, split
            autoSave: true,
            showLineNumbers: true,
            wordWrap: true,
            theme: 'light'
        };
        
        // DOM элементы
        this.dom = {};
        
        // Инициализация
        this.init();
    }

    /**
     * Инициализация Visual Editor
     */
    async init() {
        try {
            // Инициализируем HTML Parser
            const { HTMLParser } = await import('./html-parser.js');
            this.htmlParser = new HTMLParser(this.visualBuilder);
            
            this.createEditorUI();
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            
            console.info('🎨 Visual Editor инициализирован');
        } catch (error) {
            console.error('❌ Ошибка инициализации Visual Editor:', error);
        }
    }

    /**
     * Создание UI редактора
     */
    createEditorUI() {
        // Создаем модальное окно редактора
        const modal = document.createElement('div');
        modal.className = 'visual-editor-modal';
        modal.id = 'visualEditorModal';
        modal.innerHTML = `
            <div class="visual-editor-content">
                <div class="visual-editor-header">
                    <div class="visual-editor-title">
                        <i class="bi bi-file-earmark-code"></i>
                        <span id="editorTitle">Visual Editor</span>
                    </div>
                    <div class="visual-editor-actions">
                        <div class="editor-mode-toggle">
                            <button class="btn btn-sm btn-secondary" data-mode="visual" onclick="visualEditor.setMode('visual')">
                                <i class="bi bi-eye"></i> Visual
                            </button>
                            <button class="btn btn-sm btn-secondary" data-mode="code" onclick="visualEditor.setMode('code')">
                                <i class="bi bi-code-slash"></i> Code
                            </button>
                            <button class="btn btn-sm btn-secondary" data-mode="split" onclick="visualEditor.setMode('split')">
                                <i class="bi bi-layout-split"></i> Split
                            </button>
                        </div>
                        <button class="btn btn-sm btn-success" onclick="visualEditor.saveFile()" id="saveFileBtn">
                            <i class="bi bi-save"></i> Сохранить
                        </button>
                        <button class="btn btn-sm btn-info" onclick="visualEditor.previewFile()" id="previewFileBtn">
                            <i class="bi bi-eye"></i> Просмотр
                        </button>
                        <button class="btn btn-sm btn-ghost" onclick="visualEditor.close()" title="Закрыть">
                            <i class="bi bi-x-lg"></i>
                        </button>
                    </div>
                </div>
                
                <div class="visual-editor-toolbar">
                    <div class="editor-controls">
                        <button class="btn btn-sm btn-secondary" onclick="visualEditor.toggleAutoSave()" id="autoSaveBtn">
                            <i class="bi bi-check-circle"></i> Автосохранение
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualEditor.toggleLineNumbers()" id="lineNumbersBtn">
                            <i class="bi bi-list-ol"></i> Номера строк
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualEditor.toggleWordWrap()" id="wordWrapBtn">
                            <i class="bi bi-text-wrap"></i> Перенос строк
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="visualEditor.toggleTheme()" id="themeBtn">
                            <i class="bi bi-moon"></i> Тема
                        </button>
                    </div>
                    <div class="editor-info">
                        <span id="fileInfo">Файл не выбран</span>
                        <span id="cursorInfo">Ln 1, Col 1</span>
                    </div>
                </div>
                
                <div class="visual-editor-body">
                    <!-- Visual Mode -->
                    <div class="editor-panel visual-panel" id="visualPanel">
                        <div class="visual-canvas" id="visualCanvas">
                            <div class="canvas-placeholder">
                                <i class="bi bi-file-earmark-text"></i>
                                <p>Выберите HTML файл для редактирования</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Code Mode -->
                    <div class="editor-panel code-panel" id="codePanel" style="display: none;">
                        <div class="code-editor-wrapper">
                            <div class="line-numbers" id="lineNumbers"></div>
                            <textarea class="code-editor" id="codeEditor" spellcheck="false"></textarea>
                        </div>
                    </div>
                    
                    <!-- Split Mode -->
                    <div class="editor-panel split-panel" id="splitPanel" style="display: none;">
                        <div class="split-container">
                            <div class="split-panel-left">
                                <div class="code-editor-wrapper">
                                    <div class="line-numbers" id="splitLineNumbers"></div>
                                    <textarea class="code-editor" id="splitCodeEditor" spellcheck="false"></textarea>
                                </div>
                            </div>
                            <div class="split-divider"></div>
                            <div class="split-panel-right">
                                <div class="visual-canvas" id="splitVisualCanvas"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="visual-editor-footer">
                    <div class="editor-status">
                        <span id="statusMessage">Готов</span>
                    </div>
                    <div class="editor-stats">
                        <span id="elementCount">Элементов: 0</span>
                        <span id="wordCount">Слов: 0</span>
                        <span id="charCount">Символов: 0</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Кэшируем DOM элементы
        this.dom = {
            modal: modal,
            title: modal.querySelector('#editorTitle'),
            visualPanel: modal.querySelector('#visualPanel'),
            codePanel: modal.querySelector('#codePanel'),
            splitPanel: modal.querySelector('#splitPanel'),
            visualCanvas: modal.querySelector('#visualCanvas'),
            codeEditor: modal.querySelector('#codeEditor'),
            splitCodeEditor: modal.querySelector('#splitCodeEditor'),
            splitVisualCanvas: modal.querySelector('#splitVisualCanvas'),
            lineNumbers: modal.querySelector('#lineNumbers'),
            splitLineNumbers: modal.querySelector('#splitLineNumbers'),
            fileInfo: modal.querySelector('#fileInfo'),
            cursorInfo: modal.querySelector('#cursorInfo'),
            statusMessage: modal.querySelector('#statusMessage'),
            elementCount: modal.querySelector('#elementCount'),
            wordCount: modal.querySelector('#wordCount'),
            charCount: modal.querySelector('#charCount'),
            autoSaveBtn: modal.querySelector('#autoSaveBtn'),
            lineNumbersBtn: modal.querySelector('#lineNumbersBtn'),
            wordWrapBtn: modal.querySelector('#wordWrapBtn'),
            themeBtn: modal.querySelector('#themeBtn')
        };
        
        // Инициализируем CodeMirror для code editor
        this.initCodeEditor();
    }

    /**
     * Инициализация Code Editor
     */
    initCodeEditor() {
        // Простая реализация без внешних библиотек
        this.setupCodeEditor(this.dom.codeEditor);
        this.setupCodeEditor(this.dom.splitCodeEditor);
    }

    /**
     * Настройка Code Editor
     */
    setupCodeEditor(textarea) {
        // Настройка синтаксиса
        textarea.style.fontFamily = "'Fira Code', 'Courier New', monospace";
        textarea.style.fontSize = '14px';
        textarea.style.lineHeight = '1.5';
        textarea.style.tabSize = '2';
        
        // Обработка Tab
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                
                textarea.value = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = start + 2;
            }
        });
        
        // Обновление номеров строк
        textarea.addEventListener('input', () => {
            this.updateLineNumbers(textarea);
            this.updateStats();
            this.updateCursorInfo(textarea);
        });
        
        // Обновление позиции курсора
        textarea.addEventListener('click', () => {
            this.updateCursorInfo(textarea);
        });
        
        textarea.addEventListener('keyup', () => {
            this.updateCursorInfo(textarea);
        });
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // Клик по модальному окну
        this.dom.modal.addEventListener('click', (e) => {
            if (e.target === this.dom.modal) {
                this.close();
            }
        });

        // Горячие клавиши
        document.addEventListener('keydown', (e) => {
            if (!this.isEditing) return;
            
            if (e.ctrlKey || e.metaKey) {
                switch (e.key.toLowerCase()) {
                    case 's':
                        e.preventDefault();
                        this.saveFile();
                        break;
                    case 'p':
                        e.preventDefault();
                        this.previewFile();
                        break;
                    case '1':
                        e.preventDefault();
                        this.setMode('visual');
                        break;
                    case '2':
                        e.preventDefault();
                        this.setMode('code');
                        break;
                    case '3':
                        e.preventDefault();
                        this.setMode('split');
                        break;
                }
            }
        });
    }

    /**
     * Настройка горячих клавиш
     */
    setupKeyboardShortcuts() {
        // Уже реализовано в setupEventListeners
        console.info('⌨️ Горячие клавиши Visual Editor настроены');
    }

    /**
     * Открытие файла в редакторе
     */
    async openFile(filePath) {
        try {
            this.currentFile = filePath;
            this.isEditing = true;
            
            this.showLoading('Загрузка файла...');
            
            // Загружаем файл
            const response = await fetch('/api/visual-builder/files/open', {
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
                const content = data.content;
                this.originalContent = content;
                
                // Обновляем UI
                this.updateFileInfo(filePath);
                this.setContent(content);
                
                // Парсим HTML в визуальные элементы
                if (this.htmlParser) {
                    const elements = this.htmlParser.parseHTMLToElements(content, filePath);
                    this.updateElementCount(elements.length);
                }
                
                this.open();
                this.showStatus('Файл загружен успешно');
                
                console.info(`✅ Файл "${filePath}" открыт в редакторе`);
            } else {
                throw new Error(data.error || 'Ошибка загрузки файла');
            }
            
        } catch (error) {
            console.error('Ошибка открытия файла:', error);
            this.showStatus('Ошибка загрузки файла', 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Установка контента в редактор
     */
    setContent(content) {
        // Устанавливаем в code editor
        this.dom.codeEditor.value = content;
        this.dom.splitCodeEditor.value = content;
        
        // Обновляем номера строк
        this.updateLineNumbers(this.dom.codeEditor);
        this.updateLineNumbers(this.dom.splitCodeEditor);
        
        // Обновляем статистику
        this.updateStats();
        
        // Парсим в визуальные элементы
        if (this.htmlParser) {
            const elements = this.htmlParser.parseHTMLToElements(content, this.currentFile);
            this.setVisualContent(elements);
        }
    }

    /**
     * Установка визуального контента
     */
    setVisualContent(elements) {
        // Очищаем canvas
        this.dom.visualCanvas.innerHTML = '';
        this.dom.splitVisualCanvas.innerHTML = '';
        
        // Добавляем элементы
        elements.forEach(element => {
            const clone = element.cloneNode(true);
            this.dom.visualCanvas.appendChild(clone);
            this.dom.splitVisualCanvas.appendChild(clone.cloneNode(true));
        });
        
        // Если нет элементов, показываем placeholder
        if (elements.length === 0) {
            this.showCanvasPlaceholder(this.dom.visualCanvas);
            this.showCanvasPlaceholder(this.dom.splitVisualCanvas);
        }
    }

    /**
     * Показ placeholder для canvas
     */
    showCanvasPlaceholder(canvas) {
        canvas.innerHTML = `
            <div class="canvas-placeholder">
                <i class="bi bi-file-earmark-text"></i>
                <p>HTML контент будет отображен здесь</p>
            </div>
        `;
    }

    /**
     * Сохранение файла
     */
    async saveFile() {
        if (!this.currentFile) {
            this.showStatus('Файл не выбран', 'error');
            return;
        }
        
        try {
            this.showLoading('Сохранение файла...');
            
            let content;
            
            // Получаем контент в зависимости от режима
            if (this.state.mode === 'code') {
                content = this.dom.codeEditor.value;
            } else if (this.state.mode === 'split') {
                content = this.dom.splitCodeEditor.value;
            } else {
                // Визуальный режим - экспортируем HTML
                const elements = this.dom.visualCanvas.querySelectorAll('.draggable-element');
                content = this.htmlParser.exportToHTML(elements);
            }
            
            const response = await fetch('/api/visual-builder/files/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.visualBuilder.config.csrfToken
                },
                body: JSON.stringify({
                    filepath: this.currentFile,
                    content: content
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.originalContent = content;
                this.showStatus('Файл сохранен успешно', 'success');
                console.info(`✅ Файл "${this.currentFile}" сохранен`);
            } else {
                throw new Error(data.error || 'Ошибка сохранения файла');
            }
            
        } catch (error) {
            console.error('Ошибка сохранения файла:', error);
            this.showStatus('Ошибка сохранения файла', 'error');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Предварительный просмотр файла
     */
    previewFile() {
        if (!this.currentFile) {
            this.showStatus('Файл не выбран', 'error');
            return;
        }
        
        try {
            let content;
            
            if (this.state.mode === 'code') {
                content = this.dom.codeEditor.value;
            } else if (this.state.mode === 'split') {
                content = this.dom.splitCodeEditor.value;
            } else {
                const elements = this.dom.visualCanvas.querySelectorAll('.draggable-element');
                content = this.htmlParser.exportToHTML(elements);
            }
            
            // Открываем в новом окне
            const previewWindow = window.open('', '_blank', 'width=1200,height=800');
            if (previewWindow) {
                previewWindow.document.write(content);
                previewWindow.document.close();
            } else {
                this.showStatus('Не удалось открыть окно предпросмотра', 'error');
            }
            
        } catch (error) {
            console.error('Ошибка предпросмотра:', error);
            this.showStatus('Ошибка предпросмотра', 'error');
        }
    }

    /**
     * Установка режима редактора
     */
    setMode(mode) {
        this.state.mode = mode;
        
        // Обновляем кнопки
        document.querySelectorAll('.editor-mode-toggle button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
        
        // Показываем соответствующий панель
        this.dom.visualPanel.style.display = 'none';
        this.dom.codePanel.style.display = 'none';
        this.dom.splitPanel.style.display = 'none';
        
        switch (mode) {
            case 'visual':
                this.dom.visualPanel.style.display = 'block';
                break;
            case 'code':
                this.dom.codePanel.style.display = 'block';
                break;
            case 'split':
                this.dom.splitPanel.style.display = 'block';
                break;
        }
        
        this.showStatus(`Режим: ${mode}`);
    }

    /**
     * Переключение автосохранения
     */
    toggleAutoSave() {
        this.state.autoSave = !this.state.autoSave;
        this.dom.autoSaveBtn.classList.toggle('active', this.state.autoSave);
        this.showStatus(`Автосохранение: ${this.state.autoSave ? 'включено' : 'выключено'}`);
    }

    /**
     * Переключение номеров строк
     */
    toggleLineNumbers() {
        this.state.showLineNumbers = !this.state.showLineNumbers;
        this.dom.lineNumbersBtn.classList.toggle('active', this.state.showLineNumbers);
        
        const lineNumbers = document.querySelectorAll('.line-numbers');
        lineNumbers.forEach(ln => {
            ln.style.display = this.state.showLineNumbers ? 'block' : 'none';
        });
    }

    /**
     * Переключение переноса строк
     */
    toggleWordWrap() {
        this.state.wordWrap = !this.state.wordWrap;
        this.dom.wordWrapBtn.classList.toggle('active', this.state.wordWrap);
        
        const editors = [this.dom.codeEditor, this.dom.splitCodeEditor];
        editors.forEach(editor => {
            editor.style.whiteSpace = this.state.wordWrap ? 'pre-wrap' : 'pre';
        });
    }

    /**
     * Переключение темы
     */
    toggleTheme() {
        this.state.theme = this.state.theme === 'light' ? 'dark' : 'light';
        this.dom.themeBtn.innerHTML = this.state.theme === 'light' ? 
            '<i class="bi bi-moon"></i> Тема' : 
            '<i class="bi bi-sun"></i> Тема';
        
        this.dom.modal.setAttribute('data-theme', this.state.theme);
        this.showStatus(`Тема: ${this.state.theme}`);
    }

    /**
     * Обновление номеров строк
     */
    updateLineNumbers(textarea) {
        const lineNumbers = textarea === this.dom.codeEditor ? 
            this.dom.lineNumbers : this.dom.splitLineNumbers;
        
        if (!this.state.showLineNumbers) return;
        
        const lines = textarea.value.split('\n');
        const lineNumbersHTML = lines.map((_, index) => 
            `<div class="line-number">${index + 1}</div>`
        ).join('');
        
        lineNumbers.innerHTML = lineNumbersHTML;
    }

    /**
     * Обновление информации о курсоре
     */
    updateCursorInfo(textarea) {
        const text = textarea.value;
        const cursorPos = textarea.selectionStart;
        
        const lines = text.substring(0, cursorPos).split('\n');
        const line = lines.length;
        const col = lines[lines.length - 1].length + 1;
        
        this.dom.cursorInfo.textContent = `Ln ${line}, Col ${col}`;
    }

    /**
     * Обновление статистики
     */
    updateStats() {
        const content = this.dom.codeEditor.value;
        const words = content.trim().split(/\s+/).length;
        const chars = content.length;
        
        this.dom.wordCount.textContent = `Слов: ${words}`;
        this.dom.charCount.textContent = `Символов: ${chars}`;
    }

    /**
     * Обновление количества элементов
     */
    updateElementCount(count) {
        this.dom.elementCount.textContent = `Элементов: ${count}`;
    }

    /**
     * Обновление информации о файле
     */
    updateFileInfo(filePath) {
        const fileName = filePath.split('/').pop();
        this.dom.title.textContent = `Visual Editor - ${fileName}`;
        this.dom.fileInfo.textContent = fileName;
    }

    /**
     * Показ статуса
     */
    showStatus(message, type = 'info') {
        this.dom.statusMessage.textContent = message;
        this.dom.statusMessage.className = `editor-status-message ${type}`;
    }

    /**
     * Показ загрузки
     */
    showLoading(message) {
        this.showStatus(message, 'loading');
    }

    /**
     * Скрытие загрузки
     */
    hideLoading() {
        this.showStatus('Готов');
    }

    /**
     * Открытие редактора
     */
    open() {
        this.dom.modal.style.display = 'flex';
        this.isEditing = true;
        
        // Устанавливаем активный режим
        this.setMode('visual');
        
        // Фокусируемся на редакторе
        setTimeout(() => {
            if (this.state.mode === 'code') {
                this.dom.codeEditor.focus();
            }
        }, 100);
    }

    /**
     * Закрытие редактора
     */
    close() {
        this.dom.modal.style.display = 'none';
        this.isEditing = false;
        this.currentFile = null;
        this.originalContent = null;
    }

    /**
     * Проверка изменений
     */
    hasChanges() {
        if (!this.currentFile || !this.originalContent) return false;
        
        let currentContent;
        if (this.state.mode === 'code') {
            currentContent = this.dom.codeEditor.value;
        } else if (this.state.mode === 'split') {
            currentContent = this.dom.splitCodeEditor.value;
        } else {
            const elements = this.dom.visualCanvas.querySelectorAll('.draggable-element');
            currentContent = this.htmlParser.exportToHTML(elements);
        }
        
        return currentContent !== this.originalContent;
    }

    /**
     * Подтверждение закрытия с несохраненными изменениями
     */
    confirmClose() {
        if (this.hasChanges()) {
            return confirm('У вас есть несохраненные изменения. Вы уверены, что хотите закрыть редактор?');
        }
        return true;
    }
}

// Глобальные функции для обратной совместимости
let visualEditor;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        visualEditor = new VisualEditor(window.visualBuilder);
        window.visualEditor = visualEditor;
        console.info('🎨 Visual Editor готов к использованию');
    }
}); 