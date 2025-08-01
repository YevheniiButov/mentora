# 🦷 BI-toets Диагностическое тестирование - Руководство

## 📋 Обзор системы

Система диагностического тестирования BI-toets представляет собой профессиональную платформу для подготовки к голландскому стоматологическому лицензионному экзамену BIG. Система использует **Item Response Theory (IRT)** для адаптивного тестирования и точной оценки способностей кандидатов.

### 🎯 Основные возможности

- **Адаптивное тестирование** на основе IRT (3PL модель)
- **Точная оценка способностей** с минимальной стандартной ошибкой
- **Анализ по доменам** согласно программе ACTA 180 ECTS
- **Персональное планирование обучения** на основе результатов
- **Прогнозирование готовности** к экзамену

## 🏗️ Архитектура системы

### Модели данных

#### 1. BIGDomain
Домены BI-toets на основе программы ACTA:
- **THER** (25%) - Терапевтическая стоматология
- **SURG** (20%) - Хирургическая стоматология  
- **PROST** (15%) - Ортопедическая стоматология
- **PEDO** (10%) - Детская стоматология
- **PERIO** (10%) - Пародонтология
- **ORTHO** (8%) - Ортодонтия
- **PREV** (7%) - Профилактика
- **ETHICS** (5%) - Этика и право

#### 2. IRTParameters
Параметры 3PL модели для каждого вопроса:
- `difficulty` (b-parameter) - сложность вопроса
- `discrimination` (a-parameter) - дискриминационная способность
- `guessing` (c-parameter) - вероятность угадывания

#### 3. DiagnosticSession
Сессия адаптивного тестирования:
- Текущая оценка способностей (θ)
- Стандартная ошибка оценки
- История ответов и прогрессии способностей

#### 4. PersonalLearningPlan
Персональный план обучения:
- Анализ слабых и сильных доменов
- Расписание обучения
- Мильстоны и цели

## 🚀 Установка и настройка

### 1. Миграция базы данных

```bash
# Применить миграцию для новых моделей
flask db upgrade
```

### 2. Инициализация данных

```bash
# Создать домены и образцовые вопросы
python scripts/init_big_domains.py
```

### 3. Проверка установки

```bash
# Проверить созданные домены
flask shell
>>> from models import BIGDomain
>>> BIGDomain.query.all()
```

## 📊 Использование системы

### Запуск диагностического тестирования

1. **Перейти к диагностике:**
   ```
   /tests/big-diagnostic
   ```

2. **Начать сессию:**
   - Выбрать тип сессии (диагностическая/адаптивная)
   - Установить временные ограничения (опционально)
   - Нажать "Начать диагностику"

3. **Прохождение теста:**
   - Система автоматически выбирает следующий вопрос
   - Вопросы адаптируются к текущему уровню способностей
   - Тест завершается при достижении необходимой точности

### API Endpoints

#### Запуск диагностики
```http
POST /tests/big-diagnostic/start
Content-Type: application/json

{
  "session_type": "diagnostic",
  "test_length": null,
  "time_limit": 120
}
```

#### Получение следующего вопроса
```http
POST /tests/big-diagnostic/next-question
Content-Type: application/json

{
  "session_id": 123
}
```

#### Отправка ответа
```http
POST /tests/big-diagnostic/submit-answer
Content-Type: application/json

{
  "session_id": 123,
  "question_id": 456,
  "selected_answer": 2,
  "response_time": 45.2
}
```

#### Получение результатов
```http
GET /tests/big-diagnostic/results/123
```

#### Создание плана обучения
```http
POST /tests/learning-plan/generate
Content-Type: application/json

{
  "session_id": 123,
  "exam_date": "2024-06-15",
  "study_hours_per_week": 20
}
```

## 🔧 IRT Движок

### Принципы работы

1. **Maximum Likelihood Estimation (MLE)** для оценки способностей
2. **Maximum Information** для выбора следующего вопроса
3. **3PL модель** для расчета вероятности правильного ответа
4. **Адаптивное завершение** при достижении точности SE ≤ 0.3

### Ключевые функции

#### Оценка способностей
```python
from utils.irt_engine import IRTEngine

irt_engine = IRTEngine()
theta, se = irt_engine.estimate_ability(responses)
```

#### Выбор следующего вопроса
```python
next_question = irt_engine.select_next_question(session, available_questions)
```

#### Обновление сессии
```python
result = irt_engine.update_session_ability(session, question, is_correct)
```

## 📈 Анализ результатов

### Показатели готовности

