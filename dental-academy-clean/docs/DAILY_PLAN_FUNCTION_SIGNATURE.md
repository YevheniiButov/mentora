# 📋 Сигнатура функции `generate_daily_plan()`

## 🔧 Функция

```python
def generate_daily_plan(self, user_id: int, target_minutes: int = 30) -> Dict:
```

## 📥 Параметры

### `user_id: int`
- **Тип**: `int`
- **Описание**: ID пользователя в системе
- **Обязательный**: Да
- **Пример**: `6`

### `target_minutes: int = 30`
- **Тип**: `int`
- **Описание**: Целевое время обучения в минутах
- **Обязательный**: Нет (по умолчанию 30)
- **Пример**: `45`

## 📤 Возвращаемое значение

### Тип: `Dict`

### Структура успешного ответа:

```python
{
    'success': True,
    'user_id': int,
    'generated_at': str,  # ISO формат времени
    'target_minutes': int,
    'total_estimated_time': int,
    'abilities': Dict[str, float],
    'weak_domains': List[str],
    'domain_priorities': Dict[str, float],
    'daily_plan': {
        'theory_section': {
            'title': str,
            'icon': str,
            'estimated_time': int,
            'items': List[Dict]
        },
        'practice_section': {
            'title': str,
            'icon': str,
            'estimated_time': int,
            'items': List[Dict]
        },
        'review_section': {
            'title': str,
            'icon': str,
            'estimated_time': int,
            'items': List[Dict]
        }
    }
}
```

### Структура ошибки:

```python
{
    'success': False,
    'error': str,
    'daily_plan': Dict  # Fallback план
}
```

## 📊 Детальная структура данных

### 1. Основные поля

| Поле | Тип | Описание |
|------|-----|----------|
| `success` | `bool` | Успешность генерации плана |
| `user_id` | `int` | ID пользователя |
| `generated_at` | `str` | Время генерации (ISO формат) |
| `target_minutes` | `int` | Целевое время обучения |
| `total_estimated_time` | `int` | Общее расчетное время |
| `abilities` | `Dict[str, float]` | Способности по доменам |
| `weak_domains` | `List[str]` | Список слабых доменов |
| `domain_priorities` | `Dict[str, float]` | Приоритеты доменов |

### 2. Структура `daily_plan`

#### `theory_section`
```python
{
    'title': 'Теория',
    'icon': 'bi bi-book',
    'estimated_time': int,  # минуты
    'items': [
        {
            'id': int,
            'type': 'lesson',
            'title': str,
            'domain': str,
            'difficulty': int,  # 0-100
            'estimated_time': int,  # минуты
            'content': str  # краткое описание
        }
    ]
}
```

#### `practice_section`
```python
{
    'title': 'Практика',
    'icon': 'bi bi-pencil-square',
    'estimated_time': int,  # минуты
    'items': [
        {
            'id': int,
            'type': 'question',
            'title': str,
            'domain': str,
            'difficulty': int,  # 0-100
            'estimated_time': int,  # минуты
            'question_text': str,  # текст вопроса
            'options': List[str]  # варианты ответов
        }
    ]
}
```

#### `review_section`
```python
{
    'title': 'Повторение',
    'icon': 'bi bi-arrow-clockwise',
    'estimated_time': int,  # минуты
    'items': [
        {
            'content_id': int,
            'content_type': 'question',
            'domain': str,
            'overdue_days': int,  # дней просрочено
            'ease_factor': float,  # SM-2 параметр
            'repetitions': int,  # количество повторений
            'title': str,
            'estimated_time': int  # минуты
        }
    ]
}
```

### 3. Структура `abilities`

```python
{
    'THER': 0.75,    # Терапевтическая стоматология
    'SURG': 0.60,    # Хирургическая стоматология
    'ORTH': 0.45,    # Ортодонтия
    'PEDO': 0.80,    # Детская стоматология
    'PERI': 0.65,    # Пародонтология
    'ENDO': 0.55,    # Эндодонтия
    'RAD': 0.70,     # Рентгенология
    'ANAT': 0.85,    # Анатомия
    'PHAR': 0.50,    # Фармакология
    'COMM': 0.90     # Коммуникация
}
```

### 4. Структура `domain_priorities`

```python
{
    'THER': 0.85,    # Приоритет терапевтической стоматологии
    'SURG': 0.72,    # Приоритет хирургической стоматологии
    'ORTH': 0.65,    # Приоритет ортодонтии
    # ... другие домены
}
```

## 🔍 Пример использования

```python
from utils.daily_learning_algorithm import DailyLearningAlgorithm

# Создаем алгоритм
algorithm = DailyLearningAlgorithm()

# Генерируем план на 45 минут
daily_plan = algorithm.generate_daily_plan(user_id=6, target_minutes=45)

# Проверяем успешность
if daily_plan['success']:
    print(f"План сгенерирован на {daily_plan['total_estimated_time']} минут")
    
    # Получаем секции
    theory = daily_plan['daily_plan']['theory_section']
    practice = daily_plan['daily_plan']['practice_section']
    review = daily_plan['daily_plan']['review_section']
    
    print(f"Теория: {len(theory['items'])} элементов")
    print(f"Практика: {len(practice['items'])} элементов")
    print(f"Повторение: {len(review['items'])} элементов")
else:
    print(f"Ошибка: {daily_plan['error']}")
```

## ⚠️ Обработка ошибок

Функция обрабатывает следующие ошибки:
- Пользователь не найден
- Ошибки базы данных
- Ошибки анализа способностей
- Ошибки выбора контента

При любой ошибке возвращается fallback план с пустыми секциями.

## 🔧 Алгоритм работы

1. **Анализ способностей** - анализ текущих IRT способностей пользователя
2. **Определение слабых доменов** - выявление доменов с низкими показателями
3. **Поиск просроченных повторений** - элементы Spaced Repetition готовые к повторению
4. **Расчет приоритетов** - определение приоритетов доменов
5. **Распределение времени** - распределение времени по приоритетам
6. **Выбор контента** - подбор оптимального контента для каждого домена
7. **Форматирование** - форматирование для отображения в Learning Map 