# Создание админа на Render

## Способ 1: Через Render Shell

1. Зайдите в ваш Render dashboard
2. Выберите ваш сервис (mentora)
3. Перейдите в раздел "Shell"
4. Выполните команды:

```bash
# Перейдите в директорию приложения
cd /opt/render/project/src

# Создайте админа
python3 -c "
import sys
sys.path.append('.')
from app import app
from models import User, db

with app.app_context():
    email = 'admin@mentora.com.in'
    password = 'MentoraAdmin2025!'
    
    # Проверяем существующего пользователя
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        existing_user.role = 'admin'
        existing_user.is_active = True
        existing_user.email_confirmed = True
        existing_user.set_password(password)
        db.session.commit()
        print(f'✅ User {email} is now admin!')
    else:
        # Создаем нового админа
        admin_user = User(
            email=email,
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            email_confirmed=True,
            registration_completed=True
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        print(f'✅ Admin {email} created!')
    
    print(f'🌐 Access: https://www.mentora.com.in/admin/')
    print(f'📧 Email: {email}')
    print(f'🔑 Password: {password}')
"
```

## Способ 2: Через Render Console

1. В Render dashboard выберите ваш сервис
2. Перейдите в "Environment"
3. Добавьте временную переменную окружения:
   - Key: `CREATE_ADMIN`
   - Value: `true`
4. Перезапустите сервис
5. Админ будет создан автоматически при запуске

## Способ 3: Через GitHub Actions (если настроены)

Создайте файл `.github/workflows/create-admin.yml`:

```yaml
name: Create Admin
on:
  workflow_dispatch:
    inputs:
      email:
        description: 'Admin email'
        required: true
        default: 'admin@mentora.com.in'
      password:
        description: 'Admin password'
        required: true
        default: 'MentoraAdmin2025!'

jobs:
  create-admin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create Admin
        run: |
          # Ваши команды для создания админа
```

## Данные для входа

После создания админа используйте:

- **URL**: https://www.mentora.com.in/admin/
- **Email**: admin@mentora.com.in
- **Password**: MentoraAdmin2025!

⚠️ **ВАЖНО**: Смените пароль после первого входа!
