#!/usr/bin/env python3
"""
Initialize BI-toets domains and sample questions
Based on ACTA 180 ECTS program structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Question, IRTParameters, QuestionCategory, TestAttempt, DiagnosticResponse
import json
import numpy as np
from datetime import datetime, timezone
from sqlalchemy import func
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for calibration sample size
def get_calibration_config():
    """Get calibration configuration from environment variables"""
    return {
        'min_sample_size': int(os.environ.get('IRT_MIN_SAMPLE_SIZE', 30)),
        'optimal_sample_size': int(os.environ.get('IRT_OPTIMAL_SAMPLE_SIZE', 100)),
        'max_sample_size': int(os.environ.get('IRT_MAX_SAMPLE_SIZE', 500)),
        'reliability_threshold': float(os.environ.get('IRT_RELIABILITY_THRESHOLD', 0.8)),
        'confidence_level': float(os.environ.get('IRT_CONFIDENCE_LEVEL', 0.95))
    }

def calculate_required_sample_size(confidence_level=0.95, margin_of_error=0.1, p=0.5):
    """
    Calculate required sample size for reliable IRT calibration
    
    Args:
        confidence_level: Confidence level (default 0.95 for 95%)
        margin_of_error: Acceptable margin of error (default 0.1 for 10%)
        p: Expected proportion of correct answers (default 0.5 for maximum variance)
    
    Returns:
        Required sample size
    """
    from scipy import stats
    
    # Z-score for confidence level
    z_alpha = stats.norm.ppf((1 + confidence_level) / 2)
    
    # Sample size formula for proportion
    n = (z_alpha ** 2 * p * (1 - p)) / (margin_of_error ** 2)
    
    return int(np.ceil(n))

def analyze_existing_responses():
    """
    Analyze existing response data to determine calibration parameters
    
    Returns:
        Dict with analysis results
    """
    try:
        # Get total responses
        total_test_attempts = TestAttempt.query.count()
        total_diagnostic_responses = DiagnosticResponse.query.count()
        total_responses = total_test_attempts + total_diagnostic_responses
        
        # Get responses per question
        responses_per_question = db.session.query(
            Question.id,
            func.count(TestAttempt.id).label('test_responses'),
            func.count(DiagnosticResponse.id).label('diag_responses')
        ).outerjoin(TestAttempt).outerjoin(DiagnosticResponse).group_by(Question.id).all()
        
        # Calculate statistics
        response_counts = []
        for _, test_count, diag_count in responses_per_question:
            total = (test_count or 0) + (diag_count or 0)
            if total > 0:
                response_counts.append(total)
        
        if not response_counts:
            return {
                'total_responses': 0,
                'questions_with_responses': 0,
                'avg_responses_per_question': 0,
                'median_responses_per_question': 0,
                'max_responses_per_question': 0,
                'min_responses_per_question': 0,
                'recommended_sample_size': 30
            }
        
        return {
            'total_responses': total_responses,
            'questions_with_responses': len(response_counts),
            'avg_responses_per_question': np.mean(response_counts),
            'median_responses_per_question': np.median(response_counts),
            'max_responses_per_question': max(response_counts),
            'min_responses_per_question': min(response_counts),
            'recommended_sample_size': calculate_required_sample_size()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing existing responses: {e}")
        return {
            'total_responses': 0,
            'questions_with_responses': 0,
            'avg_responses_per_question': 0,
            'median_responses_per_question': 0,
            'max_responses_per_question': 0,
            'min_responses_per_question': 0,
            'recommended_sample_size': 30
        }

def validate_sample_size(sample_size, config):
    """
    Validate if sample size is sufficient for reliable calibration
    
    Args:
        sample_size: Actual sample size
        config: Calibration configuration
    
    Returns:
        Dict with validation results
    """
    if sample_size < config['min_sample_size']:
        return {
            'is_sufficient': False,
            'warning': f"Sample size {sample_size} is below minimum ({config['min_sample_size']})",
            'reliability': 'low',
            'confidence': 'low'
        }
    elif sample_size < config['optimal_sample_size']:
        return {
            'is_sufficient': True,
            'warning': f"Sample size {sample_size} is below optimal ({config['optimal_sample_size']})",
            'reliability': 'medium',
            'confidence': 'medium'
        }
    else:
        return {
            'is_sufficient': True,
            'warning': None,
            'reliability': 'high',
            'confidence': 'high'
        }

def get_calibration_sample_size(question_id=None):
    """
    Get calibration sample size based on existing data and configuration
    
    Args:
        question_id: Optional question ID to get specific sample size
    
    Returns:
        Calibration sample size and validation info
    """
    config = get_calibration_config()
    
    if question_id:
        # Get actual response count for specific question
        test_count = TestAttempt.query.filter_by(question_id=question_id).count()
        diag_count = DiagnosticResponse.query.filter_by(question_id=question_id).count()
        actual_sample_size = test_count + diag_count
        
        validation = validate_sample_size(actual_sample_size, config)
        
        return {
            'sample_size': actual_sample_size,
            'validation': validation,
            'source': 'actual_responses'
        }
    else:
        # Use recommended sample size based on analysis
        analysis = analyze_existing_responses()
        recommended_size = analysis['recommended_sample_size']
        
        # Adjust based on configuration
        if recommended_size < config['min_sample_size']:
            sample_size = config['min_sample_size']
        elif recommended_size > config['max_sample_size']:
            sample_size = config['max_sample_size']
        else:
            sample_size = recommended_size
        
        validation = validate_sample_size(sample_size, config)
        
        return {
            'sample_size': sample_size,
            'validation': validation,
            'source': 'recommended',
            'analysis': analysis
        }

def log_calibration_info(question_id, sample_size_info):
    """Log calibration information"""
    sample_size = sample_size_info['sample_size']
    validation = sample_size_info['validation']
    source = sample_size_info.get('source', 'unknown')
    
    if validation['warning']:
        logger.warning(f"Question {question_id}: {validation['warning']} (reliability: {validation['reliability']})")
    else:
        logger.info(f"Question {question_id}: Sample size {sample_size} is sufficient (reliability: {validation['reliability']})")
    
    return sample_size

def create_big_domains():
    """Create BI-toets domains based on ACTA program"""
    
    domains_data = [
        {
            'name': 'Терапевтическая стоматология',
            'code': 'THER',
            'description': 'Лечение кариеса, эндодонтия, реставрационная стоматология',
            'weight_percentage': 25.0,
            'order': 1
        },
        {
            'name': 'Хирургическая стоматология',
            'code': 'SURG',
            'description': 'Удаление зубов, имплантология, челюстно-лицевая хирургия',
            'weight_percentage': 20.0,
            'order': 2
        },
        {
            'name': 'Ортопедическая стоматология',
            'code': 'PROST',
            'description': 'Протезирование, коронки, мосты, съемные протезы',
            'weight_percentage': 15.0,
            'order': 3
        },
        {
            'name': 'Детская стоматология',
            'code': 'PEDO',
            'description': 'Стоматология для детей, профилактика, лечение молочных зубов',
            'weight_percentage': 10.0,
            'order': 4
        },
        {
            'name': 'Пародонтология',
            'code': 'PERIO',
            'description': 'Заболевания десен, пародонтит, гигиена полости рта',
            'weight_percentage': 10.0,
            'order': 5
        },
        {
            'name': 'Ортодонтия',
            'code': 'ORTHO',
            'description': 'Исправление прикуса, брекеты, выравнивание зубов',
            'weight_percentage': 8.0,
            'order': 6
        },
        {
            'name': 'Профилактика',
            'code': 'PREV',
            'description': 'Профилактическая стоматология, гигиена, образование пациентов',
            'weight_percentage': 7.0,
            'order': 7
        },
        {
            'name': 'Этика и право Нидерландов',
            'code': 'ETHICS',
            'description': 'Медицинская этика, законодательство, профессиональные стандарты',
            'weight_percentage': 5.0,
            'order': 8
        }
    ]
    
    created_domains = []
    
    for domain_data in domains_data:
        # Check if domain already exists
        existing = BIGDomain.query.filter_by(code=domain_data['code']).first()
        if existing:
            print(f"Domain {domain_data['code']} already exists, skipping...")
            created_domains.append(existing)
            continue
        
        domain = BIGDomain(**domain_data)
        db.session.add(domain)
        created_domains.append(domain)
        print(f"Created domain: {domain_data['name']} ({domain_data['code']})")
    
    db.session.commit()
    print(f"✅ Created {len(created_domains)} BI-toets domains")
    return created_domains

def create_big_domains_category():
    """Создать категорию 'BI-toets' для всех диагностических вопросов"""
    category = QuestionCategory.query.filter_by(name='BI-toets').first()
    if not category:
        category = QuestionCategory(name='BI-toets')
        db.session.add(category)
        db.session.commit()
        print("Создана категория 'BI-toets'")
    else:
        print("Категория 'BI-toets' уже существует")
    return category

def create_sample_questions():
    """Create sample questions for each domain with IRT parameters"""
    
    # Получить/создать категорию BI-toets
    bi_category = create_big_domains_category()
    
    sample_questions = [
        # Терапевтическая стоматология
        {
            'domain_code': 'THER',
            'text': 'Какой материал является наиболее подходящим для временного пломбирования кариозной полости?',
            'options': ['Амальгама', 'Композит', 'Цинк-оксид эвгенол', 'Стеклоиономер'],
            'correct_answer': 'Цинк-оксид эвгенол',
            'explanation': 'Цинк-оксид эвгенол является идеальным материалом для временного пломбирования благодаря своим антибактериальным свойствам и способности успокаивать пульпу.',
            'difficulty': -0.5,
            'discrimination': 1.2,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        {
            'domain_code': 'THER',
            'text': 'При каком диагнозе показано эндодонтическое лечение?',
            'options': ['Поверхностный кариес', 'Средний кариес', 'Глубокий кариес с пульпитом', 'Гингивит'],
            'correct_answer': 'Глубокий кариес с пульпитом',
            'explanation': 'Эндодонтическое лечение показано при воспалении пульпы (пульпит) или некрозе пульпы.',
            'difficulty': 0.2,
            'discrimination': 1.5,
            'guessing': 0.25,
            'difficulty_level': 3
        },
        
        # Хирургическая стоматология
        {
            'domain_code': 'SURG',
            'text': 'Какое осложнение наиболее часто встречается после удаления третьего моляра?',
            'options': ['Остеомиелит', 'Сухая лунка', 'Повреждение лицевого нерва', 'Кровотечение'],
            'correct_answer': 'Сухая лунка',
            'explanation': 'Сухая лунка (альвеолит) является наиболее частым осложнением после удаления третьих моляров, возникающим в 2-5% случаев.',
            'difficulty': 0.8,
            'discrimination': 1.3,
            'guessing': 0.25,
            'difficulty_level': 4
        },
        {
            'domain_code': 'SURG',
            'text': 'Какой тип анестезии используется для удаления верхнего клыка?',
            'options': ['Инфильтрационная', 'Проводниковая', 'Общая анестезия', 'Седация'],
            'correct_answer': 'Инфильтрационная',
            'explanation': 'Для удаления верхних зубов обычно используется инфильтрационная анестезия, так как кость верхней челюсти более пористая.',
            'difficulty': -0.3,
            'discrimination': 1.1,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        
        # Ортопедическая стоматология
        {
            'domain_code': 'PROST',
            'text': 'Какой тип протеза показан при отсутствии всех зубов на верхней челюсти?',
            'options': ['Частичный съемный протез', 'Полный съемный протез', 'Мостовидный протез', 'Имплант'],
            'correct_answer': 'Полный съемный протез',
            'explanation': 'При полном отсутствии зубов на одной челюсти показан полный съемный протез.',
            'difficulty': -0.8,
            'discrimination': 1.0,
            'guessing': 0.25,
            'difficulty_level': 1
        },
        {
            'domain_code': 'PROST',
            'text': 'Какой материал является наиболее биосовместимым для изготовления коронок?',
            'options': ['Металлокерамика', 'Цельнокерамика', 'Металлические сплавы', 'Пластмасса'],
            'correct_answer': 'Цельнокерамика',
            'explanation': 'Цельнокерамические коронки обладают наилучшей биосовместимостью и эстетическими свойствами.',
            'difficulty': 0.5,
            'discrimination': 1.4,
            'guessing': 0.25,
            'difficulty_level': 3
        },
        
        # Детская стоматология
        {
            'domain_code': 'PEDO',
            'text': 'В каком возрасте обычно прорезывается первый постоянный моляр?',
            'options': ['5-6 лет', '6-7 лет', '7-8 лет', '8-9 лет'],
            'correct_answer': '6-7 лет',
            'explanation': 'Первый постоянный моляр (шестой зуб) обычно прорезывается в возрасте 6-7 лет.',
            'difficulty': 0.0,
            'discrimination': 1.2,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        {
            'domain_code': 'PEDO',
            'text': 'Какой метод лечения кариеса молочных зубов является наименее инвазивным?',
            'options': ['Препарирование и пломбирование', 'Серебрение', 'Фторирование', 'Удаление'],
            'correct_answer': 'Фторирование',
            'explanation': 'Фторирование является наименее инвазивным методом лечения начального кариеса молочных зубов.',
            'difficulty': -0.2,
            'discrimination': 1.3,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        
        # Пародонтология
        {
            'domain_code': 'PERIO',
            'text': 'Какой показатель является основным для диагностики пародонтита?',
            'options': ['Глубина карманов', 'Кровоточивость десен', 'Подвижность зубов', 'Все перечисленное'],
            'correct_answer': 'Все перечисленное',
            'explanation': 'Для диагностики пародонтита необходимо учитывать все перечисленные показатели.',
            'difficulty': 0.3,
            'discrimination': 1.1,
            'guessing': 0.25,
            'difficulty_level': 3
        },
        {
            'domain_code': 'PERIO',
            'text': 'Какой тип зубной щетки рекомендуется пациентам с пародонтитом?',
            'options': ['Жесткая', 'Средней жесткости', 'Мягкая', 'Электрическая'],
            'correct_answer': 'Мягкая',
            'explanation': 'При пародонтите рекомендуется использовать мягкую зубную щетку для предотвращения травмирования десен.',
            'difficulty': -0.1,
            'discrimination': 1.0,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        
        # Ортодонтия
        {
            'domain_code': 'ORTHO',
            'text': 'Какой тип прикуса является физиологическим?',
            'options': ['Открытый прикус', 'Глубокий прикус', 'Ножницеобразный прикус', 'Ортогнатический прикус'],
            'correct_answer': 'Ортогнатический прикус',
            'explanation': 'Ортогнатический прикус является физиологическим и обеспечивает оптимальную функцию жевания.',
            'difficulty': 0.1,
            'discrimination': 1.2,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        {
            'domain_code': 'ORTHO',
            'text': 'В каком возрасте оптимально начинать ортодонтическое лечение?',
            'options': ['5-7 лет', '7-9 лет', '9-12 лет', 'После 18 лет'],
            'correct_answer': '9-12 лет',
            'explanation': 'Оптимальный возраст для начала ортодонтического лечения - 9-12 лет, когда происходит активный рост челюстей.',
            'difficulty': 0.6,
            'discrimination': 1.4,
            'guessing': 0.25,
            'difficulty_level': 3
        },
        
        # Профилактика
        {
            'domain_code': 'PREV',
            'text': 'Как часто рекомендуется проводить профессиональную гигиену полости рта?',
            'options': ['Раз в месяц', 'Раз в 3 месяца', 'Раз в 6 месяцев', 'Раз в год'],
            'correct_answer': 'Раз в 6 месяцев',
            'explanation': 'Профессиональная гигиена полости рта рекомендуется каждые 6 месяцев для большинства пациентов.',
            'difficulty': -0.4,
            'discrimination': 1.1,
            'guessing': 0.25,
            'difficulty_level': 1
        },
        {
            'domain_code': 'PREV',
            'text': 'Какой метод профилактики кариеса является наиболее эффективным?',
            'options': ['Фторирование', 'Герметизация фиссур', 'Правильная гигиена', 'Все перечисленное'],
            'correct_answer': 'Все перечисленное',
            'explanation': 'Наиболее эффективной является комплексная профилактика, включающая все перечисленные методы.',
            'difficulty': 0.2,
            'discrimination': 1.3,
            'guessing': 0.25,
            'difficulty_level': 2
        },
        
        # Этика и право
        {
            'domain_code': 'ETHICS',
            'text': 'Какой принцип медицинской этики является основным в стоматологии?',
            'options': ['Не навреди', 'Делай добро', 'Автономия пациента', 'Справедливость'],
            'correct_answer': 'Не навреди',
            'explanation': 'Принцип "Не навреди" (Primum non nocere) является основным принципом медицинской этики.',
            'difficulty': 0.4,
            'discrimination': 1.2,
            'guessing': 0.25,
            'difficulty_level': 3
        },
        {
            'domain_code': 'ETHICS',
            'text': 'Обязан ли стоматолог сообщать о подозрении на жестокое обращение с ребенком?',
            'options': ['Нет, это нарушает конфиденциальность', 'Да, это обязательная отчетность', 'Только с согласия родителей', 'Только в крайних случаях'],
            'correct_answer': 'Да, это обязательная отчетность',
            'explanation': 'В Нидерландах стоматологи обязаны сообщать о подозрении на жестокое обращение с детьми.',
            'difficulty': 0.7,
            'discrimination': 1.5,
            'guessing': 0.25,
            'difficulty_level': 4
        }
    ]
    
    created_questions = []
    
    for q_data in sample_questions:
        # Get domain
        domain = BIGDomain.query.filter_by(code=q_data['domain_code']).first()
        if not domain:
            print(f"Domain {q_data['domain_code']} not found, skipping question...")
            continue
        
        # Check if question already exists
        existing = Question.query.filter_by(text=q_data['text']).first()
        if existing:
            print(f"Question already exists, skipping...")
            continue
        
        # Create question
        question = Question(
            text=q_data['text'],
            options=json.dumps(q_data['options']),
            correct_answer=q_data['correct_answer'],
            explanation=q_data['explanation'],
            big_domain_id=domain.id,
            difficulty_level=q_data['difficulty_level'],
            question_type='multiple_choice',
            category_id=bi_category.id
        )
        
        db.session.add(question)
        db.session.flush()  # Get question ID
        
        # Create IRT parameters
        sample_size_info = get_calibration_sample_size(question.id)
        calibration_sample_size = log_calibration_info(question.id, sample_size_info)
        
        irt_params = IRTParameters(
            question_id=question.id,
            difficulty=q_data['difficulty'],
            discrimination=q_data['discrimination'],
            guessing=q_data['guessing'],
            calibration_date=datetime.now(timezone.utc),
            calibration_sample_size=calibration_sample_size
        )
        
        db.session.add(irt_params)
        created_questions.append(question)
        print(f"Created question: {q_data['text'][:50]}...")
    
    db.session.commit()
    print(f"✅ Created {len(created_questions)} sample questions with IRT parameters")
    return created_questions

def main():
    """Main function to initialize BI-toets data"""
    with app.app_context():
        print("🦷 Initializing BI-toets diagnostic testing system...")
        
        # Analyze existing response data
        print("\n📊 Analyzing existing response data...")
        analysis = analyze_existing_responses()
        config = get_calibration_config()
        
        print(f"   - Total responses: {analysis['total_responses']}")
        print(f"   - Questions with responses: {analysis['questions_with_responses']}")
        print(f"   - Average responses per question: {analysis['avg_responses_per_question']:.1f}")
        print(f"   - Recommended sample size: {analysis['recommended_sample_size']}")
        print(f"   - Configuration: min={config['min_sample_size']}, optimal={config['optimal_sample_size']}, max={config['max_sample_size']}")
        
        # Create domains
        print("\n📚 Creating BI-toets domains...")
        domains = create_big_domains()
        
        # Create sample questions
        print("\n❓ Creating sample questions...")
        questions = create_sample_questions()
        
        print(f"\n🎉 Initialization complete!")
        print(f"   - Domains: {len(domains)}")
        print(f"   - Questions: {len(questions)}")
        print(f"   - IRT parameters: {len(questions)}")
        
        # Print domain summary
        print("\n📊 Domain Summary:")
        for domain in domains:
            question_count = Question.query.filter_by(big_domain_id=domain.id).count()
            print(f"   {domain.code}: {domain.name} ({question_count} questions, {domain.weight_percentage}%)")
        
        # Print calibration summary
        print("\n🔬 Calibration Summary:")
        print(f"   - IRT parameters created with real sample size calculation")
        print(f"   - Sample size validation enabled")
        print(f"   - Configuration via environment variables:")
        print(f"     IRT_MIN_SAMPLE_SIZE={config['min_sample_size']}")
        print(f"     IRT_OPTIMAL_SAMPLE_SIZE={config['optimal_sample_size']}")
        print(f"     IRT_MAX_SAMPLE_SIZE={config['max_sample_size']}")
        print(f"     IRT_RELIABILITY_THRESHOLD={config['reliability_threshold']}")
        print(f"     IRT_CONFIDENCE_LEVEL={config['confidence_level']}")

if __name__ == '__main__':
    main() 