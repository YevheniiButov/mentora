# Email Setup Instructions for Production

## Gmail SMTP Configuration

Для отправки email подтверждений в production нужно настроить Gmail SMTP.

### Шаг 1: Создать Gmail App Password

1. Войдите в Gmail аккаунт
2. Перейдите в настройки безопасности: https://myaccount.google.com/security
3. Включите 2-Step Verification если не включена
4. Перейдите в "App passwords"
5. Создайте новый App Password для "Mail"
6. Скопируйте сгенерированный пароль (16 символов)

### Шаг 2: Настроить переменные окружения в Render

В Render Dashboard добавьте следующие переменные окружения:

```
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-character-app-password
```

### Шаг 3: Проверить конфигурацию

После настройки email подтверждения должны отправляться пользователям.

## Альтернативные варианты

### Mailgun
```
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=your-mailgun-username
MAIL_PASSWORD=your-mailgun-password
```

### SendGrid
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

### MailerSend
```
MAIL_SERVER=smtp.mailersend.net
MAIL_PORT=587
MAIL_USERNAME=your-mailersend-username
MAIL_PASSWORD=your-mailersend-password
```

## Текущая конфигурация

В render.yaml уже настроено:
- MAIL_SERVER=smtp.gmail.com
- MAIL_PORT=587
- MAIL_USE_TLS=true
- MAIL_SUPPRESS_SEND=false

Нужно только добавить MAIL_USERNAME и MAIL_PASSWORD в Render Dashboard.








