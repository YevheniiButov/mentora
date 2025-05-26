# routes/dashboard_routes.py

from flask import Blueprint, render_template, redirect, url_for, g, request, flash, jsonify, session, current_app
from flask_login import login_required, current_user
from models import db, User, Module, Lesson, UserProgress
from datetime import datetime
import traceback

# Создаем blueprint
dashboard_bp = Blueprint(
    "dashboard_bp",
    __name__,
    url_prefix='/<string:lang>/dashboard',
    template_folder='../templates'
)

# Языковые и защитные обработчики
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
DEFAULT_LANGUAGE = 'en'

@dashboard_bp.before_request
def before_request_dashboard():
    """
    Извлекает и валидирует язык из URL.
    """
    # Получаем lang из аргументов URL
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
    # Валидация и установка языка в g
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        # Если в URL нет валидного языка, берем из сессии или accept_languages
        g.lang = session.get('lang') \
                 or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                 or DEFAULT_LANGUAGE

    # Обновляем сессию, если язык отличается
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@dashboard_bp.context_processor
def inject_lang_dashboard():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

# Главный маршрут дашборда
@dashboard_bp.route("/")
@login_required
def learning_dashboard(lang):
    """Отображает дашборд обучения пользователя."""
    current_lang = g.lang
    
    try:
        # Получаем статистику обучения пользователя
        stats = get_user_stats(current_user.id)
        
        # Получаем рекомендуемый модуль
        recommended_module = get_recommended_module(current_user.id)
        
        # Получаем недавние модули пользователя
        recent_modules = get_recent_modules(current_user.id)
        
        return render_template(
            "learning/dashboard.html",
            title='Learning Dashboard',
            stats=stats,
            recommended_module=recommended_module,
            recent_modules=recent_modules,
            user=current_user  # Добавляем current_user в шаблон
        )
    except Exception as e:
        current_app.logger.error(f"Общая ошибка при загрузке дашборда: {str(e)}", exc_info=True)
        flash(f"Произошла ошибка при загрузке дашборда: {str(e)}", "danger")
        return redirect(url_for('main_bp.home', lang=current_lang))

# Функция для получения статистики пользователя
def get_user_stats(user_id):
    """Получает статистику обучения пользователя"""
    try:
        # Используем существующую функцию из learning_map_routes.py
        from routes.learning_map_routes import get_user_stats as get_map_user_stats
        stats = get_map_user_stats(user_id)
        
        # Получаем дату экзамена из сессии, если она есть
        if 'exam_date' in session:
            # Пытаемся форматировать дату более красиво
            try:
                date_obj = datetime.strptime(session['exam_date'], '%Y-%m-%d').date()
                stats['next_exam_date'] = date_obj.strftime('%d.%m.%Y')
            except:
                stats['next_exam_date'] = session['exam_date']
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении статистики: {str(e)}", exc_info=True)
        # Возвращаем пустые данные, если возникла ошибка
        return {
            'overall_progress': 0,
            'completed_lessons': 0,
            'total_lessons': 0,
            'total_time_spent': 0,
            'active_days': 0,
            'next_exam_date': None
        }

def get_recommended_module(user_id):
    """Получает рекомендуемый модуль для пользователя"""
    try:
        # Находим модуль с наибольшим прогрессом, но не завершенный
        modules = Module.query.all()
        best_module = None
        highest_progress = -1
        
        for module in modules:
            # Получаем статистику модуля
            from routes.learning_map_routes import get_module_stats
            stats = get_module_stats(module.id, user_id)
            
            # Если прогресс больше 0%, но меньше 100%, и больше предыдущего
            if 0 < stats["progress"] < 100 and stats["progress"] > highest_progress:
                highest_progress = stats["progress"]
                best_module = module
        
        # Если не нашли модуль с прогрессом, берем первый модуль
        if not best_module and modules:
            best_module = modules[0]
            
        # Если есть модуль, добавляем к нему информацию о прогрессе
        if best_module:
            from routes.learning_map_routes import get_module_stats
            module_stats = get_module_stats(best_module.id, user_id)
            return {
                'id': best_module.id,
                'title': best_module.title,
                'description': best_module.description if hasattr(best_module, 'description') else '',
                'progress': module_stats['progress'],
                'completed_lessons': module_stats['completed_lessons'],
                'total_lessons': module_stats['total_lessons']
            }
        
        return None
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении рекомендуемого модуля: {str(e)}", exc_info=True)
        return None

def get_recent_modules(user_id, limit=4):
    """Получает недавно использованные модули пользователя"""
    try:
        # Получаем все записи прогресса пользователя
        progress_entries = UserProgress.query.filter_by(
            user_id=user_id
        ).order_by(UserProgress.last_accessed.desc()).all()
        
        # Собираем уникальные module_id
        module_ids = []
        for entry in progress_entries:
            if hasattr(entry, 'lesson') and entry.lesson and entry.lesson.module_id not in module_ids:
                module_ids.append(entry.lesson.module_id)
                if len(module_ids) >= limit:
                    break
        
        # Если нет записей прогресса, просто получаем первые модули
        if not module_ids:
            modules = Module.query.limit(limit).all()
            module_ids = [module.id for module in modules]
        
        # Получаем модули с прогрессом
        recent_modules = []
        for module_id in module_ids:
            module = Module.query.get(module_id)
            if module:
                from routes.learning_map_routes import get_module_stats
                module_stats = get_module_stats(module.id, user_id)
                recent_modules.append({
                    'id': module.id,
                    'title': module.title,
                    'icon': module.icon if hasattr(module, 'icon') else 'book',
                    'progress': module_stats['progress']
                })
        
        return recent_modules
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении недавних модулей: {str(e)}", exc_info=True)
        return []

# API-маршрут для сохранения даты экзамена
@dashboard_bp.route("/api/save_exam_date", methods=["POST"])
@login_required
def save_exam_date(lang):
    """Сохраняет дату экзамена для пользователя."""
    try:
        data = request.get_json()
        exam_date = data.get('examDate')
        
        if not exam_date:
            return jsonify({"status": "error", "message": "Дата не указана"})
        
        # Сохраняем дату в сессии
        session['exam_date'] = exam_date
        
        return jsonify({"status": "success"})
    except Exception as e:
        current_app.logger.error(f"Ошибка при сохранении даты экзамена: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)})