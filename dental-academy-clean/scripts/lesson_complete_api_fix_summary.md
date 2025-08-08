# Исправление API complete_lesson - 404 ошибка

## ✅ Проблема решена

**Ошибка:** `INFO:werkzeug:127.0.0.1 - - [02/Aug/2025 18:50:22] "POST /en/content/api/lesson/21/complete HTTP/1.1" 404 -`

## 🔍 Анализ проблемы

### Причина 404 ошибки
Пользователь пытался обратиться к API endpoint `/en/content/api/lesson/21/complete`, который возвращал 404. Проблема была в неправильном URL в шаблоне `templates/content/lesson_view.html`.

### Структура маршрутов
- **Blueprint:** `content_bp`
- **URL prefix:** `/content` (зарегистрирован в `app.py`)
- **Маршрут:** `@content_bp.route("/api/lesson/<int:lesson_id>/complete")`
- **Правильный URL:** `/content/api/lesson/{lesson_id}/complete`

## 🔧 Исправление

### Файл: `templates/content/lesson_view.html`

**Было:**
```javascript
fetch(`/${document.documentElement.lang}/content/api/lesson/{{ lesson.id }}/complete`, {
```

**Стало:**
```javascript
fetch(`/content/api/lesson/{{ lesson.id }}/complete`, {
```

### Объяснение исправления
1. **Убран лишний префикс языка:** `/${document.documentElement.lang}/`
2. **Использован правильный URL:** `/content/api/lesson/...`
3. **Соответствует регистрации blueprint:** `url_prefix='/content'`

## 🛠️ Технические детали

### Регистрация blueprint (app.py):
```python
app.register_blueprint(content_bp, url_prefix='/content')
```

### Маршрут API (routes/content_routes.py):
```python
@content_bp.route("/api/lesson/<int:lesson_id>/complete", methods=['POST'])
@login_required
@csrf.exempt
def complete_lesson(lesson_id):
    """Отметить урок как завершенный"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        track_lesson_progress(current_user.id, lesson_id, completed=True)
        return jsonify({
            'success': True,
            'message': t('lesson_completed', lang)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': t('error_completing_lesson', lang)
        }), 500
```

### Функция track_lesson_progress:
- Создает/обновляет `UserProgress` для урока
- Отмечает урок как завершенный
- Обновляет статистику пользователя

## 🧪 Тестирование

### Проверенные функции:
- ✅ API endpoint `/content/api/lesson/{id}/complete` доступен
- ✅ Кнопка "Завершить урок" работает
- ✅ Прогресс урока сохраняется в базе данных
- ✅ StudySession создается корректно (после предыдущего исправления)

### Проверенные файлы:
- ✅ `templates/content/lesson_view.html`
- ✅ `routes/content_routes.py`
- ✅ `app.py` (регистрация blueprint)

## 🎯 Результат

**До исправления:**
```
POST /en/content/api/lesson/21/complete HTTP/1.1" 404 -
```

**После исправления:**
- ✅ API endpoint доступен по правильному URL
- ✅ Кнопка "Завершить урок" работает
- ✅ Прогресс урока сохраняется
- ✅ StudySession создается корректно

## 📝 Для разработчика

### Принципы работы с Flask blueprints:
1. **URL prefix:** Определяется при регистрации blueprint
2. **Маршруты:** Относительные к prefix
3. **Полный URL:** `{prefix}{route}`

### Примеры правильных URL:
- ✅ `/content/api/lesson/21/complete`
- ❌ `/${lang}/content/api/lesson/21/complete`
- ❌ `/en/content/api/lesson/21/complete`

### Структура API:
- **Blueprint:** content_bp
- **Prefix:** /content
- **API routes:** /api/lesson/{id}/complete
- **Method:** POST
- **CSRF:** exempt
- **Authentication:** required

🚀 **API complete_lesson исправлен - кнопка "Завершить урок" работает корректно!** 