"""
Translation system for Mentora
Professional medical terminology in 9 languages
"""

from .nl import translations as nl_translations
from .en import translations as en_translations
from .es import translations as es_translations
from .pt import translations as pt_translations
from .uk import translations as uk_translations
from .fa import translations as fa_translations
from .tr import translations as tr_translations
from .ru import translations as ru_translations
from .domain_diagnostic_translations import DOMAIN_DIAGNOSTIC_TRANSLATIONS

# Combine all translations
translations = {
    'nl': nl_translations,
    'en': en_translations,
    'es': es_translations,
    'pt': pt_translations,
    'uk': uk_translations,
    'fa': fa_translations,
    'tr': tr_translations,
    'ru': ru_translations
}

# Default language (Dutch)
DEFAULT_LANGUAGE = 'nl'

# Supported languages with names
LANGUAGE_NAMES = {
    'nl': 'Nederlands',
    'en': 'English',
    'es': 'Español',
    'pt': 'Português',
    'uk': 'Українська',
    'fa': 'فارسی',
    'tr': 'Türkçe',
    'ru': 'Русский'
}

# RTL languages
RTL_LANGUAGES = ['fa', 'ar']

# Country codes for flags
COUNTRY_CODES = {
    'nl': 'nl',
    'en': 'gb',
    'es': 'es',
    'pt': 'pt',
    'uk': 'ua',
    'fa': 'ir',
    'tr': 'tr',
    'ru': 'ru'
}

def get_translation(key, lang=DEFAULT_LANGUAGE, **kwargs):
    """
    Get translation for key in specified language
    
    Args:
        key (str): Translation key
        lang (str): Language code
        **kwargs: Parameters for string formatting
        
    Returns:
        str: Translated string
    """
    if lang not in translations:
        lang = DEFAULT_LANGUAGE
    
    # First check in domain diagnostic translations
    if lang in DOMAIN_DIAGNOSTIC_TRANSLATIONS:
        translation_value = DOMAIN_DIAGNOSTIC_TRANSLATIONS[lang].get(key)
        if translation_value is not None:
            # Apply formatting if parameters provided
            if kwargs:
                try:
                    return translation_value.format(**kwargs)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Formatting error for key '{key}' in lang '{lang}': {e}")
                    return translation_value
            return translation_value
    
    # Then check in main translations
    translation_value = translations[lang].get(key)
    
    # If not found and not default language, try default
    if translation_value is None and lang != DEFAULT_LANGUAGE:
        # Try domain diagnostic translations in default language
        if DEFAULT_LANGUAGE in DOMAIN_DIAGNOSTIC_TRANSLATIONS:
            translation_value = DOMAIN_DIAGNOSTIC_TRANSLATIONS[DEFAULT_LANGUAGE].get(key)
        
        # If still not found, try main translations in default language
        if translation_value is None:
            translation_value = translations[DEFAULT_LANGUAGE].get(key)
    
    # If still not found, return the key
    if translation_value is None:
        return key
    
    # Apply formatting if parameters provided
    if kwargs:
        try:
            return translation_value.format(**kwargs)
        except (KeyError, ValueError) as e:
            print(f"Warning: Formatting error for key '{key}' in lang '{lang}': {e}")
            return translation_value
    
    return translation_value

def get_available_languages():
    """Get list of available languages"""
    return list(translations.keys())

def get_language_names():
    """Get dictionary with language names"""
    return LANGUAGE_NAMES

def is_rtl_language(lang):
    """Check if language is RTL"""
    return lang in RTL_LANGUAGES

def get_country_code(lang_code):
    """Get country code for flag display"""
    return COUNTRY_CODES.get(lang_code, 'gb')

def get_language_direction(lang_code):
    """Get text direction for language"""
    return 'rtl' if is_rtl_language(lang_code) else 'ltr'

def validate_translation_completeness():
    """Validate completeness of translations"""
    base_keys = set(translations[DEFAULT_LANGUAGE].keys())
    incomplete_languages = {}
    
    for lang, lang_translations in translations.items():
        if lang == DEFAULT_LANGUAGE:
            continue
            
        lang_keys = set(lang_translations.keys())
        missing_keys = base_keys - lang_keys
        extra_keys = lang_keys - base_keys
        
        if missing_keys or extra_keys:
            incomplete_languages[lang] = {
                'missing': list(missing_keys),
                'extra': list(extra_keys)
            }
    
    return incomplete_languages

__all__ = [
    'translations',
    'DEFAULT_LANGUAGE',
    'LANGUAGE_NAMES',
    'RTL_LANGUAGES',
    'COUNTRY_CODES',
    'get_translation',
    'get_available_languages',
    'get_language_names',
    'is_rtl_language',
    'get_country_code',
    'get_language_direction',
    'validate_translation_completeness'
] 