# Page Editor API Documentation

## Обзор / Overview

API роуты для редактора страниц предоставляют полный функционал для работы с Jinja2 шаблонами через GrapesJS интерфейс. Все роуты требуют авторизации администратора и включают CSRF защиту для POST запросов.

The page editor API routes provide full functionality for working with Jinja2 templates through the GrapesJS interface. All routes require admin authentication and include CSRF protection for POST requests.

## Базовый URL / Base URL

```
/<lang>/admin/content-editor/api/editor/
```

Где `<lang>` - код языка (en, ru, nl, etc.)
Where `<lang>` is the language code (en, ru, nl, etc.)

## Структура ответов / Response Structure

Все API ответы имеют единообразную структуру:
All API responses have a consistent structure:

```json
{
  "success": true|false,
  "message": "Human readable message",
  "data": {
    // Response data
  },
  "error": "Error details (if success=false)"
}
```

## Аутентификация / Authentication

Все роуты требуют:
All routes require:

- Авторизацию пользователя / User authentication
- Права администратора / Admin privileges
- CSRF токен для POST запросов / CSRF token for POST requests

## Роуты / Routes

### 1. GET /api/editor/templates

Получение списка всех редактируемых шаблонов
Get list of all editable templates

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Found 15 templates",
  "data": {
    "templates": [
      {
        "path": "learning/subject_view.html",
        "name": "subject_view",
        "size": 31572,
        "modified": "2024-01-15T10:30:00",
        "is_live": false,
        "has_backup": true,
        "template_id": 123
      }
    ],
    "total": 15
  }
}
```

### 2. GET /api/editor/template/<path>

Получение конкретного шаблона для редактирования
Get specific template for editing

**Параметры / Parameters:**
- `path` - относительный путь к шаблону / relative path to template

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Template loaded successfully",
  "data": {
    "template": {
      "id": 123,
      "template_path": "learning/subject_view.html",
      "original_content": "...",
      "grapesjs_content": "...",
      "css_overrides": "...",
      "js_modifications": "...",
      "is_live": false,
      "language": "en",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "file_content": "{% extends 'base.html' %}...",
    "file_size": 31572,
    "last_modified": "2024-01-15T10:30:00"
  }
}
```

### 3. POST /api/editor/template/parse

Парсинг Jinja2 шаблона в GrapesJS формат
Parse Jinja2 template to GrapesJS format

**Тело запроса / Request Body:**
```json
{
  "template_path": "learning/subject_view.html"
}
```

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Template parsed successfully",
  "data": {
    "template_path": "learning/subject_view.html",
    "language": "ru",
    "css_variables": {
      "--subject-view-bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      "--text-primary": "#333333"
    },
    "preserved_logic": "...",
    "components": [
      {
        "id": "component_0",
        "type": "div",
        "content": "...",
        "styles": {},
        "attributes": {},
        "editable": true
      }
    ],
    "structure": {
      "extends": ["base.html"],
      "includes": [],
      "blocks": ["title", "content"],
      "variables": ["t('learning_map', lang)"],
      "loops": ["for path in learning_paths"],
      "conditions": ["if selected_subject"]
    },
    "metadata": {
      "file_size": 31572,
      "lines_count": 503,
      "has_extends": true,
      "has_includes": false,
      "blocks_count": 4,
      "variables_count": 115
    }
  }
}
```

### 4. POST /api/editor/template/save

Сохранение отредактированного шаблона
Save edited template

**Тело запроса / Request Body:**
```json
{
  "template_path": "learning/subject_view.html",
  "grapesjs_content": "[{\"type\":\"div\",\"content\":\"...\"}]",
  "css_overrides": "{\"--test-color\":\"#ff0000\"}",
  "js_modifications": "console.log('test');"
}
```

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Template saved successfully",
  "data": {
    "template_id": 123,
    "backup_path": "backup/templates/subject_view.html.backup_20240115_103000",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 5. POST /api/editor/template/preview

Создание превью-версии шаблона
Create preview version of template

**Тело запроса / Request Body:**
```json
{
  "template_path": "learning/subject_view.html",
  "preview_content": "<div class='test-preview'>Preview content</div>"
}
```

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Preview created successfully",
  "data": {
    "preview_url": "/static/preview/preview_subject_view_20240115_103000.html",
    "preview_path": "static/preview/preview_subject_view_20240115_103000.html"
  }
}
```

### 6. POST /api/editor/template/deploy

Публикация шаблона в продакшн
Deploy template to production

