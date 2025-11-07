#!/bin/bash
# Скрипт для полной очистки и перезапуска Flask сервера

echo "🔄 Полная очистка и перезапуск Flask сервера..."

# 1. Остановка всех процессов Flask
echo "1. Остановка процессов Flask..."
pkill -f "python.*app.py" 2>/dev/null
pkill -f "flask run" 2>/dev/null
sleep 2

# 2. Очистка кэша Python
echo "2. Очистка кэша Python..."
find . -type d -name __pycache__ -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null
find . -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null

# 3. Очистка .pyc файлов в корне
rm -f *.pyc 2>/dev/null

echo "✅ Очистка завершена"
echo ""
echo "Теперь запустите сервер:"
echo "  python3 app.py"
echo "или"
echo "  flask run --port=5002 --host=127.0.0.1 --reload"
echo ""
echo "После запуска проверьте:"
echo "  python3 check_routes.py"


