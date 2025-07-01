/**
 * HTML Parser для Visual Builder
 * Конвертация HTML файлов в редактируемые элементы
 */

class HTMLParser {
    constructor(visualBuilder) {
        this.visualBuilder = visualBuilder;
        this.parsedElements = [];
        this.currentFile = null;
        
        // Настройки парсинга
        this.config = {
            preserveComments: true,
            preserveWhitespace: false,
            autoWrapText: true,
            convertInlineStyles: true,
            extractImages: true,
            extractLinks: true
        };
        
        // Маппинг HTML тегов на компоненты Visual Builder
        this.tagMapping = {
            'h1': 'heading',
            'h2': 'heading', 
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'p': 'text',
            'div': 'container',
            'span': 'text',
            'img': 'image',
            'video': 'video',
            'audio': 'audio',
            'iframe': 'video',
            'button': 'button',
            'a': 'button',
            'form': 'form',
            'input': 'form',
            'textarea': 'form',
            'select': 'form',
            'table': 'table',
            'ul': 'container',
            'ol': 'container',
            'li': 'text',
            'blockquote': 'text',
            'code': 'code',
            'pre': 'code',
            'hr': 'divider',
            'br': 'text'
        };
        
        console.info('🔍 HTML Parser инициализирован');
    }

    /**
     * Парсинг HTML контента в редактируемые элементы
     */
    parseHTMLToElements(htmlContent, filename = '') {
        try {
            this.currentFile = filename;
            this.parsedElements = [];
            
            // Создаем DOM парсер
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlContent, 'text/html');
            
            // Извлекаем body контент
            const bodyContent = doc.body || doc.documentElement;
            
            // Конвертируем в редактируемые элементы
            const elements = this.convertToEditableElements(bodyContent);
            
            console.info(`✅ HTML файл "${filename}" успешно распарсен: ${elements.length} элементов`);
            return elements;
            
        } catch (error) {
            console.error('❌ Ошибка парсинга HTML:', error);
            this.visualBuilder.showNotification('Ошибка парсинга HTML файла', 'error');
            return [];
        }
    }

    /**
     * Конвертация HTML элементов в редактируемые элементы
     */
    convertToEditableElements(element, parentElement = null) {
        const elements = [];
        
        // Обрабатываем текущий элемент
        if (this.shouldConvertElement(element)) {
            const editableElement = this.createEditableElement(element);
            if (editableElement) {
                elements.push(editableElement);
            }
        }
        
        // Рекурсивно обрабатываем дочерние элементы
        const children = Array.from(element.children);
        children.forEach(child => {
            const childElements = this.convertToEditableElements(child, element);
            elements.push(...childElements);
        });
        
        // Обрабатываем текстовые узлы
        if (this.config.autoWrapText && element.childNodes.length > 0) {
            const textElements = this.processTextNodes(element);
            elements.push(...textElements);
        }
        
        return elements;
    }

    /**
     * Проверка, нужно ли конвертировать элемент
     */
    shouldConvertElement(element) {
        // Пропускаем скрипты и стили
        if (['script', 'style', 'meta', 'link', 'title'].includes(element.tagName.toLowerCase())) {
            return false;
        }
        
        // Пропускаем пустые элементы
        if (element.textContent.trim() === '' && !element.hasAttribute('src') && !element.hasAttribute('href')) {
            return false;
        }
        
        return true;
    }

    /**
     * Создание редактируемого элемента
     */
    createEditableElement(element) {
        const tagName = element.tagName.toLowerCase();
        const componentType = this.tagMapping[tagName] || 'text';
        
        // Создаем элемент Visual Builder
        const editableElement = document.createElement('div');
        editableElement.className = `draggable-element element-${componentType}`;
        editableElement.dataset.type = componentType;
        editableElement.dataset.id = `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        editableElement.dataset.originalTag = tagName;
        
        // Копируем атрибуты
        this.copyAttributes(element, editableElement);
        
        // Создаем контент элемента
        const content = this.createElementContent(element, componentType);
        editableElement.innerHTML = content;
        
        // Добавляем элементы управления
        editableElement.appendChild(this.getControlsTemplate());
        
        // Настраиваем обработчики событий
        this.setupElementEvents(editableElement);
        
        return editableElement;
    }

    /**
     * Копирование атрибутов элемента
     */
    copyAttributes(sourceElement, targetElement) {
        const attributes = sourceElement.attributes;
        for (let i = 0; i < attributes.length; i++) {
            const attr = attributes[i];
            
            // Пропускаем некоторые атрибуты
            if (['id', 'class'].includes(attr.name)) continue;
            
            // Копируем стили
            if (attr.name === 'style' && this.config.convertInlineStyles) {
                this.convertInlineStyles(attr.value, targetElement);
            } else {
                targetElement.setAttribute(attr.name, attr.value);
            }
        }
    }

    /**
     * Конвертация inline стилей
     */
    convertInlineStyles(styleString, element) {
        const styles = {};
        const stylePairs = styleString.split(';');
        
        stylePairs.forEach(pair => {
            const [property, value] = pair.split(':').map(s => s.trim());
            if (property && value) {
                styles[property] = value;
            }
        });
        
        // Применяем стили к элементу
        Object.assign(element.style, styles);
    }

    /**
     * Создание контента элемента
     */
    createElementContent(element, componentType) {
        const tagName = element.tagName.toLowerCase();
        
        switch (componentType) {
            case 'heading':
                return this.createHeadingContent(element);
            case 'text':
                return this.createTextContent(element);
            case 'image':
                return this.createImageContent(element);
            case 'video':
                return this.createVideoContent(element);
            case 'button':
                return this.createButtonContent(element);
            case 'form':
                return this.createFormContent(element);
            case 'container':
                return this.createContainerContent(element);
            case 'code':
                return this.createCodeContent(element);
            case 'divider':
                return this.createDividerContent(element);
            default:
                return this.createTextContent(element);
        }
    }

    /**
     * Создание контента заголовка
     */
    createHeadingContent(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        
        return `
            <div class="element-content">
                <${tagName} contenteditable="true" style="margin: 0; padding: 0;">
                    ${text || 'Заголовок'}
                </${tagName}>
            </div>
        `;
    }

    /**
     * Создание текстового контента
     */
    createTextContent(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        
        // Если это параграф или span с текстом
        if (['p', 'span', 'div'].includes(tagName) && text) {
            return `
                <div class="element-content">
                    <${tagName} contenteditable="true" style="margin: 0; padding: 0;">
                        ${text}
                    </${tagName}>
                </div>
            `;
        }
        
        // Для других элементов
        return `
            <div class="element-content">
                <div contenteditable="true">
                    ${element.innerHTML || 'Текст'}
                </div>
            </div>
        `;
    }

    /**
     * Создание контента изображения
     */
    createImageContent(element) {
        const src = element.getAttribute('src') || '';
        const alt = element.getAttribute('alt') || '';
        
        if (src) {
            return `
                <div class="element-content">
                    <img src="${src}" alt="${alt}" style="max-width: 100%; height: auto; border-radius: 8px;">
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <div class="image-placeholder" onclick="visualBuilder.selectImage(this)">
                        <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer;">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">📷</div>
                            <div>Нажмите для добавления изображения</div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Создание контента видео
     */
    createVideoContent(element) {
        const tagName = element.tagName.toLowerCase();
        
        if (tagName === 'iframe') {
            const src = element.getAttribute('src') || '';
            return `
                <div class="element-content">
                    <iframe src="${src}" width="100%" height="315" frameborder="0" allowfullscreen style="border-radius: 8px;"></iframe>
                </div>
            `;
        } else if (tagName === 'video') {
            const src = element.getAttribute('src') || '';
            return `
                <div class="element-content">
                    <video controls width="100%" style="border-radius: 8px;">
                        <source src="${src}" type="video/mp4">
                        Ваш браузер не поддерживает видео.
                    </video>
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <div class="video-placeholder" onclick="visualBuilder.selectVideo(this)">
                        <div style="text-align: center; padding: 2rem; border: 2px dashed #ccc; border-radius: 8px; cursor: pointer;">
                            <div style="font-size: 2rem; margin-bottom: 1rem;">🎥</div>
                            <div>Нажмите для добавления видео</div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Создание контента кнопки
     */
    createButtonContent(element) {
        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        
        if (tagName === 'a') {
            const href = element.getAttribute('href') || '#';
            return `
                <div class="element-content">
                    <a href="${href}" contenteditable="true" style="display: inline-block; padding: 12px 24px; background: var(--primary); color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">
                        ${text || 'Ссылка'}
                    </a>
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <button contenteditable="true" style="padding: 12px 24px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
                        ${text || 'Кнопка'}
                    </button>
                </div>
            `;
        }
    }

    /**
     * Создание контента формы
     */
    createFormContent(element) {
        const tagName = element.tagName.toLowerCase();
        
        if (tagName === 'form') {
            return `
                <div class="element-content">
                    <form style="max-width: 500px; margin: 0 auto;">
                        <h3 contenteditable="true" style="margin-bottom: 1rem;">Форма</h3>
                        <div style="margin-bottom: 1rem;">
                            <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Поле:</label>
                            <input type="text" placeholder="Введите текст" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                        </div>
                        <button type="submit" style="padding: 0.75rem 1.5rem; background: var(--primary); color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Отправить
                        </button>
                    </form>
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <input type="text" placeholder="Введите текст" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
                </div>
            `;
        }
    }

    /**
     * Создание контента контейнера
     */
    createContainerContent(element) {
        const tagName = element.tagName.toLowerCase();
        const hasChildren = element.children.length > 0;
        
        if (hasChildren) {
            return `
                <div class="element-content">
                    <div style="padding: 1rem; border: 1px dashed #ccc; border-radius: 8px; min-height: 60px;">
                        <div style="font-size: 0.875rem; color: #666; margin-bottom: 0.5rem;">Контейнер</div>
                        <div contenteditable="true">
                            ${element.innerHTML}
                        </div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <div style="padding: 1rem; border: 1px dashed #ccc; border-radius: 8px; min-height: 60px; text-align: center; color: #666;">
                        Пустой контейнер
                    </div>
                </div>
            `;
        }
    }

    /**
     * Создание контента кода
     */
    createCodeContent(element) {
        const tagName = element.tagName.toLowerCase();
        const code = element.textContent.trim();
        
        if (tagName === 'pre') {
            return `
                <div class="element-content">
                    <pre contenteditable="true" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; overflow-x: auto; font-family: 'Courier New', monospace;">
                        ${code || '// Введите код здесь'}
                    </pre>
                </div>
            `;
        } else {
            return `
                <div class="element-content">
                    <code contenteditable="true" style="background: #f8f9fa; padding: 0.25rem 0.5rem; border-radius: 4px; font-family: 'Courier New', monospace;">
                        ${code || 'код'}
                    </code>
                </div>
            `;
        }
    }

    /**
     * Создание контента разделителя
     */
    createDividerContent(element) {
        return `
            <div class="element-content">
                <hr style="border: none; height: 2px; background: var(--border); margin: 2rem 0;">
            </div>
        `;
    }

    /**
     * Обработка текстовых узлов
     */
    processTextNodes(element) {
        const elements = [];
        const textNodes = Array.from(element.childNodes).filter(node => node.nodeType === Node.TEXT_NODE);
        
        textNodes.forEach(node => {
            const text = node.textContent.trim();
            if (text && this.config.autoWrapText) {
                const textElement = this.createTextElement(text);
                if (textElement) {
                    elements.push(textElement);
                }
            }
        });
        
        return elements;
    }

    /**
     * Создание текстового элемента
     */
    createTextElement(text) {
        if (!text || text.length < 3) return null;
        
        const editableElement = document.createElement('div');
        editableElement.className = 'draggable-element element-text';
        editableElement.dataset.type = 'text';
        editableElement.dataset.id = `element_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        editableElement.innerHTML = `
            <div class="element-content">
                <p contenteditable="true" style="margin: 0; padding: 0;">
                    ${text}
                </p>
            </div>
            ${this.getControlsTemplate()}
        `;
        
        this.setupElementEvents(editableElement);
        return editableElement;
    }

    /**
     * Шаблон элементов управления
     */
    getControlsTemplate() {
        return `
            <div class="element-controls">
                <button class="control-btn" onclick="visualBuilder.moveElement(this, 'up')" title="Переместить вверх" aria-label="Переместить вверх">
                    ↑
                </button>
                <button class="control-btn secondary" onclick="visualBuilder.duplicateElement(this)" title="Дублировать" aria-label="Дублировать">
                    📋
                </button>
                <button class="control-btn danger" onclick="visualBuilder.deleteElement(this)" title="Удалить" aria-label="Удалить">
                    🗑️
                </button>
            </div>
        `;
    }

    /**
     * Настройка событий для элемента
     */
    setupElementEvents(element) {
        // Клик для выделения
        element.addEventListener('click', (event) => {
            event.stopPropagation();
            this.visualBuilder.selectElement(element);
        });

        // Двойной клик для редактирования
        element.addEventListener('dblclick', (event) => {
            event.stopPropagation();
            this.visualBuilder.editElement(element);
        });

        // Обработка изменений в contenteditable
        const editableElements = element.querySelectorAll('[contenteditable="true"]');
        editableElements.forEach(editable => {
            editable.addEventListener('input', this.visualBuilder.debounce(() => {
                this.visualBuilder.addToHistory();
            }, 1000));

            editable.addEventListener('blur', () => {
                this.visualBuilder.addToHistory();
            });
        });
    }

    /**
     * Загрузка HTML файла и парсинг
     */
    async loadAndParseHTMLFile(filePath) {
        try {
            this.visualBuilder.showLoading();
            
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
                const htmlContent = data.content;
                const elements = this.parseHTMLToElements(htmlContent, filePath);
                
                // Добавляем элементы на canvas
                this.addElementsToCanvas(elements);
                
                this.visualBuilder.showNotification(`HTML файл "${filePath}" успешно загружен`, 'success');
                return elements;
            } else {
                throw new Error(data.error || 'Ошибка загрузки файла');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки HTML файла:', error);
            this.visualBuilder.showNotification('Ошибка загрузки HTML файла', 'error');
            return [];
        } finally {
            this.visualBuilder.hideLoading();
        }
    }

    /**
     * Добавление элементов на canvas
     */
    addElementsToCanvas(elements) {
        const canvas = this.visualBuilder.dom.canvas;
        
        // Очищаем canvas
        canvas.innerHTML = '';
        
        // Добавляем элементы
        elements.forEach(element => {
            canvas.appendChild(element);
        });
        
        // Обновляем состояние
        this.visualBuilder.updateLayersPanel();
        this.visualBuilder.addToHistory();
        
        console.info(`✅ Добавлено ${elements.length} элементов на canvas`);
    }

    /**
     * Экспорт элементов обратно в HTML
     */
    exportToHTML(elements = null) {
        if (!elements) {
            elements = this.visualBuilder.dom.canvas.querySelectorAll('.draggable-element');
        }
        
        let html = '<!DOCTYPE html>\n<html lang="ru">\n<head>\n';
        html += '<meta charset="UTF-8">\n';
        html += '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
        html += '<title>Экспортированная страница</title>\n';
        html += '<style>\n';
        html += 'body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }\n';
        html += '.draggable-element { margin: 1rem 0; }\n';
        html += '</style>\n';
        html += '</head>\n<body>\n';
        
        elements.forEach(element => {
            html += this.elementToHTML(element);
        });
        
        html += '\n</body>\n</html>';
        
        return html;
    }

    /**
     * Конвертация элемента в HTML
     */
    elementToHTML(element) {
        const elementType = element.dataset.type;
        const originalTag = element.dataset.originalTag || 'div';
        const content = element.querySelector('.element-content');
        
        if (!content) return '';
        
        // Удаляем элементы управления
        const controls = content.querySelector('.element-controls');
        if (controls) {
            controls.remove();
        }
        
        // Получаем чистый HTML
        let html = content.innerHTML;
        
        // Очищаем от contenteditable атрибутов
        html = html.replace(/contenteditable="true"/g, '');
        
        // Оборачиваем в оригинальный тег
        return `<${originalTag}>${html}</${originalTag}>\n`;
    }

    /**
     * Получение статистики парсинга
     */
    getParsingStats() {
        return {
            totalElements: this.parsedElements.length,
            elementTypes: this.getElementTypesCount(),
            currentFile: this.currentFile,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Подсчет типов элементов
     */
    getElementTypesCount() {
        const counts = {};
        this.parsedElements.forEach(element => {
            const type = element.dataset.type;
            counts[type] = (counts[type] || 0) + 1;
        });
        return counts;
    }

    /**
     * Очистка данных парсера
     */
    clear() {
        this.parsedElements = [];
        this.currentFile = null;
    }
}

// Глобальные функции для обратной совместимости
let htmlParser;

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    if (window.visualBuilder) {
        htmlParser = new HTMLParser(window.visualBuilder);
        window.htmlParser = htmlParser;
        console.info('🔍 HTML Parser готов к использованию');
    }
}); 