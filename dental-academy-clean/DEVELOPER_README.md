# 👨‍💻 Developer Guide - Learning Planner

## 🏗️ Архитектура

### Структура проекта
```
learning-planner/
├── 📁 templates/dashboard/
│   └── create_learning_plan.html      # Основной UI
├── 📁 static/js/
│   ├── learning-plan.js               # Основная логика
│   ├── notification-system.js         # Уведомления
│   └── achievement-integration.js     # Достижения
├── 📁 utils/
│   ├── notification_system.py         # Email уведомления
│   ├── export_system.py               # iCal/PDF экспорт
│   └── achievement_integration.py     # Система достижений
├── 📁 routes/
│   ├── dashboard_routes.py            # Основные маршруты
│   ├── export_routes.py               # Экспорт API
│   └── achievement_routes.py          # Достижения API
└── 📁 models.py                       # Модели данных
```

### Ключевые компоненты

#### 1. Frontend (JavaScript)
- **learning-plan.js**: Основная логика планировщика
- **notification-system.js**: Browser notifications
- **achievement-integration.js**: Интеграция с достижениями

#### 2. Backend (Python)
- **notification_system.py**: Email уведомления
- **export_system.py**: Генерация iCal/PDF
- **achievement_integration.py**: Система достижений

#### 3. API Endpoints
```python
# Планировщик
POST /dashboard/create-learning-plan
GET  /dashboard/learning-plan/{id}
POST /dashboard/update-learning-plan/{id}

# Экспорт
GET /export-plan/{id}/ical
GET /export-plan/{id}/pdf

# Достижения
GET  /api/user-achievements
GET  /api/achievement-progress
POST /api/check-achievements
```

## 🚀 Установка и разработка

### 1. Клонирование и настройка
```bash
git clone https://github.com/mentora-academy/learning-planner.git
cd learning-planner

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
pip install reportlab     # Для PDF экспорта
```

### 2. Настройка базы данных
```bash
# Примените миграции
flask db upgrade

# Инициализируйте достижения
python3 -c "
from app import app
from utils.achievement_integration import achievement_system
with app.app_context():
    achievement_system.initialize_achievements()
"
```

### 3. Запуск в режиме разработки
```bash
# Запустите Flask приложение
python3 run.py

# В отдельном терминале запустите тесты
python3 test_all_features.py
```

## 🔧 Разработка

### Добавление новых функций

#### 1. Создание нового API endpoint
```python
# routes/dashboard_routes.py
@dashboard_bp.route('/api/new-feature', methods=['POST'])
@login_required
def new_feature():
    try:
        data = request.get_json()
        # Ваша логика здесь
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 2. Добавление JavaScript функции
```javascript
// static/js/learning-plan.js
function newFeature() {
    fetch('/api/new-feature', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Функция выполнена!', 'success');
        }
    });
}
```

#### 3. Обновление UI
```html
<!-- templates/dashboard/create_learning_plan.html -->
<button onclick="newFeature()" class="btn btn-primary">
    <i class="fas fa-star"></i>
    Новая функция
