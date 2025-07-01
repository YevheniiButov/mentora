# Deployment API - Система развертывания шаблонов

## Обзор

API развертывания шаблонов предоставляет безопасные эндпоинты для управления развертыванием шаблонов GrapesJS в продакшн с поддержкой резервного копирования, валидации и отката изменений.

## Возможности

- ✅ **Безопасное развертывание** с аутентификацией и авторизацией
- ✅ **Резервное копирование** перед каждым развертыванием
- ✅ **Валидация шаблонов** с проверкой синтаксиса и безопасности
- ✅ **Генерация предпросмотра** из контента GrapesJS
- ✅ **Откат изменений** к предыдущим версиям
- ✅ **История развертываний** с детальной информацией
- ✅ **Rate limiting** для защиты от злоупотреблений
- ✅ **CSRF защита** для всех POST запросов
- ✅ **Audit logging** всех операций
- ✅ **Интеграция с TemplateDeployer**

## Быстрый старт

### 1. Установка зависимостей

```bash
# Убедитесь, что все зависимости установлены
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создайте и примените миграции
flask db upgrade
```

### 3. Создание администратора

```bash
# Создайте администратора для доступа к API
flask create-admin
```

### 4. Запуск приложения

```bash
# Запустите Flask приложение
flask run
```

### 5. Тестирование API

```bash
# Запустите тестовый скрипт
python scripts/test_deployment_api.py
```

## Эндпоинты API

### Основные операции

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/deploy/backup` | Создание резервной копии |
| `POST` | `/api/deploy/preview` | Генерация предпросмотра |
| `POST` | `/api/deploy/validate` | Валидация шаблона |
| `POST` | `/api/deploy/deploy` | Развертывание шаблона |
| `POST` | `/api/deploy/rollback` | Откат изменений |
| `GET` | `/api/deploy/history/<path>` | История развертываний |
| `GET` | `/api/deploy/status/<id>` | Статус развертывания |
| `GET` | `/api/deploy/backups/<name>` | Список резервных копий |
| `GET` | `/api/deploy/health` | Проверка здоровья |

### Примеры использования

#### Создание резервной копии

```javascript
const response = await fetch('/api/deploy/backup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    template_path: 'templates/example.html',
    description: 'Backup before changes'
  })
});

const result = await response.json();
console.log('Backup created:', result.data.backup_id);
```

#### Развертывание шаблона

```javascript
const response = await fetch('/api/deploy/deploy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    content: jinja2Template,
    target_path: 'templates/example.html',
    description: 'Deploy from GrapesJS',
    require_backup: true,
    strict_validation: false
  })
});

const result = await response.json();
console.log('Deployment ID:', result.data.deployment_id);
```

#### Откат изменений

```javascript
const response = await fetch('/api/deploy/rollback', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    target_path: 'templates/example.html',
    backup_timestamp: '2024-01-15T10:30:00',
    confirmation: 'CONFIRM_ROLLBACK'
  })
});

const result = await response.json();
console.log('Rollback completed:', result.data.rollback_id);
```

## Интеграция с GrapesJS

### Конвертация GrapesJS в Jinja2

API автоматически конвертирует HTML контент GrapesJS в Jinja2 шаблоны:

```javascript
// GrapesJS контент
const grapesjsContent = `
<div class="container">
  <h1>{{ title }}</h1>
  <p>{{ description }}</p>
  <div class="component">
    <span>{{ component_text }}</span>
  </div>
</div>
`;

// Отправка на предпросмотр
const response = await fetch('/api/deploy/preview', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    content: grapesjsContent,
    template_name: 'preview_template'
  })
});

const result = await response.json();
console.log('Jinja2 template:', result.data.jinja2_content);
```

### Валидация шаблонов

API проверяет шаблоны на:

- Синтаксические ошибки Jinja2
- Потенциальные проблемы безопасности
- Совместимость с системой
- Отсутствующие файлы и зависимости

```javascript
const response = await fetch('/api/deploy/validate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify({
    content: jinja2Template,
    template_path: 'templates/example.html'
  })
});

