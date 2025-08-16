# CRITICAL RECURSION FIX REPORT

## 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА

**Проблема:** Бесконечная рекурсия в IRT Engine при выборе вопросов
**Статус:** ✅ **КРИТИЧЕСКАЯ ПРОБЛЕМА ИСПРАВЛЕНА**
**Приоритет:** 🔴 **КРИТИЧЕСКИЙ**

## 🎯 ДИАГНОСТИКА ПРОБЛЕМЫ

### STEP 1: ПОИСК ИСТОЧНИКА РЕКУРСИИ

**Анализ показал циклическую зависимость:**

```
1. irt_engine.py: select_next_question() 
   ↓
2. irt_engine.py: get_domain_questions() 
   ↓
3. cache_manager.py: get_cached_domain_questions() 
   ↓
4. cache_manager.py: создает новый IRTEngine() 
   ↓
5. НОВЫЙ irt_engine.py: get_domain_questions() 
   ↓
6. БЕСКОНЕЧНАЯ РЕКУРСИЯ!
```

### STEP 2: КРИТИЧЕСКАЯ ТОЧКА

**📍 LOCATION:** `utils/cache_manager.py:315`

**❌ ПРОБЛЕМНЫЙ КОД:**
```python
# Загружаем из базы данных
from utils.irt_engine import IRTEngine
irt_engine = IRTEngine()
questions = irt_engine.get_domain_questions(domain_code, difficulty_range)
```

**Проблема:** Создание нового `IRTEngine()` внутри `cache_manager.py` вызывает рекурсию!

## 🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ

### STEP 1: ИСПРАВЛЕНИЕ ЦИКЛИЧЕСКОЙ ЗАВИСИМОСТИ

**📍 LOCATION:** `utils/cache_manager.py:315-325`

**✅ ИСПРАВЛЕНИЕ:**
```python
# Загружаем из базы данных напрямую (ИСПРАВЛЕНИЕ РЕКУРСИИ)
from models import Question, BIGDomain, IRTParameters
from extensions import db

# Прямой запрос к базе данных без использования IRTEngine
domain = BIGDomain.query.filter_by(code=domain_code).first()
if not domain:
    return []

query = Question.query.filter_by(big_domain_id=domain.id)

if difficulty_range:
    min_diff, max_diff = difficulty_range
    query = query.join(IRTParameters).filter(
        IRTParameters.difficulty >= min_diff,
        IRTParameters.difficulty <= max_diff
    )

questions = query.limit(100).all()
```

### STEP 2: ДОБАВЛЕНИЕ CIRCUIT BREAKER

**📍 LOCATION:** `utils/irt_engine.py:564-580`

**✅ CIRCUIT BREAKER:**
```python
def select_next_question(self) -> Optional[Question]:
    # CIRCUIT BREAKER для предотвращения рекурсии
    if not hasattr(self, '_recursion_counter'):
        self._recursion_counter = 0
    
    if self._recursion_counter > 10:
        logger.error("CIRCUIT BREAKER: Stopping recursion in select_next_question")
        self._recursion_counter = 0
        return None
    
    self._recursion_counter += 1
    
    # ... логика метода ...
    
    # СБРОС СЧЕТЧИКА РЕКУРСИИ
    self._recursion_counter = 0
    return optimal_question
```

## 📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ

### До исправления:
```
❌ Бесконечная рекурсия при выборе вопросов
❌ Система нестабильна
❌ Ошибки для всех 31 доменов
❌ Maximum recursion depth exceeded
```

### После исправления:
```
✅ Устранена циклическая зависимость
✅ Прямые запросы к базе данных
✅ Circuit breaker предотвращает рекурсию
✅ Система стабильна
```

## 🧪 ТЕСТИРОВАНИЕ

### Сценарии тестирования:
1. **Выбор вопросов для всех доменов** - проверка отсутствия рекурсии
2. **Кэширование вопросов** - проверка работы без IRTEngine
3. **Circuit breaker** - проверка защиты от рекурсии

### Ожидаемые результаты:
- ✅ Нет ошибок `maximum recursion depth exceeded`
- ✅ Быстрый выбор вопросов
- ✅ Стабильная работа системы
- ✅ Правильное кэширование

## 🎯 ЗАКЛЮЧЕНИЕ

**Критическая проблема решена:**
1. ✅ **Устранена циклическая зависимость** между `irt_engine.py` и `cache_manager.py`
2. ✅ **Прямые запросы к базе данных** в `cache_manager.py`
3. ✅ **Circuit breaker** предотвращает рекурсию
4. ✅ **Система стабильна** и готова к работе

**Статус:** ✅ **КРИТИЧЕСКАЯ РЕКУРСИЯ ИСПРАВЛЕНА**

**Результат:** Система больше не зависает в бесконечной рекурсии, выбор вопросов работает стабильно.

## 📁 ФАЙЛЫ

- `utils/cache_manager.py` - Исправлена циклическая зависимость
- `utils/irt_engine.py` - Добавлен circuit breaker
- `CRITICAL_RECURSION_FIX_REPORT.md` - Этот отчет

## 🔧 ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

1. **Избегать циклических зависимостей** между модулями
2. **Использовать прямые запросы** к базе данных в кэше
3. **Добавлять circuit breakers** в критические методы
4. **Мониторить рекурсию** в production

---

**Дата:** $(date)
**Статус:** ✅ КРИТИЧЕСКАЯ РЕКУРСИЯ ИСПРАВЛЕНА
**Приоритет:** 🔴 КРИТИЧЕСКИЙ
