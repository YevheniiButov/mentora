# Утилиты для мониторинга производительности
# Вставьте сюда код мониторинга производительности

from functools import wraps
import time

def measure_performance(f):
    """Декоратор для измерения производительности функций"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        
        # Логируем медленные запросы
        if end - start > 1.0:
            # app.logger.warning(f'Slow request: {f.__name__} took {end-start:.2f}s')
            pass
        
        return result
    return decorated_function

# Вставьте сюда дополнительные функции мониторинга 