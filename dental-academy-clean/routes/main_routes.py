# routes/main_routes.py - Main application routes

from flask import Blueprint, render_template, g, send_from_directory, request, session, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_required
from models import LearningPath, Subject, Module, Lesson, UserProgress
from extensions import db

# Создаем blueprint с языковой поддержкой
main_bp = Blueprint('main', __name__, url_prefix='/<string:lang>')

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@main_bp.before_request
def before_request_main():
    """Обработка языка для всех маршрутов main"""
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
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

@main_bp.route('/')
def index(lang):
    """Main landing page"""
    
    # Get some basic statistics for the homepage
    stats = {
        'total_paths': LearningPath.query.filter_by(is_active=True).count(),
        'total_subjects': Subject.query.count(),
        'total_modules': Module.query.count(),
        'total_lessons': Lesson.query.count()
    }
    
    # Get featured learning paths
    featured_paths = LearningPath.query.filter_by(is_active=True).order_by(LearningPath.order).limit(3).all()
    
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

@main_bp.route('/big-info')
def big_info(lang):
    """BIG регистрация - главная landing страница"""
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

@main_bp.route('/community')
@login_required
def community(lang):
    """Community forum page"""
    from models import ForumCategory, ForumTopic
    
    # Получаем все категории с количеством тем
    categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
    
    # Получаем последние темы
    recent_topics = ForumTopic.query.order_by(ForumTopic.created_at.desc()).limit(10).all()
    
    # Получаем популярные темы (по количеству просмотров)
    popular_topics = ForumTopic.query.order_by(ForumTopic.views_count.desc()).limit(5).all()
    
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
    
    # Сначала закрепленные темы, потом обычные
    topics_query = ForumTopic.query.filter_by(category_id=forum_category.id)
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
                         category=category,
                         forum_category=forum_category,
                         topics=topics,
                         all_categories=all_categories,
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
                         all_categories=all_categories,
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
                'error': 'Все поля обязательны для заполнения'
            }), 400
        
        if len(title) < 5:
            return jsonify({
                'success': False,
                'error': 'Заголовок должен содержать минимум 5 символов'
            }), 400
        
        if len(content) < 10:
            return jsonify({
                'success': False,
                'error': 'Содержимое должно содержать минимум 10 символов'
            }), 400
        
        # Проверяем существование категории
        category = ForumCategory.query.get(category_id)
        if not category:
            return jsonify({
                'success': False,
                'error': 'Категория не найдена'
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
            'message': 'Тема успешно создана',
            'topic_id': topic.id,
            'redirect_url': url_for('main.community_topic', lang=lang, topic_id=topic.id)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating topic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при создании темы'
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
        'message': 'Mentora Dental Academy is running',
        'version': '1.0.0',
        'database': 'connected'
    }) 
