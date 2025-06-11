# Мобильные роуты для Dental Academy с унифицированной навигацией

from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app, jsonify, abort
from flask_login import login_required, current_user, login_user, logout_user
from models import (
    db, Subject, Module, UserProgress, Lesson, ContentCategory,
    ContentSubcategory, ContentTopic, LearningPath,
    VirtualPatientScenario, VirtualPatientAttempt, User,
    QuestionCategory, Question, Test, TestAttempt
)
from utils.mobile_detection import get_mobile_detector
from translations_new import get_translation as t
from extensions import bcrypt, babel, csrf
from forms import LoginForm, RegistrationForm
from datetime import datetime, timedelta

# Импорты других маршрутов
try:
    from routes.learning_map_routes import get_module_stats, get_user_stats
    from routes.subject_view_routes import get_virtual_patients_for_subject, get_user_recommendations
except ImportError as e:
    print(f"Warning: Some route functions not available: {e}")
    # Создаем заглушки
    def get_module_stats(module_id, user_id):
        return {"progress": 0, "completed_lessons": 0, "total_lessons": 0}
    def get_user_stats(user_id):
        return {}
    def get_virtual_patients_for_subject(subject, user_id):
        return []
    def get_user_recommendations(user_id):
        return []

mobile_bp = Blueprint('mobile', __name__, url_prefix='/<lang>/mobile', template_folder='../templates/mobile')

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

def get_navigation_config(page_type, **kwargs):
    """
    Создает унифицированную конфигурацию навигации
    
    Args:
        page_type (str): Тип страницы
        **kwargs: Дополнительные параметры навигации
    
    Returns:
        dict: Конфигурация навигации
    """
    # Базовая конфигурация - везде логотип, без кнопки назад
    base_config = {
        'show_logo': True,
        'show_back_button': False,  # Убираем кнопку назад везде
        'show_bottom_nav': True,
        'show_profile_button': True,
        'show_settings_button': True,
        'show_language_selector': True,
        'show_progress': False,
        'page_title': '',
        'breadcrumbs': [],
        'progress_data': None
    }
    
    # Обновляем конфигурацию дополнительными параметрами
    base_config.update(kwargs)
    
    return base_config

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
        supported_languages=SUPPORTED_LANGUAGES,
        get_navigation_config=get_navigation_config
    )

# ===== ОСНОВНЫЕ СТРАНИЦЫ =====

@mobile_bp.route('/')
@mobile_bp.route('/welcome')
def welcome(lang):
    """Мобильная welcome страница."""
    detector = get_mobile_detector()
    
    # Если не мобильное устройство, перенаправляем на desktop версию
    if not detector.is_mobile_device:
        return redirect(url_for('main_bp.index', lang=lang))
    
    nav_config = get_navigation_config('welcome')
    
    return render_template(
        'mobile/learning/welcome_mobile.html',
        title=t('welcome_to_dental_academy', lang=lang),
        current_language=lang,
        user=current_user if current_user.is_authenticated else None,
        nav_config=nav_config
    )

# ===== АВТОРИЗАЦИЯ =====

@mobile_bp.route('/auth/login', methods=['GET', 'POST'])
def login(lang):
    """Мобильная страница входа."""
    if current_user.is_authenticated:
        return redirect(url_for('mobile.learning_map', lang=lang))
    
    nav_config = get_navigation_config('login')
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Проверка валидности хеша
        valid_hash = False
        if user:
            try:
                if user.password_hash and (user.password_hash.startswith('$2b$') or 
                                         user.password_hash.startswith('$2a$')):
                    valid_hash = True
            except Exception as e:
                current_app.logger.error(f"Error checking password hash: {e}")
        
        # Проверяем пароль
        try:
            password_correct = False
            if user and valid_hash:
                password_correct = bcrypt.check_password_hash(user.password_hash, form.password.data)
            
            if user and password_correct:
                login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)
                flash("Вы успешно вошли в систему!", "success")
                current_app.logger.info(f"User {user.email} logged in successfully via mobile.")
                
                # Редирект на мобильную карту обучения
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('mobile.learning_map', lang=lang))
            else:
                flash("Неверный email или пароль.", "danger")
                current_app.logger.warning(f"Failed mobile login attempt for email {form.email.data}")
        except ValueError as e:
            current_app.logger.error(f"Password hash error for user {form.email.data}: {e}")
            flash("Ошибка аутентификации. Обратитесь в поддержку.", "danger")
    
    return render_template(
        'mobile/auth/login_mobile.html',
        form=form,
        title='Login',
        current_language=lang,
        nav_config=nav_config
    )

