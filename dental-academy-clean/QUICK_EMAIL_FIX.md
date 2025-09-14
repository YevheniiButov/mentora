# 🚨 БЫСТРОЕ ИСПРАВЛЕНИЕ EMAIL В PRODUCTION

## Проблема
Email уведомления не отправляются в production, хотя настройки в Render Dashboard есть.

## Причина
Несоответствие между настройками в Render (Brevo) и кодом (MailerSend).

## Решение (2 минуты)

### 1. В Render Dashboard:
Перейдите в **Environment Variables** и добавьте/обновите:

```bash
MAIL_SUPPRESS_SEND=false
```

### 2. Проверьте существующие настройки:
Убедитесь, что у вас есть:
- `MAIL_SERVER=smtp-relay.brevo.com`
- `MAIL_USERNAME=96d92f001@smtp-brevo.com`
- `MAIL_PASSWORD=JrbVFGpHhgynKMOQ`

### 3. Сохраните и перезапустите:
1. Нажмите **"Save Changes"**
2. Сервис автоматически перезапустится

## Проверка
После перезапуска:
1. Зарегистрируйте тестового пользователя
2. Проверьте получение email подтверждения

## Если не работает
Проверьте логи в Render Dashboard → Logs на наличие ошибок email.

---
**Время выполнения: 2-3 минуты**
