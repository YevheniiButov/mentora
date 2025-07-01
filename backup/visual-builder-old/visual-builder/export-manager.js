/**
 * Export Manager - Page Export System
 * Система экспорта страниц для Visual Builder
 */

export class ExportManager {
    constructor(visualBuilder) {
        this.vb = visualBuilder;
        this.exportFormats = {
            html: { name: 'HTML', icon: 'bi-file-code', mime: 'text/html' },
            pdf: { name: 'PDF', icon: 'bi-file-pdf', mime: 'application/pdf' },
            png: { name: 'PNG Image', icon: 'bi-file-image', mime: 'image/png' },
            jpg: { name: 'JPEG Image', icon: 'bi-file-image', mime: 'image/jpeg' },
            zip: { name: 'ZIP Archive', icon: 'bi-file-zip', mime: 'application/zip' }
        };
        this.exportSettings = {
            quality: 0.9,
            format: 'A4',
            margin: 20,
            includeCSS: true,
            includeJS: false,
            optimizeImages: true
        };
        
        this.init();
    }
    
    init() {
        this.loadExportSettings();
        console.info('📤 Export Manager готов');
    }
    
    loadExportSettings() {
        try {
            const saved = localStorage.getItem('vb-export-settings');
            if (saved) {
                this.exportSettings = { ...this.exportSettings, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.warn('Ошибка загрузки настроек экспорта:', error);
        }
    }
    
    saveExportSettings() {
        try {
            localStorage.setItem('vb-export-settings', JSON.stringify(this.exportSettings));
        } catch (error) {
            console.warn('Ошибка сохранения настроек экспорта:', error);
        }
    }
    
    // Основные методы экспорта
    async exportPage(format = 'html', options = {}) {
        try {
            this.vb.showNotification(`Начинаем экспорт в ${this.exportFormats[format].name}...`, 'info');
            
            const content = this.vb.getCanvasContent();
            const cleanContent = this.cleanContentForExport(content);
            
            switch (format) {
                case 'html':
                    return await this.exportToHTML(cleanContent, options);
                case 'pdf':
                    return await this.exportToPDF(cleanContent, options);
                case 'png':
                case 'jpg':
                    return await this.exportToImage(cleanContent, format, options);
                case 'zip':
                    return await this.exportToZIP(cleanContent, options);
                default:
                    throw new Error(`Неподдерживаемый формат: ${format}`);
            }
        } catch (error) {
            console.error('Ошибка экспорта:', error);
            this.vb.showNotification(`Ошибка экспорта: ${error.message}`, 'error');
            throw error;
        }
    }
    
    cleanContentForExport(content) {
        // Удаляем элементы редактирования
        let cleanContent = content
            .replace(/<div class="element-controls">[\s\S]*?<\/div>/g, '')
            .replace(/contenteditable="true"/g, '')
            .replace(/onclick="[^"]*"/g, '')
            .replace(/class="draggable-element[^"]*"/g, 'class="exported-element"')
            .replace(/data-[^=]*="[^"]*"/g, '');
        
        // Очищаем inline стили редактирования
        cleanContent = cleanContent.replace(/style="[^"]*position:\s*absolute[^"]*"/g, '');
        
        return cleanContent;
    }
    
    async exportToHTML(content, options = {}) {
        const settings = { ...this.exportSettings, ...options };
        
        const html = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${options.title || 'Экспортированная страница'} - Dental Academy</title>
    <meta name="description" content="${options.description || 'Страница, созданная в Visual Builder'}">
    <meta name="author" content="Dental Academy">
    <meta name="generator" content="Visual Builder v2.0">
    
    ${settings.includeCSS ? this.generateCSS() : ''}
    
    <style>
        /* Экспорт стили */
        .exported-element {
            margin: 1rem 0;
            border: none !important;
            background: transparent !important;
        }
        .element-content {
            padding: 1rem;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        video {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    ${content}
    
    ${settings.includeJS ? this.generateJS() : ''}
    
    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.875rem;">
        <p>Создано с помощью Visual Builder - Dental Academy</p>
        <p>Экспортировано: ${new Date().toLocaleString('ru-RU')}</p>
    </footer>
</body>
</html>`;

        const filename = `${options.filename || 'page'}.html`;
        this.downloadFile(html, filename, 'text/html');
        
        this.vb.showNotification('Страница экспортирована в HTML', 'success');
        return { success: true, filename, size: html.length };
    }
    
    async exportToPDF(content, options = {}) {
        const settings = { ...this.exportSettings, ...options };
        
        try {
            // Создаем временный контейнер для рендеринга
            const container = document.createElement('div');
            container.innerHTML = content;
            container.style.cssText = `
                position: absolute;
                left: -9999px;
                top: -9999px;
                width: 800px;
                background: white;
                padding: 20px;
                font-family: 'Inter', sans-serif;
            `;
            document.body.appendChild(container);
            
            // Используем html2canvas для рендеринга
            const canvas = await html2canvas(container, {
                scale: 2,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                width: 800,
                height: container.scrollHeight
            });
            
            document.body.removeChild(container);
            
            // Конвертируем в PDF
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: settings.format === 'A4' ? 'portrait' : 'landscape',
                unit: 'mm',
                format: settings.format
            });
            
            const imgData = canvas.toDataURL('image/png', settings.quality);
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
            
            pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
            
            const filename = `${options.filename || 'page'}.pdf`;
            pdf.save(filename);
            
            this.vb.showNotification('Страница экспортирована в PDF', 'success');
            return { success: true, filename, size: pdf.output('blob').size };
            
        } catch (error) {
            console.error('Ошибка экспорта в PDF:', error);
            throw new Error('Не удалось создать PDF. Убедитесь, что все изображения загружены.');
        }
    }
    
    async exportToImage(content, format, options = {}) {
        const settings = { ...this.exportSettings, ...options };
        
        try {
            // Создаем временный контейнер
            const container = document.createElement('div');
            container.innerHTML = content;
            container.style.cssText = `
                position: absolute;
                left: -9999px;
                top: -9999px;
                width: 1200px;
                background: white;
                padding: 40px;
                font-family: 'Inter', sans-serif;
            `;
            document.body.appendChild(container);
            
            // Рендерим в canvas
            const canvas = await html2canvas(container, {
                scale: 2,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                width: 1200,
                height: container.scrollHeight
            });
            
            document.body.removeChild(container);
            
            // Конвертируем в нужный формат
            const mimeType = format === 'jpg' ? 'image/jpeg' : 'image/png';
            const quality = format === 'jpg' ? settings.quality : 1;
            
            canvas.toBlob((blob) => {
                const filename = `${options.filename || 'page'}.${format}`;
                this.downloadBlob(blob, filename, mimeType);
            }, mimeType, quality);
            
            this.vb.showNotification(`Страница экспортирована в ${format.toUpperCase()}`, 'success');
            return { success: true, filename: `${options.filename || 'page'}.${format}` };
            
        } catch (error) {
            console.error('Ошибка экспорта в изображение:', error);
            throw new Error('Не удалось создать изображение');
        }
    }
    
    async exportToZIP(content, options = {}) {
        const settings = { ...this.exportSettings, ...options };
        
        try {
            // Создаем ZIP архив
            const JSZip = window.JSZip;
            const zip = new JSZip();
            
            // Добавляем HTML файл
            const html = await this.exportToHTML(content, { ...options, returnContent: true });
            zip.file('index.html', html);
            
            // Добавляем CSS
            if (settings.includeCSS) {
                zip.file('styles.css', this.generateCSS());
            }
            
            // Добавляем JS
            if (settings.includeJS) {
                zip.file('script.js', this.generateJS());
            }
            
            // Добавляем README
            const readme = this.generateReadme(options);
            zip.file('README.md', readme);
            
            // Генерируем и скачиваем архив
            const blob = await zip.generateAsync({ type: 'blob' });
            const filename = `${options.filename || 'page'}.zip`;
            this.downloadBlob(blob, filename, 'application/zip');
            
            this.vb.showNotification('Страница экспортирована в ZIP архив', 'success');
            return { success: true, filename, size: blob.size };
            
        } catch (error) {
            console.error('Ошибка экспорта в ZIP:', error);
            throw new Error('Не удалось создать ZIP архив');
        }
    }
    
    generateCSS() {
        return `
/* Dental Academy - Visual Builder Styles */
:root {
    --primary: #3ECDC1;
    --secondary: #6C5CE7;
    --success: #00D68F;
    --warning: #FFC107;
    --error: #FF3333;
    --text-primary: #333;
    --text-secondary: #666;
    --bg-primary: #fff;
    --bg-secondary: #f8f9fa;
    --border: #dee2e6;
}

* {
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background: var(--bg-primary);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.btn {
    display: inline-block;
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover {
    background: #2ba89e;
    transform: translateY(-1px);
}

.btn-secondary {
    background: var(--secondary);
    color: white;
}

.btn-secondary:hover {
    background: #5a4fcf;
    transform: translateY(-1px);
}

.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 2rem; }

.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }

.p-1 { padding: 0.5rem; }
.p-2 { padding: 1rem; }
.p-3 { padding: 1.5rem; }
.p-4 { padding: 2rem; }

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 0 15px;
    }
    
    .btn {
        padding: 10px 20px;
        font-size: 0.875rem;
    }
}
`;
    }
    
    generateJS() {
        return `
// Dental Academy - Visual Builder Scripts
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dental Academy page loaded');
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Form handling
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted:', this);
            // Add your form handling logic here
        });
    });
    
    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});
