# 🛡️ БЕЗОПАСНАЯ МИГРАЦИЯ ДЛЯ СУЩЕСТВУЮЩИХ ПОЛЬЗОВАТЕЛЕЙ

## ⚠️ ВАЖНО: Ваши пользователи будут в полной безопасности!

### 🎯 Что гарантирует эта миграция:

1. **НИ ОДИН пользователь не будет потерян**
2. **ВСЕ существующие данные останутся нетронутыми**
3. **Новые поля добавятся БЕЗОПАСНО**
4. **Полный план отката в случае проблем**

## 📋 Пошаговый план безопасной миграции

### Шаг 1: Создание бэкапа (ОБЯЗАТЕЛЬНО!)

```bash
# Установить переменные окружения
export DB_HOST="your_production_host"
export DB_USER="your_db_user"
export DB_PASSWORD="your_db_password"
export DB_NAME="your_db_name"

# Создать бэкап
./backup_users.sh
```

**Что создается:**
- `users_backup.sql` - полная копия таблицы пользователей
- `user_data.csv` - данные пользователей в CSV формате

### Шаг 2: Применение безопасной миграции

```bash
# Применить только безопасную миграцию
flask db upgrade safe_membership_fields
```

**Что происходит:**
1. Добавляются новые колонки (NULL разрешен)
2. Существующие пользователи получают `membership_type = 'free'`
3. Создается индекс для `member_id`
4. **НИ ОДИН пользователь не теряется!**

### Шаг 3: Проверка результатов

```bash
# Проверить, что все пользователи сохранены
python3 verify_migration.py
```

## 🔍 Что делает безопасная миграция

### SQL операции (безопасные):

```sql
-- 1. Добавить колонки (NULL разрешен - безопасно)
ALTER TABLE "user" ADD COLUMN membership_type VARCHAR(20);
ALTER TABLE "user" ADD COLUMN membership_expires TIMESTAMP;
ALTER TABLE "user" ADD COLUMN member_id VARCHAR(12);
ALTER TABLE "user" ADD COLUMN qr_code_path VARCHAR(200);

-- 2. Установить значения по умолчанию для существующих пользователей
UPDATE "user" SET membership_type = 'free' WHERE membership_type IS NULL;

-- 3. Сделать membership_type обязательным (после установки значений)
ALTER TABLE "user" ALTER COLUMN membership_type SET NOT NULL;

-- 4. Создать индекс (безопасная операция)
CREATE UNIQUE INDEX ix_user_member_id ON "user" (member_id);
```

### ✅ Гарантии безопасности:

1. **ADD COLUMN** - не влияет на существующие данные
2. **UPDATE** - только устанавливает значения по умолчанию
3. **CREATE INDEX** - не изменяет данные
4. **Никаких DROP, DELETE, TRUNCATE операций**

## 🛡️ План отката (если что-то пойдет не так)

### Быстрый откат:

```sql
-- Удалить новые колонки (данные пользователей останутся)
DROP INDEX IF EXISTS ix_user_member_id;
ALTER TABLE "user" DROP COLUMN IF EXISTS qr_code_path;
ALTER TABLE "user" DROP COLUMN IF EXISTS member_id;
ALTER TABLE "user" DROP COLUMN IF EXISTS membership_expires;
ALTER TABLE "user" DROP COLUMN IF EXISTS membership_type;

-- Отметить миграцию как невыполненную
DELETE FROM alembic_version WHERE version_num = 'safe_membership_fields';
```

### Полный откат из бэкапа:

```bash
# Восстановить из бэкапа
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backups/YYYYMMDD_HHMMSS/users_backup.sql
```

## 📊 Проверка после миграции

### Автоматическая проверка:

```bash
python3 verify_migration.py
```

**Проверяет:**
- Общее количество пользователей
- Количество пользователей с `membership_type`
- Все ли пользователи получили `membership_type = 'free'`
- Показывает примеры пользователей

### Ручная проверка:

```sql
-- Проверить общее количество
SELECT COUNT(*) FROM "user";

-- Проверить типы членства
SELECT membership_type, COUNT(*) 
FROM "user" 
GROUP BY membership_type;

-- Проверить примеры пользователей
SELECT id, email, username, membership_type 
FROM "user" 
LIMIT 10;
```

## 🚨 Что НЕ произойдет (гарантии):

- ❌ Ни один пользователь не будет удален
- ❌ Ни один email не будет изменен
- ❌ Ни один пароль не будет затронут
- ❌ Ни один профиль не будет поврежден
- ❌ Ни одна роль не будет изменена
- ❌ Ни один ID не будет изменен

## ✅ Что произойдет (безопасно):

- ✅ Добавятся 4 новые колонки
- ✅ Все пользователи получат `membership_type = 'free'`
- ✅ Создастся индекс для быстрого поиска
- ✅ Приложение продолжит работать как раньше
- ✅ Новые функции станут доступны

## 🔧 Настройка для продакшена

### Переменные окружения:

```bash
export DB_HOST="your_production_host"
export DB_USER="your_db_user" 
export DB_PASSWORD="your_db_password"
export DB_NAME="your_db_name"
export FLASK_APP="app.py"
```

### Проверка подключения:

```bash
# Проверить подключение к БД
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM \"user\";"
```

## 📞 Поддержка

### Если возникнут проблемы:

1. **Остановить приложение**
2. **Выполнить откат** (скрипт выше)
3. **Проверить логи** приложения
4. **Обратиться к команде разработки**

### Контакты для экстренных случаев:

- Техническая поддержка: [ваши контакты]
- База данных: [контакты DBA]
- Разработка: [контакты dev team]

## ✅ Финальный чеклист

- [ ] Создан бэкап пользователей
- [ ] Проверено подключение к БД
- [ ] Применена безопасная миграция
- [ ] Выполнена проверка результатов
- [ ] Протестирована функциональность
- [ ] Документированы изменения

## 🎯 Результат

После выполнения этой миграции:

1. **Все ваши пользователи останутся нетронутыми**
2. **Добавятся новые функции членства**
3. **Приложение будет работать как раньше + новые возможности**
4. **У вас будет полный бэкап для отката**

**Дата создания**: 2025-10-02  
**Статус**: Готово к безопасному развертыванию  
**Гарантия**: 100% сохранность существующих пользователей



