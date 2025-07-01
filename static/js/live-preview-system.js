// LivePreviewSystem — система живого предпросмотра для GrapesJS с двуязычной поддержкой

class LivePreviewSystem {
    constructor(editor, options = {}) {
        this.editor = editor;
        this.language = options.language || 'ru';
        this.devices = this.getDevices();
        this.previews = {};
        this.mode = 'full'; // full, component, print, accessibility
        this.history = [];
        this.comments = [];
        this.init();
    }

    // Список устройств с переводами
    getDevices() {
        return [
            { id: 'iphone', label: { en: 'iPhone', ru: 'Айфон' }, width: 375, height: 812 },
            { id: 'ipad', label: { en: 'iPad', ru: 'Айпад' }, width: 768, height: 1024 },
            { id: 'desktop', label: { en: 'Desktop', ru: 'Десктоп' }, width: 1200, height: 800 }
        ];
    }

    // Инициализация системы предпросмотра
    init() {
        this.createPreviewPanel();
        this.createPreviewIframes();
        this.createPreviewControls();
        this.bindEditorEvents();
        this.bindPreviewEvents();
    }

    // Панель предпросмотра
    createPreviewPanel() {
        const panel = document.createElement('div');
        panel.className = 'live-preview-panel';
        panel.innerHTML = `
            <div class="preview-toolbar">
                <select id="preview-mode">
                    <option value="full">${this.t({en:'Full Page',ru:'Вся страница'})}</option>
                    <option value="component">${this.t({en:'Component Only',ru:'Только компонент'})}</option>
                    <option value="print">${this.t({en:'Print Preview',ru:'Печать'})}</option>
                    <option value="accessibility">${this.t({en:'Accessibility',ru:'Доступность'})}</option>
                </select>
                <button id="preview-share">${this.t({en:'Share Preview',ru:'Поделиться'})}</button>
                <button id="preview-screenshot">${this.t({en:'Screenshot',ru:'Скриншот'})}</button>
                <button id="preview-history">${this.t({en:'History',ru:'История'})}</button>
            </div>
            <div class="preview-devices">
                ${this.devices.map(d => `
                    <div class="device-frame" data-device="${d.id}" style="width:${d.width}px;height:${d.height}px">
                        <div class="device-label">${this.t(d.label)}</div>
                        <iframe id="preview-${d.id}" class="preview-iframe"></iframe>
                    </div>
                `).join('')}
            </div>
            <div class="preview-performance" id="preview-performance"></div>
            <div class="preview-comments" id="preview-comments"></div>
        `;
        document.body.appendChild(panel);
        this.panel = panel;
    }

    // Создание iframe для каждого устройства
    createPreviewIframes() {
        this.devices.forEach(d => {
            this.previews[d.id] = document.getElementById(`preview-${d.id}`);
        });
    }

    // Контролы предпросмотра
    createPreviewControls() {
        document.getElementById('preview-mode').addEventListener('change', e => {
            this.mode = e.target.value;
            this.updateAllPreviews();
        });
        document.getElementById('preview-share').onclick = () => this.generateShareUrl();
        document.getElementById('preview-screenshot').onclick = () => this.generateScreenshot();
        document.getElementById('preview-history').onclick = () => this.showHistory();
    }

    // События GrapesJS
    bindEditorEvents() {
        this.editor.on('component:update component:selected style:propertychange', () => {
            this.updateAllPreviews();
        });
        this.editor.on('load', () => {
            this.updateAllPreviews();
        });
    }

    // События предпросмотра (скролл, интерактивность)
    bindPreviewEvents() {
        // Синхронизация скролла
        this.devices.forEach(d => {
            const iframe = this.previews[d.id];
            iframe.addEventListener('load', () => {
                const win = iframe.contentWindow;
                win.addEventListener('scroll', () => {
                    this.syncScroll(d.id, win.scrollY);
                });
            });
        });
    }

    // Синхронизация скролла между устройствами
    syncScroll(sourceId, scrollY) {
        this.devices.forEach(d => {
            if (d.id !== sourceId) {
                const win = this.previews[d.id].contentWindow;
                win.scrollTo(0, scrollY);
            }
        });
    }

    // Обновление всех предпросмотров
    updateAllPreviews() {
        this.devices.forEach(d => this.updatePreview(d.id));
        this.analyzePerformance();
    }

