# Enhanced Editor System Guide / Руководство по системе расширенного редактора

[English](#english) | [Русский](#russian)

---

## English

### Table of Contents
1. [Installation Guide](#installation-guide)
2. [Administrator Guide](#administrator-guide)
3. [Developer Guide](#developer-guide)
4. [Configuration Reference](#configuration-reference)
5. [API Reference](#api-reference)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

### Installation Guide

#### Prerequisites
- Python 3.8+
- Flask 2.0+
- SQLAlchemy 1.4+
- PostgreSQL/MySQL/SQLite
- Node.js 14+ (for asset compilation)

#### Dependencies
```bash
pip install -r requirements.txt
# Additional editor dependencies
pip install grapesjs jinja2-to-grapesjs
```

#### Step-by-Step Setup

1. **Clone and Setup**
```bash
git clone <repository>
cd flask-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Migration**
```bash
# Run migration script
python scripts/migrate_editor.py

# Or manually
flask db upgrade
```

3. **Configuration**
```bash
# Copy configuration template
cp config/editor_config.example.py config/editor_config.py

# Edit configuration
nano config/editor_config.py
```

4. **Initialize Editor**
```bash
# Run automated setup
python utils/editor_installer.py

# Or manually
flask editor init
```

5. **Start Application**
```bash
flask run
# Access editor at: http://localhost:5000/admin/content-editor
```

#### Initial Configuration

1. **Environment Variables**
```bash
export EDITOR_ENABLED=true
export EDITOR_DEBUG=false
export EDITOR_CACHE_TTL=3600
export EDITOR_CDN_URL=https://cdn.example.com
```

2. **Database Configuration**
```python
# config/editor_config.py
EDITOR_DATABASE = {
    'backup_enabled': True,
    'backup_retention_days': 30,
    'auto_backup': True
}
```

3. **Security Settings**
```python
EDITOR_SECURITY = {
    'admin_only': True,
    'audit_logging': True,
    'session_timeout': 3600
}
```

---

### Administrator Guide

#### Editor Interface Overview

The enhanced editor provides a visual interface for editing Jinja2 templates:

**Main Components:**
- **Template Browser**: Navigate and select templates
- **Visual Editor**: Drag-and-drop interface powered by GrapesJS
- **Code Editor**: Direct Jinja2/HTML editing
- **Preview Panel**: Real-time preview of changes
- **Component Library**: Pre-built components for common elements

#### Template Editing Workflow

1. **Access Editor**
   - Navigate to `/admin/content-editor`
   - Login with admin credentials
   - Select template to edit

2. **Edit Template**
   - Use visual editor for layout changes
   - Switch to code editor for Jinja2 logic
   - Preview changes in real-time
   - Save draft or publish changes

3. **Deploy Changes**
   - Review changes in preview
   - Test functionality
   - Publish to live environment
   - Monitor for issues

#### Component Library Usage

**Available Components:**
- **Layout Components**: Container, Row, Column
- **Content Components**: Text, Image, Video
- **Form Components**: Input, Button, Select
- **Navigation Components**: Menu, Breadcrumb, Pagination
- **Interactive Components**: Modal, Accordion, Tabs

**Adding Custom Components:**
```javascript
// Register custom component
editor.DomComponents.addType('custom-component', {
    model: {
        defaults: {
            tagName: 'div',
            attributes: { class: 'custom-component' },
            content: '<h3>Custom Component</h3>'
        }
    }
});
```

#### Deployment Procedures

1. **Pre-deployment Checklist**
   - [ ] All changes tested in preview
   - [ ] Database backups created
   - [ ] Cache cleared
   - [ ] Performance impact assessed

2. **Deployment Steps**
```bash
# Backup current templates
python scripts/backup_templates.py

# Deploy changes
python scripts/deploy_editor.py

# Clear cache
flask editor clear-cache

# Verify deployment
python scripts/verify_deployment.py
```

3. **Rollback Procedure**
```bash
# Restore from backup
python scripts/restore_templates.py

# Clear cache
flask editor clear-cache
```

#### Troubleshooting Common Issues

**Issue: Template not loading**
- Check template path in database
- Verify file permissions
- Clear template cache

**Issue: Editor not accessible**
- Verify admin permissions
- Check authentication
- Review middleware configuration

**Issue: Changes not appearing**
- Clear browser cache
- Check template cache
- Verify deployment status

---

### Developer Guide

#### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Middleware    │    │   Backend       │
│   (GrapesJS)    │◄──►│   (Integration) │◄──►│   (Flask)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Cache Layer   │    │   Database      │
│   (Jinja2)      │    │   (Redis/Mem)   │    │   (SQLAlchemy)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Key Components:**
- **Template Parser**: Converts Jinja2 to GrapesJS format
- **Component System**: Manages editable components
- **Middleware Layer**: Handles template override and asset injection
- **Cache System**: Optimizes performance
- **Backup System**: Ensures data safety

#### API Documentation

**Template Management API**

```python
# Get all templates
GET /api/editor/templates
Response: {
    "success": true,
    "data": {
        "templates": [...]
    }
}

# Get specific template
GET /api/editor/template/<template_path>
Response: {
    "success": true,
    "data": {
        "template": {...}
    }
}

# Update template
PUT /api/editor/template/<template_path>
Body: {
    "grapesjs_content": "...",
    "css_overrides": "...",
    "js_modifications": "..."
}

# Create backup
POST /api/editor/template/<template_path>/backup
Response: {
    "success": true,
    "data": {
        "backup_id": "..."
    }
}
```

**Component API**

```python
# Get component library
GET /api/editor/components
Response: {
    "success": true,
    "data": {
        "components": [...]
    }
}

# Register custom component
POST /api/editor/components
Body: {
    "name": "custom-component",
    "definition": {...}
}
```

#### Custom Component Creation

1. **Define Component Structure**
```javascript
const CustomComponent = {
    model: {
        defaults: {
            tagName: 'div',
            attributes: { class: 'custom-component' },
            content: '<h3>Custom Title</h3><p>Custom content</p>',
            traits: [
                {
                    type: 'text',
                    name: 'title',
                    label: 'Title',
                    default: 'Custom Title'
                }
            ]
        }
    },
    view: {
        onRender() {
            // Custom rendering logic
        }
    }
};
```

2. **Register Component**
```javascript
editor.DomComponents.addType('custom-component', CustomComponent);
```

3. **Add to Component Library**
```python
# In component registry
CUSTOM_COMPONENTS = {
    'custom-component': {
        'name': 'Custom Component',
        'category': 'Content',
        'icon': 'custom-icon',
        'description': 'A custom component for special content'
    }
}
```

#### Extension Development

**Creating Editor Extensions**

```python
class EditorExtension:
    def __init__(self, app):
        self.app = app
    
    def init_app(self, app):
        # Register routes
        app.register_blueprint(self.create_blueprint())
        
        # Register middleware
        self.register_middleware(app)
    
    def create_blueprint(self):
        bp = Blueprint('editor_extension', __name__)
        
        @bp.route('/extension/action')
        def extension_action():
            return jsonify({'success': True})
        
        return bp
```

#### Testing Procedures

**Unit Tests**
```bash
# Run editor tests
python -m pytest Tests/test_editor_system.py -v

# Run specific test category
python -m pytest Tests/test_editor_system.py::TestTemplateParsing -v
```

**Integration Tests**
```bash
# Test editor integration
python -m pytest Tests/test_editor_integration.py -v

# Test API endpoints
python -m pytest Tests/test_editor_api.py -v
```

**Performance Tests**
```bash
# Benchmark template parsing
python scripts/benchmark_editor.py

# Load testing
python scripts/load_test_editor.py
```

---

### Configuration Reference

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EDITOR_ENABLED` | `true` | Enable/disable editor system |
| `EDITOR_DEBUG` | `false` | Enable debug mode |
| `EDITOR_CACHE_TTL` | `3600` | Cache time-to-live (seconds) |
| `EDITOR_CDN_URL` | `None` | CDN URL for assets |
| `EDITOR_BACKUP_ENABLED` | `true` | Enable automatic backups |
| `EDITOR_AUDIT_LOGGING` | `true` | Enable audit logging |

#### Configuration Options

```python
# config/editor_config.py

# Editor Settings
EDITOR_SETTINGS = {
    'enabled': True,
    'debug': False,
    'cache_ttl': 3600,
    'cdn_url': None,
    'backup_enabled': True,
    'audit_logging': True
}

# Database Configuration
EDITOR_DATABASE = {
    'backup_retention_days': 30,
    'auto_backup': True,
    'backup_compression': True
}

# Security Settings
EDITOR_SECURITY = {
    'admin_only': True,
    'session_timeout': 3600,
    'max_file_size': 10485760,  # 10MB
    'allowed_extensions': ['.html', '.css', '.js']
}

# Performance Settings
EDITOR_PERFORMANCE = {
    'template_cache_size': 1000,
    'asset_cache_size': 500,
    'lazy_loading': True,
    'minification': True
}
```

#### Security Settings

```python
# Authentication
EDITOR_AUTH = {
    'require_admin': True,
    'session_timeout': 3600,
    'max_login_attempts': 5,
    'lockout_duration': 300
}

# File Upload Security
EDITOR_UPLOAD = {
    'max_file_size': 10485760,  # 10MB
    'allowed_extensions': ['.html', '.css', '.js', '.png', '.jpg'],
    'scan_for_viruses': True,
    'quarantine_suspicious': True
}
```

#### Performance Tuning

```python
# Cache Configuration
EDITOR_CACHE = {
    'template_cache_size': 1000,
    'asset_cache_size': 500,
    'cache_ttl': 3600,
    'cache_cleanup_interval': 300
}

# Asset Optimization
EDITOR_ASSETS = {
    'minification': True,
    'compression': True,
    'cdn_enabled': False,
    'lazy_loading': True
}
```

---

### API Reference

#### Template Management

**Get All Templates**
```http
GET /api/editor/templates
Authorization: Bearer <token>
```

**Response:**
```json
{
    "success": true,
    "data": {
        "templates": [
            {
                "id": 1,
                "template_path": "index.html",
                "template_name": "Home Page",
                "language": "en",
                "is_live": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
}
```

**Get Template**
```http
GET /api/editor/template/<template_path>
Authorization: Bearer <token>
```

**Update Template**
```http
PUT /api/editor/template/<template_path>
Authorization: Bearer <token>
Content-Type: application/json

{
    "grapesjs_content": "<div>Updated content</div>",
    "css_overrides": "body { background: red; }",
    "js_modifications": "console.log('Updated');"
}
```

#### Component Management

**Get Components**
```http
GET /api/editor/components
Authorization: Bearer <token>
```

**Create Component**
```http
POST /api/editor/components
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "custom-component",
    "definition": {
        "tagName": "div",
        "content": "<h3>Custom</h3>"
    }
}
```

#### Backup Management

**Create Backup**
```http
POST /api/editor/template/<template_path>/backup
Authorization: Bearer <token>
```

**Restore Backup**
```http
POST /api/editor/template/<template_path>/restore
Authorization: Bearer <token>
Content-Type: application/json

{
    "backup_id": "backup_123"
}
```

---

### Troubleshooting

#### Common Issues

**Template Not Loading**
```bash
# Check template path
flask editor list-templates

# Clear template cache
flask editor clear-cache

# Check file permissions
ls -la templates/
```

**Editor Not Accessible**
```bash
# Check authentication
flask editor check-auth

# Verify admin permissions
flask editor check-permissions

# Check middleware status
flask editor status
```

**Performance Issues**
```bash
# Monitor cache usage
flask editor cache-stats

# Clear all caches
flask editor clear-all-caches

# Check database performance
flask editor db-stats
```

#### Debug Mode

Enable debug mode for detailed logging:

```bash
export EDITOR_DEBUG=true
flask run
```

Check logs for detailed error information.

---

### FAQ

**Q: How do I enable the editor for non-admin users?**
A: Set `EDITOR_SECURITY['admin_only'] = False` in configuration.

**Q: Can I use the editor with existing templates?**
A: Yes, the editor automatically detects and can edit existing Jinja2 templates.

**Q: How do I backup templates before editing?**
A: Use `flask editor backup-template <template_path>` or enable automatic backups.

**Q: Can I customize the component library?**
A: Yes, you can add custom components through the API or configuration files.

**Q: How do I rollback changes?**
A: Use the backup system: `flask editor restore-template <template_path> <backup_id>`.

---

## Русский

### Содержание
1. [Руководство по установке](#руководство-по-установке)
2. [Руководство администратора](#руководство-администратора)
3. [Руководство разработчика](#руководство-разработчика)
4. [Справочник конфигурации](#справочник-конфигурации)
5. [Справочник API](#справочник-api)
6. [Устранение неполадок](#устранение-неполадок)
7. [Часто задаваемые вопросы](#часто-задаваемые-вопросы)

---

### Руководство по установке

#### Требования
- Python 3.8+
- Flask 2.0+
- SQLAlchemy 1.4+
- PostgreSQL/MySQL/SQLite
- Node.js 14+ (для компиляции ассетов)

#### Зависимости
```bash
pip install -r requirements.txt
# Дополнительные зависимости редактора
pip install grapesjs jinja2-to-grapesjs
```

#### Пошаговая установка

1. **Клонирование и настройка**
```bash
git clone <репозиторий>
cd flask-app
python -m venv venv
source venv/bin/activate  # В Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Миграция базы данных**
```bash
# Запуск скрипта миграции
python scripts/migrate_editor.py

# Или вручную
flask db upgrade
```

3. **Конфигурация**
```bash
# Копирование шаблона конфигурации
cp config/editor_config.example.py config/editor_config.py

# Редактирование конфигурации
nano config/editor_config.py
```

4. **Инициализация редактора**
```bash
# Запуск автоматической настройки
python utils/editor_installer.py

# Или вручную
flask editor init
```

5. **Запуск приложения**
```bash
flask run
# Доступ к редактору: http://localhost:5000/admin/content-editor
```

#### Начальная конфигурация

1. **Переменные окружения**
```bash
export EDITOR_ENABLED=true
export EDITOR_DEBUG=false
export EDITOR_CACHE_TTL=3600
export EDITOR_CDN_URL=https://cdn.example.com
```

2. **Конфигурация базы данных**
```python
# config/editor_config.py
EDITOR_DATABASE = {
    'backup_enabled': True,
    'backup_retention_days': 30,
    'auto_backup': True
}
```

3. **Настройки безопасности**
```python
EDITOR_SECURITY = {
    'admin_only': True,
    'audit_logging': True,
    'session_timeout': 3600
}
```

---

### Руководство администратора

#### Обзор интерфейса редактора

Расширенный редактор предоставляет визуальный интерфейс для редактирования Jinja2 шаблонов:

**Основные компоненты:**
- **Браузер шаблонов**: Навигация и выбор шаблонов
- **Визуальный редактор**: Интерфейс drag-and-drop на базе GrapesJS
- **Редактор кода**: Прямое редактирование Jinja2/HTML
- **Панель предпросмотра**: Предварительный просмотр изменений в реальном времени
- **Библиотека компонентов**: Готовые компоненты для общих элементов

#### Рабочий процесс редактирования шаблонов

1. **Доступ к редактору**
   - Перейдите к `/admin/content-editor`
   - Войдите с учетными данными администратора
   - Выберите шаблон для редактирования

2. **Редактирование шаблона**
   - Используйте визуальный редактор для изменений макета
   - Переключитесь на редактор кода для логики Jinja2
   - Предварительно просматривайте изменения в реальном времени
   - Сохраните черновик или опубликуйте изменения

3. **Развертывание изменений**
   - Просмотрите изменения в предварительном просмотре
   - Протестируйте функциональность
   - Опубликуйте в рабочей среде
   - Отслеживайте проблемы

#### Использование библиотеки компонентов

**Доступные компоненты:**
- **Компоненты макета**: Контейнер, Строка, Колонка
- **Компоненты контента**: Текст, Изображение, Видео
- **Компоненты форм**: Поле ввода, Кнопка, Выбор
- **Компоненты навигации**: Меню, Хлебные крошки, Пагинация
- **Интерактивные компоненты**: Модальное окно, Аккордеон, Вкладки

**Добавление пользовательских компонентов:**
```javascript
// Регистрация пользовательского компонента
editor.DomComponents.addType('custom-component', {
    model: {
        defaults: {
            tagName: 'div',
            attributes: { class: 'custom-component' },
            content: '<h3>Пользовательский компонент</h3>'
        }
    }
});
```

#### Процедуры развертывания

1. **Контрольный список перед развертыванием**
   - [ ] Все изменения протестированы в предварительном просмотре
   - [ ] Созданы резервные копии базы данных
   - [ ] Кэш очищен
   - [ ] Оценено влияние на производительность

2. **Шаги развертывания**
```bash
# Резервное копирование текущих шаблонов
python scripts/backup_templates.py

# Развертывание изменений
python scripts/deploy_editor.py

# Очистка кэша
flask editor clear-cache

# Проверка развертывания
python scripts/verify_deployment.py
```

3. **Процедура отката**
```bash
# Восстановление из резервной копии
python scripts/restore_templates.py

# Очистка кэша
flask editor clear-cache
```

#### Устранение общих проблем

**Проблема: Шаблон не загружается**
- Проверьте путь к шаблону в базе данных
- Убедитесь в правах доступа к файлам
- Очистите кэш шаблонов

**Проблема: Редактор недоступен**
- Проверьте права администратора
- Проверьте аутентификацию
- Проверьте конфигурацию middleware

**Проблема: Изменения не отображаются**
- Очистите кэш браузера
- Проверьте кэш шаблонов
- Убедитесь в статусе развертывания

---

### Руководство разработчика

#### Обзор архитектуры

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Middleware    │    │   Backend       │
│   (GrapesJS)    │◄──►│   (Integration) │◄──►│   (Flask)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   Cache Layer   │    │   Database      │
│   (Jinja2)      │    │   (Redis/Mem)   │    │   (SQLAlchemy)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Ключевые компоненты:**
- **Парсер шаблонов**: Преобразует Jinja2 в формат GrapesJS
- **Система компонентов**: Управляет редактируемыми компонентами
- **Слой middleware**: Обрабатывает переопределение шаблонов и инъекцию ассетов
- **Система кэширования**: Оптимизирует производительность
- **Система резервного копирования**: Обеспечивает безопасность данных

#### Документация API

**API управления шаблонами**

```python
# Получить все шаблоны
GET /api/editor/templates
Ответ: {
    "success": true,
    "data": {
        "templates": [...]
    }
}

# Получить конкретный шаблон
GET /api/editor/template/<template_path>
Ответ: {
    "success": true,
    "data": {
        "template": {...}
    }
}

# Обновить шаблон
PUT /api/editor/template/<template_path>
Тело: {
    "grapesjs_content": "...",
    "css_overrides": "...",
    "js_modifications": "..."
}

# Создать резервную копию
POST /api/editor/template/<template_path>/backup
Ответ: {
    "success": true,
    "data": {
        "backup_id": "..."
    }
}
```

**API компонентов**

```python
# Получить библиотеку компонентов
GET /api/editor/components
Ответ: {
    "success": true,
    "data": {
        "components": [...]
    }
}

# Зарегистрировать пользовательский компонент
POST /api/editor/components
Тело: {
    "name": "custom-component",
    "definition": {...}
}
```

#### Создание пользовательских компонентов

1. **Определение структуры компонента**
```javascript
const CustomComponent = {
    model: {
        defaults: {
            tagName: 'div',
            attributes: { class: 'custom-component' },
            content: '<h3>Пользовательский заголовок</h3><p>Пользовательский контент</p>',
            traits: [
                {
                    type: 'text',
                    name: 'title',
                    label: 'Заголовок',
                    default: 'Пользовательский заголовок'
                }
            ]
        }
    },
    view: {
        onRender() {
            // Пользовательская логика рендеринга
        }
    }
};
```

2. **Регистрация компонента**
```javascript
editor.DomComponents.addType('custom-component', CustomComponent);
```

3. **Добавление в библиотеку компонентов**
```python
# В реестре компонентов
CUSTOM_COMPONENTS = {
    'custom-component': {
        'name': 'Пользовательский компонент',
        'category': 'Контент',
        'icon': 'custom-icon',
        'description': 'Пользовательский компонент для специального контента'
    }
}
```

#### Разработка расширений

**Создание расширений редактора**

```python
class EditorExtension:
    def __init__(self, app):
        self.app = app
    
    def init_app(self, app):
        # Регистрация маршрутов
        app.register_blueprint(self.create_blueprint())
        
        # Регистрация middleware
        self.register_middleware(app)
    
    def create_blueprint(self):
        bp = Blueprint('editor_extension', __name__)
        
        @bp.route('/extension/action')
        def extension_action():
            return jsonify({'success': True})
        
        return bp
```

#### Процедуры тестирования

**Модульные тесты**
```bash
# Запуск тестов редактора
python -m pytest Tests/test_editor_system.py -v

# Запуск конкретной категории тестов
python -m pytest Tests/test_editor_system.py::TestTemplateParsing -v
```

**Интеграционные тесты**
```bash
# Тестирование интеграции редактора
python -m pytest Tests/test_editor_integration.py -v

# Тестирование API endpoints
python -m pytest Tests/test_editor_api.py -v
```

**Тесты производительности**
```bash
# Бенчмарк парсинга шаблонов
python scripts/benchmark_editor.py

# Нагрузочное тестирование
python scripts/load_test_editor.py
```

---

### Справочник конфигурации

#### Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `EDITOR_ENABLED` | `true` | Включить/выключить систему редактора |
| `EDITOR_DEBUG` | `false` | Включить режим отладки |
| `EDITOR_CACHE_TTL` | `3600` | Время жизни кэша (секунды) |
| `EDITOR_CDN_URL` | `None` | URL CDN для ассетов |
| `EDITOR_BACKUP_ENABLED` | `true` | Включить автоматическое резервное копирование |
| `EDITOR_AUDIT_LOGGING` | `true` | Включить аудит логирование |

#### Опции конфигурации

```python
# config/editor_config.py

# Настройки редактора
EDITOR_SETTINGS = {
    'enabled': True,
    'debug': False,
    'cache_ttl': 3600,
    'cdn_url': None,
    'backup_enabled': True,
    'audit_logging': True
}

# Конфигурация базы данных
EDITOR_DATABASE = {
    'backup_retention_days': 30,
    'auto_backup': True,
    'backup_compression': True
}

# Настройки безопасности
EDITOR_SECURITY = {
    'admin_only': True,
    'session_timeout': 3600,
    'max_file_size': 10485760,  # 10MB
    'allowed_extensions': ['.html', '.css', '.js']
}

# Настройки производительности
EDITOR_PERFORMANCE = {
    'template_cache_size': 1000,
    'asset_cache_size': 500,
    'lazy_loading': True,
    'minification': True
}
```

#### Настройки безопасности

```python
# Аутентификация
EDITOR_AUTH = {
    'require_admin': True,
    'session_timeout': 3600,
    'max_login_attempts': 5,
    'lockout_duration': 300
}

# Безопасность загрузки файлов
EDITOR_UPLOAD = {
    'max_file_size': 10485760,  # 10MB
    'allowed_extensions': ['.html', '.css', '.js', '.png', '.jpg'],
    'scan_for_viruses': True,
    'quarantine_suspicious': True
}
```

#### Настройка производительности

```python
# Конфигурация кэша
EDITOR_CACHE = {
    'template_cache_size': 1000,
    'asset_cache_size': 500,
    'cache_ttl': 3600,
    'cache_cleanup_interval': 300
}

# Оптимизация ассетов
EDITOR_ASSETS = {
    'minification': True,
    'compression': True,
    'cdn_enabled': False,
    'lazy_loading': True
}
```

---

### Справочник API

#### Управление шаблонами

**Получить все шаблоны**
```http
GET /api/editor/templates
Authorization: Bearer <token>
```

**Ответ:**
```json
{
    "success": true,
    "data": {
        "templates": [
            {
                "id": 1,
                "template_path": "index.html",
                "template_name": "Главная страница",
                "language": "ru",
                "is_live": true,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
}
```

**Получить шаблон**
```http
GET /api/editor/template/<template_path>
Authorization: Bearer <token>
```

**Обновить шаблон**
```http
PUT /api/editor/template/<template_path>
Authorization: Bearer <token>
Content-Type: application/json

{
    "grapesjs_content": "<div>Обновленный контент</div>",
    "css_overrides": "body { background: red; }",
    "js_modifications": "console.log('Обновлено');"
}
```

#### Управление компонентами

**Получить компоненты**
```http
GET /api/editor/components
Authorization: Bearer <token>
```

**Создать компонент**
```http
POST /api/editor/components
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "custom-component",
    "definition": {
        "tagName": "div",
        "content": "<h3>Пользовательский</h3>"
    }
}
```

#### Управление резервными копиями

**Создать резервную копию**
```http
POST /api/editor/template/<template_path>/backup
Authorization: Bearer <token>
```

**Восстановить резервную копию**
```http
POST /api/editor/template/<template_path>/restore
Authorization: Bearer <token>
Content-Type: application/json

{
    "backup_id": "backup_123"
}
```

---

### Устранение неполадок

#### Общие проблемы

**Шаблон не загружается**
```bash
# Проверить путь к шаблону
flask editor list-templates

# Очистить кэш шаблонов
flask editor clear-cache

# Проверить права доступа к файлам
ls -la templates/
```

**Редактор недоступен**
```bash
# Проверить аутентификацию
flask editor check-auth

# Проверить права администратора
flask editor check-permissions

# Проверить статус middleware
flask editor status
```

**Проблемы производительности**
```bash
# Мониторинг использования кэша
flask editor cache-stats

# Очистить все кэши
flask editor clear-all-caches

# Проверить производительность базы данных
flask editor db-stats
```

#### Режим отладки

Включите режим отладки для подробного логирования:

```bash
export EDITOR_DEBUG=true
flask run
```

Проверьте логи для получения подробной информации об ошибках.

---

### Часто задаваемые вопросы

**В: Как включить редактор для пользователей, не являющихся администраторами?**
О: Установите `EDITOR_SECURITY['admin_only'] = False` в конфигурации.

**В: Могу ли я использовать редактор с существующими шаблонами?**
О: Да, редактор автоматически обнаруживает и может редактировать существующие Jinja2 шаблоны.

**В: Как создать резервную копию шаблонов перед редактированием?**
О: Используйте `flask editor backup-template <template_path>` или включите автоматическое резервное копирование.

**В: Могу ли я настроить библиотеку компонентов?**
О: Да, вы можете добавлять пользовательские компоненты через API или файлы конфигурации.

**В: Как откатить изменения?**
О: Используйте систему резервного копирования: `flask editor restore-template <template_path> <backup_id>`. 