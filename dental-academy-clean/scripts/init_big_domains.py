#!/usr/bin/env python3
"""
Initialize BI-toets domains and sample questions
Based on ACTA 180 ECTS program structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Question, IRTParameters, QuestionCategory
import json
from datetime import datetime, timezone

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
        irt_params = IRTParameters(
            question_id=question.id,
            difficulty=q_data['difficulty'],
            discrimination=q_data['discrimination'],
            guessing=q_data['guessing'],
            calibration_date=datetime.now(timezone.utc),
            calibration_sample_size=100  # Placeholder
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

if __name__ == '__main__':
    main() 