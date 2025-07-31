# DigiD Registration System

## Описание

Система обязательной регистрации для новых пользователей DigiD. После первого входа через DigiD пользователи должны заполнить дополнительную информацию.

## Функциональность

### Обязательные поля формы:
- **Имя**: [Jan] (readonly, из DigiD)
- **Фамилия**: [van der Berg] (readonly, из DigiD)  
- **BSN**: [123456789] (readonly, из DigiD)
- **Профессия**: (required radio buttons)
  - 🦷 Tandarts
  - 💊 Apotheker  
  - 🩺 Huisarts
  - 👩‍⚕️ Verpleegkundige
- **Диплом**: [File upload] (required, PDF, max 5MB)
- **Сертификат языка**: [File upload] (optional, PDF, max 5MB)

### Валидация:
- Профессия обязательна для выбора
- Диплом обязателен для загрузки
- Файлы принимаются только в формате PDF
- Максимальный размер файла: 5MB

## Маршруты

### Основные маршруты:
- `/digid/login` - Страница входа DigiD
- `/digid/authenticate` - Аутентификация DigiD
- `/digid/complete-registration` - Форма обязательной регистрации
- `/digid/test-users` - Тестовая страница со статусом пользователей

### Логика перенаправления:
1. DigiD аутентификация → проверка `registration_completed`
2. Если регистрация не завершена → `/digid/complete-registration`
3. После успешной регистрации → карта обучения по профессии

## Модель данных

### Новые поля User:
```python
registration_completed = db.Column(db.Boolean, default=False)
profession = db.Column(db.String(50), nullable=True)
diploma_file = db.Column(db.String(255), nullable=True)
language_certificate = db.Column(db.String(255), nullable=True)
```

### Новые методы:
```python
def get_profession_display(self):
    """Возвращает профессию с эмодзи"""
    
def get_learning_map_url_by_profession(profession):
    """Возвращает URL карты обучения по профессии"""
```

## Файловая структура

```
static/uploads/documents/  # Папка для загруженных документов
├── diploma_[BSN]_[filename].pdf
└── language_cert_[BSN]_[filename].pdf
```

## Тестирование

### Тестовые пользователи:
- `demo.student` - BSN: 100000001
- `demo.docent` - BSN: 100000002  
- `demo.admin` - BSN: 100000003

### Тестовые ссылки:
- `/digid/test-users` - Просмотр всех DigiD пользователей
- `/digid/test-auth/demo.student` - Быстрый вход под тестовым пользователем

## Безопасность

### Валидация файлов:
- Проверка расширения файла (только PDF)
- Проверка размера файла (max 5MB)
- Безопасное именование файлов через `secure_filename()`
- Файлы привязаны к BSN пользователя

### Доступ к форме:
- Только для аутентифицированных DigiD пользователей
- Проверка `current_user.is_digid_user()`
- Автоматическое перенаправление если регистрация уже завершена

## Использование

1. Пользователь входит через DigiD
2. Система проверяет `registration_completed`
3. Если `False` → принудительный редирект на форму регистрации
4. Пользователь заполняет форму и загружает файлы
5. После успешной валидации → `registration_completed = True`
6. Перенаправление на карту обучения по профессии

## Стили

Форма использует DigiD дизайн-систему:
- Цвета: DigiD Blue (#003d82), DigiD Orange (#ff6600)
- Шрифты: RijksoverheidSansWebText
- Responsive дизайн для мобильных устройств
- Drag & Drop для загрузки файлов
- Интерактивные radio buttons с эмодзи 