# Template Deployer System для Dental Academy

## Обзор

Template Deployer - это комплексная система безопасного деплоя шаблонов для проекта Dental Academy. Система обеспечивает автоматическое резервное копирование, валидацию шаблонов и возможность отката изменений.

## Основные возможности

### 🔒 Безопасность
- Автоматическое создание резервных копий перед любыми изменениями
- Валидация синтаксиса Jinja2
- Проверка ссылок на CSS/JS файлы
- Валидация ключей переводов
- Проверка безопасности контента

### 📦 Резервное копирование
- Временные метки для всех бэкапов
- Метаданные с информацией о пользователе и изменениях
- Автоматическая очистка старых резервных копий
- Возможность восстановления из любой точки

### 🔍 Валидация
- Проверка синтаксиса Jinja2
- Валидация CSS/JS ссылок
- Проверка ключей переводов
- Валидация наследования шаблонов
- Проверка Bootstrap классов
- Анализ безопасности контента

## Архитектура

### Основные классы

#### TemplateDeployer
Основной класс для управления деплоем шаблонов.

```python
class TemplateDeployer:
    def __init__(self, app=None):
        self.app = app
        self.backup_dir = Path('backups/templates')
    
    def create_backup(self, template_path: str, user_id: int, notes: str = "") -> str
    def deploy_template(self, template_path: str, new_content: str, user_id: int, notes: str = "", force: bool = False) -> Dict[str, Any]
    def rollback_template(self, template_path: str, backup_id: str) -> bool
    def validate_template(self, content: str, template_path: str = "") -> ValidationResult
```

#### BackupMetadata
Метаданные резервной копии.

```python
@dataclass
class BackupMetadata:
    backup_id: str
    template_path: str
    original_size: int
    original_hash: str
    created_by: int
    created_at: datetime
    deployment_notes: str = ""
    validation_errors: List[str] = None
    deployment_status: str = "pending"
```

#### ValidationResult
Результат валидации шаблона.

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    template_info: Dict[str, Any]
```

## API Endpoints

### Деплой шаблона
```http
POST /api/content-editor/deploy
```

**Тело запроса:**
```json
{
  "template_path": "learning/subject_view.html",
  "force": false,
  "notes": "Updated navigation structure"
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Template deployed successfully",
  "backup_id": "subject_view_20250702_003000_123",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": ["Large template file: 2048 bytes"],
    "template_info": {
      "jinja2_valid": true,
      "css_references": ["test.css"],
      "js_references": ["test.js"],
      "translation_keys": ["Welcome"],
      "bootstrap_classes": ["container", "btn"]
    }
  },
  "deployed_at": "2025-07-02T00:30:00"
}
```

### Управление резервными копиями

#### Получение списка бэкапов
```http
GET /api/content-editor/backups?template_path=learning/subject_view.html&limit=10
```

**Ответ:**
```json
{
  "success": true,
  "backups": [
    {
      "backup_id": "subject_view_20250702_003000_123",
      "template_path": "learning/subject_view.html",
      "original_size": 1024,
      "original_hash": "abc123...",
      "created_by": 1,
      "created_at": "2025-07-02T00:30:00",
      "deployment_notes": "Updated navigation",
      "deployment_status": "success"
    }
  ],
  "total": 1
}
```

#### Получение содержимого бэкапа
```http
GET /api/content-editor/backups/{backup_id}
```

**Ответ:**
```json
{
  "success": true,
  "backup_id": "subject_view_20250702_003000_123",
  "content": "<!DOCTYPE html>..."
}
```

#### Восстановление из бэкапа
```http
POST /api/content-editor/backups/{backup_id}/restore
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
  "message": "Template restored successfully",
  "backup_id": "subject_view_20250702_003000_123",
  "template_path": "learning/subject_view.html"
}
```

#### Удаление бэкапа
```http
DELETE /api/content-editor/backups/{backup_id}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Backup deleted successfully",
  "backup_id": "subject_view_20250702_003000_123"
}
```

### Валидация шаблона
```http
POST /api/content-editor/validate
```

**Тело запроса:**
```json
{
  "content": "<!DOCTYPE html>...",
  "template_path": "learning/subject_view.html"
}
```

**Ответ:**
```json
{
  "success": true,
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": ["Undeclared variables: user_name"],
    "template_info": {
      "jinja2_valid": true,
      "css_references": ["main.css"],
      "js_references": ["app.js"],
      "translation_keys": ["Welcome", "Save"],
      "extends": ["base.html"],
      "content_blocks": ["content", "sidebar"],
      "bootstrap_classes": ["container", "btn-primary"],
      "file_size": 2048
    }
  }
}
```

### Статистика деплоев
```http
GET /api/content-editor/deployment-stats
```

**Ответ:**
```json
{
  "success": true,
  "stats": {
    "total_backups": 25,
    "successful_deployments": 20,
    "failed_deployments": 3,
    "rolled_back": 2,
    "total_size": 51200,
    "templates_modified": 8
  }
}
```

## Валидация шаблонов

### Проверки синтаксиса Jinja2
- Корректность синтаксиса
- Сбалансированность блоков
- Правильность наследования шаблонов

### Проверка файловых ссылок
- Существование CSS файлов
- Существование JS файлов
- Корректность путей

### Валидация переводов
- Проверка ключей переводов
- Соответствие формату `{{ _('key') }}`

### Проверка безопасности
- Отсутствие опасных паттернов
- Проверка на XSS уязвимости
- Валидация JavaScript кода

### Анализ структуры
- Проверка Bootstrap классов
- Валидация HTML структуры
- Анализ размера файла

## Управление резервными копиями

### Структура бэкапов
```
backups/
├── templates/
│   ├── metadata/
│   │   ├── template_20250702_003000_123.json
│   │   └── template_20250702_004000_456.json
│   └── files/
│       ├── template_20250702_003000_123.html
│       └── template_20250702_004000_456.html
```

### Метаданные бэкапа
```json
{
  "backup_id": "template_20250702_003000_123",
  "template_path": "learning/subject_view.html",
  "original_size": 1024,
  "original_hash": "abc123def456...",
  "created_by": 1,
  "created_at": "2025-07-02T00:30:00",
  "deployment_notes": "Updated navigation structure",
  "validation_errors": [],
  "deployment_status": "success"
}
```

### Очистка старых бэкапов
- Автоматическое удаление старых копий
- Сохранение последних 5 бэкапов по умолчанию
- Настраиваемое количество сохраняемых копий

## Интеграция с существующей системой

### Интеграция с API endpoints
```python
# В routes/content_editor.py
from utils.template_deployer import TemplateDeployer