- **Общая способность (θ)**: -3.0 до +3.0
- **Стандартная ошибка**: Чем меньше, тем точнее оценка
- **Готовность к экзамену**: 0-100% вероятность сдачи
- **Уровень уверенности**: низкий/средний/высокий

### Анализ по доменам

Система предоставляет детальный анализ по каждому домену:
- Точность ответов
- Средняя сложность вопросов
- Оценка способностей в домене
- Рекомендации по улучшению

### Слабые и сильные стороны

Автоматическое выявление:
- **Слабых доменов**: θ < 0.2 (требуют внимания)
- **Сильных доменов**: θ > 0.8 (можно поддерживать)

## 📅 Персональное планирование

### Генерация плана

1. **Анализ результатов диагностики**
2. **Выявление приоритетных доменов**
3. **Создание недельного расписания**
4. **Установка мильстонов**

### Структура плана

```json
{
  "weekly_hours": 20,
  "weeks": [
    {
      "week_number": 1,
      "focus_domain": "THER",
      "domain_name": "Терапевтическая стоматология",
      "hours": 20,
      "topics": [
        "Основы терапевтической стоматологии",
        "Клинические случаи",
        "Практические навыки"
      ]
    }
  ]
}
```

### Мильстоны

Автоматическое создание контрольных точек:
- 25% готовности
- 50% готовности  
- 75% готовности
- 90% готовности

## 🛠️ Администрирование

### Добавление новых вопросов

1. **Создать вопрос:**
```python
question = Question(
    text="Текст вопроса",
    options=json.dumps(["A", "B", "C", "D"]),
    correct_answer="A",
    big_domain_id=domain.id,
    difficulty_level=3
)
```

2. **Добавить IRT параметры:**
```python
irt_params = IRTParameters(
    question_id=question.id,
    difficulty=0.0,      # Средняя сложность
    discrimination=1.2,  # Хорошая дискриминация
    guessing=0.25        # 4 варианта ответа
)
```

### Калибровка IRT параметров

Для точной калибровки требуется:
- Минимум 30 ответов на вопрос
- Разнообразная выборка испытуемых
- Использование специализированного ПО (BILOG-MG, WINSTEPS)

### Мониторинг качества

- **Infit/Outfit статистики** для проверки соответствия модели
- **Надежность вопросов** (reliability)
- **Стандартные ошибки** параметров

## 📊 Статистика и отчеты

### Показатели системы

- Количество активных сессий
- Средняя точность оценок
- Время прохождения тестов
- Распределение способностей

### Отчеты для администраторов

- Анализ эффективности вопросов
- Статистика по доменам
- Прогресс пользователей
- Качество IRT параметров

## 🔒 Безопасность

### Защита от списывания

- **Адаптивный порядок вопросов**
- **Ограничение времени**
- **Мониторинг времени ответов**
- **Запрет на возврат к предыдущим вопросам**

### Конфиденциальность

- Шифрование персональных данных
- Анонимизация результатов исследований
- Соответствие GDPR требованиям

## 🚨 Устранение неполадок

### Частые проблемы

1. **"Нет доступных вопросов"**
   - Проверить наличие вопросов с IRT параметрами
   - Убедиться в правильной привязке к доменам

2. **"Ошибка оценки способностей"**
   - Проверить корректность IRT параметров
   - Убедиться в достаточном количестве ответов

3. **"Сессия не завершается"**
   - Проверить настройки точности (precision_threshold)
   - Убедиться в корректности условий завершения

### Логирование

```python
import logging
logger = logging.getLogger(__name__)
logger.error("Error in diagnostic session: %s", error)
```

## 📚 Дополнительные ресурсы

### Научные источники

- **Item Response Theory**: Hambleton, R. K., & Swaminathan, H. (1985)
- **Adaptive Testing**: van der Linden, W. J., & Glas, C. A. W. (2010)
- **Medical Testing Standards**: INBDE, DLOSCE guidelines

### Техническая документация

- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/
- **IRT Libraries**: Python packages for IRT analysis
- **Statistical Methods**: Maximum Likelihood Estimation

## 🤝 Поддержка

### Контакты

- **Техническая поддержка**: support@mentora.com
- **Документация**: docs.mentora.com
- **GitHub**: github.com/mentora/big-diagnostic

### Сообщество

- **Форум пользователей**: forum.mentora.com
- **Telegram группа**: @mentora_support
- **YouTube канал**: Mentora Academy

---

*Последнее обновление: 15 января 2024*
*Версия системы: 1.0.0* 