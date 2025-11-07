#!/bin/bash
# Полная очистка и перезапуск Flask сервера

echo "🔄 Полная очистка и перезапуск Flask сервера..."
echo ""

# 1. Остановка всех процессов Flask
echo "1️⃣ Остановка процессов Flask..."
pkill -9 -f "python.*app.py" 2>/dev/null
pkill -9 -f "python.*run.py" 2>/dev/null
pkill -9 -f "flask run" 2>/dev/null
pkill -9 -f "gunicorn" 2>/dev/null
sleep 2

# 2. Очистка кэша Python
echo "2️⃣ Очистка кэша Python..."
find . -type d -name __pycache__ -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null
find . -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null
find . -name "*.pyd" -not -path "./venv/*" -delete 2>/dev/null

# 3. Очистка .pyc файлов в корне
rm -f *.pyc 2>/dev/null

# 4. Проверка, что изменения применены
echo "3️⃣ Проверка изменений..."
if grep -q "🌐 BEFORE_REQUEST:" app.py; then
    echo "   ✅ Логирование найдено в app.py"
else
    echo "   ❌ Логирование НЕ найдено в app.py!"
fi

if grep -q "route_by_domain" app.py; then
    echo "   ✅ route_by_domain найден в app.py"
else
    echo "   ❌ route_by_domain НЕ найден в app.py!"
fi

echo ""
echo "✅ Очистка завершена"
echo ""
echo "📋 Теперь запустите сервер:"
echo "   python3 app.py"
echo "   или"
echo "   python3 run.py"
echo "   или"
echo "   flask run --port=5002 --host=127.0.0.1 --reload"
echo ""
echo "🔍 После запуска проверьте логи при запросе /en/"
echo "   Должны появиться сообщения:"
echo "   - 🌐 BEFORE_REQUEST: path=/en/"
echo "   - 🔍 route_by_domain: path=/en/"
echo "   - 🔍 before_request_main: path=/en/"


