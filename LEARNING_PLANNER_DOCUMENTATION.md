# 🦷 Планировщик Обучения - Mentora Academy

## 📋 Обзор

Планировщик обучения - это интеллектуальная система для создания персональных планов подготовки к BIG экзамену на основе результатов IRT диагностики. Система включает в себя календарь занятий, систему уведомлений, экспорт расписания и интеграцию с достижениями.

## 🚀 Основные функции

### 1. 📅 Интеллектуальное планирование
- **Автоматическая генерация** планов на основе IRT результатов
- **Адаптивное расписание** с учетом интенсивности обучения
- **Персонализированные цели** для каждого домена
- **Динамическая корректировка** планов

### 2. 📧 Система уведомлений
- **Email уведомления** о занятиях и прогрессе
- **Browser notifications** для активных пользователей
- **Еженедельные отчеты** о достижениях
- **Напоминания о экзамене**

### 3. 📄 Экспорт данных
- **iCal экспорт** для интеграции с календарями
- **PDF отчеты** с детальной статистикой
- **Автоматическое обновление** экспортируемых данных

### 4. 🏆 Система достижений
- **10 типов достижений** для мотивации
- **Отслеживание прогресса** в реальном времени
- **Уведомления о достижениях**
- **Интеграция с планировщиком**

## 🏗️ Архитектура системы

### Структура файлов
```
dental-academy-clean/
├── templates/dashboard/
│   └── create_learning_plan.html      # Основной интерфейс
├── static/js/
│   ├── learning-plan.js               # Основная логика планировщика
│   ├── notification-system.js         # Система уведомлений
│   └── achievement-integration.js     # Интеграция с достижениями
├── utils/
│   ├── notification_system.py         # Email уведомления
│   ├── export_system.py               # Экспорт iCal/PDF
│   └── achievement_integration.py     # Система достижений
├── routes/
│   ├── dashboard_routes.py            # Основные маршруты
│   ├── export_routes.py               # Маршруты экспорта
│   └── achievement_routes.py          # API достижений
└── models.py                          # Модели данных
```

### Модели данных

#### PersonalLearningPlan
```python
class PersonalLearningPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    exam_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    intensity = db.Column(db.String(20))
    overall_progress = db.Column(db.Float)
    current_ability = db.Column(db.Float)
    status = db.Column(db.String(20))
```

#### StudySession
```python
class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('personal_learning_plan.id'))
    domain_id = db.Column(db.Integer, db.ForeignKey('big_domain.id'))
    session_type = db.Column(db.String(50))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    planned_duration = db.Column(db.Integer)
    actual_duration = db.Column(db.Integer)
    status = db.Column(db.String(20))
```

## 🔧 Установка и настройка

### 1. Зависимости
```bash
pip install reportlab  # Для PDF экспорта
```

### 2. Инициализация базы данных
```bash
flask db upgrade
```

### 3. Инициализация достижений
```python
from utils.achievement_integration import achievement_system
achievement_system.initialize_achievements()
```

### 4. Настройка email (опционально)
```python
# В config.py
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-password'
```

## 📖 Руководство пользователя

### Создание плана обучения

1. **Перейдите на страницу планировщика**
   ```
   /dashboard/create-learning-plan
   ```

2. **Заполните форму настроек**
   - Дата экзамена
   - Период обучения
   - Интенсивность (легкая/средняя/интенсивная)
   - Предпочитаемые дни
   - Время обучения

3. **Нажмите "Создать план"**
   - Система автоматически сгенерирует расписание
   - Создаст цели для каждого домена
   - Настроит уведомления

### Использование календаря

- **Просмотр занятий**: Все занятия отображаются в календаре
- **Детали занятия**: Кликните на событие для подробностей
- **Изменение вида**: Переключение между месячным/недельным видом
- **Навигация**: Кнопки "Сегодня" и "Вид"

### Экспорт данных

#### iCal экспорт
1. Нажмите "Экспорт в календарь (iCal)"
2. Файл автоматически скачается
3. Импортируйте в Google Calendar/Outlook

#### PDF отчет
1. Нажмите "Экспорт в PDF"
2. Получите детальный отчет с:
   - Информацией о пользователе
   - Статистикой прогресса
   - Анализом по доменам
   - Расписанием занятий
   - Рекомендациями

### Система достижений

#### Типы достижений
- **Планировщик**: Создание первого плана
- **Регулярность**: 7 дней подряд занятий
- **Мастер обучения**: 30 дней подряд
- **Достигатель целей**: 5 достигнутых целей
- **Готов к экзамену**: 80% готовности
- **Эксперт домена**: 90% в любом домене
- **Воин времени**: 100 часов обучения
- **Идеальная неделя**: Все занятия завершены
- **Ранняя пташка**: Утренние занятия
- **Ночная сова**: Вечерние занятия

