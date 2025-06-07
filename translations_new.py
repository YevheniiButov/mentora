import os
import importlib.util

class ModularTranslations:
    def __init__(self):
        self.translations = {}
        # Убираем автоматическую загрузку - будем делать вручную
        # self.load_modules()
    
    def load_modules(self):
        """Загружает все модули переводов"""
        modules_dir = 'translations_modules'
        if not os.path.exists(modules_dir):
            print(f"⚠️ Directory {modules_dir} not found")
            return
        
        print(f"📂 Loading translations from {modules_dir}")
        for filename in os.listdir(modules_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                module_path = os.path.join(modules_dir, filename)
                
                print(f"  📄 Loading {filename}")
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Ищем словарь переводов в модуле
                    translation_found = False
                    for attr_name in dir(module):
                        if attr_name.endswith('_translations'):
                            print(f"    ✅ Found translations: {attr_name}")
                            module_translations = getattr(module, attr_name)
                            self.merge_translations(module_translations)
                            translation_found = True
                    
                    if not translation_found:
                        print(f"    ⚠️ No translation dict found in {filename}")
                        
                except Exception as e:
                    print(f"    ❌ Error loading {filename}: {e}")
        
        print(f"📊 Total languages loaded: {list(self.translations.keys())}")
    
    def merge_translations(self, module_translations):
        """Объединяет переводы из модуля с основными"""
        for lang, translations in module_translations.items():
            if lang not in self.translations:
                self.translations[lang] = {}
            
            # Рекурсивно объединяем вложенные структуры
            self._deep_merge(self.translations[lang], translations)
    
    def _deep_merge(self, target, source):
        """Рекурсивно объединяет словари"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get(self, key, lang='en', **kwargs):
        """Получает перевод для ключа"""
        if lang not in self.translations:
            lang = 'en'
        
        # Поддержка вложенных ключей через точку
        translation = self._get_nested_value(self.translations[lang], key)
        
        if translation is None and lang != 'en':
            translation = self._get_nested_value(self.translations['en'], key)
        
        if translation is None:
            return key
        
        if kwargs:
            try:
                return translation.format(**kwargs)
            except:
                return translation
        
        return translation
    
    def _get_nested_value(self, data, key):
        """Получает значение по вложенному ключу (например, 'module.subkey')"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current

# Глобальный экземпляр
_modular_translations = ModularTranslations()

# Загружаем оригинальные переводы как fallback
try:
    from translations import translations as original_translations
    _modular_translations.translations = original_translations
    print("📚 Загружены оригинальные переводы как fallback")
    
    # Теперь загружаем модульные переводы для перезаписи
    _modular_translations.load_modules()
    
except ImportError:
    print("⚠️ Оригинальные переводы не найдены")
    # Загружаем только модульные
    _modular_translations.load_modules()

# Функция для совместимости
def get_translation(key, lang='en', **kwargs):
    return _modular_translations.get(key, lang, **kwargs)

def setup_translations(app):
    """Настройка переводов для Flask приложения"""
    # Добавляем функцию перевода в контекст Jinja2
    @app.context_processor
    def inject_translation():
        return {'t': get_translation}
    
    print("🌐 Модульная система переводов настроена")
    return get_translation
