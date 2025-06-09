/**
 * Мобильные настройки - JavaScript
 * Управление функциональностью страницы настроек
 */

class MobileSettings {
    constructor(config) {
        this.config = config;
        this.currentSettings = {};
        this.isLoading = false;
        this.isDirty = false; // Есть ли несохраненные изменения
        this.hasErrors = false; // Есть ли ошибки
        this.errorCount = 0; // Счетчик ошибок подряд
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSettings();
        this.setupThemeDetection();
        this.setupAutoSave();
    }
    
    /**
     * Привязка событий
     */
    bindEvents() {
        // Форма настроек
        const form = document.getElementById('settingsForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
            
            // Отслеживание изменений
            form.addEventListener('change', () => {
                this.markDirty();
                this.validateForm();
            });
            
            form.addEventListener('input', () => {
                this.markDirty();
                this.updateRangeDisplay();
            });
        }
        
        // Переключение языка - мгновенное применение
        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
        
        // Переключение темы - мгновенное применение
        const themeSelect = document.getElementById('theme');
        if (themeSelect) {
            themeSelect.addEventListener('change', (e) => {
                this.applyTheme(e.target.value);
            });
        }
        
        // Размер шрифта - мгновенное применение
        const fontSizeSelect = document.getElementById('fontSize');
        if (fontSizeSelect) {
            fontSizeSelect.addEventListener('change', (e) => {
                this.applyFontSize(e.target.value);
            });
        }
        
        // Предупреждение при попытке покинуть страницу с несохраненными изменениями
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }
    