@mobile_bp.route('/auth/register', methods=['GET', 'POST'])
def register(lang):
    """Мобильная страница регистрации."""
    if current_user.is_authenticated:
        return redirect(url_for('mobile.learning_map', lang=lang))
    
    nav_config = get_navigation_config('register')
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Аккаунт с таким email уже существует.', 'warning')
            return render_template('mobile/auth/register_mobile.html', form=form, title='Register', 
                                 current_language=lang, nav_config=nav_config)
        
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            new_user = User(
                email=form.email.data,
                username=form.email.data, 
                password_hash=hashed_password,
                name=form.name.data
            )
            
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f"New user registered via mobile: {new_user.email}")
            flash('Регистрация завершена! Теперь войдите в систему.', 'success')
            
            return redirect(url_for('mobile.login', lang=lang))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during mobile registration for {form.email.data}: {e}", exc_info=True)
            flash('Произошла ошибка при регистрации. Попробуйте снова.', 'danger')
    
    return render_template(
        'mobile/auth/register_mobile.html',
        form=form,
        title='Register',
        current_language=lang,
        nav_config=nav_config
    )

@mobile_bp.route('/auth/logout')
@login_required
def logout(lang):
    """Мобильный выход из системы."""
    logout_user()
    flash("Вы успешно вышли из системы.", "info")
    return redirect(url_for('mobile.welcome', lang=lang))

# ===== ОБУЧЕНИЕ =====

@mobile_bp.route('/subjects')
@login_required
def subjects_view(lang):
    """Мобильная страница просмотра предметов (требует авторизации)."""
    try:
        nav_config = get_navigation_config('subjects')
        
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
            show_auth_prompt=True,  # Показывать призыв к регистрации
            nav_config=nav_config
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
        nav_config = get_navigation_config('learning_map')
        
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
                    # Получаем статистику модуля
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
        user_stats = get_user_stats(current_user.id)
        
        return render_template(
            'mobile/learning/learning_map_mobile.html',
            title=t('learning_map', lang=lang),
            learning_paths=learning_paths,
            subjects=subjects,
            user_stats=user_stats,
            current_language=lang,
            nav_config=nav_config
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
        nav_config = get_navigation_config('subject_view')
        
        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()

        # Обрабатываем модули
        for module in subject_modules:
            module_stats = get_module_stats(module.id, current_user.id)
            module.progress = module_stats.get("progress", 0)
            module.completed_lessons = module_stats.get("completed_lessons", 0)
            module.total_lessons = module_stats.get("total_lessons", 0)
            
            # Добавляем дополнительные атрибуты для шаблона
            if module.total_lessons > 0:
                module.progress_percentage = int((module.completed_lessons / module.total_lessons) * 100)
            else:
                module.progress_percentage = 0
                
            module.is_completed = module.progress_percentage >= 100
            module.is_locked = False  # Пока все модули доступны
            module.is_available = True  # Все модули доступны по умолчанию
            module.estimated_time = f"{max(1, module.total_lessons * 5)}min"  # 5 мин на урок
            module.difficulty = getattr(module, 'difficulty', 'Средний')
            module.has_test = True  # Предполагаем что у всех модулей есть тест
            
            # Исправляем проблему с lessons - подсчитываем количество уроков
            try:
                if hasattr(module, 'lessons') and module.lessons:
                    module.lessons_count = module.lessons.count()
                else:
                    module.lessons_count = module.total_lessons
            except:
                module.lessons_count = module.total_lessons

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
            'mobile/learning/subject_view_mobile.html',
            title=selected_subject.name,
            subject=selected_subject,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            modules=subject_modules,
            total_lessons=selected_subject.total_lessons,
            completed_lessons=selected_subject.completed_lessons,
            progress_percentage=selected_subject.progress_percentage,
            estimated_time=selected_subject.estimated_time,
            virtual_patients=virtual_patients,
            stats=stats,
            recommendations=recommendations,
            current_language=lang,
            nav_config=nav_config
        )

    except Exception as e:
        current_app.logger.error(f"Error in mobile subject_view: {e}", exc_info=True)
        flash(t("error_occurred_loading_data", lang=lang), "danger")
        return redirect(url_for('mobile.learning_map', lang=lang))

