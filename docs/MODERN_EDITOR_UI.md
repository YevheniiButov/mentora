# Modern Editor UI System
# Современная система UI для редактора

## Обзор / Overview

Современная система UI для редактора GrapesJS с профессиональным дизайном, двуязычной поддержкой и расширенными возможностями.

Modern UI system for GrapesJS editor with professional design, bilingual support, and advanced features.

## Возможности / Features

### 🎨 Дизайн и UX / Design & UX
- **Glassmorphism эффекты** для панелей и компонентов
- **Темная/светлая тема** с автоматическим переключением
- **Плавные анимации** и микро-взаимодействия
- **Адаптивный дизайн** для всех устройств
- **Профессиональная цветовая схема**

### 🌐 Двуязычная поддержка / Bilingual Support
- **Английский и русский** языки интерфейса
- **Переключение языка** без перезагрузки
- **Подготовка к RTL** языкам
- **Консистентные ключи переводов**

### ♿ Доступность / Accessibility
- **WCAG 2.1 AA** соответствие
- **Поддержка клавиатурной навигации**
- **Совместимость с экранными дикторами**
- **Режим высокой контрастности**
- **Управление фокусом**

### ⚡ Производительность / Performance
- **Lazy loading** панелей редактора
- **Эффективная обработка событий**
- **Предотвращение утечек памяти**
- **Плавные анимации (60fps)**

## Структура файлов / File Structure

```
static/
├── css/
│   └── modern-editor-ui.css    # Основные стили UI
└── js/
    └── modern-editor-ui.js     # JavaScript логика
```

## CSS Система / CSS System

### CSS Переменные / CSS Variables

```css
:root {
  /* Цвета / Colors */
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  
  /* Фоны / Backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  
  /* Текст / Text */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.8);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  --glass-blur: blur(20px);
}
```

### Темная тема / Dark Theme

```css
[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --glass-bg: rgba(30, 41, 59, 0.8);
}
```

### Компоненты / Components

#### Кнопки / Buttons

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: 8px;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: var(--primary-color);
  color: var(--text-inverse);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

#### Панели / Panels

```css
.editor-panel {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  box-shadow: var(--glass-shadow);
  transition: all var(--transition-normal);
}

.editor-panel:hover {
  box-shadow: var(--shadow-xl);
  transform: translateY(-2px);
}
```

#### Модальные окна / Modals

```css
.modal-overlay {
  background: var(--bg-overlay);
  backdrop-filter: blur(4px);
  animation: modalFadeIn 0.3s ease;
}

.modal {
  background: var(--bg-elevated);
  border-radius: 12px;
  box-shadow: var(--shadow-xl);
  animation: modalSlideIn 0.3s ease;
}
```

## JavaScript API / JavaScript API

### Инициализация / Initialization

```javascript
// Создание экземпляра
const editorUI = new ModernEditorUI({
    defaultLanguage: 'en',
    defaultTheme: 'light',
    enableAnimations: true,
    enableKeyboardShortcuts: true,
    enableAutoSave: true,
    autoSaveInterval: 30000
});

// Инициализация
editorUI.init();
```

### Управление темами / Theme Management

```javascript
// Переключение темы
editorUI.toggleTheme();

// Применение конкретной темы
editorUI.applyTheme('dark');

// Получение текущей темы
console.log(editorUI.currentTheme);
```

### Управление языками / Language Management

```javascript
// Переключение языка
editorUI.toggleLanguage();

// Применение конкретного языка
editorUI.applyLanguage('ru');

// Перевод текста
const translated = editorUI.t('editor.save');
```

### Уведомления / Notifications

```javascript
// Показать уведомление
editorUI.showNotification('success', 'Success', 'Operation completed');

// Типы уведомлений
editorUI.showNotification('info', 'Info', 'Information message');
editorUI.showNotification('warning', 'Warning', 'Warning message');
editorUI.showNotification('error', 'Error', 'Error message');
```

### Модальные окна / Modals

```javascript
// Создание модального окна
editorUI.createModal('settings', 'Settings', `
    <div class="form-group">
        <label>Theme</label>
        <select>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
        </select>
    </div>
`, [
    {
        label: 'Save',
        class: 'btn-primary',
        action: 'save',
        handler: () => console.log('Saved')
    },
    {
        label: 'Cancel',
        class: 'btn-secondary',
        action: 'cancel'
    }
]);
```

### Контекстные меню / Context Menus

```javascript
// Регистрация контекстного меню
editorUI.registerContextMenu('canvas', [
    { label: 'Undo', action: () => editorUI.undo(), icon: '↶' },
    { label: 'Redo', action: () => editorUI.redo(), icon: '↷' },
    { type: 'separator' },
    { label: 'Save', action: () => editorUI.save(), icon: '💾' }
]);
```

## Горячие клавиши / Keyboard Shortcuts

