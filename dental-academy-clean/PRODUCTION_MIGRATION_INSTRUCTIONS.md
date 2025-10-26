# 🚨 СРОЧНАЯ МИГРАЦИЯ БД НА ПРОДАКШЕНЕ

## 📋 Проблема

На продакшене отсутствуют критически важные столбцы:
- `questions.profession` - для фильтрации вопросов по профессиям
- `personal_learning_plan.spaced_repetition_enabled` - для spaced repetition
- `personal_learning_plan.sr_algorithm` - алгоритм spaced repetition
- `personal_learning_plan.next_review_date` - дата следующего повторения
- `personal_learning_plan.sr_streak` - серия повторений
- `personal_learning_plan.total_sr_reviews` - всего повторений

**Результат**: Сайт падает с ошибками `UndefinedColumn`.

## ✅ Решение

### Шаг 1: Подключиться к продакшн серверу

```bash
# Подключиться к Render серверу через SSH
ssh render@srv-d24bk7ngi27c73de3v10-859df6fdbf-lxtrk
```

### Шаг 2: Скачать файл миграции

```bash
# На локальной машине - загрузить файл на сервер
scp migrations/add_missing_columns.sql render@srv-d24bk7ngi27c73de3v10-859df6fdbf-lxtrk:~/project/src/dental-academy-clean/
```

### Шаг 3: Применить миграцию

```bash
# На продакшн сервере
cd ~/project/src/dental-academy-clean

# Получить строку подключения к БД (из настроек Render)
# Затем применить миграцию:
psql $DATABASE_URL -f migrations/add_missing_columns.sql
```

**Или вручную через psql:**

```bash
# Подключиться к БД
psql $DATABASE_URL

# Выполнить SQL из файла
\i migrations/add_missing_columns.sql

# Выйти
\q
```

### Шаг 4: Проверить результат

```bash
# Подключиться к БД и проверить столбцы
psql $DATABASE_URL -c "
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'questions' 
AND column_name = 'profession';

SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'personal_learning_plan' 
AND column_name IN ('spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak', 'total_sr_reviews');
"
```

### Шаг 5: Перезапустить приложение

```bash
# На Render Dashboard перезапустить сервис:
# 1. Зайти в Dashboard
# 2. Выбрать сервис
# 3. Нажать "Manual Deploy" -> "Deploy latest commit"
```

## 🔍 Альтернативный способ (через Render Dashboard)

### 1. Открыть Render Dashboard
https://dashboard.render.com

### 2. Выбрать сервис с базой данных PostgreSQL

### 3. Перейти в раздел "PostgreSQL Shell"

### 4. Выполнить SQL миграцию

Скопировать содержимое файла `migrations/add_missing_columns.sql` и выполнить в Shell.

## 📊 Проверка после миграции

### 1. Проверить логи приложения

```bash
# В Render Dashboard → Logs
# Должны исчезнуть ошибки:
# - column questions.profession does not exist
# - column personal_learning_plan.spaced_repetition_enabled does not exist
```

### 2. Проверить работу сайта

1. Открыть https://bigmentor.nl
2. Зайти в "Learning Map"
3. Нажать "Quick Test" или "Big Diagnostic"
4. Убедиться, что вопросы загружаются без ошибок

## ⚠️ Откат миграции (если что-то пошло не так)

```sql
BEGIN;

-- Удалить добавленные столбцы
ALTER TABLE questions DROP COLUMN IF EXISTS profession;
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS spaced_repetition_enabled;
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS sr_algorithm;
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS next_review_date;
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS sr_streak;
ALTER TABLE personal_learning_plan DROP COLUMN IF EXISTS total_sr_reviews;

COMMIT;
```

## 📝 Примечания

- Миграция безопасна: она проверяет существование столбцов перед добавлением
- Существующие данные не затрагиваются
- Новые столбцы имеют значения по умолчанию (NULL или DEFAULT)
- Миграция может быть выполнена многократно (идемпотентна)

## 🆘 Контакты для поддержки

Если возникли проблемы:
1. Проверить логи Render
2. Проверить статус БД в Render Dashboard
3. Связаться с технической поддержкой

---

**Дата создания**: 2025-10-26  
**Автор**: AI Assistant  
**Статус**: Ready for Production
