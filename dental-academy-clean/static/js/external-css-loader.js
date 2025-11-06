/**
 * Исправленный ExternalCSSLoader - решение проблем парсинга URL
 * Исправляет: 404 ошибки, неправильный парсинг url_for(), document.write проблемы
 */

class ExternalCSSLoader {
    constructor(editor) {
        this.editor = editor;
        this.loadedCSS = new Set();
        this.cssCache = new Map();
        this.projectCSSFiles = [];
        this.baseURL = window.location.origin;
        
        // Инициализируем список CSS файлов проекта
        this.initProjectCSSFiles();
    }

    /**
     * Инициализация списка CSS файлов проекта
     */
    async initProjectCSSFiles() {
        try {
            const response = await fetch('/api/content-editor/css-files');
            const data = await response.json();
            
            if (data.success && data.data?.css_files) {
                this.projectCSSFiles = data.data.css_files.map(file => ({
                    path: file.path,
                    url: `/static/${file.path}`,
                    name: file.name,
                    full_name: file.full_name,
                    category: file.category
                }));

            } else {
                console.warn('⚠️ Could not load project CSS files, using defaults');
                this.setDefaultProjectCSS();
            }
        } catch (error) {
            console.warn('⚠️ Error loading project CSS files:', error);
            this.setDefaultProjectCSS();
        }
    }

    /**
     * Установка стандартных CSS файлов проекта
     */
    setDefaultProjectCSS() {
        this.projectCSSFiles = [
            { path: 'css/themes/themes.css', url: '/static/css/themes/themes.css', name: 'themes' },
            { path: 'css/learning_map.css', url: '/static/css/learning_map.css', name: 'learning_map' },
            { path: 'css/universal-styles.css', url: '/static/css/universal-styles.css', name: 'universal-styles' },
            { path: 'css/dental-components.css', url: '/static/css/dental-components.css', name: 'dental-components' },
            { path: 'css/components/components.css', url: '/static/css/components/components.css', name: 'components' },
            { path: 'css/base/global.css', url: '/static/css/base/global.css', name: 'global' },
            { path: 'css/pages/learning_map.css', url: '/static/css/pages/learning_map.css', name: 'learning_map_page' },
            { path: 'css/category-navigation.css', url: '/static/css/category-navigation.css', name: 'category-navigation' }
        ];
    }

