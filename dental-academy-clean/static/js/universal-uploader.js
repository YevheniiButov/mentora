/**
 * Универсальный загрузчик контента для Mentora
 * Поддерживает загрузку учебных модулей и виртуальных пациентов
 */

class UniversalContentUploader {
    constructor() {
        this.config = {
            maxFileSize: 16 * 1024 * 1024, // 16MB
            allowedTypes: ['application/json', 'text/plain'],
            apiBaseUrl: this.getApiBaseUrl(),
            uploadTimeout: 300000, // 5 минут
        };
        
        this.state = {
            currentTab: 'learning-modules',
            selectedFiles: {
                theory: null,
                tests: null,
                scenario: null,
                batch: []
            },
            isUploading: false
        };
        
        this.notifications = new NotificationManager();
        
        this.init();
    }
    
    getApiBaseUrl() {
        // Получаем язык из URL или используем 'en' по умолчанию
        const pathParts = window.location.pathname.split('/');
        const lang = pathParts[1] || 'en';
        return `/${lang}/admin/uploader/api`;
    }

    getCsrfToken() {
        // Получаем CSRF токен из мета-тега
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        return metaTag ? metaTag.getAttribute('content') : '';
    }

    createFormDataWithCsrf(data = {}) {
        const formData = new FormData();
        
        // Добавляем CSRF токен
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            formData.append('csrf_token', csrfToken);
        }
        
        // Добавляем остальные данные
        Object.entries(data).forEach(([key, value]) => {
            formData.append(key, value);
        });
        
