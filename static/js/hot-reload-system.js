/**
 * HotReloadSystem - Система Hot Module Replacement
 * Обеспечивает мгновенное обновление изменений через WebSocket
 */

// Проверяем, не объявлен ли уже класс
if (typeof HotReloadSystem === 'undefined') {
    class HotReloadSystem {
        constructor() {
            this.socket = null;
            this.isConnected = false;
            this.reconnectAttempts = 0;
            this.maxReconnectAttempts = 5;
            this.reconnectInterval = 2000;
            this.serverUrl = 'ws://127.0.0.1:8082/ws/hmr';
            this.eventListeners = new Map();
            
            this.initialize();
        }
        
        async initialize() {
            try {
                console.log('🔥 Initializing Hot Module Replacement system...');
                await this.connect();
                this.setupEventListeners();
                console.log('✅ HMR system initialized successfully');
            } catch (error) {
                console.warn('⚠️ HMR system initialization failed:', error);
            }
        }
        
        async connect() {
            return new Promise((resolve, reject) => {
                try {
                    console.log(`🔌 Connecting to HMR WebSocket: ${this.serverUrl}`);
                    this.socket = new WebSocket(this.serverUrl);
                    
                    this.socket.onopen = () => {
                        console.log('✅ HMR WebSocket connected');
                        this.isConnected = true;
                        this.reconnectAttempts = 0;
                        this.dispatchEvent('connected');
                        resolve();
                    };
                    
                    this.socket.onmessage = (event) => {
                        try {
                            const data = JSON.parse(event.data);
                            this.handleMessage(data);
                        } catch (error) {
                            console.error('❌ Failed to parse HMR message:', error);
                        }
                    };
                    
                    this.socket.onerror = (error) => {
                        console.error('❌ HMR WebSocket error:', error);
                        this.isConnected = false;
                        this.dispatchEvent('error', error);
                        reject(error);
                    };
                    
                    this.socket.onclose = () => {
                        console.log('🔌 HMR WebSocket disconnected');
                        this.isConnected = false;
                        this.dispatchEvent('disconnected');
                        this.scheduleReconnect();
                    };
                    
                } catch (error) {
                    console.error('❌ Failed to create WebSocket connection:', error);
                    reject(error);
                }
            });
        }
        
        scheduleReconnect() {
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                
                setTimeout(() => {
                    this.connect().catch(() => {
                        console.log(`❌ Reconnection failed: ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
                    });
                }, this.reconnectInterval);
            } else {
                console.log('❌ Max reconnection attempts reached');
            }
        }
        
        handleMessage(data) {
            const { type, payload } = data;
            
            switch (type) {
                case 'file_changed':
                    this.handleFileChange(payload);
                    break;
                case 'project_update':
                    this.handleProjectUpdate(payload);
                    break;
                case 'build_complete':
                    this.handleBuildComplete(payload);
                    break;
                case 'error':
                    this.handleError(payload);
                    break;
                default:
                    console.log('📨 Unknown HMR message type:', type);
            }
        }
        
        handleFileChange(fileInfo) {
            console.log('📝 File changed:', fileInfo.path);
            this.dispatchEvent('fileChanged', fileInfo);
            
            // Автоматическое обновление редактора
            if (window.editor && fileInfo.type === 'html') {
                // Обновляем только HTML компоненты
                this.updateEditorComponents(fileInfo.content);
            }
        }
        
        handleProjectUpdate(projectData) {
            console.log('📦 Project updated');
            this.dispatchEvent('projectUpdated', projectData);
            
            // Обновляем весь проект
            if (window.editor) {
                this.updateEditorProject(projectData);
            }
        }
        
        handleBuildComplete(buildInfo) {
            console.log('🔨 Build completed:', buildInfo);
            this.dispatchEvent('buildComplete', buildInfo);
            
            // Показываем уведомление о завершении сборки
            this.showNotification(`Build completed in ${buildInfo.duration}ms`, 'success');
        }
        
        handleError(error) {
            console.error('❌ HMR Error:', error);
            this.dispatchEvent('error', error);
            
            // Показываем уведомление об ошибке
            this.showNotification(`HMR Error: ${error.message}`, 'error');
        }
        
        updateEditorComponents(htmlContent) {
            try {
                if (window.editor && window.editor.setComponents) {
                    window.editor.setComponents(htmlContent);
                    console.log('✅ Editor components updated');
                }
            } catch (error) {
                console.error('❌ Failed to update editor components:', error);
            }
        }
        
        updateEditorProject(projectData) {
            try {
                if (window.editor) {
                    if (projectData.html && window.editor.setComponents) {
                        window.editor.setComponents(projectData.html);
                    }
                    if (projectData.css && window.editor.setStyle) {
                        window.editor.setStyle(projectData.css);
                    }
                    if (projectData.js && window.editor.setScript) {
                        window.editor.setScript(projectData.js);
                    }
                    console.log('✅ Editor project updated');
                }
            } catch (error) {
                console.error('❌ Failed to update editor project:', error);
            }
        }
        
        async sendUpdate(data) {
            if (!this.isConnected) {
                console.warn('⚠️ HMR not connected, cannot send update');
                return;
            }
            
            try {
                const message = {
                    type: 'project_update',
                    payload: {
                        timestamp: new Date().toISOString(),
                        data: data
                    }
                };
                
                this.socket.send(JSON.stringify(message));
                console.log('📤 HMR update sent');
            } catch (error) {
                console.error('❌ Failed to send HMR update:', error);
            }
        }
        
        async sendFileChange(filePath, content) {
            if (!this.isConnected) {
                console.warn('⚠️ HMR not connected, cannot send file change');
                return;
            }
            
            try {
                const message = {
                    type: 'file_changed',
                    payload: {
                        path: filePath,
                        content: content,
                        timestamp: new Date().toISOString()
                    }
                };
                
                this.socket.send(JSON.stringify(message));
                console.log('📤 File change sent:', filePath);
            } catch (error) {
                console.error('❌ Failed to send file change:', error);
            }
        }
        
        // Система событий
        on(event, callback) {
            if (!this.eventListeners.has(event)) {
                this.eventListeners.set(event, []);
            }
            this.eventListeners.get(event).push(callback);
        }
        
        off(event, callback) {
            if (this.eventListeners.has(event)) {
                const listeners = this.eventListeners.get(event);
                const index = listeners.indexOf(callback);
                if (index > -1) {
                    listeners.splice(index, 1);
                }
            }
        }
        
        dispatchEvent(event, data = null) {
            if (this.eventListeners.has(event)) {
                this.eventListeners.get(event).forEach(callback => {
                    try {
                        callback(data);
                    } catch (error) {
                        console.error(`❌ Error in event listener for ${event}:`, error);
                    }
                });
            }
        }
        
        // Утилиты
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
        
        // Публичные методы
        getStatus() {
            return {
                connected: this.isConnected,
                reconnectAttempts: this.reconnectAttempts,
                maxReconnectAttempts: this.maxReconnectAttempts,
                serverUrl: this.serverUrl
            };
        }
        
        disconnect() {
            if (this.socket) {
                this.socket.close();
            }
        }
    }
    
    // Экспорт в глобальный объект
    window.HotReloadSystem = HotReloadSystem;
} 