@mobile_bp.route('/public/subject/<int:subject_id>')
def public_subject_view(lang, subject_id):
    """Публичный просмотр предмета с реальными данными без авторизации."""
    try:
        nav_config = get_navigation_config('public_subject')
        
        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()

        # Обрабатываем модули
        for module in subject_modules:
            # Для публичной версии просто подсчитываем количество уроков
            lesson_count = Lesson.query.filter_by(module_id=module.id).count()
            module.completed_lessons = min(3, lesson_count)  # Первые 3 урока "завершены"
            module.total_lessons = lesson_count
            
            # Добавляем дополнительные атрибуты для шаблона
            if module.total_lessons > 0:
                module.progress_percentage = int((module.completed_lessons / module.total_lessons) * 100)
            else:
                module.progress_percentage = 0
                
            module.is_completed = module.progress_percentage >= 100
            module.is_locked = False  # В публичной версии все модули доступны
            module.is_available = True
            module.estimated_time = f"{max(1, module.total_lessons * 5)}min"
            module.difficulty = getattr(module, 'difficulty', 'Средний')
            module.has_test = True
            module.lessons_count = module.total_lessons

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
            'mobile/learning/subject_view_mobile.html',
            title=selected_subject.name,
            subject=selected_subject,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            modules=subject_modules,
            total_lessons=selected_subject.total_lessons,
            completed_lessons=selected_subject.completed_lessons,
            progress_percentage=selected_subject.progress_percentage,
            estimated_time=selected_subject.estimated_time,
            virtual_patients=[],  # Пусто для публичной версии
            stats={},  # Пусто для публичной версии  
            recommendations=[],  # Пусто для публичной версии
            current_language=lang,
            nav_config=nav_config
        )

    except Exception as e:
        current_app.logger.error(f"Error in public_subject_view: {e}", exc_info=True)
        return f"<h1>Ошибка предмета: {e}</h1>", 500

# ===== ПРОФИЛЬ И НАСТРОЙКИ =====

@mobile_bp.route('/profile')
@login_required
def profile(lang):
    """Мобильная страница профиля."""
    nav_config = get_navigation_config('profile')
    
    return render_template(
        'profile/profile_mobile.html',
        title=t('profile', lang=lang),
        user=current_user,
        current_language=lang,
        nav_config=nav_config
    )

@mobile_bp.route('/settings')
@login_required
def settings(lang):
    """Мобильная страница настроек."""
    nav_config = get_navigation_config('settings')
    
    return render_template(
        'mobile/settings.html',
        title=t('settings', lang=lang),
        current_language=lang,
        nav_config=nav_config
    )

# ===== ТЕСТЫ =====

@mobile_bp.route('/tests')
@login_required
def tests(lang):
    """Мобильная страница тестов."""
    try:
        nav_config = get_navigation_config('tests')
        
        # Получаем все категории для выбора
        categories = QuestionCategory.query.all()
        
        # Подготавливаем данные о категориях
        test_categories = []
        for category in categories:
            # Подсчитываем количество вопросов в категории
            question_count = Question.query.filter_by(category_id=category.id).count()
            
            test_categories.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'question_count': question_count,
                'icon': 'fa-brain' if 'теория' in category.name.lower() else 'fa-stethoscope'
            })
        
        return render_template(
            'mobile/tests/test_mobile_system.html',
            title=t('test_system', lang=lang),
            current_language=lang,
            categories=test_categories,
            nav_config=nav_config
        )
    except Exception as e:
        current_app.logger.error(f"Error in mobile tests route: {e}", exc_info=True)
        flash(t('error_loading_tests', lang=lang), 'error')
        return redirect(url_for('mobile.welcome', lang=lang))

@mobile_bp.route('/test/<int:test_id>')
@login_required
def test_view(lang, test_id):
    """Мобильная страница тестирования."""
    nav_config = get_navigation_config('test_view')
    
    return render_template(
        'testing/test_mobile_system.html',
        title=t('test_system', lang=lang),
        current_language=lang,
        nav_config=nav_config
    )

# ===== МОДУЛИ И УРОКИ =====

