# DigiD Integration Setup Guide

## Обзор

DigiD (Digital Identity) - это система электронной идентификации граждан Нидерландов. Данная интеграция позволяет пользователям входить в Mentora Clean через DigiD.

## Архитектура

### Режимы работы

1. **Mock Mode (Разработка/Тестирование)**
   - Имитация DigiD для разработки
   - Не требует реальных сертификатов
   - Использует тестовые данные пользователей

2. **Production Mode (Staging/Production)**
   - Реальная интеграция с DigiD
   - Требует SAML сертификаты
   - Использует официальные DigiD endpoints

### Компоненты

- `config.py` - Конфигурация для разных окружений
- `routes/digid_routes.py` - Роуты для DigiD интеграции
- `models.py` - Модели User и DigiDSession
- `templates/digid/` - Шаблоны для DigiD интерфейса

## Установка и настройка

### 1. Переменные окружения

Скопируйте `env.example` в `.env` и настройте переменные:

```bash
cp env.example .env
```

#### Для разработки (Mock Mode):
```env
FLASK_ENV=development
DIGID_ENABLED=true
DIGID_MOCK_MODE=true
```

#### Для staging (Pre-production DigiD):
```env
FLASK_ENV=staging
DIGID_ENABLED=true
DIGID_MOCK_MODE=false
DIGID_BASE_URL=https://preprod.digid.nl
DIGID_ENTITY_ID=your-entity-id
DIGID_ACS_URL=https://your-domain.com/digid/callback
DIGID_SLO_URL=https://your-domain.com/digid/logout
DIGID_CERTIFICATE_PATH=/path/to/certificate.crt
DIGID_PRIVATE_KEY_PATH=/path/to/private.key
```

#### Для production (Real DigiD):
```env
FLASK_ENV=production
DIGID_ENABLED=true
DIGID_MOCK_MODE=false
DIGID_BASE_URL=https://digid.nl
# ... остальные переменные как в staging
```

### 2. Миграция базы данных

```bash
flask db upgrade
```

### 3. Тестирование конфигурации

```bash
python3 config.py
```

## Использование

### Для пользователей

1. **Вход через DigiD**
   - Нажмите "Inloggen met DigiD" в навбаре
   - Введите BSN и пароль
   - Подтвердите вход

2. **Статус DigiD**
   - В профиле отображается статус DigiD
   - Показывается время истечения сессии
   - Возможность выхода из DigiD

### Для разработчиков

#### Тестовые аккаунты (Mock Mode)

| BSN | Имя | Роль |
|-----|-----|------|
| 123456789 | Jan Jansen | Обычный пользователь |
| 987654321 | Maria de Vries | Преподаватель |
| 111222333 | Admin User | Администратор |

#### API Endpoints

- `GET /digid/login` - Страница входа DigiD
- `POST /digid/authenticate` - Аутентификация
- `GET /digid/callback` - Callback после успешной аутентификации
- `GET /digid/logout` - Выход из DigiD
- `GET /digid/status` - Статус DigiD сессии

#### Декораторы

```python
from routes.digid_routes import digid_required

@app.route('/protected')
@digid_required
def protected_route():
    return "Только для пользователей DigiD"
```

## Безопасность

### Mock Mode
- Используется только для разработки
- Не содержит реальных данных
- Сессии хранятся в базе данных

### Production Mode
- SAML 2.0 аутентификация
- Шифрование всех данных
- Проверка сертификатов
- Secure cookies

### Рекомендации

1. **Никогда не используйте Mock Mode в production**
2. **Храните сертификаты в безопасном месте**
3. **Регулярно обновляйте сертификаты**
4. **Мониторьте логи аутентификации**

## Устранение неполадок

### Ошибка "Could not build url for endpoint 'digid.login'"

**Причина:** Blueprint не зарегистрирован правильно

**Решение:**
```python
# В app.py
from routes.digid_routes import digid_bp
app.register_blueprint(digid_bp, url_prefix='/digid')
```

### Ошибка "Missing required DigiD environment variables"

**Причина:** Не настроены переменные окружения

**Решение:** Проверьте файл `.env` и установите все обязательные переменные

### Ошибка "DigiD certificate file not found"

**Причина:** Неправильный путь к сертификату

**Решение:** Проверьте переменные `DIGID_CERTIFICATE_PATH` и `DIGID_PRIVATE_KEY_PATH`

### Сессия DigiD истекает слишком быстро

**Причина:** Неправильный timeout

**Решение:** Настройте `DIGID_SESSION_TIMEOUT` в конфигурации

## Мониторинг

### Логи

DigiD интеграция логирует следующие события:
- Попытки входа
- Успешные аутентификации
- Ошибки аутентификации
- Истечение сессий

### Метрики

Отслеживайте:
- Количество успешных входов
- Количество неудачных попыток
- Время жизни сессий
- Ошибки сертификатов

## Обновления

### Версия 1.0
- Базовая интеграция DigiD
- Mock mode для разработки
- SAML 2.0 поддержка
- Управление сессиями

### Планы на будущее
- Поддержка DigiD Midden
- Интеграция с eHerkenning
- Расширенная аналитика
- Многофакторная аутентификация

## Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в правильности конфигурации
3. Проверьте статус DigiD сервисов
4. Обратитесь к документации DigiD

## Ссылки

- [Официальная документация DigiD](https://www.digid.nl/)
- [SAML 2.0 спецификация](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [Flask-SAML2 документация](https://flask-saml2.readthedocs.io/) 