    /**
     * Загрузка настроек с сервера
     */
    async loadSettings() {
        try {
            this.showLoading(true);
            
            const response = await fetch(this.config.apiEndpoint);
            const data = await response.json();
            
            if (data.success) {
                this.currentSettings = data.settings;
                this.populateForm(data.settings);
                this.applyTheme(data.settings.theme);
                this.applyFontSize(data.settings.font_size);
            } else {
                console.error('Failed to load settings:', data.error);
                this.showNotification('error', 'Ошибка загрузки настроек');
                this.loadDefaultSettings();
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showNotification('error', 'Ошибка подключения к серверу');
            this.loadDefaultSettings();
        } finally {
            this.showLoading(false);
            this.showForm();
        }
    }
    
    /**
     * Загрузка настроек по умолчанию
     */
    loadDefaultSettings() {
        const defaultSettings = {
            theme: 'auto',
            font_size: 'medium',
            language: this.config.lang || 'en',
            ai_suggestions: true,
            personalized_learning: true,
            push_notifications: true,
            daily_reminders: true,
            reminder_time: '09:00',
            progress_notifications: true,
            auto_play_videos: false,
            offline_mode: false,
            daily_goal: 3,
            content_difficulty: 'intermediate',
            analytics_enabled: true,
            data_sharing: false
        };
        
        this.currentSettings = defaultSettings;
        this.populateForm(defaultSettings);
    }
    
    /**
     * Заполнение формы данными
     */
    populateForm(settings) {
        // Текстовые поля и селекты
        const fields = [
            'theme', 'font_size', 'language', 'reminder_time', 
            'daily_goal', 'content_difficulty'
        ];
        
        fields.forEach(field => {
            const element = document.getElementById(this.toCamelCase(field));
            if (element && settings[field] !== undefined) {
                element.value = settings[field];
            }
        });
        
        // Чекбоксы
        const checkboxes = [
            'ai_suggestions', 'personalized_learning', 'push_notifications',
            'daily_reminders', 'progress_notifications', 'auto_play_videos',
            'offline_mode', 'analytics_enabled', 'data_sharing'
        ];
        
        checkboxes.forEach(field => {
            const element = document.getElementById(this.toCamelCase(field));
            if (element && settings[field] !== undefined) {
                element.checked = settings[field];
            }
        });
        
        // Обновление отображения слайдера
        this.updateRangeDisplay();
        
        // Сброс флага изменений
        this.isDirty = false;
    }
    
    /**
     * Сохранение настроек
     */
    async saveSettings() {
        if (this.isLoading) return;
        
        try {
            this.isLoading = true;
            const saveButton = document.getElementById('saveButton');
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.innerHTML = '<i class="bi bi-hourglass"></i> Сохранение...';
            }
            
            const formData = this.getFormData();
            
            // Сохраняем основные настройки
            const response = await fetch(this.config.saveEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            // Проверяем статус ответа
            if (!response.ok) {
                console.error('HTTP Error:', response.status, response.statusText);
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('success', 'Настройки сохранены');
                this.currentSettings = { ...this.currentSettings, ...formData };
                this.isDirty = false;
                this.hasErrors = false;
                this.errorCount = 0; // Сбрасываем счетчик ошибок при успехе
                
                // Убираем пульсацию с кнопки сохранения
                const saveBtn = document.getElementById('saveButton');
                if (saveBtn) {
                    saveBtn.classList.remove('pulse');
                }
                
                // Сохраняем OpenAI ключ отдельно, если он изменился
                await this.saveOpenAIKey();
                
            } else {
                this.hasErrors = true;
                this.errorCount++;
                this.showNotification('error', data.error || 'Ошибка сохранения');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.hasErrors = true;
            this.errorCount++;
            
            // Более детальная обработка ошибок
            if (error.message.includes('Failed to fetch')) {
                this.showNotification('error', 'Ошибка подключения к серверу. Проверьте интернет соединение.');
            } else if (error.message.includes('HTTP 4')) {
                this.showNotification('error', 'Ошибка авторизации. Пожалуйста, перезайдите в систему.');
            } else if (error.message.includes('HTTP 5')) {
                this.showNotification('error', 'Ошибка сервера. Попробуйте позже.');
            } else {
                this.showNotification('error', 'Произошла ошибка при сохранении настроек');
            }
        } finally {
            this.isLoading = false;
            const saveButton = document.getElementById('saveButton');
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.innerHTML = '<i class="bi bi-check-lg"></i> Сохранить изменения';
            }
        }
    }
    
    /**
     * Сохранение OpenAI ключа
     */
    async saveOpenAIKey() {
        const openaiKeyField = document.getElementById('openaiKey');
        if (!openaiKeyField || !openaiKeyField.value.trim()) return;
        
        try {
            const response = await fetch(this.config.openaiKeyEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: openaiKeyField.value.trim()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('OpenAI key saved successfully');
            } else {
                this.showNotification('warning', 'Проблема с сохранением OpenAI ключа');
            }
        } catch (error) {
            console.error('Error saving OpenAI key:', error);
        }
    }
    
    /**
     * Получение данных формы
     */
    getFormData() {
        const formData = {};
        
        // Текстовые поля и селекты
        const fields = [
            'theme', 'fontSize', 'language', 'reminderTime', 
            'dailyGoal', 'contentDifficulty'
        ];
        
        fields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                const key = this.toSnakeCase(fieldId);
                formData[key] = element.value;
            }
        });
        
        // Чекбоксы
        const checkboxes = [
            'aiSuggestions', 'personalizedLearning', 'pushNotifications',
            'dailyReminders', 'progressNotifications', 'autoPlayVideos',
            'offlineMode', 'analyticsEnabled', 'dataSharing'
        ];
        
        checkboxes.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                const key = this.toSnakeCase(fieldId);
                formData[key] = element.checked;
            }
        });
        
        return formData;
    }
    
    /**
     * Применение темы
     */
    applyTheme(theme) {
        const body = document.body;
        
        if (theme === 'dark') {
            body.setAttribute('data-theme', 'dark');
        } else if (theme === 'light') {
            body.setAttribute('data-theme', 'light');
        } else {
            // Автоматическая тема
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        }
        
        // Сохраняем в localStorage для быстрого применения
        localStorage.setItem('theme', theme);
    }
    
    /**
     * Применение размера шрифта
     */
    applyFontSize(fontSize) {
        const body = document.body;
        
        // Удаляем предыдущие классы размера шрифта
        body.classList.remove('font-small', 'font-medium', 'font-large');
        
        // Добавляем новый класс
        body.classList.add(`font-${fontSize}`);
        
        // Сохраняем в localStorage
        localStorage.setItem('fontSize', fontSize);
    }
    
    /**
     * Изменение языка
     */
    changeLanguage(language) {
        // Перенаправляем на ту же страницу с новым языком
        const currentPath = window.location.pathname;
        const pathParts = currentPath.split('/');
        
        // Заменяем язык в URL
        if (pathParts.length > 1) {
            pathParts[1] = language;
            const newPath = pathParts.join('/');
            window.location.href = newPath;
        }
    }
    
    /**
     * Настройка автоматического определения темы
     */
    setupThemeDetection() {
        // Слушаем изменения предпочтений системы
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener(() => {
            const themeSelect = document.getElementById('theme');
            if (themeSelect && themeSelect.value === 'auto') {
                this.applyTheme('auto');
            }
        });
    }
    
    /**
     * Настройка автосохранения
     */
    setupAutoSave() {
        // Автосохранение каждые 30 секунд, если есть изменения и нет ошибок
        setInterval(() => {
            if (this.isDirty && !this.isLoading && !this.hasErrors && this.errorCount < 3) {
                console.log('Auto-saving settings...');
                this.saveSettings();
            } else if (this.errorCount >= 3) {
                console.log('Auto-save disabled due to repeated errors');
            }
        }, 30000);
    }
    
    /**
     * Обновление отображения слайдера
     */
    updateRangeDisplay() {
        const dailyGoalSlider = document.getElementById('dailyGoal');
        const dailyGoalValue = document.getElementById('dailyGoalValue');
        
        if (dailyGoalSlider && dailyGoalValue) {
            dailyGoalValue.textContent = dailyGoalSlider.value;
        }
    }
    
    /**
     * Валидация формы
     */
    validateForm() {
        let isValid = true;
        const errors = [];
        
        // Валидация времени напоминаний
        const reminderTime = document.getElementById('reminderTime');
        if (reminderTime && reminderTime.value) {
            const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
            if (!timeRegex.test(reminderTime.value)) {
                errors.push('Неверный формат времени');
                isValid = false;
            }
        }
        
        // Валидация OpenAI ключа
        const openaiKey = document.getElementById('openaiKey');
        if (openaiKey && openaiKey.value.trim()) {
            if (!openaiKey.value.startsWith('sk-') || openaiKey.value.length < 20) {
                errors.push('Неверный формат OpenAI API ключа');
                isValid = false;
            }
        }
        
        // Показываем ошибки
        if (errors.length > 0) {
            this.showNotification('warning', errors.join(', '));
        }
        
        return isValid;
    }
    
    /**
     * Отметка о наличии несохраненных изменений
     */
    markDirty() {
        this.isDirty = true;
        
        // Визуальная индикация
        const saveButton = document.getElementById('saveButton');
        if (saveButton && !saveButton.classList.contains('pulse')) {
            saveButton.classList.add('pulse');
        }
    }
    
    /**
     * Показ/скрытие индикатора загрузки
     */
    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
    }
    
    /**
     * Показ/скрытие формы
     */
    showForm() {
        const form = document.getElementById('settingsForm');
        if (form) {
            form.style.display = 'block';
        }
    }
    
    /**
     * Показ уведомления
     */
    showNotification(type, message) {
        const notification = document.getElementById('notification');
        const icon = notification.querySelector('.notification-icon');
        const text = notification.querySelector('.notification-text');
        
        // Удаляем предыдущие классы типов
        notification.classList.remove('success', 'warning', 'error');
        
        // Добавляем новый тип
        notification.classList.add(type);
        
        // Устанавливаем иконку
        const icons = {
            success: 'bi-check-circle',
            warning: 'bi-exclamation-triangle',
            error: 'bi-x-circle'
        };
        
        icon.className = `notification-icon bi ${icons[type] || 'bi-info-circle'}`;
        text.textContent = message;
        
        // Показываем уведомление
        notification.style.display = 'block';
        
        // Автоматически скрываем через 4 секунды
        setTimeout(() => {
            notification.style.display = 'none';
        }, 4000);
    }
    
    /**
     * Утилиты для преобразования имен
     */
    toCamelCase(str) {
        return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
    }
    
    toSnakeCase(str) {
        return str.replace(/([A-Z])/g, '_$1').toLowerCase();
    }
}

