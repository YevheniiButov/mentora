import json
import click
from flask.cli import with_appcontext
from extensions import db
from models import Question, BIGDomain

def get_big_domain_id_by_code(domain_code):
    """Map domain codes to BIGDomain IDs"""
    domain_mapping = {
        'THER': 'Therapeutische stomatologie',
        'SURG': 'Chirurgische stomatologie', 
        'PROTH': 'Prothetische stomatologie',
        'PEDI': 'Pediatrische stomatologie',
        'PARO': 'Parodontologie',
        'ORTHO': 'Orthodontie',
        'PREV': 'Preventie',
        'ETHIEK': 'Ethiek en recht',
        'ANATOMIE': 'Anatomie',
        'FYSIOLOGIE': 'Fysiologie',
        'PATHOLOGIE': 'Pathologie',
        'MICROBIOLOGIE': 'Microbiologie',
        'MATERIAALKUNDE': 'Materiaalkunde',
        'RADIOLOGIE': 'Radiologie',
        'ALGEMENE_GENEESKUNDE': 'Algemene geneeskunde'
    }
    
    domain_name = domain_mapping.get(domain_code)
    if domain_name:
        domain = BIGDomain.query.filter_by(name=domain_name).first()
        return domain.id if domain else None
    return None

@click.command()
@click.argument('json_file')
@with_appcontext
def import_questions(json_file):
    """Import questions from JSON file - supports 160 questions with extended domains"""
    print(f"🔄 Importing questions from {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        print(f"📊 Found {len(questions_data)} questions to import")
        
        imported_count = 0
        skipped_count = 0
        
        for q_data in questions_data:
            try:
                # Проверка обязательных полей (поддерживаем оба формата IRT)
                required_fields = ['text', 'options', 'correct_answer_text', 'domain']
                missing_fields = [field for field in required_fields if field not in q_data]
                
                # Проверяем наличие IRT параметров в любом формате
                if 'irt_parameters' not in q_data and 'irt_params' not in q_data:
                    missing_fields.append('irt_parameters or irt_params')
                
                if missing_fields:
                    print(f"⚠️ Skipping question {q_data.get('id', 'unknown')}: missing {missing_fields}")
                    skipped_count += 1
                    continue
                
                # Проверка корректности correct_answer_text
                if q_data['correct_answer_text'] not in q_data['options']:
                    print(f"⚠️ Skipping question {q_data.get('id', 'unknown')}: correct answer not in options")
                    skipped_count += 1
                    continue
                
                # Получение big_domain_id
                big_domain_id = q_data.get('big_domain_id') or get_big_domain_id_by_code(q_data['domain'])
                
                # Создание вопроса
                question = Question(
                    text=q_data['text'],
                    options=q_data['options'],
                    correct_answer_index=q_data['options'].index(q_data['correct_answer_text']),
                    correct_answer_text=q_data['correct_answer_text'],
                    explanation=q_data['explanation'],
                    category=q_data.get('category', ''),
                    domain=q_data['domain'],
                    difficulty_level=q_data.get('difficulty_level', 2),
                    image_url=q_data.get('image_url'),
                    tags=q_data.get('tags', []),
                    # Новые поля с дефолтами
                    question_type=q_data.get('question_type', 'multiple_choice'),
                    clinical_context=q_data.get('clinical_context'),
                    learning_objectives=q_data.get('learning_objectives'),
                    big_domain_id=big_domain_id
                )
                
                # Добавляем вопрос в сессию
                db.session.add(question)
                db.session.flush()  # Получаем ID вопроса
                
                # Создаем IRT параметры (поддерживаем оба формата)
                from models import IRTParameters
                irt_data = q_data.get('irt_parameters') or q_data.get('irt_params')
                if not irt_data:
                    print(f"⚠️ Skipping question {q_data.get('id', 'unknown')}: no IRT parameters found")
                    skipped_count += 1
                    continue
                    
                irt_params = IRTParameters(
                    question_id=question.id,
                    difficulty=irt_data['difficulty'],
                    discrimination=irt_data['discrimination'],
                    guessing=irt_data['guessing']
                )
                
                # Валидация IRT параметров
                try:
                    irt_params.validate_parameters()
                except ValueError as e:
                    print(f"⚠️ Skipping question {q_data.get('id', 'unknown')}: IRT validation failed - {e}")
                    db.session.rollback()
                    skipped_count += 1
                    continue
                
                db.session.add(irt_params)
                imported_count += 1
                
                if imported_count % 10 == 0:
                    print(f"📝 Imported {imported_count} questions...")
                    
            except Exception as e:
                print(f"❌ Error importing question {q_data.get('id', 'unknown')}: {str(e)}")
                skipped_count += 1
                continue
        
        db.session.commit()
        print(f"✅ Successfully imported {imported_count} questions")
        if skipped_count > 0:
            print(f"⚠️ Skipped {skipped_count} questions due to errors")
            
        # Показать статистику по доменам
        print("\n📊 DOMAIN STATISTICS:")
        domains = db.session.query(Question.domain, db.func.count(Question.id)).group_by(Question.domain).all()
        for domain, count in domains:
            print(f"   {domain}: {count} questions")
            
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {str(e)}")
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    import_questions() 