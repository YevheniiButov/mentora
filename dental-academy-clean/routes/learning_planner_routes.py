from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from models import DiagnosticSession, PersonalLearningPlan
from utils.serializers import clean_for_template
from translations import get_translation

learning_planner_bp = Blueprint('learning_planner', __name__)

@learning_planner_bp.route('/learning-planner/<int:plan_id>')
@login_required
def learning_planner(plan_id):
    """Enhanced learning planner with calendar and charts"""
    
    print(f"🔍 ОТЛАДКА: learning_planner вызван")
    print(f"🔍 ОТЛАДКА: current_user.id = {current_user.id}")
    
    # Get current language
    lang = request.args.get('lang', 'en')
    
    # Get user's diagnostic results
    latest_diagnostic = DiagnosticSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(DiagnosticSession.completed_at.desc()).first()
    
    print(f"🔍 ОТЛАДКА: latest_diagnostic = {latest_diagnostic}")
    print(f"🔍 ОТЛАДКА: latest_diagnostic.id = {latest_diagnostic.id if latest_diagnostic else 'None'}")
    
    # Get user's learning plan
    learning_plan = PersonalLearningPlan.query.filter_by(id=plan_id, 
        user_id=current_user.id,
        status='active'
    ).order_by(PersonalLearningPlan.last_updated.desc()).first()
    
    print(f"🔍 ОТЛАДКА: learning_plan = {learning_plan}")
    print(f"🔍 ОТЛАДКА: learning_plan.id = {learning_plan.id if learning_plan else 'None'}")
    print(f"🔍 ОТЛАДКА: learning_plan.domain_analysis = {learning_plan.domain_analysis if learning_plan else 'None'}")
    
    # ВСЕ 25 доменов BIG экзамена
    ALL_BIG_DOMAINS = {
        'domain_1': 'Endodontics',
        'domain_2': 'Periodontics', 
        'domain_3': 'Orthodontics',
        'domain_4': 'Oral Surgery',
        'domain_5': 'Prosthodontics',
        'domain_6': 'Preventive Care',
        'domain_7': 'Dental Materials',
        'domain_8': 'Oral Pathology',
        'domain_9': 'Oral Medicine',
        'domain_10': 'Dental Radiology',
        'domain_11': 'Dental Anatomy',
        'domain_12': 'Dental Physiology',
        'domain_13': 'Dental Pharmacology',
        'domain_14': 'Dental Anesthesia',
        'domain_15': 'Dental Emergency',
        'domain_16': 'Dental Ethics',
        'domain_17': 'Dental Law',
        'domain_18': 'Practice Management',
        'domain_19': 'Patient Communication',
        'domain_20': 'Infection Control',
        'domain_21': 'Dental Implants',
        'domain_22': 'Cosmetic Dentistry',
        'domain_23': 'Pediatric Dentistry',
        'domain_24': 'Geriatric Dentistry',
        'domain_25': 'Special Needs Dentistry'
    }
    
    # Маппинг старых доменов на новые
    OLD_TO_NEW_DOMAIN_MAPPING = {
        'THER': 'domain_1',      # Терапевтическая стоматология -> Endodontics
        'SURG': 'domain_4',      # Хирургическая стоматология -> Oral Surgery
        'PROTH': 'domain_5',     # Ортопедическая стоматология -> Prosthodontics
        'PEDI': 'domain_23',     # Детская стоматология -> Pediatric Dentistry
        'PARO': 'domain_2',      # Пародонтология -> Periodontics
        'ORTHO': 'domain_3',     # Ортодонтия -> Orthodontics
        'PREV': 'domain_6',      # Профилактика -> Preventive Care
        'ETHIEK': 'domain_16',   # Этика и право -> Dental Ethics
        'ANATOMIE': 'domain_11', # Анатомия -> Dental Anatomy
        'FYSIOLOGIE': 'domain_12', # Физиология -> Dental Physiology
        'PATHOLOGIE': 'domain_8', # Патология -> Oral Pathology
        'MICROBIOLOGIE': 'domain_20', # Микробиология -> Infection Control
        'MATERIAALKUNDE': 'domain_7', # Материаловедение -> Dental Materials
        'RADIOLOGIE': 'domain_10', # Рентгенология -> Dental Radiology
        'ALGEMENE_GENEESKUNDE': 'domain_9', # Общая медицина -> Oral Medicine
        'EMERGENCY': 'domain_15', # Неотложная помощь -> Dental Emergency
        'SYSTEMIC': 'domain_9',  # Системные заболевания -> Oral Medicine
        'PHARMA': 'domain_13',   # Фармакология -> Dental Pharmacology
        'INFECTION': 'domain_20', # Инфекционный контроль -> Infection Control
        'SPECIAL': 'domain_25',  # Специальные группы пациентов -> Special Needs Dentistry
        'DIAGNOSIS': 'domain_8', # Сложная диагностика -> Oral Pathology
        'DUTCH': 'domain_18',    # Голландская система здравоохранения -> Practice Management
        'PROFESSIONAL': 'domain_17', # Профессиональное развитие -> Dental Law
        'FARMACOLOGIE': 'domain_13', # Фармакология (альтернативное название) -> Dental Pharmacology
        'DIAGNOSIS_SPECIAL': 'domain_8' # Специальная диагностика -> Oral Pathology
    }
    
    # Prepare diagnostic results for frontend
    diagnostic_results = {
        'overall_score': latest_diagnostic.current_ability if latest_diagnostic else 0,
        'domains': []
    }
    
    # Получаем данные диагностики
    diagnostic_data = {}
    if latest_diagnostic:
        diagnostic_data = latest_diagnostic.generate_results()
        print(f"🔍 ОТЛАДКА: diagnostic_data = {diagnostic_data}")
    
    # Показываем ВСЕ 25 доменов
    print(f"🔍 ОТЛАДКА: Показываем ВСЕ 25 доменов...")
    for domain_code, domain_name in ALL_BIG_DOMAINS.items():
        print(f"🔍 ОТЛАДКА: Обрабатываем домен {domain_code} = {domain_name}")
        
        # Проверяем есть ли данные по этому домену (прямое совпадение)
        if (diagnostic_data.get('domain_statistics') and 
            domain_code in diagnostic_data['domain_statistics'] and
            diagnostic_data['domain_statistics'][domain_code].get('has_data', False)):
            
            # Есть прямые данные
            domain_data = diagnostic_data['domain_statistics'][domain_code]
            score = domain_data.get('accuracy_percentage', 0)
            questions_answered = domain_data.get('questions_answered', 0)
            correct_answers = domain_data.get('correct_answers', 0)
            print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет прямые данные: {score}%")
        else:
            # Проверяем маппинг старых доменов
            score = 0
            questions_answered = 0
            correct_answers = 0
            
            # Ищем старый домен, который маппится на этот новый
            for old_domain, new_domain in OLD_TO_NEW_DOMAIN_MAPPING.items():
                if new_domain == domain_code:
                    if (diagnostic_data.get('domain_statistics') and 
                        old_domain in diagnostic_data['domain_statistics'] and
                        diagnostic_data['domain_statistics'][old_domain].get('has_data', False)):
                        
                        # Нашли данные в старом домене
                        old_domain_data = diagnostic_data['domain_statistics'][old_domain]
                        score = old_domain_data.get('accuracy_percentage', 0)
                        questions_answered = old_domain_data.get('questions_answered', 0)
                        correct_answers = old_domain_data.get('correct_answers', 0)
                        print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет данные из старого домена {old_domain}: {score}%")
                        break
            
            if score == 0:
                print(f"🔍 ОТЛАДКА: Домен {domain_name} без данных: 0%")
        
        # Переводим название домена
        translated_name = get_translation(domain_code, lang)
        if translated_name == domain_code:
            translated_name = domain_name
        
        domain_result = {
            'code': domain_code,
            'name': translated_name,
            'score': score,
            'target': 85,
            'hours': max(24 - score * 0.3, 8),  # Расчет часов
            'questions_answered': questions_answered,
            'correct_answers': correct_answers
        }
        
        print(f"🔍 ОТЛАДКА: domain_result = {domain_result}")
        diagnostic_results['domains'].append(domain_result)
    
    print(f"🔍 ОТЛАДКА: diagnostic_results = {diagnostic_results}")
    print(f"🔍 ОТЛАДКА: Всего доменов = {len(diagnostic_results['domains'])}")
    
    # Prepare learning plan data
    learning_plan_data = {}
    if learning_plan:
        learning_plan_data = {
            'exam_date': learning_plan.exam_date.isoformat() if learning_plan.exam_date else None,
            'start_date': learning_plan.start_date.isoformat() if learning_plan.start_date else None,
            'end_date': learning_plan.end_date.isoformat() if learning_plan.end_date else None,
            'intensity': learning_plan.intensity,
            'study_time': learning_plan.study_time,
            'current_ability': round(learning_plan.current_ability, 1) if learning_plan.current_ability else 0,
            'overall_progress': round(learning_plan.overall_progress, 1) if learning_plan.overall_progress else 0,
            'estimated_readiness': round(learning_plan.estimated_readiness, 1) if learning_plan.estimated_readiness else 0
        }
    
    print(f"🔍 ОТЛАДКА: learning_plan_data = {learning_plan_data}")
    
    response = make_response(render_template('dashboard/learning_planner_translated.html',
                         diagnostic_results=clean_for_template(diagnostic_results),
                         learning_plan_data=clean_for_template(learning_plan_data)))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response 