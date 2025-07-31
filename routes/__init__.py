# routes package 

# Импорт роутов системы обучения
from .subject_view_routes import subject_view_bp
from .learning_map_routes import learning_map_bp, profession_map_bp
from .lesson_routes import lesson_bp
from .modules_routes import modules_bp
from .content_navigation import content_nav_bp
from .content_routes import content_bp
from .ai_assistant_routes import ai_assistant_bp

# Импорт роутов аутентификации
from .auth_routes import auth_bp
from .digid_routes import digid_bp

# Импорт административных роутов
from .admin_routes import admin_bp

# Импорт основных роутов
from .main_routes import main_bp
from .dashboard_routes import dashboard_bp

# Импорт роутов виртуальных пациентов
from .virtual_patient_routes import virtual_patient_bp

# Импорт фармацевтических инструментов
from .learning_routes import pharmacy_tools_bp

def register_blueprints(app):
    """Регистрирует все blueprints приложения"""
    # Основные роуты
    app.register_blueprint(main_bp)
    
    # Система обучения
    app.register_blueprint(learning_map_bp)
    app.register_blueprint(profession_map_bp)  # Новый blueprint для профессиональных карт
    app.register_blueprint(subject_view_bp)
    app.register_blueprint(lesson_bp)
    # app.register_blueprint(modules_bp)  # Регистрируется в app.py
    app.register_blueprint(content_nav_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(ai_assistant_bp)
    
    # Аутентификация
    app.register_blueprint(auth_bp)
    app.register_blueprint(digid_bp)
    
    # Административные функции
    app.register_blueprint(admin_bp)
    
    # Дашборд
    app.register_blueprint(dashboard_bp)
    
    # Виртуальные пациенты
    app.register_blueprint(virtual_patient_bp)
    
    # Фармацевтические инструменты
    app.register_blueprint(pharmacy_tools_bp) 