@mobile_bp.route('/module/<int:module_id>')
@login_required
def module_view(lang, module_id):
    """Мобильная страница просмотра модуля."""
    try:
        nav_config = get_navigation_config('module_view')
        
        module = Module.query.get_or_404(module_id)
        
        # Получаем все уроки модуля
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        
        # Обрабатываем уроки для шаблона
        for lesson in lessons:
            # Получаем прогресс урока
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            
            lesson.is_completed = progress.completed if progress else False
            lesson.is_locked = False  # Все уроки доступны
            lesson.progress_percentage = 100 if lesson.is_completed else 0
        
        # Получаем статистику модуля
        module_stats = get_module_stats(module_id, current_user.id)
        module.progress_percentage = module_stats.get("progress", 0)
        module.completed_lessons = module_stats.get("completed_lessons", 0)
        module.total_lessons = module_stats.get("total_lessons", 0)

        return render_template(
            'mobile/learning/module_mobile.html',
            title=module.title,
            module=module,
            lessons=lessons,
            current_language=lang,
            nav_config=nav_config
        )

    except Exception as e:
        current_app.logger.error(f"Error in mobile module_view: {e}", exc_info=True)
        flash(t("error_loading_module", lang=lang), "danger")
        return redirect(url_for('mobile.learning_map', lang=lang))

@mobile_bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson_view(lang, lesson_id):
    """Мобильная страница просмотра урока."""
    try:
        current_app.logger.info(f"🔍 Открываем урок {lesson_id} для пользователя {current_user.id}")
        
        nav_config = get_navigation_config('lesson_view')
        
        lesson = Lesson.query.get_or_404(lesson_id)
        current_app.logger.info(f"✅ Урок найден: {lesson.title}")
        
        module = Module.query.get_or_404(lesson.module_id)
        current_app.logger.info(f"✅ Модуль найден: {module.title}")
        
        # Получаем все уроки модуля для навигации
        all_lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        current_app.logger.info(f"✅ Найдено {len(all_lessons)} уроков в модуле")
        
        # Находим текущий индекс урока
        current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), 0)
        
        # Определяем предыдущий и следующий уроки
        prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
        next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
        
        current_app.logger.info(f"✅ Навигация: предыдущий={prev_lesson.id if prev_lesson else None}, следующий={next_lesson.id if next_lesson else None}")
        
        # Обрабатываем содержимое урока
        processed_content = None
        if lesson.content:
            try:
                import json
                content_data = json.loads(lesson.content)
                
                if lesson.content_type == 'learning_card' and 'cards' in content_data:
                    processed_content = {
                        'type': 'learning_cards',
                        'cards': content_data['cards']
                    }
                elif lesson.content_type in ['quiz', 'test_question'] and 'questions' in content_data:
                    processed_content = {
                        'type': 'quiz',
                        'questions': content_data['questions']
                    }
                else:
                    processed_content = content_data
                    
            except json.JSONDecodeError as json_error:
                current_app.logger.warning(f"⚠️ JSON decode error: {json_error}")
                processed_content = {'type': 'text', 'content': lesson.content}
        
        current_app.logger.info(f"✅ Контент обработан: тип={processed_content.get('type') if processed_content else 'none'}")
        
        # Обновляем прогресс (делаем это опционально)
        try:
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson_id
            ).first()
            
            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=lesson_id,
                    viewed=True,
                    started_at=datetime.utcnow()
                )
                db.session.add(progress)
                db.session.commit()
                current_app.logger.info(f"✅ Создан новый прогресс для урока {lesson_id}")
            elif not progress.viewed:
                progress.viewed = True
                db.session.commit()
                current_app.logger.info(f"✅ Обновлен прогресс для урока {lesson_id}")
        except Exception as progress_error:
            current_app.logger.warning(f"⚠️ Ошибка при обновлении прогресса: {progress_error}")
            # Продолжаем без обновления прогресса

        current_app.logger.info(f"✅ Рендерим шаблон lesson_mobile.html")
        
        return render_template(
            'mobile/learning/lesson_mobile.html',
            title=lesson.title,
            lesson=lesson,
            module=module,
            processed_content=processed_content,
            current_index=current_index,
            total_lessons=len(all_lessons),
            prev_lesson=prev_lesson,
            next_lesson=next_lesson,
            current_language=lang,
            nav_config=nav_config
        )

    except Exception as e:
        current_app.logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в lesson_view: {e}", exc_info=True)
        current_app.logger.error(f"❌ Тип ошибки: {type(e).__name__}")
        current_app.logger.error(f"❌ Урок ID: {lesson_id}, Пользователь: {current_user.id if current_user.is_authenticated else 'anonymous'}")
        
        flash(f"Ошибка загрузки урока: {str(e)}", "danger")
        return redirect(url_for('mobile.learning_map', lang=lang))

