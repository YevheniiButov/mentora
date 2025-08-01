# config.py - Конфигурация приложения Mentora Clean
# Включает настройки для DigiD интеграции

import os
from datetime import timedelta


class Config:
    """Базовая конфигурация приложения"""
    
    # Основные настройки Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Язык по умолчанию
    DEFAULT_LANGUAGE = 'nl'
    
    # База данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Безопасность
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Интернационализация
    LANGUAGES = {
        'nl': 'Nederlands',
        'en': 'English',
        'es': 'Español',
        'pt': 'Português',
        'uk': 'Українська',
        'fa': 'فارسی',
        'tr': 'Türkçe',
        'ru': 'Русский'
    }
    BABEL_DEFAULT_LOCALE = 'nl'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    
    # Кэш
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # DigiD Configuration
    DIGID_ENABLED = True
    DIGID_SESSION_TIMEOUT = 14400  # 4 hours in seconds
    DIGID_MOCK_MODE = True  # Enable mock mode by default
    DIGID_LOGOUT_URL = '/digid/logout'
    DIGID_LOGIN_URL = '/digid/login'
    
    # DigiD URLs (для production)
    DIGID_BASE_URL = os.environ.get('DIGID_BASE_URL', 'https://digid.nl')
    DIGID_AUTH_URL = os.environ.get('DIGID_AUTH_URL', 'https://digid.nl/auth')
    DIGID_LOGOUT_URL_EXTERNAL = os.environ.get('DIGID_LOGOUT_URL_EXTERNAL', 'https://digid.nl/logout')
    
    # DigiD Credentials (для production)
    DIGID_ENTITY_ID = os.environ.get('DIGID_ENTITY_ID')
    DIGID_ACS_URL = os.environ.get('DIGID_ACS_URL')
    DIGID_SLO_URL = os.environ.get('DIGID_SLO_URL')
    DIGID_CERTIFICATE_PATH = os.environ.get('DIGID_CERTIFICATE_PATH')
    DIGID_PRIVATE_KEY_PATH = os.environ.get('DIGID_PRIVATE_KEY_PATH')
    
    # DigiD SAML Settings
    DIGID_SAML_NAME_ID_FORMAT = 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified'
    DIGID_SAML_SIGNATURE_ALGORITHM = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
    DIGID_SAML_DIGEST_ALGORITHM = 'http://www.w3.org/2001/04/xmlenc#sha256'
    
    # DigiD Session Management
    DIGID_SESSION_EXTEND_THRESHOLD = 3600  # 1 hour before expiry
    DIGID_SESSION_CHECK_INTERVAL = 300  # 5 minutes
    
    # DigiD User Attributes
    DIGID_ATTRIBUTES = [
        'bsn',  # Burger Service Nummer
        'digid_username',
        'first_name',
        'last_name',
        'email',
        'date_of_birth',
        'gender'
    ]
    
    @staticmethod
    def init_app(app):
        """Инициализация конфигурации"""
        pass


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    
    DEBUG = True
    
    # База данных для разработки
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dental_academy_clean.db'
    
    # Если DATABASE_URL не установлен, используем SQLALCHEMY_DATABASE_URI
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///dental_academy_clean.db'
    
    # DigiD для разработки (mock mode)
    DIGID_MOCK_MODE = True
    DIGID_ENABLED = True
    DIGID_SESSION_TIMEOUT = 14400  # 4 hours
    
    # WTF CSRF disabled for development
    WTF_CSRF_ENABLED = False
    
    # Mock DigiD URLs
    DIGID_BASE_URL = 'http://localhost:5005/digid'
    DIGID_AUTH_URL = 'http://localhost:5005/digid/authenticate'
    DIGID_LOGOUT_URL_EXTERNAL = 'http://localhost:5005/digid/logout'
    
    # Mock DigiD Credentials (не используются в mock mode)
    DIGID_ENTITY_ID = 'mock-entity-id'
    DIGID_ACS_URL = 'http://localhost:5005/digid/callback'
    DIGID_SLO_URL = 'http://localhost:5005/digid/logout'


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    
    TESTING = True
    
    # База данных для тестирования
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # DigiD для тестирования
    DIGID_MOCK_MODE = True
    DIGID_ENABLED = True
    DIGID_SESSION_TIMEOUT = 3600  # 1 hour for testing
    
    # WTF CSRF disabled for testing
    WTF_CSRF_ENABLED = False


