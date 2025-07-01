/**
 * Dental Academy Custom GrapesJS Components
 * Кастомные компоненты GrapesJS для Dental Academy
 * 
 * This file contains custom components that match the existing Dental Academy design system
 * Этот файл содержит кастомные компоненты, соответствующие существующей системе дизайна Dental Academy
 */

(function() {
    'use strict';

    // Component definitions with bilingual support
    // Определения компонентов с двуязычной поддержкой
    const componentDefinitions = {
        // 1. Dental Learning Card Component
        // Компонент карточки обучения
        'dental-learning-card': {
            model: {
                defaults: {
                    tagName: 'div',
                    draggable: true,
                    droppable: false,
                    attributes: { class: 'subject-card dental-component' },
                    traits: [
                        {
                            type: 'text',
                            name: 'title',
                            label: {
                                en: 'Title',
                                ru: 'Заголовок'
                            },
                            default: 'Module Title'
                        },
                        {
                            type: 'textarea',
                            name: 'description',
                            label: {
                                en: 'Description',
                                ru: 'Описание'
                            },
                            default: 'Module description goes here...'
                        },
                        {
                            type: 'number',
                            name: 'progress',
                            label: {
                                en: 'Progress %',
                                ru: 'Прогресс %'
                            },
                            default: 75,
                            min: 0,
                            max: 100
                        },
                        {
                            type: 'text',
                            name: 'link',
                            label: {
                                en: 'Link URL',
                                ru: 'Ссылка'
                            },
                            default: '#'
                        },
                        {
                            type: 'select',
                            name: 'icon',
                            label: {
                                en: 'Icon Type',
                                ru: 'Тип иконки'
                            },
                            options: [
                                { value: 'book', text: { en: 'Book', ru: 'Книга' } },
                                { value: 'file-earmark-text', text: { en: 'Document', ru: 'Документ' } },
                                { value: 'folder2-open', text: { en: 'Folder', ru: 'Папка' } },
                                { value: 'list-task', text: { en: 'List', ru: 'Список' } },
                                { value: 'mortarboard', text: { en: 'Graduation', ru: 'Диплом' } },
                                { value: 'heart-pulse', text: { en: 'Medical', ru: 'Медицина' } }
                            ],
                            default: 'book'
                        },
                        {
                            type: 'select',
                            name: 'theme',
                            label: {
                                en: 'Theme',
                                ru: 'Тема'
                            },
                            options: [
                                { value: 'light', text: { en: 'Light', ru: 'Светлая' } },
                                { value: 'dark', text: { en: 'Dark', ru: 'Темная' } },
                                { value: 'gradient', text: { en: 'Gradient', ru: 'Градиент' } }
                            ],
                            default: 'light'
                        }
                    ],
                    components: `
                        <div class="subject-card-inner">
                            <div class="subject-card-header">
                                <div class="subject-card-icon">
                                    <i class="bi bi-{icon}"></i>
                                </div>
                                <div class="subject-card-progress">
                                    <div class="progress-circle" data-progress="{progress}">
                                        <svg viewBox="0 0 36 36">
                                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                        </svg>
                                        <div class="progress-text">{progress}%</div>
                                    </div>
                                </div>
                            </div>
                            <div class="subject-card-content">
                                <h3 class="subject-card-title">{title}</h3>
                                <p class="subject-card-description">{description}</p>
                            </div>
                            <div class="subject-card-footer">
                                <a href="{link}" class="btn btn-primary btn-sm">
                                    <span class="btn-text">Start Learning</span>
                                    <i class="bi bi-arrow-right"></i>
                                </a>
                            </div>
                        </div>
                    `,
                    styles: `
                        .subject-card {
                            background: var(--subject-view-bg, #ffffff);
                            border: 1px solid var(--border-color, #e2e8f0);
                            border-radius: var(--radius-lg, 12px);
                            padding: 1.5rem;
                            transition: all var(--transition-normal, 0.3s ease);
                            box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.1));
                            position: relative;
                            overflow: hidden;
                        }
                        
                        .subject-card:hover {
                            transform: translateY(-2px);
                            box-shadow: var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.15));
                        }
                        
                        .subject-card-inner {
                            display: flex;
                            flex-direction: column;
                            height: 100%;
                        }
                        
                        .subject-card-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: flex-start;
                            margin-bottom: 1rem;
                        }
                        
                        .subject-card-icon {
                            font-size: 2rem;
                            color: var(--primary-color, #3ECDC1);
                        }
                        
                        .subject-card-progress {
                            position: relative;
                        }
                        
                        .progress-circle {
                            position: relative;
                            width: 40px;
                            height: 40px;
                        }
                        
                        .progress-circle svg {
                            width: 100%;
                            height: 100%;
                            transform: rotate(-90deg);
                        }
                        
                        .progress-circle path:first-child {
                            fill: none;
                            stroke: var(--border-color, #e2e8f0);
                            stroke-width: 3;
                        }
                        
                        .progress-circle path:last-child {
                            fill: none;
                            stroke: var(--primary-color, #3ECDC1);
                            stroke-width: 3;
                            stroke-dasharray: 100;
                            stroke-dashoffset: calc(100 - var(--progress, 75));
                            transition: stroke-dashoffset 0.5s ease;
                        }
                        
                        .progress-text {
                            position: absolute;
                            top: 50%;
                            left: 50%;
                            transform: translate(-50%, -50%);
                            font-size: 0.75rem;
                            font-weight: 600;
                            color: var(--text-primary, #1e293b);
                        }
                        
                        .subject-card-content {
                            flex: 1;
                            margin-bottom: 1rem;
                        }
                        
                        .subject-card-title {
                            font-size: 1.25rem;
                            font-weight: 600;
                            color: var(--text-primary, #1e293b);
                            margin-bottom: 0.5rem;
                            line-height: 1.3;
                        }
                        
                        .subject-card-description {
                            color: var(--text-secondary, #64748b);
                            font-size: 0.875rem;
                            line-height: 1.5;
                            margin: 0;
                        }
                        
                        .subject-card-footer {
                            margin-top: auto;
                        }
                        
                        .btn {
                            display: inline-flex;
                            align-items: center;
                            gap: 0.5rem;
                            padding: 0.5rem 1rem;
                            border-radius: var(--radius-md, 8px);
                            text-decoration: none;
                            font-weight: 500;
                            transition: all var(--transition-normal, 0.3s ease);
                        }
                        
                        .btn-primary {
                            background: var(--primary-color, #3ECDC1);
                            color: white;
                            border: none;
                        }
                        
                        .btn-primary:hover {
                            background: var(--primary-hover, #2bb8ad);
                            transform: translateY(-1px);
                        }
                        
                        .btn-sm {
                            font-size: 0.875rem;
                            padding: 0.375rem 0.75rem;
                        }
                    `
                },
                
                init() {
                    this.on('change:traits', this.handleTraitsChange);
                },
                
                handleTraitsChange() {
                    const traits = this.get('traits');
                    const progress = traits.progress;
                    const icon = traits.icon;
                    const title = traits.title;
                    const description = traits.description;
                    const link = traits.link;
                    
                    // Update component content
                    let content = this.get('components');
                    content = content.replace(/{progress}/g, progress);
                    content = content.replace(/{icon}/g, icon);
                    content = content.replace(/{title}/g, title);
                    content = content.replace(/{description}/g, description);
                    content = content.replace(/{link}/g, link);
                    
                    this.set('components', content);
                    
                    // Update CSS custom property for progress
                    const style = this.get('styles');
                    const updatedStyle = style.replace(
                        /--progress:\s*\d+/,
                        `--progress: ${progress}`
                    );
                    this.set('styles', updatedStyle);
                }
            },
            
            view: {
                onRender() {
                    // Add component label
                    const label = document.createElement('div');
                    label.className = 'component-label';
                    label.textContent = 'Dental Learning Card';
                    label.style.cssText = `
                        position: absolute;
                        top: -20px;
                        left: 0;
                        background: #3ECDC1;
                        color: white;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        z-index: 10;
                    `;
                    this.el.appendChild(label);
                }
            }
        },

        // 2. Dental Navigation Component
        // Компонент навигации
        'dental-navigation': {
            model: {
                defaults: {
                    tagName: 'nav',
                    draggable: true,
                    droppable: true,
                    attributes: { class: 'dental-navigation dental-component' },
                    traits: [
                        {
                            type: 'text',
                            name: 'title',
                            label: {
                                en: 'Navigation Title',
                                ru: 'Заголовок навигации'
                            },
                            default: 'Learning Paths'
                        },
                        {
                            type: 'number',
                            name: 'items_count',
                            label: {
                                en: 'Number of Items',
                                ru: 'Количество элементов'
                            },
                            default: 3,
                            min: 1,
                            max: 10
                        },
                        {
                            type: 'select',
                            name: 'animation',
                            label: {
                                en: 'Animation Type',
                                ru: 'Тип анимации'
                            },
                            options: [
                                { value: 'slide', text: { en: 'Slide', ru: 'Слайд' } },
                                { value: 'fade', text: { en: 'Fade', ru: 'Плавное' } },
                                { value: 'scale', text: { en: 'Scale', ru: 'Масштаб' } }
                            ],
                            default: 'slide'
                        },
                        {
                            type: 'color',
                            name: 'primary_color',
                            label: {
                                en: 'Primary Color',
                                ru: 'Основной цвет'
                            },
                            default: '#3ECDC1'
                        },
                        {
                            type: 'color',
                            name: 'secondary_color',
                            label: {
                                en: 'Secondary Color',
                                ru: 'Дополнительный цвет'
                            },
                            default: '#2bb8ad'
                        }
                    ],
                    components: `
                        <div class="navigation-header">
                            <h3 class="navigation-title">{title}</h3>
                        </div>
                        <div class="navigation-items">
                            <div class="learning-path-button" data-animation="{animation}">
                                <div class="path-icon">
                                    <i class="bi bi-list-task"></i>
                                </div>
                                <div class="path-content">
                                    <h4 class="path-title">Basic Medical Knowledge</h4>
                                    <p class="path-description">Fundamental medical concepts and terminology</p>
                                </div>
                                <div class="path-arrow">
                                    <i class="bi bi-chevron-right"></i>
                                </div>
                            </div>
                            <div class="learning-path-button" data-animation="{animation}">
                                <div class="path-icon">
                                    <i class="bi bi-heart-pulse"></i>
                                </div>
                                <div class="path-content">
                                    <h4 class="path-title">Clinical Skills</h4>
                                    <p class="path-description">Practical clinical procedures and techniques</p>
                                </div>
                                <div class="path-arrow">
                                    <i class="bi bi-chevron-right"></i>
                                </div>
                            </div>
                            <div class="learning-path-button" data-animation="{animation}">
                                <div class="path-icon">
                                    <i class="bi bi-mortarboard"></i>
                                </div>
                                <div class="path-content">
                                    <h4 class="path-title">Advanced Topics</h4>
                                    <p class="path-description">Specialized knowledge and advanced concepts</p>
                                </div>
                                <div class="path-arrow">
                                    <i class="bi bi-chevron-right"></i>
                                </div>
                            </div>
                        </div>
                    `,
                    styles: `
                        .dental-navigation {
                            background: var(--bg-primary, #ffffff);
                            border-radius: var(--radius-lg, 12px);
                            padding: 1.5rem;
                            box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.1));
                        }
                        
                        .navigation-header {
                            margin-bottom: 1.5rem;
                        }
                        
                        .navigation-title {
                            font-size: 1.5rem;
                            font-weight: 600;
                            color: var(--text-primary, #1e293b);
                            margin: 0;
                        }
                        
                        .navigation-items {
                            display: flex;
                            flex-direction: column;
                            gap: 1rem;
                        }
                        
                        .learning-path-button {
                            display: flex;
                            align-items: center;
                            gap: 1rem;
                            padding: 1rem;
                            background: var(--bg-secondary, #f8fafc);
                            border: 1px solid var(--border-color, #e2e8f0);
                            border-radius: var(--radius-md, 8px);
                            cursor: pointer;
                            transition: all var(--transition-normal, 0.3s ease);
                            text-decoration: none;
                            color: inherit;
                        }
                        
                        .learning-path-button:hover {
                            background: var(--primary-color, #3ECDC1);
                            color: white;
                            transform: translateX(5px);
                            box-shadow: var(--shadow-md, 0 4px 6px rgba(0,0,0,0.1));
                        }
                        
                        .path-icon {
                            font-size: 1.5rem;
                            color: var(--primary-color, #3ECDC1);
                            transition: color var(--transition-normal, 0.3s ease);
                        }
                        
                        .learning-path-button:hover .path-icon {
                            color: white;
                        }
                        
                        .path-content {
                            flex: 1;
                        }
                        
                        .path-title {
                            font-size: 1.125rem;
                            font-weight: 600;
                            margin: 0 0 0.25rem 0;
                            color: inherit;
                        }
                        
                        .path-description {
                            font-size: 0.875rem;
                            margin: 0;
                            opacity: 0.8;
                            color: inherit;
                        }
                        
                        .path-arrow {
                            font-size: 1.25rem;
                            opacity: 0.6;
                            transition: all var(--transition-normal, 0.3s ease);
                        }
                        
                        .learning-path-button:hover .path-arrow {
                            opacity: 1;
                            transform: translateX(3px);
                        }
                        
                        /* Animation classes */
                        .learning-path-button[data-animation="slide"]:hover {
                            transform: translateX(10px);
                        }
                        
                        .learning-path-button[data-animation="fade"]:hover {
                            opacity: 0.9;
                        }
                        
                        .learning-path-button[data-animation="scale"]:hover {
                            transform: scale(1.02);
                        }
                    `
                },
                
                init() {
                    this.on('change:traits', this.handleTraitsChange);
                },
                
                handleTraitsChange() {
                    const traits = this.get('traits');
                    const title = traits.title;
                    const animation = traits.animation;
                    const primaryColor = traits.primary_color;
                    const secondaryColor = traits.secondary_color;
                    
                    // Update component content
                    let content = this.get('components');
                    content = content.replace(/{title}/g, title);
                    content = content.replace(/{animation}/g, animation);
                    
                    this.set('components', content);
                    
                    // Update CSS custom properties
                    let style = this.get('styles');
                    style = style.replace(/--primary-color:\s*#[0-9a-fA-F]{6}/, `--primary-color: ${primaryColor}`);
                    style = style.replace(/--secondary-color:\s*#[0-9a-fA-F]{6}/, `--secondary-color: ${secondaryColor}`);
                    
                    this.set('styles', style);
                }
            },
            
            view: {
                onRender() {
                    const label = document.createElement('div');
                    label.className = 'component-label';
                    label.textContent = 'Dental Navigation';
                    label.style.cssText = `
                        position: absolute;
                        top: -20px;
                        left: 0;
                        background: #3ECDC1;
                        color: white;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        z-index: 10;
                    `;
                    this.el.appendChild(label);
                }
            }
        },

        // 3. Dental Progress Bar Component
        // Компонент индикатора прогресса
        'dental-progress-bar': {
            model: {
                defaults: {
                    tagName: 'div',
                    draggable: true,
                    droppable: false,
                    attributes: { class: 'dental-progress-container dental-component' },
                    traits: [
                        {
                            type: 'text',
                            name: 'label',
                            label: {
                                en: 'Progress Label',
                                ru: 'Подпись прогресса'
                            },
                            default: 'Course Progress'
                        },
                        {
                            type: 'number',
                            name: 'percentage',
                            label: {
                                en: 'Progress Percentage',
                                ru: 'Процент прогресса'
                            },
                            default: 65,
                            min: 0,
                            max: 100
                        },
                        {
                            type: 'select',
                            name: 'color_scheme',
                            label: {
                                en: 'Color Scheme',
                                ru: 'Цветовая схема'
                            },
                            options: [
                                { value: 'primary', text: { en: 'Primary', ru: 'Основная' } },
                                { value: 'success', text: { en: 'Success', ru: 'Успех' } },
                                { value: 'warning', text: { en: 'Warning', ru: 'Предупреждение' } },
                                { value: 'danger', text: { en: 'Danger', ru: 'Ошибка' } },
                                { value: 'info', text: { en: 'Info', ru: 'Информация' } }
                            ],
                            default: 'primary'
                        },
                        {
                            type: 'select',
                            name: 'animation',
                            label: {
                                en: 'Animation',
                                ru: 'Анимация'
                            },
                            options: [
                                { value: 'smooth', text: { en: 'Smooth', ru: 'Плавная' } },
                                { value: 'bounce', text: { en: 'Bounce', ru: 'Отскок' } },
                                { value: 'pulse', text: { en: 'Pulse', ru: 'Пульс' } }
                            ],
                            default: 'smooth'
                        },
                        {
                            type: 'checkbox',
                            name: 'show_percentage',
                            label: {
                                en: 'Show Percentage',
                                ru: 'Показывать процент'
                            },
                            default: true
                        }
                    ],
                    components: `
                        <div class="progress-wrapper">
                            <div class="progress-header">
                                <span class="progress-label">{label}</span>
                                {show_percentage ? '<span class="progress-percentage">{percentage}%</span>' : ''}
                            </div>
                            <div class="progress-bar" data-color="{color_scheme}" data-animation="{animation}">
                                <div class="progress-bar-fill" style="width: {percentage}%"></div>
                            </div>
                        </div>
                    `,
                    styles: `
                        .dental-progress-container {
                            background: var(--bg-primary, #ffffff);
                            border: 1px solid var(--border-color, #e2e8f0);
                            border-radius: var(--radius-lg, 12px);
                            padding: 1.5rem;
                            box-shadow: var(--shadow-sm, 0 1px 3px rgba(0,0,0,0.1));
                        }
                        
                        .progress-wrapper {
                            width: 100%;
                        }
                        
                        .progress-header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin-bottom: 0.75rem;
                        }
                        
                        .progress-label {
                            font-weight: 600;
                            color: var(--text-primary, #1e293b);
                            font-size: 1rem;
                        }
                        
                        .progress-percentage {
                            font-weight: 600;
                            color: var(--text-secondary, #64748b);
                            font-size: 0.875rem;
                        }
                        
                        .progress-bar {
                            width: 100%;
                            height: 12px;
                            background: var(--bg-secondary, #f1f5f9);
                            border-radius: var(--radius-full, 9999px);
                            overflow: hidden;
                            position: relative;
                        }
                        
                        .progress-bar-fill {
                            height: 100%;
                            border-radius: var(--radius-full, 9999px);
                            transition: width var(--transition-normal, 0.3s ease);
                            position: relative;
                        }
                        
                        /* Color schemes */
                        .progress-bar[data-color="primary"] .progress-bar-fill {
                            background: linear-gradient(90deg, var(--primary-color, #3ECDC1), var(--primary-hover, #2bb8ad));
                        }
                        
                        .progress-bar[data-color="success"] .progress-bar-fill {
                            background: linear-gradient(90deg, var(--success-color, #10b981), #059669);
                        }
                        
                        .progress-bar[data-color="warning"] .progress-bar-fill {
                            background: linear-gradient(90deg, var(--warning-color, #f59e0b), #d97706);
                        }
                        
                        .progress-bar[data-color="danger"] .progress-bar-fill {
                            background: linear-gradient(90deg, var(--danger-color, #ef4444), #dc2626);
                        }
                        
                        .progress-bar[data-color="info"] .progress-bar-fill {
                            background: linear-gradient(90deg, var(--info-color, #3b82f6), #2563eb);
                        }
                        
                        /* Animation effects */
                        .progress-bar[data-animation="smooth"] .progress-bar-fill {
                            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                        }
                        
                        .progress-bar[data-animation="bounce"] .progress-bar-fill {
                            transition: width 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                        }
                        
                        .progress-bar[data-animation="pulse"] .progress-bar-fill {
                            animation: pulse 2s infinite;
                        }
                        
                        @keyframes pulse {
                            0%, 100% { opacity: 1; }
                            50% { opacity: 0.8; }
                        }
                        
                        /* Glow effect */
                        .progress-bar-fill::after {
                            content: '';
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            background: inherit;
                            filter: blur(4px);
                            opacity: 0.3;
                            z-index: -1;
                        }
                    `
                },
                
                init() {
                    this.on('change:traits', this.handleTraitsChange);
                },
                
                handleTraitsChange() {
                    const traits = this.get('traits');
                    const label = traits.label;
                    const percentage = traits.percentage;
                    const colorScheme = traits.color_scheme;
                    const animation = traits.animation;
                    const showPercentage = traits.show_percentage;
                    
                    // Update component content
                    let content = this.get('components');
                    content = content.replace(/{label}/g, label);
                    content = content.replace(/{percentage}/g, percentage);
                    content = content.replace(/{color_scheme}/g, colorScheme);
                    content = content.replace(/{animation}/g, animation);
                    
                    if (showPercentage) {
                        content = content.replace(/{show_percentage \? '<span class="progress-percentage">{percentage}%</span>' : ''}/g, 
                            `<span class="progress-percentage">${percentage}%</span>`);
                    } else {
                        content = content.replace(/{show_percentage \? '<span class="progress-percentage">{percentage}%</span>' : ''}/g, '');
                    }
                    
                    this.set('components', content);
                }
            },
            
            view: {
                onRender() {
                    const label = document.createElement('div');
                    label.className = 'component-label';
                    label.textContent = 'Dental Progress Bar';
                    label.style.cssText = `
                        position: absolute;
                        top: -20px;
                        left: 0;
                        background: #3ECDC1;
                        color: white;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        z-index: 10;
                    `;
                    this.el.appendChild(label);
                }
            }
        },

        // 4. Dental Theme Background Component
        // Компонент тематического фона
        'dental-theme-background': {
            model: {
                defaults: {
                    tagName: 'div',
                    draggable: true,
                    droppable: true,
                    attributes: { class: 'dental-theme-background dental-component' },
                    traits: [
                        {
                            type: 'select',
                            name: 'theme_type',
                            label: {
                                en: 'Theme Type',
                                ru: 'Тип темы'
                            },
                            options: [
                                { value: 'gradient', text: { en: 'Gradient', ru: 'Градиент' } },
                                { value: 'glass', text: { en: 'Glass', ru: 'Стекло' } },
                                { value: 'modern', text: { en: 'Modern', ru: 'Современная' } },
                                { value: 'minimal', text: { en: 'Minimal', ru: 'Минималистичная' } }
                            ],
                            default: 'gradient'
                        },
                        {
                            type: 'color',
                            name: 'primary_color',
                            label: {
                                en: 'Primary Color',
                                ru: 'Основной цвет'
                            },
                            default: '#3ECDC1'
                        },
                        {
                            type: 'color',
                            name: 'secondary_color',
                            label: {
                                en: 'Secondary Color',
                                ru: 'Дополнительный цвет'
                            },
                            default: '#2bb8ad'
                        },
                        {
                            type: 'number',
                            name: 'border_radius',
                            label: {
                                en: 'Border Radius',
                                ru: 'Радиус границ'
                            },
                            default: 16,
                            min: 0,
                            max: 50
                        },
                        {
                            type: 'checkbox',
                            name: 'show_shadow',
                            label: {
                                en: 'Show Shadow',
                                ru: 'Показывать тень'
                            },
                            default: true
                        }
                    ],
                    components: `
                        <div class="theme-content">
                            <div class="theme-placeholder">
                                <i class="bi bi-palette"></i>
                                <p>Theme Background Container</p>
                                <small>Drop content here</small>
                            </div>
                        </div>
                    `,
                    styles: `
                        .dental-theme-background {
                            min-height: 200px;
                            padding: 2rem;
                            position: relative;
                            overflow: hidden;
                        }
                        
                        .theme-content {
                            height: 100%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        
                        .theme-placeholder {
                            text-align: center;
                            color: var(--text-primary, #1e293b);
                        }
                        
                        .theme-placeholder i {
                            font-size: 2rem;
                            margin-bottom: 0.5rem;
                            opacity: 0.6;
                        }
                        
                        .theme-placeholder p {
                            margin: 0.5rem 0;
                            font-weight: 500;
                        }
                        
                        .theme-placeholder small {
                            opacity: 0.6;
                            font-size: 0.875rem;
                        }
                        
                        /* Theme variations */
                        .dental-theme-background[data-theme="gradient"] {
                            background: linear-gradient(135deg, var(--primary-color, #3ECDC1), var(--secondary-color, #2bb8ad));
                            color: white;
                        }
                        
                        .dental-theme-background[data-theme="gradient"] .theme-placeholder {
                            color: white;
                        }
                        
                        .dental-theme-background[data-theme="glass"] {
                            background: rgba(255, 255, 255, 0.1);
                            backdrop-filter: blur(20px);
                            border: 1px solid rgba(255, 255, 255, 0.2);
                        }
                        
                        .dental-theme-background[data-theme="modern"] {
                            background: var(--bg-primary, #ffffff);
                            border: 2px solid var(--primary-color, #3ECDC1);
                        }
                        
                        .dental-theme-background[data-theme="minimal"] {
                            background: var(--bg-secondary, #f8fafc);
                            border: 1px solid var(--border-color, #e2e8f0);
                        }
                        
                        /* Border radius variations */
                        .dental-theme-background[data-radius="0"] { border-radius: 0; }
                        .dental-theme-background[data-radius="4"] { border-radius: 4px; }
                        .dental-theme-background[data-radius="8"] { border-radius: 8px; }
                        .dental-theme-background[data-radius="12"] { border-radius: 12px; }
                        .dental-theme-background[data-radius="16"] { border-radius: 16px; }
                        .dental-theme-background[data-radius="20"] { border-radius: 20px; }
                        .dental-theme-background[data-radius="24"] { border-radius: 24px; }
                        .dental-theme-background[data-radius="32"] { border-radius: 32px; }
                        
                        /* Shadow variations */
                        .dental-theme-background[data-shadow="true"] {
                            box-shadow: var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.15));
                        }
                        
                        .dental-theme-background[data-shadow="false"] {
                            box-shadow: none;
                        }
                        
                        /* Responsive design */
                        @media (max-width: 768px) {
                            .dental-theme-background {
                                padding: 1rem;
                                min-height: 150px;
                            }
                        }
                    `
                },
                
                init() {
                    this.on('change:traits', this.handleTraitsChange);
                },
                
                handleTraitsChange() {
                    const traits = this.get('traits');
                    const themeType = traits.theme_type;
                    const primaryColor = traits.primary_color;
                    const secondaryColor = traits.secondary_color;
                    const borderRadius = traits.border_radius;
                    const showShadow = traits.show_shadow;
                    
                    // Update attributes
                    this.setAttributes({
                        'data-theme': themeType,
                        'data-radius': borderRadius,
                        'data-shadow': showShadow
                    });
                    
                    // Update CSS custom properties
                    let style = this.get('styles');
                    style = style.replace(/--primary-color:\s*#[0-9a-fA-F]{6}/, `--primary-color: ${primaryColor}`);
                    style = style.replace(/--secondary-color:\s*#[0-9a-fA-F]{6}/, `--secondary-color: ${secondaryColor}`);
                    
                    this.set('styles', style);
                }
            },
            
            view: {
                onRender() {
                    const label = document.createElement('div');
                    label.className = 'component-label';
                    label.textContent = 'Dental Theme Background';
                    label.style.cssText = `
                        position: absolute;
                        top: -20px;
                        left: 0;
                        background: #3ECDC1;
                        color: white;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        z-index: 10;
                    `;
                    this.el.appendChild(label);
                }
            }
        }
    };

    // Helper function to get current language
    // Функция для получения текущего языка
    function getCurrentLanguage() {
        // Try to get language from various sources
        // Пытаемся получить язык из различных источников
        return document.documentElement.lang || 
               document.querySelector('meta[name="language"]')?.content ||
               'en';
    }

    // Helper function to get localized text
    // Функция для получения локализованного текста
    function getLocalizedText(textObj, fallback = '') {
        const lang = getCurrentLanguage();
        return textObj[lang] || textObj.en || fallback;
    }

    // Initialize components when GrapesJS is ready
    // Инициализация компонентов когда GrapesJS готов
    if (typeof grapesjs !== 'undefined') {
        // Wait for GrapesJS to be ready
        // Ждем готовности GrapesJS
        if (grapesjs.editors) {
            // GrapesJS is already loaded
            // GrapesJS уже загружен
            initializeComponents();
        } else {
            // Wait for GrapesJS to load
            // Ждем загрузки GrapesJS
            document.addEventListener('grapesjs:ready', initializeComponents);
        }
    }

    function initializeComponents() {
        // Get the editor instance
        // Получаем экземпляр редактора
        const editor = grapesjs.editors[0] || window.editor;
        
        if (!editor) {
            console.warn('Dental Academy Components: GrapesJS editor not found');
            return;
        }

        // Register each component
        // Регистрируем каждый компонент
        Object.keys(componentDefinitions).forEach(componentName => {
            const definition = componentDefinitions[componentName];
            
            // Register the component
            // Регистрируем компонент
            editor.Components.addType(componentName, definition);
            
            // Add to component categories
            // Добавляем в категории компонентов
            const componentManager = editor.Components;
            const component = componentManager.getType(componentName);
            
            if (component) {
                component.model.prototype.defaults.category = 'Dental Academy';
                component.model.prototype.defaults.label = getLocalizedText({
                    en: componentName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    ru: componentName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                });
            }
        });

        // Add component category to the panel
        // Добавляем категорию компонентов в панель
        const blockManager = editor.BlockManager;
        
        // Add blocks for each component
        // Добавляем блоки для каждого компонента
        Object.keys(componentDefinitions).forEach(componentName => {
            const definition = componentDefinitions[componentName];
            const label = getLocalizedText({
                en: componentName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                ru: componentName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            });
            
            blockManager.add(componentName, {
                label: label,
                category: 'Dental Academy',
                content: { type: componentName },
                media: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>`
            });
        });

        console.log('✅ Dental Academy Components loaded successfully');
    }

    // Export for use in other scripts
    // Экспорт для использования в других скриптах
    window.DentalAcademyComponents = {
        definitions: componentDefinitions,
        initialize: initializeComponents,
        getLocalizedText: getLocalizedText
    };

})(); 