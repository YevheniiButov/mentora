# routes/main_routes.py - Main application routes

from flask import Blueprint, render_template, g, send_from_directory, request, session, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_required
from models import LearningPath, Subject, Module, Lesson, UserProgress, ForumTopic, ForumPost
from extensions import db
from sqlalchemy import or_
from datetime import datetime, timezone

def is_user_admin(user):
    """Helper function to check if user is admin"""
    if not hasattr(user, 'role') or not user.role:
        return False
    return user.role == 'admin'

# Создаем blueprint с языковой поддержкой
main_bp = Blueprint('main', __name__, url_prefix='/<string:lang>')

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@main_bp.before_request
def before_request_main():
    """Обработка языка для всех маршрутов main"""
    # ВАЖНО: Не возвращаем ничего, чтобы не блокировать запрос
    # Flask сам определит правильный endpoint на основе маршрута
    
    # Извлекаем язык из пути напрямую (view_args еще может быть не установлен)
    path = request.path
    
    # Логируем для диагностики
    if path in ['/en/', '/uk/', '/ru/', '/nl/', '/en', '/uk', '/ru', '/nl']:
        from flask import current_app
        current_app.logger.info(f"🔍 before_request_main: path={path}, view_args={request.view_args}")
    
    lang_from_url = None
    
    # Пытаемся получить из view_args (если уже установлен)
    if request.view_args:
        lang_from_url = request.view_args.get('lang')
    
    # Если не получилось, пытаемся извлечь из пути
    if not lang_from_url:
        path_parts = path.strip('/').split('/')
        if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
            lang_from_url = path_parts[0]
    
    # Специальная обработка для /big-info без языка - используем нидерландский по умолчанию
    if not lang_from_url and '/big-info' in path:
        lang_from_url = 'nl'
    
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') or DEFAULT_LANGUAGE
    
    # Обновляем сессию
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@main_bp.context_processor
def inject_lang_main():
    """Добавляет lang в контекст шаблонов"""
    return dict(lang=getattr(g, 'lang', DEFAULT_LANGUAGE))

@main_bp.route('/', strict_slashes=False)
@main_bp.route('', strict_slashes=False)  # Allow /en without trailing slash
def index(lang):
    """Main landing page"""
    from flask import request
    
    host = request.host.lower()
    
    # Для mentora.com.in показываем космический дизайн
    if 'mentora.com.in' in host:
        return render_template('mentora_landing.html')
    
    # Get some basic statistics for the homepage
    stats = {
        'total_paths': LearningPath.query.count(),
        'total_subjects': Subject.query.count(),
        'total_modules': Module.query.count(),
        'total_lessons': Lesson.query.count()
    }
    
    # Get featured learning paths
    featured_paths = LearningPath.query.limit(3).all()
    
    # Get user progress if authenticated
    user_progress = None
    if current_user.is_authenticated:
        user_progress = current_user.get_progress_stats()
    
    return render_template('index.html', 
                         stats=stats,
                         featured_paths=featured_paths,
                         user_progress=user_progress,
                         lang=lang)

@main_bp.route('/home')
def home(lang):
    """Home page - redirect to index"""
    return index(lang)

@main_bp.route('/about')
def about(lang):
    """About page"""
    return render_template('about.html', lang=lang)

@main_bp.route('/contact')
def contact(lang):
    """Contact page"""
    return render_template('contact.html', lang=lang)

@main_bp.route('/features')
def features(lang):
    """Features overview page"""
    return render_template('features.html', lang=lang)

@main_bp.route('/privacy')
def privacy(lang):
    """Privacy policy page"""
    return render_template('privacy.html', lang=lang)

@main_bp.route('/terms')
def terms(lang):
    """Terms of service page"""
    return render_template('terms.html', lang=lang)

@main_bp.route('/faq')
def faq(lang):
    """FAQ page"""
    return render_template('faq.html', lang=lang)

@main_bp.route('/auth/login')
def auth_login_redirect(lang):
    """Handle auth login page directly"""
    from flask import g, session
    
    # Set language
    g.lang = lang
    session['lang'] = lang
    
    return render_template('auth/login.html', lang=lang)

@main_bp.route('/auth/register')
def auth_register_redirect(lang):
    """Redirect to auth register page"""
    return redirect(url_for('auth.register', lang=lang))

