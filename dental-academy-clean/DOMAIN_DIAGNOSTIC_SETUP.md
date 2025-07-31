# Доменная диагностика BI-toets - Инструкция по настройке

## Обзор

Система доменной диагностики позволяет пользователям проходить адаптивное тестирование по конкретным областям стоматологии (доменам). Каждый домен имеет свой вес в экзамене BI-toets и содержит специализированные вопросы.

## Новые домены

Добавлены 8 новых доменов:

1. **EMERGENCY** (8%) - Неотложная помощь
2. **SYSTEMIC** (7%) - Системные заболевания  
3. **PHARMA** (6%) - Фармакология
4. **INFECTION** (5%) - Инфекционный контроль
5. **SPECIAL** (4%) - Специальные группы пациентов
6. **DIAGNOSIS** (6%) - Сложная диагностика
7. **DUTCH** (3%) - Голландская система здравоохранения
8. **PROFESSIONAL** (2%) - Профессиональное развитие

## Установка и настройка

### 1. Применение миграции базы данных

```bash
# Создать и применить миграцию
flask db upgrade
```

### 2. Импорт вопросов

```bash
# Импортировать вопросы из JSON файла
flask import-questions scripts/160_2.json

# Или выполнить сухой запуск для проверки
flask import-questions scripts/160_2.json --dry-run

# Импортировать все JSON файлы из директории
flask import-questions-batch scripts/ --pattern="*.json"
```

### 3. Проверка установки

```bash
# Запустить приложение
flask run

# Проверить доступность новых endpoints
curl http://localhost:5000/big-diagnostic/api/domains
```

## Структура файлов

### Backend

- `migrations/versions/add_new_big_domains_complete.py` - Миграция для новых доменов
- `utils/irt_engine.py` - Обновленный IRT движок с поддержкой доменов
- `routes/diagnostic_routes.py` - API endpoints для доменной диагностики
- `utils/question_importer.py` - Утилита для импорта вопросов

### Frontend

- `static/js/domain-diagnostic.js` - JavaScript для управления доменной диагностикой
- `static/css/domain-diagnostic.css` - Стили для интерфейса
- `templates/assessment/domain_diagnostic.html` - Шаблон страницы диагностики
- `templates/dashboard/domain_overview.html` - Шаблон обзора доменов

### Переводы

- `translations/domain_diagnostic_translations.py` - Переводы для доменной диагностики
- Обновлен `translations/__init__.py` для интеграции новых переводов

## API Endpoints

### Получение доменов

```
GET /big-diagnostic/api/domains
```

Ответ:
```json
{
  "success": true,
  "domains": [
    {
      "code": "EMERGENCY",
      "name": "Неотложная помощь",
      "description": "Критические ситуации, анафилаксия...",
      "weight": 8.0,
      "question_count": 45,
      "user_stats": {
        "sessions_completed": 2,
        "average_score": 75.5,
        "current_ability": 0.8,
        "questions_answered": 38
      }
    }
  ]
}
```

### Информация о домене

```
GET /big-diagnostic/api/domains/{domain_code}
```

### Запуск доменной диагностики

```
POST /big-diagnostic/api/domains/{domain_code}/start
```

### Страница доменной диагностики

```
GET /big-diagnostic/domain/{domain_code}
```

## Использование

### Для пользователей

1. Перейти на страницу `/big-diagnostic/`
2. Выбрать домен для диагностики
3. Ответить на адаптивные вопросы
4. Получить результаты и рекомендации

### Для администраторов

1. Импортировать новые вопросы:
   ```bash
   flask import-questions path/to/questions.json
   ```

2. Проверить статистику доменов:
   ```bash
   flask shell
   >>> from models import BIGDomain, Question
   >>> BIGDomain.query.all()
   >>> Question.query.filter_by(domain='EMERGENCY').count()
   ```

## Особенности реализации

### Адаптивное тестирование

- Использует IRT (Item Response Theory) для адаптивного выбора вопросов
- Вопросы подбираются на основе текущей оценки способности пользователя
- Тестирование завершается при достижении достаточной точности оценки

### Автоматическое назначение доменов

Утилита импорта автоматически назначает домены на основе:
- Ключевых слов в тексте вопроса
- Категории вопроса
- Тегов
- Объяснения

### Многоязычная поддержка

- Поддержка 3 языков: голландский, английский, русский
- Автоматическое переключение языков
- Плейсхолдеры для системы переводов

## Мониторинг и отладка

### Логирование

```python
import logging
logging.getLogger('utils.question_importer').setLevel(logging.DEBUG)
```

### Проверка состояния

```python
# Проверить домены
from models import BIGDomain
domains = BIGDomain.query.filter_by(is_active=True).all()

# Проверить вопросы
from models import Question
questions = Question.query.filter_by(domain='EMERGENCY').all()
```

## Возможные проблемы и решения

### Проблема: Миграция не применяется

**Решение:**
```bash
flask db current
flask db upgrade
```

### Проблема: Вопросы не импортируются

**Решение:**
```bash
# Проверить формат JSON
python -m json.tool scripts/160_2.json

# Выполнить сухой запуск
flask import-questions scripts/160_2.json --dry-run
```

### Проблема: Домены не отображаются

**Решение:**
```python
# Проверить активные домены
from models import BIGDomain
BIGDomain.query.filter_by(is_active=True).all()
```

## Тестирование

### Функциональное тестирование

1. Создать тестового пользователя
2. Пройти диагностику по каждому домену
3. Проверить корректность результатов
4. Проверить генерацию планов обучения

### Нагрузочное тестирование

```bash
# Тестирование API endpoints
ab -n 100 -c 10 http://localhost:5000/big-diagnostic/api/domains
```

## Обновления и поддержка

### Добавление новых доменов

1. Обновить миграцию
2. Добавить переводы
3. Обновить правила автоматического назначения
4. Протестировать

### Добавление новых вопросов

1. Подготовить JSON файл
2. Запустить импорт
3. Проверить назначение доменов
4. Протестировать в системе

## Контакты

При возникновении проблем обращайтесь к команде разработки или создавайте issue в репозитории проекта. 