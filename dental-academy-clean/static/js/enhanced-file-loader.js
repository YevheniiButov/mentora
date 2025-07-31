/**
 * Исправленный EnhancedFileLoader v2.1
 * Исправляет: document.write проблемы с Bootstrap, улучшенная обработка ошибок
 */

class EnhancedFileLoader {
    constructor(editor) {
        this.editor = editor;
        this.canvas = editor.Canvas;
        this.loadedResources = new Set();
        this.pendingStyles = [];
        
        // Инициализируем External CSS Loader
        this.cssLoader = new ExternalCSSLoader(editor);
        
        console.log('🚀 EnhancedFileLoader v2.1 initialized (Fixed document.write issues)');
    }

    /**
     * Основной метод загрузки файла в редактор
     */
    async loadFileInEditor(path, fileContent) {
        console.log('🔧 Loading file into GrapesJS v2.1:', path);
        
        try {
            // 1. Парсим содержимое файла
            const parsed = await this.parseFullHTMLContent(fileContent);
            console.log('🔧 Parsed content:', {
                hasBodyHTML: !!parsed.bodyHtml,
                hasCSSContent: !!parsed.cssContent,
                externalStylesCount: parsed.externalStyles.length,
                externalScriptsCount: parsed.externalScripts.length
            });
            
            // 2. Очищаем редактор
            this.clearEditor();
            
            // 3. Загружаем базовые ресурсы БЕЗ document.write
            await this.loadBaseResourcesSafely();
            
            // 4. Загружаем внешние CSS файлы из HTML
            console.log('🎨 Loading external CSS files...');
            await this.cssLoader.loadCSSFromTemplate(fileContent);
            
            // 5. Применяем внутренние стили
            if (parsed.cssContent) {
                await this.applyCSSToCanvas(parsed.cssContent);
            }
            
            // 6. Загружаем внешние скрипты безопасно
            if (parsed.externalScripts.length > 0) {
                await this.loadExternalScriptsSafely(parsed.externalScripts);
            }
            
            // 7. Загружаем HTML компоненты (ПОСЛЕ всех стилей!)
            if (parsed.bodyHtml) {
                await this.loadHTMLComponents(parsed.bodyHtml);
            }
            
            // 8. Принудительно обновляем canvas с увеличенной задержкой
            await this.forceCanvasRefreshWithDelay();
            
            // 9. Показываем статистику загрузки
            this.showLoadingStats();
            
            console.log('✅ File loaded successfully in GrapesJS v2.1');
            
        } catch (error) {
            console.error('❌ Error loading file v2.1:', error);
            
            // Fallback к базовой загрузке
            console.log('🔄 Falling back to basic loading...');
            await this.basicFallbackLoading(fileContent);
            
            throw error;
        }
    }

