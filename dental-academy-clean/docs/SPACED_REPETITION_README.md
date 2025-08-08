# Система Spaced Repetition с SM-2 алгоритмом

## Обзор

Реализована полноценная система интервального повторения на основе SM-2 алгоритма с интеграцией IRT (Item Response Theory) для оптимизации обучения.

## Основные компоненты

### 1. Модель SpacedRepetitionItem

```python
class SpacedRepetitionItem(db.Model):
    """Модель для элементов системы интервального повторения (SM-2 алгоритм)"""
    
    # SM-2 параметры
    ease_factor = db.Column(db.Float, default=2.5)  # Фактор легкости (1.3 - 2.5)
    interval = db.Column(db.Integer, default=1)     # Интервал в днях
    repetitions = db.Column(db.Integer, default=0)  # Количество повторений
    
    # Качество ответов (0-5)
    quality = db.Column(db.Integer, default=0)      # Последнее качество ответа
    average_quality = db.Column(db.Float, default=0.0)  # Среднее качество
    
    # Временные метки
    next_review = db.Column(db.DateTime, nullable=False)
    last_review = db.Column(db.DateTime, nullable=True)
    
    # Дополнительные данные
    domain = db.Column(db.String(50), nullable=True, index=True)
    total_reviews = db.Column(db.Integer, default=0)
    consecutive_correct = db.Column(db.Integer, default=0)
    consecutive_incorrect = db.Column(db.Integer, default=0)
    
    # IRT данные
    irt_difficulty = db.Column(db.Float, nullable=True)
    user_ability = db.Column(db.Float, nullable=True)
```

### 2. SM-2 Алгоритм

Алгоритм SM-2 автоматически корректирует интервалы повторения на основе качества ответов:

- **Качество 0-2**: Неправильный ответ → интервал = 1 день
- **Качество 3-5**: Правильный ответ → интервал увеличивается по формуле SM-2

#### Формула SM-2:

```python
def _apply_sm2_algorithm(self, quality: int):
    # Обновляем фактор легкости
    if quality >= 3:  # Правильный ответ
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    else:  # Неправильный ответ
        self.ease_factor = max(1.3, self.ease_factor - 0.2)
    
    # Обновляем количество повторений
    if quality >= 3:
        self.repetitions += 1
    else:
        self.repetitions = 0
    
    # Рассчитываем новый интервал
    if self.repetitions == 0:
        self.interval = 1
    elif self.repetitions == 1:
        self.interval = 6
    else:
        self.interval = int(self.interval * self.ease_factor)
```

### 3. Система еженедельной корректировки

```python
class SimpleWeeklyAdjustment:
    """Система еженедельной корректировки плана обучения"""
    
    def analyze_weekly_progress(self, user_id: int) -> Dict:
        # Анализирует прогресс за последние 7 дней
        # Сравнивает фактический прогресс с запланированным
        # Генерирует рекомендации по корректировке
    
    def adjust_plan(self, user_id: int, adjustment_type: str) -> Dict:
        # Корректирует план обучения:
        # - increase: увеличивает нагрузку на 20%
        # - decrease: уменьшает нагрузку на 20%
        # - maintain: оставляет без изменений
```

### 4. Дашборд с прогрессом

```python
class SimpleStudentDashboard:
    """Дашборд для студента с прогрессом обучения"""
    
    def get_dashboard(self, user_id: int) -> Dict:
        # Возвращает полную картину обучения:
        # - Общая статистика за 30 дней
        # - Недавняя активность за 7 дней
        # - Обзор повторений
        # - Прогресс по доменам
        # - Быстрые действия
        # - Достижения
```

## API Endpoints

### Spaced Repetition

#### POST `/api/simple-learning/spaced-repetition/calculate`
Расчет следующего повторения с SM-2 алгоритмом.

**Параметры:**
```json
{
    "question_id": 1,
    "quality": 5,  // 0-5
    "user_ability": 0.5  // опционально
}
```

**Ответ:**
```json
{
    "success": true,
    "next_review": "2024-01-16T10:00:00Z",
    "interval": 6,
    "ease_factor": 2.5,
    "repetitions": 1,
    "quality": 5,
    "reason": "Второе повторение (через 6 дней)",
    "total_reviews": 1,
    "average_quality": 5.0
}
```

#### GET `/api/simple-learning/spaced-repetition/due-reviews`
Получение вопросов, готовых к повторению.

#### GET `/api/simple-learning/spaced-repetition/statistics`
Получение статистики повторений.

### Weekly Adjustment

#### GET `/api/simple-learning/weekly-adjustment/analyze`
Анализ еженедельного прогресса.

#### POST `/api/simple-learning/weekly-adjustment/adjust`
Корректировка плана обучения.

### Dashboard

#### GET `/api/simple-learning/dashboard`
Получение основного дашборда.

#### GET `/api/simple-learning/dashboard/progress-chart`
Получение данных для графика прогресса.

## Примеры использования

### 1. Ответ на вопрос

```python
# Пользователь отвечает на вопрос
response = requests.post("/api/simple-learning/spaced-repetition/calculate", json={
    "question_id": 123,
    "quality": 4  # Хороший ответ
})

# Система рассчитывает следующее повторение
result = response.json()
print(f"Следующее повторение через {result['interval']} дней")
```

### 2. Получение вопросов для повторения

```python
# Получаем вопросы, готовые к повторению
response = requests.get("/api/simple-learning/spaced-repetition/due-reviews")
due_reviews = response.json()['due_reviews']

for review in due_reviews:
    print(f"Вопрос {review['question_id']}: {review['question']['text']}")
```

### 3. Анализ прогресса

```python
# Анализируем еженедельный прогресс
response = requests.get("/api/simple-learning/weekly-adjustment/analyze")
analysis = response.json()

if analysis['progress_analysis']['status'] == 'behind':
    # Пользователь отстает от плана
    print("Рекомендуется увеличить время обучения")
```

## Преимущества системы

### 1. Научно обоснованный подход
- SM-2 алгоритм основан на исследованиях памяти
- Автоматическая адаптация к индивидуальным особенностям

### 2. Интеграция с IRT
- Учитывает сложность вопросов
- Корректирует интервалы на основе способностей пользователя

### 3. Адаптивное планирование
- Еженедельная корректировка планов
- Персонализированные рекомендации

### 4. Подробная аналитика
- Статистика по доменам
- Графики прогресса
- Отслеживание серий обучения

## Тестирование

Запустите тестовый скрипт:

```bash
python test_spaced_repetition_system.py
```

Скрипт проверит:
- Расчет повторений с разным качеством ответов
- Получение статистики
- Работу дашборда
- Еженедельную корректировку
- Симуляцию обучения вопроса

## Миграция базы данных

Система включает миграцию для создания таблицы `spaced_repetition_item`:

```bash
flask db upgrade spaced_repetition_001
```

## Настройка

Основные параметры можно настроить в классах:

```python
# SimpleSpacedRepetition
self.min_ease_factor = 1.3
self.max_ease_factor = 2.5
self.initial_ease_factor = 2.5

# SimpleWeeklyAdjustment
self.progress_threshold = 0.8  # 80% от запланированного прогресса
```

## Будущие улучшения

1. **Машинное обучение**: Использование ML для оптимизации интервалов
2. **Групповое обучение**: Анализ прогресса групп студентов
3. **Мобильные уведомления**: Push-уведомления о повторениях
4. **Интеграция с календарем**: Автоматическое планирование в календаре
5. **Геймификация**: Достижения и награды за регулярные повторения 