# CSS Variables Manager для Dental Academy

## Обзор

CSS Variables Manager - это комплексная система управления CSS переменными для проекта Dental Academy, интегрированная с редактором GrapesJS. Система позволяет динамически управлять дизайн-системой проекта через удобный веб-интерфейс.

## Основные возможности

### 🎨 Управление CSS переменными
- Загрузка переменных из CSS файлов проекта
- Редактирование цветов, размеров, градиентов и теней
- Категоризация переменных по типам
- Поддержка undo/redo операций

### 🔄 Интеграция с GrapesJS
- Автоматическое обновление стилей в редакторе
- Синхронизация изменений в реальном времени
- Поддержка live preview

### 💾 Персистентность данных
- Сохранение переменных в базе данных
- Версионирование изменений
- Экспорт/импорт настроек

## Архитектура

### Frontend компоненты

#### CSS Variables Manager (`static/js/css-variables-manager.js`)
Основной JavaScript модуль для управления CSS переменными.

**Основные методы:**
```javascript
// Инициализация менеджера
CSSVariablesManager.init(editor, options)

// Загрузка переменных
CSSVariablesManager.loadVariables()

// Обновление переменной
CSSVariablesManager.updateVariable(name, value)

// Экспорт настроек
CSSVariablesManager.exportSettings()

// Импорт настроек
CSSVariablesManager.importSettings(data)
```

#### Стили панели (`static/css/css-variables-panel.css`)
Стили для панели управления переменными в стиле glassmorphism.

### Backend API

#### Обновленные API endpoints

##### 1. Загрузка шаблона с полным парсингом Jinja2
```http
GET /api/content-editor/template/<path:template_path>
```

**Ответ:**
```json
{
  "success": true,
  "template": {
    "template_path": "learning/subject_view.html",
    "name": "subject_view.html",
    "content": "<!DOCTYPE html>...",
    "grapesjs_data": {...},
    "css_variables": {
      "--primary-color": "#3ECDC1",
      "--secondary-color": "#FF6B6B"
    },
    "jinja_logic": {
      "blocks": [...],
      "variables": [...],
      "macros": [...]
    },
    "metadata": {
      "file_size": 2048,
      "last_modified": "2025-07-02T00:30:00",
      "source": "file_system",
      "parsed_at": "2025-07-02T00:30:00"
    },
    "is_edited": false
  }
}
```

##### 2. Сохранение шаблона с конвертацией Jinja2
```http
POST /api/content-editor/save
```

**Тело запроса:**
```json
{
  "template_path": "learning/subject_view.html",
  "name": "Updated Subject View",
  "grapesjs_data": {...},
  "css_variables": {...},
  "jinja_logic": {...},
  "metadata": {...},
  "convert_to_jinja2": true
}
```

##### 3. Управление CSS переменными
```http
GET /api/content-editor/css-variables
POST /api/content-editor/css-variables
```

**GET ответ:**
```json
{
  "success": true,
  "css_variables": {
    "--primary-color": "#3ECDC1",
    "--secondary-color": "#FF6B6B",
    "--text-primary": "#2d3748",
    "--background-primary": "#ffffff"
  },
  "message": "CSS variables loaded successfully"
}
```

**POST тело запроса:**
```json
{
  "variables": {
    "--primary-color": "#4ECDC4",
    "--secondary-color": "#FF7B7B"
  }
}
```

##### 4. Live Preview
```http
POST /api/content-editor/live-preview
```

**Тело запроса:**
```json
{
  "template_path": "learning/subject_view.html",
  "grapesjs_data": {...},
  "css_variables": {...},
  "jinja_logic": {...}
}
```

**Ответ:**
```json
{
  "success": true,
  "preview_html": "<!DOCTYPE html>...",
  "message": "Preview generated successfully"
}
```

##### 5. Деплой шаблона
```http
POST /api/content-editor/deploy
```

**Тело запроса:**
```json
{
  "template_path": "learning/subject_view.html"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Template deployed successfully",
  "backup_path": "/backups/templates/subject_view_20250702_003000.html",
  "deployed_at": "2025-07-02T00:30:00"
}
```

## Модель данных

### CSSVariables (models.py)
```python
class CSSVariables(db.Model):
    __tablename__ = 'css_variables'
    
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(5), default='en', nullable=False, index=True)
    variables = db.Column(db.Text, nullable=False)  # JSON строка
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_default = db.Column(db.Boolean, default=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
```

## Вспомогательные функции

### extract_project_css_variables()
Извлекает CSS переменные из файлов проекта.

### validate_template_path(template_path)
Валидирует путь к шаблону для безопасности.

### create_template_backup(template_path)
Создает резервную копию шаблона.

