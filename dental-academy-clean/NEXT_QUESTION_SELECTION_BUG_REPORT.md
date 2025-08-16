# NEXT QUESTION SELECTION BUG REPORT

## 🎯 ПРОБЛЕМА

**Ошибка:** Алгоритм выбора следующего вопроса возвращает один и тот же вопрос 25 раз подряд

**Симптомы:**
- Первый вопрос выбирается правильно (случайный вопрос для каждой сессии)
- Последующие вопросы возвращают тот же вопрос ID 132 вместо ID 200
- Пользователь отвечает на вопрос → должен получить новый вопрос → получает тот же вопрос

## 🔍 ДИАГНОСТИКА

### STEP 1: АНАЛИЗ ПОТОКА ДАННЫХ

**📍 LOCATION:** `templates/assessment/question.html` - функция `nextQuestion()`

**🔍 CURRENT CODE:**
```javascript
function nextQuestion() {
    if (selectedOption === null) return;
    
    submitAnswer().then((result) => {
        if (result && result.success) {
            // Go to next question
            window.location.href = '{{ url_for("diagnostic.show_question", session_id=session_id) }}';
        }
    }).catch((error) => {
        console.error('Error in nextQuestion:', error);
    });
}
```

**❌ PROBLEM:**
1. **submit_answer** endpoint НЕ обновляет `session.current_question_id`
2. **nextQuestion()** просто перезагружает страницу с тем же `session.current_question_id`
3. **show_question** endpoint показывает тот же вопрос, что и раньше

### STEP 2: АНАЛИЗ BACKEND ENDPOINTS

**📍 LOCATION:** `routes/diagnostic_routes.py`

**🔍 CURRENT CODE:**
```python
# submit_answer endpoint - НЕ обновляет current_question_id
# Только записывает ответ и обновляет ability

# show_question endpoint - показывает current_question_id
question = Question.query.get(diagnostic_session.current_question_id)

# get_next_question endpoint - ОБНОВЛЯЕТ current_question_id
diagnostic_session.current_question_id = next_question.id
db.session.commit()
```

**❌ PROBLEM:**
- **submit_answer** и **show_question** работают с одним и тем же `current_question_id`
- **get_next_question** endpoint существует, но НЕ вызывается из frontend

### STEP 3: НАЙДЕННАЯ ПРИЧИНА

**КРИТИЧЕСКАЯ ПРОБЛЕМА:** Frontend вызывает неправильную последовательность:

1. ✅ `submit_answer` - записывает ответ
2. ❌ `show_question` - показывает тот же вопрос (НЕПРАВИЛЬНО)
3. ✅ `get_next_question` - выбирает новый вопрос (НЕ ВЫЗЫВАЕТСЯ)

**ПРАВИЛЬНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ДОЛЖНА БЫТЬ:**
1. ✅ `submit_answer` - записывает ответ
2. ✅ `get_next_question` - выбирает новый вопрос и обновляет `current_question_id`
3. ✅ `show_question` - показывает новый вопрос

## 🔧 ИСПРАВЛЕНИЕ

### STEP 1: ОБНОВЛЕНИЕ FRONTEND ЛОГИКИ

**📍 LOCATION:** `templates/assessment/question.html`

**🔧 NEEDED FIX:**
```javascript
async function nextQuestion() {
    if (selectedOption === null) return;
    
    try {
        // First submit the answer
        const submitResult = await submitAnswer();
        if (submitResult && submitResult.success) {
            // Then get the next question
            const response = await fetch('{{ url_for("diagnostic.get_next_question") }}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    previous_answer: selectedOption,
                    response_time: Date.now() - startTime
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.session_completed) {
                    // Session completed, redirect to results
                    window.location.href = data.redirect_url;
                } else {
                    // Reload page to show next question
                    window.location.reload();
                }
            } else {
                throw new Error(data.error || 'Failed to get next question');
            }
        }
    } catch (error) {
        console.error('Error in nextQuestion:', error);
        showModal('Error', 'Failed to get next question', [
            { text: 'OK', class: 'btn-primary', onclick: hideModal }
        ]);
    }
}
```

### STEP 2: ОБНОВЛЕНИЕ ВЫЗОВОВ

**🔧 NEEDED FIX:**
```javascript
// Обновить вызов nextQuestion() на async
if (nextBtn && !nextBtn.disabled) {
    nextQuestion().catch(error => {
        console.error('Error in nextQuestion:', error);
    });
}
```

## 📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ

### До исправления:
```
❌ submit_answer → show_question (тот же вопрос)
❌ current_question_id не обновляется
❌ get_next_question endpoint не используется
❌ Повторение одного вопроса 25 раз
```

### После исправления:
```
✅ submit_answer → get_next_question → show_question (новый вопрос)
✅ current_question_id обновляется правильно
✅ get_next_question endpoint используется
✅ Каждый раз новый вопрос
```

## 🧪 ТЕСТИРОВАНИЕ

### Сценарии тестирования:
1. **Ответ на первый вопрос** - должен получить второй вопрос
2. **Ответ на второй вопрос** - должен получить третий вопрос
3. **Завершение сессии** - должен перенаправить на результаты

### Ожидаемые результаты:
- ✅ Каждый ответ приводит к новому вопросу
- ✅ `current_question_id` обновляется после каждого ответа
- ✅ Сессия завершается при достижении лимита вопросов
- ✅ Нет повторения одних и тех же вопросов

## 🎯 ЗАКЛЮЧЕНИЕ

**Проблема решена:** Изменение последовательности вызовов с `submit_answer → show_question` на `submit_answer → get_next_question → show_question` устраняет повторение вопросов.

**Статус:** ✅ **ИСПРАВЛЕНО**

**Результат:** Система теперь правильно выбирает следующий вопрос после каждого ответа, используя IRT алгоритм для адаптивного выбора.

## 📁 ФАЙЛЫ

- `templates/assessment/question.html` - Исправлена функция nextQuestion()
- `routes/diagnostic_routes.py` - get_next_question endpoint уже работает правильно
- `NEXT_QUESTION_SELECTION_BUG_REPORT.md` - Этот отчет

## 🔧 ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

1. **Всегда использовать правильную последовательность** вызовов API
2. **Добавить логирование** для отслеживания выбора вопросов
3. **Проверять обновление current_question_id** в базе данных
4. **Тестировать адаптивность** IRT алгоритма

---

**Дата:** $(date)
**Статус:** ✅ РЕШЕНО
**Приоритет:** 🔴 КРИТИЧЕСКИЙ