**Тело запроса / Request Body:**
```json
{
  "template_path": "learning/subject_view.html",
  "deploy_content": "<!-- Deployed template -->\n<div>Deployed content</div>"
}
```

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Template deployed successfully",
  "data": {
    "template_path": "learning/subject_view.html",
    "backup_path": "backup/templates/subject_view.html.backup_20240115_103000",
    "deployed_at": "2024-01-15T10:30:00Z"
  }
}
```

### 7. GET /api/editor/css-variables

Получение CSS переменных проекта
Get project CSS variables

**Ответ / Response:**
```json
{
  "success": true,
  "message": "Found 25 CSS files",
  "data": {
    "css_files": [
      {
        "path": "css/pages/learning_map.css",
        "name": "learning_map",
        "variables": {
          "--subject-view-bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          "--text-primary": "#333333"
        },
        "variables_count": 16
      }
    ],
    "total_files": 25,
    "total_variables": 156
  }
}
```

### 8. POST /api/editor/css-variables

Обновление CSS переменных
Update CSS variables

**Тело запроса / Request Body:**
```json
{
  "css_file": "css/pages/learning_map.css",
  "variables": {
    "--test-variable": "#00ff00",
    "--test-size": "16px"
  }
}
```

**Ответ / Response:**
```json
{
  "success": true,
  "message": "CSS variables updated successfully",
  "data": {
    "css_file": "css/pages/learning_map.css",
    "backup_path": "backup/templates/learning_map.css.backup_20240115_103000",
    "updated_variables": 2,
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

## Обработка ошибок / Error Handling

### Коды ошибок / Error Codes

- `400` - Неверные данные / Invalid data
- `404` - Шаблон не найден / Template not found
- `500` - Внутренняя ошибка сервера / Internal server error

### Примеры ошибок / Error Examples

```json
{
  "success": false,
  "message": "Template not found",
  "error": "File not found: templates/nonexistent.html"
}
```

```json
{
  "success": false,
  "message": "Invalid data provided",
  "error": "template_path is required"
}
```

## Безопасность / Security

### Проверки безопасности / Security Checks

1. **Пути файлов / File paths:**
   - Запрещены пути с `..` / Paths with `..` are forbidden
   - Запрещены абсолютные пути / Absolute paths are forbidden
   - Ограничение доступа к папке templates / Access limited to templates folder

2. **Авторизация / Authentication:**
   - Все роуты требуют авторизации / All routes require authentication
   - Только администраторы / Admin only access

3. **CSRF защита / CSRF Protection:**
   - Все POST запросы требуют CSRF токен / All POST requests require CSRF token

## Резервное копирование / Backup

### Автоматические бэкапы / Automatic Backups

- Создаются перед каждым изменением файла / Created before each file modification
- Сохраняются в папке `backup/templates/` / Saved in `backup/templates/` folder
- Имя файла включает timestamp / Filename includes timestamp

### Формат имени бэкапа / Backup Filename Format

```
filename.backup_YYYYMMDD_HHMMSS
```

## Логирование / Logging

Все операции логируются с уровнем INFO и ERROR:
All operations are logged with INFO and ERROR levels:

```python
logger.info(f"Backup created: {backup_path}")
logger.error(f"Error parsing template: {e}")
```

## Примеры использования / Usage Examples

### JavaScript (Frontend)

```javascript
// Получение списка шаблонов
fetch('/en/admin/content-editor/api/editor/templates')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Templates:', data.data.templates);
    }
  });

// Парсинг шаблона
fetch('/en/admin/content-editor/api/editor/template/parse', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    template_path: 'learning/subject_view.html'
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Parsed template:', data.data);
  }
});
```

### Python (Backend)

```python
import requests

# Получение CSS переменных
response = requests.get('http://localhost:5000/en/admin/content-editor/api/editor/css-variables')
data = response.json()

if data['success']:
    css_files = data['data']['css_files']
    for css_file in css_files:
        print(f"File: {css_file['path']}, Variables: {css_file['variables_count']}")
```

## Интеграция с GrapesJS / GrapesJS Integration

### Конфигурация GrapesJS / GrapesJS Configuration

```javascript
const editor = grapesjs.init({
  // ... other config
  storage: {
    type: 'remote',
    autosave: true,
    autoload: true,
    stepsBeforeSave: 1,
    urlStore: '/en/admin/content-editor/api/editor/template/save',
    urlLoad: '/en/admin/content-editor/api/editor/template/parse',
    params: {
      template_path: 'learning/subject_view.html'
    }
  }
});
```

### Обработка событий / Event Handling

```javascript
editor.on('storage:store', (data) => {
  console.log('Template saved:', data);
});

editor.on('storage:load', (data) => {
  console.log('Template loaded:', data);
});
```

## Заключение / Conclusion

API редактора страниц предоставляет полный функционал для работы с Jinja2 шаблонами через GrapesJS интерфейс, включая парсинг, редактирование, превью и публикацию. Все операции защищены и логируются для обеспечения безопасности и отслеживания изменений.

The page editor API provides full functionality for working with Jinja2 templates through the GrapesJS interface, including parsing, editing, preview, and deployment. All operations are secured and logged to ensure security and track changes. 