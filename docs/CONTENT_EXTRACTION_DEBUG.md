# Отладка извлечения контента в редакторе

## 🚨 Проблема

**Симптомы:**
- ✅ Реальная страница: полный контент (заголовок, текст, кнопки, статистика)
- ❌ Редактор: только мобильный виджет, основной контент отсутствует

**Причина:** Агрессивная очистка Jinja2 удаляет основной контент вместе с шаблонными конструкциями.

## 🛠️ Решение

### Шаг 1: Обновленные методы парсинга

В `static/js/enhanced-file-loader.js` добавлены:

1. **`parseFullHTMLContent()`** - исправленный парсинг HTML с полным извлечением контента
2. **`lightCleanJinja()`** - легкая очистка Jinja2, заменяет только `url_for`, не удаляет контент
3. **`gentleCleanJinja()`** - мягкая очистка для body контента, превращает Jinja2 в комментарии
4. **`clearEditor()`** - улучшенная очистка редактора
5. **`loadHTMLComponents()`** - загрузка компонентов с отладкой и fallback методами
6. **`debugContentExtraction()`** - диагностика потери контента

### Шаг 2: Отладочные функции

В `static/js/debug-content-extraction.js` доступны функции для консоли браузера:

```javascript
// 1. Проверка оригинального HTML
await debugOriginalContent();

// 2. Проверка парсинга
const original = await debugOriginalContent();
debugParsing(original);

// 3. Полная отладка
await fullDebug();

// 4. Тест очистки Jinja2
testJinjaClean();

// 5. Принудительная загрузка полного контента
await forceLoadFullContent();

// 6. Проверка DOM парсинга
const html = await debugOriginalContent();
checkDOMParsing(html);

// 7. Анализ Jinja2 контента
analyzeJinjaContent(html);
```

## 🔍 Диагностика проблем

### Если контент все еще теряется:

1. **Откройте консоль браузера** (F12)
2. **Запустите полную отладку:**
   ```javascript
   await fullDebug();
   ```
3. **Проверьте результаты:**
   - Если `contentLost: true` - контент теряется при парсинге
   - Если `contentLost: false` - контент сохраняется

### Принудительная загрузка:

Если основной контент все еще не отображается:

```javascript
await forceLoadFullContent();
```

Эта функция:
- Загружает оригинальный HTML
- Применяет минимальную очистку (только `url_for`)
- Загружает контент в редактор напрямую

## 📊 Ожидаемые результаты

После исправлений в редакторе должен отображаться **полный контент:**

✅ Заголовок "Uw succesvolle pad naar de tandartslicentie"  
✅ Описание "Modern educatieplatform voor BIG-examenvoorbereiding"  
✅ Кнопки "Start gratis" и "Meer leren"  
✅ Статистика внизу (BIG, 8, 24/7)  
✅ Мобильный виджет справа  

## 🔧 Технические детали

### Ключевые улучшения:

1. **Мягкая очистка Jinja2:**
   - `{{ title or "текст" }}` → `<span data-jinja="title or 'текст'">Content</span>`
   - `{% if condition %}` → `<!-- IF: condition -->`
   - `{{ url_for('static', filename='file.css') }}` → `/static/file.css`

2. **Fallback методы:**
   - Если DOM парсинг не работает → regex извлечение body
   - Если gentle очистка не работает → light очистка
   - Если все не работает → emergency fallback

3. **Отладка на каждом этапе:**
   - Логирование длины контента
   - Проверка наличия ключевых элементов
   - Диагностика потери контента

### Проверка успешности:

```javascript
// В консоли браузера должны быть логи:
// ✅ HTML parsing completed: { bodyLength: >0, ... }
// ✅ HTML components loaded successfully
// ✅ Loaded components count: >0
// ✅ Has main title: true
// ✅ Has mobile widget: true
```

## 🚀 Быстрый тест

1. Откройте редактор контента
2. Откройте консоль браузера (F12)
3. Запустите: `await fullDebug()`
4. Проверьте результаты
5. Если контент теряется: `await forceLoadFullContent()`

## 📝 Логирование

Все этапы парсинга логируются в консоль:

- 🔧 Parsing HTML content (full version)
- 🔍 Original body content length
- 🔍 Cleaned body content length
- ✅ HTML parsing completed
- 📊 Content to load (с проверкой ключевых элементов)
- ✅ HTML components loaded successfully

Следите за этими логами для диагностики проблем. 