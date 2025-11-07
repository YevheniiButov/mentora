# IELTS English Reading - Checklist Status

## ✅ Completed Tasks

- [x] **1. Add new models to models.py**
  - ✅ `EnglishPassage` - добавлена
  - ✅ `EnglishQuestion` - добавлена
  - ✅ `UserEnglishProgress` - добавлена
  - ✅ `get_english_band_estimate()` метод в User - добавлен

- [x] **2. Run migration: flask db migrate -m "add english reading"**
  - ⚠️ **Нужно выполнить вручную:**
  ```bash
  flask db migrate -m "add english reading models"
  ```

- [x] **3. Run upgrade: flask db upgrade**
  - ⚠️ **Нужно выполнить вручную:**
  ```bash
  flask db upgrade
  ```

- [x] **4. Create routes/english_reading.py**
  - ✅ Создан `routes/english_routes.py` (API endpoints)
  - ✅ Создан `routes/english_reading_routes.py` (page routes)

- [x] **5. Register blueprint in app.py**
  - ✅ `english_bp` зарегистрирован
  - ✅ `english_reading_bp` зарегистрирован

- [x] **6. Update get_daily_tasks() in routes/learning.py**
  - ✅ Функция обновлена для поддержки `english_reading`
  - ✅ Проверка `UserEnglishProgress` добавлена

- [x] **7. Create template templates/english_reading.html**
  - ✅ Создан шаблон
  - ✅ Наследуется от `base.html`
  - ✅ Подключен CSS файл

- [x] **8. Create static/js/english_reading.js**
  - ✅ Создан JavaScript файл
  - ✅ Поддержка всех типов вопросов
  - ✅ Интеграция с API

- [x] **9. Add CSS styles for english reading**
  - ✅ Создан `static/css/english-reading.css`
  - ✅ Стили встроены в шаблон (fallback)
  - ✅ Адаптивный дизайн

- [x] **10. Update learning_map.html to show daily tasks with rotation**
  - ✅ Обновлен `templates/learning/learning_map_modern_style.html`
  - ✅ Добавлен контейнер `dailyTasksContainer`
  - ✅ Добавлены функции `loadDailyTasks()` и `startTask()`
  - ✅ Добавлены стили для ротации задач

## ⚠️ Tasks to Complete

- [ ] **11. Generate 10 passages using prompts above**
  - 📝 Используйте `utils/ielts_generator.py` для создания промптов
  - 📝 Сгенерируйте тексты через ChatGPT/Claude
  - 📝 Сгенерируйте вопросы используя `generate_questions_prompt()`

- [ ] **12. Insert generated content into database**
  - 📝 Используйте `scripts/load_ielts_passage.py`
  - 📝 Или используйте `load_from_json()` для массовой загрузки
  - 📝 См. `scripts/IELTS_LOADING_GUIDE.md` для инструкций

- [ ] **13. Test rotation logic (check cycle_day calculation)**
  - 📝 Проверьте `/api/daily-tasks` endpoint
  - 📝 Убедитесь, что cycle_day правильно рассчитывается (1, 2, 3)
  - 📝 Проверьте, что задачи меняются в зависимости от дня цикла

- [ ] **14. Test English reading flow (passage → questions → results)**
  - 📝 Откройте `/english/practice`
  - 📝 Проверьте загрузку passage и questions
  - 📝 Отправьте ответы и проверьте результаты
  - 📝 Убедитесь, что XP начисляется

- [ ] **15. Verify XP calculation and daily task completion**
  - 📝 Проверьте начисление XP после завершения reading
  - 📝 Проверьте, что задача отмечается как completed в daily tasks
  - 📝 Проверьте обновление прогресса в `UserEnglishProgress`

## 📋 Migration Commands

```bash
# 1. Create migration
flask db migrate -m "add english reading models"

# 2. Review migration file (optional)
# Check migrations/versions/XXXXX_add_english_reading_models.py

# 3. Apply migration
flask db upgrade
```

## 🧪 Testing Checklist

### API Endpoints
- [ ] `GET /api/english/passage/<id>` - получить passage с вопросами
- [ ] `POST /api/english/submit` - отправить ответы
- [ ] `GET /api/daily-tasks` - получить ежедневные задачи

### Page Routes
- [ ] `/english/practice` - страница практики
- [ ] `/english/practice/<id>` - конкретный passage

### Database
- [ ] Проверить создание таблиц после миграции
- [ ] Проверить связь между моделями
- [ ] Проверить сохранение прогресса

### Frontend
- [ ] Загрузка passage и questions
- [ ] Отображение разных типов вопросов
- [ ] Отправка ответов
- [ ] Отображение результатов
- [ ] Начисление XP

## 📝 Next Steps

1. **Выполнить миграции:**
   ```bash
   flask db migrate -m "add english reading models"
   flask db upgrade
   ```

2. **Сгенерировать тестовые данные:**
   - Используйте промпты для генерации 10 passages
   - Загрузите их в БД используя скрипт

3. **Протестировать функциональность:**
   - Проверьте все endpoints
   - Проверьте ротацию задач
   - Проверьте начисление XP

4. **Добавить больше passages:**
   - Используйте разные темы
   - Разные уровни сложности (6.0, 7.0, 8.0)


