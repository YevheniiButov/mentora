# routes/main_routes.py

from flask import (
    Blueprint, render_template, g, request, current_app, session,
    redirect, url_for, flash, jsonify, abort
)
from flask_login import login_required, current_user
import os
import json
import random
from datetime import datetime
from mobile_integration import render_adaptive_template, mobile_template_manager  
from utils.mobile_detection import get_user_stats, get_app_stats, get_mobile_detector


from models import db, User, Module, Lesson, UserProgress

main_bp = Blueprint('main_bp', __name__, template_folder='../templates')

@main_bp.context_processor
def inject_lang():
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    return dict(lang=lang)

@main_bp.route('/')
def index():
    lang_to_use = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    return redirect(url_for('.home', lang=lang_to_use))

@main_bp.route('/<string:lang>/')
@main_bp.route('/<string:lang>/index')
@main_bp.route('/<string:lang>/home')
def home(lang):
    """
    Адаптивная главная страница с автоматическим выбором шаблона
    """
    # Проверяем валидность языка
    if lang not in current_app.config.get('SUPPORTED_LANGUAGES', ['en']):
        lang = current_app.config.get('DEFAULT_LANGUAGE', 'en')
    
    # Устанавливаем язык в g
    g.lang = lang
    g.current_language = lang  # Для совместимости с mobile_base.html
    
    # Получаем статистику
    stats = get_app_stats()
    user_data = get_user_stats()
    
    # Получаем информацию об устройстве
    detector = get_mobile_detector()
    
    # Отладочная информация
    print(f"🏠 Home route called with lang: {lang}")
    print(f"📱 Is mobile device: {detector.is_mobile_device}")
    print(f"👤 User authenticated: {current_user.is_authenticated}")
    
    # ВАЖНО: Используем адаптивный рендеринг через систему mobile_integration
    return render_adaptive_template(
        'index.html',  # ← ВАЖНО: указываем index.html, система сама выберет welcome_mobile.html для мобильных
        stats=stats,
        user_data=user_data,
        current_language=lang,
        supported_languages=current_app.config.get('SUPPORTED_LANGUAGES', []),
        # Дополнительные переменные для mobile_base.html
        has_pending_tests=False,
        get_country_code=lambda code: {
            'en': 'gb', 'nl': 'nl', 'ru': 'ru', 'uk': 'ua',
            'es': 'es', 'pt': 'pt', 'tr': 'tr', 'fa': 'ir', 'ar': 'sa'
        }.get(code, code)
    )

@main_bp.route('/<string:lang>/set_language/<string:new_lang>')
def set_language(lang, new_lang):
    """
    Маршрут для переключения языка приложения
    """
    # Проверяем, что новый язык поддерживается
    if new_lang not in current_app.config.get('SUPPORTED_LANGUAGES', ['en']):
        new_lang = current_app.config.get('DEFAULT_LANGUAGE', 'en')
    
    # Обновляем язык в сессии
    session['lang'] = new_lang
    
    # Получаем URL для возврата (referer)
    referrer = request.referrer
    
    # Если referer есть и принадлежит нашему сайту, возвращаемся туда с новым языком
    if referrer:
        # Заменяем старый язык на новый в URL
        parts = referrer.split('/')
        for i, part in enumerate(parts):
            if part in current_app.config.get('SUPPORTED_LANGUAGES', ['en']):
                parts[i] = new_lang
                return redirect('/'.join(parts))
    
    # Если referer не определен или не удалось обработать, перенаправляем на главную
    return redirect(url_for('.home', lang=new_lang))

@main_bp.route("/<string:lang>/profile")
@login_required
def profile(lang):
    current_lang = getattr(g, 'lang', lang)
    user = current_user
    user_progress_list = []
    try:
        all_modules = Module.query.order_by(Module.id).all()
        completed_lesson_ids = { p.lesson_id for p in UserProgress.query.filter_by(user_id=user.id, completed=True).all() }
        for module in all_modules:
            lessons_in_module = Lesson.query.filter_by(module_id=module.id).with_entities(Lesson.id).all()
            lesson_ids_in_module = {lesson.id for lesson in lessons_in_module}
            total_lessons = len(lesson_ids_in_module)
            completed_lessons_count = len(lesson_ids_in_module.intersection(completed_lesson_ids))
            percentage = int((completed_lessons_count / total_lessons * 100)) if total_lessons > 0 else 0
            user_progress_list.append({
                'id': module.id,
                'title': module.title,
                'completed_lessons': completed_lessons_count,
                'total_lessons': total_lessons,
                'percentage': percentage
            })
    except Exception as e:
        current_app.logger.error(f"Error calculating progress for user {user.id}: {e}", exc_info=True)
        flash("Could not load learning progress.", "warning")
        user_progress_list = []
    return render_template("profile/profile.html", user=user, progress=user_progress_list)


@main_bp.route("/<string:lang>/learn")
@login_required
def learn(lang):
    user = current_user
    categorized_modules = {}
    flash("Learn page content needs implementation.", "info")
    return render_template("learn.html", categories=categorized_modules, user=user)

@main_bp.route("/<string:lang>/big-info")
def big_info(lang):
    return render_template("big-info.html")

@main_bp.route('/<string:lang>/subscribe')
@login_required
def subscribe(lang):
    flash("Subscription page is not implemented yet.", "info")
    return redirect(url_for('.profile', lang=g.lang))

@main_bp.route('/<string:lang>/demo')
def demo(lang):
    return render_template('demo.html', title='Demo')