#### Отслеживание прогресса
- Прогресс отображается в реальном времени
- Уведомления о новых достижениях
- Детальная статистика по каждому типу

## 🔌 API документация

### Маршруты планировщика

#### Создание плана
```http
POST /dashboard/create-learning-plan
Content-Type: application/json

{
  "exam_date": "2024-12-15",
  "start_date": "2024-09-01",
  "end_date": "2024-12-08",
  "intensity": "moderate",
  "study_time": "afternoon",
  "diagnostic_session_id": 1
}
```

#### Получение плана
```http
GET /dashboard/learning-plan/{plan_id}
```

#### Обновление плана
```http
POST /dashboard/update-learning-plan/{plan_id}
```

### Маршруты экспорта

#### iCal экспорт
```http
GET /export-plan/{plan_id}/ical
```

#### PDF экспорт
```http
GET /export-plan/{plan_id}/pdf
```

### API достижений

#### Получение достижений пользователя
```http
GET /api/user-achievements
```

#### Получение прогресса
```http
GET /api/achievement-progress
```

#### Проверка новых достижений
```http
POST /api/check-achievements
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Тестирование всех функций
python3 test_all_features.py

# Тестирование веб-интерфейса
python3 test_browser_interface.py

# Тестирование интеграции с достижениями
python3 test_achievement_integration.py
```

### Проверка функциональности
1. **Базовая функциональность**: Создание и управление планами
2. **Система уведомлений**: Email и browser notifications
3. **Экспорт данных**: iCal и PDF генерация
4. **Доступность**: ARIA атрибуты и семантические теги
5. **Интеграция достижений**: Система мотивации

## 🎨 Кастомизация

### CSS стили
Основные стили находятся в:
```
static/css/pages/create_learning_plan.css
```

### JavaScript функции
Основная логика в:
```
static/js/learning-plan.js
```

### Шаблоны уведомлений
Email шаблоны в:
```
utils/notification_system.py
```

## 🔒 Безопасность

### Аутентификация
- Все маршруты защищены `@login_required`
- Проверка принадлежности планов пользователю
- Валидация входных данных

### Валидация данных
- Проверка дат (экзамен не может быть в прошлом)
- Валидация интенсивности обучения
- Проверка существования диагностической сессии

## 🚀 Производительность

### Оптимизации
- Асинхронная загрузка JavaScript
- Кэширование данных пользователя
- Оптимизированные SQL запросы
- Минификация CSS/JS в продакшене

### Мониторинг
- Логирование создания планов
- Отслеживание ошибок экспорта
- Мониторинг производительности API

## 🐛 Устранение неполадок

### Частые проблемы

#### План не создается
1. Проверьте наличие диагностической сессии
2. Убедитесь в корректности дат
3. Проверьте логи приложения

#### Уведомления не отправляются
1. Проверьте настройки SMTP
2. Убедитесь в наличии email пользователя
3. Проверьте разрешения browser notifications

#### Экспорт не работает
1. Установите reportlab: `pip install reportlab`
2. Проверьте права доступа к файлам
3. Убедитесь в корректности ID плана

#### Достижения не выдаются
1. Запустите инициализацию: `achievement_system.initialize_achievements()`
2. Проверьте данные пользователя
3. Убедитесь в корректности прогресса

### Логи
```bash
# Просмотр логов приложения
tail -f logs/app.log

# Логи ошибок
grep "ERROR" logs/app.log
```

## 📈 Метрики и аналитика

### Ключевые показатели
- Количество созданных планов
- Процент завершенных занятий
- Средняя готовность к экзамену
- Количество полученных достижений
- Время, проведенное в системе

### Отчеты
- Еженедельные отчеты по активности
- Анализ эффективности планов
- Статистика по доменам
- Отслеживание прогресса пользователей

## 🔄 Обновления и версии

### Версия 1.0 (Текущая)
- ✅ Базовый планировщик
- ✅ Система уведомлений
- ✅ Экспорт данных
- ✅ Интеграция с достижениями
- ✅ ARIA доступность

### Планы на будущее
- 🔄 Интеграция с внешними календарями
- 🔄 Мобильное приложение
- 🔄 ИИ для оптимизации планов
- 🔄 Социальные функции
- 🔄 Геймификация

## 📞 Поддержка

### Контакты
- **Email**: support@mentora.academy
- **Документация**: [docs.mentora.academy](https://docs.mentora.academy)
- **GitHub**: [github.com/mentora-academy](https://github.com/mentora-academy)

### Сообщество
- **Форум**: [community.mentora.academy](https://community.mentora.academy)
- **Discord**: [discord.gg/mentora](https://discord.gg/mentora)
- **Telegram**: [t.me/mentora_academy](https://t.me/mentora_academy)

---

**© 2024 Mentora Academy. Все права защищены.**

*Документация обновлена: 15 декабря 2024* 