    /**
     * НОВОЕ: Очистка Jinja2 синтаксиса из HTML перед парсингом
     */
    cleanJinjaFromHTML(htmlContent) {
        return htmlContent
            // Заменяем url_for на реальные пути ПЕРЕД парсингом DOM
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename\s*=\s*['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            .replace(/\{\{\s*url_for\(\s*['"]static['"],?\s*filename=['"]([^'"]+)['"]\s*\)\s*\}\}/g, '/static/$1')
            // Убираем другие Jinja2 конструкции
            .replace(/\{\%\s*.*?\s*\%\}/g, '')
            .replace(/\{\{\s*[^}]*\s*\}\}/g, '')
            // Очищаем условные блоки
            .replace(/\{\%\s*if\s+.*?\%\}[\s\S]*?\{\%\s*endif\s*\%\}/g, '')
            .replace(/\{\%\s*for\s+.*?\%\}[\s\S]*?\{\%\s*endfor\s*\%\}/g, '');
    }

    /**
     * ИСПРАВЛЕНО: Преобразование URL с улучшенной обработкой
     */
    resolveURL(href, originalHTML = '') {

        // Проверяем, что это не закодированный URL с ошибками
        if (href.includes('%7D') || href.includes('%7B')) {
            console.warn('⚠️ Detected encoded Jinja2 syntax, trying to fix:', href);
            // Пытаемся найти оригинальный URL в исходном HTML
            const match = originalHTML.match(new RegExp(`url_for\\([^)]*['"]([^'"]*${href.split('.')[0]}[^'"]*)['"]`, 'i'));
            if (match) {
                const filename = match[1];
                return `${this.baseURL}/static/${filename}`;
            }
        }

        // Уже обработанные пути
        if (href.startsWith('/static/')) {
            return `${this.baseURL}${href}`;
        }

        // Абсолютные URL - возвращаем как есть
        if (href.startsWith('http://') || href.startsWith('https://')) {
            return href;
        }

        // Абсолютные пути от корня
        if (href.startsWith('/')) {
            return `${this.baseURL}${href}`;
        }

        // Относительные пути
        if (href.startsWith('./') || href.startsWith('../')) {
            return `${this.baseURL}/static/${href.replace(/^\.\//, '')}`;
        }

        // Простые имена файлов - ищем в проекте
        if (href.endsWith('.css')) {
            const projectFile = this.findProjectCSSFile(href);
            if (projectFile) {

                return `${this.baseURL}${projectFile.url}`;
            }
            // Fallback - пробуем static
            return `${this.baseURL}/static/css/${href}`;
        }

        console.warn('⚠️ Could not resolve URL:', href);
        return null;
    }

    /**
     * УЛУЧШЕНО: Поиск CSS файла в проекте по имени
     */
    findProjectCSSFile(filename) {
        const baseName = filename.replace(/^.*\//, ''); // Убираем путь, оставляем имя
        const nameWithoutExt = baseName.replace('.css', '');
        
        // Ищем точное совпадение
        let found = this.projectCSSFiles.find(file => 
            file.path.endsWith(filename) || 
            file.full_name === baseName ||
            file.name === nameWithoutExt
        );
        
        if (found) {

            return found;
        }
        
        // Ищем частичное совпадение
        found = this.projectCSSFiles.find(file => 
            file.path.includes(nameWithoutExt) ||
            file.name.includes(nameWithoutExt)
        );
        
        if (found) {

            return found;
        }

        return null;
    }

    /**
     * ИСПРАВЛЕНО: Загрузка одного CSS файла с улучшенной обработкой ошибок
     */
    async loadSingleCSS(url, linkElement = null) {

        try {
            // Проверяем кэш
            if (this.cssCache.has(url)) {
                const cached = this.cssCache.get(url);
                await this.injectCSSIntoCanvas(cached.content, url);
                this.loadedCSS.add(url);

                return { url, success: true, source: 'cache' };
            }

            // Загружаем CSS
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const cssContent = await response.text();
            
            if (!cssContent || cssContent.trim() === '') {
                throw new Error('Empty CSS content');
            }
            
            // Обрабатываем относительные пути в CSS
            const processedCSS = this.processRelativeURLsInCSS(cssContent, url);
            
            // Кэшируем
            this.cssCache.set(url, {
                content: processedCSS,
                originalURL: url,
                loadedAt: Date.now(),
                size: cssContent.length
            });
            
            // Инжектируем в canvas
            await this.injectCSSIntoCanvas(processedCSS, url);
            this.loadedCSS.add(url);

            return { url, success: true, source: 'network', size: cssContent.length };
            
        } catch (error) {
            console.error('❌ Failed to load CSS:', url, error.message);
            
            // Пробуем альтернативные пути
            const alternatives = this.getAlternativeURLs(url);
            for (const altURL of alternatives) {
                try {

                    const altResponse = await fetch(altURL);
                    if (altResponse.ok) {
                        const altCSS = await altResponse.text();
                        if (altCSS && altCSS.trim() !== '') {
                            const processedCSS = this.processRelativeURLsInCSS(altCSS, altURL);
                            await this.injectCSSIntoCanvas(processedCSS, altURL);
                            this.loadedCSS.add(url); // Оригинальный URL
                            this.loadedCSS.add(altURL); // Альтернативный URL

                            return { url: altURL, success: true, source: 'alternative' };
                        }
                    }
                } catch (altError) {
                    console.warn('⚠️ Alternative also failed:', altURL, altError.message);
                }
            }
            
            return { url, success: false, error: error.message };
        }
    }

    /**
     * УЛУЧШЕНО: Получение альтернативных URL для CSS файла
     */
    getAlternativeURLs(originalURL) {
        const alternatives = [];
        
        // Извлекаем имя файла
        const fileName = originalURL.split('/').pop().split('?')[0]; // Убираем query параметры
        
        // Пробуем в разных папках static
        const staticPaths = [
            `/static/css/${fileName}`,
            `/static/css/themes/${fileName}`,
            `/static/css/components/${fileName}`,
            `/static/css/pages/${fileName}`,
            `/static/css/base/${fileName}`,
            `/static/styles/${fileName}`, // Дополнительная папка
            `/static/${fileName}` // Прямо в static
        ];
        
        staticPaths.forEach(path => {
            const fullURL = `${this.baseURL}${path}`;
            if (!originalURL.includes(path) && !alternatives.includes(fullURL)) {
                alternatives.push(fullURL);
            }
        });
        
        // Пробуем найти в проекте по имени
        const projectFile = this.findProjectCSSFile(fileName);
        if (projectFile) {
            const projectURL = `${this.baseURL}${projectFile.url}`;
            if (!alternatives.includes(projectURL)) {
                alternatives.push(projectURL);
            }
        }

        return alternatives;
    }

    /**
     * ИСПРАВЛЕНО: Инжекция CSS в canvas без document.write
     */
    async injectCSSIntoCanvas(cssContent, sourceURL) {
        const canvas = this.editor.Canvas;
        const canvasDoc = canvas.getDocument();
        
        if (!canvasDoc) {
            console.warn('⚠️ Canvas document not ready');
            // Ждем готовности canvas
            await new Promise(resolve => {
                const checkCanvas = setInterval(() => {
                    if (canvas.getDocument()) {
                        clearInterval(checkCanvas);
                        resolve();
                    }
                }, 100);
            });
            return this.injectCSSIntoCanvas(cssContent, sourceURL);
        }
        
        // Проверяем, не добавлен ли уже этот CSS
        const existingStyle = canvasDoc.querySelector(`style[data-source="${sourceURL}"]`);
        if (existingStyle) {

            existingStyle.textContent = cssContent;
            return;
        }
        
        // Создаем style элемент БЕЗ document.write
        const styleElement = canvasDoc.createElement('style');
        styleElement.setAttribute('data-source', sourceURL);
        styleElement.setAttribute('data-loaded-by', 'ExternalCSSLoader');
        styleElement.setAttribute('type', 'text/css');
        styleElement.textContent = cssContent;
        
        // Добавляем в head
        const head = canvasDoc.head || canvasDoc.getElementsByTagName('head')[0];
        if (head) {
            head.appendChild(styleElement);

        } else {
            // Если нет head - создаем
            const newHead = canvasDoc.createElement('head');
            newHead.appendChild(styleElement);
            const htmlElement = canvasDoc.documentElement || canvasDoc.getElementsByTagName('html')[0];
            if (htmlElement) {
                htmlElement.insertBefore(newHead, htmlElement.firstChild);

            } else {
                console.warn('⚠️ Could not inject CSS - no HTML structure');
            }
        }
    }

    /**
     * Обработка относительных URL в CSS файле
     */
    processRelativeURLsInCSS(cssContent, cssURL) {
        const cssBaseURL = cssURL.substring(0, cssURL.lastIndexOf('/'));
        
        // Заменяем относительные пути в url() на абсолютные
        return cssContent.replace(/url\(\s*['"]?([^'")]+)['"]?\s*\)/g, (match, url) => {
            if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/')) {
                return match; // Уже абсолютный
            }
            
            if (url.startsWith('data:')) {
                return match; // Data URL
            }
            
            // Относительный путь - делаем абсолютным
            const absoluteURL = `${cssBaseURL}/${url}`;
            return `url('${absoluteURL}')`;
        });
    }

    /**
     * Извлечение @import из CSS
     */
    extractImportsFromCSS(cssContent) {
        const imports = [];
        const importRegex = /@import\s+(?:url\()?['"]?([^'")]+)['"]?\)?/g;
        
        let match;
        while ((match = importRegex.exec(cssContent)) !== null) {
            imports.push(match[1]);
        }
        
        return imports;
    }

    /**
     * ИСПРАВЛЕНО: Извлечение и загрузка всех внешних CSS файлов из HTML
     */
    async loadExternalCSSFromHTML(htmlContent) {

        // ИСПРАВЛЕНИЕ: Сначала очищаем Jinja2 синтаксис из HTML
        const cleanedHTML = this.cleanJinjaFromHTML(htmlContent);
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(cleanedHTML, 'text/html');
        
        // Находим все link теги с CSS
        const linkTags = doc.querySelectorAll('link[rel="stylesheet"], link[href*=".css"]');
        const cssPromises = [];

        for (const link of linkTags) {
            const href = link.getAttribute('href');
            if (href) {

                // ИСПРАВЛЕНО: Улучшенный парсинг URL
                const resolvedURL = this.resolveURL(href, htmlContent);
                if (resolvedURL && !this.loadedCSS.has(resolvedURL)) {

                    cssPromises.push(this.loadSingleCSS(resolvedURL, link));
                } else {
                    console.warn('⚠️ Could not resolve URL:', href);
                }
            }
        }

        // Также проверяем style теги с @import
        const styleTags = doc.querySelectorAll('style');
        for (const style of styleTags) {
            const imports = this.extractImportsFromCSS(style.textContent);
            for (const importURL of imports) {
                const resolvedURL = this.resolveURL(importURL, htmlContent);
                if (resolvedURL && !this.loadedCSS.has(resolvedURL)) {
                    cssPromises.push(this.loadSingleCSS(resolvedURL));
                }
            }
        }

        // Загружаем все CSS файлы параллельно
        const results = await Promise.allSettled(cssPromises);
        
        const successful = results.filter(r => r.status === 'fulfilled').length;
        const failed = results.filter(r => r.status === 'rejected').length;

        return results;
    }

    /**
     * Очистка загруженных CSS
     */
    clearLoadedCSS() {
        this.loadedCSS.clear();
        
        const canvas = this.editor.Canvas;
        const canvasDoc = canvas.getDocument();
        
        if (canvasDoc) {
            const injectedStyles = canvasDoc.querySelectorAll('style[data-loaded-by="ExternalCSSLoader"]');
            injectedStyles.forEach(style => style.remove());

        }

    }

    /**
     * Публичный метод для загрузки CSS из HTML
     */
    async loadCSSFromTemplate(htmlContent) {

        try {
            // Очищаем предыдущие CSS
            this.clearLoadedCSS();
            
            // Загружаем CSS из HTML
            const results = await this.loadExternalCSSFromHTML(htmlContent);
            
            // Также загружаем базовые CSS файлы проекта
            await this.loadBaseCSSFiles();

            return results;
            
        } catch (error) {
            console.error('❌ Error loading external CSS:', error);
            throw error;
        }
    }

    /**
     * Загрузка базовых CSS файлов проекта
     */
    async loadBaseCSSFiles() {

        const baseCSSFiles = [
            '/static/css/themes/themes.css',
            '/static/css/universal-styles.css',
            '/static/css/dental-components.css',
            '/static/css/learning_map.css',
            '/static/css/category-navigation.css'
        ];
        
        const promises = baseCSSFiles.map(url => {
            const fullURL = `${this.baseURL}${url}`;
            if (!this.loadedCSS.has(fullURL)) {
                return this.loadSingleCSS(fullURL);
            }
            return Promise.resolve({ url: fullURL, success: true, source: 'already-loaded' });
        });
        
        const results = await Promise.allSettled(promises);
        const successful = results.filter(r => r.status === 'fulfilled' && r.value.success).length;

        return results;
    }

    /**
     * Получение статистики загруженных CSS
     */
    getLoadingStats() {
        return {
            loadedCount: this.loadedCSS.size,
            cachedCount: this.cssCache.size,
            projectFilesCount: this.projectCSSFiles.length,
            loadedFiles: Array.from(this.loadedCSS),
            cacheInfo: Array.from(this.cssCache.entries()).map(([url, info]) => ({
                url,
                size: info.size,
                loadedAt: new Date(info.loadedAt).toLocaleTimeString()
            }))
        };
    }
}

// Интеграция с window
if (typeof window !== 'undefined') {
    window.ExternalCSSLoader = ExternalCSSLoader;
}
