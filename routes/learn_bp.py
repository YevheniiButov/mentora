# routes/lesson_routes.py
from flask import Blueprint, render_template, redirect, url_for, g, flash, current_app, request
from flask_login import login_required, current_user
from models import db, Lesson, Module, UserProgress
from utils.unified_stats import track_lesson_progress
import json

# Создаем Blueprint
lesson_bp = Blueprint(
    "lesson_bp",
    __name__,
    url_prefix='/<string:lang>/modules/<int:module_id>/lessons',
    template_folder='../templates'
)

@lesson_bp.context_processor
def inject_lesson_context():
    """Добавляем язык в контекст шаблонов."""
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    return dict(lang=lang)

@lesson_bp.route("/<int:lesson_index>", methods=["GET", "POST"])
@login_required
def lesson_view(lang, module_id, lesson_index):
    """Отображает урок по индексу в модуле."""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Проверяем доступность модуля (премиум проверка)
        if module.is_premium and not current_user.has_subscription:
            flash("Этот модуль доступен только для премиум-подписчиков", "warning")
            return redirect(url_for('modules_bp.modules_list', lang=lang))
        
        # Получаем все уроки для модуля, сортируем по порядку
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        total_lessons = len(lessons)
        
        # Проверяем индекс урока
        if lesson_index < 0 or lesson_index >= total_lessons:
            flash("Урок не найден", "danger")
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
        
        # Получаем текущий урок
        lesson = lessons[lesson_index]
        
        # Обработка формы квиза
        quiz_result = None
        if request.method == "POST" and lesson.quiz:
            # Здесь логика обработки ответов на квиз
            # ...
            pass
        
        # Отслеживаем прогресс урока
        track_lesson_progress(current_user.id, lesson.id)
        
        # Перенесенный шаблон
        return render_template(
            "learning/lesson.html",
            module=module,
            lesson=lesson,
            lesson_index=lesson_index,
            total_lessons=total_lessons,
            quiz_result=quiz_result
        )
    except Exception as e:
        current_app.logger.error(f"Error in lesson_view: {e}", exc_info=True)
        flash(f"Ошибка при загрузке урока: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))