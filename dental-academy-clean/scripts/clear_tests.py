from app import app, db
from models import QuestionCategory, Question, Test

def clear_tests():
    """Удаляет все тесты и категории"""
    with app.app_context():
        QuestionCategory.query.delete()
        Question.query.delete()
        Test.query.delete()
        db.session.commit()
        print('✅ Все тесты и категории удалены')

if __name__ == '__main__':
    clear_tests() 