`;
    }
    
    generateReadme(options = {}) {
        return `# ${options.title || 'Экспортированная страница'}

Эта страница была создана с помощью Visual Builder - Dental Academy.

## Информация

- **Создано:** ${new Date().toLocaleString('ru-RU')}
- **Формат:** HTML/CSS/JS
- **Генератор:** Visual Builder v2.0

## Структура файлов

- \`index.html\` - Основная HTML страница
- \`styles.css\` - Стили CSS
- \`script.js\` - JavaScript код
- \`README.md\` - Этот файл

## Использование

1. Откройте \`index.html\` в веб-браузере
2. Все стили и скрипты подключены автоматически
3. Страница адаптивна и работает на всех устройствах

## Техническая поддержка

Для получения поддержки обращайтесь в Dental Academy.

---
*Создано с помощью Visual Builder*
`;
    }
    
    // Утилиты
    downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        this.downloadBlob(blob, filename, mimeType);
    }
    
    downloadBlob(blob, filename, mimeType) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }
    
    // UI методы
    openExportDialog() {
        this.createExportModal();
    }
    
    createExportModal() {
        const modal = document.createElement('div');
        modal.className = 'export-modal';
        modal.innerHTML = `
            <div class="export-content">
                <div class="export-header">
                    <h3>Экспорт страницы</h3>
                    <button class="close-btn" onclick="this.closest('.export-modal').remove()">×</button>
                </div>
                
                <div class="export-body">
                    <div class="export-formats">
                        <h4>Выберите формат экспорта:</h4>
                        <div class="format-grid">
                            ${Object.entries(this.exportFormats).map(([key, format]) => `
                                <div class="format-item" data-format="${key}">
                                    <div class="format-icon">
                                        <i class="${format.icon}"></i>
                                    </div>
                                    <div class="format-info">
                                        <div class="format-name">${format.name}</div>
                                        <div class="format-desc">${this.getFormatDescription(key)}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="export-options">
                        <h4>Настройки экспорта:</h4>
                        <div class="option-group">
                            <label>Название файла:</label>
                            <input type="text" class="filename-input" value="page" placeholder="Введите название файла">
                        </div>
                        <div class="option-group">
                            <label>Качество (для изображений):</label>
                            <input type="range" class="quality-slider" min="0.1" max="1" step="0.1" value="${this.exportSettings.quality}">
                            <span class="quality-value">${Math.round(this.exportSettings.quality * 100)}%</span>
                        </div>
                        <div class="option-group">
                            <label>Формат страницы (для PDF):</label>
                            <select class="format-select">
                                <option value="A4" ${this.exportSettings.format === 'A4' ? 'selected' : ''}>A4</option>
                                <option value="A3" ${this.exportSettings.format === 'A3' ? 'selected' : ''}>A3</option>
                                <option value="Letter" ${this.exportSettings.format === 'Letter' ? 'selected' : ''}>Letter</option>
                            </select>
                        </div>
                        <div class="option-group">
                            <label>
                                <input type="checkbox" class="include-css" ${this.exportSettings.includeCSS ? 'checked' : ''}>
                                Включить CSS стили
                            </label>
                        </div>
                        <div class="option-group">
                            <label>
                                <input type="checkbox" class="include-js" ${this.exportSettings.includeJS ? 'checked' : ''}>
                                Включить JavaScript
                            </label>
                        </div>
                    </div>
                </div>
                
                <div class="export-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.export-modal').remove()">Отмена</button>
                    <button class="btn btn-primary" onclick="exportManager.executeExport(this.closest('.export-modal'))">
                        <i class="bi bi-download"></i> Экспортировать
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Обработчики событий
        this.setupExportModalHandlers(modal);
    }
    
    setupExportModalHandlers(modal) {
        // Выбор формата
        modal.querySelectorAll('.format-item').forEach(item => {
            item.addEventListener('click', () => {
                modal.querySelectorAll('.format-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
            });
        });
        
        // Качество
        const qualitySlider = modal.querySelector('.quality-slider');
        const qualityValue = modal.querySelector('.quality-value');
        qualitySlider.addEventListener('input', (e) => {
            qualityValue.textContent = Math.round(e.target.value * 100) + '%';
        });
        
        // Настройки
        modal.querySelector('.include-css').addEventListener('change', (e) => {
            this.exportSettings.includeCSS = e.target.checked;
        });
        
        modal.querySelector('.include-js').addEventListener('change', (e) => {
            this.exportSettings.includeJS = e.target.checked;
        });
        
        modal.querySelector('.format-select').addEventListener('change', (e) => {
            this.exportSettings.format = e.target.value;
        });
        
        qualitySlider.addEventListener('change', (e) => {
            this.exportSettings.quality = parseFloat(e.target.value);
        });
    }
    
    async executeExport(modal) {
        const selectedFormat = modal.querySelector('.format-item.selected')?.dataset.format || 'html';
        const filename = modal.querySelector('.filename-input').value || 'page';
        const quality = parseFloat(modal.querySelector('.quality-slider').value);
        
        const options = {
            filename,
            quality,
            title: filename.charAt(0).toUpperCase() + filename.slice(1),
            description: `Страница ${filename}, созданная в Visual Builder`
        };
        
        // Сохраняем настройки
        this.saveExportSettings();
        
        // Закрываем модал
        modal.remove();
        
        // Выполняем экспорт
        try {
            await this.exportPage(selectedFormat, options);
        } catch (error) {
            console.error('Export failed:', error);
        }
    }
    
    getFormatDescription(format) {
        const descriptions = {
            html: 'Веб-страница с полной функциональностью',
            pdf: 'Документ для печати и архивирования',
            png: 'Изображение высокого качества',
            jpg: 'Сжатое изображение для веба',
            zip: 'Архив со всеми файлами'
        };
        return descriptions[format] || 'Экспорт страницы';
    }
    
    // Статистика экспорта
    getExportStats() {
        const stats = JSON.parse(localStorage.getItem('vb-export-stats') || '{}');
        return {
            totalExports: stats.totalExports || 0,
            byFormat: stats.byFormat || {},
            lastExport: stats.lastExport || null,
            mostUsedFormat: this.getMostUsedFormat(stats.byFormat)
        };
    }
    
    getMostUsedFormat(byFormat) {
        if (!byFormat || Object.keys(byFormat).length === 0) return 'html';
        
        return Object.entries(byFormat)
            .sort(([,a], [,b]) => b - a)[0][0];
    }
    
    updateExportStats(format) {
        try {
            const stats = JSON.parse(localStorage.getItem('vb-export-stats') || '{}');
            
            stats.totalExports = (stats.totalExports || 0) + 1;
            stats.byFormat = stats.byFormat || {};
            stats.byFormat[format] = (stats.byFormat[format] || 0) + 1;
            stats.lastExport = new Date().toISOString();
            
            localStorage.setItem('vb-export-stats', JSON.stringify(stats));
        } catch (error) {
            console.warn('Ошибка обновления статистики экспорта:', error);
        }
    }
}