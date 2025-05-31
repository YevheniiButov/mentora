# Конфигурация для мобильного приложения
# Вставьте сюда код конфигурации

class MobileConfig:
    """Конфигурация мобильного приложения"""
    
    # PWA настройки
    PWA_NAME = "Dental Academy"
    PWA_SHORT_NAME = "DentalAcademy"
    PWA_DESCRIPTION = "Master dental skills for BIG exam"
    PWA_THEME_COLOR = "#3ECDC1"
    PWA_BACKGROUND_COLOR = "#667eea"
    
    # Мобильные настройки
    MOBILE_CACHE_TIMEOUT = 3600  # 1 час
    MOBILE_API_RATE_LIMIT = "100/hour"
    MOBILE_OFFLINE_PAGES = [
        "/mobile/welcome",
        "/mobile/auth/login",
        "/mobile/learning/map"
    ]
    
    # Push уведомления
    PUSH_NOTIFICATIONS_ENABLED = True
    VAPID_PUBLIC_KEY = ""  # Вставьте ваш VAPID ключ
    VAPID_PRIVATE_KEY = ""  # Вставьте ваш приватный ключ
    
    # Аналитика
    MOBILE_ANALYTICS_ENABLED = True
    GOOGLE_ANALYTICS_ID = ""  # Вставьте ваш GA ID

# Вставьте сюда дополнительные настройки 