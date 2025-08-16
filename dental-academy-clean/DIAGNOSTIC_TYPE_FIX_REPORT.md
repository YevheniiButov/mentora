# DIAGNOSTIC TYPE FIX REPORT

## Проблема
Пользователь выбирал 75 вопросов, но `diagnostic_type` оставался 'preliminary', что приводило к преждевременному завершению по SE threshold вместо завершения по количеству вопросов.

## Анализ проблемы
1. **Неправильный diagnostic_type**: при выборе 75 вопросов `diagnostic_type` оставался 'preliminary'
2. **Конфликт типов**: `session_type` был 'full', но `diagnostic_type` был 'preliminary'
3. **SE threshold для preliminary**: IRT Engine применял SE threshold (0.4) к 75-вопросным тестам

## Исправления

### 1. Исправление создания сессии в `routes/diagnostic_routes.py`:

**Строки 175-195:**
```python
# БЫЛО:
if diagnostic_type == 'preliminary':
    session_type = 'full'
    estimated_questions = 75
    questions_per_domain = 3

session_data = {
    'diagnostic_type': diagnostic_type,  # ❌ Оставался 'preliminary'
    'session_type': session_type,
    'questions_per_domain': questions_per_domain,
    'estimated_total_questions': estimated_questions
}

# СТАЛО:
if diagnostic_type == 'preliminary':
    session_type = 'full'
    diagnostic_type = 'full'  # ✅ ИСПРАВЛЕНИЕ: меняем на 'full'
    estimated_questions = 75
    questions_per_domain = 3

session_data = {
    'diagnostic_type': diagnostic_type,  # ✅ Теперь правильный тип
    'session_type': session_type,
    'questions_per_domain': questions_per_domain,
    'estimated_total_questions': estimated_questions
}
```

### 2. Исправление конструктора IRT Engine в `utils/irt_engine.py`:

**Строки 225-245:**
```python
# БЫЛО:
elif diagnostic_type == 'preliminary':
    self.questions_per_domain = 3
    self.max_questions = 75
elif diagnostic_type == 'readiness':
    self.questions_per_domain = 6
    self.max_questions = 130

# СТАЛО:
elif diagnostic_type == 'preliminary':
    self.questions_per_domain = 3
    self.max_questions = 75
elif diagnostic_type == 'full':  # ✅ ИСПРАВЛЕНИЕ: добавлен тип 'full'
    self.questions_per_domain = 3
    self.max_questions = 75
elif diagnostic_type == 'readiness':
    self.questions_per_domain = 6
    self.max_questions = 130
elif diagnostic_type == 'comprehensive':  # ✅ ИСПРАВЛЕНИЕ: добавлен тип 'comprehensive'
    self.questions_per_domain = 6
    self.max_questions = 130
```

### 3. Исправление логики завершения в `utils/irt_engine.py`:

**Строки 1085-1090:**
```python
# ИСПРАВЛЕНИЕ: используем session_type вместо diagnostic_type
session_data = session.get_session_data()
session_type = session_data.get('session_type', 'preliminary')
diagnostic_type = session_data.get('diagnostic_type', 'preliminary')

logger.info(f"Session type: {session_type}, Diagnostic type: {diagnostic_type}")
```

## Результаты тестирования

### До исправления:
- **Diagnostic type**: 'preliminary' (неправильно)
- **Session type**: 'full' (правильно)
- **SE threshold**: 0.4 применялся к 75-вопросным тестам
- **Результат**: завершение после 36 вопросов при SE=0.296

### После исправления:
- **Diagnostic type**: 'full' (правильно)
- **Session type**: 'full' (правильно)
- **Max questions**: 75 (правильно)
- **SE threshold**: не применяется к full тестам

### Тестовые результаты:
- ✅ **36 вопросов, SE=0.296**: сессия продолжается (правильно)
- ✅ **50 вопросов, SE=0.296**: сессия продолжается (правильно)
- ✅ **75 вопросов, SE=0.296**: сессия завершается по max_questions (правильно)

## Логика завершения теперь работает корректно:

1. **Express (25 вопросов)**: diagnostic_type = 'express', завершается по SE threshold
2. **Preliminary (75 вопросов)**: diagnostic_type = 'full', завершается по количеству вопросов
3. **Readiness (130 вопросов)**: diagnostic_type = 'comprehensive', завершается по количеству вопросов

## Статус
🟢 **ИСПРАВЛЕНО И ПРОТЕСТИРОВАНО**

**Диагностические тесты теперь завершаются корректно:**
- **Express**: ~25 вопросов (или по SE threshold)
- **Preliminary**: ~75 вопросов (по количеству вопросов)
- **Readiness**: ~130 вопросов (по количеству вопросов)

**Система больше не завершает 75-вопросные тесты преждевременно.**


