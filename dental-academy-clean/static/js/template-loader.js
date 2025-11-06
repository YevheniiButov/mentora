/**
 * Enhanced Template Loader
 * Улучшенная система загрузки и управления шаблонами
 */

class TemplateLoader {
    constructor(editor, options = {}) {
        this.editor = editor;
        this.options = {
            cacheEnabled: true,
            cacheTimeout: 5 * 60 * 1000, // 5 минут
            showPreview: true,
            autoSave: true,
            ...options
        };
        
        this.templates = [];
        this.templateCache = new Map();
        this.currentTemplate = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {

        // Создаем улучшенный UI
        this.createEnhancedUI();
        
        // Настраиваем обработчики событий
        this.setupEventListeners();

    }
    
    createEnhancedUI() {
        // Ищем уже существующую кнопку "Открыть проводник"
        const openFileExplorerBtn = document.getElementById('open-file-explorer');

        // Если кнопка не найдена, создаем её
        if (!openFileExplorerBtn) {

            // Ищем место для вставки кнопки
            const buttonContainer = document.querySelector('.d-flex.gap-2.align-items-center');
            if (buttonContainer) {
                const newButton = document.createElement('button');
                newButton.className = 'btn btn-outline-primary';
                newButton.id = 'open-file-explorer';
                newButton.title = 'Открыть проводник';
                newButton.innerHTML = '<i class="bi bi-folder2"></i> Открыть проводник';
                buttonContainer.appendChild(newButton);

            }
        }
    }
    
    setupEventListeners() {

        // Используем делегирование событий для кнопки открытия файлового проводника
        document.addEventListener('click', (e) => {
            if (e.target.id === 'open-file-explorer' || e.target.closest('#open-file-explorer')) {

                e.preventDefault();
                e.stopPropagation();
                
                // Открываем FileExplorer
                if (window.fileExplorer) {
                    window.fileExplorer.open();
                } else {
                    console.error('❌ FileExplorer instance not found');
                    alert('Файловый проводник не инициализирован. Обновите страницу.');
                }
            }
        });

    }
    
    enableButtons() {
        const buttons = ['undo-btn', 'redo-btn', 'preview-btn', 'save-btn'];
        buttons.forEach(btnId => {
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.disabled = false;
            }
        });
    }
    
    updateStatus(type, text) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            statusDot.className = `status-dot ${type}`;
            statusText.textContent = text;
        }
    }
    
    showNotification(message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
        `;
        document.body.appendChild(notification);
        
        // Автоудаление через 3 секунды
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
    
    getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || '';
    }
    
    getTemplateIcon(category) {
        const icons = {
            'core': 'file-earmark-text',
            'learning': 'book',
            'virtual_patient': 'person-heart',
            'tests': 'question-circle',
            'includes': 'code-slash'
        };
        return icons[category] || 'file-earmark';
    }
    
    getCategoryName(category) {
        const names = {
            'core': 'Основные',
            'learning': 'Обучение',
            'virtual_patient': 'Виртуальный пациент',
            'tests': 'Тесты',
            'includes': 'Включения'
        };
        return names[category] || category;
    }
    
    destroy() {

        // Уничтожаем FileExplorer если он существует
        if (window.fileExplorer) {
            window.fileExplorer.destroy();
            window.fileExplorer = null;
        }
    }
}

// Глобальный экземпляр
window.TemplateLoader = TemplateLoader;

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {

    let attempts = 0;
    const maxAttempts = 20; // Максимум 10 секунд (20 * 500ms)
    
    // Ждем инициализации редактора и FileExplorer
    const checkEditor = setInterval(() => {
        attempts++;
        
        // Проверяем только window.editor
        const editor = window.editor;
        const fileExplorer = typeof FileExplorer !== 'undefined';

        if (editor && editor.getComponents && fileExplorer) {
            clearInterval(checkEditor);
            
            // Создаем template loader
            window.templateLoader = new TemplateLoader(editor, {
                cacheEnabled: true,
                cacheTimeout: 5 * 60 * 1000,
                showPreview: true,
                autoSave: true
            });

        } else if (attempts >= maxAttempts) {
            clearInterval(checkEditor);
            console.error('❌ Template Loader failed to initialize: editor or FileExplorer not found after maximum attempts');
        }
    }, 500);
}); 