    // Обновление предпросмотра для устройства
    updatePreview(deviceId) {
        const iframe = this.previews[deviceId];
        if (!iframe) return;
        let html = '', css = '', js = '';
        if (this.mode === 'component') {
            const selected = this.editor.getSelected();
            if (selected) {
                html = selected.toHTML();
                css = selected.toCSS();
            }
        } else {
            html = this.editor.getHtml();
            css = this.editor.getCss();
        }
        // Интеграция с Flask: подгружаем все нужные CSS/JS
        const assets = this.getProjectAssets();
        // Jinja2: сохраняем переменные как есть
        iframe.srcdoc = `<!DOCTYPE html><html><head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            ${assets.css}
            <style>${css}</style>
            </head><body>
            ${html}
            ${assets.js}
            <script>window.parent.postMessage({type:'previewReady',device:'${deviceId}'},'*');</script>
            </body></html>`;
    }

    // Получение CSS/JS проекта (Flask)
    getProjectAssets() {
        // Можно доработать для динамической загрузки
        return {
            css: [
                '<link rel="stylesheet" href="/static/css/themes/themes.css">',
                '<link rel="stylesheet" href="/static/css/universal-styles.css">',
                '<link rel="stylesheet" href="/static/css/universal-layout-system.css">',
                '<link rel="stylesheet" href="/static/css/components/components.css">'
            ].join('\n'),
            js: [
                // Можно добавить JS-плагины
            ].join('\n')
        };
    }

    // Генерация URL предпросмотра для шаринга
    generateShareUrl() {
        const url = window.location.href + '?preview=' + Date.now();
        window.prompt(this.t({en:'Share this URL:',ru:'Поделитесь этой ссылкой:'}), url);
    }

    // Генерация скриншота (заготовка)
    generateScreenshot() {
        alert(this.t({en:'Screenshot feature coming soon',ru:'Скриншоты скоро будут доступны'}));
    }

    // История предпросмотров (before/after)
    showHistory() {
        alert(this.t({en:'Preview history coming soon',ru:'История предпросмотров скоро будет доступна'}));
    }

    // Анализ производительности
    analyzePerformance() {
        // Пример: анализ размера CSS/JS, советы по оптимизации
        const css = this.editor.getCss();
        const js = '';
        const imgCount = (this.editor.getHtml().match(/<img /g) || []).length;
        let perf = '';
        perf += `<div>${this.t({en:'CSS size',ru:'Размер CSS'})}: ${(css.length/1024).toFixed(1)} KB</div>`;
        perf += `<div>${this.t({en:'Images on page',ru:'Изображений на странице'})}: ${imgCount}</div>`;
        if (imgCount > 10) {
            perf += `<div class='perf-warning'>${this.t({en:'Too many images! Optimize for mobile.',ru:'Слишком много изображений! Оптимизируйте для мобильных.'})}</div>`;
        }
        document.getElementById('preview-performance').innerHTML = perf;
    }

    // Двуязычный перевод
    t(obj) {
        return obj[this.language] || obj['en'] || '';
    }
}

// GrapesJS plugin
if (typeof grapesjs !== 'undefined') {
    grapesjs.plugins.add('live-preview-system', (editor, opts = {}) => {
        new LivePreviewSystem(editor, opts);
    });
}

// Экспорт для Node
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LivePreviewSystem;
}

// Стили для панели предпросмотра
const livePreviewStyles = `
<style>
.live-preview-panel { position: fixed; top: 0; right: 0; width: 100vw; height: 60vh; background: #f8fafc; z-index: 9999; box-shadow: 0 2px 16px rgba(0,0,0,0.12); padding: 10px; overflow: auto; }
.preview-toolbar { display: flex; gap: 10px; margin-bottom: 10px; }
.preview-devices { display: flex; gap: 20px; justify-content: center; }
.device-frame { background: #222; border-radius: 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.18); position: relative; margin-bottom: 10px; }
.device-label { position: absolute; top: 8px; left: 50%; transform: translateX(-50%); color: #fff; font-size: 13px; background: rgba(0,0,0,0.4); padding: 2px 10px; border-radius: 8px; z-index: 2; }
.preview-iframe { width: 100%; height: 100%; border: none; border-radius: 12px; background: #fff; }
.preview-performance { margin-top: 10px; font-size: 13px; color: #333; }
.perf-warning { color: #e74c3c; font-weight: bold; }
</style>
`;
document.head.insertAdjacentHTML('beforeend', livePreviewStyles); 