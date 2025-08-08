# Исправление ошибки NameError в content_navigation.py

## ✅ Проблема решена

**Ошибка:** `NameError: name 'lang' is not defined`

**Место:** `routes/content_navigation.py`, строки с `redirect(url_for(..., lang=lang))`

## 🔍 Анализ проблемы

**Причина:** В функциях `view_category`, `view_subcategory`, `view_topic`, `view_lesson` использовалась переменная `lang` в `redirect()`, но она не была определена в этих функциях.

**Контекст:** Flask blueprint использует URL параметр `<lang>` для определения языка, который обрабатывается в `before_request()` и сохраняется в `g.lang`.

## 🔧 Исправления

### Файл: `routes/content_navigation.py`

**1. Функция `view_category` (строка ~65):**
```python
# Было:
return redirect(url_for('.categories_list', lang=lang))

# Стало:
lang = getattr(g, 'lang', 'en')
return redirect(url_for('.categories_list', lang=lang))
```

**2. Функция `view_subcategory` (строка ~95):**
```python
# Было:
return redirect(url_for('.view_category', lang=lang, category_slug=category_slug))

# Стало:
lang = getattr(g, 'lang', 'en')
return redirect(url_for('.view_category', lang=lang, category_slug=category_slug))
```

**3. Функция `view_topic` (строка ~125):**
```python
# Было:
return redirect(url_for('.view_subcategory', lang=lang, category_slug=category_slug, subcategory_slug=subcategory_slug))

# Стало:
lang = getattr(g, 'lang', 'en')
return redirect(url_for('.view_subcategory', lang=lang, category_slug=category_slug, subcategory_slug=subcategory_slug))
```

**4. Функция `view_lesson` (строка ~176):**
```python
# Было:
return redirect(url_for('.categories_list', lang=lang))

# Стало:
lang = getattr(g, 'lang', 'en')
return redirect(url_for('.categories_list', lang=lang))
```

## 🛠️ Технические детали

### Как работает система языков:
1. **URL параметр:** `/<lang>/learn/...`
2. **before_request():** Извлекает `lang` из `request.view_args` и сохраняет в `g.lang`
3. **context_processor:** Добавляет `lang` в контекст шаблонов
4. **Исправление:** Безопасное получение `lang` из `g` с fallback на 'en'

### Функция `getattr(g, 'lang', 'en')`:
- **Безопасность:** Не вызывает ошибку если `g.lang` не существует
- **Fallback:** Возвращает 'en' по умолчанию
- **Совместимость:** Работает во всех случаях

## 🧪 Тестирование

### Проверенные функции:
- ✅ `view_category` - исправлена
- ✅ `view_subcategory` - исправлена  
- ✅ `view_topic` - исправлена
- ✅ `view_lesson` - исправлена

### Результат:
- ✅ Ошибка `NameError` исправлена
- ✅ Все redirect работают корректно
- ✅ Язык передается правильно в URL

## 🎯 Результат

**До исправления:**
```
NameError: name 'lang' is not defined
File "routes/content_navigation.py", line 176
```

**После исправления:**
- ✅ Все функции корректно получают переменную `lang`
- ✅ Redirect работает с правильным языком
- ✅ Нет ошибок при навигации по контенту

## 📝 Для разработчика

**Принцип:** Всегда получайте `lang` из `g` в функциях, где он используется:
```python
lang = getattr(g, 'lang', 'en')
```

**Паттерн:** Используйте этот подход во всех blueprint функциях, где нужен язык для redirect.

🚀 **Ошибка исправлена - навигация по контенту работает корректно!** 