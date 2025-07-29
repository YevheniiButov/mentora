# Editor Debug Panel Documentation

## Обзор

Панель отладки Editor Debug Panel - это комплексный инструмент для мониторинга состояния enhanced editor и диагностики проблем во время разработки и тестирования.

## Возможности

### 🔍 Мониторинг в реальном времени
- Состояние редактора GrapesJS
- Количество компонентов
- Выбранный компонент
- Текущее устройство (desktop/mobile/tablet)
- Активность пользователя

### 📊 API Логирование
- Все API вызовы с временными метками
- Успешные и неуспешные запросы
- Время выполнения запросов
- Экспорт логов для анализа

### 🧩 Отслеживание компонентов
- Дерево компонентов
- Детали выбранного компонента
- Состояние компонентов
- История изменений

### 🎨 CSS Переменные
- Мониторинг CSS переменных
- Состояние CSS Variables Manager
- Значения переменных в реальном времени

### ⚡ Метрики производительности
- Количество компонентов
- Шаги отмены/повтора
- Использование памяти (если доступно)
- Общая производительность

### 🛠️ Инструменты диагностики
- Очистка кэша
- Сброс к настройкам по умолчанию
- Принудительная перезагрузка шаблона
- Валидация текущего состояния
- Экспорт/импорт состояния
- Восстановление после ошибок

## Установка и настройка

### Автоматическая инициализация

Панель отладки автоматически инициализируется при загрузке страницы:

```javascript
// Автоматически создается при готовности редактора
window.debugPanel = new EditorDebugPanel(window.editor, {
    enabled: true,
    theme: 'dark',
    autoRefresh: true,
    refreshInterval: 2000,
    maxLogEntries: 100
});
```

### Ручная инициализация

```javascript
// Создание экземпляра панели отладки
const debugPanel = new EditorDebugPanel(editor, {
    enabled: true,
    position: 'bottom-right',
    theme: 'dark', // или 'light'
    autoRefresh: true,
    refreshInterval: 2000,
    maxLogEntries: 100
});

// Показать/скрыть панель
debugPanel.show();
debugPanel.hide();
debugPanel.toggle();
```

## Использование

### Кнопка переключения

В правом нижнем углу появляется кнопка 🐛 для переключения панели отладки.

### Вкладки панели

#### 1. Overview (Обзор)
- **Editor Status**: Текущее состояние редактора
- **Recent Activity**: Последние действия
- **Quick Actions**: Быстрые действия

#### 2. State (Состояние)
- **Editor State**: JSON представление состояния редактора
- **State History**: История изменений состояния
- **Controls**: Обновление, экспорт, сравнение

#### 3. API Logs (API Логи)
- **API Calls**: Все API вызовы
- **Filters**: Фильтрация по успеху/ошибкам
- **Export**: Экспорт логов

#### 4. Components (Компоненты)
- **Component Tree**: Дерево компонентов
- **Selected Component**: Детали выбранного компонента

#### 5. CSS Variables (CSS Переменные)
- **CSS Variables**: Список переменных
- **Manager Status**: Состояние менеджера

#### 6. Performance (Производительность)
- **Performance Metrics**: Метрики производительности
- **Memory Usage**: Использование памяти

#### 7. Tools (Инструменты)
- **Debug Tools**: Инструменты диагностики
- **Error Recovery**: Восстановление после ошибок

## API Методы

### Логирование

```javascript
// Логирование операций с шаблонами
debugPanel.logTemplateOperation('load', { templateId: 'test' });

// Логирование API вызовов
debugPanel.logAPICall('/api/template', 'POST', data, response, error);

// Логирование активности
debugPanel.logActivity('User clicked save button');
```

### Обновление данных

```javascript
// Обновить все данные
debugPanel.refreshAllData();

// Обновить конкретную вкладку
debugPanel.refreshTabContent('state');

// Обновить обзор
debugPanel.updateOverview();
```

### Экспорт данных

```javascript
// Экспорт всей отладочной информации
debugPanel.exportDebugInfo();

// Экспорт текущего состояния
debugPanel.exportCurrentState();

// Экспорт API логов
debugPanel.exportApiLogs();
```

### Инструменты диагностики

```javascript
// Очистка кэша
debugPanel.clearCache();

// Сброс к настройкам по умолчанию
debugPanel.resetToDefaults();

// Принудительная перезагрузка шаблона
debugPanel.forceTemplateReload();

// Валидация состояния
debugPanel.validateCurrentState();

// Перезапуск редактора
debugPanel.restartEditor();

// Безопасный режим
debugPanel.enableSafeMode();
```

