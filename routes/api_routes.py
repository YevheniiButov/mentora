# routes/api_routes.py
import json
from flask import Blueprint, jsonify, g, request, current_app, session
from flask_login import login_required, current_user
from models import db, Lesson, UserProgress, Module, ContentTopic, ContentSubcategory, User, UserExamDate, ContentCategory, UserStats
from translations_new import get_translation as t
from datetime import datetime
from extensions import csrf
import logging
from utils.unified_stats import get_unified_user_stats, clear_stats_cache

# Создаем Blueprint с префиксом /<lang>/api
api_bp = Blueprint(
    "api_bp",
    __name__,
    url_prefix='/<string:lang>/api')

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

# Базовые переводы для сплеш-скрина и гайда
SPLASH_GUIDE_TRANSLATIONS = {
    'en': {
        'splash': {
            'loading_steps': [
                'Initializing learning system...',
                'Loading study materials...',
                'Preparing interactive elements...',
                'Almost ready...',
                'Welcome!'
            ],
            'quotes': [
                "Every step in learning brings you closer to your dream of becoming an excellent dentist"
            ]
        },
        'guide': {
            'welcome_title': '🎓 Welcome to Dental Academy!',
            'welcome_subtitle': "Let's quickly get acquainted with the platform",
            'navigation': {
                'prev': '← Back',
                'next': 'Next →',
                'start': 'Start learning!',
                'skip': 'Skip guide',
                'dont_show': "Don't show again"
            }
        }
    },
    'ru': {
        'splash': {
            'loading_steps': [
                'Инициализация системы обучения...',
                'Загрузка учебных материалов...',
                'Подготовка интерактивных элементов...',
                'Почти готово...',
                'Добро пожаловать!'
            ],
            'quotes': [
                "Каждый шаг в обучении приближает вас к мечте стать отличным стоматологом"
            ]
        },
        'guide': {
            'welcome_title': '🎓 Добро пожаловать в Dental Academy!',
            'welcome_subtitle': 'Давайте быстро познакомимся с платформой',
            'navigation': {
                'prev': '← Назад',
                'next': 'Далее →',
                'start': 'Начать обучение!',
                'skip': 'Пропустить гайд',
                'dont_show': 'Больше не показывать'
            }
        }
    },
    'nl': {
        'splash': {
            'loading_steps': [
                'Leersysteem initialiseren...',
                'Studiemateriaal laden...',
                'Interactieve elementen voorbereiden...',
                'Bijna klaar...',
                'Welkom!'
            ],
            'quotes': [
                "Elke stap in het leren brengt je dichter bij je droom om een uitstekende tandarts te worden"
            ]
        },
        'guide': {
            'welcome_title': '🎓 Welkom bij Dental Academy!',
            'welcome_subtitle': 'Laten we snel kennismaken met het platform',
            'navigation': {
                'prev': '← Terug',
                'next': 'Volgende →',
                'start': 'Begin met leren!',
                'skip': 'Gids overslaan',
                'dont_show': 'Niet meer tonen'
            }
        }
    }
}

@api_bp.before_request
def before_request_api():
    """Обработка языка для API роутов."""
    try:
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            g.lang = session.get('lang') or DEFAULT_LANGUAGE
        
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
    except Exception as e:
        current_app.logger.error(f"Error in before_request_api: {e}", exc_info=True)
        g.lang = DEFAULT_LANGUAGE

