# Система автоматических напоминаний о переоценке

## 📋 Обзор

Система автоматических напоминаний о переоценке обеспечивает регулярное обновление планов обучения на основе актуальных результатов диагностики. Каждые 14 дней пользователи получают уведомление о необходимости пройти переоценку для поддержания актуальности их персонального плана обучения.

## 🏗️ Архитектура

### Модель данных

#### PersonalLearningPlan
```python
# Новые поля для системы переоценки
next_diagnostic_date = db.Column(db.Date, nullable=True)  # Дата следующей переоценки
diagnostic_reminder_sent = db.Column(db.Boolean, default=False)  # Флаг отправки напоминания
```

### Основные компоненты

1. **Модель данных** - расширение `PersonalLearningPlan`
2. **Роуты переоценки** - `/big-diagnostic/reassessment/<plan_id>`
3. **Алгоритм ежедневного плана** - проверка даты переоценки
4. **Dashboard уведомления** - визуальные напоминания
5. **Автоматическое обновление планов** - после завершения переоценки

## 🔄 Workflow

### 1. Создание плана обучения
```python
# При создании плана устанавливается дата следующей переоценки
plan.next_diagnostic_date = date.today() + timedelta(days=14)
plan.diagnostic_reminder_sent = False
```

### 2. Проверка необходимости переоценки
```python
# В DailyLearningAlgorithm.generate_daily_plan()
if active_plan.next_diagnostic_date <= today:
    return {
        'success': False,
        'requires_reassessment': True,
        'plan_id': active_plan.id,
        'redirect_url': f'/big-diagnostic/reassessment/{active_plan.id}'
    }
```

### 3. Уведомление на Dashboard
```html
<!-- Показывается если reassessment_needed = True -->
<div class="reassessment-notification">
    <div class="notification-content">
        <div class="notification-icon">
            <i class="bi bi-clipboard-data"></i>
        </div>
        <div class="notification-text">
            <h4>Время для переоценки!</h4>
            <p>Прошло 14 дней с последней диагностики...</p>
        </div>
        <div class="notification-action">
            <a href="/big-diagnostic/reassessment/{{ active_plan.id }}" class="btn btn-primary">
                Пройти переоценку
            </a>
        </div>
    </div>
</div>
```

### 4. Запуск переоценки
```python
@diagnostic_bp.route('/reassessment/<int:plan_id>')
def start_reassessment(plan_id):
    # Создает новую диагностическую сессию типа 'reassessment'
    diagnostic_session = DiagnosticSession.create_session(
        user_id=current_user.id,
        session_type='reassessment',
        ip_address=request.remote_addr
    )
    
    # Обновляет план с новой сессией
    plan.diagnostic_session_id = diagnostic_session.id
    plan.diagnostic_reminder_sent = False
```

### 5. Обновление плана после переоценки
```python
# В show_results() для session_type == 'reassessment'
if diagnostic_session.session_type == 'reassessment':
    # Обновляем план с новыми результатами
    active_plan.current_ability = results['final_ability']
    active_plan.set_domain_analysis(results['domain_abilities'])
    active_plan.set_weak_domains(results['weak_domains'])
    active_plan.set_strong_domains(results['strong_domains'])
    
    # Устанавливаем новую дату переоценки
    active_plan.next_diagnostic_date = date.today() + timedelta(days=14)
    active_plan.diagnostic_reminder_sent = False
```

## 🎯 Функциональность

### Автоматические напоминания
- **Периодичность**: каждые 14 дней
- **Триггер**: `next_diagnostic_date <= today`
- **Уведомления**: на dashboard и в learning map

### Блокировка генерации задач
- Если переоценка просрочена, новые задачи не генерируются
- Показывается только сообщение о необходимости переоценки
- Редирект на страницу переоценки

### Обновление планов
- Автоматическое обновление `current_ability`
- Обновление `weak_domains` и `strong_domains`
- Сброс даты следующей переоценки

## 📁 Файлы

### Модели
- `models.py` - расширение `PersonalLearningPlan`

### Роуты
- `routes/diagnostic_routes.py` - роут `/reassessment/<plan_id>`
- `routes/dashboard_routes.py` - проверка `reassessment_needed`
- `routes/learning_routes_new.py` - обработка ошибок переоценки

### Алгоритмы
- `utils/daily_learning_algorithm.py` - проверка даты переоценки

### Шаблоны
- `templates/dashboard/enhanced_index.html` - уведомление о переоценке
- `static/css/pages/enhanced_dashboard.css` - стили уведомления

### Миграции
- `migrations/versions/add_diagnostic_reassessment_fields.py`

### Скрипты
- `scripts/update_existing_plans_reassessment.py` - обновление существующих планов

## 🚀 Развертывание

### 1. Применение миграции
```bash
flask db upgrade
```

### 2. Обновление существующих планов
```bash
python3 scripts/update_existing_plans_reassessment.py
```

### 3. Проверка работы
- Создать план обучения
- Установить `next_diagnostic_date` в прошлое
- Проверить уведомление на dashboard
- Протестировать переоценку

## 🔧 Конфигурация

### Настройка периода переоценки
```python
# В routes/diagnostic_routes.py и utils/learning_plan_generator.py
REASSESSMENT_DAYS = 14  # Период между переоценками в днях
```

### Настройка уведомлений
```css
/* В static/css/pages/enhanced_dashboard.css */
.reassessment-notification {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    /* Стили уведомления */
}
```

## 📊 Мониторинг

### Проверка планов с просроченной переоценкой
```python
overdue_plans = PersonalLearningPlan.query.filter(
    PersonalLearningPlan.status == 'active',
    PersonalLearningPlan.next_diagnostic_date <= date.today()
).all()
```

### Статистика переоценок
- Количество планов с просроченной переоценкой
- Частота прохождения переоценок
- Влияние переоценок на прогресс обучения

## 🐛 Отладка

### Логи
```python
logger.info(f"Reassessment started for plan {plan_id}")
logger.error(f"Error in reassessment: {e}")
```

### Проверка состояния
```python
# Проверка даты переоценки
if plan.next_diagnostic_date:
    days_until_reassessment = (plan.next_diagnostic_date - date.today()).days
    print(f"Days until reassessment: {days_until_reassessment}")
```

## 🔮 Будущие улучшения

1. **Email уведомления** - отправка напоминаний на email
2. **Настраиваемый период** - возможность изменения периода переоценки
3. **Аналитика переоценок** - отслеживание прогресса между переоценками
4. **Автоматическая переоценка** - упрощенная версия для быстрой проверки
5. **Интеграция с календарем** - планирование переоценок

## 📝 Версия

**Версия**: 1.0  
**Дата**: 2025-01-27  
**Автор**: AI Assistant 