# 🚀 Инструкции по деплою на mentora.com.in

## 📋 Готовые коммиты для деплоя:

1. **e9b50af** - Fix PostgreSQL compatibility issues in admin analytics
2. **8caf3bf** - Add test domain setup for safe deployment  
3. **81fd10b** - Configure mentora.com.in with landing page
4. **c4eb5c3** - Add login functionality to mentora.com.in landing page

## 🎯 Что нужно сделать:

### 1. На продакшн сервере (bigmentor.nl):
```bash
# Создать резервную копию БД
pg_dump -h localhost -U your_user -d your_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Или использовать наш скрипт (если настроены переменные окружения)
python3 backup_production_postgresql.py
```

### 2. На тестовом сервере (mentora.com.in):
```bash
# Клонировать репозиторий
git clone https://github.com/your-repo/dental-academy-clean.git
cd dental-academy-clean

# Переключиться на нужные коммиты
git checkout c4eb5c3

# Настроить тестовую конфигурацию
cp mentora_test_config.env .env

# Установить зависимости
pip install -r requirements.txt

# Настроить БД (если нужно)
python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Запустить приложение
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### 3. Настроить Nginx:
```bash
# Скопировать конфигурацию
sudo cp nginx_mentora_test.conf /etc/nginx/sites-available/mentora.com.in
sudo ln -s /etc/nginx/sites-available/mentora.com.in /etc/nginx/sites-enabled/

# Получить SSL сертификат
sudo certbot --nginx -d mentora.com.in -d www.mentora.com.in

# Перезапустить Nginx
sudo systemctl reload nginx
```

## 🧪 Тестирование:

### 1. Проверить лендинговую страницу:
```bash
# Открыть в браузере
open https://mentora.com.in

# Или протестировать автоматически
python3 test_mentora_landing.py
```

### 2. Проверить функциональность входа:
```bash
# Протестировать вход
python3 test_mentora_login.py
```

### 3. Проверить аналитику:
- Зайти в админ панель
- Проверить, что нет ошибок PostgreSQL
- Убедиться, что аналитика работает

## ✅ Что должно работать:

1. **Лендинговая страница** - космический дизайн с формой входа
2. **Вход в систему** - через форму на лендинговой странице
3. **Аналитика** - исправления PostgreSQL совместимости
4. **Админ панель** - без ошибок julianday/date функций
5. **Все остальные функции** - как на продакшне

## 🚨 В случае проблем:

### Откат:
```bash
# Откатиться к предыдущему коммиту
git checkout d727518

# Восстановить БД из бэкапа
psql -h localhost -U your_user -d your_db < backup_file.sql
```

### Логи для отладки:
```bash
# Логи приложения
tail -f logs/mentora_test.log

# Логи Nginx
tail -f /var/log/nginx/mentora.com.in.error.log
tail -f /var/log/nginx/mentora.com.in.access.log
```

## 📊 После успешного тестирования:

### Деплой на продакшн:
```bash
# На продакшн сервере
git pull origin main
# Приложение автоматически перезапустится (если настроен auto-deploy)
```

## 🔧 Полезные команды:

```bash
# Проверить статус приложения
systemctl status your-app-service

# Перезапустить приложение
systemctl restart your-app-service

# Проверить логи
journalctl -u your-app-service -f

# Проверить подключение к БД
python3 -c "from app import create_app; app = create_app(); print('DB connection OK')"
```

---

**Важно**: Всегда тестируйте на mentora.com.in перед деплоем на продакшн bigmentor.nl!
