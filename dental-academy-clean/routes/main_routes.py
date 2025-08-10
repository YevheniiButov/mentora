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
    return render_template('community/index.html', lang=lang)

@main_bp.route('/community/category/<category>')
@login_required
def community_category(lang, category):
    """Community category page"""
    # Данные для разных категорий
    categories_data = {
        'trending': {
            'title': 'Trending Discussions',
            'topics': [
                {
                    'id': 1,
                    'title': 'Complex Root Canal with Unusual Anatomy - Need Advice',
                    'author': 'Dr. Sarah Johnson',
                    'time': '2 hours ago',
                    'category': 'Endodontics',
                    'preview': 'Patient presents with a maxillary first molar with 4 canals and unusual MB2 anatomy...',
                    'replies': 12,
                    'views': 89,
                    'likes': 5,
                    'status': 'new'
                },
                {
                    'id': 2,
                    'title': 'Modern Implant Techniques - Best Practices Discussion',
                    'author': 'Dr. Emma Rodriguez',
                    'time': '3 hours ago',
                    'category': 'Expert Advice',
                    'preview': 'Let\'s discuss the latest advances in implant dentistry...',
                    'replies': 8,
                    'views': 67,
                    'likes': 3,
                    'status': 'normal'
                }
            ]
        },
        'clinical-cases': {
            'title': 'Clinical Cases',
            'topics': [
                {
                    'id': 3,
                    'title': 'Pediatric Dentistry - Behavior Management Techniques',
                    'author': 'Dr. Lisa Wang',
                    'time': '1 day ago',
                    'category': 'Clinical Cases',
                    'preview': 'Share your most effective behavior management techniques for pediatric patients...',
                    'replies': 22,
                    'views': 156,
                    'likes': 12,
                    'status': 'normal'
                },
                {
                    'id': 4,
                    'title': 'Emergency Case: Acute Dental Trauma',
                    'author': 'Dr. Robert Smith',
                    'time': '4 hours ago',
                    'category': 'Clinical Cases',
                    'preview': 'Patient with fractured anterior tooth after sports injury...',
                    'replies': 15,
                    'views': 98,
                    'likes': 7,
                    'status': 'new'
                }
            ]
        },
        'study-materials': {
            'title': 'Study Materials',
            'topics': [
                {
                    'id': 5,
                    'title': '📌 BIG Exam Study Guide - Periodontics Section',
                    'author': 'Dr. Michael Chen',
                    'time': '1 day ago',
                    'category': 'Study Materials',
                    'preview': 'Comprehensive study notes for the periodontics section of the BIG exam...',
                    'replies': 34,
                    'views': 234,
                    'likes': 18,
                    'status': 'pinned'
                },
                {
                    'id': 6,
                    'title': 'Anatomy Review: Cranial Nerves in Dentistry',
                    'author': 'Dr. Anna Kowalski',
                    'time': '2 days ago',
                    'category': 'Study Materials',
                    'preview': 'Detailed review of cranial nerves relevant to dental practice...',
                    'replies': 28,
                    'views': 189,
                    'likes': 14,
                    'status': 'normal'
                }
            ]
        },
        'expert-advice': {
            'title': 'Expert Advice',
            'topics': [
                {
                    'id': 7,
                    'title': 'Practice Management: Patient Communication Strategies',
                    'author': 'Dr. Jennifer Davis',
                    'time': '6 hours ago',
                    'category': 'Expert Advice',
                    'preview': 'What communication techniques do you find most effective...',
                    'replies': 19,
                    'views': 145,
                    'likes': 9,
                    'status': 'normal'
                }
            ]
        },
        'research': {
            'title': 'Research & Publications',
            'topics': [
                {
                    'id': 8,
                    'title': 'Latest Research on Bioactive Materials',
                    'author': 'Dr. Carlos Mendez',
                    'time': '1 day ago',
                    'category': 'Research',
                    'preview': 'Review of recent studies on bioactive materials in restorative dentistry...',
                    'replies': 11,
                    'views': 87,
                    'likes': 6,
                    'status': 'normal'
                }
            ]
        },
        'equipment': {
            'title': 'Equipment & Technology',
            'topics': [
                {
                    'id': 9,
                    'title': 'Digital Workflow Integration - Software Recommendations',
                    'author': 'Dr. Alex Kim',
                    'time': '5 hours ago',
                    'category': 'Equipment',
                    'preview': 'Looking to upgrade our digital workflow. What software solutions...',
                    'replies': 15,
                    'views': 112,
                    'likes': 3,
                    'status': 'normal'
                }
            ]
        }
    }
    
    category_data = categories_data.get(category, categories_data['trending'])
    return render_template('community/category.html', 
                         category=category,
                         category_data=category_data,
                         lang=lang)

