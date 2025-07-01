# Advanced Design System Integration

## Обзор

Advanced Design System - это комплексная система дизайна для Visual Builder, которая включает в себя продвинутые инструменты для работы со стилями, цветами, типографикой и визуализацией CSS Box Model.

## Архитектура

### Основные модули

1. **AdvancedStyleEditor** - Визуальный CSS редактор
2. **BoxModelVisualizer** - Визуализатор CSS Box Model
3. **ColorSystem** - Система управления цветами
4. **TypographySystem** - Система типографики

### Структура файлов

```
static/js/visual-builder/
├── advanced-style-editor.js    # Основной редактор стилей
├── box-model-visualizer.js     # Визуализатор Box Model
├── color-system.js             # Система цветов
└── typography-system.js        # Система типографики
```

## Интеграция с Visual Builder

### Подключение модулей

Модули подключаются в шаблоне `templates/admin/visual_builder.html`:

```html
<!-- Advanced Design System Modules -->
<script src="{{ url_for('static', filename='js/visual-builder/advanced-style-editor.js') }}"></script>
<script src="{{ url_for('static', filename='js/visual-builder/box-model-visualizer.js') }}"></script>
<script src="{{ url_for('static', filename='js/visual-builder/color-system.js') }}"></script>
<script src="{{ url_for('static', filename='js/visual-builder/typography-system.js') }}"></script>
```

### Интеграция в Visual Builder

Основной класс `VisualBuilder` получил новые методы:

```javascript
// Открытие Advanced Style Editor
openAdvancedStyleEditor()

// Применение стилей к элементу
applyStylesToElement(element, styles)

// Обновление панели свойств
updatePropertiesPanel()

// Обновление стиля элемента
updateElementStyle(property, value)
```

## Использование

### Открытие Advanced Style Editor

1. Выберите элемент на canvas
2. Нажмите кнопку "Advanced" в панели свойств
3. Или используйте метод `visualBuilder.openAdvancedStyleEditor()`

### Работа с Color System

```javascript
const colorSystem = new ColorSystem();

// Генерация палитры
const palette = colorSystem.generatePalette('#3ECDC1');

// Получение контрастных цветов
const contrastColors = colorSystem.getContrastColors('#3ECDC1');
```

### Работа с Typography System

```javascript
const typographySystem = new TypographySystem();

// Генерация шкалы размеров
const scale = typographySystem.generateScale(16, 1.25);

// Получение типографических стилей
const styles = typographySystem.getTypographyStyles('heading');
```

### Работа с Box Model Visualizer

```javascript
const visualizer = new BoxModelVisualizer({
    targetElement: element,
    onUpdate: (boxModel) => {
        console.log('Box Model updated:', boxModel);
    }
});

visualizer.show();
```

## UI Компоненты

### Кнопка Advanced Style Editor

Добавлена в панель свойств:

```html
<button class="btn btn-sm btn-primary" onclick="visualBuilder.openAdvancedStyleEditor()" title="Advanced Style Editor">
    <i class="bi bi-palette2"></i>
    Advanced
</button>
```

### Панель свойств

Обновлена для отображения:
- Информации о выбранном элементе
- Базовых стилей (ширина, высота, отступы)
- Кнопки для открытия Advanced Style Editor

## CSS Стили

Добавлены стили для Advanced Style Editor в `static/css/visual-builder.css`:

- `.advanced-style-editor` - Основной контейнер
- `.advanced-style-editor-content` - Содержимое редактора
- `.style-control-group` - Группы контролов
- `.style-control` - Отдельные контролы
- `.color-picker` - Выбор цвета
- `.range-slider` - Слайдеры

## Тестирование

### Тестовая страница

Создана тестовая страница `test_reports/advanced_design_system_integration_test.html` для проверки:

- Загрузки модулей
- Работы Advanced Style Editor
- Функциональности Color System
- Функциональности Typography System
- Работы Box Model Visualizer

### Запуск тестов

1. Откройте тестовую страницу в браузере
2. Выберите тестовый элемент
3. Нажмите кнопки для тестирования различных модулей
4. Проверьте результаты в консоли браузера

## Конфигурация

### Настройки Visual Builder

```javascript
window.visualBuilder = new VisualBuilder({
    apiEndpoint: '/api/visual-builder',
    mediaEndpoint: '/api/visual-builder/media',
    templatesEndpoint: '/api/visual-builder/templates',
    currentPageId: null,
    currentUserId: userId,
    csrfToken: csrfToken
});
```

### Настройки Advanced Style Editor

```javascript
const editor = new AdvancedStyleEditor({
    targetElement: element,
    onStyleChange: (styles) => {
        // Обработка изменений стилей
    },
    onClose: () => {
        // Обработка закрытия редактора
    }
});
```

## Обратная совместимость

- Все существующие функции Visual Builder сохранены
- Новые модули работают независимо
- Старые элементы продолжают работать как прежде
- Постепенная миграция на новые возможности

## Производительность

### Оптимизации

- Ленивая загрузка модулей
- Кэширование результатов
- Дебаунсинг для частых операций
- Виртуализация для больших списков

### Мониторинг

```javascript
// Логирование производительности
console.time('style-application');
this.applyStylesToElement(element, styles);
console.timeEnd('style-application');
```

## Безопасность

### Валидация

- Проверка типов данных
- Санитизация CSS значений
- Защита от XSS атак
- Валидация цветовых значений

### Ограничения

- Максимальный размер CSS: 100KB
- Максимальное количество правил: 1000
- Запрещенные CSS свойства: `expression`, `javascript:`

## Расширение

### Добавление новых модулей

1. Создайте новый файл модуля
2. Реализуйте базовый интерфейс
3. Добавьте подключение в шаблон
4. Интегрируйте в Visual Builder

### Кастомизация

```javascript
// Расширение Color System
class CustomColorSystem extends ColorSystem {
    generateCustomPalette(baseColor) {
        // Кастомная логика генерации палитры
    }
}
```

## Поддержка

### Отладка

- Включите режим отладки в консоли
- Используйте тестовую страницу
- Проверьте логи в консоли браузера

### Известные проблемы

- Некоторые браузеры могут не поддерживать все CSS свойства
- Мобильные устройства имеют ограничения по производительности
- Старые версии браузеров могут требовать полифиллов

## Планы развития

### Краткосрочные цели

- [ ] Добавление анимаций и переходов
- [ ] Поддержка CSS Grid и Flexbox
- [ ] Интеграция с системой тем

### Долгосрочные цели

- [ ] AI-ассистент для дизайна
- [ ] Автоматическая оптимизация
- [ ] Экспорт в различные форматы
- [ ] Интеграция с внешними API

## Заключение

Advanced Design System предоставляет мощные инструменты для создания профессиональных веб-страниц в Visual Builder. Система модульная, расширяемая и полностью интегрирована с существующей архитектурой проекта. 