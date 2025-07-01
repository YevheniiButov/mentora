/**
 * Editor Components - Переиспользуемые компоненты для Content Editor
 * Библиотека компонентов с конфигурацией, рендерингом и свойствами
 */

class EditorComponents {
    constructor() {
        this.components = this.initializeComponents();
        this.init();
    }

    /**
     * Инициализация
     */
    init() {
        console.log('🚀 Initializing Editor Components...');
        this.registerComponents();
        console.log('✅ Editor Components initialized successfully!');
    }

    /**
     * Инициализация компонентов
     */
    initializeComponents() {
        return {
            // Текстовые компоненты
            text: {
                name: 'Текстовый блок',
                icon: 'text-paragraph',
                category: 'text',
                defaultContent: '<p>Введите текст здесь...</p>',
                defaultProperties: {
                    fontSize: '16px',
                    textColor: '#000000',
                    textAlign: 'left',
                    fontWeight: 'normal',
                    lineHeight: '1.5'
                },
                properties: [
                    {
                        name: 'fontSize',
                        label: 'Размер шрифта',
                        type: 'select',
                        defaultValue: '16px',
                        options: [
                            { value: '12px', label: '12px' },
                            { value: '14px', label: '14px' },
                            { value: '16px', label: '16px' },
                            { value: '18px', label: '18px' },
                            { value: '20px', label: '20px' },
                            { value: '24px', label: '24px' },
                            { value: '28px', label: '28px' },
                            { value: '32px', label: '32px' }
                        ]
                    },
                    {
                        name: 'textColor',
                        label: 'Цвет текста',
                        type: 'color',
                        defaultValue: '#000000'
                    },
                    {
                        name: 'textAlign',
                        label: 'Выравнивание',
                        type: 'select',
                        defaultValue: 'left',
                        options: [
                            { value: 'left', label: 'По левому краю' },
                            { value: 'center', label: 'По центру' },
                            { value: 'right', label: 'По правому краю' },
                            { value: 'justify', label: 'По ширине' }
                        ]
                    },
                    {
                        name: 'fontWeight',
                        label: 'Жирность',
                        type: 'select',
                        defaultValue: 'normal',
                        options: [
                            { value: 'normal', label: 'Обычный' },
                            { value: 'bold', label: 'Жирный' },
                            { value: 'lighter', label: 'Тонкий' }
                        ]
                    },
                    {
                        name: 'lineHeight',
                        label: 'Высота строки',
                        type: 'select',
                        defaultValue: '1.5',
                        options: [
                            { value: '1.2', label: '1.2' },
                            { value: '1.4', label: '1.4' },
                            { value: '1.5', label: '1.5' },
                            { value: '1.8', label: '1.8' },
                            { value: '2.0', label: '2.0' }
                        ]
                    }
                ],
                render: (component) => {
                    const style = `
                        font-size: ${component.properties.fontSize || '16px'};
                        color: ${component.properties.textColor || '#000000'};
                        text-align: ${component.properties.textAlign || 'left'};
                        font-weight: ${component.properties.fontWeight || 'normal'};
                        line-height: ${component.properties.lineHeight || '1.5'};
                    `;
                    return `<div class="text-component" style="${style}">${component.content}</div>`;
                }
            },

            heading: {
                name: 'Заголовок',
                icon: 'type-h1',
                category: 'text',
                defaultContent: '<h2>Заголовок</h2>',
                defaultProperties: {
                    level: 'h2',
                    textColor: '#000000',
                    textAlign: 'left',
                    fontWeight: 'bold'
                },
                properties: [
                    {
                        name: 'level',
                        label: 'Уровень заголовка',
                        type: 'select',
                        defaultValue: 'h2',
                        options: [
                            { value: 'h1', label: 'H1 - Главный' },
                            { value: 'h2', label: 'H2 - Подзаголовок' },
                            { value: 'h3', label: 'H3 - Раздел' },
                            { value: 'h4', label: 'H4 - Подраздел' },
                            { value: 'h5', label: 'H5 - Пункт' },
                            { value: 'h6', label: 'H6 - Подпункт' }
                        ]
                    },
                    {
                        name: 'textColor',
                        label: 'Цвет текста',
                        type: 'color',
                        defaultValue: '#000000'
                    },
                    {
                        name: 'textAlign',
                        label: 'Выравнивание',
                        type: 'select',
                        defaultValue: 'left',
                        options: [
                            { value: 'left', label: 'По левому краю' },
                            { value: 'center', label: 'По центру' },
                            { value: 'right', label: 'По правому краю' }
                        ]
                    },
                    {
                        name: 'fontWeight',
                        label: 'Жирность',
                        type: 'select',
                        defaultValue: 'bold',
                        options: [
                            { value: 'normal', label: 'Обычный' },
                            { value: 'bold', label: 'Жирный' },
                            { value: 'lighter', label: 'Тонкий' }
                        ]
                    }
                ],
                render: (component) => {
                    const level = component.properties.level || 'h2';
                    const style = `
                        color: ${component.properties.textColor || '#000000'};
                        text-align: ${component.properties.textAlign || 'left'};
                        font-weight: ${component.properties.fontWeight || 'bold'};
                    `;
                    return `<${level} class="heading-component" style="${style}">${component.content.replace(/<h\d[^>]*>(.*?)<\/h\d>/i, '$1')}</${level}>`;
                }
            },

            // Медиа компоненты
            image: {
                name: 'Изображение',
                icon: 'image',
                category: 'media',
                defaultContent: '<div class="image-placeholder"><i class="bi bi-image"></i><p>Изображение</p></div>',
                defaultProperties: {
                    src: '',
                    alt: '',
                    width: '100%',
                    height: 'auto',
                    borderRadius: '0px',
                    shadow: 'none'
                },
                properties: [
                    {
                        name: 'src',
                        label: 'URL изображения',
                        type: 'text',
                        placeholder: 'Введите URL изображения'
                    },
                    {
                        name: 'alt',
                        label: 'Альтернативный текст',
                        type: 'text',
                        placeholder: 'Описание изображения'
                    },
                    {
                        name: 'width',
                        label: 'Ширина',
                        type: 'text',
                        defaultValue: '100%',
                        placeholder: '100% или 300px'
                    },
                    {
                        name: 'height',
                        label: 'Высота',
                        type: 'text',
                        defaultValue: 'auto',
                        placeholder: 'auto или 200px'
                    },
                    {
                        name: 'borderRadius',
                        label: 'Скругление углов',
                        type: 'select',
                        defaultValue: '0px',
                        options: [
                            { value: '0px', label: 'Без скругления' },
                            { value: '4px', label: '4px' },
                            { value: '8px', label: '8px' },
                            { value: '12px', label: '12px' },
                            { value: '16px', label: '16px' },
                            { value: '50%', label: 'Круглое' }
                        ]
                    },
                    {
                        name: 'shadow',
                        label: 'Тень',
                        type: 'select',
                        defaultValue: 'none',
                        options: [
                            { value: 'none', label: 'Без тени' },
                            { value: 'small', label: 'Маленькая' },
                            { value: 'medium', label: 'Средняя' },
                            { value: 'large', label: 'Большая' }
                        ]
                    }
                ],
                render: (component) => {
                    const src = component.properties.src;
                    if (!src) {
                        return component.defaultContent;
                    }

                    const style = `
                        width: ${component.properties.width || '100%'};
                        height: ${component.properties.height || 'auto'};
                        border-radius: ${component.properties.borderRadius || '0px'};
                        box-shadow: ${this.getShadowStyle(component.properties.shadow)};
                    `;

                    return `<img src="${src}" alt="${component.properties.alt || ''}" style="${style}" class="image-component">`;
                }
            },

            video: {
                name: 'Видео',
                icon: 'play-circle',
                category: 'media',
                defaultContent: '<div class="video-placeholder"><i class="bi bi-play-circle"></i><p>Видео</p></div>',
                defaultProperties: {
                    src: '',
                    width: '100%',
                    height: 'auto',
                    controls: true,
                    autoplay: false,
                    muted: false,
                    loop: false
                },
                properties: [
                    {
                        name: 'src',
                        label: 'URL видео',
                        type: 'text',
                        placeholder: 'Введите URL видео'
                    },
                    {
                        name: 'width',
                        label: 'Ширина',
                        type: 'text',
                        defaultValue: '100%',
                        placeholder: '100% или 640px'
                    },
                    {
                        name: 'height',
                        label: 'Высота',
                        type: 'text',
                        defaultValue: 'auto',
                        placeholder: 'auto или 360px'
                    },
                    {
                        name: 'controls',
                        label: 'Элементы управления',
                        type: 'checkbox',
                        defaultValue: true
                    },
                    {
                        name: 'autoplay',
                        label: 'Автовоспроизведение',
                        type: 'checkbox',
                        defaultValue: false
                    },
                    {
                        name: 'muted',
                        label: 'Без звука',
                        type: 'checkbox',
                        defaultValue: false
                    },
                    {
                        name: 'loop',
                        label: 'Зацикливание',
                        type: 'checkbox',
                        defaultValue: false
                    }
                ],
                render: (component) => {
                    const src = component.properties.src;
                    if (!src) {
                        return component.defaultContent;
                    }

                    const controls = component.properties.controls ? 'controls' : '';
                    const autoplay = component.properties.autoplay ? 'autoplay' : '';
                    const muted = component.properties.muted ? 'muted' : '';
                    const loop = component.properties.loop ? 'loop' : '';

                    const style = `
                        width: ${component.properties.width || '100%'};
                        height: ${component.properties.height || 'auto'};
                    `;

                    return `<video src="${src}" ${controls} ${autoplay} ${muted} ${loop} style="${style}" class="video-component"></video>`;
                }
            },

            // Интерактивные компоненты
            button: {
                name: 'Кнопка',
                icon: 'cursor',
                category: 'interactive',
                defaultContent: '<button class="component-button">Кнопка</button>',
                defaultProperties: {
                    text: 'Кнопка',
                    backgroundColor: '#3ECDC1',
                    textColor: '#ffffff',
                    borderRadius: '8px',
                    padding: '12px 24px',
                    fontSize: '16px',
                    fontWeight: 'bold'
                },
                properties: [
                    {
                        name: 'text',
                        label: 'Текст кнопки',
                        type: 'text',
                        defaultValue: 'Кнопка',
                        placeholder: 'Введите текст кнопки'
                    },
                    {
                        name: 'backgroundColor',
                        label: 'Цвет фона',
                        type: 'color',
                        defaultValue: '#3ECDC1'
                    },
                    {
                        name: 'textColor',
                        label: 'Цвет текста',
                        type: 'color',
                        defaultValue: '#ffffff'
                    },
                    {
                        name: 'borderRadius',
                        label: 'Скругление углов',
                        type: 'select',
                        defaultValue: '8px',
                        options: [
                            { value: '0px', label: 'Без скругления' },
                            { value: '4px', label: '4px' },
                            { value: '8px', label: '8px' },
                            { value: '12px', label: '12px' },
                            { value: '20px', label: '20px' },
                            { value: '50px', label: 'Сильно скруглено' }
                        ]
                    },
                    {
                        name: 'padding',
                        label: 'Отступы',
                        type: 'select',
                        defaultValue: '12px 24px',
                        options: [
                            { value: '8px 16px', label: 'Маленькие' },
                            { value: '12px 24px', label: 'Средние' },
                            { value: '16px 32px', label: 'Большие' },
                            { value: '20px 40px', label: 'Очень большие' }
                        ]
                    },
                    {
                        name: 'fontSize',
                        label: 'Размер шрифта',
                        type: 'select',
                        defaultValue: '16px',
                        options: [
                            { value: '14px', label: '14px' },
                            { value: '16px', label: '16px' },
                            { value: '18px', label: '18px' },
                            { value: '20px', label: '20px' },
                            { value: '24px', label: '24px' }
                        ]
                    },
                    {
                        name: 'fontWeight',
                        label: 'Жирность',
                        type: 'select',
                        defaultValue: 'bold',
                        options: [
                            { value: 'normal', label: 'Обычный' },
                            { value: 'bold', label: 'Жирный' },
                            { value: 'lighter', label: 'Тонкий' }
                        ]
                    }
                ],
                render: (component) => {
                    const text = component.properties.text || 'Кнопка';
                    const style = `
                        background-color: ${component.properties.backgroundColor || '#3ECDC1'};
                        color: ${component.properties.textColor || '#ffffff'};
                        border-radius: ${component.properties.borderRadius || '8px'};
                        padding: ${component.properties.padding || '12px 24px'};
                        font-size: ${component.properties.fontSize || '16px'};
                        font-weight: ${component.properties.fontWeight || 'bold'};
                        border: none;
                        cursor: pointer;
                        transition: all 0.3s ease;
                    `;

                    return `<button class="component-button" style="${style}">${text}</button>`;
                }
            },

            // Структурные компоненты
            card: {
                name: 'Карточка',
                icon: 'card-text',
                category: 'layout',
                defaultContent: '<div class="card-content"><h3>Заголовок карточки</h3><p>Содержимое карточки</p></div>',
                defaultProperties: {
                    backgroundColor: '#ffffff',
                    borderColor: '#e0e0e0',
                    borderRadius: '12px',
                    padding: '20px',
                    shadow: 'medium'
                },
                properties: [
                    {
                        name: 'backgroundColor',
                        label: 'Цвет фона',
                        type: 'color',
                        defaultValue: '#ffffff'
                    },
                    {
                        name: 'borderColor',
                        label: 'Цвет границы',
                        type: 'color',
                        defaultValue: '#e0e0e0'
                    },
                    {
                        name: 'borderRadius',
                        label: 'Скругление углов',
                        type: 'select',
                        defaultValue: '12px',
                        options: [
                            { value: '0px', label: 'Без скругления' },
                            { value: '4px', label: '4px' },
                            { value: '8px', label: '8px' },
                            { value: '12px', label: '12px' },
                            { value: '16px', label: '16px' },
                            { value: '20px', label: '20px' }
                        ]
                    },
                    {
                        name: 'padding',
                        label: 'Внутренние отступы',
                        type: 'select',
                        defaultValue: '20px',
                        options: [
                            { value: '10px', label: '10px' },
                            { value: '15px', label: '15px' },
                            { value: '20px', label: '20px' },
                            { value: '25px', label: '25px' },
                            { value: '30px', label: '30px' }
                        ]
                    },
                    {
                        name: 'shadow',
                        label: 'Тень',
                        type: 'select',
                        defaultValue: 'medium',
                        options: [
                            { value: 'none', label: 'Без тени' },
                            { value: 'small', label: 'Маленькая' },
                            { value: 'medium', label: 'Средняя' },
                            { value: 'large', label: 'Большая' }
                        ]
                    }
                ],
                render: (component) => {
                    const style = `
                        background-color: ${component.properties.backgroundColor || '#ffffff'};
                        border: 1px solid ${component.properties.borderColor || '#e0e0e0'};
                        border-radius: ${component.properties.borderRadius || '12px'};
                        padding: ${component.properties.padding || '20px'};
                        box-shadow: ${this.getShadowStyle(component.properties.shadow)};
                    `;

                    return `<div class="card-component" style="${style}">${component.content}</div>`;
                }
            },

            divider: {
                name: 'Разделитель',
                icon: 'dash',
                category: 'layout',
                defaultContent: '<hr class="component-divider">',
                defaultProperties: {
                    color: '#e0e0e0',
                    width: '100%',
                    height: '2px',
                    style: 'solid'
                },
                properties: [
                    {
                        name: 'color',
                        label: 'Цвет линии',
                        type: 'color',
                        defaultValue: '#e0e0e0'
                    },
                    {
                        name: 'width',
                        label: 'Ширина',
                        type: 'select',
                        defaultValue: '100%',
                        options: [
                            { value: '25%', label: '25%' },
                            { value: '50%', label: '50%' },
                            { value: '75%', label: '75%' },
                            { value: '100%', label: '100%' }
                        ]
                    },
                    {
                        name: 'height',
                        label: 'Толщина',
                        type: 'select',
                        defaultValue: '2px',
                        options: [
                            { value: '1px', label: '1px' },
                            { value: '2px', label: '2px' },
                            { value: '3px', label: '3px' },
                            { value: '4px', label: '4px' },
                            { value: '5px', label: '5px' }
                        ]
                    },
                    {
                        name: 'style',
                        label: 'Стиль линии',
                        type: 'select',
                        defaultValue: 'solid',
                        options: [
                            { value: 'solid', label: 'Сплошная' },
                            { value: 'dashed', label: 'Пунктирная' },
                            { value: 'dotted', label: 'Точечная' },
                            { value: 'double', label: 'Двойная' }
                        ]
                    }
                ],
                render: (component) => {
                    const style = `
                        border: none;
                        border-top: ${component.properties.height || '2px'} ${component.properties.style || 'solid'} ${component.properties.color || '#e0e0e0'};
                        width: ${component.properties.width || '100%'};
                        margin: 20px 0;
                    `;

                    return `<hr class="divider-component" style="${style}">`;
                }
            },

            // Специальные компоненты
            table: {
                name: 'Таблица',
                icon: 'table',
                category: 'data',
                defaultContent: `
                    <table class="component-table">
                        <thead>
                            <tr><th>Заголовок 1</th><th>Заголовок 2</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>Ячейка 1</td><td>Ячейка 2</td></tr>
                        </tbody>
                    </table>
                `,
                defaultProperties: {
                    borderColor: '#e0e0e0',
                    headerBackground: '#f8f9fa',
                    cellPadding: '12px',
                    borderWidth: '1px'
                },
                properties: [
                    {
                        name: 'borderColor',
                        label: 'Цвет границ',
                        type: 'color',
                        defaultValue: '#e0e0e0'
                    },
                    {
                        name: 'headerBackground',
                        label: 'Фон заголовков',
                        type: 'color',
                        defaultValue: '#f8f9fa'
                    },
                    {
                        name: 'cellPadding',
                        label: 'Отступы ячеек',
                        type: 'select',
                        defaultValue: '12px',
                        options: [
                            { value: '8px', label: '8px' },
                            { value: '12px', label: '12px' },
                            { value: '16px', label: '16px' },
                            { value: '20px', label: '20px' }
                        ]
                    },
                    {
                        name: 'borderWidth',
                        label: 'Толщина границ',
                        type: 'select',
                        defaultValue: '1px',
                        options: [
                            { value: '0px', label: 'Без границ' },
                            { value: '1px', label: '1px' },
                            { value: '2px', label: '2px' },
                            { value: '3px', label: '3px' }
                        ]
                    }
                ],
                render: (component) => {
                    const style = `
                        border-collapse: collapse;
                        width: 100%;
                        border: ${component.properties.borderWidth || '1px'} solid ${component.properties.borderColor || '#e0e0e0'};
                    `;

                    const thStyle = `
                        background-color: ${component.properties.headerBackground || '#f8f9fa'};
                        padding: ${component.properties.cellPadding || '12px'};
                        border: ${component.properties.borderWidth || '1px'} solid ${component.properties.borderColor || '#e0e0e0'};
                        font-weight: bold;
                    `;

                    const tdStyle = `
                        padding: ${component.properties.cellPadding || '12px'};
                        border: ${component.properties.borderWidth || '1px'} solid ${component.properties.borderColor || '#e0e0e0'};
                    `;

                    // Заменяем стили в существующей таблице
                    let tableHTML = component.content;
                    tableHTML = tableHTML.replace(/<table[^>]*>/i, `<table class="component-table" style="${style}">`);
                    tableHTML = tableHTML.replace(/<th[^>]*>/gi, `<th style="${thStyle}">`);
                    tableHTML = tableHTML.replace(/<td[^>]*>/gi, `<td style="${tdStyle}">`);

                    return tableHTML;
                }
            },

            code: {
                name: 'Код',
                icon: 'code-slash',
                category: 'special',
                defaultContent: '<pre><code>// Введите код здесь</code></pre>',
                defaultProperties: {
                    language: 'javascript',
                    theme: 'light',
                    fontSize: '14px',
                    backgroundColor: '#f8f9fa'
                },
                properties: [
                    {
                        name: 'language',
                        label: 'Язык программирования',
                        type: 'select',
                        defaultValue: 'javascript',
                        options: [
                            { value: 'html', label: 'HTML' },
                            { value: 'css', label: 'CSS' },
                            { value: 'javascript', label: 'JavaScript' },
                            { value: 'python', label: 'Python' },
                            { value: 'php', label: 'PHP' },
                            { value: 'java', label: 'Java' },
                            { value: 'csharp', label: 'C#' },
                            { value: 'cpp', label: 'C++' },
                            { value: 'sql', label: 'SQL' },
                            { value: 'bash', label: 'Bash' }
                        ]
                    },
                    {
                        name: 'theme',
                        label: 'Тема',
                        type: 'select',
                        defaultValue: 'light',
                        options: [
                            { value: 'light', label: 'Светлая' },
                            { value: 'dark', label: 'Темная' },
                            { value: 'github', label: 'GitHub' },
                            { value: 'monokai', label: 'Monokai' }
                        ]
                    },
                    {
                        name: 'fontSize',
                        label: 'Размер шрифта',
                        type: 'select',
                        defaultValue: '14px',
                        options: [
                            { value: '12px', label: '12px' },
                            { value: '14px', label: '14px' },
                            { value: '16px', label: '16px' },
                            { value: '18px', label: '18px' }
                        ]
                    },
                    {
                        name: 'backgroundColor',
                        label: 'Цвет фона',
                        type: 'color',
                        defaultValue: '#f8f9fa'
                    }
                ],
                render: (component) => {
                    const style = `
                        background-color: ${component.properties.backgroundColor || '#f8f9fa'};
                        font-size: ${component.properties.fontSize || '14px'};
                        padding: 16px;
                        border-radius: 8px;
                        border: 1px solid #e0e0e0;
                        overflow-x: auto;
                        font-family: 'Courier New', monospace;
                    `;

                    const language = component.properties.language || 'javascript';
                    const theme = component.properties.theme || 'light';

                    return `<pre class="code-component code-${theme}" style="${style}"><code class="language-${language}">${component.content.replace(/<pre[^>]*><code[^>]*>(.*?)<\/code><\/pre>/is, '$1')}</code></pre>`;
                }
            }
        };
    }

