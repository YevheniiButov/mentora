# 🚨 РУЧНОЕ ПРИМЕНЕНИЕ МИГРАЦИИ БД

## 📋 Проблема
На продакшене отсутствуют необходимые столбцы в БД, из-за чего сайт падает с ошибками.

## ✅ Решение 1: Через psql (самый простой)

### 1. Подключиться к серверу Render через SSH:

```bash
ssh render@srv-d24bk7ngi27c73de3v10-859df6fdbf-lxtrk
```

### 2. Получить строку подключения к БД:

В Render Dashboard:
1. Залогиньтесь на https://dashboard.render.com
2. Найдите сервис с PostgreSQL базой данных
3. Откройте настройки (Settings)
4. Найдите секцию "Connections" или "Database URL"
5. Скопируйте значение `DATABASE_URL` или "Internal Database URL"

Выглядит примерно так:
```
postgresql://user:password@host:port/database
```

### 3. Подключиться к БД:

```bash
# На сервере Render выполните:
psql $DATABASE_URL
```

Если `DATABASE_URL` не установлен, используйте прямую строку:
```bash
psql "postgresql://user:password@host:port/database"
```

### 4. Выполнить миграцию:

После подключения к psql выполните команды из файла `migrations/add_missing_columns.sql`:

```sql
-- Скопируйте и вставьте весь код из migrations/add_missing_columns.sql
-- Начните с:
BEGIN;
-- ... остальной код ...
COMMIT;
```

Или загрузите файл напрямую:
```sql
\i /path/to/migrations/add_missing_columns.sql
```

### 5. Проверить результат:

```sql
-- Проверить questions.profession
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'questions' 
AND column_name = 'profession';

-- Проверить personal_learning_plan
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'personal_learning_plan' 
AND column_name IN ('spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak', 'total_sr_reviews');
```

### 6. Выйти из psql:

```sql
\q
```

---

## ✅ Решение 2: Через Python скрипт

Создайте файл `apply_migration.py` на сервере:

```python
#!/usr/bin/env python3
import os
import psycopg2
from pathlib import Path

# Получить DATABASE_URL из переменных окружения
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL не установлен!")
    exit(1)

# Подключиться к БД
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Прочитать файл миграции
migration_file = Path('migrations/add_missing_columns.sql')
if not migration_file.exists():
    print(f"❌ Файл миграции не найден: {migration_file}")
    exit(1)

# Выполнить миграцию
print("🔧 Применяем миграцию...")
with open(migration_file, 'r') as f:
    cur.execute(f.read())

# Сохранить изменения
conn.commit()

print("✅ Миграция применена успешно!")

# Проверить результат
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'questions' 
    AND column_name = 'profession'
""")

result = cur.fetchone()
if result:
    print(f"✅ questions.profession существует: {result}")
else:
    print("❌ questions.profession не найден")

# Закрыть соединение
cur.close()
conn.close()
```

Запустить:
```bash
cd ~/project/src/dental-academy-clean
python3 apply_migration.py
```

---

## ✅ Решение 3: Через Flask команду

Создайте Flask команду в `app.py`:

```python
@app.cli.command('apply-db-migration')
def apply_db_migration():
    """Применить миграцию БД"""
    from sqlalchemy import text
    from pathlib import Path
    
    migration_file = Path('migrations/add_missing_columns.sql')
    
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return
    
    print("🔧 Применяем миграцию...")
    
    with open(migration_file, 'r') as f:
        sql = f.read()
    
    # Выполнить SQL
    with db.engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✅ Миграция применена успешно!")
```

Выполнить:
```bash
flask apply-db-migration
```

---

## ✅ Решение 4: Через любой SQL клиент

Если у вас есть доступ к БД через любой SQL клиент (DBeaver, pgAdmin, TablePlus и т.д.):

1. Подключитесь к базе данных
2. Скопируйте весь код из `migrations/add_missing_columns.sql`
3. Вставьте и выполните в SQL консоли

---

## 🔍 Где найти PostgreSQL в Render

Render обычно показывает два сервиса:
1. **Web Service** (ваше приложение)
2. **PostgreSQL** (отдельный сервис БД)

Чтобы найти PostgreSQL в Dashboard:
1. Откройте https://dashboard.render.com
2. В списке сервисов найдите тот, у которого тип "PostgreSQL"
3. Откройте его
4. На вкладке "Info" будут подключения к БД

---

## ⚠️ Если ничего не помогает

Свяжитесь с технической поддержкой Render или попробуйте:

1. Пересоздать переменные окружения
2. Проверить, что БД не заблокирована
3. Убедиться, что у вас есть права на изменение БД

---

**Дата создания**: 2025-10-26