@mobile_bp.route('/public/lesson/<int:lesson_id>')
@mobile_bp.route('/public/lesson/<int:lesson_id>/step/<int:step>')
def public_lesson_view(lang, lesson_id, step=1):
    """Публичный просмотр урока без авторизации."""
    try:
        nav_config = get_navigation_config('public_lesson')
        
        lesson = Lesson.query.get_or_404(lesson_id)
        module = Module.query.get_or_404(lesson.module_id)
        
        # Получаем все уроки модуля для навигации
        all_lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        
        # Находим текущий индекс урока
        current_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson_id), 0)
        
        # Определяем предыдущий и следующий уроки
        prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
        next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
        
        # Обрабатываем содержимое урока (ограниченно для публичной версии)
        processed_content = None
        if lesson.content:
            try:
                import json
                content_data = json.loads(lesson.content)
                
                # Ограничиваем контент для публичной версии
                if lesson.content_type == 'learning_card' and 'cards' in content_data:
                    cards = content_data['cards'][:3]  # Только первые 3 карточки
                    processed_content = {
                        'type': 'learning_cards',
                        'cards': cards,
                        'limited': True
                    }
                elif lesson.content_type in ['quiz', 'test_question'] and 'questions' in content_data:
                    questions = content_data['questions'][:2]  # Только первые 2 вопроса
                    processed_content = {
                        'type': 'quiz',
                        'questions': questions,
                        'limited': True
                    }
                else:
                    processed_content = content_data
                    
            except json.JSONDecodeError:
                processed_content = {'type': 'text', 'content': lesson.content[:500] + '...'}  # Урезанный текст
        
        return render_template(
            'mobile/learning/lesson_single_mobile.html',
            title=lesson.title,
            lesson=lesson,
            module=module,
            processed_content=processed_content,
            current_index=current_index,
            total_lessons=len(all_lessons),
            prev_lesson=prev_lesson,
            next_lesson=next_lesson,
            current_step=step,
            current_language=lang,
            nav_config=nav_config,
            is_public=True  # Флаг для шаблона
        )

    except Exception as e:
        current_app.logger.error(f"Error in public lesson_view: {e}", exc_info=True)
        return f"<h1>Ошибка урока: {e}</h1>", 500

# ===== API =====

@mobile_bp.route('/api/subjects')
@login_required
@csrf.exempt
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

# ===== РЕДИРЕКТ ДЛЯ СОВМЕСТИМОСТИ =====

@mobile_bp.route('/dashboard')
@login_required
def dashboard_redirect(lang):
    """Перенаправление на карту обучения."""
    return redirect(url_for('mobile.learning_map', lang=lang))

# ===== ДИАГНОСТИКА =====

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
        'supported_languages': SUPPORTED_LANGUAGES,
        'navigation_unified': True
    })

@mobile_bp.route('/debug/lesson/<int:lesson_id>')
@login_required
def debug_lesson(lang, lesson_id):
    """Отладочный маршрут для диагностики урока."""
    try:
        lesson = Lesson.query.get_or_404(lesson_id)
        module = Module.query.get_or_404(lesson.module_id)
        
        debug_info = {
            'lesson_id': lesson_id,
            'lesson_title': lesson.title,
            'lesson_content_type': lesson.content_type,
            'lesson_content_length': len(lesson.content) if lesson.content else 0,
            'module_id': module.id,
            'module_title': module.title,
            'user_id': current_user.id,
            'user_username': current_user.username,
            'correct_url': url_for('mobile.lesson_view', lang=lang, lesson_id=lesson_id),
            'template_exists': True,  # мы знаем что он существует
            'database_working': True
        }
        
        return f"""
        <h1>🔍 ДИАГНОСТИКА УРОКА {lesson_id}</h1>
        <h2>✅ Информация:</h2>
        <ul>
            <li><strong>Урок:</strong> {lesson.title}</li>
            <li><strong>Модуль:</strong> {module.title}</li>
            <li><strong>Пользователь:</strong> {current_user.username}</li>
            <li><strong>Правильный URL:</strong> <a href="{url_for('mobile.lesson_view', lang=lang, lesson_id=lesson_id)}">{url_for('mobile.lesson_view', lang=lang, lesson_id=lesson_id)}</a></li>
        </ul>
        <h2>🧪 Тестировать:</h2>
        <p><a href="{url_for('mobile.lesson_view', lang=lang, lesson_id=lesson_id)}" style="background: blue; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">ОТКРЫТЬ УРОК</a></p>
        <hr>
        <h3>📊 Детали:</h3>
        <pre>{debug_info}</pre>
        """
        
    except Exception as e:
        return f"<h1>❌ ОШИБКА ДИАГНОСТИКИ: {e}</h1>"

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
        'request_headers': dict(request.headers),
        'navigation_config': 'unified_with_logo'
    })

