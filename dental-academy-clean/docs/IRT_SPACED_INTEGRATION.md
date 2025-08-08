# Интеграция IRT + Spaced Repetition

## Обзор

Интеграция IRT (Item Response Theory) и Spaced Repetition - это ключевая технология системы адаптивного обучения Mentora. Эта интеграция обеспечивает максимальную эффективность обучения, сочетая точную диагностику способностей с оптимальным планированием повторений.

## Архитектура интеграции

### Основные компоненты

1. **IRTSpacedIntegration** - главный класс интеграции
2. **IRTSpacedItem** - интегрированный элемент данных
3. **API роуты** - REST API для работы с системой
4. **DailyLearningAlgorithm** - обновленный алгоритм с интеграцией

### Принципы работы

1. **IRT определяет базовую сложность и способности**
2. **Spaced Repetition адаптирует интервалы на основе IRT данных**
3. **Обратная связь обновляет как IRT способности, так и SR интервалы**

## Ключевые файлы

### `utils/irt_spaced_integration.py`
Основной модуль интеграции, содержащий:
- `IRTSpacedIntegration` - главный класс
- `IRTSpacedItem` - структура данных
- Алгоритмы интеграции IRT + SM-2

### `routes/irt_spaced_routes.py`
API роуты для работы с интеграцией:
- `/irt-spaced/review-schedule` - расписание повторений
- `/irt-spaced/process-review` - обработка ответов
- `/irt-spaced/adaptive-plan` - адаптивный план
- `/irt-spaced/user-insights` - пользовательские инсайты
- `/irt-spaced/statistics` - статистика

### `utils/daily_learning_algorithm.py`
Обновленный алгоритм с интеграцией IRT + SR

## API Endpoints

### 1. Получение расписания повторений
```http
GET /irt-spaced/review-schedule?domain=THER&max_items=20
```

**Ответ:**
```json
{
  "success": true,
  "review_items": [
    {
      "id": 123,
      "question_text": "Текст вопроса...",
      "domain": "THER",
      "irt_difficulty": 1.5,
      "user_ability": 0.8,
      "confidence_level": 0.75,
      "learning_rate": 1.2,
      "repetitions": 3,
      "quality": 4,
      "next_review": "2025-08-10T10:00:00Z",
      "estimated_time": 3,
      "priority_score": 8.5
    }
  ],
  "total_count": 15,
  "domain": "THER",
  "max_items": 20
}
```

### 2. Обработка ответа на повторение
```http
POST /irt-spaced/process-review
Content-Type: application/json

{
  "question_id": 123,
  "quality": 4,
  "response_time": 15.5
}
```

**Ответ:**
```json
{
  "success": true,
  "result": {
    "old_interval": 1,
    "new_interval": 2,
    "ability_change": 0.05,
    "irt_adjusted_quality": 4.0,
    "confidence_level": 0.78,
    "learning_rate": 1.15,
    "next_review": "2025-08-10T10:00:00Z"
  },
  "message": "Review processed successfully"
}
```

### 3. Получение адаптивного плана
```http
GET /irt-spaced/adaptive-plan?target_minutes=30
```

**Ответ:**
```json
{
  "success": true,
  "user_id": 1,
  "target_minutes": 30,
  "current_abilities": {
    "THER": 0.75,
    "PARO": 0.45,
    "RADI": 0.60
  },
  "review_items": [...],
  "new_content": [...],
  "estimated_time": {
    "review": 12,
    "new_content": 18,
    "total": 30
  },
  "irt_insights": {
    "strongest_domain": "THER",
    "weakest_domain": "PARO",
    "overall_ability": 0.60,
    "recommendations": [
      "Рекомендуется больше практики в слабых областях"
    ]
  },
  "learning_recommendations": [
    "У вас 5 элементов готовых к повторению",
    "Рекомендуется уделить внимание доменам: PARO"
  ]
}
```

### 4. Получение пользовательских инсайтов
```http
GET /irt-spaced/user-insights
```

**Ответ:**
```json
{
  "success": true,
  "insights": {
    "strongest_domain": "THER",
    "weakest_domain": "PARO",
    "overall_ability": 0.60,
    "recommendations": [...]
  },
  "current_abilities": {
    "THER": 0.75,
    "PARO": 0.45,
    "RADI": 0.60
  },
  "review_statistics": {
    "total_items": 25,
    "due_items": 8,
    "overdue_items": 3,
    "domain_statistics": [...]
  }
}
```

### 5. Получение статистики
```http
GET /irt-spaced/statistics
```

**Ответ:**
```json
{
  "success": true,
  "review_statistics": {
    "total_items": 25,
    "due_items": 8,
    "overdue_items": 3,
    "domain_statistics": [
      {
        "domain": "THER",
        "count": 10,
        "avg_quality": 3.8,
        "avg_repetitions": 2.5
      }
    ]
  },
  "irt_statistics": {
    "overall_ability": 0.60,
    "min_ability": 0.45,
    "max_ability": 0.75,
    "domain_count": 3,
    "strongest_domain": "THER",
    "weakest_domain": "PARO",
    "domain_abilities": {...}
  },
  "overall_statistics": {
    "total_items": 25,
    "due_items": 8,
    "overall_ability": 0.60,
    "recommendations": [...],
    "last_updated": "2025-08-08T01:50:00Z"
  }
}
```

