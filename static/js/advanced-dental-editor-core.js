/**
 * Advanced Dental Editor Core - Основной модуль координации
 * Объединяет все компоненты: HMR, импорт/экспорт, Webpack, 3D модели
 */

class AdvancedDentalEditorCore {
    constructor() {
        this.version = '2.0.0';
        this.components = {};
        this.isInitialized = false;
        this.config = {
            hmr: {
                enabled: true,
                port: 5001,
                autoConnect: true
            },
            import: {
                maxFileSize: 50 * 1024 * 1024, // 50MB
                supportedFormats: ['zip', 'github', 'url', 'file']
            },
            webpack: {
                enabled: true,
                frameworks: ['react', 'vue', 'angular', 'vanilla']
            },
            models3d: {
                enabled: true,
                autoLoad: true
            }
        };
        
        this.initialize();
    }
    
    async initialize() {
        try {
            console.log('🚀 Initializing Advanced Dental Editor Core...');
            
            // Инициализируем компоненты
            await this.initializeComponents();
            
            // Настраиваем интеграции
            await this.setupIntegrations();
            
            // Запускаем автозагрузку
            await this.autoLoad();
            
            this.isInitialized = true;
            console.log('✅ Advanced Dental Editor Core initialized successfully');
            
            // Уведомляем о готовности
            this.dispatchEvent('core:ready', { version: this.version });
            
        } catch (error) {
            console.error('❌ Advanced Dental Editor Core initialization failed:', error);
            this.dispatchEvent('core:error', { error: error.message });
        }
    }
    
    async initializeComponents() {
        // Инициализируем HMR систему
        if (this.config.hmr.enabled) {
            try {
                this.components.hmr = new HotReloadSystem();
                await this.components.hmr.initialize();
                console.log('✅ HMR system initialized');
            } catch (error) {
                console.warn('⚠️ HMR system initialization failed:', error);
            }
        }
        
        // Инициализируем Universal Importer
        if (window.UniversalImporter) {
            this.components.importer = new UniversalImporter();
            console.log('✅ Universal Importer initialized');
        }
        
        // Инициализируем Webpack Integration
        if (window.WebpackIntegration) {
            this.components.webpack = new WebpackIntegration();
            console.log('✅ Webpack Integration initialized');
        }
        
        // Инициализируем 3D Model System
        if (this.config.models3d.enabled) {
            this.components.models3d = new ThreeDModelSystem();
            console.log('✅ 3D Model System initialized');
        }
    }
    
    async setupIntegrations() {
        // Интеграция с GrapesJS
        if (window.editor) {
            this.setupGrapesJSIntegration();
        }
        
        // Интеграция с Monaco Editor
        if (window.monaco) {
            this.setupMonacoIntegration();
        }
        
        // Интеграция с Three.js
        if (window.THREE) {
            this.setupThreeJSIntegration();
        }
    }
    
    setupGrapesJSIntegration() {
        const editor = window.editor;
        
        // Добавляем методы для работы с проектами
        editor.loadProject = async (projectData) => {
            try {
                console.log('📦 Loading project into GrapesJS...');
                
                // Загружаем HTML
                if (projectData.html) {
                    editor.setComponents(projectData.html);
                }
                
                // Загружаем CSS
                if (projectData.css) {
                    editor.setStyle(projectData.css);
                }
                
                // Загружаем JavaScript
                if (projectData.js) {
                    editor.setScript(projectData.js);
                }
                
                // Обновляем статус
                this.updateStatus('Project loaded successfully');
                
            } catch (error) {
                console.error('Failed to load project:', error);
                this.showError('Failed to load project');
            }
        };
        
        editor.getProjectData = () => {
            return {
                html: editor.getComponents(),
                css: editor.getStyle(),
                js: editor.getScript(),
                timestamp: new Date().toISOString()
            };
        };
        
        editor.saveProject = async () => {
            try {
                const projectData = editor.getProjectData();
                
                // Сохраняем в localStorage
                localStorage.setItem('dental-editor-project', JSON.stringify(projectData));
                
                // Отправляем в HMR если доступно
                if (this.components.hmr) {
                    await this.components.hmr.sendUpdate(projectData);
                }
                
                this.updateStatus('Project saved');
                
            } catch (error) {
                console.error('Failed to save project:', error);
                this.showError('Failed to save project');
            }
        };
        
        console.log('✅ GrapesJS integration setup completed');
    }
    
