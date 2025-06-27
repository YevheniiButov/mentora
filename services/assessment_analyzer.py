"""
Базовый класс для анализа результатов оценки знаний
"""

from typing import Dict, List, Tuple, Any
import numpy as np
from datetime import datetime

class AssessmentAnalyzer:
    """Базовый анализатор результатов оценки"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    def analyze_attempt(self, attempt) -> Dict[str, Any]:
        """Базовый анализ попытки прохождения оценки"""
        
        # Получаем данные попытки
        total_questions = attempt.total_questions
        correct_answers = attempt.correct_answers
        total_score = attempt.total_score
        time_spent = attempt.time_spent
        
        # Базовые метрики
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        average_time_per_question = time_spent / total_questions if total_questions > 0 else 0
        
        # Определяем уровень навыков
        skill_level = self._determine_skill_level(total_score)
        
        # Анализ по категориям
        category_analyses = self._analyze_categories(attempt)
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(category_analyses, total_score)
        
        # Определяем сильные и слабые стороны
        strengths, weaknesses = self._identify_strengths_weaknesses(category_analyses)
        
        return {
            'overall_score': total_score,
            'accuracy': round(accuracy, 1),
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'time_spent': time_spent,
            'average_time_per_question': round(average_time_per_question, 1),
            'skill_level': skill_level['level'],
            'skill_description': skill_level['description'],
            'category_analyses': category_analyses,
            'recommendations': recommendations,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'completion_time': self._format_time(time_spent),
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    def _determine_skill_level(self, score: float) -> Dict[str, str]:
        """Определение уровня навыков на основе баллов"""
        if score >= 90:
            return {
                'level': 'excellent',
                'description': 'Отличный уровень знаний. Вы демонстрируете глубокое понимание материала.'
            }
        elif score >= 80:
            return {
                'level': 'good',
                'description': 'Хороший уровень знаний. Есть небольшие области для улучшения.'
            }
        elif score >= 70:
            return {
                'level': 'average',
                'description': 'Средний уровень знаний. Рекомендуется дополнительное изучение.'
            }
        elif score >= 60:
            return {
                'level': 'below_average',
                'description': 'Уровень ниже среднего. Требуется серьезная работа над материалом.'
            }
        else:
            return {
                'level': 'poor',
                'description': 'Низкий уровень знаний. Необходимо пройти курс заново.'
            }
    
    def _analyze_categories(self, attempt) -> List[Dict[str, Any]]:
        """Анализ результатов по категориям"""
        category_scores = attempt.get_category_scores()
        analyses = []
        
        for category_id, scores in category_scores.items():
            score = scores.get('score', 0)
            correct = scores.get('correct', 0)
            total = scores.get('total', 0)
            
            # Определяем уровень категории
            if score >= 80:
                level = 'excellent'
                level_text = 'Отлично'
                level_icon = 'check-circle-fill'
            elif score >= 70:
                level = 'good'
                level_text = 'Хорошо'
                level_icon = 'check-circle'
            elif score >= 60:
                level = 'average'
                level_text = 'Средне'
                level_icon = 'exclamation-circle'
            else:
                level = 'poor'
                level_text = 'Плохо'
                level_icon = 'x-circle'
            
            analyses.append({
                'category_id': category_id,
                'category_name': scores.get('name', f'Категория {category_id}'),
                'score': score,
                'correct': correct,
                'total': total,
                'level': level,
                'level_text': level_text,
                'level_icon': level_icon,
                'level_class': level,
                'description': self._get_category_description(score),
                'gradient': self._get_category_gradient(score),
                'icon': self._get_category_icon(category_id),
                'slug': scores.get('slug', f'category_{category_id}')
            })
        
        return analyses
    
    def _generate_recommendations(self, category_analyses: List[Dict], overall_score: float) -> List[Dict]:
        """Генерация рекомендаций на основе анализа"""
        recommendations = []
        
        # Рекомендации на основе общего балла
        if overall_score < 70:
            recommendations.append({
                'title': 'Повторите основные концепции',
                'description': 'Рекомендуется пройти курс заново, уделив особое внимание фундаментальным темам.',
                'gradient': 'linear-gradient(135deg, #ff6b6b, #ee5a52)',
                'icon': 'book',
                'duration': '2-3 недели',
                'difficulty': 'Начальный'
            })
        
        # Рекомендации на основе слабых категорий
        weak_categories = [cat for cat in category_analyses if cat['score'] < 70]
        for category in weak_categories[:3]:  # Топ-3 слабые категории
            recommendations.append({
                'title': f'Улучшите знания в области "{category["category_name"]}"',
                'description': f'Ваш результат в этой категории составляет {category["score"]}%. Рекомендуется дополнительное изучение.',
                'gradient': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
                'icon': 'lightbulb',
                'duration': '1-2 недели',
                'difficulty': 'Средний'
            })
        
        # Рекомендации для сильных категорий
        strong_categories = [cat for cat in category_analyses if cat['score'] >= 80]
        if strong_categories:
            recommendations.append({
                'title': 'Развивайте сильные стороны',
                'description': f'У вас отличные результаты в {len(strong_categories)} категориях. Рассмотрите возможность углубленного изучения.',
                'gradient': 'linear-gradient(135deg, #667eea, #764ba2)',
                'icon': 'star',
                'duration': 'Постоянно',
                'difficulty': 'Продвинутый'
            })
        
        # Общие рекомендации
        recommendations.append({
            'title': 'Практикуйтесь регулярно',
            'description': 'Регулярная практика поможет закрепить знания и улучшить результаты.',
            'gradient': 'linear-gradient(135deg, #f093fb, #f5576c)',
            'icon': 'calendar-check',
            'duration': 'Еженедельно',
            'difficulty': 'Любой'
        })
        
        return recommendations[:5]  # Ограничиваем 5 рекомендациями
    
    def _identify_strengths_weaknesses(self, category_analyses: List[Dict]) -> Tuple[List[str], List[str]]:
        """Определение сильных и слабых сторон"""
        strengths = []
        weaknesses = []
        
        for category in category_analyses:
            if category['score'] >= 80:
                strengths.append(f"Отличные знания в области '{category['category_name']}' ({category['score']}%)")
            elif category['score'] < 60:
                weaknesses.append(f"Требуется улучшение в области '{category['category_name']}' ({category['score']}%)")
        
        return strengths, weaknesses
    
    def _get_category_description(self, score: float) -> str:
        """Получение описания для категории на основе баллов"""
        if score >= 80:
            return "Отличное понимание материала"
        elif score >= 70:
            return "Хорошее понимание с небольшими пробелами"
        elif score >= 60:
            return "Базовое понимание, требуется повторение"
        else:
            return "Требуется серьезная работа над материалом"
    
    def _get_category_gradient(self, score: float) -> str:
        """Получение градиента для категории на основе баллов"""
        if score >= 80:
            return "linear-gradient(135deg, #667eea, #764ba2)"
        elif score >= 70:
            return "linear-gradient(135deg, #4ecdc4, #44a08d)"
        elif score >= 60:
            return "linear-gradient(135deg, #f093fb, #f5576c)"
        else:
            return "linear-gradient(135deg, #ff6b6b, #ee5a52)"
    
    def _get_category_icon(self, category_id: str) -> str:
        """Получение иконки для категории"""
        icon_mapping = {
            'anatomy': 'body-text',
            'diagnosis': 'search',
            'treatment': 'tools',
            'prevention': 'shield-check',
            'materials': 'box',
            'radiology': 'camera',
            'surgery': 'scissors',
            'pediatrics': 'heart',
            'emergency': 'exclamation-triangle',
            'ethics': 'person-check'
        }
        
        # Пытаемся найти иконку по ID категории
        for key, icon in icon_mapping.items():
            if key in str(category_id).lower():
                return icon
        
        # Возвращаем иконку по умолчанию
        return 'book'
    
    def _format_time(self, seconds: int) -> str:
        """Форматирование времени в читаемый вид"""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes} мин {remaining_seconds} сек"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} ч {minutes} мин"
