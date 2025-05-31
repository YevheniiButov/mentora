# Мобильные роуты для Dental Academy
# Вставьте сюда код мобильных роутов

from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import (
    db, Subject, Module, UserProgress, Lesson, ContentCategory,
    ContentSubcategory, ContentTopic, LearningPath,
    VirtualPatientScenario, VirtualPatientAttempt
)
from utils.mobile_detection import get_mobile_detector
from translations import get_translation as t

mobile_bp = Blueprint('mobile', __name__, url_prefix='/<lang>/mobile', template_folder='../templates/mobile')

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
DEFAULT_LANGUAGE = 'en'

@mobile_bp.before_request
def before_request_mobile():
    """Обработка языка и проверка мобильности для мобильных роутов."""
    try:
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            g.lang = session.get('lang') or DEFAULT_LANGUAGE
        
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
    except Exception as e:
        current_app.logger.error(f"Error in before_request_mobile: {e}", exc_info=True)
        g.lang = DEFAULT_LANGUAGE

@mobile_bp.context_processor
def inject_mobile_context():
    """Добавляет мобильный контекст в шаблоны."""
    detector = get_mobile_detector()
    return dict(
        lang=getattr(g, 'lang', DEFAULT_LANGUAGE),
        is_mobile=detector.is_mobile_device,
        device_type=detector.device_type,
        supported_languages=SUPPORTED_LANGUAGES
    )

# Welcome страница
@mobile_bp.route('/')
@mobile_bp.route('/welcome')
def welcome(lang):
    """Мобильная welcome страница."""
    detector = get_mobile_detector()
    
    # Если не мобильное устройство, перенаправляем на desktop версию
    if not detector.is_mobile_device:
        return redirect(url_for('main_bp.index', lang=lang))
    
    return render_template(
        'mobile/learning/welcome_mobile.html',
        title=t('welcome_to_dental_academy', lang=lang),
        current_language=lang,
        user=current_user if current_user.is_authenticated else None
    )

# Авторизация
@mobile_bp.route('/auth/login')
def login(lang):
    """Мобильная страница входа."""
    return render_template(
        'mobile/auth/login_mobile.html',
        title='Login',
        current_language=lang
    )

@mobile_bp.route('/auth/register')
def register(lang):
    """Мобильная страница регистрации."""
    return render_template(
        'mobile/auth/register_mobile.html',
        title='Register',
        current_language=lang
    )

