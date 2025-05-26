# utils/adaptive_learning.py
"""
Система адаптивного обучения для виртуальных пациентов
Анализирует поведение пользователя и предлагает персонализированный контент
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class LearningStyle(Enum):
    """Стили обучения пользователей"""
    VISUAL = "visual"           # Предпочитает визуальную информацию
    ANALYTICAL = "analytical"   # Любит детальный анализ
    INTUITIVE = "intuitive"     # Полагается на интуицию
    SYSTEMATIC = "systematic"   # Следует протоколам
    EMPATHETIC = "empathetic"   # Фокус на эмоциях пациента

class SkillLevel(Enum):
    """Уровни навыков"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class UserProfile:
    """Профиль пользователя для адаптивного обучения"""
    user_id: int
    learning_style: LearningStyle
    skill_levels: Dict[str, SkillLevel]  # по областям: диагностика, коммуникация и т.д.
    preferences: Dict[str, any]
    performance_history: List[Dict]
    weakness_areas: List[str]
    strength_areas: List[str]
    last_updated: datetime

class AdaptiveLearningEngine:
    """Основной класс системы адаптивного обучения"""
    
    def __init__(self):
        self.skill_areas = [
            'diagnosis', 'communication', 'empathy', 'clinical_reasoning',
            'patient_management', 'treatment_planning', 'emergency_response'
        ]
        
    def analyze_user_performance(self, user_id: int, recent_attempts: List[Dict]) -> UserProfile:
        """
        Анализирует производительность пользователя и создает/обновляет профиль
        
        Args:
            user_id: ID пользователя
            recent_attempts: Последние попытки прохождения сценариев
            
        Returns:
            UserProfile: Обновленный профиль пользователя
        """
        # Анализируем стиль обучения
        learning_style = self._determine_learning_style(recent_attempts)
        
        # Оцениваем уровни навыков по областям
        skill_levels = self._assess_skill_levels(recent_attempts)
        
        # Определяем предпочтения
        preferences = self._extract_preferences(recent_attempts)
        
        # Находим слабые и сильные стороны
        weakness_areas, strength_areas = self._identify_strengths_weaknesses(recent_attempts)
        
        return UserProfile(
            user_id=user_id,
            learning_style=learning_style,
            skill_levels=skill_levels,
            preferences=preferences,
            performance_history=recent_attempts,
            weakness_areas=weakness_areas,
            strength_areas=strength_areas,
            last_updated=datetime.utcnow()
        )
    
    def _determine_learning_style(self, attempts: List[Dict]) -> LearningStyle:
        """Определяет стиль обучения на основе поведения"""
        if not attempts:
            return LearningStyle.SYSTEMATIC  # По умолчанию
        
        # Анализируем время принятия решений
        decision_times = []
        empathy_scores = []
        systematic_choices = 0
        
        for attempt in attempts:
            history = json.loads(attempt.get('dialogue_history', '{}'))
            decisions = history.get('decisions', [])
            
            for decision in decisions:
                # Время принятия решения
                if 'decision_time' in decision:
                    decision_times.append(decision['decision_time'])
                
                # Эмпатические решения
                if 'factors' in decision and 'empathy' in decision['factors']:
                    empathy_scores.append(decision['factors']['empathy'])
                
                # Систематические решения (следование протоколу)
                option_text = decision.get('option_text', '').lower()
                if any(word in option_text for word in ['осмотр', 'анамнез', 'тест', 'исследование']):
                    systematic_choices += 1
        
        # Анализируем паттерны
        avg_decision_time = np.mean(decision_times) if decision_times else 30
        avg_empathy = np.mean(empathy_scores) if empathy_scores else 1.0
        systematic_ratio = systematic_choices / len([d for a in attempts for d in json.loads(a.get('dialogue_history', '{}')).get('decisions', [])])
        
        # Определяем стиль
        if avg_empathy > 1.1 and systematic_ratio < 0.5:
            return LearningStyle.EMPATHETIC
        elif avg_decision_time > 45 and systematic_ratio > 0.7:
            return LearningStyle.ANALYTICAL
        elif avg_decision_time < 15:
            return LearningStyle.INTUITIVE
        elif systematic_ratio > 0.6:
            return LearningStyle.SYSTEMATIC
        else:
            return LearningStyle.VISUAL
    
    def _assess_skill_levels(self, attempts: List[Dict]) -> Dict[str, SkillLevel]:
        """Оценивает уровни навыков по различным областям"""
        skill_scores = {area: [] for area in self.skill_areas}
        
        for attempt in attempts:
            scenario_score = attempt.get('score', 0)
            max_score = attempt.get('max_score', 100)
            percentage = (scenario_score / max_score) * 100 if max_score > 0 else 0
            
            # Анализируем историю решений для определения навыков
            history = json.loads(attempt.get('dialogue_history', '{}'))
            decisions = history.get('decisions', [])
            
            # Диагностические навыки
            diagnosis_decisions = [d for d in decisions if 'диагност' in d.get('option_text', '').lower() or 'осмотр' in d.get('option_text', '').lower()]
            if diagnosis_decisions:
                avg_diagnosis_score = np.mean([d.get('final_score', 0) for d in diagnosis_decisions])
                skill_scores['diagnosis'].append(avg_diagnosis_score)
            
            # Коммуникативные навыки
            comm_decisions = [d for d in decisions if any(word in d.get('option_text', '').lower() for word in ['объясн', 'расскаж', 'спрос', 'выслуш'])]
            if comm_decisions:
                avg_comm_score = np.mean([d.get('final_score', 0) for d in comm_decisions])
                skill_scores['communication'].append(avg_comm_score)
            
            # Эмпатия
            empathy_factors = [d.get('factors', {}).get('empathy', 1.0) for d in decisions if 'factors' in d]
            if empathy_factors:
                skill_scores['empathy'].append(np.mean(empathy_factors) * 50)  # Нормализуем
        
        # Определяем уровни навыков
        skill_levels = {}
        for area, scores in skill_scores.items():
            if not scores:
                skill_levels[area] = SkillLevel.BEGINNER
                continue
                
            avg_score = np.mean(scores)
            if avg_score >= 15:
                skill_levels[area] = SkillLevel.EXPERT
            elif avg_score >= 10:
                skill_levels[area] = SkillLevel.ADVANCED
            elif avg_score >= 5:
                skill_levels[area] = SkillLevel.INTERMEDIATE
            else:
                skill_levels[area] = SkillLevel.BEGINNER
        
        return skill_levels
    
    def _extract_preferences(self, attempts: List[Dict]) -> Dict[str, any]:
        """Извлекает предпочтения пользователя из поведения"""
        preferences = {
            'scenario_length': 'medium',
            'difficulty_preference': 'adaptive',
            'feedback_frequency': 'medium',
            'hint_usage': False,
            'detailed_explanations': True
        }
        
        if not attempts:
            return preferences
        
        # Анализируем предпочтения длины сценариев
        scenario_lengths = [len(json.loads(a.get('dialogue_history', '{}')).get('decisions', [])) for a in attempts]
        avg_length = np.mean(scenario_lengths) if scenario_lengths else 5
        
        if avg_length > 8:
            preferences['scenario_length'] = 'long'
        elif avg_length < 4:
            preferences['scenario_length'] = 'short'
        
        # Предпочитаемая сложность
        completion_rates = []
        for attempt in attempts:
            if attempt.get('completed', False):
                score_ratio = attempt.get('score', 0) / attempt.get('max_score', 100)
                completion_rates.append(score_ratio)
        
        if completion_rates:
            avg_completion = np.mean(completion_rates)
            if avg_completion > 0.8:
                preferences['difficulty_preference'] = 'challenging'
            elif avg_completion < 0.4:
                preferences['difficulty_preference'] = 'easier'
        
        return preferences
    
    def _identify_strengths_weaknesses(self, attempts: List[Dict]) -> Tuple[List[str], List[str]]:
        """Определяет сильные и слабые стороны пользователя"""
        area_scores = {area: [] for area in self.skill_areas}
        
        for attempt in attempts:
            history = json.loads(attempt.get('dialogue_history', '{}'))
            decisions = history.get('decisions', [])
            
            # Группируем решения по областям
            for decision in decisions:
                option_text = decision.get('option_text', '').lower()
                score = decision.get('final_score', 0)
                
                if any(word in option_text for word in ['диагност', 'осмотр', 'исследован']):
                    area_scores['diagnosis'].append(score)
                elif any(word in option_text for word in ['объясн', 'расскаж', 'сообщ']):
                    area_scores['communication'].append(score)
                elif any(word in option_text for word in ['понима', 'сочувств', 'поддерж']):
                    area_scores['empathy'].append(score)
                elif any(word in option_text for word in ['лечен', 'терап', 'процедур']):
                    area_scores['treatment_planning'].append(score)
        
        # Вычисляем средние баллы по областям
        area_averages = {}
        for area, scores in area_scores.items():
            if scores:
                area_averages[area] = np.mean(scores)
            else:
                area_averages[area] = 0
        
        # Определяем сильные и слабые стороны
        sorted_areas = sorted(area_averages.items(), key=lambda x: x[1])
        
        weakness_areas = [area for area, score in sorted_areas[:2] if score < 5]
        strength_areas = [area for area, score in sorted_areas[-2:] if score > 8]
        
        return weakness_areas, strength_areas
    
    def recommend_next_scenarios(self, user_profile: UserProfile, available_scenarios: List[Dict]) -> List[Dict]:
        """
        Рекомендует следующие сценарии на основе профиля пользователя
        
        Args:
            user_profile: Профиль пользователя
            available_scenarios: Доступные сценарии
            
        Returns:
            List[Dict]: Рекомендованные сценарии с приоритетом
        """
        recommendations = []
        
        for scenario in available_scenarios:
            score = self._calculate_scenario_relevance(user_profile, scenario)
            recommendations.append({
                'scenario': scenario,
                'relevance_score': score,
                'recommendation_reason': self._get_recommendation_reason(user_profile, scenario, score)
            })
        
        # Сортируем по релевантности
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations[:5]  # Топ 5 рекомендаций
    
    def _calculate_scenario_relevance(self, user_profile: UserProfile, scenario: Dict) -> float:
        """Рассчитывает релевантность сценария для пользователя"""
        relevance_score = 0.0
        
        # Анализируем сценарий
        scenario_data = json.loads(scenario.get('scenario_data', '{}'))
        
        # Учитываем слабые стороны пользователя
        for weakness in user_profile.weakness_areas:
            if self._scenario_addresses_skill(scenario_data, weakness):
                relevance_score += 3.0
        
        # Соответствие уровню навыков
        scenario_difficulty = self._assess_scenario_difficulty(scenario_data)
        user_avg_skill = np.mean([skill.value for skill in user_profile.skill_levels.values()])
        
        # Оптимальная сложность немного выше текущего уровня
        if scenario_difficulty == user_avg_skill + 0.5:
            relevance_score += 2.0
        elif abs(scenario_difficulty - user_avg_skill) <= 1.0:
            relevance_score += 1.0
        
        # Учитываем стиль обучения
        if self._scenario_matches_learning_style(scenario_data, user_profile.learning_style):
            relevance_score += 1.5
        
        # Избегаем повторений недавно пройденных сценариев
        recent_scenarios = [attempt.get('scenario_id') for attempt in user_profile.performance_history[-5:]]
        if scenario.get('id') in recent_scenarios:
            relevance_score -= 2.0
        
        return max(0.0, relevance_score)
    
    def _scenario_addresses_skill(self, scenario_data: Dict, skill_area: str) -> bool:
        """Проверяет, развивает ли сценарий определенный навык"""
        # Простая эвристика на основе ключевых слов в сценарии
        skill_keywords = {
            'diagnosis': ['диагност', 'симптом', 'признак', 'исследован'],
            'communication': ['объясн', 'сообщ', 'расскаж', 'вопрос'],
            'empathy': ['беспокой', 'волн', 'страх', 'поддерж'],
            'treatment_planning': ['лечен', 'план', 'терап', 'процедур']
        }
        
        keywords = skill_keywords.get(skill_area, [])
        scenario_text = json.dumps(scenario_data).lower()
        
        return any(keyword in scenario_text for keyword in keywords)
    
    def _assess_scenario_difficulty(self, scenario_data: Dict) -> float:
        """Оценивает сложность сценария"""
        # Упрощенная оценка сложности
        dialogue_nodes = scenario_data.get('dialogue_nodes', [])
        
        complexity_factors = {
            'num_nodes': len(dialogue_nodes),
            'avg_options': np.mean([len(node.get('options', [])) for node in dialogue_nodes]) if dialogue_nodes else 0,
            'score_variance': 0  # Можно добавить анализ разброса баллов
        }
        
        # Простая формула сложности
        difficulty = (complexity_factors['num_nodes'] * 0.1 + 
                     complexity_factors['avg_options'] * 0.3)
        
        return min(4.0, max(1.0, difficulty))  # Ограничиваем 1-4
    
    def _scenario_matches_learning_style(self, scenario_data: Dict, learning_style: LearningStyle) -> bool:
        """Проверяет соответствие сценария стилю обучения"""
        # Эвристики для разных стилей обучения
        if learning_style == LearningStyle.VISUAL:
            # Проверяем наличие изображений или визуальных элементов
            return 'image' in json.dumps(scenario_data) or 'visual' in json.dumps(scenario_data)
        
        elif learning_style == LearningStyle.EMPATHETIC:
            # Проверяем наличие эмоциональных элементов
            return any(emotion in json.dumps(scenario_data) for emotion in ['angry', 'concerned', 'worried', 'happy'])
        
        elif learning_style == LearningStyle.SYSTEMATIC:
            # Проверяем структурированность сценария
            dialogue_nodes = scenario_data.get('dialogue_nodes', [])
            return len(dialogue_nodes) > 5  # Более длинные, структурированные сценарии
        
        return True  # По умолчанию подходит
    
    def _get_recommendation_reason(self, user_profile: UserProfile, scenario: Dict, score: float) -> str:
        """Генерирует объяснение рекомендации"""
        reasons = []
        
        if score >= 3.0:
            weakness_areas = [area for area in user_profile.weakness_areas 
                            if self._scenario_addresses_skill(json.loads(scenario.get('scenario_data', '{}')), area)]
            if weakness_areas:
                reasons.append(f"Поможет улучшить навыки в области: {', '.join(weakness_areas)}")
        
        if score >= 2.0:
            reasons.append("Соответствует вашему текущему уровню")
        
        if self._scenario_matches_learning_style(json.loads(scenario.get('scenario_data', '{}')), user_profile.learning_style):
            reasons.append(f"Подходит для вашего стиля обучения ({user_profile.learning_style.value})")
        
        return '; '.join(reasons) if reasons else "Рекомендуется для общего развития"

    def generate_personalized_hints(self, user_profile: UserProfile, current_node: Dict, scenario_context: Dict) -> List[str]:
        """
        Генерирует персонализированные подсказки на основе профиля пользователя
        
        Args:
            user_profile: Профиль пользователя
            current_node: Текущий узел диалога
            scenario_context: Контекст сценария
            
        Returns:
            List[str]: Список персонализированных подсказок
        """
        hints = []
        
        # Подсказки на основе слабых сторон
        if 'communication' in user_profile.weakness_areas:
            hints.append("💬 Помните о важности активного слушания и эмпатии в общении с пациентом")
        
        if 'diagnosis' in user_profile.weakness_areas:
            hints.append("🔍 Следуйте систематическому подходу: анамнез → осмотр → дополнительные исследования")
        
        if 'empathy' in user_profile.weakness_areas:
            patient_emotion = current_node.get('patient_emotion', 'neutral')
            if patient_emotion in ['angry', 'concerned', 'worried']:
                hints.append("❤️ Пациент выглядит обеспокоенным. Проявите понимание и поддержку")
        
        # Подсказки на основе стиля обучения
        if user_profile.learning_style == LearningStyle.SYSTEMATIC:
            hints.append("📋 Рассмотрите использование стандартного клинического протокола")
        
        elif user_profile.learning_style == LearningStyle.ANALYTICAL:
            hints.append("🧠 Проанализируйте все доступные данные перед принятием решения")
        
        # Контекстуальные подсказки
        if current_node.get('clinical_phase') == 'examination':
            hints.append("👨‍⚕️ При осмотре обращайте внимание на визуальные признаки и пальпацию")
        
        return hints[:3]  # Максимум 3 подсказки, чтобы не перегружать

