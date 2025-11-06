# Инструкция по деплою: Арабский язык и English Reading

## 📋 Что было добавлено

### 1. Арабский язык (Arabic)
- ✅ Файл переводов: `translations/ar.py` (2790+ ключей)
- ✅ Добавлен в систему переводов: `translations/__init__.py`
- ✅ Добавлен в меню языков: `templates/includes/_header.html`, `templates/learning/learning_map_modern_style.html`
- ✅ Добавлены переводы для страницы big-info: `templates/big_info/index.html`
- ✅ Исправлены жестко закодированные ссылки в `tandarts_eu.html`, `apotheker_eu.html`, `verpleegkundige_eu.html`

### 2. English Reading (IELTS Passages)
- ✅ Модели: `EnglishPassage`, `EnglishQuestion`, `UserEnglishProgress`
- ✅ Маршруты: `routes/english_routes.py` (API), `routes/english_reading_routes.py` (страницы)
- ✅ Шаблоны: `templates/english_reading.html`
- ✅ Статические файлы: `static/css/english-reading.css`, `static/js/english_reading.js`
- ✅ Изображения: `static/images/passages/` (10 изображений)
- ✅ Скрипт загрузки: `scripts/seed_english_passages.py`

### 3. Daily Assignments (Индивидуальный план)
- ✅ Модель: `DailyAssignment`
- ✅ Интеграция в `utils/individual_plan_helpers.py`

## 🗄️ Миграции базы данных

### Порядок применения миграций:

```bash
# 1. English Reading модели
flask db upgrade 66cd825725a2

# 2. Daily Assignments модель
flask db upgrade eadf0bc80aff

# 3. image_url для English Passages
flask db upgrade 1762253286
```

Или применить все новые миграции сразу:
```bash
flask db upgrade head
```

## 📦 Файлы для коммита

### Миграции:
- `migrations/versions/66cd825725a2_add_english_reading_models.py`
- `migrations/versions/eadf0bc80aff_add_daily_assignments_model.py`
- `migrations/versions/1762253286_add_image_url_to_english_passages.py`

### Роуты:
- `routes/english_routes.py`
- `routes/english_reading_routes.py`

### Шаблоны:
- `templates/english_reading.html`
- `templates/big_info/index.html` (арабские переводы)
- `templates/big_info/tandarts_eu.html` (исправления)
- `templates/big_info/apotheker_eu.html` (исправления)
- `templates/big_info/verpleegkundige_eu.html` (исправления)
- `templates/includes/_header.html` (арабский в меню)
- `templates/learning/learning_map_modern_style.html` (арабский в меню)

### Статические файлы:
- `static/css/english-reading.css`
- `static/js/english_reading.js`
- `static/images/passages/` (все 10 изображений)

### Переводы:
- `translations/ar.py` (новый файл)
- `translations/__init__.py` (добавлен арабский)

### Утилиты:
- `utils/individual_plan_helpers.py` (Daily Assignments)
- `scripts/seed_english_passages.py` (скрипт загрузки пассажей)

## 🚀 Скрипт для деплоя на продакшене

Создайте файл `scripts/deploy_arabic_english_reading.sh`:

```bash
#!/bin/bash
# Скрипт для деплоя арабского языка и English Reading на продакшене

set -e  # Остановка при ошибке

echo "🚀 Начинаем деплой арабского языка и English Reading..."

# 1. Применяем миграции
echo "📊 Применяем миграции базы данных..."
flask db upgrade head

# 2. Загружаем English Passages (если еще не загружены)
echo "📚 Проверяем наличие English Passages..."
python3 scripts/seed_english_passages.py

# 3. Проверяем, что все файлы на месте
echo "✅ Проверяем наличие файлов..."
if [ ! -f "translations/ar.py" ]; then
    echo "❌ ОШИБКА: translations/ar.py не найден!"
    exit 1
fi

if [ ! -d "static/images/passages" ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: static/images/passages не найден!"
fi

echo "✅ Деплой завершен успешно!"
```

## ⚠️ Важные замечания

1. **Миграции**: Убедитесь, что на продакшене применены все три миграции в правильном порядке
2. **Изображения**: Убедитесь, что папка `static/images/passages/` с изображениями загружена на сервер
3. **Переводы**: Файл `translations/ar.py` должен быть на сервере
4. **Зависимости**: Все зависимости уже в `requirements.txt`, дополнительных установок не требуется

## 🔍 Проверка после деплоя

1. Проверьте, что арабский язык отображается в меню: `/ar/learning-map`
2. Проверьте, что English Reading работает: `/english/practice`
3. Проверьте, что переводы работают на странице big-info: `/ar/big-info`
4. Проверьте, что кнопка "назад" сохраняет язык: `/uk/big-info/eu/tandarts` → назад → `/uk/big-info`