@main_bp.route('/coming-soon')
def coming_soon(lang):
    """Coming Soon page - перенаправляет на карту обучения"""
    return redirect(url_for('learning_map_bp.learning_map', lang=lang))


@main_bp.route('/farmacie/advanced-drug-checker')
@login_required
def advanced_drug_checker(lang):
    """Расширенный Drug Interaction Checker"""
    
    # База данных лекарственных взаимодействий
    drug_interactions = {
        'warfarine': {
            'name': 'Warfarine',
            'category': 'Anticoagulantia',
            'interactions': {
                'ibuprofen': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd bloedingsrisico door remming van bloedplaatjesaggregatie',
                    'recommendation': 'Vermijd combinatie. Gebruik paracetamol als alternatief.',
                    'mechanism': 'Synergistische remming van bloedstolling'
                },
                'aspirine': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op bloedingen',
                    'recommendation': 'Strikte monitoring van INR vereist',
                    'mechanism': 'Dubbele remming van bloedstolling'
                },
                'omeprazol': {
                    'severity': 'MODERATE',
                    'description': 'Mogelijk verhoogde warfarine effectiviteit',
                    'recommendation': 'Monitor INR frequentie verhogen',
                    'mechanism': 'CYP2C19 remming'
                }
            }
        },
        'digoxine': {
            'name': 'Digoxine',
            'category': 'Cardiaca',
            'interactions': {
                'furosemide': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op digitalis toxiciteit door hypokaliëmie',
                    'recommendation': 'Strikte monitoring van kalium en digoxine spiegel',
                    'mechanism': 'Kaliumverlies door diurese'
                },
                'amiodarone': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogde digoxine concentratie door remming van uitscheiding',
                    'recommendation': 'Digoxine dosering met 50% verlagen',
                    'mechanism': 'P-gp remming'
                }
            }
        },
        'simvastatine': {
            'name': 'Simvastatine',
            'category': 'Lipidenverlagers',
            'interactions': {
                'amiodarone': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op rhabdomyolyse',
                    'recommendation': 'Simvastatine dosering beperken tot 20mg/dag',
                    'mechanism': 'CYP3A4 remming'
                }
            }
        }
    }
    
    # Категории лекарств для фильтрации
    drug_categories = {
        'Anticoagulantia': ['warfarine', 'acenocoumarol', 'fenprocoumon'],
        'Cardiaca': ['digoxine', 'amiodarone', 'verapamil', 'diltiazem'],
        'Lipidenverlagers': ['simvastatine', 'atorvastatine', 'pravastatine'],
        'Beta-blokkers': ['metoprolol', 'atenolol', 'bisoprolol'],
        'Antiplaatjesmiddelen': ['clopidogrel', 'aspirine', 'ticagrelor'],
        'NSAIDs': ['ibuprofen', 'diclofenac', 'naproxen'],
        'Protonpompremmers': ['omeprazol', 'pantoprazol', 'esomeprazol']
    }
    
    return render_template(
        'learning/advanced_drug_checker.html',
        drug_interactions=drug_interactions,
        drug_categories=drug_categories,
        lang=lang
    )

