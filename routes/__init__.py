# Импорт всех blueprints для экспорта

# Основные маршруты
from .auth_routes import auth_bp
from .main_routes import main_bp
from .learning_map_routes import learning_map_bp
from .lesson_routes import lesson_bp
from .modules_routes import modules_bp
from .tests_routes import tests_bp
from .content_routes import content_bp
from .forum_routes import forum_bp
from .virtual_patient_routes import virtual_patient_bp
from .subject_view_routes import subject_view_bp
from .assessment_routes import assessment_bp

# API маршруты
from .api_routes import api_bp

# Административные маршруты
from .admin_routes import admin_bp
from .admin_unified import admin_unified_bp

# AI маршруты
from .ai_routes import ai_bp

# Мобильные маршруты
from .mobile_routes import mobile_bp

# Виртуальные пациенты API
from .virtual_patient_api import virtual_patient_api_bp

# Навигация контента
from .content_navigation import content_nav_bp

# Дашборд
from .dashboard_routes import dashboard_bp

# Экспорт всех blueprints
__all__ = [
    'auth_bp',
    'main_bp', 
    'learning_map_bp',
    'lesson_bp',
    'modules_bp',
    'tests_bp',
    'content_bp',
    'forum_bp',
    'virtual_patient_bp',
    'subject_view_bp',
    'assessment_bp',
    'api_bp',
    'admin_bp',
    'admin_unified_bp',
    'ai_bp',
    'mobile_bp',
    'virtual_patient_api_bp',
    'content_nav_bp',
    'dashboard_bp'
]