## Алгоритмы интеграции

### 1. IRT-скорректированные интервалы

```python
def _calculate_irt_adjusted_interval(self, difficulty: float, ability: float, base_interval: int) -> int:
    # Если вопрос слишком легкий для пользователя
    if ability > difficulty + 0.5:
        return int(base_interval * self.EASY_QUESTION_MULTIPLIER)  # 1.2x
    # Если вопрос слишком сложный
    elif ability < difficulty - 0.5:
        return int(base_interval * self.HARD_QUESTION_MULTIPLIER)  # 0.8x
    # Если сложность подходящая
    else:
        return base_interval
```

### 2. Уровень уверенности

```python
def _calculate_confidence_level(self, difficulty: float, ability: float, repetitions: int, quality: int) -> float:
    # Базовый уровень на основе IRT
    irt_confidence = 1.0 / (1.0 + math.exp(-(ability - difficulty)))
    
    # Корректировка на основе истории повторений
    sr_confidence = min(1.0, repetitions * 0.2 + quality * 0.1)
    
    # Взвешенное среднее
    return self.IRT_WEIGHT * irt_confidence + self.SR_WEIGHT * sr_confidence
```

### 3. Скорость обучения

```python
def _calculate_learning_rate(self, ability: float, difficulty: float, repetitions: int, quality: int) -> float:
    # Базовая скорость на основе IRT
    if ability < difficulty:
        base_rate = 1.2  # Быстрее учимся сложным вещам
    else:
        base_rate = 0.8  # Медленнее учимся легким вещам
    
    # Корректировка на основе качества ответов
    quality_factor = 1.0 + (quality - 2.5) * 0.1
    
    # Корректировка на основе количества повторений
    repetition_factor = 1.0 - repetitions * 0.05
    
    return base_rate * quality_factor * repetition_factor
```

## Интеграция с DailyLearningAlgorithm

Обновленный `DailyLearningAlgorithm` теперь использует интегрированную систему:

```python
def generate_daily_plan(self, user_id: int, target_minutes: int = 30) -> Dict:
    # Используем интегрированную систему IRT + Spaced Repetition
    try:
        irt_spaced_integration = get_irt_spaced_integration()
        integrated_plan = irt_spaced_integration.generate_adaptive_daily_plan(
            user_id, target_minutes
        )
        
        if not integrated_plan.get('success', True):
            # Fallback к старой логике
            return self._generate_legacy_plan(user_id, target_minutes, active_plan, reassessment_warning)
        
        # Форматируем план для совместимости
        return self._format_integrated_plan(integrated_plan, user, active_plan, reassessment_warning)
        
    except Exception as e:
        # Fallback к старой логике при ошибках
        return self._generate_legacy_plan(user_id, target_minutes, active_plan, reassessment_warning)
```

## Преимущества интеграции

### 1. Максимальная эффективность обучения
- IRT обеспечивает точную диагностику способностей
- Spaced Repetition оптимизирует интервалы повторений
- Интеграция объединяет лучшие стороны обеих технологий

### 2. Персонализация
- Каждый пользователь получает уникальный план
- Система адаптируется к индивидуальным особенностям
- Динамическая корректировка на основе прогресса

### 3. Научная обоснованность
- IRT основан на психометрических принципах
- SM-2 алгоритм проверен десятилетиями исследований
- Интеграция использует современные подходы к адаптивному обучению

### 4. Конкурентное преимущество
- Уникальная комбинация технологий
- Отсутствие аналогов на рынке
- Высокая эффективность обучения

## Тестирование

### Запуск тестов
```bash
# Тест интеграции
python3 test_irt_spaced_integration.py

# Тест API
python3 test_api_integration.py
```

### Проверка работоспособности
1. Запустить сервер: `PORT=5001 python3 app.py`
2. Запустить тесты API
3. Проверить логи на наличие ошибок

## Будущие улучшения

### 1. Машинное обучение
- Использование ML для оптимизации параметров
- Предсказание успешности обучения
- Адаптивная корректировка алгоритмов

### 2. Расширенная аналитика
- Детальная статистика по доменам
- Прогресс-трекинг
- Рекомендации по обучению

### 3. Интеграция с внешними системами
- Экспорт данных для анализа
- API для внешних приложений
- Интеграция с LMS

## Заключение

Интеграция IRT + Spaced Repetition представляет собой мощную технологию адаптивного обучения, которая:

1. **Максимизирует эффективность** обучения за счет точной диагностики и оптимального планирования
2. **Обеспечивает персонализацию** для каждого пользователя
3. **Создает конкурентное преимущество** благодаря уникальной комбинации технологий
4. **Основана на научных принципах** психометрии и когнитивной науки

Эта интеграция является сердцем системы адаптивного обучения Mentora и обеспечивает максимальную эффективность образовательного процесса. 