| Комбинация / Shortcut | Действие / Action |
|----------------------|-------------------|
| `Ctrl+S` | Сохранить / Save |
| `Ctrl+Z` | Отменить / Undo |
| `Ctrl+Y` | Повторить / Redo |
| `Ctrl+P` | Предпросмотр / Preview |
| `Ctrl+D` | Развернуть / Deploy |
| `F1` | Помощь / Help |
| `Escape` | Закрыть модальные окна / Close modals |
| `Ctrl+,` | Настройки / Settings |

## Интеграция с GrapesJS / GrapesJS Integration

### Подключение стилей / Including Styles

```html
<!-- В head документа -->
<link rel="stylesheet" href="/static/css/modern-editor-ui.css">
```

### Подключение скриптов / Including Scripts

```html
<!-- Перед закрывающим тегом body -->
<script src="/static/js/modern-editor-ui.js"></script>
```

### Инициализация с GrapesJS / Initialization with GrapesJS

```javascript
// После инициализации GrapesJS
const editor = grapesjs.init({
    container: '#gjs',
    // ... другие настройки
});

// Инициализация UI системы
const editorUI = new ModernEditorUI({
    defaultLanguage: 'en',
    defaultTheme: 'light'
});

// Интеграция с GrapesJS
editor.on('component:selected', () => {
    // Обновление UI при выборе компонента
});

editor.on('component:update', () => {
    // Обновление UI при изменении компонента
});
```

## Адаптивность / Responsiveness

### Breakpoints / Точки перелома

```css
/* Desktop */
@media (min-width: 1200px) {
    .editor-layout {
        grid-template-columns: 280px 1fr 320px;
    }
}

/* Tablet */
@media (max-width: 992px) {
    .editor-layout {
        grid-template-columns: 240px 1fr;
    }
    .editor-sidebar-right {
        display: none;
    }
}

/* Mobile */
@media (max-width: 768px) {
    .editor-layout {
        grid-template-columns: 1fr;
    }
    .editor-sidebar-left,
    .editor-sidebar-right {
        display: none;
    }
}
```

## Доступность / Accessibility

### ARIA атрибуты / ARIA Attributes

```html
<button 
    class="btn btn-primary" 
    aria-label="Save changes"
    aria-describedby="save-tooltip">
    Save
</button>
```

### Фокус / Focus Management

```css
/* Индикаторы фокуса */
.btn:focus,
.form-input:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* Только для экранного диктора */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

### Уменьшенное движение / Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

## Производительность / Performance

### Lazy Loading / Ленивая загрузка

```javascript
// Ленивая загрузка панелей
const loadPanel = async (panelName) => {
    const panel = await import(`./panels/${panelName}.js`);
    return panel.default;
};
```

### Debouncing / Дебаунсинг

```javascript
// Дебаунсинг для resize событий
window.addEventListener('resize', editorUI.debounce(() => {
    editorUI.handleResize();
}, 250));
```

### Memory Management / Управление памятью

```javascript
// Очистка при уничтожении
editorUI.destroy();

// Удаление обработчиков событий
document.removeEventListener('keydown', handler);
```

## Кастомизация / Customization

### Создание новых компонентов / Creating New Components

```css
/* Новый компонент */
.custom-component {
    background: var(--glass-bg);
    border-radius: 8px;
    padding: var(--spacing-md);
    transition: all var(--transition-fast);
}

.custom-component:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}
```

### Расширение переводов / Extending Translations

```javascript
// Добавление новых переводов
editorUI.translations.en['custom.key'] = 'Custom text';
editorUI.translations.ru['custom.key'] = 'Пользовательский текст';
```

### Создание новых тем / Creating New Themes

```css
[data-theme="custom"] {
    --primary-color: #your-color;
    --bg-primary: #your-bg;
    --text-primary: #your-text;
}
```

## Тестирование / Testing

### Unit Tests / Модульные тесты

```javascript
// Тест переключения темы
test('should toggle theme', () => {
    const ui = new ModernEditorUI();
    ui.toggleTheme();
    expect(ui.currentTheme).toBe('dark');
});

// Тест переводов
test('should translate text', () => {
    const ui = new ModernEditorUI();
    ui.applyLanguage('ru');
    expect(ui.t('editor.save')).toBe('Сохранить');
});
```

### E2E Tests / End-to-End тесты

```javascript
// Тест полного цикла
test('should complete save workflow', async () => {
    await page.click('[data-action="save"]');
    await expect(page.locator('.notification.success')).toBeVisible();
});
```

## Развертывание / Deployment

### Production Build / Продакшн сборка

```bash
# Минификация CSS
npm run build:css

# Минификация JS
npm run build:js

# Оптимизация изображений
npm run optimize:images
```

### CDN / CDN развертывание

```html
<!-- Использование CDN -->
<link rel="stylesheet" href="https://cdn.example.com/modern-editor-ui.min.css">
<script src="https://cdn.example.com/modern-editor-ui.min.js"></script>
```

## Поддержка браузеров / Browser Support

| Браузер / Browser | Версия / Version |
|------------------|------------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

## Лицензия / License

MIT License - свободное использование и модификация.

## Поддержка / Support

Для получения поддержки:

1. Проверьте документацию
2. Посмотрите примеры в коде
3. Создайте issue в репозитории
4. Обратитесь к команде разработки 