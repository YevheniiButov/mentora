# 📧 Настройка Email подтверждения

## ✅ Что реализовано

Система подтверждения регистрации по email полностью реализована:

### 🔧 Функциональность:
- **Регистрация с подтверждением email** - после регистрации отправляется письмо с ссылкой подтверждения
- **Безопасные токены** - токены хешируются и имеют срок действия 1 час
- **Повторная отправка** - возможность отправить письмо подтверждения повторно
- **Блокировка входа** - пользователи не могут войти без подтверждения email
- **Приветственное письмо** - автоматическая отправка после подтверждения

### 📁 Добавленные файлы:
- `utils/email_service.py` - сервис отправки email
- `templates/emails/confirm_email.html` - HTML шаблон письма подтверждения
- `templates/emails/confirm_email.txt` - текстовый шаблон письма подтверждения
- `templates/emails/welcome.html` - HTML шаблон приветственного письма
- `templates/emails/welcome.txt` - текстовый шаблон приветственного письма

### 🔄 Измененные файлы:
- `config.py` - добавлены настройки email
- `models.py` - добавлены поля для подтверждения email
- `extensions.py` - добавлен Flask-Mail
- `routes/auth_routes.py` - обновлена логика регистрации и входа
- `templates/auth/login.html` - добавлена обработка неподтвержденных email
- `requirements.txt` - добавлен Flask-Mail

## ⚙️ Настройка для production

### 1. Настройка SMTP сервера

Добавьте в `.env` файл:

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@dentalacademy.nl

# Base URL for confirmation links
BASE_URL=https://yourdomain.com
```

### 2. Для Gmail:

1. Включите двухфакторную аутентификацию
2. Создайте пароль приложения:
   - Перейдите в настройки Google аккаунта
   - Безопасность → Пароли приложений
   - Создайте пароль для "Почта"
   - Используйте этот пароль в `MAIL_PASSWORD`

### 3. Для других провайдеров:

#### Mailgun:
```bash
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@yourdomain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
```

#### SendGrid:
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

#### Amazon SES:
```bash
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USERNAME=your-ses-username
MAIL_PASSWORD=your-ses-password
```

## 🧪 Тестирование

### 1. Локальное тестирование (без отправки email):

Для разработки можно использовать консольный вывод вместо реальной отправки:

```python
# В config.py для development
MAIL_SUPPRESS_SEND = True  # Не отправлять реальные письма
```

### 2. Тестирование с реальной отправкой:

1. Настройте SMTP сервер
2. Зарегистрируйте нового пользователя
3. Проверьте почту на наличие письма подтверждения
4. Перейдите по ссылке в письме
5. Попробуйте войти в систему

## 🔒 Безопасность

- **Токены хешируются** перед сохранением в базу данных
- **Срок действия** токенов - 1 час
- **Одноразовые токены** - после подтверждения токен удаляется
- **Валидация** всех входящих данных

## 📊 Мониторинг

Логи отправки email записываются в:
- `current_app.logger.info()` - успешная отправка
- `current_app.logger.error()` - ошибки отправки

## 🚀 Деплой

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Создайте миграцию для новых полей:
   ```bash
   flask db migrate -m "Add email confirmation fields"
   flask db upgrade
   ```

3. Настройте переменные окружения для email

4. Перезапустите приложение

## 📝 API Endpoints

- `POST /auth/register` - регистрация с отправкой email подтверждения
- `GET /auth/confirm-email/<token>` - подтверждение email по токену
- `POST /auth/resend-confirmation` - повторная отправка письма подтверждения

## 🎯 Следующие шаги

- [ ] Добавить сброс пароля по email
- [ ] Добавить уведомления о важных событиях
- [ ] Настроить мониторинг доставки email
- [ ] Добавить шаблоны для разных языков