@main_bp.route('/community/topic/<int:topic_id>')
@login_required
def community_topic(lang, topic_id):
    """Individual topic page"""
    # Данные для тем (в реальном приложении это было бы из базы данных)
    topics_data = {
        1: {
            'id': 1,
            'title': 'Complex Root Canal with Unusual Anatomy - Need Advice',
            'author': 'Dr. Sarah Johnson',
            'time': '2 hours ago',
            'category': 'Endodontics',
            'content': '''
            <p>Hello everyone,</p>
            <p>I have a challenging case that I'd like to discuss with the community. Patient presents with a maxillary first molar with 4 canals and unusual MB2 anatomy. The patient is experiencing severe pain and the tooth has been previously treated.</p>
            
            <h4>Case Details:</h4>
            <ul>
                <li>Patient: 45-year-old female</li>
                <li>Tooth: Maxillary first molar (#3)</li>
                <li>Previous treatment: Incomplete root canal 2 years ago</li>
                <li>Current symptoms: Severe pain, especially to percussion</li>
            </ul>
            
            <h4>Radiographic Findings:</h4>
            <p>CBCT shows unusual MB2 canal configuration with multiple accessory canals. The MB2 appears to have a complex branching pattern.</p>
            
            <p>Has anyone encountered similar cases? I'm looking for treatment approach recommendations and any tips for managing this type of anatomy.</p>
            
            <p>Thanks in advance for your insights!</p>
            ''',
            'replies': [
                {
                    'id': 1,
                    'author': 'Dr. Michael Chen',
                    'time': '1 hour ago',
                    'content': 'I had a similar case last month. The key is to use a surgical operating microscope and take your time with the MB2. I recommend using a small file (#08 or #10) initially to negotiate the canal.',
                    'likes': 8
                },
                {
                    'id': 2,
                    'author': 'Dr. Emma Rodriguez',
                    'time': '45 minutes ago',
                    'content': 'Agree with Dr. Chen. Also, consider using ultrasonic tips to remove any calcifications. The MB2 in these cases is often calcified and requires careful negotiation.',
                    'likes': 5
                },
                {
                    'id': 3,
                    'author': 'Dr. Lisa Wang',
                    'time': '30 minutes ago',
                    'content': 'I would also recommend taking multiple working length radiographs from different angles. The MB2 often has a curved path that can be missed on standard views.',
                    'likes': 3
                }
            ],
            'views': 89,
            'likes': 5
        },
        2: {
            'id': 2,
            'title': 'Modern Implant Techniques - Best Practices Discussion',
            'author': 'Dr. Emma Rodriguez',
            'time': '3 hours ago',
            'category': 'Expert Advice',
            'content': '''
            <p>Let's discuss the latest advances in implant dentistry. What techniques are you using? Any tips for improving success rates?</p>
            
            <p>I've been using guided surgery more frequently and have seen excellent results. The precision and predictability are remarkable.</p>
            
            <p>What are your thoughts on immediate loading protocols? I've had good success with single tooth implants, but I'm more conservative with full arch cases.</p>
            ''',
            'replies': [
                {
                    'id': 1,
                    'author': 'Dr. Alex Kim',
                    'time': '2 hours ago',
                    'content': 'I\'ve been using digital workflows for all my implant cases. The combination of CBCT, intraoral scanning, and guided surgery has significantly improved my outcomes.',
                    'likes': 6
                },
                {
                    'id': 2,
                    'author': 'Dr. Sarah Johnson',
                    'time': '1 hour ago',
                    'content': 'For immediate loading, I stick to single tooth implants in the anterior region with good primary stability. Full arch cases I still prefer delayed loading.',
                    'likes': 4
                }
            ],
            'views': 67,
            'likes': 3
        }
    }
    
    topic_data = topics_data.get(topic_id)
    if not topic_data:
        return redirect(url_for('main.community', lang=lang))
    
    return render_template('community/topic.html', 
                         topic=topic_data,
                         lang=lang)

@main_bp.route('/community/new-topic')
@login_required
def new_topic(lang):
    """Create new topic page"""
    return render_template('community/new_topic.html', lang=lang)

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