/**
 * Глобальные функции для HTML
 */

// Переключение видимости пароля
function togglePasswordVisibility(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + 'Icon');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

// Сброс к настройкам по умолчанию
async function resetToDefaults() {
    if (!confirm('Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?')) {
        return;
    }
    
    try {
        const response = await fetch(window.settingsManager.config.resetEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.settingsManager.showNotification('success', 'Настройки сброшены');
            window.location.reload();
        } else {
            window.settingsManager.showNotification('error', data.error || 'Ошибка сброса настроек');
        }
    } catch (error) {
        console.error('Error resetting settings:', error);
        window.settingsManager.showNotification('error', 'Ошибка подключения к серверу');
    }
}

// Очистка кэша
async function clearCache() {
    if (!confirm('Очистить кэш приложения? Это может помочь освободить место на устройстве.')) {
        return;
    }
    
    try {
        const response = await fetch(window.settingsManager.config.clearCacheEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.settingsManager.showNotification('success', 'Кэш очищен');
        } else {
            window.settingsManager.showNotification('error', data.error || 'Ошибка очистки кэша');
        }
    } catch (error) {
        console.error('Error clearing cache:', error);
        window.settingsManager.showNotification('error', 'Ошибка подключения к серверу');
    }
}

// Показ модального окна экспорта данных
function showDataExportModal() {
    const modal = document.getElementById('dataExportModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

// Скрытие модального окна экспорта данных
function hideDataExportModal() {
    const modal = document.getElementById('dataExportModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Экспорт пользовательских данных
function exportUserData() {
    window.settingsManager.showNotification('info', 'Функция экспорта данных будет доступна в следующем обновлении');
    hideDataExportModal();
}

// Подтверждение удаления аккаунта
function confirmDeleteAccount() {
    const confirmText = prompt('Для подтверждения удаления аккаунта введите "DELETE":');
    
    if (confirmText === 'DELETE') {
        window.settingsManager.showNotification('info', 'Функция удаления аккаунта будет доступна в следующем обновлении');
    }
    
    hideDataExportModal();
}

// Применение сохраненной темы при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const savedFontSize = localStorage.getItem('fontSize');
    
    if (savedTheme) {
        const body = document.body;
        if (savedTheme === 'dark') {
            body.setAttribute('data-theme', 'dark');
        } else if (savedTheme === 'light') {
            body.setAttribute('data-theme', 'light');
        } else {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            body.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
        }
    }
    
    if (savedFontSize) {
        document.body.classList.add(`font-${savedFontSize}`);
    }
});

// Стили для пульсации кнопки сохранения
const style = document.createElement('style');
style.textContent = `
    .action-button.pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
        }
    }
    
    /* Классы размеров шрифта */
    .font-small {
        font-size: 14px;
    }
    
    .font-medium {
        font-size: 16px;
    }
    
    .font-large {
        font-size: 18px;
    }
`;
document.head.appendChild(style); 