    setupMonacoIntegration() {
        // Настраиваем Monaco Editor для работы с проектами
        if (window.monaco && window.monaco.editor) {
            // Добавляем поддержку TypeScript для Angular проектов
            window.monaco.languages.typescript.typescriptDefaults.setDiagnosticsOptions({
                noSemanticValidation: false,
                noSyntaxValidation: false
            });
            
            // Добавляем поддержку JSX для React проектов
            window.monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
                noSemanticValidation: false,
                noSyntaxValidation: false
            });
            
            console.log('✅ Monaco Editor integration setup completed');
        }
    }
    
    setupThreeJSIntegration() {
        // Настраиваем Three.js для 3D моделей
        if (window.THREE && this.components.models3d) {
            this.components.models3d.setupThreeJS();
            console.log('✅ Three.js integration setup completed');
        }
    }
    
    async autoLoad() {
        // Автозагрузка последнего проекта
        const savedProject = localStorage.getItem('dental-editor-project');
        if (savedProject && window.editor) {
            try {
                const projectData = JSON.parse(savedProject);
                await window.editor.loadProject(projectData);
                console.log('✅ Auto-loaded previous project');
            } catch (error) {
                console.warn('⚠️ Failed to auto-load previous project:', error);
            }
        }
        
        // Автозагрузка 3D моделей
        if (this.config.models3d.autoLoad && this.components.models3d) {
            await this.components.models3d.loadDefaultModels();
        }
    }
    
    // Методы для работы с проектами
    async createProject(framework = 'vanilla', options = {}) {
        try {
            console.log(`🆕 Creating new ${framework} project...`);
            
            const projectData = this.generateProjectTemplate(framework, options);
            
            if (window.editor) {
                await window.editor.loadProject(projectData);
            }
            
            this.updateStatus(`New ${framework} project created`);
            this.dispatchEvent('project:created', { framework, options });
            
        } catch (error) {
            console.error('Failed to create project:', error);
            this.showError('Failed to create project');
        }
    }
    
    async exportProject(format = 'zip') {
        try {
            if (!window.editor) {
                throw new Error('Editor not available');
            }
            
            const projectData = window.editor.getProjectData();
            
            if (this.components.webpack) {
                await this.components.webpack.exportProject();
            } else {
                // Fallback экспорт
                this.downloadProjectData(projectData, format);
            }
            
        } catch (error) {
            console.error('Failed to export project:', error);
            this.showError('Failed to export project');
        }
    }
    
    async importProject(source, data) {
        try {
            console.log(`📥 Importing project from ${source}...`);
            
            if (window.editor) {
                await window.editor.loadProject(data);
            }
            
            this.updateStatus(`Project imported from ${source}`);
            this.dispatchEvent('project:imported', { source, data });
            
        } catch (error) {
            console.error('Failed to import project:', error);
            this.showError('Failed to import project');
        }
    }
    
    // Генераторы шаблонов проектов
    generateProjectTemplate(framework, options = {}) {
        const templates = {
            react: {
                html: '<div id="root"></div>',
                css: this.getDefaultStyles(),
                js: this.getReactTemplate(options)
            },
            vue: {
                html: '<div id="app"></div>',
                css: this.getDefaultStyles(),
                js: this.getVueTemplate(options)
            },
            angular: {
                html: '<app-root></app-root>',
                css: this.getDefaultStyles(),
                js: this.getAngularTemplate(options)
            },
            vanilla: {
                html: '<div id="app"></div>',
                css: this.getDefaultStyles(),
                js: this.getVanillaTemplate(options)
            }
        };
        
        return templates[framework] || templates.vanilla;
    }
    
    getDefaultStyles() {
        return `* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f5f5f5;
}

#app, #root {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

p {
  color: #7f8c8d;
  text-align: center;
}`;
    }
    
    getReactTemplate(options) {
        return `import React from 'react';
import ReactDOM from 'react-dom';

function App() {
  return (
    <div className="container">
      <h1>🦷 Dental React App</h1>
      <p>Welcome to your new React project!</p>
    </div>
  );
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);`;
    }
    
    getVueTemplate(options) {
        return `import { createApp } from 'vue';

const app = createApp({
  template: \`
    <div class="container">
      <h1>🦷 Dental Vue App</h1>
      <p>Welcome to your new Vue project!</p>
    </div>
  \`
});

app.mount('#app');`;
    }
    
    getAngularTemplate(options) {
        return `import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: \`
    <div class="container">
      <h1>🦷 Dental Angular App</h1>
      <p>Welcome to your new Angular project!</p>
    </div>
  \`
})
export class AppComponent {
  title = 'dental-angular-app';
}`;
    }
    
    getVanillaTemplate(options) {
        return `document.addEventListener('DOMContentLoaded', () => {
  const app = document.getElementById('app');
  if (app) {
    app.innerHTML = \`
      <div class="container">
        <h1>🦷 Dental Vanilla App</h1>
        <p>Welcome to your new Vanilla JS project!</p>
      </div>
    \`;
  }
});`;
    }
    
    // Утилиты
    downloadProjectData(projectData, format) {
        const dataStr = JSON.stringify(projectData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `dental-project-${new Date().toISOString().split('T')[0]}.${format}`;
        link.click();
        
        URL.revokeObjectURL(link.href);
    }
    
    updateStatus(message) {
        const statusElement = document.getElementById('save-status');
        if (statusElement) {
            statusElement.textContent = message;
        }
        
        // Показываем уведомление
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    // Система событий
    dispatchEvent(eventName, data = {}) {
        const event = new CustomEvent(eventName, {
            detail: {
                timestamp: new Date().toISOString(),
                ...data
            }
        });
        document.dispatchEvent(event);
    }
    
    // Получение статуса системы
    getStatus() {
        return {
            version: this.version,
            initialized: this.isInitialized,
            components: Object.keys(this.components),
            config: this.config
        };
    }
}

// Система 3D моделей
class ThreeDModelSystem {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.models = new Map();
        this.isInitialized = false;
    }
    
    async initialize() {
        if (!window.THREE) {
            throw new Error('Three.js not available');
        }
        
        this.setupThreeJS();
        await this.loadDefaultModels();
        this.isInitialized = true;
    }
    
    setupThreeJS() {
        // Базовая настройка Three.js
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0xf0f0f0);
    }
    
    async loadDefaultModels() {
        // Загружаем базовые 3D модели зубов
        const defaultModels = [
            { name: 'tooth-1', geometry: 'sphere', color: 0xffffff },
            { name: 'tooth-2', geometry: 'cylinder', color: 0xf0f0f0 },
            { name: 'upper-jaw', geometry: 'box', color: 0xe0e0e0 },
            { name: 'lower-jaw', geometry: 'box', color: 0xe0e0e0 }
        ];
        
        for (const model of defaultModels) {
            await this.createModel(model);
        }
    }
    
    async createModel(modelData) {
        let geometry;
        
        switch (modelData.geometry) {
            case 'sphere':
                geometry = new THREE.SphereGeometry(1, 32, 32);
                break;
            case 'cylinder':
                geometry = new THREE.CylinderGeometry(0.5, 0.5, 2, 32);
                break;
            case 'box':
                geometry = new THREE.BoxGeometry(2, 1, 1);
                break;
            default:
                geometry = new THREE.SphereGeometry(1, 32, 32);
        }
        
        const material = new THREE.MeshPhongMaterial({ color: modelData.color });
        const mesh = new THREE.Mesh(geometry, material);
        
        this.models.set(modelData.name, mesh);
        this.scene.add(mesh);
    }
    
    getModel(name) {
        return this.models.get(name);
    }
    
    addToScene(modelName, position = { x: 0, y: 0, z: 0 }) {
        const model = this.getModel(modelName);
        if (model) {
            model.position.set(position.x, position.y, position.z);
            return model;
        }
        return null;
    }
}

// Инициализация при загрузке страницы
let advancedEditorCore;
document.addEventListener('DOMContentLoaded', () => {
    advancedEditorCore = new AdvancedDentalEditorCore();
});

// Экспорт для использования в других модулях
window.AdvancedDentalEditorCore = AdvancedDentalEditorCore;
window.ThreeDModelSystem = ThreeDModelSystem; 