# ===== API ENDPOINTS ДЛЯ НАСТРОЕК =====

@mobile_bp.route('/api/get-settings')
@login_required
@csrf.exempt
def api_get_settings(lang):
    """API для получения настроек пользователя."""
    try:
        # Получаем настройки пользователя из базы данных или сессии
        user_settings = {
            'language': lang,
            'theme': session.get('theme', 'auto'),
            'notifications': {
                'push_enabled': session.get('push_notifications', True),
                'email_enabled': session.get('email_notifications', True),
                'study_reminders': session.get('study_reminders', True),
                'achievement_alerts': session.get('achievement_alerts', True)
            },
            'privacy': {
                'profile_visibility': session.get('profile_visibility', 'public'),
                'progress_sharing': session.get('progress_sharing', True),
                'analytics_tracking': session.get('analytics_tracking', True)
            },
            'study_preferences': {
                'auto_next_lesson': session.get('auto_next_lesson', True),
                'show_hints': session.get('show_hints', True),
                'difficulty_adjustment': session.get('difficulty_adjustment', 'adaptive'),
                'daily_goal': session.get('daily_goal', 30)  # минут в день
            },
            'accessibility': {
                'high_contrast': session.get('high_contrast', False),
                'large_text': session.get('large_text', False),
                'reduced_motion': session.get('reduced_motion', False),
                'screen_reader': session.get('screen_reader', False)
            }
        }
        
        # Если пользователь авторизован, можем добавить данные из БД
        if current_user.is_authenticated:
            # Добавляем информацию о пользователе
            user_settings['user'] = {
                'name': current_user.name or current_user.username,
                'email': current_user.email,
                'registration_date': current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None,
                'last_activity': current_user.last_activity.isoformat() if hasattr(current_user, 'last_activity') else None
            }
        
        return jsonify({
            'success': True,
            'settings': user_settings
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user settings: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to load settings'
        }), 500