@main_bp.route('/farmacie/api/check-interaction', methods=['POST'])
@login_required
def check_interaction(lang):
    """API endpoint для проверки взаимодействий"""
    import json
    
    try:
        data = request.get_json()
        drug1 = data.get('drug1', '').lower()
        drug2 = data.get('drug2', '').lower()
        
        if not drug1 or not drug2:
            return jsonify({'error': 'Beide medicijnen moeten worden ingevuld'}), 400
        
        # База данных взаимодействий (упрощенная версия)
        interactions_db = {
            'warfarine+ibuprofen': {
                'severity': 'MAJOR',
                'description': 'Verhoogd bloedingsrisico',
                'recommendation': 'Vermijd combinatie',
                'mechanism': 'Synergistische remming van bloedstolling'
            },
            'warfarine+aspirine': {
                'severity': 'MAJOR',
                'description': 'Verhoogd risico op bloedingen',
                'recommendation': 'Strikte monitoring van INR',
                'mechanism': 'Dubbele remming van bloedstolling'
            },
            'digoxine+furosemide': {
                'severity': 'MAJOR',
                'description': 'Digitalis toxiciteit risico',
                'recommendation': 'Monitor kalium en digoxine spiegel',
                'mechanism': 'Kaliumverlies door diurese'
            },
            'simvastatine+amiodarone': {
                'severity': 'MAJOR',
                'description': 'Verhoogd risico op rhabdomyolyse',
                'recommendation': 'Dosering beperken tot 20mg/dag',
                'mechanism': 'CYP3A4 remming'
            }
        }
        
        # Проверяем взаимодействие
        key1 = f"{drug1}+{drug2}"
        key2 = f"{drug2}+{drug1}"
        
        interaction = interactions_db.get(key1) or interactions_db.get(key2)
        
        if interaction:
            return jsonify({
                'found': True,
                'interaction': interaction
            })
        else:
            return jsonify({
                'found': False,
                'message': 'Geen bekende interactie gevonden'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error in check_interaction: {e}")
        return jsonify({'error': 'Er is een fout opgetreden'}), 500

@main_bp.route('/farmacie/api/search-drugs')
@login_required
def search_drugs(lang):
    """API endpoint для поиска лекарств"""
    from flask import jsonify
    
    try:
        query = request.args.get('q', '').lower()
        
        # База данных лекарств
        drugs_db = {
            'warfarine': {'name': 'Warfarine', 'category': 'Anticoagulantia'},
            'acenocoumarol': {'name': 'Acenocoumarol', 'category': 'Anticoagulantia'},
            'fenprocoumon': {'name': 'Fenprocoumon', 'category': 'Anticoagulantia'},
            'digoxine': {'name': 'Digoxine', 'category': 'Cardiaca'},
            'amiodarone': {'name': 'Amiodarone', 'category': 'Cardiaca'},
            'verapamil': {'name': 'Verapamil', 'category': 'Cardiaca'},
            'diltiazem': {'name': 'Diltiazem', 'category': 'Cardiaca'},
            'simvastatine': {'name': 'Simvastatine', 'category': 'Lipidenverlagers'},
            'atorvastatine': {'name': 'Atorvastatine', 'category': 'Lipidenverlagers'},
            'pravastatine': {'name': 'Pravastatine', 'category': 'Lipidenverlagers'},
            'metoprolol': {'name': 'Metoprolol', 'category': 'Beta-blokkers'},
            'atenolol': {'name': 'Atenolol', 'category': 'Beta-blokkers'},
            'bisoprolol': {'name': 'Bisoprolol', 'category': 'Beta-blokkers'},
            'clopidogrel': {'name': 'Clopidogrel', 'category': 'Antiplaatjesmiddelen'},
            'aspirine': {'name': 'Aspirine', 'category': 'Antiplaatjesmiddelen'},
            'ticagrelor': {'name': 'Ticagrelor', 'category': 'Antiplaatjesmiddelen'},
            'ibuprofen': {'name': 'Ibuprofen', 'category': 'NSAIDs'},
            'diclofenac': {'name': 'Diclofenac', 'category': 'NSAIDs'},
            'naproxen': {'name': 'Naproxen', 'category': 'NSAIDs'},
            'omeprazol': {'name': 'Omeprazol', 'category': 'Protonpompremmers'},
            'pantoprazol': {'name': 'Pantoprazol', 'category': 'Protonpompremmers'},
            'esomeprazol': {'name': 'Esomeprazol', 'category': 'Protonpompremmers'}
        }
        
        # Поиск лекарств
        results = []
        for drug_id, drug_data in drugs_db.items():
            if query in drug_id or query in drug_data['name'].lower():
                results.append({
                    'id': drug_id,
                    'name': drug_data['name'],
                    'category': drug_data['category']
                })
        
        return jsonify({'drugs': results})
    except Exception as e:
        current_app.logger.error(f"Error in search_drugs: {e}")
        return jsonify({'error': 'Er is een fout opgetreden'}), 500

@main_bp.route('/big-info', strict_slashes=False)
def big_info(lang):
    """BIG регистрация - главная landing страница"""
    # Если язык не указан или не поддерживается, используем нидерландский по умолчанию
    if not lang or lang not in SUPPORTED_LANGUAGES:
        lang = 'nl'
        g.lang = 'nl'
        session['lang'] = 'nl'
    
    return render_template(
        'big_info/index.html',
        title='BIG Registratie - Complete gids',
        current_user=current_user,
        lang=lang
    )

@main_bp.route('/big-info/eu/<profession>')
def big_info_eu_profession(lang, profession):
    """BIG регистрация - детальные страницы для каждой EU профессии"""
    
    # Проверяем, что профессия существует
    valid_professions = ['tandarts', 'huisarts', 'apotheker', 'verpleegkundige']
    if profession not in valid_professions:
        return redirect(url_for('main.big_info', lang=lang))
    
    # Выбираем соответствующий EU шаблон
    template_map = {
        'tandarts': 'big_info/tandarts_eu.html',
        'huisarts': 'big_info/huisarts_eu.html',
        'apotheker': 'big_info/apotheker_eu.html',
        'verpleegkundige': 'big_info/verpleegkundige_eu.html'
    }
    
    template_name = template_map.get(profession)
    if not template_name:
        return redirect(url_for('main.big_info', lang=lang))
    
    return render_template(
        template_name,
        title=f'BIG Registratie {profession.title()} (EU/EEA) - Complete gids',
        profession=profession,
        current_user=current_user,
        lang=lang
    )

@main_bp.route('/big-info/<profession>')
def big_info_profession(lang, profession):
    """BIG регистрация - детальные страницы для каждой профессии (не-EU)"""
    
    # Проверяем, что профессия существует
    valid_professions = ['tandarts', 'huisarts', 'apotheker', 'verpleegkundige']
    if profession not in valid_professions:
        return redirect(url_for('main.big_info', lang=lang))
    
    # Выбираем соответствующий шаблон
    template_map = {
        'tandarts': 'big_info/tandarts.html',
        'huisarts': 'big_info/huisarts.html',
        'apotheker': 'big_info/apotheker.html',
        'verpleegkundige': 'big_info/verpleegkundige.html'
    }
    
    template_name = template_map.get(profession)
    if not template_name:
        return redirect(url_for('main.big_info', lang=lang))
    
    return render_template(
        template_name,
        title=f'BIG Registratie {profession.title()} - Complete gids',
        profession=profession,
        current_user=current_user,
        lang=lang
    )

@main_bp.route('/favicon.ico')
def favicon():
    """Favicon route"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/community', strict_slashes=False)
@login_required
def community(lang):
    """Community forum page"""
    from models import ForumCategory, ForumTopic
    
    # Получаем все категории с количеством тем
    categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    # Получаем последние темы (исключаем удаленные)
    recent_topics = ForumTopic.query.filter(
        or_(ForumTopic.is_deleted == False, ForumTopic.is_deleted.is_(None))
    ).order_by(ForumTopic.created_at.desc()).limit(10).all()
    
    # Получаем популярные темы (по количеству просмотров, исключаем удаленные)
    popular_topics = ForumTopic.query.filter(
        or_(ForumTopic.is_deleted == False, ForumTopic.is_deleted.is_(None))
    ).order_by(ForumTopic.views_count.desc()).limit(5).all()
    
    return render_template('community/index.html', 
                         categories=categories,
                         recent_topics=recent_topics,
                         popular_topics=popular_topics,
                         lang=lang)

@main_bp.route('/community/category/<category>')
@login_required
def community_category(lang, category):
    """Community category page"""
    from models import ForumCategory, ForumTopic
    
    # Находим категорию по slug
    forum_category = ForumCategory.query.filter_by(slug=category, is_active=True).first()
    
    if not forum_category:
        return redirect(url_for('main.community', lang=lang))
    
    # Получаем темы в этой категории
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Сначала закрепленные темы, потом обычные (исключаем удаленные)
    topics_query = ForumTopic.query.filter_by(category_id=forum_category.id).filter(
        or_(ForumTopic.is_deleted == False, ForumTopic.is_deleted.is_(None))
    )
    topics = topics_query.order_by(
        ForumTopic.is_sticky.desc(),
        ForumTopic.created_at.desc()
    ).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Получаем все категории для навигации
    all_categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    return render_template('community/category.html',
                         category=forum_category,
                         topics=topics,
                         categories=all_categories,
                         lang=lang)

@main_bp.route('/community/topic/<int:topic_id>')
@login_required
def community_topic(lang, topic_id):
    """Individual topic page"""
    from models import ForumTopic, ForumPost, ForumCategory
    
    # Находим тему
    topic = ForumTopic.query.get_or_404(topic_id)
    
    # Увеличиваем счетчик просмотров
    topic.increment_views()
    
    # Получаем посты в теме
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts = ForumPost.query.filter_by(
        topic_id=topic_id, 
        is_deleted=False
    ).order_by(ForumPost.created_at.asc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # Получаем все категории для навигации
    all_categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    return render_template('community/topic.html',
                         topic=topic,
                         posts=posts,
                         categories=all_categories,
                         lang=lang)

@main_bp.route('/community/new-topic')
@login_required
def new_topic(lang):
    """Create new topic page"""
    from models import ForumCategory
    
    # Получаем все категории для выбора
    categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    return render_template('community/new_topic.html', 
                         categories=categories, 
                         lang=lang)

@main_bp.route('/community/create-topic', methods=['POST'])
@login_required
def create_topic(lang):
    """Create new topic"""
    from models import ForumTopic, ForumPost, ForumCategory
    from flask import jsonify
    
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id')
        
        # Валидация
        if not title or not content or not category_id:
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        if len(title) < 5:
            return jsonify({
                'success': False,
                'error': 'The title must contain at least 5 characters.'
            }), 400
        
        if len(content) < 10:
            return jsonify({
                'success': False,
                'error': 'Content must be at least 10 characters long.'
            }), 400
        
        # Проверяем существование категории
        category = ForumCategory.query.get(category_id)
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 400
        
        # Создаем тему
        topic = ForumTopic(
            title=title,
            content=content,
            category_id=category_id,
            author_id=current_user.id
        )
        
        db.session.add(topic)
        db.session.flush()  # Получаем ID темы
        
        # Создаем первый пост (содержимое темы)
        post = ForumPost(
            content=content,
            topic_id=topic.id,
            author_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Topic successfully created',
            'topic_id': topic.id,
            'redirect_url': url_for('main.community_topic', lang=lang, topic_id=topic.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating topic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error creating topic'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/reply', methods=['POST'])
@login_required
def reply_to_topic(lang, topic_id):
    """Reply to a topic"""
    from models import ForumTopic, ForumPost
    
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        # Валидация
        if not content:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        if len(content) < 1:
            return jsonify({
                'success': False,
                'error': 'Message must contain at least 1 character'
            }), 400
        
        # Проверяем существование темы
        topic = ForumTopic.query.get(topic_id)
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic not found'
            }), 404
        
        # Создаем ответ
        post = ForumPost(
            content=content,
            topic_id=topic_id,
            author_id=current_user.id
        )
        
        db.session.add(post)
        
        # Обновляем счетчик ответов в теме
        topic.replies_count = ForumPost.query.filter_by(topic_id=topic_id).count() + 1
        topic.last_activity = db.func.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Answer successfully added',
            'post': {
                'id': post.id,
                'content': post.content,
                'author_name': f"{current_user.first_name} {current_user.last_name}",
                'created_at': post.created_at.strftime('%d.%m.%Y %H:%M'),
                'author_id': current_user.id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating reply: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error sending reply'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/edit')
@login_required
def edit_topic(lang, topic_id):
    """Edit topic page"""
    from models import ForumTopic, ForumCategory
    
    topic = ForumTopic.query.get_or_404(topic_id)
    
    # Проверяем права на редактирование
    if topic.author_id != current_user.id and not is_user_admin(current_user):
        flash('You do not have permission to edit this topic', 'error')
        return redirect(url_for('main.community_topic', lang=lang, topic_id=topic_id))
    
    categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    return render_template('community/edit_topic.html',
                         topic=topic,
                         categories=categories,
                         lang=lang)

@main_bp.route('/community/topic/<int:topic_id>/update', methods=['POST'])
@login_required
def update_topic(lang, topic_id):
    """Update topic"""
    from models import ForumTopic, ForumCategory
    from flask import jsonify
    
    try:
        topic = ForumTopic.query.get_or_404(topic_id)
        
        # Проверяем права на редактирование
        if topic.author_id != current_user.id and not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to edit this topic'
            }), 403
        
        data = request.get_json()
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id')
        
        # Валидация
        if not title or not content or not category_id:
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        if len(title) < 5:
            return jsonify({
                'success': False,
                'error': 'The title must contain at least 5 characters.'
            }), 400
        
        if len(content) < 10:
            return jsonify({
                'success': False,
                'error': 'Content must be at least 10 characters long.'
            }), 400
        
        # Проверяем существование категории
        category = ForumCategory.query.get(category_id)
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 400
        
        # Обновляем тему
        topic.title = title
        topic.content = content
        topic.category_id = category_id
        topic.updated_at = db.func.now()
        
        # Обновляем первый пост (содержимое темы)
        first_post = topic.posts.filter_by(author_id=topic.author_id).first()
        if first_post:
            first_post.content = content
            first_post.mark_as_edited()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Topic successfully updated',
            'redirect_url': url_for('main.community_topic', lang=lang, topic_id=topic.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating topic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error updating topic'
        }), 500

@main_bp.route('/community/post/<int:post_id>/edit')
@login_required
def edit_post(lang, post_id):
    """Edit post page"""
    from models import ForumPost
    
    post = ForumPost.query.get_or_404(post_id)
    
    # Проверяем права на редактирование
    if post.author_id != current_user.id and not is_user_admin(current_user):
        flash('You do not have permission to edit this post', 'error')
        return redirect(url_for('main.community_topic', lang=lang, topic_id=post.topic_id))
    
    return render_template('community/edit_post.html',
                         post=post,
                         lang=lang)

@main_bp.route('/community/post/<int:post_id>/update', methods=['POST'])
@login_required
def update_post(lang, post_id):
    """Update post"""
    from models import ForumPost
    from flask import jsonify
    
    try:
        post = ForumPost.query.get_or_404(post_id)
        
        # Проверяем права на редактирование
        if post.author_id != current_user.id and not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to edit this post'
            }), 403
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        # Валидация
        if not content:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400
        
        if len(content) < 1:
            return jsonify({
                'success': False,
                'error': 'Message must contain at least 1 character'
            }), 400
        
        # Обновляем пост
        post.content = content
        post.mark_as_edited()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post successfully updated',
            'redirect_url': url_for('main.community', lang=lang)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating post: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error updating post'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/delete', methods=['POST'])
@login_required
def delete_topic(lang, topic_id):
    """Delete topic (admin or topic author)"""
    from models import ForumTopic
    from flask import jsonify
    
    try:
        topic = ForumTopic.query.get_or_404(topic_id)
        
        # Проверяем права администратора или автора темы
        if not is_user_admin(current_user) and topic.author_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'You do not have permission to delete this topic'
            }), 403
        
        # Удаляем тему и все связанные посты
        db.session.delete(topic)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Topic successfully deleted',
            'redirect_url': url_for('main.community', lang=lang)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting topic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error deleting topic'
        }), 500

@main_bp.route('/community/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(lang, post_id):
    """Delete post (admin only)"""
    from models import ForumPost
    from flask import jsonify
    
    try:
        post = ForumPost.query.get_or_404(post_id)
        
        # Проверяем права администратора
        if not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to delete posts'
            }), 403
        
        # Мягкое удаление поста
        post.soft_delete(current_user.id)
        
        # Обновляем статистику темы
        post.topic.update_reply_stats()
        
        return jsonify({
            'success': True,
            'message': 'Post successfully deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting post: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error deleting post'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/toggle-sticky', methods=['POST'])
@login_required
def toggle_topic_sticky(lang, topic_id):
    """Toggle topic sticky status (admin only)"""
    from models import ForumTopic
    from flask import jsonify
    
    try:
        topic = ForumTopic.query.get_or_404(topic_id)
        
        # Проверяем права администратора
        if not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to change topic status'
            }), 403
        
        # Переключаем статус закрепления
        topic.is_sticky = not topic.is_sticky
        topic.status = 'pinned' if topic.is_sticky else 'normal'
        
        db.session.commit()
        
        status_text = 'pinned' if topic.is_sticky else 'normal'
        
        return jsonify({
            'success': True,
            'message': f'Тема {status_text}',
            'is_sticky': topic.is_sticky
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling topic sticky: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error changing topic status'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/toggle-lock', methods=['POST'])
@login_required
def toggle_topic_lock(lang, topic_id):
    """Toggle topic lock status (admin only)"""
    from models import ForumTopic
    from flask import jsonify
    
    try:
        topic = ForumTopic.query.get_or_404(topic_id)
        
        # Проверяем права администратора
        if not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to lock topics'
            }), 403
        
        # Переключаем статус блокировки
        topic.is_locked = not topic.is_locked
        topic.status = 'locked' if topic.is_locked else 'normal'
        
        db.session.commit()
        
        status_text = 'locked' if topic.is_locked else 'normal'
        
        return jsonify({
            'success': True,
            'message': f'Topic {status_text}',
            'is_locked': topic.is_locked
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling topic lock: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error changing topic status'
        }), 500

@main_bp.route('/community/topic/<int:topic_id>/content')
@login_required
def get_topic_content(lang, topic_id):
    """Get topic content for AJAX loading"""
    from models import ForumTopic, ForumPost
    from flask import jsonify
    
    try:
        topic = ForumTopic.query.get_or_404(topic_id)
        
        # Увеличиваем счетчик просмотров
        topic.increment_views()
        
        # Получаем посты в теме
        posts = ForumPost.query.filter_by(
            topic_id=topic_id, 
            is_deleted=False
        ).order_by(ForumPost.created_at.asc()).all()
        
        # Формируем данные для JSON
        topic_data = {
            'id': topic.id,
            'title': topic.title,
            'content': topic.content,
            'author': {
                'id': topic.author.id,
                'name': f"{topic.author.first_name} {topic.author.last_name}",
                'email': topic.author.email
            },
            'category': {
                'id': topic.category.id,
                'name': topic.category.name,
                'slug': topic.category.slug
            },
            'created_at': topic.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': topic.updated_at.strftime('%d.%m.%Y %H:%M') if topic.updated_at else None,
            'last_reply_at': topic.last_reply_at.strftime('%d.%m.%Y %H:%M') if topic.last_reply_at else None,
            'views_count': topic.views_count,
            'replies_count': topic.replies_count,
            'is_sticky': topic.is_sticky,
            'is_locked': topic.is_locked,
            'status': topic.status,
            'can_edit': topic.author_id == current_user.id or is_user_admin(current_user),
            'can_delete': topic.author_id == current_user.id or is_user_admin(current_user),
            'can_moderate': is_user_admin(current_user)
        }
        
        # Формируем данные постов
        posts_data = []
        for post in posts:
            post_data = {
                'id': post.id,
                'content': post.content,
                'author': {
                    'id': post.author.id,
                    'name': f"{post.author.first_name} {post.author.last_name}",
                    'email': post.author.email
                },
                'created_at': post.created_at.strftime('%d.%m.%Y %H:%M'),
                'updated_at': post.updated_at.strftime('%d.%m.%Y %H:%M') if post.updated_at else None,
                'is_edited': post.is_edited,
                'is_deleted': post.is_deleted,
                'can_edit': post.author_id == current_user.id or is_user_admin(current_user),
                'can_delete': is_user_admin(current_user)
            }
            posts_data.append(post_data)
        
        return jsonify({
            'success': True,
            'topic': topic_data,
            'posts': posts_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting topic content: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error loading topic'
        }), 500

# API endpoints for message editing and deletion
@main_bp.route('/api/community/message/edit', methods=['POST'])
@login_required
def api_edit_message(lang):
    """API endpoint for editing messages (topics or posts)"""
    try:
        # Debug logging
        current_app.logger.info(f"=== EDIT MESSAGE DEBUG ===")
        current_app.logger.info(f"Current user: {current_user}")
        current_app.logger.info(f"Current user ID: {getattr(current_user, 'id', 'NO_ID')}")
        current_app.logger.info(f"Current user role: {getattr(current_user, 'role', 'NO_ROLE')}")
        current_app.logger.info(f"Is admin: {is_user_admin(current_user)}")
        
        data = request.get_json()
        current_app.logger.info(f"Request data: {data}")
        
        message_id = data.get('message_id')
        message_type = data.get('message_type')  # 'topic' or 'post'
        new_content = data.get('content', '').strip()
        
        current_app.logger.info(f"Parsed: message_id={message_id}, message_type={message_type}, content_length={len(new_content)}")
        
        if not message_id or not message_type or not new_content:
            current_app.logger.error(f"Missing parameters: message_id={message_id}, message_type={message_type}, content={bool(new_content)}")
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Check if user is admin
        if not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin privileges required.'
            }), 403
        
        if message_type == 'topic':
            # Edit topic
            topic = ForumTopic.query.get_or_404(message_id)
            topic.content = new_content
            topic.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Topic updated successfully',
                'updated_at': topic.updated_at.strftime('%d.%m.%Y %H:%M')
            })
            
        elif message_type == 'post':
            # Edit post
            post = ForumPost.query.get_or_404(message_id)
            post.content = new_content
            post.updated_at = datetime.now(timezone.utc)
            post.is_edited = True
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Post updated successfully',
                'updated_at': post.updated_at.strftime('%d.%m.%Y %H:%M')
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid message type'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error editing message: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': str(type(e))
        }), 500

@main_bp.route('/api/community/message/delete', methods=['POST'])
@login_required
def api_delete_message(lang):
    """API endpoint for deleting messages (topics or posts)"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        message_type = data.get('message_type')  # 'topic' or 'post'
        
        if not message_id or not message_type:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Check if user is admin
        if not is_user_admin(current_user):
            return jsonify({
                'success': False,
                'error': 'Access denied. Admin privileges required.'
            }), 403
        
        if message_type == 'topic':
            # Delete topic
            topic = ForumTopic.query.get_or_404(message_id)
            
            # Soft delete all posts in this topic
            ForumPost.query.filter_by(topic_id=message_id).update({
                'is_deleted': True, 
                'deleted_at': datetime.now(timezone.utc),
                'deleted_by': current_user.id
            })
            
            # Soft delete the topic
            topic.is_deleted = True
            topic.deleted_at = datetime.now(timezone.utc)
            topic.deleted_by = current_user.id
            topic.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Topic deleted successfully'
            })
            
        elif message_type == 'post':
            # Delete post
            post = ForumPost.query.get_or_404(message_id)
            post.is_deleted = True
            post.deleted_at = datetime.now(timezone.utc)
            post.deleted_by = current_user.id
            post.updated_at = datetime.now(timezone.utc)
            
            # Update topic stats
            topic = ForumTopic.query.get(post.topic_id)
            if topic:
                topic.replies_count = ForumPost.query.filter_by(
                    topic_id=post.topic_id, 
                    is_deleted=False
                ).count()
                topic.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Post deleted successfully'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid message type'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"Error deleting message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete message'
        }), 500

