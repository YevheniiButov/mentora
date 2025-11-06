from translations import get_translation, DEFAULT_LANGUAGE

def t(key, lang=DEFAULT_LANGUAGE, **kwargs):
    """
    Функция для получения перевода по ключу и языку
    """
    return get_translation(key, lang, **kwargs)

__all__ = ['t', 'DEFAULT_LANGUAGE'] 