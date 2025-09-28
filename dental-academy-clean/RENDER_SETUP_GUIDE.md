# 🚀 Настройка Render для двух доменов

## 📋 Текущая ситуация:
- **Веб-сервис**: `mentora-nl` на Render
- **Домены**: 
  - `bigmentor.nl` (продакшн)
  - `mentora.com.in` (тестовый)

## 🔧 Настройка в Render:

### 1. **Добавить второй домен в Render:**

1. Зайти в панель Render
2. Выбрать сервис `mentora-nl`
3. Перейти в раздел "Settings" → "Custom Domains"
4. Добавить домен `mentora.com.in`
5. Настроить DNS записи для `mentora.com.in`

### 2. **DNS настройки для mentora.com.in:**

```
Type: CNAME
Name: @
Value: mentora-nl.onrender.com

Type: CNAME  
Name: www
Value: mentora-nl.onrender.com
```

### 3. **Переменные окружения:**

Убедитесь, что в Render настроены переменные окружения:

```bash
# Основные настройки
FLASK_ENV=production
SECRET_KEY=your_secret_key

# База данных (общая для обоих доменов)
DATABASE_URL=postgresql://user:pass@host:port/db

# Домены
PRODUCTION_DOMAIN=bigmentor.nl
TEST_DOMAIN=mentora.com.in
```

## 🧪 Тестирование после деплоя:

### 1. **Проверить роутинг доменов:**
```bash
python3 test_domain_routing.py
```

### 2. **Ручная проверка:**
- **bigmentor.nl** → должна показывать обычную главную страницу
- **mentora.com.in** → должна показывать космическую лендинговую страницу

### 3. **Проверить функциональность входа:**
- Открыть `https://mentora.com.in`
- Ввести тестовые учетные данные
- Нажать "Come In"
- Проверить, что происходит вход в систему

## 🔑 Создание тестового пользователя:

### Вариант 1: Через админ панель
1. Зайти на `https://bigmentor.nl/admin`
2. Создать нового пользователя:
   - Email: `mentora@bigmentor.nl`
   - Username: `mentora_prod_test`
   - Password: `mentora2024!`

### Вариант 2: Через скрипт (если есть доступ к серверу)
```bash
python3 create_production_test_user.py
```

## 📊 Логика приложения:

Приложение автоматически определяет домен и показывает соответствующую страницу:

```python
# В app.py
host = request.host.lower()

if 'mentora.com.in' in host:
    return render_template('mentora_landing.html')  # Космическая страница
else:
    return render_template('index.html')  # Обычная главная
```

## 🚨 В случае проблем:

### 1. **Проверить логи Render:**
- Зайти в панель Render
- Выбрать сервис `mentora-nl`
- Перейти в "Logs"
- Проверить ошибки деплоя

### 2. **Проверить DNS:**
```bash
# Проверить DNS для mentora.com.in
nslookup mentora.com.in
dig mentora.com.in
```

### 3. **Проверить SSL сертификаты:**
- Render автоматически выдает SSL сертификаты
- Убедиться, что оба домена имеют валидные сертификаты

## ✅ Ожидаемый результат:

После успешного деплоя:

1. **bigmentor.nl** - работает как обычно (продакшн)
2. **mentora.com.in** - показывает космическую лендинговую страницу
3. **Вход через mentora.com.in** - работает с тестовыми учетными данными
4. **Аналитика** - исправлена, нет ошибок PostgreSQL
5. **Безопасность** - полная изоляция тестирования от продакшн

---

**Важно**: Все изменения уже запушены в GitHub, Render должен автоматически начать деплой!


