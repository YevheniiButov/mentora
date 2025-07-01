# routes/content_navigation.py
# Универсальные роуты для навигации по контенту

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, current_app
from flask_login import login_required, current_user
from models import db, ContentCategory, ContentSubcategory, ContentTopic, Lesson, UserProgress
from utils.unified_stats import track_lesson_progress
import json

# Создаем blueprint для контента
content_nav_bp = Blueprint('content_nav', __name__, url_prefix='/<lang>/learn')

@content_nav_bp.before_request
def before_request():
    """Обработка языка"""
    g.lang = request.view_args.get('lang', 'en')

@content_nav_bp.context_processor
def inject_lang():
    """Добавляет lang в контекст"""
    return dict(lang=getattr(g, 'lang', 'en'))

@content_nav_bp.route("/")
@login_required
def categories_list(lang):
    """Список всех категорий"""
    try:
        categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        # Добавляем статистику
        for category in categories:
            category.subcategories_count = category.subcategories.count()
            category.total_topics = 0
            category.total_lessons = 0
            
            for subcat in category.subcategories:
                category.total_topics += subcat.topics.count()
                for topic in subcat.topics:
                    category.total_lessons += topic.lessons.count()
        
        return render_template(
            "content/categories_list.html",
            title="Категории обучения",
            categories=categories,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в categories_list: {e}", exc_info=True)
        flash("Ошибка загрузки категорий", "danger")
        return redirect(url_for('main_bp.index', lang=lang))

@content_nav_bp.route("/<category_slug>")
@login_required  
def view_category(lang, category_slug):
    """Просмотр категории"""
    try:
        category = ContentCategory.query.filter_by(slug=category_slug).first_or_404()
        subcategories = category.subcategories.order_by(ContentSubcategory.order).all()
        
        return render_template(
            "content/category_view.html",
            title=category.name,
            category=category,
            subcategories=subcategories,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_category: {e}", exc_info=True)
        flash("Ошибка загрузки категории", "danger")
        return redirect(url_for('.categories_list', lang=lang))

@content_nav_bp.route("/<category_slug>/<subcategory_slug>")
@login_required
def view_subcategory(lang, category_slug, subcategory_slug):
    """Просмотр подкатегории"""
    try:
        category = ContentCategory.query.filter_by(slug=category_slug).first_or_404()
        subcategory = ContentSubcategory.query.filter_by(
            slug=subcategory_slug, 
            category_id=category.id
        ).first_or_404()
        
        topics = subcategory.topics.order_by(ContentTopic.order).all()
        
        return render_template(
            "content/subcategory_view.html",
            title=subcategory.name,
            category=category,
            subcategory=subcategory,
            topics=topics,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_subcategory: {e}", exc_info=True)
        flash("Ошибка загрузки подкатегории", "danger")
        return redirect(url_for('.view_category', lang=lang, category_slug=category_slug))

@content_nav_bp.route("/<category_slug>/<subcategory_slug>/<topic_slug>")
@login_required
def view_topic(lang, category_slug, subcategory_slug, topic_slug):
    """Просмотр темы"""
    try:
        category = ContentCategory.query.filter_by(slug=category_slug).first_or_404()
        subcategory = ContentSubcategory.query.filter_by(
            slug=subcategory_slug, 
            category_id=category.id
        ).first_or_404()
        topic = ContentTopic.query.filter_by(
            slug=topic_slug,
            subcategory_id=subcategory.id
        ).first_or_404()
        
        lessons = topic.lessons.order_by(Lesson.order).all()
        
        return render_template(
            "content/topic_view.html",
            title=topic.name,
            category=category,
            subcategory=subcategory,
            topic=topic,
            lessons=lessons,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_topic: {e}", exc_info=True)
        flash("Ошибка загрузки темы", "danger")
        return redirect(url_for('.view_subcategory', lang=lang, category_slug=category_slug, subcategory_slug=subcategory_slug))

@content_nav_bp.route("/lesson/<int:lesson_id>")
@login_required
def view_lesson(lang, lesson_id):
    """Просмотр урока"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Получаем связанную тему
        topic = None
        category = None
        subcategory = None
        
        if hasattr(lesson, 'topic_id') and lesson.topic_id:
            topic = ContentTopic.query.get(lesson.topic_id)
            if topic:
                subcategory = topic.content_subcategory
                category = subcategory.content_category if subcategory else None
        
        # Парсим контент
        lesson_content = None
        if lesson.content:
            try:
                lesson_content = json.loads(lesson.content)
            except:
                lesson_content = {"error": "Ошибка парсинга контента"}
        
        # Отслеживаем прогресс урока
        track_lesson_progress(current_user.id, lesson_id)
        
        return render_template(
            "content/lesson_view.html",
            title=lesson.title,
            lesson=lesson,
            lesson_content=lesson_content,
            category=category,
            subcategory=subcategory,
            topic=topic,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_lesson: {e}", exc_info=True)
        flash("Ошибка загрузки урока", "danger")
        return redirect(url_for('.categories_list', lang=lang))
