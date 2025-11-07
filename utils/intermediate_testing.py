#!/usr/bin/env python3
"""
Система промежуточного тестирования
Проверка знаний по модулям с адаптивной сложностью
"""

from typing import Dict, List, Optional, Tuple
from models import User, Module, Lesson, Question, UserProgress, TestSession, TestResult, QuestionCategory
from extensions import db
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc
import random
import json

class IntermediateTestingSystem:
    """Система промежуточного тестирования"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def create_module_test(self, module_id: int, test_type: str = 'adaptive') -> Dict:
        """Создает промежуточный тест для модуля"""
        
        module = Module.query.get_or_404(module_id)
        
        # Определяем сложность теста на основе прогресса пользователя
        difficulty = self._determine_test_difficulty(module_id)
        
        # Получаем вопросы для теста
        questions = self._get_test_questions(module_id, difficulty, test_type)
        
        # Создаем сессию тестирования
        test_session = TestSession(
            user_id=self.user_id,
            module_id=module_id,
            test_type=test_type,
            difficulty=difficulty,
            total_questions=len(questions),
            started_at=datetime.now(timezone.utc),
            status='in_progress'
        )
        db.session.add(test_session)
        db.session.flush()
        
        # Сохраняем вопросы в сессии
        test_session.set_session_data({
            'questions': [q.id for q in questions],
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now(timezone.utc).isoformat()
        })
        db.session.commit()
        
        return {
            'session_id': test_session.id,
            'module_name': module.title,
            'total_questions': len(questions),
            'difficulty': difficulty,
            'estimated_time': len(questions) * 2,  # 2 минуты на вопрос
            'first_question': self._format_question(questions[0]) if questions else None
        }
    
    def _determine_test_difficulty(self, module_id: int) -> str:
        """Определяет сложность теста на основе прогресса пользователя"""
        
        # Получаем прогресс по модулю
        module_progress = self._get_module_progress(module_id)
        
        # Получаем результаты предыдущих тестов
        previous_tests = TestSession.query.filter_by(
            user_id=self.user_id,
            module_id=module_id,
            status='completed'
        ).order_by(TestSession.completed_at.desc()).limit(3).all()
        
        # Рассчитываем средний балл
        avg_score = 0
        if previous_tests:
            scores = []
            for test in previous_tests:
                if test.score is not None:
                    scores.append(test.score)
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # Определяем сложность на основе прогресса и предыдущих результатов
        if module_progress['completion_rate'] < 30 or avg_score < 50:
            return 'easy'
        elif module_progress['completion_rate'] < 70 or avg_score < 80:
            return 'medium'
        else:
            return 'hard'
    
    def _get_module_progress(self, module_id: int) -> Dict:
        """Получает прогресс пользователя по модулю"""
        
        lessons = Lesson.query.filter_by(module_id=module_id).all()
        total_lessons = len(lessons)
        completed_lessons = 0
        total_time = 0
        
        for lesson in lessons:
            progress = lesson.get_user_progress(self.user_id)
            if progress and progress.completed:
                completed_lessons += 1
            if progress and progress.time_spent:
                total_time += progress.time_spent
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'total_time': total_time
        }
    
    def _get_test_questions(self, module_id: int, difficulty: str, test_type: str) -> List[Question]:
        """Получает вопросы для теста"""
        
        # Получаем категории вопросов, связанные с модулем
        # Для простоты берем все категории, но в реальной системе нужно связать их с модулями
        categories = QuestionCategory.query.all()
        
        if not categories:
            # Если категорий нет, создаем тестовую
            category = QuestionCategory(
                name=f"Тесты для модуля {module_id}",
                description="Промежуточные тесты"
            )
            db.session.add(category)
            db.session.flush()
            categories = [category]
        
        category_ids = [cat.id for cat in categories]
        
        # Базовый запрос вопросов
        query = Question.query.filter(Question.category_id.in_(category_ids))
        
        # Фильтруем по сложности
        if difficulty == 'easy':
            query = query.filter(Question.difficulty == 'easy')
        elif difficulty == 'hard':
            query = query.filter(Question.difficulty == 'hard')
        else:  # medium - смешанная сложность
            query = query.filter(Question.difficulty.in_(['easy', 'medium']))
        
        # Получаем вопросы
        questions = query.all()
        
        # Для адаптивного теста выбираем меньше вопросов
        if test_type == 'adaptive':
            max_questions = min(10, len(questions))
        else:
            max_questions = min(20, len(questions))
        
        # Перемешиваем и выбираем нужное количество
        random.shuffle(questions)
        return questions[:max_questions]
    
    def _format_question(self, question: Question) -> Dict:
        """Форматирует вопрос для отображения"""
        
        return {
            'id': question.id,
            'text': question.text,
            'type': question.type,
            'options': question.get_options() if question.type == 'multiple_choice' else None,
            'image_url': question.image_url,
            'explanation': question.explanation
        }
    
    def get_next_question(self, session_id: int) -> Optional[Dict]:
        """Получает следующий вопрос теста"""
        
        session = TestSession.query.get_or_404(session_id)
        
        if session.status != 'in_progress':
            return None
        
        session_data = session.get_session_data()
        current_question_index = session_data.get('current_question', 0)
        questions = session_data.get('questions', [])
        
        if current_question_index >= len(questions):
            return None
        
        question_id = questions[current_question_index]
        question = Question.query.get(question_id)
        
        if not question:
            return None
        
        return {
            'question': self._format_question(question),
            'question_number': current_question_index + 1,
            'total_questions': len(questions),
            'time_remaining': self._calculate_time_remaining(session)
        }
    
    def _calculate_time_remaining(self, session: TestSession) -> int:
        """Рассчитывает оставшееся время"""
        
        session_data = session.get_session_data()
        start_time = datetime.fromisoformat(session_data.get('start_time', datetime.now(timezone.utc).isoformat()))
        elapsed_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # 2 минуты на вопрос
        total_time = session.total_questions * 120
        remaining_time = max(0, total_time - elapsed_time)
        
        return int(remaining_time)
    
    def submit_answer(self, session_id: int, question_id: int, answer: str) -> Dict:
        """Отправляет ответ на вопрос"""
        
        session = TestSession.query.get_or_404(session_id)
        question = Question.query.get_or_404(question_id)
        
        if session.status != 'in_progress':
            return {'error': 'Тест уже завершен'}
        
        # Сохраняем ответ
        session_data = session.get_session_data()
        session_data['answers'][str(question_id)] = answer
        session_data['current_question'] = session_data.get('current_question', 0) + 1
        
        session.set_session_data(session_data)
        db.session.commit()
        
        # Проверяем, завершен ли тест
        if session_data['current_question'] >= len(session_data.get('questions', [])):
            return self._complete_test(session)
        
        # Возвращаем следующий вопрос
        next_question = self.get_next_question(session_id)
        return {
            'status': 'continue',
            'next_question': next_question,
            'progress': (session_data['current_question'] / len(session_data.get('questions', []))) * 100
        }
    
    def _complete_test(self, session: TestSession) -> Dict:
        """Завершает тест и рассчитывает результаты"""
        
        session_data = session.get_session_data()
        questions = session_data.get('questions', [])
        answers = session_data.get('answers', {})
        
        # Проверяем ответы
        correct_answers = 0
        total_questions = len(questions)
        
        for question_id in questions:
            question = Question.query.get(question_id)
            if question and str(question_id) in answers:
                user_answer = answers[str(question_id)]
                if question.check_answer(user_answer):
                    correct_answers += 1
        
        # Рассчитываем балл
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Обновляем сессию
        session.status = 'completed'
        session.completed_at = datetime.now(timezone.utc)
        session.score = score
        session.correct_answers = correct_answers
        
        # Сохраняем результаты
        session.set_session_data({
            **session_data,
            'final_score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'completion_time': datetime.now(timezone.utc).isoformat()
        })
        
        db.session.commit()
        
        # Создаем результат теста
        test_result = TestResult(
            user_id=self.user_id,
            test_session_id=session.id,
            module_id=session.module_id,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            test_type=session.test_type,
            difficulty=session.difficulty
        )
        db.session.add(test_result)
        db.session.commit()
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(session, score)
        
        return {
            'status': 'completed',
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'recommendations': recommendations,
            'performance_analysis': self._analyze_performance(session, answers)
        }
    
    def _generate_recommendations(self, session: TestSession, score: float) -> List[str]:
        """Генерирует рекомендации на основе результатов теста"""
        
        recommendations = []
        
        if score >= 90:
            recommendations.extend([
                "🎉 Отличный результат! Вы хорошо освоили материал.",
                "💡 Можете переходить к более сложным темам.",
                "📚 Рекомендуется повторить материал через неделю для закрепления."
            ])
        elif score >= 70:
            recommendations.extend([
                "👍 Хороший результат! Есть небольшие пробелы в знаниях.",
                "📖 Рекомендуется повторить темы с неправильными ответами.",
                "🔍 Обратите внимание на детали в изученном материале."
            ])
        elif score >= 50:
            recommendations.extend([
                "⚠️ Средний результат. Требуется дополнительное изучение.",
                "📚 Рекомендуется пройти уроки модуля еще раз.",
                "⏰ Уделите больше времени изучению сложных тем."
            ])
        else:
            recommendations.extend([
                "❌ Низкий результат. Требуется серьезная работа.",
                "🔄 Рекомендуется начать изучение модуля заново.",
                "📖 Обратитесь к дополнительным материалам.",
                "⏰ Увеличьте время на изучение каждой темы."
            ])
        
        # Добавляем специфичные рекомендации
        if session.difficulty == 'easy' and score < 70:
            recommendations.append("🎯 Рекомендуется пройти тест средней сложности после повторения.")
        elif session.difficulty == 'hard' and score > 80:
            recommendations.append("🚀 Отличные результаты! Можете попробовать более сложные задания.")
        
        return recommendations
    
    def _analyze_performance(self, session: TestSession, answers: Dict) -> Dict:
        """Анализирует производительность по тесту"""
        
        session_data = session.get_session_data()
        questions = session_data.get('questions', [])
        
        # Анализ по типам вопросов
        question_types = {}
        for question_id in questions:
            question = Question.query.get(question_id)
            if question:
                q_type = question.type
                if q_type not in question_types:
                    question_types[q_type] = {'total': 0, 'correct': 0}
                
                question_types[q_type]['total'] += 1
                if str(question_id) in answers and question.check_answer(answers[str(question_id)]):
                    question_types[q_type]['correct'] += 1
        
        # Рассчитываем процент правильных ответов по типам
        type_analysis = {}
        for q_type, stats in question_types.items():
            type_analysis[q_type] = {
                'total': stats['total'],
                'correct': stats['correct'],
                'percentage': (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            }
        
        return {
            'question_types': type_analysis,
            'time_spent': self._calculate_test_duration(session),
            'difficulty_level': session.difficulty,
            'test_type': session.test_type
        }
    
    def _calculate_test_duration(self, session: TestSession) -> int:
        """Рассчитывает продолжительность теста"""
        
        session_data = session.get_session_data()
        start_time = datetime.fromisoformat(session_data.get('start_time', datetime.now(timezone.utc).isoformat()))
        completion_time = datetime.fromisoformat(session_data.get('completion_time', datetime.now(timezone.utc).isoformat()))
        
        return int((completion_time - start_time).total_seconds())
    
    def get_test_history(self, module_id: Optional[int] = None) -> List[Dict]:
        """Получает историю тестов пользователя"""
        
        query = TestSession.query.filter_by(user_id=self.user_id, status='completed')
        
        if module_id:
            query = query.filter_by(module_id=module_id)
        
        sessions = query.order_by(TestSession.completed_at.desc()).limit(10).all()
        
        history = []
        for session in sessions:
            module = Module.query.get(session.module_id)
            history.append({
                'id': session.id,
                'module_name': module.title if module else 'Неизвестный модуль',
                'test_type': session.test_type,
                'difficulty': session.difficulty,
                'score': session.score,
                'completed_at': session.completed_at.isoformat(),
                'total_questions': session.total_questions,
                'correct_answers': session.correct_answers
            })
        
        return history
    
    def get_performance_stats(self, module_id: Optional[int] = None) -> Dict:
        """Получает статистику производительности"""
        
        query = TestSession.query.filter_by(user_id=self.user_id, status='completed')
        
        if module_id:
            query = query.filter_by(module_id=module_id)
        
        sessions = query.all()
        
        if not sessions:
            return {
                'total_tests': 0,
                'average_score': 0,
                'best_score': 0,
                'improvement_trend': 'stable'
            }
        
        scores = [s.score for s in sessions if s.score is not None]
        average_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        
        # Анализируем тренд улучшения
        recent_scores = scores[:5]  # Последние 5 тестов
        if len(recent_scores) >= 2:
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            if avg_second > avg_first + 5:
                trend = 'improving'
            elif avg_second < avg_first - 5:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'total_tests': len(sessions),
            'average_score': round(average_score, 1),
            'best_score': round(best_score, 1),
            'improvement_trend': trend,
            'recent_scores': recent_scores
        }

def create_module_test(user_id: int, module_id: int, test_type: str = 'adaptive') -> Dict:
    """Создает промежуточный тест для модуля"""
    
    testing_system = IntermediateTestingSystem(user_id)
    return testing_system.create_module_test(module_id, test_type)

def get_next_question(user_id: int, session_id: int) -> Optional[Dict]:
    """Получает следующий вопрос теста"""
    
    testing_system = IntermediateTestingSystem(user_id)
    return testing_system.get_next_question(session_id)

def submit_test_answer(user_id: int, session_id: int, question_id: int, answer: str) -> Dict:
    """Отправляет ответ на вопрос теста"""
    
    testing_system = IntermediateTestingSystem(user_id)
    return testing_system.submit_answer(session_id, question_id, answer)

def get_test_history(user_id: int, module_id: Optional[int] = None) -> List[Dict]:
    """Получает историю тестов пользователя"""
    
    testing_system = IntermediateTestingSystem(user_id)
    return testing_system.get_test_history(module_id)

def get_performance_stats(user_id: int, module_id: Optional[int] = None) -> Dict:
    """Получает статистику производительности"""
    
    testing_system = IntermediateTestingSystem(user_id)
    return testing_system.get_performance_stats(module_id) 