    /**
     * Исправленный парсинг HTML - загружает ВЕСЬ контент страницы
     * Решает проблему: в редакторе отображается только часть контента
     */
    parseFullHTMLContent(htmlContent) {
        console.log('🔧 Parsing HTML content (full version)...');
        
        const result = {
            bodyHtml: '',
            cssContent: '',
            jsContent: '',
            externalStyles: [],
            externalScripts: [],
            metaTags: [],
            title: '',
            rawHTML: htmlContent
        };
        
        try {
            // ПЕРВЫЙ ЭТАП: Предварительная очистка Jinja2 БЕЗ агрессивного удаления
            const lightlyCleanedHTML = this.lightCleanJinja(htmlContent);
            
            const parser = new DOMParser();
            const doc = parser.parseFromString(lightlyCleanedHTML, 'text/html');
            
            // Извлекаем title
            const titleTag = doc.querySelector('title');
            if (titleTag) {
                result.title = titleTag.textContent;
            }
            
            // Извлекаем meta теги
            const metaTags = doc.querySelectorAll('meta');
            metaTags.forEach(meta => {
                result.metaTags.push({
                    name: meta.getAttribute('name'),
                    content: meta.getAttribute('content'),
                    charset: meta.getAttribute('charset'),
                    httpEquiv: meta.getAttribute('http-equiv')
                });
            });
            
            // Извлекаем внешние CSS файлы
            const linkTags = doc.querySelectorAll('link[rel="stylesheet"], link[href*=".css"]');
            linkTags.forEach(link => {
                const href = link.getAttribute('href');
                if (href && !href.includes('bootstrap') && !href.includes('font-awesome')) {
                    result.externalStyles.push({
                        href: href,
                        media: link.getAttribute('media') || 'all',
                        integrity: link.getAttribute('integrity'),
                        crossorigin: link.getAttribute('crossorigin'),
                        originalElement: link.outerHTML
                    });
                }
            });
            
            // Извлекаем внешние JS файлы
            const scriptTags = doc.querySelectorAll('script[src]');
            scriptTags.forEach(script => {
                const src = script.getAttribute('src');
                if (src && !src.includes('bootstrap')) {
                    result.externalScripts.push({
                        src: src,
                        async: script.hasAttribute('async'),
                        defer: script.hasAttribute('defer'),
                        integrity: script.getAttribute('integrity'),
                        crossorigin: script.getAttribute('crossorigin')
                    });
                }
            });
            
            // Извлекаем внутренние стили
            const styleTags = doc.querySelectorAll('style');
            styleTags.forEach(style => {
                result.cssContent += style.textContent + '\n';
            });
            
            // Извлекаем внутренние скрипты
            const inlineScripts = doc.querySelectorAll('script:not([src])');
            inlineScripts.forEach(script => {
                result.jsContent += script.textContent + '\n';
            });
            
            // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Извлекаем ВЕСЬ контент body
            if (doc.body) {
                // Получаем полный innerHTML body
                let fullBodyContent = doc.body.innerHTML;
                
                console.log('🔍 Original body content length:', fullBodyContent.length);
                console.log('🔍 First 200 chars:', fullBodyContent.substring(0, 200));
                
                // Применяем более мягкую очистку к контенту body
                const cleanBodyContent = this.gentleCleanJinja(fullBodyContent);
                
                console.log('🔍 Cleaned body content length:', cleanBodyContent.length);
                console.log('🔍 Cleaned first 200 chars:', cleanBodyContent.substring(0, 200));
                
                result.bodyHtml = cleanBodyContent;
            } else {
                console.warn('⚠️ No body element found in HTML');
                
                // Fallback: извлекаем всё между <body> тегами вручную
                const bodyMatch = lightlyCleanedHTML.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
                if (bodyMatch) {
                    console.log('🔄 Using fallback body extraction');
                    result.bodyHtml = this.gentleCleanJinja(bodyMatch[1]);
                } else {
                    // Последний fallback: используем весь контент
                    console.log('🔄 Using entire content as fallback');
                    result.bodyHtml = this.gentleCleanJinja(lightlyCleanedHTML);
                }
            }
            
            console.log('✅ HTML parsing completed:', {
                bodyLength: result.bodyHtml.length,
                cssLength: result.cssContent.length,
                externalStyles: result.externalStyles.length,
                externalScripts: result.externalScripts.length
            });
            
            return result;
            
        } catch (error) {
            console.error('❌ Error parsing HTML:', error);
            
            // Emergency fallback
            console.log('🆘 Using emergency fallback parsing');
            result.bodyHtml = this.gentleCleanJinja(htmlContent);
            return result;
        }
    }

