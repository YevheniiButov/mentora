# SEO Implementation for Mentora

## ✅ Что сделано

### 1. Мета-теги (base.html)
- ✅ Title tags с блоками для кастомизации
- ✅ Meta description (уникальное для каждой страницы)
- ✅ Meta keywords
- ✅ Meta robots (index/noindex control)
- ✅ Canonical URLs
- ✅ Author tag

### 2. Open Graph (Facebook/LinkedIn)
- ✅ og:type, og:url, og:title
- ✅ og:description, og:image
- ✅ og:locale, og:site_name

### 3. Twitter Cards
- ✅ twitter:card (summary_large_image)
- ✅ twitter:title, twitter:description
- ✅ twitter:image

### 4. Hreflang (мультиязычность)
- ✅ Alternate links для всех языков
- ✅ x-default для fallback

### 5. Schema.org (структурированные данные)
- ✅ JSON-LD разметка
- ✅ EducationalOrganization type
- ✅ Расширяемый через blocks

### 6. robots.txt
- ✅ Создан в /static/robots.txt
- ✅ Блокирует админку и приватные разделы
- ✅ Указывает sitemap.xml

### 7. Sitemap.xml
- ✅ Динамическая генерация через Flask
- ✅ Роут: /sitemap.xml
- ✅ Включает статические и динамические страницы

### 8. OG Image
- ✅ Создан SVG placeholder
- ✅ Путь: /static/images/og-image.svg

## 📋 Как использовать

### Для каждой новой страницы добавь:

```jinja
{% extends "base.html" %}

{% block title %}Название страницы{% endblock %}

{% block meta_description %}Описание страницы для Google (150-160 символов){% endblock %}

{% block meta_keywords %}ключ1, ключ2, ключ3{% endblock %}

{% block og_title %}Название для соцсетей{% endblock %}

{% block og_description %}Описание для соцсетей{% endblock %}
```

### Запретить индексацию:

```jinja
{% block meta_robots %}noindex, nofollow{% endblock %}
```

### Кастомная Schema.org разметка:

```jinja
{% block schema_type %}Course{% endblock %}

{% block schema_extra %}
,
"hasCourseInstance": {
  "@type": "CourseInstance",
  "name": "BIG Exam Prep"
}
{% endblock %}
```

## 🚀 Что еще нужно сделать

### Критично:
1. **Замени SVG на реальную картинку** (1200x630px) для og:image
2. **Добавь реальный домен** в robots.txt (замени mentora.nl)
3. **Создай реальный контент** для описаний

### Опционально:
1. Google Analytics
2. Schema.org для курсов (Course type)
3. FAQ Schema для страниц с FAQ
4. Breadcrumbs Schema
5. Review/Rating Schema

## 📊 Проверка SEO

### Онлайн инструменты:
- https://search.google.com/test/rich-results - Schema.org
- https://cards-dev.twitter.com/validator - Twitter Cards
- https://developers.facebook.com/tools/debug/ - Open Graph
- https://www.xml-sitemaps.com/validate-xml-sitemap.html - Sitemap

### Локальная проверка:
```bash
# Проверить robots.txt
curl http://localhost:5002/robots.txt

# Проверить sitemap
curl http://localhost:5002/sitemap.xml

# Проверить мета-теги
curl http://localhost:5002/ | grep -i "meta"
```

## 🔍 Мониторинг

После запуска в продакшене:
1. Google Search Console - индексация
2. Google Analytics - трафик
3. Ahrefs/SEMrush - позиции
4. PageSpeed Insights - скорость

## ⚠️ Важно

- Все мета-теги должны быть **уникальными** для каждой страницы
- Длина title: **50-60 символов**
- Длина description: **150-160 символов**
- OG image должна быть минимум **1200x630px**
- Обновляй sitemap.xml при добавлении страниц
