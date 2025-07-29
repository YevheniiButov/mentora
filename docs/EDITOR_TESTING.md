# Enhanced Editor Testing System

## Обзор

Система тестирования для Enhanced Editor предоставляет комплексные инструменты для автоматизированного тестирования всех функций визуального редактора Dental Academy.

## Архитектура

### Основные компоненты

#### EditorTestSuite
Основной класс для запуска тестов редактора.

```javascript
class EditorTestSuite {
    constructor(editor, options = {})
    async runAllTests()
    async runCategoryTests(category)
    generateReport()
}
```

#### EditorTestUtils
Утилиты для тестирования, включая скриншоты, производительность и валидацию.

```javascript
class EditorTestUtils {
    async captureScreenshot(name, element)
    async compareScreenshots(screenshot1, screenshot2)
    startPerformanceTimer(name)
    endPerformanceTimer(name)
    validateHTML(html)
    validateCSS(css)
}
```

## Категории тестов

### 1. Template Loading & Parsing
- Загрузка шаблонов
- Парсинг Jinja2 синтаксиса
- Валидация структуры HTML

### 2. Component System
- Вставка компонентов Dental Academy
- Редактирование traits
- Валидация компонентов

### 3. Style Management
- Редактирование стилей
- Responsive дизайн
- Bootstrap классы

### 4. CSS Variables
- Загрузка CSS переменных
- Редактирование переменных
- Real-time обновления

### 5. Save & Restore
- Сохранение шаблонов
- Создание резервных копий
- Восстановление из бэкапов

### 6. Deployment System
- Валидация шаблонов
- Деплой шаблонов
- Откат деплоя

### 7. API Integration
- Тестирование API endpoints
- Обработка ошибок
- Валидация ответов

### 8. Visual Regression
- Сравнение скриншотов
- Responsive breakpoints
- Применение тем

### 9. User Workflow
- Полный workflow редактирования
- Сценарии ошибок
- Edge cases

## Использование

### Базовое использование

```javascript
// Создание тестового набора
const testSuite = new EditorTestSuite(editor, {
    verbose: true,
    testTemplates: ['learning/subject_view.html']
});

// Запуск всех тестов
await testSuite.runAllTests();

// Запуск тестов по категории
await testSuite.runCategoryTests('template');

// Генерация отчета
const report = testSuite.generateReport();
```

### Быстрое тестирование

```javascript
// Быстрый тест
const report = await EditorTestRunner.runQuickTest(editor);

// Полный тест
const report = await EditorTestRunner.runFullTest(editor);
```

### Использование утилит

```javascript
const utils = new EditorTestUtils();

// Создание скриншота
const screenshot = await utils.captureScreenshot('test-state');

// Измерение производительности
utils.startPerformanceTimer('operation');
// ... выполнение операции
utils.endPerformanceTimer('operation');

// Валидация HTML
const validation = utils.validateHTML(html);
```

## Примеры тестов

### Тест загрузки шаблона

```javascript
async testTemplateLoading(templatePath) {
    const response = await fetch(`/api/content-editor/load?template_path=${templatePath}`);
    const data = await response.json();
    
    this.utils.assert(data.success, 'Template load failed');
    this.utils.assert(data.html || data.grapesjs_data, 'No content received');
    
    // Загрузка в редактор
    if (data.grapesjs_data) {
        this.editor.loadData(data.grapesjs_data);
    } else {
        this.editor.setComponents(data.html);
    }
    
    // Проверка загрузки
    const components = this.editor.getComponents();
    this.utils.assert(components.length > 0, 'No components loaded');
}
```

### Тест компонентов

```javascript
async testComponentInsertion(componentType) {
    const component = this.editor.addComponent({
        type: componentType,
        content: this.getTestComponentContent(componentType)
    });
    
    this.utils.assert(component, 'Component not created');
    
    const components = this.editor.getComponents();
    const foundComponent = components.find(c => c.get('type') === componentType);
    this.utils.assert(foundComponent, 'Component not found');
}
```

### Тест CSS переменных

```javascript
async testCSSVariablesEditing() {
    if (!window.cssVariablesManager) return;
    
    const manager = window.cssVariablesManager;
    manager.updateVariable('--primary-color', '#ff0000');
    
    const variables = manager.getVariables();
    this.utils.assert(variables['--primary-color'] === '#ff0000', 'Variable not updated');
    
    // Проверка real-time обновлений
    const computedStyle = getComputedStyle(document.documentElement);
    const appliedColor = computedStyle.getPropertyValue('--primary-color').trim();
    this.utils.assert(appliedColor === '#ff0000', 'Variable not applied in real-time');
}
```

## UI для тестирования

### Панель тестирования

Система автоматически создает панель тестирования в правом верхнем углу редактора:

- **Run All Tests** - запуск всех тестов
- **Run Category** - запуск тестов по категории
- **Clear Results** - очистка результатов
- **Progress Bar** - индикатор прогресса
- **Results List** - список результатов тестов

### Статусы тестов

- ✅ **PASS** - тест прошел успешно
- ❌ **FAIL** - тест провалился
- ⏳ **RUNNING** - тест выполняется

### Отчеты

После завершения тестов генерируется подробный отчет:

```javascript
{
    summary: {
        total: 25,
        passed: 23,
        failed: 2,
        successRate: 92.0
    },
    categories: {
        template: { total: 3, passed: 3, failed: 0 },
        components: { total: 4, passed: 4, failed: 0 },
        // ...
    },
    details: [
        {
            category: 'template',
            name: 'Load Subject View Template',
            status: 'pass',
            duration: 1500,
            error: null
        }
        // ...
    ]
}
```

## Производительность

### Метрики производительности

Система отслеживает производительность операций:

- Время загрузки шаблонов
- Время вставки компонентов
- Время сохранения
- Время валидации
- Время деплоя

### Оптимизация

- Параллельное выполнение независимых тестов
- Кэширование результатов
- Минимизация DOM операций
- Эффективное управление памятью

## Визуальное регрессионное тестирование

### Создание скриншотов

```javascript
const utils = new EditorTestUtils();

// Создание скриншота
const screenshot = await utils.captureScreenshot('initial-state');

// Сравнение скриншотов
const comparison = await utils.compareScreenshots(screenshot1, screenshot2);
```

### Анализ различий

- Покомпонентное сравнение
- Настройка порога различий
- Игнорирование анимаций
- Поддержка разных разрешений

## Интеграция с CI/CD

### Автоматизированное тестирование

```yaml
# .github/workflows/editor-tests.yml
name: Editor Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm install
      - name: Run editor tests
        run: npm run test:editor
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results/
```

### Отчеты в CI

- Автоматическая генерация отчетов
- Уведомления о проваленных тестах
- Интеграция с системами мониторинга
- Slack/Discord уведомления

## Расширение системы

### Добавление новых тестов

```javascript
// Регистрация нового теста
testSuite.registerTest('custom', 'My Custom Test', async () => {
    // Логика теста
    this.utils.assert(condition, 'Test assertion');
});
```

### Создание кастомных утилит

```javascript
class CustomTestUtils extends EditorTestUtils {
    async customTestFunction() {
        // Кастомная логика тестирования
    }
}
```

### Интеграция с внешними системами

```javascript
// Интеграция с внешними API
async testExternalAPI() {
    const response = await fetch('https://api.example.com/test');
    const data = await response.json();
    this.utils.assert(data.success, 'External API test failed');
}
```

## Отладка

### Логирование

```javascript
// Включение подробного логирования
const testSuite = new EditorTestSuite(editor, {
    verbose: true
});

// Логирование в тестах
this.log('Test message', { data: 'value' });
```

### Обработка ошибок

```javascript
try {
    await testSuite.runAllTests();
} catch (error) {
    console.error('Test suite failed:', error);
    
    // Сохранение состояния для отладки
    const state = testSuite.getCurrentState();
    console.log('Current state:', state);
}
```

### Воспроизведение ошибок

```javascript
// Сохранение состояния при ошибке
if (test.status === 'fail') {
    const state = {
        editor: testSuite.getEditorState(),
        test: test,
        error: test.error
    };
    
    localStorage.setItem('test-error-state', JSON.stringify(state));
}
```

## Лучшие практики

### Организация тестов

1. **Группировка по функциональности** - тесты должны быть логически сгруппированы
2. **Изоляция тестов** - каждый тест должен быть независимым
3. **Очистка состояния** - тесты должны очищать состояние после выполнения
4. **Описательные имена** - имена тестов должны быть понятными

### Производительность

1. **Минимизация DOM операций** - используйте эффективные селекторы
2. **Кэширование результатов** - избегайте повторных вычислений
3. **Параллельное выполнение** - запускайте независимые тесты параллельно
4. **Оптимизация скриншотов** - используйте сжатие и оптимизацию

### Надежность

1. **Обработка ошибок** - всегда обрабатывайте исключения
2. **Таймауты** - устанавливайте разумные таймауты для операций
3. **Retry логика** - повторяйте неустойчивые операции
4. **Валидация результатов** - проверяйте корректность результатов

## Заключение

Система тестирования Enhanced Editor предоставляет мощные инструменты для обеспечения качества и надежности визуального редактора Dental Academy. Используйте эти инструменты для:

- Автоматизированного тестирования всех функций
- Обнаружения регрессий
- Измерения производительности
- Обеспечения стабильности при разработке

Система готова к использованию в продакшене и может быть расширена для поддержки новых требований проекта. 