    /**
     * Регистрация компонентов
     */
    registerComponents() {
        // Регистрируем компоненты в глобальном объекте
        window.editorComponents = this;
    }

    /**
     * Получение компонента по типу
     */
    getComponent(type) {
        return this.components[type] || null;
    }

    /**
     * Получение всех компонентов
     */
    getAllComponents() {
        return this.components;
    }

    /**
     * Получение компонентов по категории
     */
    getComponentsByCategory(category) {
        return Object.entries(this.components)
            .filter(([key, component]) => component.category === category)
            .reduce((acc, [key, component]) => {
                acc[key] = component;
                return acc;
            }, {});
    }

    /**
     * Получение списка категорий
     */
    getCategories() {
        const categories = new Set();
        Object.values(this.components).forEach(component => {
            if (component.category) {
                categories.add(component.category);
            }
        });
        return Array.from(categories);
    }

    /**
     * Добавление нового компонента
     */
    addComponent(type, config) {
        if (this.components[type]) {
            console.warn(`Component ${type} already exists. Overwriting...`);
        }
        
        this.components[type] = {
            name: config.name || 'Новый компонент',
            icon: config.icon || 'box',
            category: config.category || 'other',
            defaultContent: config.defaultContent || '',
            defaultProperties: config.defaultProperties || {},
            properties: config.properties || [],
            render: config.render || ((component) => component.content)
        };
    }

