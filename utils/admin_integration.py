# utils/admin_integration.py
# Интеграция единой админ панели в Flask приложение

def register_unified_admin(app):
    """
    Регистрация единой админ панели в Flask приложении
    
    Args:
        app: Flask приложение
    """
    
    # Импортируем единую админку
    from routes.admin import admin_unified_bp
    
    # Регистрируем blueprint
    app.register_blueprint(admin_unified_bp)
    
    # Добавляем контекстные переменные для шаблонов
    @app.context_processor
    def inject_admin_vars():
        from flask_login import current_user
        
        # Определяем права доступа к админке
        admin_access = False
        if current_user.is_authenticated:
            admin_access = hasattr(current_user, 'is_admin') and current_user.is_admin
        
        return {
            'has_admin_access': admin_access,
            'admin_url': '/ru/admin/dashboard' if admin_access else None
        }
    
    print("✅ Единая админ панель успешно зарегистрирована!")
    print("📍 Доступ по адресу: /{lang}/admin/dashboard")
    print("🔐 Требуется роль: admin, super_admin, content_admin, user_admin")
    
    return True 