# Обучение
@mobile_bp.route('/subjects')
def subjects_view(lang):
    """Публичная мобильная страница просмотра предметов."""
    try:
        # Получаем пути обучения
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        
        # Получаем все предметы без прогресса (публичный доступ)
        subjects = Subject.query.all()
        for subject in subjects:
            try:
                subject_modules = Module.query.filter_by(subject_id=subject.id).all()
                total_lessons = sum(len(getattr(module, 'lessons', [])) for module in subject_modules)
                
                # Для неавторизованных пользователей прогресс всегда 0
                subject.progress_percentage = 0
                subject.total_lessons = total_lessons
                subject.completed_lessons = 0
                subject.is_completed = False
                subject.estimated_time = f"{max(1, total_lessons // 10)}h"
                
                if not hasattr(subject, 'category') or not subject.category:
                    subject.category = 'general'
                    
            except Exception as e:
                current_app.logger.error(f"Error calculating info for subject {subject.id}: {e}")
                subject.progress_percentage = 0
                subject.total_lessons = 0
                subject.completed_lessons = 0
                subject.is_completed = False
                subject.estimated_time = "2h"
                subject.category = 'general'
        
        # Статистика для неавторизованных пользователей
        user_stats = {
            'total_progress': 0,
            'completed_subjects': 0,
            'total_subjects': len(subjects),
            'current_streak': 0
        }
        
        return render_template(
            'mobile/learning/learning_map_mobile.html',
            title='Explore Subjects',
            learning_paths=learning_paths,
            subjects=subjects,
            user_stats=user_stats,
            current_language=lang,
            show_auth_prompt=True  # Показывать призыв к регистрации
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in mobile subjects_view: {e}", exc_info=True)
        flash("Error loading subjects", "danger")
        return redirect(url_for('mobile.welcome', lang=lang))

@mobile_bp.route('/learning')
@login_required
def learning_map(lang):
    """Мобильная карта обучения."""
    try:
        # Получаем пути обучения
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        
        # Получаем все предметы с прогрессом
        subjects = Subject.query.all()
        for subject in subjects:
            try:
                subject_modules = Module.query.filter_by(subject_id=subject.id).all()
                total_lessons = 0
                completed_lessons = 0
                
                for module in subject_modules:
                    # Получаем статистику модуля (функция должна быть импортирована)
                    from routes.learning_map_routes import get_module_stats
                    module_stats = get_module_stats(module.id, current_user.id)
                    total_lessons += module_stats.get("total_lessons", 0)
                    completed_lessons += module_stats.get("completed_lessons", 0)
                
                # Вычисляем прогресс предмета
                if total_lessons > 0:
                    progress_percentage = int((completed_lessons / total_lessons) * 100)
                else:
                    progress_percentage = 0
                
                subject.progress_percentage = progress_percentage
                subject.total_lessons = total_lessons
                subject.completed_lessons = completed_lessons
                subject.is_completed = progress_percentage == 100
                subject.estimated_time = f"{max(1, total_lessons // 10)}h"
                
                if not hasattr(subject, 'category') or not subject.category:
                    subject.category = 'general'
                    
            except Exception as e:
                current_app.logger.error(f"Error calculating progress for subject {subject.id}: {e}")
                subject.progress_percentage = 0
                subject.total_lessons = 0
                subject.completed_lessons = 0
                subject.is_completed = False
                subject.estimated_time = "2h"
                subject.category = 'general'
        
        # Получаем статистику пользователя
        from routes.learning_map_routes import get_user_stats
        user_stats = get_user_stats(current_user.id)
        
        return render_template(
            'learning/learning_map_mobile.html',
            title=t('learning_map', lang=lang),
            learning_paths=learning_paths,
            subjects=subjects,
            user_stats=user_stats,
            current_language=lang
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in mobile learning_map: {e}", exc_info=True)
        flash(t("error_loading_data", lang=lang), "danger")
        return redirect(url_for('mobile.welcome', lang=lang))

@mobile_bp.route('/subject/<int:subject_id>')
@login_required
def subject_view(lang, subject_id):
    """Мобильная страница просмотра предмета."""
    try:
        from routes.learning_map_routes import get_module_stats, get_user_stats
        from routes.subject_view_routes import get_virtual_patients_for_subject, get_user_recommendations
        
        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()

        # Обрабатываем модули
        for module in subject_modules:
            module_stats = get_module_stats(module.id, current_user.id)
            module.progress = module_stats.get("progress", 0)
            module.completed_lessons = module_stats.get("completed_lessons", 0)
            module.total_lessons = module_stats.get("total_lessons", 0)

        # Получаем данные
        virtual_patients = get_virtual_patients_for_subject(selected_subject, current_user.id)
        stats = get_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id)
        
        # Вычисляем прогресс предмета
        total_lessons = sum(module.total_lessons for module in subject_modules)
        completed_lessons = sum(module.completed_lessons for module in subject_modules)
        
        if total_lessons > 0:
            selected_subject.progress_percentage = int((completed_lessons / total_lessons) * 100)
        else:
            selected_subject.progress_percentage = 0
            
        selected_subject.total_lessons = total_lessons
        selected_subject.completed_lessons = completed_lessons
        selected_subject.estimated_time = f"{max(1, total_lessons // 10)}h"

        return render_template(
            'learning/subject_view_mobile.html',
            title=selected_subject.name,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            virtual_patients=virtual_patients,
            stats=stats,
            recommendations=recommendations,
            current_language=lang
        )

    except Exception as e:
        current_app.logger.error(f"Error in mobile subject_view: {e}", exc_info=True)
        flash(t("error_occurred_loading_data", lang=lang), "danger")
        return redirect(url_for('mobile.learning_map', lang=lang))

@mobile_bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson_view(lang, lesson_id):
    """Мобильная страница просмотра урока."""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        module = lesson.module
        
        # Получаем прогресс урока
        user_progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        return render_template(
            'learning/lesson_view_mobile.html',
            title=lesson.title,
            lesson=lesson,
            module=module,
            user_progress=user_progress,
            current_language=lang
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in mobile lesson_view: {e}", exc_info=True)
        flash(t("error_loading_lesson", lang=lang), "danger")
        return redirect(url_for('mobile.learning_map', lang=lang))

# Тестирование
@mobile_bp.route('/test/<int:test_id>')
@login_required
def test_view(lang, test_id):
    """Мобильная страница тестирования."""
    return render_template(
        'testing/test_mobile_system.html',
        title=t('test_system', lang=lang),
        current_language=lang
    )

# Профиль
@mobile_bp.route('/profile')
@login_required
def profile(lang):
    """Мобильная страница профиля."""
    return render_template(
        'profile/profile_mobile.html',
        title=t('profile', lang=lang),
        user=current_user,
        current_language=lang
    )

# API для мобильных приложений
@mobile_bp.route('/api/subjects')
@login_required
def api_subjects(lang):
    """API для получения предметов."""
    try:
        subjects = Subject.query.all()
        subjects_data = []
        
        for subject in subjects:
            # Вычисляем прогресс
            subject_modules = Module.query.filter_by(subject_id=subject.id).all()
            total_lessons = 0
            completed_lessons = 0
            
            for module in subject_modules:
                from routes.learning_map_routes import get_module_stats
                module_stats = get_module_stats(module.id, current_user.id)
                total_lessons += module_stats.get("total_lessons", 0)
                completed_lessons += module_stats.get("completed_lessons", 0)
            
            progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            
            subjects_data.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description or '',
                'category': getattr(subject, 'category', 'general'),
                'icon': getattr(subject, 'icon', 'book'),
                'progress_percentage': progress_percentage,
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'estimated_time': f"{max(1, total_lessons // 10)}h",
                'is_completed': progress_percentage == 100
            })
        
        return jsonify(subjects_data)
        
    except Exception as e:
        current_app.logger.error(f"Error in mobile api_subjects: {e}", exc_info=True)
        return jsonify([]), 500

