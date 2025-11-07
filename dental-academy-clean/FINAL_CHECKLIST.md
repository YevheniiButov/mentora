# IELTS English Reading - Final Checklist

## ✅ COMPLETED (10/15)

- [x] **1. Add new models to models.py** ✅
  - ✅ `EnglishPassage` - добавлена в `models.py`
  - ✅ `EnglishQuestion` - добавлена в `models.py`
  - ✅ `UserEnglishProgress` - добавлена в `models.py`
  - ✅ `get_english_band_estimate()` метод в User - добавлен
  - ✅ Relationship `english_progress` в User - добавлен

- [x] **4. Create routes/english_reading.py** ✅
  - ✅ `routes/english_routes.py` - API endpoints
  - ✅ `routes/english_reading_routes.py` - page routes
  - ✅ Endpoints: `/api/english/passage/<id>`, `/api/english/submit`
  - ✅ Page route: `/english/practice`

- [x] **5. Register blueprint in app.py** ✅
  - ✅ `english_bp` зарегистрирован (API)
  - ✅ `english_reading_bp` зарегистрирован (pages)

- [x] **6. Update get_daily_tasks() in routes/learning.py** ✅
  - ✅ Функция обновлена для поддержки `english_reading`
  - ✅ Проверка `UserEnglishProgress` добавлена
  - ✅ English Reading появляется в день 3 цикла

- [x] **7. Create template templates/english_reading.html** ✅
  - ✅ Создан шаблон, наследуется от `base.html`
  - ✅ Подключен CSS файл `english-reading.css`
  - ✅ Передача `passage_id` в JavaScript

- [x] **8. Create static/js/english_reading.js** ✅
  - ✅ Создан JavaScript файл
  - ✅ Поддержка всех типов вопросов
  - ✅ Интеграция с API endpoints

- [x] **9. Add CSS styles for english reading** ✅
  - ✅ Создан `static/css/english-reading.css`
  - ✅ Адаптивный дизайн

- [x] **10. Update learning_map.html to show daily tasks with rotation** ✅
  - ✅ Обновлен `templates/learning/learning_map_modern_style.html`
  - ✅ Добавлены функции `loadDailyTasks()` и `startTask()`

## ⚠️ TODO (5/15)

- [ ] **2. Run migration: flask db migrate -m "add english reading"**
  ```bash
  flask db migrate -m "add english reading models"
  ```
  📝 См. `MIGRATION_INSTRUCTIONS.md`

- [ ] **3. Run upgrade: flask db upgrade**
  ```bash
  flask db upgrade
  ```

- [ ] **11. Generate 10 passages using prompts above**
  - Используйте `utils/ielts_generator.py`
  - См. `scripts/IELTS_LOADING_GUIDE.md`

- [ ] **12. Insert generated content into database**
  - Используйте `scripts/load_ielts_passage.py`

- [ ] **13-15. Testing** (после миграции и загрузки данных)
  - Тестирование ротации
  - Тестирование flow
  - Проверка XP

## 📋 Quick Start Commands

```bash
# 1. Миграция
flask db migrate -m "add english reading models"
flask db upgrade

# 2. Генерация промпта для текста
python3 -c "from utils.ielts_generator import generate_ielts_prompt; print(generate_ielts_prompt('Ancient Architecture', 450, 7.0, 3))"

# 3. Генерация промпта для вопросов
python3 -c "from utils.ielts_generator import generate_questions_prompt; print(generate_questions_prompt('[текст passage]', 5, 3, 4))"

# 4. Загрузка passage в БД
python3 scripts/load_ielts_passage.py
```

## 📁 Created Files

✅ `models.py` - добавлены модели  
✅ `routes/english_routes.py` - API endpoints  
✅ `routes/english_reading_routes.py` - page routes  
✅ `templates/english_reading.html` - шаблон  
✅ `static/js/english_reading.js` - JavaScript  
✅ `static/css/english-reading.css` - стили  
✅ `utils/ielts_generator.py` - генераторы промптов  
✅ `utils/ielts_prompt_template.py` - шаблоны промптов  
✅ `scripts/load_ielts_passage.py` - скрипт загрузки  
✅ `scripts/IELTS_LOADING_GUIDE.md` - руководство  
✅ `MIGRATION_INSTRUCTIONS.md` - инструкции по миграции  

## 🎯 Status: 10/15 Complete (67%)

**Готово к миграции и тестированию!**


