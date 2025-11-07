# Migration Instructions for English Reading Models

## Выполнение миграций

### Шаг 1: Создание миграции

```bash
flask db migrate -m "add english reading models"
```

Это создаст файл миграции в `migrations/versions/` с префиксом даты.

### Шаг 2: Проверка миграции (опционально)

Проверьте созданный файл миграции:

```bash
# Найдите последний файл миграции
ls -lt migrations/versions/ | head -1

# Откройте файл и убедитесь, что все таблицы создаются правильно
```

### Шаг 3: Применение миграции

```bash
flask db upgrade
```

### Шаг 4: Проверка создания таблиц

```python
from app import app, db
from models import EnglishPassage, EnglishQuestion, UserEnglishProgress

with app.app_context():
    # Проверка таблиц
    print("Tables created:")
    print(f"EnglishPassage: {db.inspect(EnglishPassage).table}")
    print(f"EnglishQuestion: {db.inspect(EnglishQuestion).table}")
    print(f"UserEnglishProgress: {db.inspect(UserEnglishProgress).table}")
```

## Откат миграции (если нужно)

```bash
flask db downgrade
```

## Проверка после миграции

```python
from app import app, db
from models import EnglishPassage, EnglishQuestion, UserEnglishProgress

with app.app_context():
    # Проверка наличия таблиц
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    required_tables = ['english_passages', 'english_questions', 'user_english_progress']
    for table in required_tables:
        if table in tables:
            print(f"✅ {table} exists")
        else:
            print(f"❌ {table} missing")
```


