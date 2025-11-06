# routes/content_routes.py
# Универсальные роуты для навигации по контенту

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, g, current_app, abort
from flask_login import login_required, current_user
from sqlalchemy import func
import json

from models import db, ContentCategory, ContentSubcategory, ContentTopic, Lesson, UserProgress, LearningPath, Subject, Module
from utils.translations import t
from utils.unified_stats import track_lesson_progress

# Создаем blueprint для контента
content_bp = Blueprint('content', __name__, url_prefix='/<lang>/content')

# Импортируем CSRF из основного приложения
from extensions import csrf

@content_bp.before_request
def before_request_content():
    """Обработка языка для всех маршрутов контента"""
    if hasattr(g, 'lang'):
        pass  # Язык уже установлен в middleware
    else:
        g.lang = request.view_args.get('lang', 'en')

@content_bp.context_processor
def inject_lang_content():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    return dict(lang=getattr(g, 'lang', 'en'))

# ================== УНИВЕРСАЛЬНЫЕ РОУТЫ ==================

@content_bp.route("/")
@login_required
def content_home(lang):
    """Главная страница контента - показывает все категории"""
    try:
        categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        # Добавляем статистику для каждой категории
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
            title=t('content_categories', lang),
            categories=categories,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в content_home: {e}", exc_info=True)
        flash(t("error_loading_content", lang), "danger")
        return redirect(f'/{lang}/')

