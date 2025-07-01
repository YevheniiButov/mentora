# Deployment API Documentation
# Документация API развертывания

## Обзор / Overview

API развертывания шаблонов предоставляет безопасные эндпоинты для управления развертыванием шаблонов GrapesJS в продакшн с поддержкой резервного копирования, валидации и отката изменений.

The Deployment API provides secure endpoints for managing GrapesJS template deployment to production with backup, validation, and rollback support.

## Аутентификация / Authentication

Все эндпоинты требуют аутентификации и прав администратора.

All endpoints require authentication and admin privileges.

```bash
# Headers для запросов
X-CSRF-Token: your_csrf_token
Authorization: Bearer your_session_token
```

## Эндпоинты / Endpoints

### 1. Создание резервной копии / Create Backup

**POST** `/api/deploy/backup`

Создает резервную копию текущего шаблона.

Creates a backup of the current template.

#### Параметры запроса / Request Parameters

```json
{
  "template_path": "templates/example.html",
  "description": "Manual backup before changes"
}
```

#### Ответ / Response

```json
{
  "success": true,
  "message": "Backup created successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "backup_id": "2024-01-15T10:30:00",
    "backup_metadata": {
      "timestamp": "2024-01-15T10:30:00",
      "user": "admin@example.com",
      "description": "Manual backup before changes",
      "template_path": "templates/example.html",
      "backup_hash": "abc123...",
      "file_size": 2048,
      "version": "1.0.0"
    }
  }
}
```

### 2. Генерация предпросмотра / Generate Preview

**POST** `/api/deploy/preview`

Генерирует предпросмотр из контента GrapesJS.

Generates a preview from GrapesJS content.

#### Параметры запроса / Request Parameters

```json
{
  "content": "GrapesJS HTML content...",
  "template_name": "preview_template"
}
```

#### Ответ / Response

```json
{
  "success": true,
  "message": "Preview generated successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "preview_url": "/previews/preview_template.html",
    "preview_path": "previews/preview_template.html",
    "template_name": "preview_template",
    "validation_issues": [],
    "validation_passed": true,
    "jinja2_content": "Converted Jinja2 template..."
  }
}
```

### 3. Валидация шаблона / Validate Template

**POST** `/api/deploy/validate`

Валидирует шаблон перед развертыванием.

Validates template before deployment.

#### Параметры запроса / Request Parameters

```json
{
  "content": "Jinja2 template content...",
  "template_path": "templates/example.html"
}
```

#### Ответ / Response

```json
{
  "success": true,
  "message": "Template validation completed",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "validation_issues": [],
    "validation_passed": true,
    "issues_count": 0,
    "additional_checks": {
      "syntax_valid": true,
      "security_valid": true,
      "compatibility_valid": true
    },
    "recommendations": ["Template is ready for deployment"]
  }
}
```

### 4. Развертывание шаблона / Deploy Template

**POST** `/api/deploy/deploy`

Развертывает шаблон в продакшн.

Deploys template to production.

#### Параметры запроса / Request Parameters

```json
{
  "content": "Jinja2 template content...",
  "target_path": "templates/example.html",
  "description": "API deployment",
  "require_backup": true,
  "strict_validation": false
}
```

#### Ответ / Response

```json
{
  "success": true,
  "message": "Template deployed successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "deployment_id": "2024-01-15T10:30:00",
    "target_path": "templates/example.html",
    "status": "success",
    "backup_metadata": {
      "timestamp": "2024-01-15T10:30:00",
      "user": "admin@example.com",
      "description": "Backup before deployment"
    },
    "validation_issues": [],
    "deployment_record": {
      "timestamp": "2024-01-15T10:30:00",
      "user": "admin@example.com",
      "description": "API deployment",
      "status": "success"
    }
  }
}
```

### 5. Откат изменений / Rollback

**POST** `/api/deploy/rollback`

Откатывает изменения к предыдущей резервной копии.

Rolls back changes to previous backup.

#### Параметры запроса / Request Parameters

```json
{
  "target_path": "templates/example.html",
  "backup_timestamp": "2024-01-15T10:30:00",
  "confirmation": "CONFIRM_ROLLBACK"
}
```

#### Ответ / Response

```json
{
  "success": true,
  "message": "Template rollback completed successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "rollback_id": "2024-01-15T10:35:00",
    "target_path": "templates/example.html",
    "status": "success",
    "restored_from": "2024-01-15T10:30:00",
    "metadata": {
      "backup_timestamp": "2024-01-15T10:30:00",
      "user": "admin@example.com"
    },
    "rollback_record": {
      "timestamp": "2024-01-15T10:35:00",
      "user": "admin@example.com",
      "status": "success"
    }
  }
}
```

### 6. История развертываний / Deployment History

**GET** `/api/deploy/history/<template_path>`

Получает историю развертываний для шаблона.

Gets deployment history for template.

#### Ответ / Response

```json
{
  "success": true,
  "message": "Deployment history retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "template_path": "templates/example.html",
    "deployment_history": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "user": "admin@example.com",
        "description": "API deployment",
        "status": "success"
      }
    ],
    "backups": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "user": "admin@example.com",
        "description": "Manual backup",
        "file_size": 2048
      }
    ],
    "total_deployments": 1,
    "total_backups": 1
  }
}
```

### 7. Статус развертывания / Deployment Status

**GET** `/api/deploy/status/<deployment_id>`

Проверяет статус развертывания.

Checks deployment status.

#### Ответ / Response