## Интеграция с проектом

### Подключение в шаблоне

Добавьте в `enhanced_editor.html`:

```html
<!-- Debug Panel -->
<script src="{{ url_for('static', filename='js/editor-debug.js') }}"></script>
```

### Интеграция с API

```javascript
// Перехват API вызовов для логирования
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const startTime = Date.now();
    
    return originalFetch.apply(this, args)
        .then(response => {
            const duration = Date.now() - startTime;
            if (window.debugPanel) {
                window.debugPanel.logAPICall(args[0], 'GET', null, { duration });
            }
            return response;
        })
        .catch(error => {
            if (window.debugPanel) {
                window.debugPanel.logAPICall(args[0], 'GET', null, null, error.message);
            }
            throw error;
        });
};
```

### Интеграция с CSS Variables Manager

```javascript
// Логирование изменений CSS переменных
if (window.cssVariablesManager) {
    window.cssVariablesManager.on('change', (variable, value) => {
        if (window.debugPanel) {
            window.debugPanel.logActivity(`CSS variable changed: ${variable} = ${value}`);
        }
    });
}
```

## Настройки

### Опции конфигурации

```javascript
const options = {
    enabled: true,              // Включить/выключить панель
    position: 'bottom-right',   // Позиция панели
    theme: 'dark',              // Тема: 'dark' или 'light'
    autoRefresh: true,          // Автообновление
    refreshInterval: 2000,      // Интервал обновления (мс)
    maxLogEntries: 100          // Максимум записей в логах
};
```

### Кастомизация стилей

```css
/* Переопределение стилей панели */
.debug-panel {
    width: 600px !important;
    max-height: 700px !important;
}

.debug-toggle {
    background: #28a745 !important;
}
```

## Примеры использования

### Отладка проблем с загрузкой шаблона

```javascript
// Включить подробное логирование
debugPanel.logTemplateOperation('load', { templateId: 'problematic-template' });

// Мониторинг API вызовов
debugPanel.logAPICall('/api/template/load', 'POST', { id: 'problematic-template' });

// Проверка состояния после загрузки
setTimeout(() => {
    debugPanel.refreshEditorState();
    debugPanel.updateComponentTree();
}, 1000);
```

### Диагностика проблем с CSS переменными

```javascript
// Проверка состояния CSS Variables Manager
debugPanel.updateCSSVariables();

// Логирование изменений
debugPanel.logActivity('CSS variables updated');

// Экспорт состояния для анализа
debugPanel.exportCurrentState();
```

### Анализ производительности

```javascript
// Мониторинг метрик производительности
debugPanel.updatePerformanceMetrics();

// Проверка использования памяти
if (performance.memory) {
    console.log('Memory usage:', performance.memory);
}
```

## Устранение неполадок

### Панель не появляется

1. Проверьте, что файл `editor-debug.js` подключен
2. Убедитесь, что редактор инициализирован
3. Проверьте консоль на ошибки JavaScript

### Нет данных в логах

1. Проверьте настройки логирования
2. Убедитесь, что API вызовы перехватываются
3. Проверьте права доступа к localStorage

### Проблемы с производительностью

1. Увеличьте интервал обновления
2. Ограничьте количество записей в логах
3. Отключите автообновление при необходимости

## Безопасность

### В продакшене

```javascript
// Отключить панель отладки в продакшене
const debugPanel = new EditorDebugPanel(editor, {
    enabled: process.env.NODE_ENV === 'development'
});
```

### Очистка данных

```javascript
// Очистить все логи
debugPanel.clearLogs();
debugPanel.clearApiLogs();

// Уничтожить панель
debugPanel.destroy();
```

## Расширение функциональности

### Добавление новых вкладок

```javascript
// Расширение класса
class CustomDebugPanel extends EditorDebugPanel {
    constructor(editor, options) {
        super(editor, options);
        this.addCustomTab();
    }
    
    addCustomTab() {
        // Добавление новой вкладки
    }
}
```

### Кастомные метрики

```javascript
// Добавление собственных метрик
debugPanel.performanceMetrics.customMetric = 'value';
debugPanel.updatePerformanceMetrics();
```

## Заключение

Editor Debug Panel предоставляет мощные инструменты для отладки и мониторинга enhanced editor. Используйте её для:

- Диагностики проблем во время разработки
- Мониторинга производительности
- Анализа пользовательских действий
- Экспорта данных для дальнейшего анализа

Панель автоматически интегрируется с проектом и предоставляет удобный интерфейс для всех задач отладки. 