@mobile_bp.route('/api/lesson/<int:lesson_id>/progress', methods=['POST'])
@login_required
def api_save_lesson_progress(lang, lesson_id):
    """API для сохранения прогресса урока."""
    try:
        data = request.get_json()
        
        progress = UserProgress.query.filter_by(
            user_id=current_user.id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                lesson_id=lesson_id
            )
        
        # Обновляем прогресс
        if 'completed' in data:
            progress.completed = data['completed']
        if 'progress_percentage' in data:
            progress.progress_percentage = data['progress_percentage']
        if 'time_spent' in data:
            progress.time_spent = data.get('time_spent', 0)
        
        progress.updated_at = db.func.now()
        
        db.session.add(progress)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error saving lesson progress: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Редирект для совместимости
@mobile_bp.route('/dashboard')
@login_required
def dashboard_redirect(lang):
    """Перенаправление на карту обучения."""
    return redirect(url_for('mobile.learning_map', lang=lang))

# Тестовые роуты для отладки
@mobile_bp.route('/test')
def mobile_test(lang):
    """Тестовый роут для проверки мобильной системы."""
    detector = get_mobile_detector()
    device_info = detector.get_device_info()
    
    return jsonify({
        'mobile_routes_working': True,
        'language': lang,
        'device_info': device_info,
        'is_mobile': detector.is_mobile_device,
        'current_user': current_user.username if current_user.is_authenticated else None,
        'supported_languages': SUPPORTED_LANGUAGES
    })

@mobile_bp.route('/device-info')
def device_info(lang):
    """Информация об устройстве для отладки."""
    detector = get_mobile_detector()
    user_agent = request.headers.get('User-Agent', 'No User-Agent')
    
    return jsonify({
        'user_agent': user_agent,
        'device_info': detector.get_device_info(),
        'is_mobile': detector.is_mobile_device,
        'device_type': detector.device_type,
        'should_use_mobile_template': detector.should_use_mobile_template(),
        'current_language': lang,
        'request_headers': dict(request.headers)
    })

# Вставьте сюда роуты 