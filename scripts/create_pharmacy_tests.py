from models import db, QuestionCategory, Question, Test, Subject, LearningPath
import json

def create_pharmacy_learning_path():
    """Создает путь обучения для фармацевтов если он не существует"""
    path = LearningPath.query.filter_by(name='Farmacie').first()
    if not path:
        path = LearningPath(
            name='Farmacie',
            description='Voorbereidingscursus voor BIG-registratie als apotheker',
            order=1,
            icon='capsule',
            exam_phase=1,
            is_active=True
        )
        db.session.add(path)
        db.session.commit()
    return path

def create_pharmacy_subject():
    """Создает предмет фармацевтики если он не существует"""
    path = create_pharmacy_learning_path()
    
    subject = Subject.query.filter_by(id=101).first()
    if not subject:
        subject = Subject(
            id=101,
            name='Farmacie',
            description='Voorbereidingscursus voor BIG-registratie als apotheker',
            order=1,
            icon='capsule',
            learning_path_id=path.id
        )
        db.session.add(subject)
        db.session.commit()
    return subject

def create_pharmacy_test_categories():
    """Создает категории тестов для фармацевтов"""
    subject = create_pharmacy_subject()
    
    # Категории тестов
    categories = [
        {
            'name': 'Algemene Farmacologie',
            'questions': [
                {
                    'text': 'Wat is de definitie van farmacokinetiek?',
                    'options': json.dumps([
                        'De werking van geneesmiddelen op het lichaam',
                        'Het proces van opname, verdeling, metabolisme en uitscheiding van geneesmiddelen',
                        'De chemische structuur van geneesmiddelen',
                        'De interactie tussen verschillende geneesmiddelen'
                    ]),
                    'correct_answer': 1,
                    'explanation': 'Farmacokinetiek beschrijft hoe het lichaam het geneesmiddel verwerkt (ADME: Absorptie, Distributie, Metabolisme, Excretie)'
                },
                {
                    'text': 'Welk proces beschrijft de biotransformatie?',
                    'options': json.dumps([
                        'De opname van medicijnen in het maag-darmkanaal',
                        'De verdeling van medicijnen door het lichaam',
                        'De omzetting van medicijnen in de lever',
                        'De uitscheiding van medicijnen via de nieren'
                    ]),
                    'correct_answer': 2,
                    'explanation': 'Biotransformatie vindt voornamelijk plaats in de lever en zorgt voor de omzetting van geneesmiddelen'
                }
            ]
        },
        {
            'name': 'Medicijnkennis',
            'questions': [
                {
                    'text': 'Welke groep medicijnen wordt gebruikt bij de behandeling van hypertensie?',
                    'options': json.dumps([
                        'ACE-remmers',
                        'Antihistaminica',
                        'Antidepressiva',
                        'Antibiotica'
                    ]),
                    'correct_answer': 0,
                    'explanation': 'ACE-remmers zijn een belangrijke groep medicijnen bij de behandeling van hoge bloeddruk'
                }
            ]
        },
        {
            'name': 'Interacties & Bijwerkingen',
            'questions': [
                {
                    'text': 'Wat is een contra-indicatie?',
                    'options': json.dumps([
                        'Een gewenst effect van een geneesmiddel',
                        'Een reden om een geneesmiddel niet te gebruiken',
                        'Een wisselwerking tussen twee geneesmiddelen',
                        'Een bijwerking van een geneesmiddel'
                    ]),
                    'correct_answer': 1,
                    'explanation': 'Een contra-indicatie is een omstandigheid of conditie waarbij een bepaald geneesmiddel niet gebruikt mag worden'
                }
            ]
        }
    ]
    
    for category_data in categories:
        category = QuestionCategory(
            name=category_data['name']
        )
        db.session.add(category)
        db.session.flush()  # Получаем ID категории
        
        for question_data in category_data['questions']:
            question = Question(
                text=question_data['text'],
                options=question_data['options'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                category_id=category.id
            )
            db.session.add(question)
    
    db.session.commit()

def create_pharmacy_tests():
    """Создает тесты для фармацевтов"""
    subject = Subject.query.get(101)
    if not subject:
        print("Предмет фармацевтики не найден")
        return
    
    # Создаем тест
    test = Test(
        title='BIG-registratie Proefexamen',
        description='Voorbereidende test voor BIG-registratie als apotheker',
        test_type='final_subject',
        subject_final_test_id=subject.id
    )
    db.session.add(test)
    db.session.commit()

if __name__ == '__main__':
    create_pharmacy_test_categories()
    create_pharmacy_tests() 