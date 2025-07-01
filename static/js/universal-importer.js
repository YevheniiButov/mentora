/**
 * UniversalImporter - Универсальный импортер проектов
 * Поддерживает ZIP, GitHub, URL импорт с анализом структуры
 */

// Проверяем, не объявлен ли уже класс
if (typeof UniversalImporter === 'undefined') {
    class UniversalImporter {
        constructor() {
            this.supportedFormats = {
                zip: ['.zip'],
                github: ['github.com'],
                url: ['.html', '.htm', '.js', '.css', '.jsx', '.tsx', '.vue'],
                file: ['.html', '.htm', '.js', '.css', '.jsx', '.tsx', '.vue']
            };
            
            this.maxFileSize = 50 * 1024 * 1024; // 50MB
            this.apiBaseUrl = '/api/import-export';
            
            this.initializeEventListeners();
        }
        
        initializeEventListeners() {
            // Импорт ZIP
            const zipInput = document.getElementById('zip-import');
            if (zipInput) {
                zipInput.addEventListener('change', (e) => this.handleZipImport(e));
            }
            
            // Импорт GitHub
            const githubForm = document.getElementById('github-import-form');
            if (githubForm) {
                githubForm.addEventListener('submit', (e) => this.handleGitHubImport(e));
            }
            
            // Импорт URL
            const urlForm = document.getElementById('url-import-form');
            if (urlForm) {
                urlForm.addEventListener('submit', (e) => this.handleUrlImport(e));
            }
            
            // Drag & Drop для ZIP
            const dropZone = document.getElementById('drop-zone');
            if (dropZone) {
                dropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
                dropZone.addEventListener('drop', (e) => this.handleDrop(e));
            }
        }
        
        async handleZipImport(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                this.showLoading('Analyzing ZIP file...');
                
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch(`${this.apiBaseUrl}/upload-zip`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.displayAnalysis(result.analysis, 'ZIP Import');
                    this.showSuccess('ZIP file analyzed successfully!');
                } else {
                    this.showError(result.error || 'Failed to analyze ZIP file');
                }
                
            } catch (error) {
                console.error('ZIP import error:', error);
                this.showError('Failed to process ZIP file');
            } finally {
                this.hideLoading();
            }
        }
        
        async handleGitHubImport(event) {
            event.preventDefault();
            
            const form = event.target;
            const repoUrl = form.querySelector('input[name="repo_url"]').value;
            
            if (!repoUrl) {
                this.showError('Please enter a GitHub repository URL');
                return;
            }
            
            try {
                this.showLoading('Fetching repository from GitHub...');
                
                const response = await fetch(`${this.apiBaseUrl}/import-github`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ repo_url: repoUrl })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.displayAnalysis(result.analysis, 'GitHub Import');
                    this.showSuccess('Repository imported successfully!');
                } else {
                    this.showError(result.error || 'Failed to import from GitHub');
                }
                
            } catch (error) {
                console.error('GitHub import error:', error);
                this.showError('Failed to import from GitHub');
            } finally {
                this.hideLoading();
            }
        }
        
        async handleUrlImport(event) {
            event.preventDefault();
            
            const form = event.target;
            const url = form.querySelector('input[name="url"]').value;
            
            if (!url) {
                this.showError('Please enter a URL');
                return;
            }
            
            try {
                this.showLoading('Fetching content from URL...');
                
                const response = await fetch(`${this.apiBaseUrl}/import-url`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.displayAnalysis(result.analysis, 'URL Import');
                    this.showSuccess('Content imported successfully!');
                } else {
                    this.showError(result.error || 'Failed to import from URL');
                }
                
            } catch (error) {
                console.error('URL import error:', error);
                this.showError('Failed to import from URL');
            } finally {
                this.hideLoading();
            }
        }
        
        handleDragOver(event) {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'copy';
            event.target.classList.add('drag-over');
        }
        
        handleDrop(event) {
            event.preventDefault();
            event.target.classList.remove('drag-over');
            
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.toLowerCase().endsWith('.zip')) {
                    // Создаем временный input для обработки файла
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.files = files;
                    this.handleZipImport({ target: input });
                } else {
                    this.showError('Only ZIP files are supported for drag & drop');
                }
            }
        }
        
        displayAnalysis(analysis, source) {
            const modal = this.createAnalysisModal(analysis, source);
            document.body.appendChild(modal);
            
            // Анимация появления
            setTimeout(() => modal.classList.add('show'), 10);
            
            // Обработчик закрытия
            modal.addEventListener('click', (e) => {
                if (e.target === modal || e.target.classList.contains('close-btn')) {
                    modal.classList.remove('show');
                    setTimeout(() => document.body.removeChild(modal), 300);
                }
            });
        }
        
        createAnalysisModal(analysis, source) {
            const modal = document.createElement('div');
            modal.className = 'modal-overlay analysis-modal';
            modal.innerHTML = `
                <div class="modal-content" style="width: 80vw; height: 80vh;">
                    <div class="modal-header">
                        <h3 style="margin: 0;">📊 ${source} Analysis</h3>
                        <button class="close-btn">✕ Close</button>
                    </div>
                    <div class="modal-body">
                        <div class="analysis-grid">
                            <div class="analysis-section">
                                <h4>📁 Project Structure</h4>
                                <div class="structure-info">
                                    <p><strong>Framework:</strong> <span class="framework-badge ${analysis.framework}">${analysis.framework.toUpperCase()}</span></p>
                                    <p><strong>Total Files:</strong> ${analysis.total_files || analysis.files?.length || 0}</p>
                                    ${analysis.package_json ? `<p><strong>Package.json:</strong> ✅ Found</p>` : ''}
                                    ${analysis.readme ? `<p><strong>README:</strong> ✅ Found</p>` : ''}
                                </div>
                            </div>
                            
                            <div class="analysis-section">
                                <h4>📄 Main Files</h4>
                                <div class="file-list">
                                    ${(analysis.main_files || []).map(file => `
                                        <div class="file-item">
                                            <span class="file-icon">📄</span>
                                            <span class="file-name">${file}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            
                            <div class="analysis-section">
                                <h4>⚙️ Configuration Files</h4>
                                <div class="file-list">
                                    ${(analysis.config_files || []).map(file => `
                                        <div class="file-item">
                                            <span class="file-icon">⚙️</span>
                                            <span class="file-name">${file}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                            
                            ${analysis.components ? `
                            <div class="analysis-section">
                                <h4>🧩 Components</h4>
                                <div class="component-list">
                                    ${analysis.components.map(comp => `
                                        <span class="component-tag">${comp}</span>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${analysis.scripts ? `
                            <div class="analysis-section">
                                <h4>📜 Scripts</h4>
                                <div class="script-list">
                                    ${analysis.scripts.map(script => `
                                        <span class="script-tag">${script}</span>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                            
                            ${analysis.styles ? `
                            <div class="analysis-section">
                                <h4>🎨 Styles</h4>
                                <div class="style-list">
                                    ${analysis.styles.map(style => `
                                        <span class="style-tag">${style}</span>
                                    `).join('')}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        
                        <div class="analysis-actions">
                            <button class="btn btn-primary" onclick="universalImporter.importToEditor('${source.toLowerCase()}', ${JSON.stringify(analysis)})">
                                🚀 Import to Editor
                            </button>
                            <button class="btn btn-secondary" onclick="universalImporter.downloadAnalysis(${JSON.stringify(analysis)})">
                                📥 Download Analysis
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            return modal;
        }
        
        async importToEditor(source, analysis) {
            try {
                this.showLoading('Importing to editor...');
                
                // Здесь будет логика импорта в GrapesJS редактор
                if (window.editor && window.editor.loadProject) {
                    await window.editor.loadProject(analysis);
                    this.showSuccess('Project imported to editor successfully!');
                } else {
                    this.showError('Editor not ready for import');
                }
                
            } catch (error) {
                console.error('Import to editor error:', error);
                this.showError('Failed to import to editor');
            } finally {
                this.hideLoading();
            }
        }
        
        downloadAnalysis(analysis) {
            const dataStr = JSON.stringify(analysis, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `project-analysis-${new Date().toISOString().split('T')[0]}.json`;
            link.click();
            
            this.showSuccess('Analysis downloaded successfully!');
        }
        
        getCSRFToken() {
            return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        }
        
        showLoading(message) {
            const loading = document.getElementById('loading-overlay');
            if (loading) {
                loading.querySelector('h2').textContent = message;
                loading.style.display = 'flex';
            }
        }
        
        hideLoading() {
            const loading = document.getElementById('loading-overlay');
            if (loading) {
                loading.style.display = 'none';
            }
        }
        
        showSuccess(message) {
            this.showNotification(message, 'success');
        }
        
        showError(message) {
            this.showNotification(message, 'error');
        }
        
        showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon">${type === 'success' ? '✅' : '❌'}</span>
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
    }
    
    // Инициализация при загрузке страницы
    let universalImporter;
    document.addEventListener('DOMContentLoaded', () => {
        universalImporter = new UniversalImporter();
    });
    
    // Экспорт для использования в других модулях
    window.UniversalImporter = UniversalImporter;
} 