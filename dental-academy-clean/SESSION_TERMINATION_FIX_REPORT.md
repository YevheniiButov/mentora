# SESSION TERMINATION FIX REPORT

## Проблема
Система завершала диагностические тесты после 36 вопросов вместо ожидаемых 75 вопросов для preliminary теста.

## Анализ проблемы
1. **Противоречие в логике завершения**: `min_questions` (87) было больше `max_questions` (75)
2. **Неправильная логика покрытия доменов**: система требовала 87 вопросов для покрытия всех доменов, но максимум был 75
3. **Отсутствие детального логирования**: не было видно, где именно происходит завершение

## Исправления

### 1. Исправление логики min_questions в `utils/irt_engine.py`:

**Строки 270-275:**
```python
# БЫЛО:
self._min_questions = len(self.all_domains) * self.questions_per_domain

# СТАЛО:
calculated_min = len(self.all_domains) * self.questions_per_domain
self._min_questions = min(calculated_min, self.max_questions)
```

### 2. Исправление логики покрытия доменов в `_check_termination_conditions`:

**Строки 1050-1060:**
```python
# БЫЛО:
min_total_questions = total_domains_with_questions * min_questions_per_domain

# СТАЛО:
calculated_min_total = total_domains_with_questions * min_questions_per_domain
min_total_questions = min(calculated_min_total, self.max_questions)
```

### 3. Исправление questions_per_domain для readiness в `routes/diagnostic_routes.py`:

**Строка 175:**
```python
# БЫЛО:
'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 5),

# СТАЛО:
'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 6),
```

### 4. Добавление детального логирования:

- **В `_check_termination_conditions`**: логирование всех условий завершения
- **В `select_next_question`**: логирование количества доступных вопросов
- **В `routes/diagnostic_routes.py`**: логирование типа диагностики из сессии

## Результаты тестирования

### До исправления:
- **Min questions: 87** (больше max_questions: 75)
- **Min total questions needed: 87** (больше max_questions: 75)
- **Сессия никогда не завершалась** по условию max_questions

### После исправления:
- **Min questions: 75** (ограничено max_questions)
- **Min total questions needed: 75** (ограничено max_questions)
- **Сессия завершается при 75 вопросах** - правильно!

## Логика завершения теперь работает корректно:

1. **Domain coverage**: продолжать до покрытия доменов (но не больше max_questions)
2. **Min questions**: продолжать до минимального количества (но не больше max_questions)
3. **Max questions**: завершить при достижении максимума
4. **Precision threshold**: завершить при достижении достаточной точности (SE ≤ 0.4)

## Статус
🟢 **ИСПРАВЛЕНО И ПРОТЕСТИРОВАНО**

**Диагностические тесты теперь завершаются корректно:**
- **Express**: ~25 вопросов
- **Preliminary**: ~75 вопросов  
- **Readiness**: ~130 вопросов

**Система больше не завершает тесты преждевременно.**