```json
{
  "success": true,
  "message": "Deployment status retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "deployment_id": "2024-01-15T10:30:00",
    "status": "success",
    "progress": 100,
    "timestamp": "2024-01-15T10:30:00",
    "user": "admin@example.com",
    "description": "API deployment",
    "target_path": "templates/example.html",
    "error": null,
    "backup_metadata": {
      "timestamp": "2024-01-15T10:30:00",
      "user": "admin@example.com"
    }
  }
}
```

### 8. Список резервных копий / Backup List

**GET** `/api/deploy/backups/<template_name>`

Получает список резервных копий для шаблона.

Gets list of backups for template.

#### Ответ / Response

```json
{
  "success": true,
  "message": "Backup list retrieved successfully",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "template_name": "example",
    "backups": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "user": "admin@example.com",
        "description": "Manual backup",
        "file_size": 2048,
        "backup_hash": "abc123..."
      }
    ],
    "total_backups": 1
  }
}
```

### 9. Проверка здоровья / Health Check

**GET** `/api/deploy/health`

Проверяет состояние сервиса развертывания.

Checks deployment service health.

#### Ответ / Response

```json
{
  "success": true,
  "message": "Deployment service is healthy",
  "timestamp": "2024-01-15T10:30:00",
  "data": {
    "status": "healthy",
    "deployer_available": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

## Коды ошибок / Error Codes

| Код / Code | Описание / Description |
|------------|----------------------|
| `AUTH_REQUIRED` | Требуется аутентификация / Authentication required |
| `ADMIN_REQUIRED` | Требуются права администратора / Admin privileges required |
| `CSRF_INVALID` | Недействительный CSRF токен / Invalid CSRF token |
| `RATE_LIMIT_EXCEEDED` | Превышен лимит запросов / Rate limit exceeded |
| `MISSING_TEMPLATE_PATH` | Отсутствует путь к шаблону / Template path missing |
| `MISSING_CONTENT` | Отсутствует контент / Content missing |
| `TEMPLATE_NOT_FOUND` | Шаблон не найден / Template not found |
| `BACKUP_FAILED` | Ошибка создания резервной копии / Backup creation failed |
| `CONVERSION_ERROR` | Ошибка конвертации / Conversion error |
| `VALIDATION_FAILED` | Ошибка валидации / Validation failed |
| `DEPLOYMENT_ERROR` | Ошибка развертывания / Deployment error |
| `ROLLBACK_ERROR` | Ошибка отката / Rollback error |
| `BACKUP_NOT_FOUND` | Резервная копия не найдена / Backup not found |

## Примеры использования / Usage Examples

### JavaScript / Frontend

```javascript
// Создание резервной копии
async function createBackup(templatePath, description) {
  const response = await fetch('/api/deploy/backup', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken()
    },
    body: JSON.stringify({
      template_path: templatePath,
      description: description
    })
  });
  
  return await response.json();
}

// Развертывание шаблона
async function deployTemplate(content, targetPath, description) {
  const response = await fetch('/api/deploy/deploy', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken()
    },
    body: JSON.stringify({
      content: content,
      target_path: targetPath,
      description: description,
      require_backup: true,
      strict_validation: false
    })
  });
  
  return await response.json();
}

// Откат изменений
async function rollbackTemplate(targetPath, backupTimestamp) {
  const response = await fetch('/api/deploy/rollback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken()
    },
    body: JSON.stringify({
      target_path: targetPath,
      backup_timestamp: backupTimestamp,
      confirmation: 'CONFIRM_ROLLBACK'
    })
  });
  
  return await response.json();
}
```

### Python / Backend

```python
import requests

# Создание резервной копии
def create_backup(session, template_path, description):
    response = session.post('/api/deploy/backup', json={
        'template_path': template_path,
        'description': description
    })
    return response.json()

# Развертывание шаблона
def deploy_template(session, content, target_path, description):
    response = session.post('/api/deploy/deploy', json={
        'content': content,
        'target_path': target_path,
        'description': description,
        'require_backup': True,
        'strict_validation': False
    })
    return response.json()

# Получение истории развертываний
def get_deployment_history(session, template_path):
    response = session.get(f'/api/deploy/history/{template_path}')
    return response.json()
```

## Безопасность / Security

### Rate Limiting

- **Backup**: 10 запросов в 5 минут / 10 requests per 5 minutes
- **Preview**: 20 запросов в 5 минут / 20 requests per 5 minutes
- **Validate**: 30 запросов в 5 минут / 30 requests per 5 minutes
- **Deploy**: 5 запросов в 10 минут / 5 requests per 10 minutes
- **Rollback**: 3 запроса в 10 минут / 3 requests per 10 minutes

### CSRF Protection

Все POST запросы требуют валидный CSRF токен.

All POST requests require a valid CSRF token.

### Audit Logging

Все операции логируются с информацией о пользователе, IP адресе и деталях операции.

All operations are logged with user information, IP address, and operation details.

## Интеграция с GrapesJS / GrapesJS Integration

API интегрируется с системой развертывания шаблонов и поддерживает:

The API integrates with the template deployment system and supports:

- Конвертацию GrapesJS в Jinja2 шаблоны / GrapesJS to Jinja2 conversion
- Валидацию шаблонов / Template validation
- Резервное копирование / Backup creation
- Развертывание в продакшн / Production deployment
- Откат изменений / Rollback functionality

## Мониторинг / Monitoring

### Health Check

Регулярно проверяйте состояние сервиса через `/api/deploy/health`.

Regularly check service health via `/api/deploy/health`.

### Логирование / Logging

Все операции логируются с уровнем INFO и выше.

All operations are logged with INFO level and above.

### Метрики / Metrics

- Количество развертываний / Deployment count
- Количество резервных копий / Backup count
- Время выполнения операций / Operation execution time
- Количество ошибок / Error count 