# Класс для интеграции с существующей системой
class AdaptiveLearningService:
    """Сервис для интеграции адаптивного обучения в приложение"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.engine = AdaptiveLearningEngine()
        self.user_profiles = {}  # Кэш профилей пользователей
    
    def get_user_profile(self, user_id: int) -> UserProfile:
        """Получает профиль пользователя"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            # Обновляем профиль, если он старый (более 7 дней)
            if datetime.utcnow() - profile.last_updated > timedelta(days=7):
                profile = self.update_user_profile(user_id)
        else:
            profile = self.update_user_profile(user_id)
        
        return profile
    
    def update_user_profile(self, user_id: int) -> UserProfile:
        """Обновляет профиль пользователя на основе последних данных"""
        from models import VirtualPatientAttempt
        
        # Получаем последние попытки пользователя (последние 10)
        recent_attempts = self.db.query(VirtualPatientAttempt).filter_by(
            user_id=user_id,
            completed=True
        ).order_by(VirtualPatientAttempt.completed_at.desc()).limit(10).all()
        
        # Преобразуем в нужный формат
        attempts_data = []
        for attempt in recent_attempts:
            attempts_data.append({
                'scenario_id': attempt.scenario_id,
                'score': attempt.score,
                'max_score': attempt.scenario.max_score,
                'dialogue_history': attempt.dialogue_history,
                'completed': attempt.completed,
                'time_spent': attempt.time_spent
            })
        
        # Анализируем и создаем профиль
        profile = self.engine.analyze_user_performance(user_id, attempts_data)
        
        # Кэшируем профиль
        self.user_profiles[user_id] = profile
        
        return profile
    
    def get_scenario_recommendations(self, user_id: int, available_scenarios: List) -> List[Dict]:
        """Получает рекомендации сценариев для пользователя"""
        profile = self.get_user_profile(user_id)
        
        # Преобразуем сценарии в нужный формат
        scenarios_data = []
        for scenario in available_scenarios:
            scenarios_data.append({
                'id': scenario.id,
                'title': scenario.title,
                'scenario_data': scenario.scenario_data,
                'difficulty': scenario.difficulty,
                'category': getattr(scenario, 'category', 'general')
            })
        
        return self.engine.recommend_next_scenarios(profile, scenarios_data)
    
    def get_personalized_hints(self, user_id: int, current_node: Dict, scenario_context: Dict) -> List[str]:
        """Получает персонализированные подсказки"""
        profile = self.get_user_profile(user_id)
        return self.engine.generate_personalized_hints(profile, current_node, scenario_context)