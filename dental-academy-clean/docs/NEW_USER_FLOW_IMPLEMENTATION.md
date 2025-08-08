# Новый Flow для Пользователей - Реализация

## Обзор изменений

Реализован новый flow для новых пользователей, который направляет их на диагностику перед доступом к основному функционалу.

## Изменения в коде

### 1. Модель User (`models.py`)

Добавлено новое поле:
```python
# Learning flow control
requires_diagnostic = db.Column(db.Boolean, default=True)  # Flag to redirect new users to diagnostic
```

### 2. DigiD аутентификация (`routes/digid_routes.py`)

**Изменения в функции `authenticate()`:**
- Добавлена проверка флага `requires_diagnostic`
- Новые пользователи перенаправляются на `/big-diagnostic/choose-type`
- Пользователи с диагностикой идут на карту обучения

**Изменения в функции `complete_registration()`:**
- Добавлена проверка флага после завершения регистрации
- Новые пользователи перенаправляются на диагностику

### 3. Dashboard (`routes/dashboard_routes.py`)

**Изменения в функции `index()`:**
- Добавлена проверка флага `requires_diagnostic` в начале функции
- Пользователи без диагностики перенаправляются на диагностику с flash сообщением

### 4. Диагностика (`routes/diagnostic_routes.py`)

**Изменения в функции `show_results()`:**
- Добавлена проверка первой завершенной диагностики
- Автоматический сброс флага `requires_diagnostic = False`
- Автоматическое создание персонального плана обучения
- Редирект на dashboard с поздравлением

## Миграция базы данных

### 1. Создание миграции

Файл: `migrations/versions/add_requires_diagnostic_field.py`

```python
def upgrade():
    # Add requires_diagnostic field to user table
    op.add_column('user', sa.Column('requires_diagnostic', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    # Remove requires_diagnostic field from user table
    op.drop_column('user', 'requires_diagnostic')
```

### 2. Обновление существующих пользователей

Скрипт: `scripts/update_existing_users_diagnostic_flag.py`

```bash
python scripts/update_existing_users_diagnostic_flag.py
```

## Новый Flow пользователя

### Для новых пользователей:

1. **Регистрация через DigiD** → `/digid/login`
2. **Заполнение профиля** → `/digid/complete-registration`
3. **Проверка флага** → `requires_diagnostic = True`
4. **Редирект на диагностику** → `/big-diagnostic/choose-type`
5. **Прохождение диагностики** → Выбор типа и прохождение теста
6. **Завершение диагностики** → Автоматическое создание плана обучения
7. **Редирект на dashboard** → `/dashboard` с поздравлением

### Для существующих пользователей:

1. **Вход в систему** → Проверка флага `requires_diagnostic`
2. **Если нет диагностики** → Редирект на диагностику
3. **Если есть диагностика** → Доступ к dashboard

## Развертывание

### 1. Применение миграции

```bash
# В production
flask db upgrade

# Или через Python
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 2. Обновление существующих пользователей

```bash
python scripts/update_existing_users_diagnostic_flag.py
```

### 3. Проверка работы

1. Создать нового пользователя через DigiD
2. Проверить редирект на диагностику
3. Пройти диагностику
4. Проверить создание плана обучения
5. Проверить редирект на dashboard

## Тестирование

### Тестовые сценарии:

1. **Новый пользователь без диагностики:**
   - Регистрация → Редирект на диагностику ✅

2. **Существующий пользователь без диагностики:**
   - Вход в dashboard → Редирект на диагностику ✅

3. **Пользователь с диагностикой:**
   - Вход в dashboard → Доступ к dashboard ✅

4. **Завершение диагностики:**
   - Прохождение теста → Создание плана → Редирект на dashboard ✅

## Возможные проблемы

### 1. Циклические редиректы
- Проверка: убедиться, что флаг корректно сбрасывается
- Решение: добавить дополнительную проверку в роутах

### 2. Ошибки создания плана обучения
- Проверка: логи в `show_results()`
- Решение: обработка исключений в блоке try-catch

### 3. Проблемы с миграцией
- Проверка: совместимость с существующими данными
- Решение: backup базы данных перед миграцией

## Мониторинг

### Логи для отслеживания:

1. **Создание пользователей:**
   ```
   🔍 DEBUG: User requires diagnostic - redirecting to diagnostic
   ```

2. **Завершение диагностики:**
   ```
   🔍 ОТЛАДКА: Это первая завершенная диагностика пользователя
   🔍 ОТЛАДКА: Learning plan created: {plan_id}
   ```

3. **Ошибки:**
   ```
   ❌ Ошибка создания learning plan: {error}
   ```

## Откат изменений

### 1. Откат миграции

```bash
flask db downgrade
```

### 2. Откат кода

Вернуть предыдущие версии файлов:
- `models.py`
- `routes/digid_routes.py`
- `routes/dashboard_routes.py`
- `routes/diagnostic_routes.py`

---

**Статус**: ✅ Реализовано  
**Дата**: 2025-01-27  
**Версия**: 1.0 