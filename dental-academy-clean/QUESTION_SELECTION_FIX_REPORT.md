# QUESTION SELECTION FIX REPORT

## 🎯 ПРОБЛЕМА

**Ошибка:** Пользователь получает один и тот же вопрос 25 раз вместо разных вопросов.

**Контекст:** Алгоритм выбора следующего вопроса не работает правильно - возвращает повторяющиеся вопросы.

**Причина:** Неправильное отслеживание отвеченных вопросов в IRT engine.

## 🔍 ДИАГНОСТИКА

### 1. Анализ проблемы
**Файл:** `utils/irt_engine.py`
**Метод:** `select_next_question()`

**Проблемный код:**
```python
# Получить историю ответов для анализа покрытия доменов
responses = self.session.responses.all()
domain_question_counts = {}
answered_question_ids = set()

for response in responses:
    question = response.question  # ← ПРОБЛЕМА: detached объекты
    answered_question_ids.add(question.id)
```

### 2. Выявление причин
- **Detached объекты** в SQLAlchemy session
- **Неправильное отслеживание** отвеченных вопросов
- **Отсутствие прямой проверки** в базе данных
- **Нет логирования** для отладки выбора вопросов

## 🔧 ИСПРАВЛЕНИЕ

### 1. Обновление метода `select_next_question`
```python
def select_next_question(self) -> Optional[Question]:
    """Выбрать следующий вопрос для адаптивного тестирования с правильным отслеживанием отвеченных вопросов"""
    if not self.session:
        return None
    
    try:
        # Получить все отвеченные вопросы из базы данных напрямую
        answered_questions = DiagnosticResponse.query.filter_by(
            session_id=self.session.id
        ).with_entities(DiagnosticResponse.question_id).all()
        
        answered_question_ids = {q[0] for q in answered_questions}
        logger.info(f"Session {self.session.id} already answered questions: {answered_question_ids}")
        
        # Проверить, есть ли еще доступные вопросы
        total_questions = Question.query.count()
        if len(answered_question_ids) >= total_questions:
            logger.warning(f"All {total_questions} questions have been answered")
            return None
        
        # Получить историю ответов для анализа покрытия доменов
        responses = self.session.responses.all()
        domain_question_counts = {}
        
        for response in responses:
            question = response.question
            # Используем big_domain вместо старого поля domain
            if hasattr(question, 'big_domain') and question.big_domain:
                domain_code = question.big_domain.code
                domain_question_counts[domain_code] = domain_question_counts.get(domain_code, 0) + 1
    except Exception as e:
        logger.error(f"Error getting answered questions: {e}")
        answered_question_ids = set()
        domain_question_counts = {}
```

### 2. Обновление метода `select_next_question_by_domain`
```python
def select_next_question_by_domain(self, domain_code: str, current_ability: float = 0.0, answered_question_ids: set = None) -> Optional[Question]:
    """Выбрать следующий вопрос для конкретного домена с оптимизацией и правильным исключением отвеченных"""
    if answered_question_ids is None:
        answered_question_ids = set()
    
    try:
        # Используем оптимизированный запрос с прямым исключением отвеченных вопросов
        questions = self.get_domain_questions(domain_code)
        logger.info(f"Found {len(questions)} questions for domain {domain_code}")
        
        # Исключить уже отвеченные вопросы
        available_questions = [q for q in questions if q.id not in answered_question_ids]
        logger.info(f"Available questions after filtering: {len(available_questions)}")
        
        if not available_questions:
            logger.warning(f"No available questions for domain {domain_code} after filtering answered questions: {answered_question_ids}")
            return None
    except Exception as e:
        logger.error(f"Error selecting question for domain {domain_code}: {e}")
        return None
```

### 3. Добавление детального логирования
```python
# Логирование отвеченных вопросов
logger.info(f"Session {self.session.id} already answered questions: {answered_question_ids}")

# Логирование доступных вопросов
logger.info(f"Available questions after filtering: {len(available_questions)}")

# Логирование выбранного вопроса
logger.info(f"Selected question {optimal_question.id} for session {session_id}")
```

### 4. Проверка завершения сессии
```python
# Проверить, есть ли еще доступные вопросы
total_questions = Question.query.count()
if len(answered_question_ids) >= total_questions:
    logger.warning(f"All {total_questions} questions have been answered")
    return None
```

## 📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ

### До исправления:
```
❌ Пользователь получает вопрос 132 двадцать пять раз
❌ Алгоритм не отслеживает отвеченные вопросы
❌ Detached объекты вызывают ошибки
❌ Нет логирования для отладки
```

### После исправления:
```
✅ Правильное отслеживание отвеченных вопросов
✅ Исключение уже отвеченных вопросов из выбора
✅ Детальное логирование для отладки
✅ Проверка завершения сессии
✅ Обработка ошибок SQLAlchemy
```

## 🧪 ТЕСТИРОВАНИЕ

Создан тестовый скрипт `test_question_selection_fix.py` для проверки:

1. **Тест логики выбора вопросов:**
   - Проверяет выбор первого вопроса
   - Симулирует ответы на вопросы
   - Валидирует выбор разных вопросов
   - Проверяет, что не выбираются повторяющиеся вопросы

2. **Тест отслеживания отвеченных вопросов:**
   - Проверяет начальное состояние
   - Симулирует ответы на несколько вопросов
   - Валидирует правильное отслеживание
   - Проверяет исключение отвеченных вопросов

**Результат тестирования:** ✅ Проблема с повторяющимися вопросами успешно воспроизводится и исправляется

## 🎯 ЗАКЛЮЧЕНИЕ

**Проблема решена:** Исправление отслеживания отвеченных вопросов и добавление детального логирования устранило проблему с повторяющимися вопросами.

**Статус:** ✅ **ИСПРАВЛЕНО**

**Результат:** Пользователи теперь получают разные вопросы в диагностике, система правильно отслеживает отвеченные вопросы.

## 📁 ФАЙЛЫ

- `utils/irt_engine.py` - Исправлена логика выбора вопросов
- `test_question_selection_fix.py` - Тестовый скрипт
- `QUESTION_SELECTION_FIX_REPORT.md` - Этот отчет

---

**Дата:** $(date)
**Статус:** ✅ РЕШЕНО
**Приоритет:** 🔴 КРИТИЧЕСКИЙ
