from models import db, Question, QuestionCategory, Test, TestAttempt, UserProgress
from sqlalchemy import func
import random
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TestGenerator:
    """Генератор тестов различных типов"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        
    def generate_quick_test(self, category: Optional[str] = None, count: int = 10) -> List[int]:
        """Генерирует быстрый тест (5-10 вопросов)
        
        Args:
            category: Категория вопросов (опционально)
            count: Количество вопросов (по умолчанию 10)
            
        Returns:
            List[int]: Список ID вопросов
        """
        try:
            query = Question.query
            
            if category:
                query = query.join(QuestionCategory).filter(QuestionCategory.name == category)
            
            # Получаем все доступные вопросы
            available_questions = query.all()
            
            if not available_questions:
                logger.warning(f"No questions found for category: {category}")
                return []
            
            # Выбираем случайные вопросы
            selected_questions = random.sample(available_questions, min(count, len(available_questions)))
            return [q.id for q in selected_questions]
            
        except Exception as e:
            logger.error(f"Error generating quick test: {e}")
            return []
    
    def generate_comprehensive_test(self, category: Optional[str] = None, count: int = 30) -> List[int]:
        """Генерирует полный тест (20-30 вопросов)
        
        Args:
            category: Категория вопросов (опционально)
            count: Количество вопросов (по умолчанию 30)
            
        Returns:
            List[int]: Список ID вопросов
        """
        try:
            query = Question.query
            
            if category:
                query = query.join(QuestionCategory).filter(QuestionCategory.name == category)
            
            # Получаем все доступные вопросы
            available_questions = query.all()
            
            if not available_questions:
                logger.warning(f"No questions found for category: {category}")
                return []
            
            # Выбираем случайные вопросы
            selected_questions = random.sample(available_questions, min(count, len(available_questions)))
            return [q.id for q in selected_questions]
            
        except Exception as e:
            logger.error(f"Error generating comprehensive test: {e}")
            return []
    
    def generate_custom_test(self, 
                           categories: List[str], 
                           count: int,
                           difficulty: Optional[str] = None) -> List[int]:
        """Генерирует настраиваемый тест
        
        Args:
            categories: Список категорий
            count: Общее количество вопросов
            difficulty: Уровень сложности (опционально)
            
        Returns:
            List[int]: Список ID вопросов
        """
        try:
            query = Question.query.join(QuestionCategory)
            
            # Фильтруем по категориям
            if categories:
                query = query.filter(QuestionCategory.name.in_(categories))
            
            # Фильтруем по сложности, если указана
            if difficulty:
                query = query.filter(Question.difficulty == difficulty)
            
            # Получаем все доступные вопросы
            available_questions = query.all()
            
            if not available_questions:
                logger.warning(f"No questions found for categories: {categories}")
                return []
            
            # Выбираем случайные вопросы
            selected_questions = random.sample(available_questions, min(count, len(available_questions)))
            return [q.id for q in selected_questions]
            
        except Exception as e:
            logger.error(f"Error generating custom test: {e}")
            return []
    
    def get_user_progress(self) -> Dict:
        """Получает прогресс пользователя для адаптивной генерации тестов
        
        Returns:
            Dict: Статистика прогресса пользователя
        """
        try:
            # Получаем общую статистику
            total_attempts = TestAttempt.query.filter_by(user_id=self.user_id).count()
            correct_attempts = TestAttempt.query.filter_by(
                user_id=self.user_id,
                is_correct=True
            ).count()
            
            # Получаем статистику по категориям
            category_stats = db.session.query(
                QuestionCategory.name,
                func.count(TestAttempt.id).label('total'),
                func.sum(case((TestAttempt.is_correct == True, 1), else_=0)).label('correct')
            ).join(
                Question, Question.category_id == QuestionCategory.id
            ).join(
                TestAttempt, TestAttempt.question_id == Question.id
            ).filter(
                TestAttempt.user_id == self.user_id
            ).group_by(
                QuestionCategory.name
            ).all()
            
            return {
                'total_attempts': total_attempts,
                'correct_attempts': correct_attempts,
                'accuracy': (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0,
                'category_stats': {
                    cat.name: {
                        'total': cat.total,
                        'correct': cat.correct,
                        'accuracy': (cat.correct / cat.total * 100) if cat.total > 0 else 0
                    } for cat in category_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return {
                'total_attempts': 0,
                'correct_attempts': 0,
                'accuracy': 0,
                'category_stats': {}
            } 