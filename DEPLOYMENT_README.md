# 🚀 ДЕПЛОЙ НА RENDER - ИНСТРУКЦИЯ

## ✅ **ГОТОВЫЕ ФАЙЛЫ:**
- `render.yaml` - конфигурация Render
- `requirements-render.txt` - зависимости
- `scripts/seed_production_data.py` - загрузка данных
- Health check в `app.py`
- `env.production.example` - переменные окружения

## 🎯 **ПОШАГИ:**

### 1. **Подготовка**
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. **Render.com**
1. Создайте аккаунт на render.com
2. "New +" → "Web Service"
3. Подключите GitHub репозиторий
4. Выберите ветку `main`

### 3. **База данных**
1. "New +" → "PostgreSQL"
2. Name: `mentora-db`
3. Database: `mentora`
4. User: `mentora_user`

### 4. **Переменные окружения**
В настройках Web Service добавьте:
```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://mentora_user:password@host:port/mentora
DIGID_MOCK_MODE=true
DIGID_ENABLED=true
```

### 5. **Запуск**
Нажмите "Create Web Service"

## 🔍 **ПРОВЕРКА:**
- Health: `https://your-app.onrender.com/health`
- Главная: `https://your-app.onrender.com/`
- Admin: `admin@mentora.nl` / `admin123`

## 🎉 **ГОТОВО!** 