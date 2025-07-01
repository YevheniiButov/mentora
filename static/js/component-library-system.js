// ComponentLibrarySystem — система библиотеки компонентов для GrapesJS с двуязычной поддержкой

class ComponentLibrarySystem {
    constructor(editor, options = {}) {
        this.editor = editor;
        this.options = options;
        this.language = options.language || 'ru';
        this.categories = this.getCategories();
        this.components = [];
        this.customComponents = [];
        this.usageStats = {};
        this.init();
    }

    // Категории компонентов с переводами
    getCategories() {
        return [
            { id: 'dental', label: { en: 'Dental Academy Blocks', ru: 'Блоки Dental Academy' } },
            { id: 'layout', label: { en: 'Layout Components', ru: 'Компоненты макета' } },
            { id: 'content', label: { en: 'Content Components', ru: 'Контентные компоненты' } },
            { id: 'form', label: { en: 'Form Components', ru: 'Формы' } },
            { id: 'interactive', label: { en: 'Interactive Components', ru: 'Интерактивные компоненты' } },
        ];
    }

    // Инициализация системы
    init() {
        this.loadDefaultComponents();
        this.createBlocksPanel();
        this.createComponentInspector();
        this.createComponentBuilder();
        this.createSearchAndFilter();
        this.createImportExport();
        this.createUsageAnalytics();
    }

    // Загрузка стандартных компонентов (пример)
    loadDefaultComponents() {
        this.components = [
            {
                id: 'subject-card',
                category: 'dental',
                label: { en: 'Subject Card', ru: 'Карточка предмета' },
                description: { en: 'Reusable subject card block', ru: 'Переиспользуемая карточка предмета' },
                html: `<div class="card subject-card"><div class="card-body"><h5>Subject</h5><p>Description</p></div></div>`,
                traits: [
                    { name: 'title', label: { en: 'Title', ru: 'Заголовок' }, type: 'text' },
                    { name: 'desc', label: { en: 'Description', ru: 'Описание' }, type: 'textarea' }
                ],
                style: '',
                version: 1
            },
            {
                id: 'progress-bar',
                category: 'dental',
                label: { en: 'Progress Bar', ru: 'Прогресс-бар' },
                description: { en: 'Progress indicator', ru: 'Индикатор прогресса' },
                html: `<div class="progress-bar-container"><div class="progress-bar-fill" style="width: 50%"></div></div>`,
                traits: [
                    { name: 'progress', label: { en: 'Progress (%)', ru: 'Прогресс (%)' }, type: 'number', min: 0, max: 100 }
                ],
                style: '',
                version: 1
            },
            {
                id: 'navigation-block',
                category: 'dental',
                label: { en: 'Navigation', ru: 'Навигация' },
                description: { en: 'Navigation element', ru: 'Элемент навигации' },
                html: `<nav class="nav-list"><a class="nav-link active">Link</a></nav>`,
                traits: [
                    { name: 'links', label: { en: 'Links', ru: 'Ссылки' }, type: 'list' }
                ],
                style: '',
                version: 1
            },
            // ... layout, content, form, interactive (accordion, modal, etc.)
        ];
    }

    // Создание панели блоков с категориями и поиском
    createBlocksPanel() {
        const { editor, categories, components, language } = this;
        const blockManager = editor.BlockManager;
        categories.forEach(cat => {
            blockManager.addCategory(cat.id, {
                label: cat.label[language],
                open: true
            });
        });
        components.forEach(comp => {
            blockManager.add(comp.id, {
                label: comp.label[language],
                category: comp.category,
                attributes: { title: comp.description[language] },
                content: comp.html,
                media: '<svg width="20" height="20"><rect width="20" height="20" fill="#3ECDC1"/></svg>'
            });
        });
    }

    // Панель инспектора компонента
    createComponentInspector() {
        // Добавляет инспектор для выбранного компонента с трейтом, версией, статистикой
        // ... (реализация зависит от GrapesJS версии)
    }

    // Визуальный редактор/билдер компонента
    createComponentBuilder() {
        // Позволяет собирать компонент из блоков, настраивать трейты, стили, preview
        // ... (визуальный интерфейс, drag&drop, preview)
    }

    // Поиск и фильтрация компонентов (двуязычно)
    createSearchAndFilter() {
        // Добавляет строку поиска и фильтр по категориям, поддерживает оба языка
        // ...
    }

    // Импорт/экспорт библиотеки компонентов
    createImportExport() {
        // Позволяет экспортировать/импортировать JSON с компонентами, поддерживает версии
        // ...
    }

    // Аналитика использования компонентов
    createUsageAnalytics() {
        // Считает сколько раз компонент добавлен, когда обновлялся, кем
        // ...
    }

    // Сохранение пользовательского компонента
    saveCustomComponent(component) {
        this.customComponents.push(component);
        // ... (сохранение в localStorage или сервер)
    }

    // Импорт компонентов
    importComponents(json) {
        // ...
    }

    // Экспорт компонентов
    exportComponents() {
        // ...
    }

    // Глобальное обновление компонента
    updateGlobalComponent(id, newData) {
        // ...
    }

    // Проверка доступности (accessibility)
    checkAccessibility(component) {
        // ...
    }

    // Двуязычный перевод
    t(obj) {
        return obj[this.language] || obj['en'] || '';
    }
}

// GrapesJS plugin
if (typeof grapesjs !== 'undefined') {
    grapesjs.plugins.add('component-library-system', (editor, opts = {}) => {
        new ComponentLibrarySystem(editor, opts);
    });
}

// Экспорт для Node
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComponentLibrarySystem;
} 