@main_bp.route('/api/community/user/is-admin')
@login_required
def api_check_admin(lang):
    """API endpoint to check if current user is admin"""
    try:
        # Debug logging
        current_app.logger.info(f"=== ADMIN CHECK DEBUG ===")
        current_app.logger.info(f"Current user object: {current_user}")
        current_app.logger.info(f"Current user ID: {getattr(current_user, 'id', 'NO_ID')}")
        current_app.logger.info(f"Current user authenticated: {getattr(current_user, 'is_authenticated', 'NO_AUTH_ATTR')}")
        current_app.logger.info(f"Current user role: {getattr(current_user, 'role', 'NO_ROLE')}")
        current_app.logger.info(f"Has role attr: {hasattr(current_user, 'role')}")
        
        # Check if user is admin - handle None role gracefully
        is_admin = False
        user_role = getattr(current_user, 'role', None)
        if user_role:
            is_admin = user_role == 'admin'
        
        result = {
            'success': True,
            'is_admin': is_admin,
            'user_id': getattr(current_user, 'id', None),
            'user_role': user_role,
            'debug_info': {
                'has_role_attr': hasattr(current_user, 'role'),
                'role_value': user_role,
                'is_authenticated': getattr(current_user, 'is_authenticated', None)
            }
        }
        current_app.logger.info(f"Admin check result: {result}")
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in admin check: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': str(type(e))
        }), 500

@main_bp.route('/test')
def test_page():
    """Тестовая страница для отладки"""
    return render_template('test_login.html')

@main_bp.route('/health')
def health():
    """Health check endpoint для мониторинга"""
    return jsonify({
        'status': 'healthy',
        'message': 'Mentora Professional Platform is running',
        'version': '1.0.0',
        'database': 'connected'
    })

