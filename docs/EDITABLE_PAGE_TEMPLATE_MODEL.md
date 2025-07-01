# EditablePageTemplate Model Documentation

## Обзор / Overview

Модель `EditablePageTemplate` предназначена для системы визуального редактирования страниц, которая позволяет администраторам редактировать существующие Jinja2 шаблоны через интерфейс GrapesJS, сохраняя при этом логику шаблонов.

The `EditablePageTemplate` model is designed for a visual page editing system that allows administrators to edit existing Jinja2 templates through the GrapesJS interface while preserving template logic.

## Структура модели / Model Structure

### Основные поля / Primary Fields

| Поле / Field | Тип / Type | Описание / Description |
|--------------|------------|----------------------|
| `id` | Integer | Первичный ключ / Primary key |
| `template_path` | String(500) | Путь к Jinja2 шаблону / Path to Jinja2 template |
| `original_content` | Text | Оригинальное содержимое шаблона / Original template content |
| `grapesjs_content` | Text | Контент отредактированный в GrapesJS / Content edited in GrapesJS |
| `css_overrides` | Text | CSS переопределения / CSS overrides |
| `js_modifications` | Text | JavaScript модификации / JavaScript modifications |
| `is_live` | Boolean | Активен ли шаблон / Is template active |
| `language` | String(5) | Язык шаблона (en/ru) / Template language |

### Связи / Relationships

| Поле / Field | Тип / Type | Описание / Description |
|--------------|------------|----------------------|
| `created_by` | Integer | Внешний ключ к User / Foreign key to User |

### Метаданные / Metadata

| Поле / Field | Тип / Type | Описание / Description |
|--------------|------------|----------------------|
| `template_name` | String(255) | Человекочитаемое имя / Human-readable name |
| `description` | Text | Описание шаблона / Template description |
| `category` | String(100) | Категория шаблона / Template category |
| `version` | String(20) | Версия шаблона / Template version |
| `is_system` | Boolean | Системный шаблон / System template |

### Временные метки / Timestamps

| Поле / Field | Тип / Type | Описание / Description |
|--------------|------------|----------------------|
| `created_at` | DateTime | Время создания / Creation time |
| `updated_at` | DateTime | Время обновления / Update time |

## Методы модели / Model Methods

### Основные методы / Primary Methods

#### `to_dict()`
Сериализация в словарь / Serialize to dictionary
```python
template_dict = template.to_dict()
```

#### `backup()`
Создание резервной копии шаблона / Create template backup
```python
backup_data = template.backup()
```

#### `restore(backup_data)`
Восстановление шаблона из резервной копии / Restore template from backup
```python
success = template.restore(backup_data)
```

### Утилитарные методы / Utility Methods

#### `get_effective_content()`
Получение эффективного содержимого шаблона / Get effective template content
```python
content = template.get_effective_content()  # Returns GrapesJS content or original
```

#### `has_modifications()`
Проверка наличия модификаций / Check if template has modifications
```python
has_mods = template.has_modifications()
```

#### `reset_to_original()`
Сброс к оригинальному содержимому / Reset to original content
```python
success = template.reset_to_original()
```

### Методы управления состоянием / State Management Methods

#### `activate()`
Активация шаблона / Activate template
```python
success = template.activate()
```

#### `deactivate()`
Деактивация шаблона / Deactivate template
```python
success = template.deactivate()
```

### Классовые методы / Class Methods

#### `get_by_path_and_language(template_path, language='en')`
Получение шаблона по пути и языку / Get template by path and language
```python
template = EditablePageTemplate.get_by_path_and_language('templates/index.html', 'ru')
```

#### `get_live_templates(language='en')`
Получение активных шаблонов / Get live templates
```python
live_templates = EditablePageTemplate.get_live_templates('ru')
```

## Индексы / Indexes

Модель включает следующие индексы для оптимизации производительности:

- `idx_editable_templates_path_lang` - композитный индекс по пути и языку
- `idx_editable_templates_live` - индекс по статусу активности
- `idx_editable_templates_category` - индекс по категории
- `idx_editable_templates_created_by` - индекс по создателю

## Примеры использования / Usage Examples

### Создание нового шаблона / Creating a new template

```python
from models import EditablePageTemplate, User

# Получаем пользователя
user = User.query.filter_by(email='admin@example.com').first()

# Создаем шаблон
template = EditablePageTemplate(
    template_path='templates/lesson.html',
    template_name='Lesson Template',
    description='Шаблон для страниц уроков',
    original_content='''
<!DOCTYPE html>
<html>
<head>
    <title>{{ lesson.title }}</title>
</head>
<body>
    <h1>{{ lesson.title }}</h1>
    <div class="content">{{ lesson.content }}</div>
</body>
</html>
    ''',
    language='ru',
    category='lesson',
    created_by=user.id
)

db.session.add(template)
db.session.commit()
```

### Редактирование шаблона / Editing a template

```python
# Получаем шаблон
template = EditablePageTemplate.get_by_path_and_language('templates/lesson.html', 'ru')

# Обновляем GrapesJS контент
template.grapesjs_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ lesson.title }}</title>
    <style>
        .lesson-header { background: #f0f0f0; padding: 20px; }
    </style>
</head>
<body>
    <div class="lesson-header">
        <h1>{{ lesson.title }}</h1>
    </div>
    <div class="content">{{ lesson.content }}</div>
</body>
</html>
'''

# Добавляем CSS переопределения
template.css_overrides = '''
.lesson-header { 
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 8px;
}
'''

# Активируем шаблон
template.activate()
db.session.commit()
```

### Резервное копирование и восстановление / Backup and restore

```python
# Создание резервной копии
backup = template.backup()

# Восстановление из резервной копии
template.restore(backup)
db.session.commit()
```

## Интеграция с системой / System Integration

### Связь с User моделью / User Model Relationship

```python
# Получение всех шаблонов пользователя
user_templates = user.editable_templates.all()

# Получение активных шаблонов пользователя
active_templates = user.editable_templates.filter_by(is_live=True).all()
```

### Использование в роутах / Usage in Routes

```python
@app.route('/admin/templates/<int:template_id>')
@login_required
def edit_template(template_id):
    template = EditablePageTemplate.query.get_or_404(template_id)
    return render_template('admin/edit_template.html', template=template)

@app.route('/admin/templates/<int:template_id>/update', methods=['POST'])
@login_required
def update_template(template_id):
    template = EditablePageTemplate.query.get_or_404(template_id)
    
    template.grapesjs_content = request.form.get('grapesjs_content')
    template.css_overrides = request.form.get('css_overrides')
    template.js_modifications = request.form.get('js_modifications')
    
    db.session.commit()
    return jsonify({'success': True})
```

## Безопасность / Security

- Все операции с шаблонами требуют аутентификации
- Системные шаблоны (`is_system=True`) имеют дополнительные ограничения
- Резервные копии создаются перед критическими операциями
- Валидация контента перед сохранением

## Производительность / Performance

- Индексы оптимизированы для частых запросов
- Ленивая загрузка связей (`lazy='dynamic'`)
- Эффективные запросы по пути и языку
- Кэширование активных шаблонов

## Миграции / Migrations

Для создания таблицы в базе данных выполните:

```bash
flask db migrate -m "Add EditablePageTemplate model"
flask db upgrade
```

Или создайте таблицы напрямую:

```python
from app import app, db
from models import EditablePageTemplate

with app.app_context():
    db.create_all()
``` 