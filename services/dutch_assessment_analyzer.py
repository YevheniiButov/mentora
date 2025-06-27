from services.assessment_analyzer import AssessmentAnalyzer
from data.dutch_assessment_categories import DUTCH_COMPETENCY_LEVELS, REGIONAL_FOCUS
from typing import Dict, List, Tuple
import numpy as np

class DutchAssessmentAnalyzer(AssessmentAnalyzer):
    """Специализированный анализатор для оценки готовности к работе в Нидерландах"""
    
    def __init__(self):
        super().__init__()
        self.dutch_competency_levels = DUTCH_COMPETENCY_LEVELS
        self.regional_focus = REGIONAL_FOCUS
        
        # Специфические пороги для нидерландских требований
        self.dutch_thresholds = {
            'critical_areas': ['dutch_standards', 'healthcare_system', 'preventive_care'],
            'minimum_critical_score': 70,  # Минимум для критических областей
            'overall_minimum': 65,         # Общий минимум для работы
            'independent_practice': 80     # Для самостоятельной практики
        }
    
    def analyze_dutch_competency(self, attempt, regional_focus=None):
        """Анализ соответствия нидерландским требованиям"""
        
        # Базовый анализ
        base_analysis = self.analyze_attempt(attempt)
        
        # Дополнительный анализ для Нидерландов
        dutch_analysis = {
            'competency_level': self._determine_dutch_competency_level(base_analysis),
            'critical_areas_assessment': self._assess_critical_areas(base_analysis),
            'practice_readiness': self._assess_practice_readiness(base_analysis),
            'regional_recommendations': self._generate_regional_recommendations(base_analysis, regional_focus),
            'next_steps': self._generate_next_steps(base_analysis),
            'certification_pathway': self._recommend_certification_pathway(base_analysis)
        }
        
        # Объединяем анализы
        combined_analysis = {**base_analysis, **dutch_analysis}
        
        return combined_analysis

    def _determine_dutch_competency_level(self, analysis):
        """Определение уровня компетенции для работы в Нидерландах"""
        overall_score = analysis.get('overall_score', 0)
        critical_scores = [cat['score'] for cat in analysis.get('category_analyses', []) if cat['slug'] in self.dutch_thresholds['critical_areas']]
        critical_areas_score = np.mean(critical_scores) if critical_scores else 0
        level = 'insufficient'
        for lvl, data in sorted(self.dutch_competency_levels.items(), key=lambda x: x[1]['threshold']):
            if overall_score >= data['threshold']:
                level = lvl
        return {
            'level': level,
            'overall_score': overall_score,
            'critical_areas_score': critical_areas_score,
            'description': self.dutch_competency_levels[level]['description'],
            'recommendation': self.dutch_competency_levels[level]['recommendation']
        }

    def _assess_critical_areas(self, analysis):
        """Проверка критических областей по порогам"""
        result = {}
        for area in self.dutch_thresholds['critical_areas']:
            cat = next((c for c in analysis.get('category_analyses', []) if c['slug'] == area), None)
            if cat:
                status = 'ok' if cat['score'] >= self.dutch_thresholds['minimum_critical_score'] else 'low'
                result[area] = {'score': cat['score'], 'status': status}
        return result

    def _assess_practice_readiness(self, analysis):
        """Оценка готовности к практике (под надзором/самостоятельно)"""
        overall = analysis.get('overall_score', 0)
        critical = [cat['score'] for cat in analysis.get('category_analyses', []) if cat['slug'] in self.dutch_thresholds['critical_areas']]
        min_critical = min(critical) if critical else 0
        return {
            'supervised_practice': {
                'ready': overall >= self.dutch_thresholds['overall_minimum'] and min_critical >= self.dutch_thresholds['minimum_critical_score'],
                'explanation': 'Можно работать под супервизией' if overall >= self.dutch_thresholds['overall_minimum'] else 'Требуется дополнительное обучение'
            },
            'independent_general': {
                'ready': overall >= self.dutch_thresholds['independent_practice'] and min_critical >= self.dutch_thresholds['minimum_critical_score'],
                'explanation': 'Готов к самостоятельной практике' if overall >= self.dutch_thresholds['independent_practice'] else 'Требуется повышение квалификации'
            }
        }

    def _generate_regional_recommendations(self, analysis, regional_focus):
        """Рекомендации с учетом регионального фокуса (urban/rural)"""
        if not regional_focus or regional_focus not in self.regional_focus:
            return {}
        focus_data = self.regional_focus[regional_focus]
        recs = {
            'focus': focus_data['focus'],
            'additional_weight': focus_data.get('additional_weight', {})
        }
        return recs

    def _generate_next_steps(self, analysis):
        """Генерация следующих шагов для пользователя"""
        level = self._determine_dutch_competency_level(analysis)['level']
        if level == 'insufficient':
            return [
                'Пройти адаптационный курс',
                'Улучшить знание нидерландских стандартов',
                'Повысить уровень языка до B2',
                'Повторно пройти оценку после обучения'
            ]
        elif level == 'basic':
            return [
                'Пройти практику под супервизией',
                'Углубить знания по критическим областям',
                'Подготовиться к BIG экзамену'
            ]
        elif level == 'competent':
            return [
                'Подать документы в BIG-register',
                'Пройти краткий ознакомительный курс',
                'Начать самостоятельную практику'
            ]
        else:
            return [
                'Зарегистрироваться в BIG',
                'Начать работу в выбранном регионе',
                'Рассмотреть возможности для преподавания или наставничества'
            ]

    def _recommend_certification_pathway(self, analysis):
        """Рекомендация по пути сертификации"""
        level = self._determine_dutch_competency_level(analysis)['level']
        if level == 'insufficient':
            return {
                'duration_months': 12,
                'estimated_cost_eur': 20000,
                'required_courses': [
                    'Адаптационный курс для иностранных стоматологов',
                    'Языковая подготовка (голландский B2)',
                    'Практическая стажировка'
                ]
            }
        elif level == 'basic':
            return {
                'duration_months': 6,
                'estimated_cost_eur': 12000,
                'required_courses': [
                    'Курс по нидерландским стандартам',
                    'Практика под супервизией'
                ]
            }
        elif level == 'competent':
            return {
                'duration_months': 2,
                'estimated_cost_eur': 3000,
                'required_courses': [
                    'BIG-register регистрация',
                    'Краткий ознакомительный курс'
                ]
            }
        else:
            return {
                'duration_months': 1,
                'estimated_cost_eur': 1500,
                'required_courses': [
                    'BIG-register регистрация'
                ]
            } 