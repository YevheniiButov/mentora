#!/bin/bash
# Быстрый деплой на mentora.com.in

echo "🚀 Быстрый деплой на mentora.com.in"
echo "=================================="

# Проверить, что мы на правильном коммите
echo "📋 Текущий коммит:"
git log --oneline -1

echo ""
echo "📋 Коммиты для деплоя:"
git log --oneline d727518..HEAD

echo ""
read -p "❓ Продолжить деплой? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Деплой отменен"
    exit 1
fi

# Переключиться на тестовую конфигурацию
echo "🔧 Настройка конфигурации..."
if [ -f "mentora_test_config.env" ]; then
    cp mentora_test_config.env .env
    echo "✅ Использована конфигурация mentora.com.in"
elif [ -f ".env.test" ]; then
    cp .env.test .env
    echo "✅ Использована тестовая конфигурация"
else
    echo "❌ Файлы конфигурации не найдены"
    exit 1
fi

# Установить зависимости
echo "📦 Установка зависимостей..."
pip install -r requirements.txt

# Проверить, что приложение запускается
echo "🧪 Проверка приложения..."
python3 -c "from app import create_app; app = create_app(); print('✅ Приложение создается успешно')"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Деплой готов!"
    echo ""
    echo "📋 Следующие шаги:"
    echo "1. Запустить приложение: gunicorn --bind 0.0.0.0:5000 app:app"
    echo "2. Настроить Nginx (если нужно)"
    echo "3. Протестировать: python3 test_mentora_landing.py"
    echo "4. Открыть: https://mentora.com.in"
else
    echo "❌ Ошибка при создании приложения"
    exit 1
fi