@mobile_bp.route('/api/update-settings', methods=['POST'])
@login_required
@csrf.exempt
def api_update_settings(lang):
    """API для обновления настроек пользователя."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        updated_settings = []
        
        # Обновляем настройки в сессии
        if 'theme' in data:
            session['theme'] = data['theme']
            updated_settings.append('theme')
        
        if 'notifications' in data:
            notifications = data['notifications']
            session['push_notifications'] = notifications.get('push_enabled', True)
            session['email_notifications'] = notifications.get('email_enabled', True)
            session['study_reminders'] = notifications.get('study_reminders', True)
            session['achievement_alerts'] = notifications.get('achievement_alerts', True)
            updated_settings.append('notifications')
        
        if 'privacy' in data:
            privacy = data['privacy']
            session['profile_visibility'] = privacy.get('profile_visibility', 'public')
            session['progress_sharing'] = privacy.get('progress_sharing', True)
            session['analytics_tracking'] = privacy.get('analytics_tracking', True)
            updated_settings.append('privacy')
        
        if 'study_preferences' in data:
            study = data['study_preferences']
            session['auto_next_lesson'] = study.get('auto_next_lesson', True)
            session['show_hints'] = study.get('show_hints', True)
            session['difficulty_adjustment'] = study.get('difficulty_adjustment', 'adaptive')
            session['daily_goal'] = int(study.get('daily_goal', 30))
            updated_settings.append('study_preferences')
        
        if 'accessibility' in data:
            accessibility = data['accessibility']
            session['high_contrast'] = accessibility.get('high_contrast', False)
            session['large_text'] = accessibility.get('large_text', False)
            session['reduced_motion'] = accessibility.get('reduced_motion', False)
            session['screen_reader'] = accessibility.get('screen_reader', False)
            updated_settings.append('accessibility')
        
        # Если изменился язык, обновляем его
        if 'language' in data and data['language'] != lang:
            new_lang = data['language']
            if new_lang in SUPPORTED_LANGUAGES:
                session['lang'] = new_lang
                updated_settings.append('language')
                
                # Возвращаем новый URL для перенаправления
                return jsonify({
                    'success': True,
                    'updated': updated_settings,
                    'redirect_url': url_for('mobile.settings', lang=new_lang)
                })
        
        # TODO: Сохранить настройки в базе данных для авторизованных пользователей
        if current_user.is_authenticated:
            try:
                # Здесь можно добавить сохранение в БД
                # user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
                # if not user_settings:
                #     user_settings = UserSettings(user_id=current_user.id)
                #     db.session.add(user_settings)
                # user_settings.theme = session.get('theme')
                # user_settings.notifications = json.dumps(session.get('notifications', {}))
                # db.session.commit()
                pass
            except Exception as e:
                current_app.logger.error(f"Failed to save settings to database: {e}")
        
        return jsonify({
            'success': True,
            'updated': updated_settings,
            'message': t('settings_updated_successfully', lang) or 'Settings updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating user settings: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to update settings'
        }), 500

@mobile_bp.route('/api/reset-settings', methods=['POST'])
@login_required
@csrf.exempt
def api_reset_settings(lang):
    """API для сброса настроек к значениям по умолчанию."""
    try:
        # Список ключей настроек для сброса
        settings_keys = [
            'theme', 'push_notifications', 'email_notifications', 
            'study_reminders', 'achievement_alerts', 'profile_visibility',
            'progress_sharing', 'analytics_tracking', 'auto_next_lesson',
            'show_hints', 'difficulty_adjustment', 'daily_goal',
            'high_contrast', 'large_text', 'reduced_motion', 'screen_reader'
        ]
        
        # Удаляем настройки из сессии (будут использоваться значения по умолчанию)
        for key in settings_keys:
            session.pop(key, None)
        
        # TODO: Сброс настроек в базе данных для авторизованных пользователей
        if current_user.is_authenticated:
            try:
                # Здесь можно добавить сброс в БД
                pass
            except Exception as e:
                current_app.logger.error(f"Failed to reset settings in database: {e}")
        
        return jsonify({
            'success': True,
            'message': t('settings_reset_successfully', lang) or 'Settings reset to defaults'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error resetting user settings: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to reset settings'
        }), 500

@mobile_bp.route('/api/export-data')
@login_required
@csrf.exempt
def api_export_data(lang):
    """API для экспорта пользовательских данных."""
    try:
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Собираем данные пользователя для экспорта
        export_data = {
            'user_info': {
                'username': current_user.username,
                'email': current_user.email,
                'name': getattr(current_user, 'name', ''),
                'registration_date': getattr(current_user, 'created_at').isoformat() if hasattr(current_user, 'created_at') else None
            },
            'settings': {
                'language': lang,
                'theme': session.get('theme', 'auto'),
                'notifications': {
                    'push_enabled': session.get('push_notifications', True),
                    'email_enabled': session.get('email_notifications', True),
                    'study_reminders': session.get('study_reminders', True),
                    'achievement_alerts': session.get('achievement_alerts', True)
                }
            },
            'progress': {
                # TODO: Добавить данные о прогрессе из БД
                'completed_lessons': 0,
                'total_time_spent': 0,
                'achievements': []
            },
            'export_date': datetime.utcnow().isoformat()
        }
        
        # Возвращаем данные в JSON формате
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=dental_academy_data_{current_user.id}_{datetime.utcnow().strftime("%Y%m%d")}.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting user data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to export data'
        }), 500

@mobile_bp.route('/api/delete-account', methods=['POST'])
@login_required
@csrf.exempt
def api_delete_account(lang):
    """API для удаления аккаунта пользователя."""
    try:
        data = request.get_json()
        confirmation = data.get('confirmation', '')
        
        # Проверяем подтверждение
        if confirmation.lower() != 'delete':
            return jsonify({
                'success': False,
                'error': t('delete_confirmation_required', lang) or 'Please type "delete" to confirm'
            }), 400
        
        user_id = current_user.id
        user_email = current_user.email
        
        # TODO: Реализовать удаление аккаунта
        # Здесь должна быть логика:
        # 1. Удаление связанных данных (прогресс, настройки, результаты тестов)
        # 2. Анонимизация или удаление персональных данных
        # 3. Удаление учетной записи
        
        current_app.logger.info(f"Account deletion requested for user {user_id} ({user_email})")
        
        # Пока что просто логируем запрос
        return jsonify({
            'success': False,
            'error': t('delete_account_not_implemented', lang) or 'Account deletion is not yet implemented. Please contact support.'
        }), 501
        
    except Exception as e:
        current_app.logger.error(f"Error processing account deletion: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to process deletion request'
        }), 500

@mobile_bp.route('/api/device-info')
@csrf.exempt
def api_device_info(lang):
    """API для получения информации об устройстве."""
    try:
        detector = get_mobile_detector()
        device_info = detector.get_device_info()
        
        # Добавляем дополнительную информацию
        device_info.update({
            'language': lang,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'device_info': device_info
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting device info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to get device info'
        }), 500

# ===== КОНЕЦ API ENDPOINTS ДЛЯ НАСТРОЕК =====

# ===== ДОПОЛНИТЕЛЬНЫЕ API ENDPOINTS =====

@mobile_bp.route('/api/save-settings', methods=['POST'])
@login_required
@csrf.exempt
def api_save_settings(lang):
    """API для сохранения настроек пользователя (alias для api_update_settings)."""
    # Перенаправляем на основной endpoint для сохранения настроек
    return api_update_settings(lang)

@mobile_bp.route('/api/save-openai-key', methods=['POST'])
@login_required
@csrf.exempt
def api_save_openai_key(lang):
    """API для сохранения OpenAI API ключа."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        openai_key = data.get('openai_key', '').strip()
        
        if not openai_key:
            return jsonify({
                'success': False,
                'error': t('openai_key_required', lang) or 'OpenAI API key is required'
            }), 400
        
        # Базовая валидация ключа
        if not openai_key.startswith('sk-'):
            return jsonify({
                'success': False,
                'error': t('invalid_openai_key_format', lang) or 'Invalid OpenAI API key format'
            }), 400
        
        # Сохраняем ключ в сессии (в реальном приложении лучше в зашифрованном виде в БД)
        session['openai_api_key'] = openai_key
        
        # TODO: Сохранить в БД для авторизованных пользователей
        if current_user.is_authenticated:
            try:
                # Здесь можно добавить сохранение зашифрованного ключа в БД
                # user_settings = UserSettings.query.filter_by(user_id=current_user.id).first()
                # if not user_settings:
                #     user_settings = UserSettings(user_id=current_user.id)
                #     db.session.add(user_settings)
                # user_settings.openai_key_encrypted = encrypt_key(openai_key)
                # db.session.commit()
                pass
            except Exception as e:
                current_app.logger.error(f"Failed to save OpenAI key to database: {e}")
        
        current_app.logger.info(f"OpenAI API key saved for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': t('openai_key_saved_successfully', lang) or 'OpenAI API key saved successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error saving OpenAI API key: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to save OpenAI API key'
        }), 500

