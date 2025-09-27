# 🚀 Инструкции по применению миграции на продакшене

## ❌ Проблема
После добавления полей `is_deleted`, `deleted_at`, `deleted_by` в модель `ForumTopic` возникла ошибка:
```
column forum_topics.is_deleted does not exist
```

## ✅ Решение
Нужно применить миграцию на продакшн базе данных.

## 📋 Пошаговые инструкции

### 1. Подключение к продакшн серверу Render
```bash
# Подключитесь к серверу через SSH или используйте Render Dashboard
```

### 2. Переход в директорию проекта
```bash
cd ~/project/src/dental-academy-clean
```

### 3. Получение последних изменений
```bash
git pull origin main
```

### 4. Установка переменной окружения
```bash
export DATABASE_URL='postgresql://mentora_user:pWjbqoOgAAIGdLMNHfxPTiozhF7jG2LV@dpg-d3403vre5dus73ejhfjg-a.frankfurt-postgres.render.com/mentora'
```

### 5. Запуск миграции
```bash
python3 add_forum_topic_deletion_fields.py
```

### 6. Ожидаемый результат
```
🔧 ДОБАВЛЕНИЕ ПОЛЕЙ SOFT DELETE В FORUM_TOPICS
============================================================
✅ Подключение к базе данных установлено
📊 Существующие колонки: []
➕ Добавляем колонку is_deleted...
✅ Колонка is_deleted добавлена
➕ Добавляем колонку deleted_at...
✅ Колонка deleted_at добавлена
➕ Добавляем колонку deleted_by...
✅ Колонка deleted_by добавлена
🔍 Создаем индекс для is_deleted...
✅ Индекс создан

📋 Проверяем структуру таблицы forum_topics...
Структура таблицы forum_topics:
  - id: integer (nullable: NO, default: nextval('forum_topics_id_seq'::regclass))
  - title: character varying (nullable: NO, default: None)
  - content: text (nullable: NO, default: None)
  - category_id: integer (nullable: NO, default: None)
  - author_id: integer (nullable: NO, default: None)
  - status: character varying (nullable: YES, default: 'normal')
  - is_sticky: boolean (nullable: YES, default: false)
  - is_locked: boolean (nullable: YES, default: false)
  - is_deleted: boolean (nullable: YES, default: false)
  - deleted_at: timestamp with time zone (nullable: YES, default: None)
  - deleted_by: integer (nullable: YES, default: None)
  - views_count: integer (nullable: YES, default: 0)
  - replies_count: integer (nullable: YES, default: 0)
  - likes_count: integer (nullable: YES, default: 0)
  - created_at: timestamp without time zone (nullable: YES, default: None)
  - updated_at: timestamp without time zone (nullable: YES, default: None)
  - last_reply_at: timestamp without time zone (nullable: YES, default: None)
  - last_reply_by: integer (nullable: YES, default: None)

✅ Миграция успешно завершена!
🎉 Поля is_deleted, deleted_at, deleted_by добавлены в forum_topics
```

### 7. После успешной миграции
После успешного применения миграции нужно:

1. **Раскомментировать поля в модели** `models.py`:
```python
# Раскомментировать эти строки:
is_deleted = db.Column(db.Boolean, default=False)
deleted_at = db.Column(db.DateTime)
deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
deleted_by_user = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_topics')
```

2. **Обновить API endpoint** в `routes/main_routes.py`:
```python
# Заменить временное решение на:
topic.is_deleted = True
topic.deleted_at = datetime.now(timezone.utc)
topic.deleted_by = current_user.id
```

3. **Зафиксировать изменения**:
```bash
git add models.py routes/main_routes.py
git commit -m "Enable soft delete fields after successful migration"
git push origin main
```

## 🔍 Проверка
После применения миграции:
- ✅ Страница `/community` должна загружаться без ошибок
- ✅ API endpoints для редактирования/удаления должны работать
- ✅ Админские кнопки должны отображаться для администраторов

## ⚠️ Важно
- Миграция безопасна - не удаляет данные
- Добавляет только новые поля со значениями по умолчанию
- Создает индекс для оптимизации запросов
- Все существующие данные остаются нетронутыми
