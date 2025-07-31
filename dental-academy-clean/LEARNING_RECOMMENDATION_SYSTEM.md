# Система рекомендаций обучения для BIT экзаменов

## Обзор

Система рекомендаций обучения - это интеллектуальная система, которая анализирует результаты тестирования студентов и автоматически генерирует персонализированные планы обучения на основе доступных карточек из всех папок проекта.

## Архитектура системы

### 1. Маппинг доменов (`cards/domain_mapping.json`)

Центральный файл, который сопоставляет все карточки из разных папок с доменами BIT экзаменов:

```json
{
  "domain_mapping": {
    "Praktische vaardigheden": {
      "description": "Практические навыки стоматолога",
      "weight": 15,
      "priority": "high",
      "card_sources": {
        "bit_exam": {
          "files": ["praktische_vaardigheden_cards.json"],
          "card_count": 40,
          "topics": ["Simodont техники", "Kroonpreparatie", ...]
        },
        "caries": {
          "files": ["learning_cards.json", "tests.json"],
          "relevant_tags": ["Cariology", "Restorative-Dentistry"],
          "topics": ["Cariës behandeling", "Restauratie technieken"]
        }
      }
    }
  }
}
```

### 2. Движок рекомендаций (`utils/learning_recommendation_engine.py`)

Основной движок, который:
- Анализирует результаты тестирования
- Определяет слабые и сильные области
- Генерирует персонализированные рекомендации
- Создает планы обучения

### 3. API маршруты (`routes/learning_recommendation_routes.py`)

Flask маршруты для:
- Генерации рекомендаций
- Получения сохраненных рекомендаций
- Экспорта планов обучения
- Управления прогрессом обучения

### 4. Веб-интерфейс (`templates/learning/recommendations.html`)

Интерактивная страница для:
- Просмотра рекомендаций
- Симуляции тестирования
- Экспорта планов
- Отслеживания прогресса

## Алгоритм работы

### Шаг 1: Анализ результатов тестирования

```python
def analyze_test_results(test_results):
    # Вычисление общего балла
    overall_score = sum(result.score for result in test_results) / len(test_results)
    
    # Определение слабых и сильных областей
    weak_domains = [result.domain for result in test_results if result.score < 60]
    strong_domains = [result.domain for result in test_results if result.score >= 90]
    
    return analysis
```

### Шаг 2: Приоритизация рекомендаций

Система приоритизирует рекомендации по следующему алгоритму:

1. **Слабые области с высоким приоритетом** (например, Praktische vaardigheden с весом 15%)
2. **Слабые области со средним приоритетом** (например, Prothetiek en tandtechniek с весом 4%)
3. **Слабые области с низким приоритетом** (например, Anatomie en fysiologie с весом 0.4%)

### Шаг 3: Определение количества карточек

Количество рекомендуемых карточек зависит от уровня производительности:

- **Poor (0-59%)**: Все карточки домена (до 100)
- **Fair (60-74%)**: 50% карточек домена
- **Good (75-89%)**: 25% карточек домена
- **Excellent (90-100%)**: 10% карточек домена (только сложные)

### Шаг 4: Оценка времени обучения

```python
def estimate_learning_time(card_count, performance_level):
    base_time_per_card = 2  # минуты на карточку
    
    multipliers = {
        'poor': 1.5,      # Больше времени для слабых областей
        'fair': 1.2,
        'good': 1.0,
        'excellent': 0.8  # Меньше времени для сильных областей
    }
    
    return int(card_count * base_time_per_card * multipliers[performance_level])
```

## Интеграция с существующими карточками

### Поддерживаемые источники карточек

