# 🔧 Создание администратора на деплой сервере

## Способы создания админа

### 1. 🚀 Быстрый способ (рекомендуется)

```bash
# На деплой сервере
python3 quick_admin.py admin@mentora.com "Admin User" "secure_password123"
```

**Параметры:**
- `admin@mentora.com` - email администратора
- `"Admin User"` - имя и фамилия
- `"secure_password123"` - пароль (минимум 8 символов)

### 2. 📋 Интерактивный способ

```bash
# На деплой сервере
python3 create_admin.py create
```

Скрипт попросит ввести:
- Email
- Имя
- Фамилию  
- Пароль

### 3. 📊 Просмотр существующих админов

```bash
# Показать всех администраторов
python3 create_admin.py list
```

## На Render.com

### Через Render Shell:

1. **Откройте Render Dashboard**
2. **Перейдите в ваш сервис**
3. **Нажмите "Shell"** в левом меню
4. **Выполните команду:**

```bash
python3 quick_admin.py admin@mentora.com "Admin User" "your_secure_password"
```

### Через Render Logs (если Shell недоступен):

1. **Добавьте временный маршрут** в `app.py`:

```python
@app.route('/create-admin')
def create_admin_route():
    if request.args.get('token') != 'your_secret_token':
        return 'Unauthorized', 401
    
    email = request.args.get('email', 'admin@mentora.com')
    password = request.args.get('password', 'admin123456')
    
    try:
        admin = User(
            email=email,
            username=email,
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            email_confirmed=True,
            registration_completed=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        return f'Admin created: {email}'
    except Exception as e:
        return f'Error: {str(e)}'
```

2. **Откройте URL:** `https://your-app.onrender.com/create-admin?token=your_secret_token&email=admin@mentora.com&password=admin123456`

3. **Удалите маршрут** после создания админа

## На VPS/сервере

### SSH подключение:

```bash
# Подключитесь к серверу
ssh user@your-server.com

# Перейдите в директорию проекта
cd /path/to/mentora

# Создайте админа
python3 quick_admin.py admin@mentora.com "Admin User" "secure_password123"
```

### Docker:

```bash
# Если приложение в Docker
docker exec -it your-container-name python3 quick_admin.py admin@mentora.com "Admin User" "secure_password123"
```

## Проверка создания

После создания админа:

1. **Откройте админ панель:** `https://your-domain.com/admin`
2. **Войдите с созданными данными**
3. **Проверьте доступ к функциям админа**

## Безопасность

⚠️ **Важно:**
- Используйте **сложные пароли** (минимум 12 символов)
- **Удалите временные маршруты** после создания админа
- **Не оставляйте скрипты** в production
- **Ограничьте доступ** к админ панели по IP (если возможно)

## Устранение проблем

### Ошибка "User already exists":
```bash
# Проверьте существующих пользователей
python3 create_admin.py list

# Сделайте существующего пользователя админом
python3 quick_admin.py existing@email.com "Existing User" "new_password"
```

### Ошибка подключения к БД:
- Проверьте переменные окружения `DATABASE_URL`
- Убедитесь, что база данных доступна
- Проверьте права доступа

### Ошибка импорта модулей:
- Убедитесь, что находитесь в правильной директории
- Проверьте, что все зависимости установлены
- Используйте виртуальное окружение

## Примеры команд

```bash
# Создать админа с русским именем
python3 quick_admin.py admin@mentora.com "Админ Админов" "AdminPass123!"

# Создать админа с английским именем  
python3 quick_admin.py admin@mentora.com "Admin User" "SecurePass123"

# Показать всех админов
python3 create_admin.py list

# Интерактивное создание
python3 create_admin.py create
```

## После создания

1. ✅ **Войдите в админ панель**
2. ✅ **Проверьте доступ к функциям**
3. ✅ **Удалите временные файлы** (если использовали)
4. ✅ **Настройте безопасность**
5. ✅ **Создайте резервную копию** базы данных