template_deployer = TemplateDeployer()

@content_editor_bp.route('/api/content-editor/deploy', methods=['POST'])
def api_deploy_template(lang):
    # Использование TemplateDeployer для деплоя
    result = template_deployer.deploy_template(
        template_path=template_path,
        new_content=jinja2_content,
        user_id=current_user.id,
        notes=deployment_notes
    )
```

### Интеграция с GrapesJS
```javascript
// В frontend редакторе
async function deployTemplate() {
    const response = await fetch('/api/content-editor/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            template_path: currentTemplate,
            force: false,
            notes: 'Updated via GrapesJS editor'
        })
    });
    
    const result = await response.json();
    if (result.success) {
        showSuccess(`Template deployed! Backup: ${result.backup_id}`);
    } else {
        showError(`Deployment failed: ${result.error}`);
    }
}
```

## Использование

### Базовое использование
```python
from utils.template_deployer import TemplateDeployer

# Инициализация
deployer = TemplateDeployer()

# Валидация шаблона
validation = deployer.validate_template(content, 'test.html')
if not validation.is_valid:
    print(f"Validation errors: {validation.errors}")

# Деплой шаблона
result = deployer.deploy_template(
    template_path='test.html',
    new_content=content,
    user_id=1,
    notes='Updated template'
)

if result['success']:
    print(f"Deployed successfully! Backup: {result['backup_id']}")
else:
    print(f"Deployment failed: {result['error']}")
```

### Управление бэкапами
```python
# Получение списка бэкапов
backups = deployer.get_backup_list('test.html', limit=10)

# Восстановление из бэкапа
success = deployer.rollback_template('test.html', backup_id)

# Удаление бэкапа
success = deployer.delete_backup(backup_id)

# Получение статистики
stats = deployer.get_deployment_stats()
```

### Расширенная валидация
```python
# Детальная валидация
validation = deployer.validate_template(content, 'test.html')

print(f"Valid: {validation.is_valid}")
print(f"Errors: {validation.errors}")
print(f"Warnings: {validation.warnings}")
print(f"Template info: {validation.template_info}")
```

## Безопасность

### Валидация путей
- Проверка на path traversal атаки
- Ограничение доступа к файловой системе
- Валидация расширений файлов

### Проверка контента
- Анализ на XSS уязвимости
- Проверка JavaScript кода
- Валидация HTML структуры

### Права доступа
- Требуется авторизация администратора
- Логирование всех операций
- Проверка прав на редактирование

## Логирование

### Операции деплоя
```
INFO - Template deployed successfully: learning/subject_view.html (backup: subject_view_20250702_003000_123)
INFO - Backup created: subject_view_20250702_003000_123 for learning/subject_view.html
INFO - Template rolled back: learning/subject_view.html to subject_view_20250702_003000_123
```

### Ошибки валидации
```
ERROR - Template validation failed: Jinja2 syntax error at line 15
ERROR - CSS file not found: missing.css
WARNING - Undeclared variables: user_name, user_email
```

## Тестирование

### Запуск тестов
```bash
python scripts/test_template_deployer.py
```

### Тестовые сценарии
1. Валидация корректного шаблона
2. Валидация некорректного шаблона
3. Проверка отсутствующих файлов
4. Создание резервных копий
5. Деплой шаблонов
6. Восстановление из бэкапов
7. Управление бэкапами

## Производительность

### Оптимизации
- Кэширование результатов валидации
- Асинхронная обработка больших файлов
- Сжатие резервных копий
- Инкрементальные бэкапы

### Мониторинг
- Статистика деплоев
- Время выполнения операций
- Использование дискового пространства
- Частота ошибок

## Расширение функциональности

### Добавление новых проверок
1. Создать новую функцию валидации
2. Добавить в `validate_template()`
3. Обновить документацию
4. Добавить тесты

### Интеграция с CI/CD
1. Автоматическая валидация при коммитах
2. Проверка шаблонов в pipeline
3. Уведомления об ошибках
4. Автоматический откат при проблемах

### Поддержка новых форматов
1. Добавить парсер для нового формата
2. Обновить валидацию
3. Расширить метаданные
4. Добавить конвертеры

## Заключение

Template Deployer System обеспечивает безопасный и надежный деплой шаблонов для Dental Academy с полной интеграцией в существующую архитектуру. Система предоставляет:

- Автоматическое резервное копирование
- Комплексную валидацию шаблонов
- Возможность отката изменений
- Управление версиями
- Мониторинг и статистику

Система готова к использованию в продакшене и может быть расширена для поддержки новых требований проекта. 