@api_bp.route('/splash-guide-translations', methods=['GET'])
def get_splash_guide_translations(lang):
    """Возвращает переводы для сплеш-гайда."""
    try:
        translations = {
            'splash': {
                'title': t('splash_title', lang),
                'description': t('splash_description', lang),
                'button': t('splash_button', lang)
            },
            'guide': {
                'title': t('guide_title', lang),
                'description': t('guide_description', lang),
                'button': t('guide_button', lang)
            }
        }
        return jsonify(translations)
    except Exception as e:
        current_app.logger.error(f"Error getting splash guide translations: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get translations'}), 500

@api_bp.route('/user-onboarding-status', methods=['GET'])
@login_required
def get_user_onboarding_status(lang):
    """Возвращает статус онбординга пользователя."""
    try:
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if user:
                return jsonify({
                    'onboarding_completed': user.onboarding_completed,
                    'guide_completed': user.guide_completed,
                    'skip_guides': user.skip_guides
                })
        
        # Если пользователь не авторизован, используем сессию
        return jsonify({
            'onboarding_completed': session.get('dental_academy_visited', False),
            'guide_completed': session.get('dental_academy_guide_completed', False),
            'skip_guides': session.get('dental_academy_skip_guides', False)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user onboarding status: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get onboarding status'}), 500

@api_bp.route('/complete-onboarding', methods=['POST'])
@login_required
def complete_onboarding(lang):
    """Отмечает завершение онбординга."""
    try:
        data = request.get_json()
        completed_splash = data.get('completed_splash', False)
        completed_guide = data.get('completed_guide', False)
        skip_future_guides = data.get('skip_future_guides', False)
        
        if completed_splash:
            session['dental_academy_visited'] = True
            
        if completed_guide:
            session['dental_academy_guide_completed'] = True
            
        if skip_future_guides:
            session['dental_academy_skip_guides'] = True
            
        # Если пользователь авторизован, сохраняем также в БД
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if user:
                if completed_splash:
                    user.onboarding_completed = True
                if completed_guide:
                    user.guide_completed = True
                if skip_future_guides:
                    user.skip_guides = True
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': t('onboarding_completed_successfully', lang) or 'Onboarding completed successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error completing onboarding: {e}", exc_info=True)
        return jsonify({'error': 'Failed to complete onboarding'}), 500

@api_bp.route('/reset-onboarding', methods=['POST'])
@login_required
def reset_onboarding():
    """Сбрасывает статус онбординга (для тестирования)."""
    try:
        # Очищаем сессию
        session.pop('dental_academy_visited', None)
        session.pop('dental_academy_guide_completed', None)
        session.pop('dental_academy_skip_guides', None)
        
        # Если пользователь авторизован, сбрасываем также в БД
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
            if user:
                user.onboarding_completed = False
                user.guide_completed = False
                user.skip_guides = False
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': t('onboarding_reset_successfully', g.lang) or 'Onboarding status reset successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error resetting onboarding: {e}", exc_info=True)
        return jsonify({'error': 'Failed to reset onboarding'}), 500

# --- API эндпоинты ---
@api_bp.route('/lessons-for-topic/<int:topic_id>')
@login_required
def get_lessons_for_topic(lang, topic_id):
    try:
        # Убедитесь, что импортированы нужные модели
        from models import ContentTopic, Lesson, UserProgress
        
        topic = ContentTopic.query.get_or_404(topic_id)
        lessons = Lesson.query.filter_by(content_topic_id=topic.id).all()
        
        lessons_data = []
        for lesson in lessons:
            # Получаем прогресс пользователя для урока
            progress = 0
            if current_user.is_authenticated:
                user_progress = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    lesson_id=lesson.id
                ).first()
                
                if user_progress and user_progress.completed:
                    progress = 100
                elif user_progress:
                    progress = 50  # В процессе
            
            lessons_data.append({
                'id': lesson.id,
                'title': lesson.title,
                'content_type': lesson.content_type,
                'progress': progress
            })
            
        return jsonify({
            'topic_name': topic.name,
            'lessons': lessons_data
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching lessons for topic {topic_id}: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route("/progress/<int:module_id>")
@login_required
def get_module_progress(lang, module_id):
    """Возвращает прогресс пользователя по урокам в модуле в виде JSON."""
    user_id = current_user.id

    # Получаем ID уроков для модуля
    lessons_query = Lesson.query.filter_by(module_id=module_id).with_entities(Lesson.id)
    lesson_ids = [item[0] for item in lessons_query.all()]

    if not lesson_ids:
        return jsonify({}), 404

    # Получаем записи прогресса для этих уроков для текущего пользователя
    progress_entries = UserProgress.query.filter(
        UserProgress.user_id == user_id,
        UserProgress.lesson_id.in_(lesson_ids)
    ).all()

    # Формируем словарь {lesson_id: percentage}
    progress_dict = {lesson_id: 0 for lesson_id in lesson_ids}
    for entry in progress_entries:
        if entry.completed:
            progress_dict[entry.lesson_id] = 100

    return jsonify(progress_dict)

@api_bp.route("/save-progress", methods=["POST"])
@login_required
def save_progress(lang):
    """
    Сохраняет прогресс урока (отмечает как пройденный) для текущего пользователя.
    Ожидает POST запрос с JSON вида: {"lesson_id": <id>}
    """
    data = request.get_json()
    current_app.logger.info(f"Получен запрос на сохранение прогресса: {data}")

    # Валидация входных данных
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON payload"}), 400

    lesson_id = data.get("lesson_id")
    if lesson_id is None:
        return jsonify({"status": "error", "message": "Missing 'lesson_id' in payload"}), 400

    try:
        # Пытаемся преобразовать lesson_id в int
        lesson_id_int = int(lesson_id)

        # Проверяем существование урока и получаем его модуль
        lesson = Lesson.query.get(lesson_id_int)
        if not lesson:
            return jsonify({"status": "error", "message": f"Lesson with ID {lesson_id_int} not found"}), 404

        # Получаем module_id для возврата статистики
        module_id = lesson.module_id
        module = Module.query.get(module_id)
        if not module:
            return jsonify({"status": "error", "message": f"Module with ID {module_id} not found"}), 404

        # Ищем или создаем запись прогресса
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id_int
        ).first()

        if not progress:
            # Создаем новую запись
            progress = UserProgress(
                user_id=current_user.id,
                lesson_id=lesson_id_int,
                completed=True,
                time_spent=data.get('time_spent', 0.0)
            )
            db.session.add(progress)
            message = "Progress created and marked as completed."
            status_code = 201  # Created
        else:
            # Обновляем существующую, если она не была завершена
            if not progress.completed:
                progress.completed = True
                message = "Progress marked as completed."
            else:
                message = "Lesson already completed."
            
            # Обновляем время, если оно предоставлено
            if 'time_spent' in data and data['time_spent'] is not None:
                try:
                    time_spent = float(data['time_spent'])
                    progress.add_time(time_spent)
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Invalid time_spent value: {data['time_spent']}")
            
            status_code = 200  # OK

        db.session.commit()
        current_app.logger.info(f"Progress saved for user {current_user.id}, lesson {lesson_id_int}. Message: {message}")

        # Очищаем кэш статистики пользователя
        try:
            from routes.learning_map_routes import clear_user_stats_cache
            clear_user_stats_cache(current_user.id)
        except ImportError:
            pass  # Игнорируем ошибки импорта

        # Рассчитываем текущую статистику модуля
        module_stats = calculate_module_stats(module_id, current_user.id)

        return jsonify({
            "status": "ok", 
            "message": message,
            "module_id": module_id,
            "module_title": module.title,
            "progress": module_stats
        }), status_code

    except ValueError:
        # Ошибка преобразования lesson_id в int
        return jsonify({"status": "error", "message": f"Invalid 'lesson_id' format: must be an integer"}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving progress for user {current_user.id}, lesson_id {lesson_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"An internal server error occurred: {str(e)}"}), 500

def calculate_module_stats(module_id, user_id):
    """Рассчитывает статистику модуля для пользователя."""
    try:
        # Получаем все уроки в модуле
        lessons = Lesson.query.filter_by(module_id=module_id).all()
        total_lessons = len(lessons)
        
        if total_lessons == 0:
            return {
                "progress": 0,
                "completed_lessons": 0,
                "total_lessons": 0
            }
        
        # Получаем завершенные уроки
        completed_lessons = 0
        lesson_ids = [lesson.id for lesson in lessons]
        
        # Более эффективный запрос для получения всех завершенных уроков за один раз
        completed_progress = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        ).all()
        
        completed_lesson_ids = {progress.lesson_id for progress in completed_progress}
        completed_lessons = len(completed_lesson_ids)
        
        # Рассчитываем прогресс
        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        return {
            "progress": round(progress),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        }
    except Exception as e:
        current_app.logger.error(f"Ошибка в calculate_module_stats: {str(e)}", exc_info=True)
        return {
            "progress": 0,
            "completed_lessons": 0,
            "total_lessons": 0
        }

@api_bp.route('/get-next-topics/<int:module_id>')
@login_required
def get_next_topics(lang, module_id):
    """Возвращает рекомендуемые следующие темы для изучения."""
    try:
        from models import Module, Subject, Lesson
        
        # Получаем текущий модуль
        current_module = Module.query.get_or_404(module_id)
        
        # Получаем другие модули того же предмета
        subject_modules = Module.query.filter_by(
            subject_id=current_module.subject_id
        ).filter(Module.id != module_id).order_by(Module.order).all()
        
        next_topics = []
        for module in subject_modules[:3]:  # Максимум 3 рекомендации
            # Подсчитываем прогресс модуля
            module_lessons = Lesson.query.filter_by(module_id=module.id).all()
            if module_lessons:
                completed_lessons = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    completed=True
                ).filter(UserProgress.lesson_id.in_([l.id for l in module_lessons])).count()
                
                progress = int((completed_lessons / len(module_lessons)) * 100)
            else:
                progress = 0
            
            next_topics.append({
                'id': module.id,
                'title': module.title,
                'description': module.description or '',
                'progress': progress,
                'is_premium': module.is_premium or False
            })
        
        return jsonify({
            'success': True,
            'next_topics': next_topics
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting next topics: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get next topics'}), 500

# Тестовый маршрут для отладки прогресса
@api_bp.route("/debug/progress")
@login_required
def debug_progress(lang):
    """Отладочный маршрут для проверки прогресса пользователя"""
    try:
        # Получаем все записи прогресса для текущего пользователя
        progress_entries = UserProgress.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).all()
        
        # Формируем результат
        result = {
            "user_id": current_user.id,
            "completed_lessons_count": len(progress_entries),
            "lessons": []
        }
        
        for entry in progress_entries:
            lesson = Lesson.query.get(entry.lesson_id)
            if lesson:
                result["lessons"].append({
                    "lesson_id": lesson.id,
                    "title": lesson.title,
                    "module_id": lesson.module_id
                })
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in debug_progress: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
    # routes/api_routes.py - добавить новые маршруты API

@api_bp.route("/hierarchy")
@login_required
def get_complete_hierarchy(lang):
    """Возвращает полную иерархию категорий, подкатегорий и тем"""
    try:
        categories = Category.query.order_by(Category.order).all()
        result = []
        
        for category in categories:
            cat_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'icon': category.icon,
                'subcategories': []
            }
            
            subcategories = Subcategory.query.filter_by(
                category_id=category.id
            ).order_by(Subcategory.order).all()
            
            for subcategory in subcategories:
                subcat_data = {
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'icon': subcategory.icon,
                    'topics': []
                }
                
                topics = Topic.query.filter_by(
                    subcategory_id=subcategory.id
                ).order_by(Topic.order).all()
                
                for topic in topics:
                    # Получаем прогресс по теме для пользователя
                    lessons_count = Lesson.query.filter_by(topic_id=topic.id).count()
                    completed_count = db.session.query(func.count(Lesson.id)).join(
                        UserProgress, 
                        and_(
                            UserProgress.lesson_id == Lesson.id,
                            UserProgress.user_id == current_user.id,
                            UserProgress.completed == True
                        )
                    ).filter(Lesson.topic_id == topic.id).scalar()
                    
                    progress = int((completed_count / lessons_count * 100)) if lessons_count > 0 else 0
                    
                    topic_data = {
                        'id': topic.id,
                        'name': topic.name,
                        'slug': topic.slug,
                        'description': topic.description,
                        'lessons_count': lessons_count,
                        'completed_count': completed_count,
                        'progress': progress
                    }
                    
                    subcat_data['topics'].append(topic_data)
                
                cat_data['subcategories'].append(subcat_data)
            
            result.append(cat_data)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting hierarchy: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@api_bp.route("/topic/<int:topic_id>/lessons")
@login_required
def get_topic_lessons(lang, topic_id):
    """Возвращает все уроки для выбранной темы с прогрессом пользователя"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        
        # Получаем уроки с прогрессом
        query = db.session.query(
            Lesson,
            UserProgress.completed,
            UserProgress.time_spent
        ).outerjoin(
            UserProgress,
            and_(
                UserProgress.lesson_id == Lesson.id,
                UserProgress.user_id == current_user.id
            )
        ).filter(Lesson.topic_id == topic_id).order_by(Lesson.order)
        
        lessons = []
        for lesson, completed, time_spent in query.all():
            lessons.append({
                'id': lesson.id,
                'title': lesson.title,
                'content_type': lesson.content_type,
                'cards_count': lesson.get_cards_count() if hasattr(lesson, 'get_cards_count') else 0,
                'completed': completed or False,
                'time_spent': time_spent or 0,
                'order': lesson.order
            })
        
        return jsonify({
            'topic': {
                'id': topic.id,
                'name': topic.name,
                'description': topic.description
            },
            'lessons': lessons
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting topic lessons: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

 # Маршрут для получения подкатегорий категории
@api_bp.route("/category/<int:category_id>/subcategories")
@login_required
def get_category_subcategories(lang, category_id):
    """Возвращает подкатегории для выбранной категории"""
    try:
        category = ContentCategory.query.get_or_404(category_id)
        subcategories = []
        
        for subcat in category.subcategories.order_by(ContentSubcategory.order):
            topics_count = ContentTopic.query.filter_by(subcategory_id=subcat.id).count()
            
            subcategories.append({
                'id': subcat.id,
                'name': subcat.name,
                'slug': subcat.slug,
                'icon': subcat.icon,
                'description': getattr(subcat, 'description', ''),
                'topics_count': topics_count
            })
        
        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name
            },
            'subcategories': subcategories
        })
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении подкатегорий: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Ошибка при получении подкатегорий: {str(e)}"
        }), 500

# Маршрут для получения тем подкатегории
@api_bp.route("/subcategory/<int:subcategory_id>/topics")
@login_required
def get_subcategory_topics(lang, subcategory_id):
    """Возвращает темы для выбранной подкатегории"""
    try:
        subcategory = ContentSubcategory.query.get_or_404(subcategory_id)
        topics = []
        
        for topic in subcategory.topics.order_by(ContentTopic.order):
            # Получение количества уроков для темы
            lessons_count = Lesson.query.filter_by(content_topic_id=topic.id).count()
            
            # Получение прогресса пользователя по теме
            completed_count = 0
            if lessons_count > 0:
                # Получаем ID всех уроков темы
                lesson_ids = [lesson.id for lesson in Lesson.query.filter_by(content_topic_id=topic.id)]
                
                # Получаем количество завершенных уроков
                completed_count = UserProgress.query.filter(
                    UserProgress.user_id == current_user.id,
                    UserProgress.lesson_id.in_(lesson_ids),
                    UserProgress.completed == True
                ).count()
            
            # Вычисляем прогресс в процентах
            progress = round((completed_count / lessons_count) * 100) if lessons_count > 0 else 0
            
            topics.append({
                'id': topic.id,
                'name': topic.name,
                'slug': topic.slug,
                'description': topic.description,
                'lessons_count': lessons_count,
                'completed_count': completed_count,
                'progress': progress
            })
        
        return jsonify({
            'success': True,
            'subcategory': {
                'id': subcategory.id,
                'name': subcategory.name
            },
            'topics': topics
        })
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении тем: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Ошибка при получении тем: {str(e)}"
        }), 500

# Маршрут для сохранения даты экзамена
@api_bp.route("/save-exam-date", methods=["POST"])
@login_required
def save_exam_date(lang):
    """Сохраняет выбранную дату экзамена пользователя"""
    try:
        data = request.get_json()
        if not data or 'exam_date' not in data:
            return jsonify({
                'success': False,
                'message': 'Дата экзамена не указана'
            }), 400
        
        exam_date = data['exam_date']
        
        # Поиск существующей записи
        user_exam_date = UserExamDate.query.filter_by(user_id=current_user.id).first()
        
        if user_exam_date:
            # Обновление существующей записи
            user_exam_date.exam_date = exam_date
        else:
            # Создание новой записи
            user_exam_date = UserExamDate(
                user_id=current_user.id,
                exam_date=exam_date
            )
            db.session.add(user_exam_date)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Дата экзамена успешно сохранена',
            'exam_date': exam_date,
            'formatted_date': datetime.strptime(exam_date, '%Y-%m-%d').strftime('%d.%m.%Y')
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при сохранении даты экзамена: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Ошибка при сохранении даты: {str(e)}"
        }), 500

@api_bp.route('/update-stats', methods=['POST'])
@login_required
@csrf.exempt
def update_stats(lang):
    """
    AJAX endpoint для обновления статистики в реальном времени
    Вызывается после завершения урока
    """
    try:
        # Очищаем кэш для текущего пользователя
        clear_stats_cache(current_user.id)
        
        # Получаем обновленную статистику
        stats = get_unified_user_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Статистика обновлена'
        })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка обновления статистики: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Ошибка обновления статистики: {str(e)}'
        }), 500

@api_bp.route('/test-progress/<int:lesson_id>', methods=['POST'])
@login_required
@csrf.exempt
def test_progress(lang, lesson_id):
    """
    Тестовый endpoint для проверки работы track_lesson_progress
    """
    try:
        print(f"🧪 ТЕСТОВЫЙ ВЫЗОВ track_lesson_progress: user={current_user.id}, lesson={lesson_id}")
        current_app.logger.info(f"🧪 ТЕСТОВЫЙ ВЫЗОВ track_lesson_progress: user={current_user.id}, lesson={lesson_id}")
        
        # Проверяем, существует ли урок
        lesson = Lesson.query.get_or_404(lesson_id)
        print(f"✅ Урок найден: {lesson.title}")
        
        # Вызываем track_lesson_progress
        result = track_lesson_progress(current_user.id, lesson_id, completed=True)
        
        # Получаем обновленную статистику
        stats = get_unified_user_stats(current_user.id)
        
        return jsonify({
            'success': result,
            'lesson_id': lesson_id,
            'lesson_title': lesson.title,
            'stats': stats,
            'message': 'Тестовый вызов track_lesson_progress выполнен'
        })
        
    except Exception as e:
        print(f"❌ ОШИБКА в тестовом endpoint: {e}")
        current_app.logger.error(f"❌ ОШИБКА в test_progress: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/debug-user-progress/<int:user_id>')
@login_required
def debug_user_progress(lang, user_id):
    """
    Debug endpoint для проверки прогресса пользователя в БД
    """
    try:
        print(f"🔍 DEBUG: Проверяем прогресс пользователя {user_id}")
        
        # Получаем последние 10 записей прогресса
        recent_progress = UserProgress.query.filter_by(user_id=user_id).order_by(UserProgress.id.desc()).limit(10).all()
        
        progress_data = []
        for p in recent_progress:
            progress_data.append({
                'id': p.id,
                'lesson_id': p.lesson_id,
                'completed': p.completed,
                'time_spent': p.time_spent,
                'last_accessed': p.last_accessed.isoformat() if p.last_accessed else None,
                'timestamp': p.timestamp.isoformat() if p.timestamp else None
            })
            print(f"📊 Урок {p.lesson_id}, время: {p.last_accessed}, завершен: {p.completed}")
        
        # Получаем общую статистику
        total_lessons = Lesson.query.count()
        completed_lessons = UserProgress.query.filter_by(user_id=user_id, completed=True).count()
        
        return jsonify({
            'user_id': user_id,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0,
            'recent_progress': progress_data
        })
        
    except Exception as e:
        print(f"❌ ОШИБКА в debug_user_progress: {e}")
        current_app.logger.error(f"❌ ОШИБКА в debug_user_progress: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
    
@api_bp.route('/test-progress-page')
def test_progress_page(lang):
    """Тестовая страница для проверки системы прогресса"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Тест системы прогресса</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
            .success { background-color: #d4edda; border-color: #c3e6cb; }
            .error { background-color: #f8d7da; border-color: #f5c6cb; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            pre { background: #f8f9fa; padding: 10px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🧪 Тест системы прогресса уроков</h1>
        
        <div class="test-section">
            <h3>1️⃣ Тест открытия урока</h3>
            <button onclick="testOpenLesson()">Открыть урок 1</button>
            <div id="openResult"></div>
        </div>
        
        <div class="test-section">
            <h3>2️⃣ Тест завершения урока</h3>
            <button onclick="testCompleteLesson()">Завершить урок 1</button>
            <div id="completeResult"></div>
        </div>
        
        <div class="test-section">
            <h3>3️⃣ Тест получения статистики</h3>
            <button onclick="testGetStats()">Получить статистику</button>
            <div id="statsResult"></div>
        </div>
        
        <div class="test-section">
            <h3>4️⃣ Тест API статистики</h3>
            <button onclick="testApiStats()">API статистика</button>
            <div id="apiStatsResult"></div>
        </div>

        <script>
            const LESSON_ID = 1;
            
            function showResult(elementId, success, message, data = null) {
                const element = document.getElementById(elementId);
                element.className = success ? 'success' : 'error';
                element.innerHTML = `
                    <h4>${success ? '✅ Успех' : '❌ Ошибка'}</h4>
                    <p>${message}</p>
                    ${data ? `<pre>${JSON.stringify(data, null, 2)}</pre>` : ''}
                `;
            }
            
            async function testOpenLesson() {
                try {
                    const response = await fetch(`/en/content/lesson/${LESSON_ID}`);
                    const success = response.ok;
                    const data = success ? await response.text() : await response.text();
                    
                    showResult('openResult', success, 
                        success ? 'Урок открыт успешно' : `Ошибка ${response.status}`,
                        success ? { status: response.status, size: data.length } : data
                    );
                } catch (error) {
                    showResult('openResult', false, `Ошибка сети: ${error.message}`);
                }
            }
            
            async function testCompleteLesson() {
                try {
                    const response = await fetch(`/en/content/api/lesson/${LESSON_ID}/complete`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            completed: true,
                            time_spent: 30.0
                        })
                    });
                    
                    const success = response.ok;
                    const data = success ? await response.json() : await response.text();
                    
                    showResult('completeResult', success,
                        success ? 'Урок завершен успешно' : `Ошибка ${response.status}`,
                        data
                    );
                } catch (error) {
                    showResult('completeResult', false, `Ошибка сети: ${error.message}`);
                }
            }
            
            async function testGetStats() {
                try {
                    const response = await fetch('/en/learning-map');
                    const success = response.ok;
                    const data = await response.text();
                    
                    showResult('statsResult', success,
                        success ? 'Статистика загружена' : `Ошибка ${response.status}`,
                        {
                            status: response.status,
                            size: data.length,
                            hasCompletedLessons: data.includes('completed_lessons'),
                            hasProgress: data.includes('progress')
                        }
                    );
                } catch (error) {
                    showResult('statsResult', false, `Ошибка сети: ${error.message}`);
                }
            }
            
            async function testApiStats() {
                try {
                    const response = await fetch('/en/api/user-stats');
                    const success = response.ok;
                    const data = success ? await response.json() : await response.text();
                    
                    showResult('apiStatsResult', success,
                        success ? 'API статистика получена' : `Ошибка ${response.status}`,
                        data
                    );
                } catch (error) {
                    showResult('apiStatsResult', false, `Ошибка сети: ${error.message}`);
                }
            }
        </script>
    </body>
    </html>
    '''

@api_bp.route('/user-stats')
@login_required
def get_user_stats(lang):
    """Получает унифицированную статистику пользователя"""
    try:
        # Получаем унифицированную статистику
        stats = get_unified_user_stats(current_user.id)
        
        return jsonify({
            'status': 'success',
            'stats': stats
        })
    except Exception as e:
        current_app.logger.error(f"Error getting user stats: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    