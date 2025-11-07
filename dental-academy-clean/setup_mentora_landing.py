#!/usr/bin/env python3
"""
Скрипт для настройки mentora.com.in с лендинговой страницей
"""
import os
import shutil
from pathlib import Path

def verify_mentora_landing_exists():
    """Проверить, что файл mentora_landing.html существует"""
    landing_path = Path("templates/mentora_landing.html")
    if landing_path.exists():
        print(f"✅ Лендинговая страница найдена: {landing_path}")
        return True
    else:
        print(f"❌ Лендинговая страница не найдена: {landing_path}")
        return False

def check_app_routing():
    """Проверить, что в app.py есть правильная логика роутинга"""
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ Файл app.py не найден")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверить наличие логики для mentora.com.in
    if "mentora.com.in" in content and "mentora_landing.html" in content:
        print("✅ Логика роутинга для mentora.com.in настроена")
        return True
    else:
        print("❌ Логика роутинга для mentora.com.in не найдена")
        return False

def create_test_domain_config():
    """Создать конфигурацию для тестового домена"""
    config_content = """# Mentora Test Domain Configuration
# Этот файл содержит настройки для тестового домена mentora.com.in

# Основные настройки
TEST_DOMAIN=mentora.com.in
PRODUCTION_DOMAIN=bigmentor.nl
USE_MENTORA_LANDING=True

# Лендинговая страница
LANDING_PAGE_TEMPLATE=mentora_landing.html
LANDING_PAGE_TITLE=Mentora - Come In to Excellence

# Настройки для тестового домена
ENABLE_ANALYTICS=True
ENABLE_DIAGNOSTICS=True
ENABLE_IRT_TESTING=True
ENABLE_DEBUG_MODE=False

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/mentora_test.log

# Безопасность
SECRET_KEY=mentora_test_secret_key_change_in_production
WTF_CSRF_ENABLED=True

# Email (тестовый)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=test@mentora.com.in
MAIL_PASSWORD=test_email_password

# База данных (тестовая)
DATABASE_URL=postgresql://mentora_test_user:test_password@localhost:5432/mentora_test_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=mentora_test_db
DATABASE_USER=mentora_test_user
DATABASE_PASSWORD=test_password
"""
    
    with open('mentora_test_config.env', 'w') as f:
        f.write(config_content)
    
    print("✅ Создана конфигурация mentora_test_config.env")

def create_landing_test_script():
    """Создать скрипт для тестирования лендинговой страницы"""
    script_content = """#!/usr/bin/env python3
\"\"\"
Скрипт для тестирования лендинговой страницы mentora.com.in
\"\"\"
import requests
import sys

def test_mentora_landing():
    \"\"\"Тестировать лендинговую страницу\"\"\"
    test_urls = [
        "http://mentora.com.in",
        "http://www.mentora.com.in",
        "https://mentora.com.in",
        "https://www.mentora.com.in"
    ]
    
    print("🧪 Тестирование лендинговой страницы mentora.com.in...")
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "Mentora - Come In to Excellence" in response.text:
                    print(f"✅ {url} - Лендинговая страница загружается корректно")
                else:
                    print(f"⚠️  {url} - Страница загружается, но не содержит ожидаемый контент")
            else:
                print(f"❌ {url} - Ошибка {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - Ошибка подключения: {e}")
    
    print("\\n📋 Проверьте вручную:")
    print("1. Откройте https://mentora.com.in в браузере")
    print("2. Убедитесь, что загружается космический дизайн")
    print("3. Проверьте, что все элементы отображаются корректно")
    print("4. Протестируйте на мобильных устройствах")

if __name__ == "__main__":
    test_mentora_landing()
"""
    
    with open('test_mentora_landing.py', 'w') as f:
        f.write(script_content)
    
    os.chmod('test_mentora_landing.py', 0o755)
    print("✅ Создан скрипт test_mentora_landing.py")

def create_deployment_guide():
    """Создать руководство по деплою с лендинговой страницей"""
    guide_content = """# Руководство по деплою mentora.com.in с лендинговой страницей

## 🚀 Быстрый старт

### 1. Подготовка
```bash
# Проверить, что все файлы на месте
python3 setup_mentora_landing.py

# Создать резервную копию продакшн БД
python3 backup_production_postgresql.py
```

### 2. Настройка тестового домена
```bash
# Настроить тестовую БД
./setup_test_database.sh

# Переключиться на тестовую конфигурацию
cp mentora_test_config.env .env
```

### 3. Деплой
```bash
# Задеплоить коммиты на тестовый домен
python3 deploy_to_test_domain.py
```

### 4. Тестирование
```bash
# Протестировать лендинговую страницу
python3 test_mentora_landing.py

# Открыть в браузере
open https://mentora.com.in
```

## 📋 Что должно работать

### ✅ Лендинговая страница (mentora.com.in)
- Космический дизайн с черной дырой
- Анимации и эффекты
- Адаптивный дизайн
- Быстрая загрузка

### ✅ Основное приложение (после входа)
- Аналитика (исправления PostgreSQL)
- IRT диагностика
- Регистрация пользователей
- Админ панель
- Форум

## 🔧 Настройка Nginx

Убедитесь, что в Nginx конфигурации:
```nginx
server_name mentora.com.in www.mentora.com.in;
```

## 🛡️ Безопасность

- Тестовая БД изолирована от продакшн
- Отдельные SSL сертификаты
- Логирование в отдельные файлы
- Тестовые API ключи

## 📊 Мониторинг

- Логи: `/var/log/nginx/mentora.com.in.*.log`
- Приложение: `logs/mentora_test.log`
- Метрики: доступны в админ панели

## 🚨 Откат

В случае проблем:
```bash
# Откатиться к предыдущей версии
git checkout d727518

# Восстановить БД из бэкапа
# (инструкции в backup_production_postgresql.py)
```
"""
    
    with open('MENTORA_DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Создано руководство MENTORA_DEPLOYMENT_GUIDE.md")

def main():
    """Основная функция"""
    print("🚀 Настройка mentora.com.in с лендинговой страницей")
    print("=" * 60)
    
    # Проверить наличие лендинговой страницы
    if not verify_mentora_landing_exists():
        print("❌ Лендинговая страница не найдена")
        return False
    
    # Проверить логику роутинга
    if not check_app_routing():
        print("❌ Логика роутинга не настроена")
        return False
    
    # Создать конфигурацию
    create_test_domain_config()
    
    # Создать скрипт тестирования
    create_landing_test_script()
    
    # Создать руководство
    create_deployment_guide()
    
    print("\n" + "=" * 60)
    print("✅ Настройка mentora.com.in завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Создать резервную копию продакшн БД")
    print("2. Настроить тестовую БД")
    print("3. Задеплоить на тестовый домен")
    print("4. Протестировать лендинговую страницу")
    print("\n📖 Подробное руководство: MENTORA_DEPLOYMENT_GUIDE.md")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


