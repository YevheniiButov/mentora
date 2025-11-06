# 🚀 Production Migration Instructions

## Проблема
На prodакшене отсутствуют колонки в таблице `personal_learning_plan`:
- `weak_categories` - JSON
- `strong_categories` - JSON
- `category_abilities` - JSON

Новые пользователи при завершении диагностики получают ошибку **500**.

## Решение
Запустить SQL скрипт миграции на production БД.

---

## ✅ Как запустить на Render

### Способ 1: Через Render Console (БЫСТРЫЙ)

1. Откройте Render Dashboard → PostgreSQL instance
2. Нажмите **"Connect"** → **"Render PostgreSQL Console"**
3. Скопируйте весь текст из `scripts/production_migration.sql`
4. Вставьте в консоль и нажмите **Enter**
5. Ждите сообщения об успехе ✅

### Способ 2: Через Render Shell (АВТОМАТИЧЕСКИЙ)

1. Откройте **Render Dashboard** → вашу Web Service
2. Нажмите **"Shell"** (вверху) для открытия терминала
3. Выполните команду:
```bash
bash scripts/run_migration_render.sh
```
4. Ждите сообщения `✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО`

### Способ 3: Через psql (если есть local psql)

```bash
# Подставьте свои данные:
psql postgresql://[user]:[password]@[host]:5432/[database] < scripts/production_migration.sql
```

Пример:
```bash
psql postgresql://user_12345:pass_xyz@postgres.render.com:5432/dental_db_prod < scripts/production_migration.sql
```

---

## 📋 Что делает скрипт

✅ Добавляет колонку `weak_categories` (JSON)
✅ Добавляет колонку `strong_categories` (JSON)
✅ Добавляет колонку `category_abilities` (JSON)
✅ Безопасно (не упадет, если колонки уже есть)
✅ Проверяет результаты миграции

---

## ⏱️ Время выполнения
**~5-10 секунд**

---

## ✔️ Проверка результата

После запуска в консоли должны увидеть:
```
✅ Столбец personal_learning_plan.weak_categories добавлен
✅ Столбец personal_learning_plan.strong_categories добавлен
✅ Столбец personal_learning_plan.category_abilities добавлен
...
✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО
```

---

## 🐛 Если ошибка

Если скрипт не работает:

1. Скопируйте только эту часть и запустите:
```sql
ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS weak_categories JSON;
ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS strong_categories JSON;
ALTER TABLE personal_learning_plan ADD COLUMN IF NOT EXISTS category_abilities JSON;
```

2. Проверьте, что колонки добавились:
```sql
\d personal_learning_plan
```

Должны увидеть строки:
```
 weak_categories       | json
 strong_categories     | json
 category_abilities    | json
```

---

## 📝 Дата
**27 October 2025**

## 🔧 Файлы
- `migrations/add_missing_columns.sql` - полная миграция
- `scripts/production_migration.sql` - копия для Render console