    /**
     * Удаление компонента
     */
    removeComponent(type) {
        if (this.components[type]) {
            delete this.components[type];
            return true;
        }
        return false;
    }

    /**
     * Валидация компонента
     */
    validateComponent(component) {
        const errors = [];
        
        if (!component.name) {
            errors.push('Название компонента обязательно');
        }
        
        if (!component.icon) {
            errors.push('Иконка компонента обязательна');
        }
        
        if (!component.category) {
            errors.push('Категория компонента обязательна');
        }
        
        if (!component.render || typeof component.render !== 'function') {
            errors.push('Функция рендеринга обязательна');
        }
        
        return {
            isValid: errors.length === 0,
            errors: errors
        };
    }

    /**
     * Клонирование компонента
     */
    cloneComponent(type, newType) {
        const original = this.components[type];
        if (!original) {
            throw new Error(`Component ${type} not found`);
        }
        
        this.components[newType] = {
            ...original,
            name: `${original.name} (копия)`,
            defaultContent: original.defaultContent
        };
        
        return this.components[newType];
    }

    /**
     * Экспорт компонента в JSON
     */
    exportComponent(type) {
        const component = this.components[type];
        if (!component) {
            throw new Error(`Component ${type} not found`);
        }
        
        return JSON.stringify(component, null, 2);
    }

