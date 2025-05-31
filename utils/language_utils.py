# Утилиты для работы с языками
# Вставьте сюда код языковых утилит

RTL_LANGUAGES = ['fa', 'ar', 'he', 'ur']

def get_text_direction(lang_code):
    """Возвращает направление текста для языка"""
    return 'rtl' if lang_code in RTL_LANGUAGES else 'ltr'

def is_rtl_language(lang_code):
    """Проверяет, является ли язык RTL"""
    return lang_code in RTL_LANGUAGES

# Вставьте сюда дополнительные функции 