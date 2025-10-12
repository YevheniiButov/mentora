# ✅ SEO ГОТОВО - Что дальше?

## 🎉 Сделано прямо сейчас:

### 1. Мета-теги в base.html
- Title, description, keywords
- Open Graph для соцсетей
- Twitter Cards
- Canonical URLs
- Hreflang для мультиязычности
- Schema.org разметка

### 2. robots.txt
- Путь: `/static/robots.txt`
- URL: `https://yoursite.com/robots.txt`
- Закрывает админку и приватные разделы

### 3. Sitemap.xml
- Путь: `/sitemap.xml` (динамическая генерация)
- URL: `https://yoursite.com/sitemap.xml`

### 4. SEO роуты
- Blueprint зарегистрирован в app.py
- Работает автоматически

### 5. Пример (index.html)
- Все SEO блоки заполнены
- Готовый пример для копирования

## 🚀 Как проверить что работает:

1. **Запусти приложение:**
```bash
python app.py
```

2. **Открой в браузере:**
```
http://localhost:5000/robots.txt  - должен показать текст
http://localhost:5000/sitemap.xml - должен показать XML
http://localhost:5000/            - открой код страницы (Ctrl+U)
```

3. **В коде страницы ищи:**
```html
<meta name="description" content="...">
<meta property="og:title" content="...">
<script type="application/ld+json">
```

## ⚠️ ВАЖНО - что нужно сделать СРОЧНО:

### 1. Замени og-image на реальную картинку
Сейчас там SVG placeholder. Нужна PNG/JPG 1200x630px:
```
/static/images/og-image.png  <- создай эту картинку
```

Потом в base.html замени:
```html
filename='images/og-image.png'  вместо .svg
```

### 2. Обновь robots.txt
Замени `https://mentora.nl` на свой реальный домен

### 3. Для каждой новой страницы копируй из index.html:
```jinja
{% block title %}Твой заголовок{% endblock %}
{% block meta_description %}Твое описание{% endblock %}
{% block meta_keywords %}ключ1, ключ2{% endblock %}
```

## 📊 Проверка после деплоя:

1. **Google Search Console:**
   - Зарегистрируй сайт
   - Отправь sitemap.xml
   - Проверь индексацию

2. **Тестеры:**
   - https://search.google.com/test/rich-results
   - https://cards-dev.twitter.com/validator
   - https://developers.facebook.com/tools/debug/

3. **PageSpeed Insights:**
   - https://pagespeed.web.dev/

## 💡 Полезные команды:

```bash
# Проверить robots.txt локально
curl http://localhost:5000/robots.txt

# Проверить sitemap
curl http://localhost:5000/sitemap.xml

# Посмотреть мета-теги
curl http://localhost:5000/ | grep -i "meta name"

# Проверить OG теги
curl http://localhost:5000/ | grep -i "og:"
```

## 📝 Где что находится:

```
/static/robots.txt           - robots.txt
/routes/seo_routes.py        - SEO роуты
/templates/seo/sitemap.xml   - шаблон sitemap
/templates/base.html         - мета-теги (строки 3-40)
/templates/index.html        - пример использования (строки 1-12)
/static/images/og-image.svg  - картинка для соцсетей (ЗАМЕНИ!)
/SEO_GUIDE.md               - подробная документация
```

## ✨ Готово!

SEO базово настроено. Теперь:
1. Замени og-image на реальную картинку
2. Обнови домен в robots.txt
3. Добавь мета-теги на остальные страницы
4. После деплоя - зарегистрируй в Google Search Console

Вопросы? Смотри `SEO_GUIDE.md` для деталей.