### convert_grapesjs_to_jinja2(grapesjs_data, jinja_logic)
Конвертирует данные GrapesJS обратно в Jinja2 шаблон.

### update_css_variables(variables)
Обновляет CSS переменные и генерирует новый CSS.

### generate_live_preview_html(grapesjs_data, css_variables, jinja_logic, lang)
Генерирует полный HTML для live preview.

## Интеграция с Jinja2 парсером

Система полностью интегрирована с `Jinja2ToGrapesJSConverter`:

1. **Парсинг шаблонов**: Автоматическое извлечение Jinja2 логики
2. **Конвертация**: Преобразование между GrapesJS и Jinja2 форматами
3. **Сохранение**: Поддержка обоих форматов в базе данных
4. **Деплой**: Автоматическая конвертация при публикации

## Безопасность

### Валидация путей
- Проверка на path traversal атаки
- Ограничение доступа к файловой системе
- Валидация расширений файлов

### Права доступа
- Требуется авторизация администратора
- Проверка прав на редактирование
- Логирование всех операций

### Резервное копирование
- Автоматическое создание бэкапов
- Версионирование изменений
- Возможность отката изменений

## Использование

### 1. Инициализация в редакторе
```javascript
// В enhanced_editor.html
CSSVariablesManager.init(editor, {
    apiEndpoint: '/api/content-editor/css-variables',
    language: '{{ lang }}'
});
```

### 2. Загрузка шаблона
```javascript
fetch(`/api/content-editor/template/${templatePath}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            editor.setComponents(data.template.grapesjs_data);
            CSSVariablesManager.setVariables(data.template.css_variables);
        }
    });
```

### 3. Сохранение изменений
```javascript
const saveData = {
    template_path: templatePath,
    grapesjs_data: editor.getComponents(),
    css_variables: CSSVariablesManager.getVariables(),
    jinja_logic: jinjaLogic,
    convert_to_jinja2: true
};

fetch('/api/content-editor/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(saveData)
});
```

### 4. Live Preview
```javascript
fetch('/api/content-editor/live-preview', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        grapesjs_data: editor.getComponents(),
        css_variables: CSSVariablesManager.getVariables()
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        previewWindow.document.write(data.preview_html);
    }
});
```

## Обработка ошибок

### Сообщения об ошибках
Система поддерживает многоязычные сообщения об ошибках:

```python
def get_error_message(error: str, lang: str = 'en') -> str:
    messages = {
        'en': {
            'template_not_found': 'Template not found',
            'invalid_request': 'Invalid request data',
            'save_failed': 'Failed to save template',
            'deploy_failed': 'Failed to deploy template',
            'preview_failed': 'Failed to generate preview'
        },
        'ru': {
            'template_not_found': 'Шаблон не найден',
            'invalid_request': 'Неверные данные запроса',
            'save_failed': 'Не удалось сохранить шаблон',
            'deploy_failed': 'Не удалось опубликовать шаблон',
            'preview_failed': 'Не удалось создать предпросмотр'
        }
    }
```

### Логирование
Все операции логируются с детальной информацией:
- ID пользователя
- Время операции
- Тип операции
- Результат
- Детали ошибок

## Производительность

### Кэширование
- Кэширование CSS переменных в памяти
- Оптимизация загрузки шаблонов
- Минимизация запросов к базе данных

### Оптимизация
- Асинхронная загрузка переменных
- Ленивая загрузка шаблонов
- Сжатие CSS и HTML

## Расширение функциональности

### Добавление новых типов переменных
1. Обновите `CSSVariablesManager.getVariableType()`
2. Добавьте соответствующие контролы в UI
3. Обновите валидацию в backend

### Интеграция с другими редакторами
1. Создайте адаптер для нового редактора
2. Реализуйте интерфейс `EditorInterface`
3. Обновите API endpoints

### Поддержка новых форматов
1. Добавьте новый конвертер в `utils/template_parser.py`
2. Обновите логику конвертации
3. Добавьте тесты

## Тестирование

### Unit тесты
```python
def test_css_variables_extraction():
    variables = extract_project_css_variables()
    assert '--primary-color' in variables
    assert variables['--primary-color'] == '#3ECDC1'

def test_template_path_validation():
    is_valid, error = validate_template_path('learning/subject_view.html')
    assert is_valid == True
    assert error is None
```

### Integration тесты
```python
def test_css_variables_api():
    response = client.get('/api/content-editor/css-variables')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'css_variables' in data
```

## Заключение

CSS Variables Manager предоставляет полную функциональность для управления дизайн-системой Dental Academy с интеграцией в GrapesJS редактор. Система обеспечивает безопасность, производительность и расширяемость для будущих потребностей проекта. 