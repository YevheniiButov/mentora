# 🔍 Диагностика проблем импорта вопросов

## Текущая ситуация
- ✅ Миграция применена успешно
- ❌ Импорт: 0 новых, 796 ошибок, 4 пропущено

## Шаг 1: Проверить структуру таблицы

```bash
psql $DATABASE_URL -c "\d questions"
```

Ожидаемые столбцы:
- `id`, `text`, `options`, `correct_answer_index`, `correct_answer_text`
- `explanation`, `category`, `domain`, `difficulty_level`
- `image_url`, `tags`, `big_domain_id`, `question_type`
- `clinical_context`, `learning_objectives`, `profession`
- `created_at`, `updated_at`

## Шаг 2: Посмотреть детали ошибок

На продакшене запустите обновленный скрипт:
```bash
git pull origin main
python3 scripts/import_questions_to_production.py
```

Теперь будут показаны первые 3 ошибки с полным traceback.

## Шаг 3: Возможные проблемы

### Проблема 1: Типы данных не совпадают
Если `options` или `tags` имеют другой тип в PostgreSQL.

**Решение**: Проверить тип столбца:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'questions' 
AND column_name IN ('options', 'tags', 'learning_objectives');
```

### Проблема 2: Отсутствует столбец profession
Хотя миграция должна была добавить его.

**Решение**: Применить миграцию вручную:
```bash
python3 apply_migration.py
```

### Проблема 3: Несоответствие JSON
PostgreSQL ожидает JSONB вместо JSON или наоборот.

**Решение**: Конвертировать данные:
```sql
-- Если ошибка "cannot cast type text to jsonb"
-- То изменить в скрипте:
json.dumps(q.get('options'))  # на:
json.dumps(q.get('options')) if q.get('options') else None
```

## Шаг 4: Быстрая диагностика

Выполните на продакшене:
```bash
# Проверить количество вопросов
psql $DATABASE_URL -c "SELECT COUNT(*) FROM questions;"

# Проверить структуру
psql $DATABASE_URL -c "\d questions" > questions_structure.txt

# Проверить один вопрос
psql $DATABASE_URL -c "SELECT * FROM questions LIMIT 1;"
```

Пришлите вывод команды `\d questions` для дальнейшей диагностики.
