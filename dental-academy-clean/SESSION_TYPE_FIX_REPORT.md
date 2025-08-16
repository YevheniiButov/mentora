# SESSION TYPE FIX REPORT

## Проблема
Пользователь выбирал 75 вопросов, но сессия создавалась как 'preliminary', что приводило к преждевременному завершению по SE threshold вместо завершения по количеству вопросов.

## Анализ проблемы
1. **Неправильное создание сессии**: все сессии создавались с `session_type='adaptive_diagnostic'`
2. **Неправильная логика завершения**: IRT Engine не учитывал правильный тип сессии
3. **SE threshold для всех типов**: preliminary логика применялась ко всем сессиям

## Исправления

### 1. Исправление создания сессии в `routes/diagnostic_routes.py`:

**Строки 160-185:**
```python
# БЫЛО:
session_data = {
    'diagnostic_type': diagnostic_type,
    'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 6),
    'estimated_total_questions': 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130)
}

# СТАЛО:
# Определяем правильный session_type на основе diagnostic_type
if diagnostic_type == 'express':
    session_type = 'preliminary'
    estimated_questions = 25
    questions_per_domain = 1
elif diagnostic_type == 'preliminary':
    session_type = 'full'
    estimated_questions = 75
    questions_per_domain = 3
elif diagnostic_type == 'readiness':
    session_type = 'comprehensive'
    estimated_questions = 130
    questions_per_domain = 6

session_data = {
    'diagnostic_type': diagnostic_type,
    'session_type': session_type,
    'questions_per_domain': questions_per_domain,
    'estimated_total_questions': estimated_questions
}
```

### 2. Исправление логики завершения в `utils/irt_engine.py`:

**Строки 1080-1150:**
```python
# Check precision threshold based on session type
session_data = session.get_session_data()
session_type = session_data.get('session_type', 'preliminary')

# For preliminary sessions (≤40 questions): Use SE threshold
if session_type == 'preliminary':
    if session.questions_answered >= self.min_questions and session.ability_se <= self.min_se_threshold:
        return {'should_terminate': True, 'reason': 'precision_reached'}

# For full sessions (75 questions): Use question count primarily, SE threshold only if very confident
elif session_type == 'full':
    min_questions = max(50, session_data.get('estimated_total_questions', 75) * 0.7)
    max_questions = session_data.get('estimated_total_questions', 75)
    
    if session.questions_answered < min_questions:
        return {'should_terminate': False, 'reason': 'min_questions_full'}
    elif session.questions_answered >= max_questions:
        return {'should_terminate': True, 'reason': 'max_questions_full'}
    else:
        # Only terminate early if extremely confident (SE < 0.25)
        if session.ability_se < 0.25:
            return {'should_terminate': True, 'reason': 'precision_reached_full'}

# For comprehensive sessions (130 questions): Use question count only
elif session_type == 'comprehensive':
    max_questions = session_data.get('estimated_total_questions', 130)
    if session.questions_answered >= max_questions:
        return {'should_terminate': True, 'reason': 'max_questions_comprehensive'}
```

## Результаты тестирования

### До исправления:
- **Все сессии** создавались как 'preliminary'
- **SE threshold (0.4)** применялся ко всем типам
- **75-вопросные тесты** завершались после 36 вопросов

### После исправления:
- **Express (25 вопросов)**: session_type = 'preliminary', завершается по SE threshold
- **Preliminary (75 вопросов)**: session_type = 'full', завершается по количеству вопросов
- **Readiness (130 вопросов)**: session_type = 'comprehensive', завершается по количеству вопросов

### Тестовые результаты:
- ✅ **35 вопросов, SE=0.3**: сессия продолжается (правильно)
- ✅ **50 вопросов, SE=0.2**: сессия продолжается (правильно для full)
- ✅ **75 вопросов, SE=0.3**: сессия завершается по max_questions (правильно)

## Логика завершения теперь работает корректно:

1. **Preliminary (≤40 вопросов)**: завершается по SE threshold (0.4)
2. **Full (75 вопросов)**: завершается по количеству вопросов, раннее завершение только при SE < 0.25
3. **Comprehensive (130 вопросов)**: завершается только по количеству вопросов

## Статус
🟢 **ИСПРАВЛЕНО И ПРОТЕСТИРОВАНО**

**Диагностические тесты теперь завершаются корректно:**
- **Express**: ~25 вопросов (или по SE threshold)
- **Preliminary**: ~75 вопросов (или по SE threshold только при очень высокой точности)
- **Readiness**: ~130 вопросов (только по количеству вопросов)

**Система больше не завершает 75-вопросные тесты преждевременно.**