const result = await response.json();
if (result.data.validation_passed) {
  console.log('Template is ready for deployment');
} else {
  console.log('Validation issues:', result.data.validation_issues);
}
```

## Безопасность

### Аутентификация

Все эндпоинты требуют аутентификации и прав администратора:

```javascript
// Проверка аутентификации
if (!isAuthenticated || !isAdmin) {
  throw new Error('Authentication required');
}
```

### CSRF защита

Все POST запросы требуют валидный CSRF токен:

```javascript
// Получение CSRF токена
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

// Использование в запросах
headers: {
  'X-CSRF-Token': csrfToken
}
```

### Rate Limiting

Ограничения на количество запросов:

- **Backup**: 10 запросов в 5 минут
- **Preview**: 20 запросов в 5 минут
- **Validate**: 30 запросов в 5 минут
- **Deploy**: 5 запросов в 10 минут
- **Rollback**: 3 запроса в 10 минут

### Audit Logging

Все операции логируются с информацией о:

- Пользователе
- IP адресе
- Времени выполнения
- Деталях операции
- Результате

## Мониторинг

### Health Check

Регулярно проверяйте состояние сервиса:

```bash
curl http://localhost:5000/api/deploy/health
```

### Логи

Проверяйте логи приложения:

```bash
# Flask логи
tail -f logs/app.log

# Audit логи
grep "DEPLOYMENT_AUDIT" logs/app.log
```

### Метрики

Отслеживайте ключевые метрики:

- Количество развертываний
- Количество резервных копий
- Время выполнения операций
- Количество ошибок

## Конфигурация

### Настройки TemplateDeployer

```python
from utils.template_deployer import DeploymentConfig

config = DeploymentConfig(
    backup_enabled=True,
    preview_enabled=True,
    validation_enabled=True,
    max_backups=10,
    backup_dir="backups/templates",
    preview_dir="previews",
    temp_dir="temp"
)
```

### Переменные окружения

```bash
# Настройки безопасности
FLASK_SECRET_KEY=your_secret_key
CSRF_SECRET_KEY=your_csrf_key

# Настройки логирования
LOG_LEVEL=INFO
AUDIT_LOG_ENABLED=true

# Настройки развертывания
MAX_BACKUPS=10
BACKUP_RETENTION_DAYS=30
```

## Устранение неполадок

### Частые проблемы

#### 1. Ошибка аутентификации

```
Error: AUTH_REQUIRED
```

**Решение**: Убедитесь, что пользователь аутентифицирован и имеет права администратора.

#### 2. Ошибка CSRF токена

```
Error: CSRF_INVALID
```

**Решение**: Проверьте, что CSRF токен передается в заголовке `X-CSRF-Token`.

#### 3. Превышение лимита запросов

```
Error: RATE_LIMIT_EXCEEDED
```

**Решение**: Подождите указанное время или увеличьте лимиты в конфигурации.

#### 4. Ошибка валидации шаблона

```
Error: VALIDATION_FAILED
```

**Решение**: Проверьте синтаксис Jinja2 и исправьте ошибки в шаблоне.

### Отладка

#### Включение отладочного режима

```python
# В app.py
app.config['DEBUG'] = True
app.config['LOG_LEVEL'] = 'DEBUG'
```

#### Проверка логов

```bash
# Просмотр всех логов развертывания
grep -i "deployment" logs/app.log

# Просмотр ошибок
grep -i "error" logs/app.log
```

## Разработка

### Добавление новых эндпоинтов

1. Создайте функцию в `routes/deployment_routes.py`
2. Добавьте декораторы для безопасности
3. Реализуйте логику обработки
4. Добавьте тесты
5. Обновите документацию

### Расширение функциональности

- Добавление новых типов валидации
- Поддержка дополнительных форматов
- Интеграция с внешними системами
- Расширенная аналитика

## Лицензия

Этот проект лицензирован под MIT License.

## Поддержка

Для получения поддержки:

1. Проверьте документацию
2. Посмотрите примеры в `scripts/`
3. Создайте issue в репозитории
4. Обратитесь к команде разработки 