# ========== XRAY PUBLIC ROUTES ==========
@main_bp.route('/<string:lang>/xray-index')
def xray_index(lang):
    xray_dir = os.path.join(current_app.static_folder, 'xray')
    files = []
    if os.path.exists(xray_dir):
        for f in os.listdir(xray_dir):
            if f.endswith(('.jpg', '.jpeg')):
                path = os.path.join(xray_dir, f)
                files.append({"filename": f, "size": os.path.getsize(path)})
    return render_template("xray_index.html", files=files, title="X-ray Cases")

@main_bp.route('/<string:lang>/xray-case/<filename>')
def xray_case(lang, filename):
    annotations_path = os.path.join(current_app.static_folder, 'annotations', 'annotations.json')
    region_list = []
    tasks = []
    try:
        with open(annotations_path) as f:
            annotations = json.load(f)["_via_img_metadata"]
            for key, data in annotations.items():
                if data["filename"] == filename:
                    for i, region in enumerate(data.get("regions", [])):
                        shape = region.get("shape_attributes", {})
                        attrs = region.get("region_attributes", {})
                        shape_name = shape.get("name")
                        if shape_name == "polyline":
                            x_points = shape.get("all_points_x", [])
                            y_points = shape.get("all_points_y", [])
                            if not x_points or not y_points:
                                continue
                            x_min = min(x_points)
                            y_min = min(y_points)
                            x_max = max(x_points)
                            y_max = max(y_points)
                            region_list.append({
                                "x": x_min,
                                "y": y_min,
                                "w": x_max - x_min,
                                "h": y_max - y_min,
                                "label": attrs.get("Teeth", f"Object {i+1}"),
                                "points_x": x_points,
                                "points_y": y_points,
                                "type": "polyline"
                            })
                            tasks.append({
                                "type": "identify",
                                "description": f"Найдите {attrs.get('Teeth', f'объект {i+1}')}",
                                "target_region": i
                            })
                        elif shape_name == "rect":
                            region_list.append({
                                "x": shape.get("x", 0),
                                "y": shape.get("y", 0),
                                "w": shape.get("width", 0),
                                "h": shape.get("height", 0),
                                "label": attrs.get("Teeth", f"Object {i+1}"),
                                "type": "rect"
                            })
                            tasks.append({
                                "type": "identify",
                                "description": f"Найдите {attrs.get('Teeth', f'объект {i+1}')}",
                                "target_region": i
                            })
                    break
    except Exception as e:
        current_app.logger.error(f"Error loading annotations for {filename}: {e}")
    if not tasks and region_list:
        tasks = [{"type": "identify", "description": "Найдите патологию", "target_region": 0}]
    return render_template("xray_case.html", filename=filename, regions=json.dumps(region_list), tasks=json.dumps(tasks), title="Рентген-диагностика")

@main_bp.route('/<string:lang>/xray-quiz')
def xray_quiz(lang):
    xray_dir = os.path.join(current_app.static_folder, 'xray')
    annotations_path = os.path.join(current_app.static_folder, 'annotations', 'annotations.json')
    quiz_items = []
    xray_files = []
    if os.path.exists(xray_dir):
        xray_files = [f for f in os.listdir(xray_dir) if f.lower().endswith('.jpg')]
    if os.path.exists(annotations_path):
        try:
            with open(annotations_path) as f:
                annotations = json.load(f)["_via_img_metadata"]
                for data in annotations.values():
                    filename = data["filename"]
                    if filename in xray_files:
                        tasks = []
                        boxes = []
                        for i, region in enumerate(data.get("regions", [])):
                            shape = region.get("shape_attributes", {})
                            attrs = region.get("region_attributes", {})
                            if shape.get("name") == "rect":
                                x, y, w, h = shape["x"], shape["y"], shape["width"], shape["height"]
                                boxes.append({"x": x, "y": y, "w": w, "h": h, "label": attrs.get("label", f"Object {i+1}")})
                                tasks.append({"type": attrs.get("task_type", "identify"), "description": attrs.get("description", f"Найдите объект {i+1}"), "target_region": i})
                        if tasks:
                            quiz_items.append({"filename": filename, "boxes": boxes, "tasks": tasks})
        except Exception as e:
            current_app.logger.error(f"Ошибка при загрузке аннотаций для викторины: {e}")
    random.shuffle(quiz_items)
    quiz_items = quiz_items[:5]
    return render_template("xray_quiz.html", quiz_items=json.dumps(quiz_items), title="Рентген-викторина")

@main_bp.route("/<string:lang>/save-profile", methods=["POST"])
@login_required
def save_profile(lang):
    """Сохраняет изменения профиля пользователя."""
    try:
        data = request.get_json()
        
        # Получаем данные из запроса
        name = data.get('name')
        email = data.get('email')
        preferred_language = data.get('preferred_language')
        
        # Проверяем данные
        if not name or not email:
            return jsonify({"status": "error", "message": "Name and email are required"}), 400
        
        # Обновляем данные пользователя
        user = current_user
        user.name = name
        user.email = email
        
        # Обновляем предпочитаемый язык, если есть модель для этого
        try:
            user_settings = UserSettings.query.filter_by(user_id=user.id).first()
            if not user_settings:
                user_settings = UserSettings(user_id=user.id)
                db.session.add(user_settings)
            
            user_settings.preferred_language = preferred_language
        except Exception as e:
            # Если нет модели UserSettings, просто обновляем сессию
            pass
        
        # Обновляем сессию с новым языком
        if preferred_language:
            session['lang'] = preferred_language
        
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving profile: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

# Тестовые роуты для проверки ошибок
@main_bp.route('/<string:lang>/test-404')
def test_404(lang):
    """Тестовый роут для проверки страницы 404."""
    abort(404)

@main_bp.route('/<string:lang>/test-500')
def test_500(lang):
    """Тестовый роут для проверки страницы 500."""
    abort(500)