@content_bp.route("/category/<category_slug>")
@login_required
def view_category(category_slug):
    """Просмотр категории и её подкатегорий"""
    try:
        category = ContentCategory.query.filter_by(slug=category_slug).first_or_404()
        subcategories = category.subcategories.order_by(ContentSubcategory.order).all()
        
        # Добавляем статистику для каждой подкатегории
        for subcat in subcategories:
            subcat.topics_count = subcat.topics.count()
            subcat.total_lessons = 0
            subcat.completed_lessons = 0
            
            for topic in subcat.topics:
                topic_lessons_count = topic.lessons.count()
                subcat.total_lessons += topic_lessons_count
                
                # Подсчитываем завершенные уроки
                if topic_lessons_count > 0:
                    lesson_ids = [lesson.id for lesson in topic.lessons]
                    completed_count = UserProgress.query.filter(
                        UserProgress.user_id == current_user.id,
                        UserProgress.lesson_id.in_(lesson_ids),
                        UserProgress.completed == True
                    ).count()
                    subcat.completed_lessons += completed_count
            
            # Вычисляем прогресс подкатегории
            if subcat.total_lessons > 0:
                subcat.progress = round((subcat.completed_lessons / subcat.total_lessons) * 100)
            else:
                subcat.progress = 0
        
        return render_template(
            "content/category_view.html",
            title=category.name,
            category=category,
            subcategories=subcategories,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_category ({category_slug}): {e}", exc_info=True)
        flash(t("error_loading_category", lang), "danger")
        return redirect(url_for('.content_home', lang=lang))

@content_bp.route("/category/<category_slug>/<subcategory_slug>")
@login_required
def view_subcategory(category_slug, subcategory_slug):
    """Просмотр подкатегории и её тем"""
    try:
        category = ContentCategory.query.filter_by(slug=category_slug).first_or_404()
        subcategory = ContentSubcategory.query.filter_by(
            slug=subcategory_slug, 
            category_id=category.id
        ).first_or_404()
        
        topics = subcategory.topics.order_by(ContentTopic.order).all()
        
        # Добавляем статистику для каждой темы
        for topic in topics:
            topic.lessons_count = topic.lessons.count()
            topic.completed_lessons = 0
            
            if topic.lessons_count > 0:
                lesson_ids = [lesson.id for lesson in topic.lessons]
                topic.completed_lessons = UserProgress.query.filter(
                    UserProgress.user_id == current_user.id,
                    UserProgress.lesson_id.in_(lesson_ids),
                    UserProgress.completed == True
                ).count()
                
                topic.progress = round((topic.completed_lessons / topic.lessons_count) * 100)
            else:
                topic.progress = 0
        
        return render_template(
            "content/subcategory_view.html",
            title=subcategory.name,
            category=category,
            subcategory=subcategory,
            topics=topics,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_subcategory ({category_slug}/{subcategory_slug}): {e}", exc_info=True)
        flash(t("error_loading_subcategory", lang), "danger")
        return redirect(url_for('.view_category', lang=lang, category_slug=category_slug))

@content_bp.route("/category/<category_slug>/<subcategory_slug>/<topic_slug>")
@login_required
def view_topic(category_slug, subcategory_slug, topic_slug):
    """Просмотр темы и её уроков"""
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
        
        # Добавляем прогресс для каждого урока
        for lesson in lessons:
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            lesson.is_completed = progress.completed if progress else False
            # Рассчитываем процент прогресса на основе времени или статуса
            if progress and progress.completed:
                lesson.progress_percentage = 100
            elif progress and progress.time_spent:
                lesson.progress_percentage = min(int(progress.time_spent / 10 * 100), 99)  # Примерный расчет
            else:
                lesson.progress_percentage = 0
        
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
        current_app.logger.error(f"Ошибка в view_topic ({category_slug}/{subcategory_slug}/{topic_slug}): {e}", exc_info=True)
        flash(t("error_loading_topic", lang), "danger")
        return redirect(url_for('.view_subcategory', lang=lang, category_slug=category_slug, subcategory_slug=subcategory_slug))

@content_bp.route("/lesson/<int:lesson_id>")
@login_required
def view_lesson(lesson_id):
    """Просмотр конкретного урока"""
    print(f"🚀 ВЫЗВАН content_routes.view_lesson: lesson_id={lesson_id}, user_id={current_user.id}")
    current_app.logger.info(f"🚀 ВЫЗВАН content_routes.view_lesson: lesson_id={lesson_id}, user_id={current_user.id}")
    
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        print(f"✅ Урок найден: {lesson.title}")
        
        # Получаем связанную тему (если есть)
        topic = None
        category = None
        subcategory = None
        
        if hasattr(lesson, 'content_topic_id') and lesson.content_topic_id:
            topic = ContentTopic.query.get(lesson.content_topic_id)
            if topic:
                subcategory = topic.content_subcategory
                category = subcategory.content_category if subcategory else None
        
        # Получаем прогресс пользователя
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        is_completed = progress.completed if progress else False
        # Рассчитываем процент прогресса на основе времени или статуса
        if progress and progress.completed:
            progress_percentage = 100
        elif progress and progress.time_spent:
            progress_percentage = min(int(progress.time_spent / 10 * 100), 99)  # Примерный расчет
        else:
            progress_percentage = 0
        
        print(f"📊 Текущий прогресс: completed={is_completed}, percentage={progress_percentage}")
        
        # Парсим контент урока
        lesson_content = None
        if lesson.content:
            try:
                lesson_content = json.loads(lesson.content)
            except:
                lesson_content = {"error": "Ошибка парсинга контента"}
        
        print(f"🔥 ВЫЗЫВАЕМ track_lesson_progress для урока {lesson_id}")
        track_lesson_progress(current_user.id, lesson_id)
        
        return render_template(
            "content/lesson_view.html",
            title=lesson.title,
            lesson=lesson,
            lesson_content=lesson_content,
            category=category,
            subcategory=subcategory,
            topic=topic,
            is_completed=is_completed,
            progress_percentage=progress_percentage,
            user=current_user
        )
        
    except Exception as e:
        print(f"❌ ОШИБКА в content_routes.view_lesson: {e}")
        current_app.logger.error(f"Ошибка в view_lesson ({lesson_id}): {e}", exc_info=True)
        flash(t("error_loading_lesson", lang), "danger")
        return redirect(url_for('.content_home', lang=lang))

# ================== API РОУТЫ ==================

@content_bp.route("/api/lesson/<int:lesson_id>/complete", methods=['POST'])
@login_required
@csrf.exempt
def complete_lesson(lesson_id):
    """Отметить урок как завершенный"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Получаем язык из контекста
        lang = getattr(g, 'lang', 'en')
        
        # Используем унифицированную функцию для отслеживания прогресса
        track_lesson_progress(current_user.id, lesson_id, completed=True)
        
        return jsonify({
            'success': True,
            'message': t('lesson_completed', lang)
        })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в complete_lesson ({lesson_id}): {e}", exc_info=True)
        lang = getattr(g, 'lang', 'en')
        return jsonify({
            'success': False,
            'message': t('error_completing_lesson', lang)
        }), 500

@content_bp.route("/api/lesson/<int:lesson_id>/next", methods=['GET'])
@login_required
def get_next_lesson(lesson_id):
    """Получить следующий урок"""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        lang = getattr(g, 'lang', 'en')
        
        # Получаем все уроки в той же теме, отсортированные по порядку
        if lesson.topic_id:
            lessons = Lesson.query.filter_by(topic_id=lesson.topic_id).order_by(Lesson.order).all()
        else:
            # Если нет topic_id, ищем по module_id
            lessons = Lesson.query.filter_by(module_id=lesson.module_id).order_by(Lesson.order).all()
        
        # Находим индекс текущего урока
        current_index = -1
        for i, l in enumerate(lessons):
            if l.id == lesson_id:
                current_index = i
                break
        
        # Получаем следующий урок
        next_lesson = None
        if current_index >= 0 and current_index < len(lessons) - 1:
            next_lesson = lessons[current_index + 1]
        
        if next_lesson:
            return jsonify({
                'success': True,
                'next_lesson': {
                    'id': next_lesson.id,
                    'title': next_lesson.title,
                    'url': url_for('content.view_lesson', lesson_id=next_lesson.id, lang=lang)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': t('no_next_lesson', lang),
                'is_last': True
            })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_next_lesson ({lesson_id}): {e}", exc_info=True)
        lang = getattr(g, 'lang', 'en')
        return jsonify({
            'success': False,
            'message': t('error_getting_next_lesson', lang)
        }), 500

# ================== ПОИСК ==================

@content_bp.route("/search")
@login_required
def search_content(lang):
    """Поиск по контенту"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template(
            "content/search_results.html",
            title=t('search_content', lang),
            query='',
            results=[],
            user=current_user
        )
    
    try:
        # Поиск по категориям
        categories = ContentCategory.query.filter(
            ContentCategory.name.ilike(f'%{query}%')
        ).all()
        
        # Поиск по подкатегориям
        subcategories = ContentSubcategory.query.filter(
            ContentSubcategory.name.ilike(f'%{query}%')
        ).all()
        
        # Поиск по темам
        topics = ContentTopic.query.filter(
            ContentTopic.name.ilike(f'%{query}%')
        ).all()
        
        # Поиск по урокам
        lessons = Lesson.query.filter(
            Lesson.title.ilike(f'%{query}%')
        ).limit(20).all()
        
        results = {
            'categories': categories,
            'subcategories': subcategories,
            'topics': topics,
            'lessons': lessons
        }
        
        return render_template(
            "content/search_results.html",
            title=f"{t('search_results', lang)}: {query}",
            query=query,
            results=results,
            user=current_user
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка поиска ({query}): {e}", exc_info=True)
        flash(t("error_search", lang), "danger")
        return redirect(url_for('.content_home', lang=lang)) 