1. **bit_exam/** - Карточки для BIT экзаменов (358 карточек)
2. **caries/** - Карточки по кариесу
3. **anatomy/** - Карточки по анатомии
4. **endodontic/** - Карточки по эндодонтии
5. **pediatric/** - Карточки по детской стоматологии
6. **periodontic/** - Карточки по пародонтологии
7. **saliva/** - Карточки по слюне и оральным жидкостям
8. **methodology/** - Карточки по методологии
9. **statistics/** - Карточки по статистике
10. **virtual_patient/** - Виртуальные пациенты

### Сопоставление по тегам

Система использует теги для сопоставления карточек с доменами:

```json
{
  "relevant_tags": [
    "Cariology",
    "Restorative-Dentistry", 
    "Preventive-Dentistry-Hygiene",
    "Endodontics-Diagnosis-Pulp",
    "Anatomy-Head-Neck",
    "Periodontology-Diagnosis-Diseases"
  ]
}
```

## API Endpoints

### 1. Генерация рекомендаций

```http
POST /api/generate-recommendations
Content-Type: application/json

{
  "test_results": [
    {
      "domain": "Praktische vaardigheden",
      "score": 45.0,
      "total_questions": 20,
      "correct_answers": 9,
      "time_spent": 30
    }
  ]
}
```

### 2. Получение рекомендаций

```http
GET /api/get-recommendations
```

### 3. Экспорт плана обучения

```http
POST /api/export-learning-plan
Content-Type: application/json

{
  "format": "json"
}
```

### 4. Симуляция тестирования

```http
GET /api/simulate-test-results
```

## Пример использования

### 1. Запуск движка

```python
from utils.learning_recommendation_engine import LearningRecommendationEngine, TestResult

# Создание движка
engine = LearningRecommendationEngine()

# Результаты тестирования
test_results = [
    TestResult("Praktische vaardigheden", 45.0, 20, 9, 30),
    TestResult("Behandelplanning", 75.0, 15, 11, 25),
    TestResult("Farmacologie", 30.0, 18, 5, 35)
]

# Генерация отчета
report = engine.generate_personalized_report(test_results)
```

### 2. Результат

```json
{
  "test_summary": {
    "overall_score": 50.0,
    "performance_level": "poor",
    "weak_domains_count": 2,
    "strong_domains_count": 0
  },
  "learning_recommendations": [
    {
      "domain": "Praktische vaardigheden",
      "priority": "high",
      "weight": 15.0,
      "card_count": 100,
      "estimated_time_minutes": 300,
      "difficulty_level": "easy",
      "card_sources": ["bit_exam", "caries", "endodontic"],
      "topics": ["Simodont техники", "Kroonpreparatie", "Cariës behandeling"]
    }
  ],
  "study_plan": {
    "total_estimated_time": 450,
    "priority_order": ["Praktische vaardigheden", "Farmacologie"],
    "focus_areas": ["Praktische vaardigheden", "Farmacologie"]
  }
}
```

## Преимущества системы

### 1. Персонализация
- Адаптация к индивидуальным результатам тестирования
- Учет приоритетов и весов доменов
- Динамическое определение сложности

### 2. Интеграция
- Использование всех доступных карточек
- Сопоставление по тегам и темам
- Единая система рекомендаций

### 3. Масштабируемость
- Легкое добавление новых доменов
- Поддержка новых источников карточек
- Гибкая система приоритизации

### 4. Аналитика
- Детальный анализ по доменам
- Оценка времени обучения
- Отслеживание прогресса

## Расширение системы

### Добавление нового домена

1. Добавить домен в `domain_mapping.json`:
```json
{
  "Nieuwe Domein": {
    "description": "Описание нового домена",
    "weight": 5,
    "priority": "medium",
    "card_sources": {
      "nieuwe_bron": {
        "files": ["nieuwe_cards.json"],
        "topics": ["Nieuwe onderwerpen"]
      }
    }
  }
}
```

### Добавление нового источника карточек

1. Создать папку с карточками
2. Добавить источник в соответствующие домены
3. Указать теги для сопоставления

### Настройка алгоритма

Можно настроить:
- Пороги производительности
- Множители времени обучения
- Правила приоритизации
- Количество рекомендуемых карточек

## Мониторинг и аналитика

### Метрики системы

1. **Точность рекомендаций**: Соответствие рекомендаций улучшению результатов
2. **Время обучения**: Фактическое время vs. оценка
3. **Завершаемость**: Процент студентов, завершивших рекомендованные карточки
4. **Улучшение результатов**: Изменение баллов после обучения

### Логирование

Система ведет логи:
- Генерация рекомендаций
- Использование карточек
- Прогресс обучения
- Ошибки и исключения

## Заключение

Система рекомендаций обучения представляет собой мощный инструмент для персонализации образовательного процесса. Она интегрирует все доступные карточки, анализирует результаты тестирования и создает индивидуальные планы обучения, что значительно повышает эффективность подготовки к BIT экзаменам.

Система легко расширяется и может быть адаптирована для других образовательных контекстов в стоматологии. 