class StagingConfig(Config):
    """Конфигурация для staging/pre-production"""
    
    DEBUG = False
    
    # База данных для staging
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # DigiD для staging (pre-production environment)
    DIGID_MOCK_MODE = False
    DIGID_ENABLED = True
    DIGID_SESSION_TIMEOUT = 14400  # 4 hours
    
    # Pre-production DigiD URLs
    DIGID_BASE_URL = os.environ.get('DIGID_BASE_URL', 'https://preprod.digid.nl')
    DIGID_AUTH_URL = os.environ.get('DIGID_AUTH_URL', 'https://preprod.digid.nl/auth')
    DIGID_LOGOUT_URL_EXTERNAL = os.environ.get('DIGID_LOGOUT_URL_EXTERNAL', 'https://preprod.digid.nl/logout')
    
    @classmethod
    def validate_digid_config(cls):
        """Валидация обязательных DigiD настроек для staging"""
        required_vars = [
            'DIGID_ENTITY_ID',
            'DIGID_ACS_URL', 
            'DIGID_SLO_URL',
            'DIGID_CERTIFICATE_PATH',
            'DIGID_PRIVATE_KEY_PATH'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required DigiD environment variables: {', '.join(missing_vars)}")


class ProductionConfig(Config):
    """Конфигурация для production"""
    
    DEBUG = False
    
    # База данных для production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # DigiD для production (real DigiD)
    DIGID_MOCK_MODE = False
    DIGID_ENABLED = True
    DIGID_SESSION_TIMEOUT = 14400  # 4 hours
    
    # Production DigiD URLs
    DIGID_BASE_URL = os.environ.get('DIGID_BASE_URL', 'https://digid.nl')
    DIGID_AUTH_URL = os.environ.get('DIGID_AUTH_URL', 'https://digid.nl/auth')
    DIGID_LOGOUT_URL_EXTERNAL = os.environ.get('DIGID_LOGOUT_URL_EXTERNAL', 'https://digid.nl/logout')
    
    # Дополнительные настройки безопасности для production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def validate_digid_config(cls):
        """Валидация обязательных DigiD настроек для production"""
        required_vars = [
            'DIGID_ENTITY_ID',
            'DIGID_ACS_URL', 
            'DIGID_SLO_URL',
            'DIGID_CERTIFICATE_PATH',
            'DIGID_PRIVATE_KEY_PATH'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required DigiD environment variables: {', '.join(missing_vars)}")
        
        # Проверка существования файлов сертификатов
        cert_path = os.environ.get('DIGID_CERTIFICATE_PATH')
        key_path = os.environ.get('DIGID_PRIVATE_KEY_PATH')
        
        if cert_path and not os.path.exists(cert_path):
            raise ValueError(f"DigiD certificate file not found: {cert_path}")
        
        if key_path and not os.path.exists(key_path):
            raise ValueError(f"DigiD private key file not found: {key_path}")


# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Получить конфигурацию по имени"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = config.get(config_name, config['default'])
    
    # Валидация DigiD настроек для staging и production
    if config_name in ['staging', 'production']:
        config_class.validate_digid_config()
    
    return config_class


def validate_digid_environment():
    """Валидация DigiD окружения"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name in ['staging', 'production']:
        try:
            config_class = config[config_name]
            config_class.validate_digid_config()
            print(f"✅ DigiD configuration validated for {config_name}")
            return True
        except ValueError as e:
            print(f"❌ DigiD configuration error for {config_name}: {e}")
            return False
    else:
        print(f"ℹ️ DigiD mock mode enabled for {config_name}")
        return True


if __name__ == '__main__':
    # Тестирование конфигурации
    print("🔧 Testing DigiD configuration...")
    validate_digid_environment()
    
    # Показать текущую конфигурацию
    current_config = get_config()
    print(f"\n📋 Current configuration: {current_config.__name__}")
    print(f"   DigiD Enabled: {current_config.DIGID_ENABLED}")
    print(f"   DigiD Mock Mode: {current_config.DIGID_MOCK_MODE}")
    print(f"   DigiD Session Timeout: {current_config.DIGID_SESSION_TIMEOUT} seconds")
    print(f"   DigiD Base URL: {current_config.DIGID_BASE_URL}") 