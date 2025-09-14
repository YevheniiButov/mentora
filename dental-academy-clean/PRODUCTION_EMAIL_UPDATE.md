# Обновление Email настроек в Production

## 🚨 КРИТИЧЕСКОЕ ОБНОВЛЕНИЕ: Включение Email уведомлений в Production

### Проблема
В production сервере email уведомления отключены (`MAIL_SUPPRESS_SEND=true`).

### Решение для Render.com

#### 1. Обновить переменные окружения в Render Dashboard:

Перейдите в Render Dashboard → Ваш сервис → Environment → Environment Variables

**Добавить/обновить следующие переменные:**

```bash
MAIL_SUPPRESS_SEND=false
MAIL_SERVER=smtp.mailersend.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=MS_uUzJtfkAxyPn@mentora.mlsender.net
MAIL_PASSWORD=mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM
MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>
EMAIL_CONFIRMATION_SALT=mentora-production-salt-2025
```

#### 2. Обновить render.yaml (опционально):

Добавить в `render.yaml` в секцию `envVars`:

```yaml
envVars:
  - key: MAIL_SUPPRESS_SEND
    value: "false"
  - key: MAIL_SERVER
    value: "smtp.mailersend.net"
  - key: MAIL_PORT
    value: "587"
  - key: MAIL_USE_TLS
    value: "true"
  - key: MAIL_USE_SSL
    value: "false"
  - key: MAIL_USERNAME
    value: "MS_uUzJtfkAxyPn@mentora.mlsender.net"
  - key: MAIL_PASSWORD
    value: "mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM"
  - key: MAIL_DEFAULT_SENDER
    value: "Mentora <noreply@mentora.com>"
  - key: EMAIL_CONFIRMATION_SALT
    value: "mentora-production-salt-2025"
```

#### 3. Перезапустить сервис:

После обновления переменных окружения:
1. Нажмите "Save Changes" в Render Dashboard
2. Сервис автоматически перезапустится
3. Или нажмите "Manual Deploy" для принудительного перезапуска

### Решение для других хостингов

#### Для VPS/серверов:

1. Обновить файл `.env` на сервере:
```bash
MAIL_SUPPRESS_SEND=false
```

2. Перезапустить приложение:
```bash
systemctl restart your-app-service
# или
pm2 restart your-app
# или
docker-compose restart
```

### Проверка

После обновления:

1. **Зарегистрировать тестового пользователя**
2. **Проверить получение email подтверждения**
3. **Протестировать сброс пароля**

### Важные замечания

- ✅ **MailerSend учетные данные** уже настроены и работают
- ✅ **Конфигурация проверена** локально
- ⚠️ **Переменные окружения** нужно обновить в production
- ⚠️ **Сервис нужно перезапустить** после изменений

### Откат (если что-то пойдет не так)

Если нужно временно отключить email:
```bash
MAIL_SUPPRESS_SEND=true
```

Это вернет режим "только консоль" без отправки реальных email.