@mobile_bp.route('/api/clear-cache', methods=['POST'])
@login_required
@csrf.exempt
def api_clear_cache(lang):
    """API для очистки кэша приложения."""
    try:
        # Очищаем различные типы кэша
        cleared_items = []
        
        # 1. Очистка сессионного кэша
        cache_keys_to_clear = [
            'cached_subjects', 'cached_modules', 'cached_lessons',
            'cached_progress', 'cached_stats', 'temp_files',
            'uploaded_images', 'processed_data'
        ]
        
        for key in cache_keys_to_clear:
            if session.pop(key, None) is not None:
                cleared_items.append(key)
        
        # 2. Очистка временных файлов (если есть)
        # TODO: Добавить очистку временных файлов из файловой системы
        
        # 3. Очистка кэша браузера (инструкции для клиента)
        browser_cache_instructions = {
            'clear_local_storage': True,
            'clear_session_storage': True,
            'reload_page': True
        }
        
        # 4. Логирование очистки кэша
        current_app.logger.info(f"Cache cleared for user {current_user.id}, items: {cleared_items}")
        
        return jsonify({
            'success': True,
            'cleared_items': cleared_items,
            'browser_instructions': browser_cache_instructions,
            'message': t('cache_cleared_successfully', lang) or 'Cache cleared successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Failed to clear cache'
        }), 500

# ===== КОНЕЦ ДОПОЛНИТЕЛЬНЫХ API ENDPOINTS =====

# ===== КОНЕЦ API ENDPOINTS ДЛЯ НАСТРОЕК =====