</button>
```

### Добавление новых достижений

#### 1. Определение достижения
```python
# utils/achievement_integration.py
self.achievements['new_achievement'] = {
    'name': 'Новое достижение',
    'description': 'Описание достижения',
    'icon': 'star',
    'category': 'learning',
    'requirement_type': 'new_requirement',
    'requirement_value': 10,
    'badge_color': 'primary'
}
```

#### 2. Создание проверки
```python
def check_new_achievement(self, user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Ваша логика проверки
        if condition_met:
            achievement = Achievement.query.filter_by(
                requirement_type='new_requirement',
                requirement_value=10
            ).first()
            
            if achievement:
                return self._award_achievement(user, achievement)
        
        return False
    except Exception as e:
        print(f"Error checking new achievement: {e}")
        return False
```

#### 3. Интеграция в систему
```python
def check_all_achievements(self, user_id):
    # ... существующие проверки ...
    if self.check_new_achievement(user_id):
        awarded = True
    return awarded
```

### Добавление новых типов уведомлений

#### 1. Создание шаблона
```python
# utils/notification_system.py
'new_notification': {
    'subject': 'Новое уведомление - {{title}}',
    'template': '''
    <div style="font-family: Arial, sans-serif;">
        <h1>{{title}}</h1>
        <p>{{message}}</p>
    </div>
    '''
}
```

#### 2. Создание метода отправки
```python
def send_new_notification(self, user_id, title, message):
    context = {
        'title': title,
        'message': message
    }
    return self.send_email_notification(user_id, 'new_notification', context)
```

### Добавление новых типов экспорта

#### 1. Создание метода экспорта
```python
# utils/export_system.py
def export_to_new_format(self, plan_id, user_id):
    try:
        plan = PersonalLearningPlan.query.get(plan_id)
        if not plan or plan.user_id != user_id:
            return None
        
        # Ваша логика экспорта
        content = self._generate_new_format_content(plan)
        return content
        
    except Exception as e:
        print(f"Error exporting to new format: {e}")
        return None
```

#### 2. Добавление маршрута
```python
# routes/export_routes.py
@export_bp.route('/export-plan/<int:plan_id>/new-format')
def export_plan_new_format(plan_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from utils.export_system import exporter
        content = exporter.export_to_new_format(plan_id, current_user.id)
        
        if not content:
            return jsonify({'error': 'Export failed'}), 404
        
        response = make_response(content)
        response.headers['Content-Type'] = 'application/new-format'
        response.headers['Content-Disposition'] = f'attachment; filename=plan_{plan_id}.new'
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'Export failed'}), 500
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
python3 test_all_features.py

# Веб-интерфейс
python3 test_browser_interface.py

# Достижения
python3 test_achievement_integration.py

# Создание тестовых данных
python3 create_test_diagnostic.py
```

### Создание новых тестов
```python
# test_new_feature.py
def test_new_feature():
    with app.test_client() as client:
        # Тестируйте вашу функцию
        response = client.post('/api/new-feature', 
                             json={'test': 'data'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
```

## 🔍 Отладка

### Логирование
```python
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Использование
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Отладка в браузере
```javascript
// Включите отладку
console.log('Debug message');
console.error('Error message');

// Проверка данных
console.log('User data:', userData);
console.log('Plan data:', planData);
```

### Отладка API
```bash
# Тестирование API с curl
curl -X POST http://localhost:5000/api/new-feature \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 📊 Мониторинг

### Ключевые метрики
- Количество созданных планов
- Процент завершенных занятий
- Время отклика API
- Количество ошибок

### Логи для мониторинга
```python
# Логирование важных событий
current_app.logger.info(f"Plan created: {plan_id}")
current_app.logger.error(f"Export failed: {error}")
current_app.logger.warning(f"User inactive: {user_id}")
```

## 🚀 Деплой

### Продакшн настройки
```python
# config.py
class ProductionConfig:
    DEBUG = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
```

### Переменные окружения
```bash
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-password"
export FLASK_ENV="production"
```

## 🤝 Вклад в проект

### Git workflow
```bash
# Создайте ветку для новой функции
git checkout -b feature/new-feature

# Внесите изменения
git add .
git commit -m "Add new feature"

# Отправьте изменения
git push origin feature/new-feature

# Создайте Pull Request
```

### Стандарты кода
- **Python**: PEP 8
- **JavaScript**: ESLint
- **HTML**: W3C Validator
- **CSS**: Stylelint

### Комментарии
```python
def complex_function(param1, param2):
    """
    Краткое описание функции.
    
    Args:
        param1: Описание параметра 1
        param2: Описание параметра 2
    
    Returns:
        Описание возвращаемого значения
    
    Raises:
        ValueError: Когда что-то идет не так
    """
    # Ваш код здесь
    pass
```

## 📚 Ресурсы

### Документация
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FullCalendar Documentation](https://fullcalendar.io/docs)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)

### Полезные инструменты
- **Postman**: Тестирование API
- **Chrome DevTools**: Отладка frontend
- **SQLite Browser**: Просмотр базы данных
- **GitKraken**: Git GUI

---

**Удачной разработки! 🚀** 