    /**
     * Импорт компонента из JSON
     */
    importComponent(type, jsonString) {
        try {
            const component = JSON.parse(jsonString);
            const validation = this.validateComponent(component);
            
            if (!validation.isValid) {
                throw new Error('Неверный формат компонента: ' + validation.errors.join(', '));
            }
            
            this.components[type] = component;
            return true;
        } catch (error) {
            console.error('Error importing component:', error);
            return false;
        }
    }

    /**
     * Утилиты для стилей
     */
    getShadowStyle(shadowType) {
        const shadows = {
            none: 'none',
            small: '0 2px 4px rgba(0,0,0,0.1)',
            medium: '0 4px 8px rgba(0,0,0,0.15)',
            large: '0 8px 16px rgba(0,0,0,0.2)'
        };
        return shadows[shadowType] || shadows.none;
    }

    /**
     * Генерация CSS для компонентов
     */
    generateCSS() {
        let css = '';
        
        Object.entries(this.components).forEach(([type, component]) => {
            css += `
/* ${component.name} */
.${type}-component {
    /* Базовые стили для ${component.name} */
}

.${type}-component:hover {
    /* Стили при наведении */
}
`;
        });
        
        return css;
    }

    /**
     * Получение статистики компонентов
     */
    getStats() {
        const stats = {
            total: Object.keys(this.components).length,
            byCategory: {},
            categories: this.getCategories()
        };
        
        Object.values(this.components).forEach(component => {
            const category = component.category || 'other';
            stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
        });
        
        return stats;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.editorComponents = new EditorComponents();
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EditorComponents;
} 