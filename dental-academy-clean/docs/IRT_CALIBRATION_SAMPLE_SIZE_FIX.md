# Исправление calibration_sample_size - замена placeholder на реальную логику

## Проблема

В файле `scripts/init_big_domains.py` (строка 345) использовался placeholder `calibration_sample_size=100` вместо реального расчета размера выборки для калибровки IRT параметров.

## Решение

### 1. Добавлена конфигурация через environment variables

**Файл**: `env.example` (добавлены новые переменные)

```bash
# IRT Calibration Configuration
# Minimum sample size required for reliable IRT parameter calibration
IRT_MIN_SAMPLE_SIZE=30

# Optimal sample size for high-quality IRT calibration
IRT_OPTIMAL_SAMPLE_SIZE=100

# Maximum sample size to prevent excessive computation
IRT_MAX_SAMPLE_SIZE=500

# Reliability threshold for IRT parameter quality (0.0 - 1.0)
IRT_RELIABILITY_THRESHOLD=0.8

# Confidence level for sample size calculation (0.0 - 1.0)
IRT_CONFIDENCE_LEVEL=0.95
```

### 2. Реализованы функции для расчета размера выборки

**Файл**: `scripts/init_big_domains.py` (строки 25-200)

#### `get_calibration_config()`
Загружает конфигурацию из environment variables с разумными значениями по умолчанию.

#### `calculate_required_sample_size()`
Вычисляет минимальный размер выборки для надежной калибровки на основе статистической формулы:

```python
def calculate_required_sample_size(confidence_level=0.95, margin_of_error=0.1, p=0.5):
    """
    Calculate required sample size for reliable IRT calibration
    
    Formula: n = (z_alpha^2 * p * (1-p)) / (margin_of_error^2)
    """
    from scipy import stats
    
    # Z-score for confidence level
    z_alpha = stats.norm.ppf((1 + confidence_level) / 2)
    
    # Sample size formula for proportion
    n = (z_alpha ** 2 * p * (1 - p)) / (margin_of_error ** 2)
    
    return int(np.ceil(n))
```

#### `analyze_existing_responses()`
Анализирует существующие данные ответов для определения параметров калибровки:

```python
def analyze_existing_responses():
    """
    Analyze existing response data to determine calibration parameters
    
    Returns:
        Dict with analysis results including:
        - total_responses: Общее количество ответов
        - questions_with_responses: Количество вопросов с ответами
        - avg_responses_per_question: Среднее количество ответов на вопрос
        - recommended_sample_size: Рекомендуемый размер выборки
    """
```

### 3. Добавлена валидация размера выборки

**Файл**: `scripts/init_big_domains.py` (строки 120-150)

#### `validate_sample_size()`
Проверяет достаточность размера выборки для надежной калибровки:

```python
def validate_sample_size(sample_size, config):
    """
    Validate if sample size is sufficient for reliable calibration
    
    Returns:
        Dict with validation results:
        - is_sufficient: Достаточен ли размер выборки
        - warning: Предупреждение если размер недостаточен
        - reliability: Уровень надежности (low/medium/high)
        - confidence: Уровень доверия (low/medium/high)
    """
```

### 4. Обновлена логика создания IRT параметров

**Файл**: `scripts/init_big_domains.py` (строки 340-350)

```python
# Create IRT parameters
sample_size_info = get_calibration_sample_size(question.id)
calibration_sample_size = log_calibration_info(question.id, sample_size_info)

irt_params = IRTParameters(
    question_id=question.id,
    difficulty=q_data['difficulty'],
    discrimination=q_data['discrimination'],
    guessing=q_data['guessing'],
    calibration_date=datetime.now(timezone.utc),
    calibration_sample_size=calibration_sample_size  # Реальный размер выборки
)
```

### 5. Добавлено логирование и мониторинг

**Файл**: `scripts/init_big_domains.py` (строки 180-200)

#### `log_calibration_info()`
Логирует информацию о калибровке и предупреждает о недостаточном размере выборки:

```python
def log_calibration_info(question_id, sample_size_info):
    """Log calibration information"""
    sample_size = sample_size_info['sample_size']
    validation = sample_size_info['validation']
    
    if validation['warning']:
        logger.warning(f"Question {question_id}: {validation['warning']} (reliability: {validation['reliability']})")
    else:
        logger.info(f"Question {question_id}: Sample size {sample_size} is sufficient (reliability: {validation['reliability']})")
    
    return sample_size
```

## Результат

### До изменений:
```python
calibration_sample_size=100  # Placeholder
```

### После изменений:
```python
sample_size_info = get_calibration_sample_size(question.id)
calibration_sample_size = log_calibration_info(question.id, sample_size_info)
# Реальный размер выборки на основе существующих данных
```

## Преимущества

1. **Статистическая обоснованность**: Размер выборки рассчитывается по статистическим формулам
2. **Гибкость**: Конфигурация через environment variables
3. **Валидация**: Автоматическая проверка достаточности размера выборки
4. **Мониторинг**: Логирование и предупреждения о проблемах
5. **Адаптивность**: Учет существующих данных для оптимизации

## Тестирование

Создан тестовый скрипт `scripts/test_calibration_logic.py` для проверки:

- Загрузки конфигурации
- Анализа существующих данных
- Валидации размера выборки
- Создания IRT параметров
- Производительности функций

## Использование

1. Установите environment variables в `.env` файле
2. Запустите инициализацию: `python scripts/init_big_domains.py`
3. Проверьте логи для информации о калибровке
4. При необходимости скорректируйте параметры в environment variables 