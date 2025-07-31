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
        console.log('🔧 Template Loader initializing...');
        console.log('🔧 Current language:', window.currentLang);
        
        // Создаем улучшенный UI
        this.createEnhancedUI();
        
        // Настраиваем обработчики событий
        this.setupEventListeners();
        
        console.log('✅ Template Loader initialized');
        console.log('🔧 Template selector after init:', document.querySelector('.template-selector'));
        console.log('🔧 Template dropdown after init:', document.getElementById('template-dropdown'));
    }
    
    createEnhancedUI() {
        // Ищем уже существующую кнопку "Открыть проводник"
        const openFileExplorerBtn = document.getElementById('open-file-explorer');
        console.log('🔧 Existing open file explorer button found:', openFileExplorerBtn);
        
        // Если кнопка не найдена, создаем её
        if (!openFileExplorerBtn) {
            console.log('🔧 Creating new file explorer button...');
            // Ищем место для вставки кнопки
            const buttonContainer = document.querySelector('.d-flex.gap-2.align-items-center');
            if (buttonContainer) {
                const newButton = document.createElement('button');
                newButton.className = 'btn btn-outline-primary';
                newButton.id = 'open-file-explorer';
                newButton.title = 'Открыть проводник';
                newButton.innerHTML = '<i class="bi bi-folder2"></i> Открыть проводник';
                buttonContainer.appendChild(newButton);
                console.log('✅ File explorer button created');
            }
        }
    }
    
    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Используем делегирование событий для кнопки открытия файлового проводника
        document.addEventListener('click', (e) => {
            if (e.target.id === 'open-file-explorer' || e.target.closest('#open-file-explorer')) {
                console.log('🔧 Opening File Explorer...');
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
        
        console.log('✅ Event listeners set up with delegation');
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
        console.log('🔧 Template Loader destroyed');
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
    console.log('🔧 DOM loaded, waiting for editor and FileExplorer...');
    
    let attempts = 0;
    const maxAttempts = 20; // Максимум 10 секунд (20 * 500ms)
    
    // Ждем инициализации редактора и FileExplorer
    const checkEditor = setInterval(() => {
        attempts++;
        
        // Проверяем только window.editor
        const editor = window.editor;
        const fileExplorer = typeof FileExplorer !== 'undefined';
        console.log(`🔧 Checking for editor and FileExplorer... (attempt ${attempts}/${maxAttempts})`, { editor: !!editor, fileExplorer });
        
        if (editor && editor.getComponents && fileExplorer) {
            clearInterval(checkEditor);
            
            // Создаем template loader
            window.templateLoader = new TemplateLoader(editor, {
                cacheEnabled: true,
                cacheTimeout: 5 * 60 * 1000,
                showPreview: true,
                autoSave: true
            });
            
            console.log('🔧 Template Loader auto-initialized');
        } else if (attempts >= maxAttempts) {
            clearInterval(checkEditor);
            console.error('❌ Template Loader failed to initialize: editor or FileExplorer not found after maximum attempts');
        }
    }, 500);
}); 