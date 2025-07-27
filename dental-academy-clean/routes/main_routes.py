# routes/main_routes.py - Main application routes

from flask import Blueprint, render_template, g, send_from_directory, request, session, current_app, jsonify, redirect, url_for
from flask_login import current_user, login_required
from models import LearningPath, Subject, Module, Lesson, UserProgress

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
        current_user=current_user
    )

@main_bp.route('/big-info/<profession>')
def big_info_profession(lang, profession):
    """BIG регистрация - детальные страницы для каждой профессии"""
    
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
        current_user=current_user
    )

@main_bp.route('/favicon.ico')
def favicon():
    """Favicon route"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/community')
@login_required
def community(lang):
    """Community/Forum страница"""
    
    # Данные форумных категорий
    forum_categories = [
        {
            'id': 1,
            'name': 'Algemene Discussies',
            'description': 'Общие обсуждения медицинских тем',
            'icon': 'message-circle',
            'color': 'primary',
            'posts_count': 142,
            'members_count': 89,
            'last_activity': {
                'user': 'Dr. van Berg',
                'topic': 'Nieuwe richtlijnen 2024',
                'time': '2 uur geleden'
            }
        },
        {
            'id': 2,
            'name': '🦷 Tandheelkunde',
            'description': 'Discussies over tandheelkundige praktijk',
            'icon': 'tooth',
            'color': 'info',
            'posts_count': 98,
            'members_count': 45,
            'last_activity': {
                'user': 'Tandarts Sarah',
                'topic': 'Endodontie technieken',
                'time': '4 uur geleden'
            }
        },
        {
            'id': 3,
            'name': '💊 Farmacie',
            'description': 'Medicatiebegeleiding en farmacologie',
            'icon': 'pill',
            'color': 'success',
            'posts_count': 76,
            'members_count': 32,
            'last_activity': {
                'user': 'Apotheker Jan',
                'topic': 'Medicatie interacties',
                'time': '6 uur geleden'
            }
        },
        {
            'id': 4,
            'name': '🩺 Huisartsgeneeskunde',
            'description': 'Huisartspraktijk en patiëntenzorg',
            'icon': 'stethoscope',
            'color': 'warning',
            'posts_count': 134,
            'members_count': 67,
            'last_activity': {
                'user': 'Dr. Jansen',
                'topic': 'Diabetes management',
                'time': '1 uur geleden'
            }
        },
        {
            'id': 5,
            'name': '👩‍⚕️ Verpleegkunde',
            'description': 'Verpleegkundige zorg en procedures',
            'icon': 'heart-pulse',
            'color': 'danger',
            'posts_count': 87,
            'members_count': 56,
            'last_activity': {
                'user': 'Verpleegkundige Lisa',
                'topic': 'Wondverzorging protocol',
                'time': '3 uur geleden'
            }
        },
        {
            'id': 6,
            'name': 'BIG Voorbereiding',
            'description': 'Voorbereiding op BIG examens - alle specialismen',
            'icon': 'graduation-cap',
            'color': 'secondary',
            'posts_count': 203,
            'members_count': 128,
            'last_activity': {
                'user': 'Student Marc',
                'topic': 'BIG examen tips',
                'time': '30 min geleden'
            }
        },
        {
            'id': 7,
            'name': 'Praktijkcases',
            'description': 'Bespreking van complexe patiëntcases',
            'icon': 'file-text',
            'color': 'dark',
            'posts_count': 156,
            'members_count': 78,
            'last_activity': {
                'user': 'Dr. Smit',
                'topic': 'Complexe orthodontische case',
                'time': '5 uur geleden'
            }
        },
        {
            'id': 8,
            'name': 'Vragen & Antwoorden',
            'description': 'Snel antwoord op specifieke vragen',
            'icon': 'help-circle',
            'color': 'info',
            'posts_count': 89,
            'members_count': 94,
            'last_activity': {
                'user': 'Student Emma',
                'topic': 'Vraag over farmacologie',
                'time': '15 min geleden'
            }
        },
        {
            'id': 9,
            'name': 'Netwerken & Events',
            'description': 'Evenementen, cursussen en netwerkmogelijkheden',
            'icon': 'calendar',
            'color': 'success',
            'posts_count': 45,
            'members_count': 156,
            'last_activity': {
                'user': 'Event Organisator',
                'topic': 'Webinar aankondiging',
                'time': '7 uur geleden'
            }
        }
    ]
    
    # Algemene community statistieken
    community_stats = {
        'total_members': 234,
        'online_members': 23,
        'total_posts': 1030,
        'total_topics': 287,
        'new_members_today': 5
    }
    
    # Recente activiteiten
    recent_activities = [
        {
            'user': 'Dr. van Berg',
            'action': 'plaatste een nieuw topic',
            'topic': 'Update Nederlandse richtlijnen 2024',
            'category': 'Algemene Discussies',
            'time': '2 uur geleden',
            'avatar': '👨‍⚕️'
        },
        {
            'user': 'Student Marc',
            'action': 'reageerde op',
            'topic': 'BIG examen ervaringen delen',
            'category': 'BIG Voorbereiding',
            'time': '30 min geleden',
            'avatar': '👨‍🎓'
        },
        {
            'user': 'Apotheker Jan',
            'action': 'startte discussie',
            'topic': 'Nieuwe medicatie richtlijnen',
            'category': 'Farmacie',
            'time': '6 uur geleden',
            'avatar': '💊'
        },
        {
            'user': 'Verpleegkundige Lisa',
            'action': 'deelde case',
            'topic': 'Complexe wondbehandeling',
            'category': 'Praktijkcases',
            'time': '3 uur geleden',
            'avatar': '👩‍⚕️'
        },
        {
            'user': 'Dr. Jansen',
            'action': 'beantwoordde vraag',
            'topic': 'Diabetes type 2 behandeling',
            'category': 'Vragen & Antwoorden',
            'time': '1 uur geleden',
            'avatar': '🩺'
        }
    ]
    
    return render_template(
        'community/index.html',
        title='Community & Forum',
        forum_categories=forum_categories,
        community_stats=community_stats,
        recent_activities=recent_activities,
        user=current_user
    ) 

@main_bp.route('/test')
def test_page():
    """Тестовая страница для отладки"""
    return render_template('test_login.html') 