        return formData;
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupKeyboardNavigation();

    }
    
    setupEventListeners() {
        // Навигация по вкладкам
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e.target.dataset.target));
        });
        
        // Селекторы иерархии
        document.getElementById('learning-path-select')?.addEventListener('change', (e) => {
            this.loadSubjects(e.target.value);
            // Управляем состоянием кнопок создания
            const createSubjectBtn = document.getElementById('create-subject-btn');
            const createModuleBtn = document.getElementById('create-module-btn');
            if (e.target.value) {
                createSubjectBtn.disabled = false;
            } else {
                createSubjectBtn.disabled = true;
                createModuleBtn.disabled = true;
            }
        });
        
        document.getElementById('subject-select')?.addEventListener('change', (e) => {
            this.loadModules(e.target.value);
            // Управляем состоянием кнопки создания модуля
            const createModuleBtn = document.getElementById('create-module-btn');
            if (e.target.value) {
                createModuleBtn.disabled = false;
            } else {
                createModuleBtn.disabled = true;
            }
        });
        
        document.getElementById('module-select')?.addEventListener('change', () => {
            this.checkUploadReadiness();
        });
        
        // Файловые input'ы
        this.setupFileInputs();
        
        // Кнопки действий
        this.setupActionButtons();
        
        // Кнопки создания новых элементов
        this.setupCreateButtons();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }
    
    setupFileInputs() {
        const fileInputs = [
            { id: 'theory-file', type: 'theory' },
            { id: 'tests-file', type: 'tests' },
            { id: 'scenario-file', type: 'scenario' },
            { id: 'batch-files', type: 'batch' }
        ];
        
        fileInputs.forEach(({ id, type }) => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('change', (e) => this.handleFileSelect(e, type));
            }
        });
    }
    
    setupActionButtons() {
        // Кнопки предпросмотра
        document.getElementById('preview-learning-btn')?.addEventListener('click', () => this.showPreview('learning'));
        document.getElementById('preview-scenario-btn')?.addEventListener('click', () => this.showPreview('scenario'));
        
        // Кнопки загрузки
        document.getElementById('upload-learning-btn')?.addEventListener('click', () => this.startUpload('learning'));
        document.getElementById('upload-scenario-btn')?.addEventListener('click', () => this.startUpload('scenario'));
        document.getElementById('batch-upload-btn')?.addEventListener('click', () => this.startUpload('batch'));
        
        // Кнопка анализа пакетных файлов
        document.getElementById('analyze-batch-btn')?.addEventListener('click', () => this.analyzeBatchFiles());
    }
    
    setupDragAndDrop() {
        document.querySelectorAll('.file-drop-zone').forEach(zone => {
            // Click handler
            zone.addEventListener('click', () => {
                const fileType = zone.dataset.fileType;
                const inputId = this.getInputIdForType(fileType);
                document.getElementById(inputId)?.click();
            });
            
            // Drag & Drop handlers
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('dragover');
            });
            
            zone.addEventListener('dragleave', () => {
                zone.classList.remove('dragover');
            });
            
            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                zone.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                const fileType = zone.dataset.fileType;
                
                this.handleDroppedFiles(files, fileType);
            });
        });
    }
    
    setupKeyboardNavigation() {
        // Tab navigation
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach((tab, index) => {
            tab.setAttribute('tabindex', '0');
            tab.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.switchTab(tab.dataset.target);
                } else if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    const nextTab = tabs[index + 1] || tabs[0];
                    nextTab.focus();
                } else if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevTab = tabs[index - 1] || tabs[tabs.length - 1];
                    prevTab.focus();
                }
            });
        });
    }
    
    handleKeyboardShortcuts(e) {
        // Ctrl+P - Preview
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            if (this.state.currentTab === 'learning-modules') {
                this.showPreview('learning');
            } else if (this.state.currentTab === 'virtual-patients') {
                this.showPreview('scenario');
            }
        }
        
        // Ctrl+U - Upload
        if (e.ctrlKey && e.key === 'u') {
            e.preventDefault();
            const action = this.state.currentTab === 'learning-modules' ? 'learning' :
                          this.state.currentTab === 'virtual-patients' ? 'scenario' : 'batch';
            this.startUpload(action);
        }
        
        // Escape - Clear all
        if (e.key === 'Escape') {
            this.clearAllFiles();
        }
    }
    
    switchTab(targetTab) {
        // Убираем активные классы
        document.querySelectorAll('.nav-tab, .upload-section').forEach(el => {
            el.classList.remove('active');
        });
        
        // Добавляем активные классы
        document.querySelector(`[data-target="${targetTab}"]`).classList.add('active');
        document.getElementById(targetTab).classList.add('active');
        
        this.state.currentTab = targetTab;
        this.checkUploadReadiness();
    }
    
    async loadSubjects(pathId) {
        if (!pathId) {
            this.clearSelector('subject-select');
            this.clearSelector('module-select');
            return;
        }
        
        try {
            this.showLoading('subject-select');
            
            const response = await fetch(`${this.config.apiBaseUrl}/subjects/${pathId}`);
            if (!response.ok) throw new Error('Failed to load subjects');
            
            const subjects = await response.json();
            this.populateSelector('subject-select', subjects, 'Выберите предмет...');
            
        } catch (error) {
            console.error('Error loading subjects:', error);
            this.notifications.show('Ошибка загрузки предметов', 'error');
            this.clearSelector('subject-select');
        }
    }
    
    async loadModules(subjectId) {
        if (!subjectId) {
            this.clearSelector('module-select');
            return;
        }
        
        try {
            this.showLoading('module-select');
            
            const response = await fetch(`${this.config.apiBaseUrl}/modules/${subjectId}`);
            if (!response.ok) throw new Error('Failed to load modules');
            
            const modules = await response.json();
            this.populateSelector('module-select', modules, 'Выберите модуль...', 'title');
            
        } catch (error) {
            console.error('Error loading modules:', error);
            this.notifications.show('Ошибка загрузки модулей', 'error');
            this.clearSelector('module-select');
        }
    }
    
    populateSelector(selectorId, items, placeholder, textField = 'name') {
        const select = document.getElementById(selectorId);
        if (!select) return;
        
        select.innerHTML = `<option value="">${placeholder}</option>`;
        
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item[textField];
            select.appendChild(option);
        });
        
        select.disabled = false;
    }
    
    clearSelector(selectorId) {
        const select = document.getElementById(selectorId);
        if (!select) return;
        
        select.innerHTML = '<option value="">Сначала выберите предыдущий элемент</option>';
        select.disabled = true;
    }
    
    showLoading(selectorId) {
        const select = document.getElementById(selectorId);
        if (!select) return;
        
        select.innerHTML = '<option value="">Загрузка...</option>';
        select.disabled = true;
    }
    
    handleFileSelect(event, fileType) {
        const files = Array.from(event.target.files);
        this.processFiles(files, fileType);
    }
    
    handleDroppedFiles(files, fileType) {
        this.processFiles(files, fileType);
    }
    
    processFiles(files, fileType) {
        if (fileType === 'batch') {
            this.state.selectedFiles.batch = files;
            this.showBatchInfo(files);
        } else {
            const file = files[0];
            if (file && this.validateFile(file)) {
                this.state.selectedFiles[fileType] = file;
                this.showFileInfo(fileType, file);
            }
        }
        
        this.checkUploadReadiness();
    }
    
    validateFile(file) {
        // Проверка размера
        if (file.size > this.config.maxFileSize) {
            this.notifications.show(
                `Файл слишком большой. Максимальный размер: ${this.formatFileSize(this.config.maxFileSize)}`,
                'error'
            );
            return false;
        }
        
        // Проверка типа
        if (!file.name.toLowerCase().endsWith('.json')) {
            this.notifications.show('Поддерживаются только JSON файлы', 'error');
            return false;
        }
        
        return true;
    }
    
    showFileInfo(fileType, file) {
        const infoDiv = document.getElementById(`${fileType}-info`);
        const detailsDiv = document.getElementById(`${fileType}-details`);
        
        if (infoDiv && detailsDiv) {
            infoDiv.classList.add('show');
            detailsDiv.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        }
    }
    
    showBatchInfo(files) {
        const totalModulesDiv = document.getElementById('total-modules');
        if (totalModulesDiv) {
            totalModulesDiv.textContent = files.length;
        }
        
        // Анализ файлов
        this.analyzeBatchFiles();
    }
    
    async analyzeBatchFiles() {
        const files = this.state.selectedFiles.batch;
        if (files.length === 0) {
            this.notifications.show('Выберите файлы для анализа', 'warning');
            return;
        }
        
        const analysis = {
            modules: 0,
            scenarios: 0,
            invalid: 0
        };
        
        for (const file of files) {
            try {
                const content = await this.readFileAsText(file);
                const data = JSON.parse(content);
                
                if (this.isLearningModule(data)) {
                    analysis.modules++;
                } else if (this.isVirtualPatientScenario(data)) {
                    analysis.scenarios++;
                } else {
                    analysis.invalid++;
                }
            } catch (error) {
                analysis.invalid++;
            }
        }
        
        this.updateBatchAnalysis(analysis);
    }
    
    isLearningModule(data) {
        return Array.isArray(data) && data.some(item => 
            item.card_title || item.question || item.module_title
        );
    }
    
    isVirtualPatientScenario(data) {
        return data.title && data.description && (data.scenario_data || data.dialogue_nodes);
    }
    
    updateBatchAnalysis(analysis) {
        const modulesDiv = document.getElementById('total-modules');
        const scenariosDiv = document.getElementById('total-scenarios');
        
        if (modulesDiv) modulesDiv.textContent = analysis.modules;
        if (scenariosDiv) scenariosDiv.textContent = analysis.scenarios;
        
        if (analysis.invalid > 0) {
            this.notifications.show(
                `Найдено ${analysis.invalid} неподдерживаемых файлов`,
                'warning'
            );
        }
        
        // Включаем кнопку загрузки если есть валидные файлы
        const batchBtn = document.getElementById('batch-upload-btn');
        if (batchBtn) {
            batchBtn.disabled = (analysis.modules + analysis.scenarios) === 0;
        }
    }
    
    checkUploadReadiness() {
        // Проверка для учебных модулей
        const moduleSelected = document.getElementById('module-select')?.value;
        const hasTheory = this.state.selectedFiles.theory !== null;
        const hasTests = this.state.selectedFiles.tests !== null;
        
        const learningBtn = document.getElementById('upload-learning-btn');
        if (learningBtn) {
            learningBtn.disabled = !(moduleSelected && (hasTheory || hasTests));
        }
        
        // Проверка для виртуальных пациентов
        const scenarioBtn = document.getElementById('upload-scenario-btn');
        if (scenarioBtn) {
            scenarioBtn.disabled = this.state.selectedFiles.scenario === null;
        }
    }
    
    async showPreview(type) {
        if (type === 'learning') {
            await this.previewLearningContent();
        } else if (type === 'scenario') {
            await this.previewScenario();
        }
    }
    
    async previewLearningContent() {
        const { theory, tests } = this.state.selectedFiles;
        
        if (!theory && !tests) {
            this.notifications.show('Выберите хотя бы один файл для предпросмотра', 'warning');
            return;
        }
        
        try {
            const formData = this.createFormDataWithCsrf();
            if (theory) formData.append('theory', theory);
            if (tests) formData.append('tests', tests);
            
            const response = await fetch(`${this.config.apiBaseUrl}/preview-learning-content`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Preview failed');
            
            const result = await response.json();
            
            if (result.success) {
                this.displayLearningPreview(result.data);
                this.notifications.show('Предпросмотр готов', 'success');
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error previewing content:', error);
            this.notifications.show(`Ошибка предпросмотра: ${error.message}`, 'error');
        }
    }
    
    async previewScenario() {
        const scenario = this.state.selectedFiles.scenario;
        
        if (!scenario) {
            this.notifications.show('Выберите файл сценария для предпросмотра', 'warning');
            return;
        }
        
        try {
            const formData = this.createFormDataWithCsrf();
            formData.append('scenario', scenario);
            
            const response = await fetch(`${this.config.apiBaseUrl}/preview-scenario`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Preview failed');
            
            const result = await response.json();
            
            if (result.success) {
                this.displayScenarioPreview(result.data);
                this.notifications.show('Предпросмотр готов', 'success');
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error previewing scenario:', error);
            this.notifications.show(`Ошибка предпросмотра: ${error.message}`, 'error');
        }
    }
    
    displayLearningPreview(data) {
        const container = document.getElementById('preview-content');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Предпросмотр карточек
        if (data.theory && data.theory.length > 0) {
            const theorySection = this.createPreviewSection(
                'Карточки обучения',
                'bi-book',
                data.theory.length
            );
            
            data.theory.slice(0, 3).forEach(card => {
                const cardElement = this.createPreviewCard(
                    card.card_title || 'Без названия',
                    this.truncateText(card.content || '', 100)
                );
                theorySection.appendChild(cardElement);
            });
            
            container.appendChild(theorySection);
        }
        
        // Предпросмотр тестов
        if (data.tests && data.tests.length > 0) {
            const testsSection = this.createPreviewSection(
                'Тестовые вопросы',
                'bi-question-circle',
                data.tests.length
            );
            
            data.tests.slice(0, 3).forEach(test => {
                const testElement = this.createPreviewCard(
                    test.question || 'Вопрос без текста',
                    `Варианты: ${(test.options || []).join(', ')}`
                );
                testsSection.appendChild(testElement);
            });
            
            container.appendChild(testsSection);
        }
        
        // Показываем контейнер предпросмотра
        document.getElementById('learning-preview')?.classList.add('show');
        
        // Плавная прокрутка к предпросмотру
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    displayScenarioPreview(data) {
        const container = document.getElementById('scenario-preview-content');
        if (!container) return;
        
        container.innerHTML = `
            <div class="content-preview">
                <h6>${this.escapeHtml(data.title)}</h6>
                <p><strong>Описание:</strong> ${this.escapeHtml(data.description)}</p>
                <p><strong>Сложность:</strong> ${data.difficulty}</p>
                <p><strong>Категория:</strong> ${data.category}</p>
                <p><strong>Узлов диалога:</strong> ${data.dialogue_nodes || 0}</p>
            </div>
        `;
        
        document.getElementById('scenario-preview')?.classList.add('show');
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    createPreviewSection(title, icon, count) {
        const section = document.createElement('div');
        section.innerHTML = `
            <h6><i class="bi ${icon}"></i> ${title} (${count})</h6>
        `;
        return section;
    }
    
    createPreviewCard(title, content) {
        const card = document.createElement('div');
        card.className = 'content-preview';
        card.innerHTML = `
            <strong>${this.escapeHtml(title)}</strong>
            <p class="text-muted mb-0">${this.escapeHtml(content)}</p>
        `;
        return card;
    }
    
    async startUpload(type) {
        if (this.state.isUploading) {
            this.notifications.show('Уже выполняется загрузка', 'warning');
            return;
        }
        
        this.state.isUploading = true;
        
        try {
            if (type === 'learning') {
                await this.uploadLearningContent();
            } else if (type === 'scenario') {
                await this.uploadScenario();
            } else if (type === 'batch') {
                await this.uploadBatch();
            }
        } finally {
            this.state.isUploading = false;
        }
    }
    
    async uploadLearningContent() {
        const moduleId = document.getElementById('module-select')?.value;
        
        if (!moduleId) {
            this.notifications.show('Выберите модуль для загрузки', 'warning');
            return;
        }
        
        const formData = this.createFormDataWithCsrf({ module_id: moduleId });
        
        const { theory, tests } = this.state.selectedFiles;
        if (theory) formData.append('theory', theory);
        if (tests) formData.append('tests', tests);
        
        const button = document.getElementById('upload-learning-btn');
        const originalText = button?.innerHTML;
        
        try {
            this.setButtonLoading(button, 'Загружается...');
            
            const response = await fetch(`${this.config.apiBaseUrl}/upload-learning-content`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Upload failed');
            
            const result = await response.json();
            
            if (result.success) {
                this.notifications.show(
                    `Успешно загружено!\nКарточек: ${result.uploaded.theory || 0}\nТестов: ${result.uploaded.tests || 0}`,
                    'success'
                );
                
                this.clearLearningFiles();
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error uploading learning content:', error);
            this.notifications.show(`Ошибка загрузки: ${error.message}`, 'error');
        } finally {
            this.resetButton(button, originalText);
            this.checkUploadReadiness();
        }
    }
    
    async uploadScenario() {
        const category = document.getElementById('vp-category-select')?.value;
        const difficulty = document.getElementById('vp-difficulty-select')?.value;
        const scenario = this.state.selectedFiles.scenario;
        
        if (!scenario) {
            this.notifications.show('Выберите файл сценария', 'warning');
            return;
        }
        
        const formData = this.createFormDataWithCsrf({
            category: category || 'general',
            difficulty: difficulty || 'medium'
        });
        formData.append('scenario', scenario);
        
        const button = document.getElementById('upload-scenario-btn');
        const originalText = button?.innerHTML;
        
        try {
            this.setButtonLoading(button, 'Загружается...');
            
            const response = await fetch(`${this.config.apiBaseUrl}/upload-scenario`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Upload failed');
            
            const result = await response.json();
            
            if (result.success) {
                this.notifications.show('Сценарий успешно загружен!', 'success');
                this.clearScenarioFiles();
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error uploading scenario:', error);
            this.notifications.show(`Ошибка загрузки: ${error.message}`, 'error');
        } finally {
            this.resetButton(button, originalText);
            this.checkUploadReadiness();
        }
    }
    
    async uploadBatch() {
        const files = this.state.selectedFiles.batch;
        
        if (files.length === 0) {
            this.notifications.show('Выберите файлы для загрузки', 'warning');
            return;
        }
        
        const formData = this.createFormDataWithCsrf();
        files.forEach(file => {
            formData.append('files', file);
        });
        
        try {
            const response = await fetch(`${this.config.apiBaseUrl}/batch-upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('Batch upload failed');
            
            const result = await response.json();
            
            if (result.success) {
                this.notifications.show(
                    `Загрузка завершена!\nУспешно: ${result.results.success}\nОшибок: ${result.results.errors}`,
                    result.results.errors === 0 ? 'success' : 'warning'
                );
                
                // Обновляем статистику
                document.getElementById('success-rate').textContent = 
                    `${Math.round((result.results.success / result.results.total) * 100)}%`;
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('Error in batch upload:', error);
            this.notifications.show(`Ошибка массовой загрузки: ${error.message}`, 'error');
        }
    }
    
    // Утилитарные методы
    
    setButtonLoading(button, text) {
        if (!button) return;
        button.innerHTML = `<i class="bi bi-hourglass-split"></i> ${text}`;
        button.disabled = true;
    }
    
    resetButton(button, originalText) {
        if (!button || !originalText) return;
        button.innerHTML = originalText;
        button.disabled = false;
    }
    
    clearLearningFiles() {
        this.state.selectedFiles.theory = null;
        this.state.selectedFiles.tests = null;
        
        ['theory-info', 'tests-info', 'learning-preview'].forEach(id => {
            document.getElementById(id)?.classList.remove('show');
        });
        
        ['theory-file', 'tests-file'].forEach(id => {
            const input = document.getElementById(id);
            if (input) input.value = '';
        });
    }
    
    clearScenarioFiles() {
        this.state.selectedFiles.scenario = null;
        
        ['scenario-info', 'scenario-preview'].forEach(id => {
            document.getElementById(id)?.classList.remove('show');
        });
        
        const input = document.getElementById('scenario-file');
        if (input) input.value = '';
    }
    
    clearAllFiles() {
        this.clearLearningFiles();
        this.clearScenarioFiles();
        this.state.selectedFiles.batch = [];
        
        const batchInput = document.getElementById('batch-files');
        if (batchInput) batchInput.value = '';
        
        // Reset stats
        document.getElementById('total-modules').textContent = '0';
        document.getElementById('total-scenarios').textContent = '0';
        document.getElementById('success-rate').textContent = '0%';
    }
    
    getInputIdForType(fileType) {
        const mapping = {
            theory: 'theory-file',
            tests: 'tests-file',
            scenario: 'scenario-file',
            batch: 'batch-files'
        };
        return mapping[fileType];
    }
    
    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // === Методы для создания новых элементов ===

    setupCreateButtons() {
        // Кнопка создания категории
        const createPathBtn = document.getElementById('create-path-btn');
        if (createPathBtn) {
            createPathBtn.addEventListener('click', () => this.showCreateModal('path'));
        }

        // Кнопка создания предмета
        const createSubjectBtn = document.getElementById('create-subject-btn');
        if (createSubjectBtn) {
            createSubjectBtn.addEventListener('click', () => this.showCreateModal('subject'));
        }

        // Кнопка создания модуля
        const createModuleBtn = document.getElementById('create-module-btn');
        if (createModuleBtn) {
            createModuleBtn.addEventListener('click', () => this.showCreateModal('module'));
        }

        // Подтверждение создания
        document.getElementById('confirmCreatePath')?.addEventListener('click', () => this.createItem('path'));
        document.getElementById('confirmCreateSubject')?.addEventListener('click', () => this.createItem('subject'));
        document.getElementById('confirmCreateModule')?.addEventListener('click', () => this.createItem('module'));
    }

    showCreateModal(type) {
        const modalId = `create${type.charAt(0).toUpperCase() + type.slice(1)}Modal`;
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        
        // Очищаем форму
        const form = document.getElementById(`create${type.charAt(0).toUpperCase() + type.slice(1)}Form`);
        if (form) {
            form.reset();
        }
        
        modal.show();
    }

    async createItem(type) {
        try {
            let data = {};
            let endpoint = '';
            
            if (type === 'path') {
                data = {
                    name: document.getElementById('pathName').value.trim(),
                    description: document.getElementById('pathDescription').value.trim(),
                    icon: document.getElementById('pathIcon').value
                };
                endpoint = 'create-learning-path';
            } else if (type === 'subject') {
                const selectedPathId = document.getElementById('learning-path-select').value;
                if (!selectedPathId) {
                    this.notifications.show('Сначала выберите категорию', 'warning');
                    return;
                }
                
                data = {
                    name: document.getElementById('subjectName').value.trim(),
                    description: document.getElementById('subjectDescription').value.trim(),
                    learning_path_id: parseInt(selectedPathId),
                    icon: document.getElementById('subjectIcon').value
                };
                endpoint = 'create-subject';
            } else if (type === 'module') {
                const selectedSubjectId = document.getElementById('subject-select').value;
                if (!selectedSubjectId) {
                    this.notifications.show('Сначала выберите предмет', 'warning');
                    return;
                }
                
                data = {
                    title: document.getElementById('moduleTitle').value.trim(),
                    description: document.getElementById('moduleDescription').value.trim(),
                    subject_id: parseInt(selectedSubjectId),
                    module_type: document.getElementById('moduleType').value,
                    icon: document.getElementById('moduleIcon').value,
                    is_premium: document.getElementById('moduleIsPremium').checked
                };
                endpoint = 'create-module';
            }
            
            if (!data.name && !data.title) {
                this.notifications.show('Название обязательно для заполнения', 'warning');
                return;
            }
            
            // Отправляем запрос
            const response = await fetch(`${this.config.apiBaseUrl}/${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.notifications.show(result.message, 'success');
                
                // Закрываем модальное окно
                const modalId = `create${type.charAt(0).toUpperCase() + type.slice(1)}Modal`;
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                if (modal) {
                    modal.hide();
                }
                
                // Обновляем соответствующие селекторы
                await this.refreshSelectors(type, result.data);
                
            } else {
                this.notifications.show(result.message, 'error');
            }
            
        } catch (error) {
            console.error(`Error creating ${type}:`, error);
            this.notifications.show(`Ошибка создания: ${error.message}`, 'error');
        }
    }

    async refreshSelectors(type, newItemData) {
        if (type === 'path') {
            // Обновляем список категорий
            const pathSelect = document.getElementById('learning-path-select');
            const option = document.createElement('option');
            option.value = newItemData.id;
            option.textContent = newItemData.name;
            pathSelect.appendChild(option);
            
            // Автоматически выбираем созданную категорию
            pathSelect.value = newItemData.id;
            
            // Загружаем предметы для новой категории
            await this.loadSubjects(newItemData.id);
            
            // Активируем кнопку создания предмета
            document.getElementById('create-subject-btn').disabled = false;
            
        } else if (type === 'subject') {
            // Обновляем список предметов
            const subjectSelect = document.getElementById('subject-select');
            const option = document.createElement('option');
            option.value = newItemData.id;
            option.textContent = newItemData.name;
            subjectSelect.appendChild(option);
            
            // Автоматически выбираем созданный предмет
            subjectSelect.value = newItemData.id;
            
            // Загружаем модули для нового предмета
            await this.loadModules(newItemData.id);
            
            // Активируем кнопку создания модуля
            document.getElementById('create-module-btn').disabled = false;
            
        } else if (type === 'module') {
            // Обновляем список модулей
            const moduleSelect = document.getElementById('module-select');
            const option = document.createElement('option');
            option.value = newItemData.id;
            option.textContent = newItemData.title;
            moduleSelect.appendChild(option);
            
            // Автоматически выбираем созданный модуль
            moduleSelect.value = newItemData.id;
            
            // Проверяем готовность к загрузке
            this.checkUploadReadiness();
        }
    }
}

// Класс для управления уведомлениями
class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }
    
    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }
    
    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `uploader-toast ${type}`;
        
        const iconMap = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        
        notification.innerHTML = `
            <div class="toast-header">
                <div class="toast-icon">
                    <i class="bi ${iconMap[type]}"></i>
                </div>
                <div class="toast-title">${this.getTypeTitle(type)}</div>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="bi bi-x"></i>
                </button>
            </div>
            <div class="toast-body">${message.replace(/\n/g, '<br>')}</div>
        `;
        
        this.container.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Автоудаление
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    }
    
    getTypeTitle(type) {
        const titles = {
            success: 'Успех',
            error: 'Ошибка',
            warning: 'Предупреждение',
            info: 'Информация'
        };
        return titles[type] || 'Уведомление';
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    window.universalUploader = new UniversalContentUploader();
});

// Экспорт для модульных систем
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UniversalContentUploader, NotificationManager };
} 