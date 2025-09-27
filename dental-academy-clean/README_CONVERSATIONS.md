# Настройка переписок на продакшене

## 🎯 Быстрый старт

### 1. Установите DATABASE_URL
```bash
export DATABASE_URL='postgresql://mentora_user:pWjbqoOgAAIGdLMNHfxPTiozhF7jG2LV@dpg-d3403vre5dus73ejhfjg-a.frankfurt-postgres.render.com/mentora'
```

### 2. Запустите скрипт
```bash
python3 setup_production_conversations.py
```

## ✅ Что будет сделано

1. **Очистка:** Удалены все существующие переписки
2. **Создание:** 11 пользователей + 3 темы с голландскими сообщениями
3. **Результат:** Переписки в стиле WhatsApp как на скриншотах

## 📱 Создаваемые переписки

- **"Collega Chat - Taal certificaten"** - обсуждение языковых сертификатов
- **"AKV Tandartsen - BIG Registratie"** - информация о BIG регистрации  
- **"BGB Examen Materialen"** - материалы для экзаменов

## 👥 Пользователи

Liliam, Ümit Isiklar, Bahar Yıldız, Drs. B. De lange, Viktoriia, Shiva, Karlien Bruwer, Pelin Babayigit, Rinsy, Yuliya Termonia, Rami

## 🔧 Требования

- Python 3.6+
- psycopg2-binary: `pip install psycopg2-binary`
- DATABASE_URL из Render Environment

## ⚠️ Внимание

Скрипт **удаляет ВСЕ существующие переписки** безвозвратно!