    /**
     * НОВОЕ: Легкая очистка Jinja2 - только заменяет url_for, не удаляет контент
     */
    lightCleanJinja(html) {
        return html
            // Заменяем url_for на реальные пути
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename\s*=\s*['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename=['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            // Заменяем другие популярные url_for паттерны
            .replace(/\{\{\s*url_for\(\s*['"]([^'"]+)['"],?\s*[^}]*\)\s*\}\}/g, '/$1')
            // НЕ удаляем Jinja2 блоки полностью - заменяем на комментарии
            .replace(/\{\%\s*(.*?)\s*\%\}/g, '<!-- Jinja2: $1 -->')
            .replace(/\{\{\s*([^}]*)\s*\}\}/g, '<!-- Jinja2 var: $1 -->');
    }

    /**
     * НОВОЕ: Мягкая очистка Jinja2 для body контента
     */
    gentleCleanJinja(html) {
        return html
            // Заменяем url_for (если остались)
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename\s*=\s*['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename=['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            .replace(/\{\{\s*url_for\(\s*['"]([^'"]+)['"],?\s*[^}]*\)\s*\}\}/g, '/$1')
            
            // Обрабатываем Jinja2 переменные - заменяем на плейсхолдеры
            .replace(/\{\{\s*([^}|]+)\s*\|\s*([^}]+)\s*\}\}/g, '<!-- $1 | $2 -->')  // Фильтры
            .replace(/\{\{\s*([^}]+)\s*\}\}/g, (match, varName) => {
                // Сохраняем важные переменные как плейсхолдеры
                const trimmed = varName.trim();
                if (trimmed.includes('title') || trimmed.includes('name') || trimmed.includes('text')) {
                    return `<span data-jinja="${trimmed}">Content</span>`;
                }
                return '<!-- Jinja2 var -->';
            })
            
            // Обрабатываем Jinja2 блоки - НЕ удаляем, а комментируем
            .replace(/\{\%\s*if\s+([^%]+)\s*\%\}/g, '<!-- IF: $1 -->')
            .replace(/\{\%\s*endif\s*\%\}/g, '<!-- ENDIF -->')
            .replace(/\{\%\s*for\s+([^%]+)\s*\%\}/g, '<!-- FOR: $1 -->')
            .replace(/\{\%\s*endfor\s*\%\}/g, '<!-- ENDFOR -->')
            .replace(/\{\%\s*block\s+([^%]+)\s*\%\}/g, '<!-- BLOCK: $1 -->')
            .replace(/\{\%\s*endblock\s*\%\}/g, '<!-- ENDBLOCK -->')
            .replace(/\{\%\s*extends\s+([^%]+)\s*\%\}/g, '<!-- EXTENDS: $1 -->')
            .replace(/\{\%\s*include\s+([^%]+)\s*\%\}/g, '<!-- INCLUDE: $1 -->')
            
            // Очищаем оставшиеся Jinja2 конструкции
            .replace(/\{\%\s*([^%]*)\s*\%\}/g, '<!-- Jinja2: $1 -->')
            
            // Удаляем только пустые строки и лишние пробелы
            .replace(/^\s*$/gm, '')  // Пустые строки
            .replace(/\s+/g, ' ')    // Множественные пробелы
            .trim();
    }

    /**
     * УСТАРЕВШИЙ: Очистка Jinja2 шаблонов для GrapesJS (заменен на gentleCleanJinja)
     */
    cleanJinjaTemplate(html) {
        // Используем новый мягкий метод
        return this.gentleCleanJinja(html);
    }

    /**
     * ОБНОВЛЕНО: Улучшенная очистка редактора
     */
    clearEditor() {
        console.log('🧹 Clearing editor (enhanced)...');
        
        try {
            // Очищаем компоненты и стили
            this.editor.setComponents('');
            this.editor.setStyle('');
            this.pendingStyles = [];
            
            // Очищаем также загруженные CSS
            if (this.cssLoader) {
                this.cssLoader.clearLoadedCSS();
            }
            
            // Очищаем canvas полностью
            const canvas = this.editor.Canvas;
            const canvasDoc = canvas.getDocument();
            
            if (canvasDoc && canvasDoc.body) {
                // Удаляем все элементы из body canvas
                canvasDoc.body.innerHTML = '';
                
                // Очищаем head от пользовательских стилей
                const head = canvasDoc.head;
                if (head) {
                    const userStyles = head.querySelectorAll('style[data-loaded-by], link[data-loaded-by]');
                    userStyles.forEach(style => style.remove());
                }
            }
            
            console.log('✅ Editor cleared completely');
            
        } catch (error) {
            console.warn('⚠️ Error during editor clearing:', error);
        }
    }

    /**
     * ИСПРАВЛЕНО: Загрузка базовых ресурсов БЕЗ document.write
     */
    async loadBaseResourcesSafely() {
        console.log('📦 Loading base resources safely...');
        
        const baseStyles = [
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ];
        
        // Загружаем CSS без document.write
        const cssPromises = baseStyles.map(url => {
            if (!this.loadedResources.has(url)) {
                return this.addStyleToCanvasSafely(url);
            }
            return Promise.resolve({ url, success: true, source: 'already-loaded' });
        });
        
        const cssResults = await Promise.allSettled(cssPromises);
        console.log('📦 Base CSS loaded:', cssResults.filter(r => r.status === 'fulfilled').length);
        
        // Загружаем Bootstrap JS БЕЗ document.write
        await this.loadBootstrapSafely();
        
        console.log('✅ Base resources loaded safely');
    }

    /**
     * НОВОЕ: Безопасная загрузка Bootstrap JS
     */
    async loadBootstrapSafely() {
        const bootstrapJS = 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js';
        
        if (this.loadedResources.has(bootstrapJS)) {
            console.log('📦 Bootstrap JS already loaded');
            return;
        }
        
        try {
            await this.addScriptToCanvasSafely(bootstrapJS);
            this.loadedResources.add(bootstrapJS);
            console.log('✅ Bootstrap JS loaded safely');
        } catch (error) {
            console.warn('⚠️ Could not load Bootstrap JS:', error.message);
            // Не критическая ошибка - продолжаем без Bootstrap JS
        }
    }

    /**
     * НОВОЕ: Безопасное добавление CSS в canvas (без document.write)
     */
    async addStyleToCanvasSafely(href, media = 'all') {
        return new Promise((resolve) => {
            const canvas = this.editor.Canvas;
            const canvasDoc = canvas.getDocument();
            
            if (!canvasDoc) {
                console.warn('⚠️ Canvas document not ready for CSS');
                resolve({ url: href, success: false, error: 'Canvas not ready' });
                return;
            }
            
            const canvasHead = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
            if (!canvasHead) {
                console.warn('⚠️ No head element in canvas');
                resolve({ url: href, success: false, error: 'No head element' });
                return;
            }
            
            // Проверяем, не загружен ли уже этот стиль
            const existingLink = canvasDoc.querySelector(`link[href="${href}"]`);
            if (existingLink) {
                console.log('📦 CSS already exists in canvas:', href);
                resolve({ url: href, success: true, source: 'existing' });
                return;
            }
            
            // Создаем link элемент БЕЗ document.write
            const link = canvasDoc.createElement('link');
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = href;
            link.media = media;
            link.setAttribute('data-loaded-by', 'EnhancedFileLoader');
            
            link.onload = () => {
                console.log('✅ CSS loaded safely:', href);
                this.loadedResources.add(href);
                resolve({ url: href, success: true, source: 'network' });
            };
            
            link.onerror = () => {
                console.warn('⚠️ CSS failed to load:', href);
                resolve({ url: href, success: false, error: 'Failed to load' });
            };
            
            // Добавляем в head
            canvasHead.appendChild(link);
        });
    }

    /**
     * НОВОЕ: Безопасное добавление скрипта в canvas
     */
    async addScriptToCanvasSafely(src) {
        return new Promise((resolve) => {
            const canvas = this.editor.Canvas;
            const canvasDoc = canvas.getDocument();
            
            if (!canvasDoc) {
                console.warn('⚠️ Canvas document not ready for script');
                resolve({ url: src, success: false, error: 'Canvas not ready' });
                return;
            }
            
            // Проверяем, не загружен ли уже этот скрипт
            const existingScript = canvasDoc.querySelector(`script[src="${src}"]`);
            if (existingScript) {
                console.log('📦 Script already exists in canvas:', src);
                resolve({ url: src, success: true, source: 'existing' });
                return;
            }
            
            const script = canvasDoc.createElement('script');
            script.src = src;
            script.type = 'text/javascript';
            script.setAttribute('data-loaded-by', 'EnhancedFileLoader');
            
            script.onload = () => {
                console.log('✅ Script loaded safely:', src);
                resolve({ url: src, success: true, source: 'network' });
            };
            
            script.onerror = () => {
                console.warn('⚠️ Script failed to load:', src);
                resolve({ url: src, success: false, error: 'Failed to load' });
            };
            
            // Добавляем в head или body
            const canvasHead = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
            const canvasBody = canvasDoc.body || canvasDoc.getElementsByTagName('body')[0];
            
            if (canvasHead) {
                canvasHead.appendChild(script);
            } else if (canvasBody) {
                canvasBody.appendChild(script);
            } else {
                console.warn('⚠️ No head or body element for script');
                resolve({ url: src, success: false, error: 'No container element' });
            }
        });
    }

    /**
     * НОВОЕ: Безопасная загрузка внешних скриптов
     */
    async loadExternalScriptsSafely(externalScripts) {
        console.log('📜 Loading external scripts safely:', externalScripts.length);
        
        const scriptPromises = externalScripts.map(script => {
            if (script.src && !this.loadedResources.has(script.src)) {
                return this.addScriptToCanvasSafely(script.src);
            }
            return Promise.resolve({ url: script.src, success: true, source: 'already-loaded' });
        });
        
        const results = await Promise.allSettled(scriptPromises);
        const successful = results.filter(r => r.status === 'fulfilled' && r.value.success).length;
        
        console.log('📜 External scripts loaded:', successful, 'of', externalScripts.length);
    }

    /**
     * Загрузка внешних ресурсов
     */
    async loadExternalResources(externalStyles = [], externalScripts = []) {
        console.log('🔧 Loading external resources...');
        
        // Загружаем CSS файлы
        for (const style of externalStyles) {
            if (!this.loadedResources.has(style.href)) {
                await this.addStyleToCanvas(style.href, style.media);
                this.loadedResources.add(style.href);
            }
        }
        
        // Загружаем JS файлы
        for (const script of externalScripts) {
            if (!this.loadedResources.has(script.src)) {
                await this.addScriptToCanvas(script.src);
                this.loadedResources.add(script.src);
            }
        }
    }

    /**
     * Добавление CSS в canvas с улучшенной обработкой
     */
    async addStyleToCanvas(href, media = 'all') {
        return new Promise((resolve, reject) => {
            const canvas = this.editor.Canvas;
            const canvasDoc = canvas.getDocument();
            
            if (!canvasDoc) {
                console.warn('⚠️ Canvas document not ready');
                resolve();
                return;
            }
            
            const canvasHead = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
            if (!canvasHead) {
                console.warn('⚠️ No head element in canvas');
                resolve();
                return;
            }
            
            // Проверяем, не загружен ли уже этот стиль
            const existingLink = canvasDoc.querySelector(`link[href="${href}"]`);
            if (existingLink) {
                resolve();
                return;
            }
            
            const link = canvasDoc.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = media;
            link.setAttribute('data-loaded-by', 'EnhancedFileLoader');
            
            link.onload = () => {
                console.log('✅ CSS loaded:', href);
                this.loadedResources.add(href);
                resolve();
            };
            
            link.onerror = () => {
                console.warn('⚠️ CSS failed to load:', href);
                resolve(); // Не прерываем процесс
            };
            
            canvasHead.appendChild(link);
        });
    }

    /**
     * Добавление скрипта в canvas
     */
    async addScriptToCanvas(src) {
        return new Promise((resolve, reject) => {
            const canvas = this.editor.Canvas;
            const canvasDoc = canvas.getDocument();
            const canvasHead = canvasDoc.head;
            
            // Проверяем, не загружен ли уже этот скрипт
            const existingScript = canvasDoc.querySelector(`script[src="${src}"]`);
            if (existingScript) {
                resolve();
                return;
            }
            
            const script = canvasDoc.createElement('script');
            script.src = src;
            
            script.onload = () => {
                console.log('✅ Script loaded:', src);
                resolve();
            };
            
            script.onerror = () => {
                console.warn('⚠️ Script failed to load:', src);
                resolve(); // Не прерываем процесс
            };
            
            canvasHead.appendChild(script);
        });
    }

    /**
     * Применение внутренних CSS к canvas
     */
    async applyCSSToCanvas(cssContent) {
        console.log('🎨 Applying internal CSS to canvas...');
        
        const canvas = this.editor.Canvas;
        const canvasDoc = canvas.getDocument();
        
        if (!canvasDoc) {
            console.warn('⚠️ Canvas document not ready for CSS');
            return;
        }
        
        const canvasHead = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
        if (canvasHead) {
            // Создаем style элемент
            const styleElement = canvasDoc.createElement('style');
            styleElement.setAttribute('data-loaded-by', 'EnhancedFileLoader');
            styleElement.setAttribute('data-type', 'internal');
            styleElement.textContent = cssContent;
            canvasHead.appendChild(styleElement);
            
            console.log('✅ Internal CSS applied to canvas');
        }
        
        // Также добавляем в StyleManager редактора
        try {
            this.editor.setStyle(cssContent);
        } catch (error) {
            console.warn('⚠️ Could not set CSS in StyleManager:', error);
        }
        
        // Добавляем в pending styles для повторного применения
        this.pendingStyles.push(cssContent);
    }

    /**
     * Загрузка HTML компонентов с задержкой
     */
    async loadHTMLComponents(htmlContent) {
        console.log('🔧 Loading HTML components (enhanced)...');
        console.log('📊 Content to load:', {
            length: htmlContent.length,
            preview: htmlContent.substring(0, 300) + (htmlContent.length > 300 ? '...' : ''),
            containsMainContent: htmlContent.includes('succesvolle') || htmlContent.includes('tandartslicentie'),
            containsMobileWidget: htmlContent.includes('Become') || htmlContent.includes('Tandarts')
        });
        
        // Ждем полной загрузки CSS
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        try {
            // Проверяем, что контент не пустой
            if (!htmlContent || htmlContent.trim() === '') {
                console.error('❌ Empty HTML content provided');
                throw new Error('Empty HTML content');
            }
            
            // Загружаем компоненты
            this.editor.setComponents(htmlContent);
            console.log('✅ HTML components loaded successfully');
            
            // Принудительно обновляем canvas
            const canvas = this.editor.Canvas;
            canvas.refresh();
            
            // Проверяем что загрузилось
            const components = this.editor.getComponents();
            console.log('📊 Loaded components count:', components.length);
            
            // Дополнительная задержка для рендеринга
            await new Promise(resolve => setTimeout(resolve, 500));
            
        } catch (error) {
            console.error('❌ Error loading HTML components:', error);
            console.log('🔄 Attempting fallback loading...');
            
            // Fallback: пробуем загрузить в несколько этапов
            try {
                // Сначала очищаем и пробуем загрузить снова
                this.editor.setComponents('');
                await new Promise(resolve => setTimeout(resolve, 200));
                
                // Загружаем только текстовое содержимое
                const textOnlyContent = htmlContent.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '');
                this.editor.setComponents(textOnlyContent);
                
                console.log('✅ Fallback loading completed');
                
            } catch (fallbackError) {
                console.error('❌ Fallback loading also failed:', fallbackError);
                throw fallbackError;
            }
        }
    }

    /**
     * Принудительное обновление canvas с задержкой
     */
    async forceCanvasRefreshWithDelay() {
        console.log('🔄 Force refreshing canvas with delay...');
        
        // Первое обновление
        this.refreshCanvas();
        
        // Второе обновление через задержку для CSS
        setTimeout(() => {
            this.refreshCanvas();
            this.reapplyPendingStyles();
        }, 1000);
        
        // Третье обновление для уверенности
        setTimeout(() => {
            this.refreshCanvas();
            console.log('✅ Canvas refresh completed');
        }, 2000);
    }

    /**
     * Обновление canvas
     */
    refreshCanvas() {
        const canvas = this.editor.Canvas;
        
        try {
            // Метод 1: Refresh canvas
            canvas.refresh();
            
            // Метод 2: Перерисовываем компоненты
            const components = this.editor.getComponents();
            if (components && components.each) {
                components.each(component => {
                    try {
                        if (component.view && component.view.render) {
                            component.view.render();
                        }
                    } catch (e) {
                        console.warn('Warning rendering component:', e);
                    }
                });
            }
            
            // Метод 3: Событие обновления
            this.editor.trigger('canvas:update');
            
        } catch (error) {
            console.warn('⚠️ Error during canvas refresh:', error);
        }
    }

    /**
     * Повторное применение ожидающих стилей
     */
    reapplyPendingStyles() {
        if (this.pendingStyles.length === 0) return;
        
        console.log('🔄 Reapplying pending styles...');
        
        const canvas = this.editor.Canvas;
        const canvasDoc = canvas.getDocument();
        
        if (canvasDoc) {
            this.pendingStyles.forEach((css, index) => {
                const styleId = `pending-style-${index}`;
                
                // Удаляем предыдущий если есть
                const existing = canvasDoc.getElementById(styleId);
                if (existing) existing.remove();
                
                // Добавляем новый
                const style = canvasDoc.createElement('style');
                style.id = styleId;
                style.textContent = css;
                style.setAttribute('data-loaded-by', 'EnhancedFileLoader-pending');
                
                const head = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
                if (head) {
                    head.appendChild(style);
                }
            });
        }
    }

    /**
     * Показ статистики загрузки
     */
    showLoadingStats() {
        if (this.cssLoader) {
            const stats = this.cssLoader.getLoadingStats();
            console.log('📊 Loading Statistics:', {
                externalCSS: stats,
                internalCSS: this.pendingStyles.length,
                baseResources: this.loadedResources.size
            });
        }
    }

    /**
     * УЛУЧШЕНО: Базовый fallback
     */
    async basicFallbackLoading(fileContent) {
        console.log('🛟 Basic fallback loading...');
        
        try {
            // Простое извлечение CSS и HTML
            const parser = new DOMParser();
            const cleanedHTML = this.cleanJinjaTemplate(fileContent);
            const doc = parser.parseFromString(cleanedHTML, 'text/html');
            
            // Извлекаем CSS
            let cssContent = '';
            const styleTags = doc.querySelectorAll('style');
            styleTags.forEach(style => {
                cssContent += style.textContent + '\n';
            });
            
            // Извлекаем HTML
            let bodyHtml = '';
            if (doc.body) {
                bodyHtml = doc.body.innerHTML;
            }
            
            // Загружаем в редактор
            if (bodyHtml) {
                this.editor.setComponents(bodyHtml);
            }
            if (cssContent) {
                this.editor.setStyle(cssContent);
            }
            
            // Обновление через задержку
            setTimeout(() => {
                this.refreshCanvas();
            }, 1000);
            
            console.log('✅ Fallback loading completed');
            
        } catch (error) {
            console.error('❌ Even fallback loading failed:', error);
        }
    }

    /**
     * Публичный метод для использования в FileExplorer
     */
    async loadFile(path) {
        try {
            console.log('📁 Loading file via Enhanced File Loader v2.1:', path);
            
            // Загружаем содержимое файла
            const response = await fetch(`/api/content-editor/template-content/${encodeURIComponent(path)}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to load file');
            }
            
            // Загружаем в редактор
            await this.loadFileInEditor(path, data.content);
            
            return { 
                success: true, 
                message: 'File loaded successfully with fixed CSS support',
                stats: this.cssLoader ? this.cssLoader.getLoadingStats() : null
            };
            
        } catch (error) {
            console.error('❌ Error loading file v2.1:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Получение информации о загруженных ресурсах
     */
    getLoadedResources() {
        return {
            baseResources: Array.from(this.loadedResources),
            internalStyles: this.pendingStyles.length,
            externalCSS: this.cssLoader ? this.cssLoader.getLoadingStats() : null
        };
    }

    /**
     * НОВОЕ: Отладка извлечения контента
     */
    debugContentExtraction(originalHTML, extractedContent) {
        console.log('🐛 Content Extraction Debug:');
        console.log('Original HTML length:', originalHTML.length);
        console.log('Extracted content length:', extractedContent.length);
        
        // Проверяем ключевые элементы
        const originalHasMainTitle = originalHTML.includes('succesvolle');
        const extractedHasMainTitle = extractedContent.includes('succesvolle');
        
        const originalHasMobile = originalHTML.includes('Become');
        const extractedHasMobile = extractedContent.includes('Become');
        
        console.log('Main title in original:', originalHasMainTitle);
        console.log('Main title in extracted:', extractedHasMainTitle);
        console.log('Mobile widget in original:', originalHasMobile);
        console.log('Mobile widget in extracted:', extractedHasMobile);
        
        if (originalHasMainTitle && !extractedHasMainTitle) {
            console.error('❌ CRITICAL: Main content lost during extraction!');
            
            // Ищем где потерялся контент
            const bodyMatch = originalHTML.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
            if (bodyMatch) {
                console.log('🔍 Body content found, length:', bodyMatch[1].length);
                console.log('🔍 Body starts with:', bodyMatch[1].substring(0, 200));
            }
        }
        
        return {
            originalHasMainTitle,
            extractedHasMainTitle,
            originalHasMobile,
            extractedHasMobile,
            contentLost: originalHasMainTitle && !extractedHasMainTitle
        };
    }
}

// Интеграция с существующим FileExplorer
if (typeof window !== 'undefined') {
    // Экспортируем класс в глобальную область
    window.EnhancedFileLoader = EnhancedFileLoader;
    
    console.log('✅ EnhancedFileLoader v2.1 loaded (Fixed document.write and URL parsing)');
    
    // Автоматическая инициализация при загрузке редактора
    const initFileLoader = () => {
        if (window.editor && window.editor.Canvas) {
            try {
                window.fileLoader = new EnhancedFileLoader(window.editor);
                console.log('✅ EnhancedFileLoader instance created');
                return true;
            } catch (error) {
                console.error('❌ Error creating EnhancedFileLoader:', error);
                return false;
            }
        }
        return false;
    };
    
    // Пытаемся инициализировать сразу
    if (!initFileLoader()) {
        // Если не получилось, ждем готовности редактора
        const waitForEditor = setInterval(() => {
            if (initFileLoader()) {
                clearInterval(waitForEditor);
            }
        }, 100);
        
        // Таймаут через 10 секунд
        setTimeout(() => {
            clearInterval(waitForEditor);
            console.warn('⚠️ EnhancedFileLoader initialization timeout');
        }, 10000);
    }
}

console.log('✅ EnhancedFileLoader loaded'); 