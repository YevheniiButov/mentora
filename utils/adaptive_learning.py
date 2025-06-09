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
import logging

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

    # ===== НОВЫЕ ML ПРЕДСКАЗАНИЯ (расширение существующей системы) =====
    
    def predict_big_exam_success(self, user_id: int) -> Dict[str, Any]:
        """
        Предсказание успеха на BIG экзамене
        Использует существующие данные + новые метрики
        """
        try:
            # Логгер для отладки
            self.logger = getattr(self, 'logger', logging.getLogger(__name__))
            
            # Получаем существующий анализ
            from models import VirtualPatientAttempt, UserProgress, TestAttempt
            
            # Получаем данные пользователя
            recent_attempts_data = self._get_user_attempts_data(user_id)
            if not recent_attempts_data:
                return self._fallback_prediction()
            
            user_profile = self.analyze_user_performance(user_id, recent_attempts_data)
            
            # Собираем расширенные метрики
            extended_metrics = self._collect_extended_metrics(user_id)
            
            # Рассчитываем вероятность успеха
            success_probability = self._calculate_success_probability(
                user_profile, recent_attempts_data, extended_metrics
            )
            
            # Определяем слабые области
            weak_areas = self._identify_exam_weak_areas(user_id, user_profile)
            
            # Генерируем рекомендации
            recommendations = self._generate_exam_recommendations(
                weak_areas, success_probability, user_profile
            )
            
            return {
                'success_probability': success_probability,
                'confidence_level': self._calculate_confidence(user_id, extended_metrics),
                'weak_areas': weak_areas,
                'recommendations': recommendations,
                'optimal_exam_date': self._suggest_optimal_exam_date(user_id, user_profile),
                'required_study_hours': self._estimate_study_hours(user_id, user_profile),
                'emotional_state': self._analyze_emotional_state(user_id, recent_attempts_data),
                'readiness_score': self._calculate_readiness_score(user_profile, extended_metrics),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"BIG exam prediction error for user {user_id}: {e}")
            return self._fallback_prediction()
    
    def _get_user_attempts_data(self, user_id: int) -> List[Dict]:
        """Получает данные попыток пользователя"""
        try:
            from models import db, VirtualPatientAttempt
            
            # Получаем последние 20 попыток
            attempts = db.session.query(VirtualPatientAttempt).filter_by(
                user_id=user_id,
                completed=True
            ).order_by(VirtualPatientAttempt.completed_at.desc()).limit(20).all()
            
            attempts_data = []
            for attempt in attempts:
                attempts_data.append({
                    'scenario_id': attempt.scenario_id,
                    'score': attempt.score,
                    'max_score': attempt.max_score or 100,
                    'dialogue_history': attempt.dialogue_history or '{}',
                    'completed': attempt.completed,
                    'time_spent': attempt.time_spent or 0,
                    'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
                })
            
            return attempts_data
            
        except Exception as e:
            self.logger.error(f"Error getting user attempts data: {e}")
            return []
    
    def _collect_extended_metrics(self, user_id: int) -> Dict[str, float]:
        """Собирает расширенные метрики для ML предсказаний"""
        try:
            from models import db, UserProgress, TestAttempt, VirtualPatientAttempt
            
            metrics = {
                'total_study_sessions': 0,
                'avg_session_duration': 0,
                'consistency_score': 0,
                'improvement_rate': 0,
                'test_performance': 0,
                'virtual_patient_performance': 0,
                'recent_activity_level': 0,
                'streak_days': 0
            }
            
            # Общий прогресс обучения
            total_progress = db.session.query(UserProgress).filter_by(
                user_id=user_id, completed=True
            ).count()
            
            # Тестовые результаты за последние 30 дней
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_tests = db.session.query(TestAttempt).filter(
                TestAttempt.user_id == user_id,
                TestAttempt.attempt_date >= thirty_days_ago
            ).all()
            
            if recent_tests:
                correct_answers = sum(1 for test in recent_tests if test.is_correct)
                metrics['test_performance'] = correct_answers / len(recent_tests)
            
            # Виртуальные пациенты за последние 30 дней
            recent_vp = db.session.query(VirtualPatientAttempt).filter(
                VirtualPatientAttempt.user_id == user_id,
                VirtualPatientAttempt.completed_at >= thirty_days_ago,
                VirtualPatientAttempt.completed == True
            ).all()
            
            if recent_vp:
                avg_vp_score = np.mean([
                    (attempt.score / (attempt.max_score or 100)) 
                    for attempt in recent_vp 
                    if attempt.max_score and attempt.max_score > 0
                ])
                metrics['virtual_patient_performance'] = avg_vp_score
                
                # Расчет стабильности (низкое стандартное отклонение = высокая стабильность)
                vp_scores = [
                    (attempt.score / (attempt.max_score or 100)) 
                    for attempt in recent_vp 
                    if attempt.max_score and attempt.max_score > 0
                ]
                if len(vp_scores) > 1:
                    metrics['consistency_score'] = 1.0 - min(1.0, np.std(vp_scores))
                
                # Уровень активности
                metrics['recent_activity_level'] = min(1.0, len(recent_vp) / 10.0)  # Нормализуем к 10 попыткам
            
            # Общие метрики
            metrics['total_study_sessions'] = total_progress
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting extended metrics: {e}")
            return {key: 0.0 for key in [
                'total_study_sessions', 'avg_session_duration', 'consistency_score',
                'improvement_rate', 'test_performance', 'virtual_patient_performance',
                'recent_activity_level', 'streak_days'
            ]}
    
    def _calculate_success_probability(self, user_profile: UserProfile, 
                                     performance_data: List[Dict], 
                                     metrics: Dict[str, float]) -> float:
        """Рассчитывает вероятность успеха на основе всех данных"""
        try:
            # Базовая вероятность на основе навыков
            skill_score = 0.0
            skill_count = 0
            
            for skill_area, skill_level in user_profile.skill_levels.items():
                if skill_level == SkillLevel.EXPERT:
                    skill_score += 4.0
                elif skill_level == SkillLevel.ADVANCED:
                    skill_score += 3.0
                elif skill_level == SkillLevel.INTERMEDIATE:
                    skill_score += 2.0
                else:  # BEGINNER
                    skill_score += 1.0
                skill_count += 1
            
            avg_skill_score = skill_score / max(1, skill_count)
            base_probability = min(0.9, avg_skill_score / 4.0)  # Нормализуем к 0-0.9
            
            # Корректировки на основе метрик
            performance_bonus = 0.0
            
            # Бонус за хорошие результаты в тестах
            if metrics['test_performance'] > 0.8:
                performance_bonus += 0.1
            elif metrics['test_performance'] > 0.6:
                performance_bonus += 0.05
            
            # Бонус за виртуальных пациентов
            if metrics['virtual_patient_performance'] > 0.8:
                performance_bonus += 0.1
            elif metrics['virtual_patient_performance'] > 0.6:
                performance_bonus += 0.05
            
            # Бонус за стабильность
            if metrics['consistency_score'] > 0.8:
                performance_bonus += 0.05
            
            # Бонус за активность
            if metrics['recent_activity_level'] > 0.7:
                performance_bonus += 0.05
            
            # Штраф за слабые области
            weakness_penalty = len(user_profile.weakness_areas) * 0.05
            
            # Финальная вероятность
            final_probability = base_probability + performance_bonus - weakness_penalty
            
            return max(0.1, min(0.95, final_probability))  # Ограничиваем 10%-95%
            
        except Exception as e:
            self.logger.error(f"Error calculating success probability: {e}")
            return 0.5  # Средняя вероятность как fallback
    
    def _identify_exam_weak_areas(self, user_id: int, user_profile: UserProfile) -> List[Dict]:
        """Определяет слабые области для BIG экзамена"""
        try:
            weak_areas_detailed = []
            
            # Анализируем слабые области из профиля
            for weakness in user_profile.weakness_areas:
                area_info = {
                    'area': weakness,
                    'severity': 'high',
                    'description': self._get_weakness_description(weakness),
                    'improvement_suggestions': self._get_improvement_suggestions(weakness)
                }
                weak_areas_detailed.append(area_info)
            
            # Добавляем области со средними навыками как потенциальные улучшения
            for area, skill_level in user_profile.skill_levels.items():
                if area not in user_profile.weakness_areas and skill_level in [SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE]:
                    area_info = {
                        'area': area,
                        'severity': 'medium' if skill_level == SkillLevel.INTERMEDIATE else 'high',
                        'description': self._get_weakness_description(area),
                        'improvement_suggestions': self._get_improvement_suggestions(area)
                    }
                    weak_areas_detailed.append(area_info)
            
            return weak_areas_detailed[:5]  # Максимум 5 областей
            
        except Exception as e:
            self.logger.error(f"Error identifying exam weak areas: {e}")
            return []
    
    def _get_weakness_description(self, area: str) -> str:
        """Получает описание слабой области"""
        descriptions = {
            'diagnosis': 'Диагностические навыки требуют улучшения. Важно развивать систематический подход к постановке диагноза.',
            'communication': 'Коммуникативные навыки нуждаются в развитии. Работайте над активным слушанием и эмпатией.',
            'empathy': 'Эмпатические навыки можно улучшить. Больше внимания к эмоциональному состоянию пациентов.',
            'clinical_reasoning': 'Клиническое мышление требует практики. Развивайте логическое обоснование решений.',
            'patient_management': 'Навыки управления пациентами нуждаются в улучшении.',
            'treatment_planning': 'Планирование лечения требует более глубокого изучения.',
            'emergency_response': 'Навыки экстренного реагирования нужно развивать.'
        }
        return descriptions.get(area, f'Область {area} требует дополнительного внимания.')
    
    def _get_improvement_suggestions(self, area: str) -> List[str]:
        """Получает предложения по улучшению"""
        suggestions = {
            'diagnosis': [
                'Практикуйте систематический сбор анамнеза',
                'Изучите дифференциальную диагностику',
                'Больше работайте с клиническими случаями'
            ],
            'communication': [
                'Практикуйте активное слушание',
                'Работайте над разъяснением сложных терминов',
                'Развивайте навыки невербального общения'
            ],
            'empathy': [
                'Обращайте внимание на эмоции пациентов',
                'Практикуйте эмпатичные ответы',
                'Изучите психологию пациентов'
            ]
        }
        return suggestions.get(area, ['Уделите больше времени практике в этой области'])
    
    def _generate_exam_recommendations(self, weak_areas: List[Dict], 
                                     probability: float, 
                                     user_profile: UserProfile) -> List[Dict]:
        """Генерирует персональные рекомендации для подготовки"""
        try:
            recommendations = []
            
            # Рекомендации на основе вероятности успеха
            if probability < 0.4:
                recommendations.append({
                    'type': 'urgent',
                    'title': 'Интенсивная подготовка необходима',
                    'description': 'Рекомендуется увеличить время изучения и сосредоточиться на слабых областях',
                    'priority': 'high'
                })
            elif probability < 0.7:
                recommendations.append({
                    'type': 'improvement',
                    'title': 'Продолжайте активную подготовку',
                    'description': 'Вы на правильном пути, но есть области для улучшения',
                    'priority': 'medium'
                })
            else:
                recommendations.append({
                    'type': 'maintenance',
                    'title': 'Поддерживайте текущий уровень',
                    'description': 'Отличные результаты! Продолжайте регулярную практику',
                    'priority': 'low'
                })
            
            # Рекомендации по слабым областям
            for weak_area in weak_areas[:3]:  # Топ 3 слабые области
                recommendations.append({
                    'type': 'skill_improvement',
                    'title': f'Улучшить навыки: {weak_area["area"]}',
                    'description': weak_area['description'],
                    'suggestions': weak_area['improvement_suggestions'],
                    'priority': weak_area['severity']
                })
            
            # Рекомендации по стилю обучения
            style_rec = self._get_learning_style_recommendation(user_profile.learning_style)
            if style_rec:
                recommendations.append(style_rec)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating exam recommendations: {e}")
            return [{'type': 'general', 'title': 'Продолжайте обучение', 'description': 'Регулярная практика - ключ к успеху'}]
    
    def _get_learning_style_recommendation(self, learning_style: LearningStyle) -> Dict:
        """Получает рекомендацию на основе стиля обучения"""
        style_recommendations = {
            LearningStyle.VISUAL: {
                'type': 'learning_style',
                'title': 'Используйте визуальные материалы',
                'description': 'Изучайте диаграммы, рентгеновские снимки и анатомические атласы',
                'priority': 'medium'
            },
            LearningStyle.ANALYTICAL: {
                'type': 'learning_style',
                'title': 'Углубленный анализ случаев',
                'description': 'Детально разбирайте сложные клинические случаи и изучайте исследования',
                'priority': 'medium'
            },
            LearningStyle.SYSTEMATIC: {
                'type': 'learning_style',
                'title': 'Следуйте протоколам',
                'description': 'Изучайте клинические руководства и стандартные процедуры',
                'priority': 'medium'
            },
            LearningStyle.EMPATHETIC: {
                'type': 'learning_style',
                'title': 'Практика общения с пациентами',
                'description': 'Больше времени уделяйте сценариям с эмоциональными пациентами',
                'priority': 'medium'
            }
        }
        return style_recommendations.get(learning_style, None)
    
    def _suggest_optimal_exam_date(self, user_id: int, user_profile: UserProfile) -> Optional[str]:
        """Предлагает оптимальную дату экзамена"""
        try:
            # Базовое время подготовки в зависимости от навыков
            required_hours = self._estimate_study_hours(user_id, user_profile)
            
            # Предполагаем 10 часов обучения в неделю
            hours_per_week = 10
            weeks_needed = max(4, int(required_hours / hours_per_week))
            
            # Добавляем буферное время
            buffer_weeks = 2
            total_weeks = weeks_needed + buffer_weeks
            
            optimal_date = datetime.utcnow() + timedelta(weeks=total_weeks)
            
            return optimal_date.strftime('%Y-%m-%d')
            
        except Exception as e:
            self.logger.error(f"Error suggesting optimal exam date: {e}")
            return None
    
    def _estimate_study_hours(self, user_id: int, user_profile: UserProfile) -> int:
        """Оценивает необходимое время для подготовки"""
        try:
            base_hours = 80  # Базовое время для подготовки
            
            # Корректировка на основе навыков
            skill_adjustment = 0
            for skill_level in user_profile.skill_levels.values():
                if skill_level == SkillLevel.EXPERT:
                    skill_adjustment -= 10
                elif skill_level == SkillLevel.ADVANCED:
                    skill_adjustment -= 5
                elif skill_level == SkillLevel.BEGINNER:
                    skill_adjustment += 15
                # INTERMEDIATE не изменяет базовое время
            
            # Дополнительное время для слабых областей
            weakness_hours = len(user_profile.weakness_areas) * 10
            
            # Корректировка на стиль обучения
            style_adjustment = 0
            if user_profile.learning_style == LearningStyle.ANALYTICAL:
                style_adjustment += 20  # Больше времени на глубокий анализ
            elif user_profile.learning_style == LearningStyle.INTUITIVE:
                style_adjustment -= 10  # Быстрее усваивает информацию
            
            total_hours = base_hours + skill_adjustment + weakness_hours + style_adjustment
            
            return max(40, min(200, total_hours))  # Ограничиваем 40-200 часов
            
        except Exception as e:
            self.logger.error(f"Error estimating study hours: {e}")
            return 100  # Среднее время как fallback
    
    def _analyze_emotional_state(self, user_id: int, attempts_data: List[Dict]) -> Dict[str, Any]:
        """Анализирует эмоциональное состояние пользователя во время обучения"""
        try:
            if not attempts_data:
                return {'state': 'neutral', 'confidence': 0.3, 'trends': []}
            
            # Анализируем паттерны в данных
            performance_trend = []
            time_patterns = []
            
            for attempt in attempts_data:
                if attempt.get('max_score', 0) > 0:
                    score_ratio = attempt['score'] / attempt['max_score']
                    performance_trend.append(score_ratio)
                
                time_spent = attempt.get('time_spent', 0)
                if time_spent > 0:
                    time_patterns.append(time_spent)
            
            emotional_indicators = {
                'performance_variance': np.std(performance_trend) if performance_trend else 0,
                'average_performance': np.mean(performance_trend) if performance_trend else 0,
                'time_consistency': 1.0 - (np.std(time_patterns) / np.mean(time_patterns)) if time_patterns and np.mean(time_patterns) > 0 else 0,
                'recent_trend': self._calculate_recent_trend(performance_trend)
            }
            
            # Определяем эмоциональное состояние
            emotional_state = self._determine_emotional_state(emotional_indicators)
            
            return {
                'state': emotional_state['state'],
                'confidence': emotional_state['confidence'],
                'indicators': emotional_indicators,
                'suggestions': emotional_state['suggestions'],
                'trends': self._analyze_performance_trends(performance_trend)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing emotional state: {e}")
            return {'state': 'neutral', 'confidence': 0.3, 'trends': [], 'suggestions': []}
    
    def _calculate_recent_trend(self, performance_data: List[float]) -> str:
        """Рассчитывает тренд последних результатов"""
        if len(performance_data) < 3:
            return 'insufficient_data'
        
        recent_half = performance_data[-len(performance_data)//2:]
        early_half = performance_data[:len(performance_data)//2]
        
        recent_avg = np.mean(recent_half)
        early_avg = np.mean(early_half)
        
        if recent_avg > early_avg + 0.1:
            return 'improving'
        elif recent_avg < early_avg - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _determine_emotional_state(self, indicators: Dict) -> Dict[str, Any]:
        """Определяет эмоциональное состояние на основе индикаторов"""
        performance = indicators['average_performance']
        variance = indicators['performance_variance']
        trend = indicators['recent_trend']
        
        if performance > 0.8 and variance < 0.15 and trend in ['improving', 'stable']:
            return {
                'state': 'confident',
                'confidence': 0.8,
                'suggestions': ['Отличная работа! Продолжайте в том же духе', 'Рассмотрите более сложные задачи']
            }
        elif performance < 0.4 or variance > 0.3 or trend == 'declining':
            return {
                'state': 'stressed',
                'confidence': 0.7,
                'suggestions': ['Сделайте перерыв для восстановления', 'Вернитесь к более простым задачам', 'Рассмотрите изменение подхода к обучению']
            }
        elif trend == 'improving':
            return {
                'state': 'motivated',
                'confidence': 0.7,
                'suggestions': ['Ваш прогресс очевиден!', 'Продолжайте увеличивать сложность постепенно']
            }
        else:
            return {
                'state': 'neutral',
                'confidence': 0.5,
                'suggestions': ['Поддерживайте регулярную практику', 'Попробуйте варьировать типы заданий']
            }
    
    def _analyze_performance_trends(self, performance_data: List[float]) -> List[Dict]:
        """Анализирует тренды производительности"""
        if len(performance_data) < 5:
            return []
        
        trends = []
        
        # Анализ последних 5 попыток
        recent_5 = performance_data[-5:]
        avg_recent = np.mean(recent_5)
        
        if avg_recent > 0.8:
            trends.append({'type': 'positive', 'description': 'Стабильно высокие результаты'})
        elif avg_recent < 0.4:
            trends.append({'type': 'concerning', 'description': 'Низкие результаты требуют внимания'})
        
        # Анализ стабильности
        std_recent = np.std(recent_5)
        if std_recent < 0.1:
            trends.append({'type': 'stable', 'description': 'Стабильная производительность'})
        elif std_recent > 0.3:
            trends.append({'type': 'volatile', 'description': 'Неустойчивые результаты'})
        
        return trends
    
    def _calculate_confidence(self, user_id: int, metrics: Dict[str, float]) -> float:
        """Рассчитывает уровень уверенности в предсказании"""
        try:
            confidence_factors = {
                'data_availability': min(1.0, metrics.get('total_study_sessions', 0) / 20.0),
                'recent_activity': metrics.get('recent_activity_level', 0),
                'consistency': metrics.get('consistency_score', 0),
                'test_data': 1.0 if metrics.get('test_performance', 0) > 0 else 0.3
            }
            
            # Взвешенная сумма факторов
            weights = [0.3, 0.3, 0.2, 0.2]
            confidence = sum(factor * weight for factor, weight in zip(confidence_factors.values(), weights))
            
            return max(0.3, min(0.9, confidence))  # Ограничиваем 30%-90%
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _calculate_readiness_score(self, user_profile: UserProfile, metrics: Dict[str, float]) -> float:
        """Рассчитывает общий балл готовности к экзамену"""
        try:
            # Компоненты готовности
            skill_score = np.mean([
                4.0 if skill == SkillLevel.EXPERT else
                3.0 if skill == SkillLevel.ADVANCED else
                2.0 if skill == SkillLevel.INTERMEDIATE else 1.0
                for skill in user_profile.skill_levels.values()
            ]) / 4.0  # Нормализуем к 0-1
            
            practice_score = min(1.0, metrics.get('recent_activity_level', 0))
            consistency_score = metrics.get('consistency_score', 0)
            test_score = metrics.get('test_performance', 0)
            
            # Штраф за слабые области
            weakness_penalty = len(user_profile.weakness_areas) * 0.1
            
            # Итоговый балл
            readiness = (skill_score * 0.4 + practice_score * 0.2 + 
                        consistency_score * 0.2 + test_score * 0.2) - weakness_penalty
            
            return max(0.0, min(1.0, readiness))
            
        except Exception as e:
            self.logger.error(f"Error calculating readiness score: {e}")
            return 0.5
    
    def _fallback_prediction(self) -> Dict[str, Any]:
        """Базовое предсказание если ML недоступен"""
        return {
            'success_probability': 0.5,
            'confidence_level': 0.3,
            'weak_areas': [],
            'recommendations': [
                {
                    'type': 'general',
                    'title': 'Продолжайте обучение',
                    'description': 'Регулярная практика поможет улучшить ваши навыки',
                    'priority': 'medium'
                }
            ],
            'optimal_exam_date': (datetime.utcnow() + timedelta(weeks=12)).strftime('%Y-%m-%d'),
            'required_study_hours': 100,
            'emotional_state': {'state': 'neutral', 'confidence': 0.3, 'trends': []},
            'readiness_score': 0.5,
            'timestamp': datetime.utcnow().isoformat()
        }

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

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ ML ИНТЕГРАЦИИ =====
    
    def get_big_exam_prediction(self, user_id: int) -> Dict[str, Any]:
        """
        Получает комплексное предсказание готовности к BIG экзамену
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Детальное предсказание с рекомендациями
        """
        try:
            return self.engine.predict_big_exam_success(user_id)
        except Exception as e:
            logging.error(f"Error getting BIG exam prediction for user {user_id}: {e}")
            return self.engine._fallback_prediction()
    
    def get_personalized_study_plan(self, user_id: int, target_exam_date: str = None) -> Dict[str, Any]:
        """
        Создает персонализированный план обучения
        
        Args:
            user_id: ID пользователя
            target_exam_date: Целевая дата экзамена (YYYY-MM-DD)
            
        Returns:
            Dict: Персонализированный план обучения
        """
        try:
            exam_prediction = self.get_big_exam_prediction(user_id)
            profile = self.get_user_profile(user_id)
            
            # Если дата не указана, используем предложенную
            if not target_exam_date:
                target_exam_date = exam_prediction.get('optimal_exam_date')
            
            # Рассчитываем время до экзамена
            if target_exam_date:
                try:
                    exam_date = datetime.strptime(target_exam_date, '%Y-%m-%d')
                    days_until_exam = (exam_date - datetime.utcnow()).days
                except ValueError:
                    days_until_exam = 84  # 12 недель по умолчанию
            else:
                days_until_exam = 84
            
            # Создаем план
            study_plan = {
                'user_id': user_id,
                'target_exam_date': target_exam_date,
                'days_until_exam': max(1, days_until_exam),
                'total_required_hours': exam_prediction.get('required_study_hours', 100),
                'hours_per_week': max(5, exam_prediction.get('required_study_hours', 100) / max(1, days_until_exam // 7)),
                'current_readiness': exam_prediction.get('readiness_score', 0.5),
                'success_probability': exam_prediction.get('success_probability', 0.5),
                'weak_areas': exam_prediction.get('weak_areas', []),
                'weekly_schedule': self._generate_weekly_schedule(profile, exam_prediction, days_until_exam),
                'milestones': self._generate_study_milestones(days_until_exam, exam_prediction),
                'adaptive_adjustments': self._get_adaptive_adjustments(profile, exam_prediction),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return study_plan
            
        except Exception as e:
            logging.error(f"Error creating study plan for user {user_id}: {e}")
            return self._fallback_study_plan(user_id, target_exam_date)
    
    def _generate_weekly_schedule(self, profile: 'UserProfile', prediction: Dict, days_until_exam: int) -> List[Dict]:
        """Генерирует еженедельное расписание обучения"""
        weeks_until_exam = max(1, days_until_exam // 7)
        total_hours = prediction.get('required_study_hours', 100)
        hours_per_week = total_hours / weeks_until_exam
        
        schedule = []
        weak_areas = [area['area'] for area in prediction.get('weak_areas', [])]
        
        for week in range(min(12, weeks_until_exam)):  # Максимум 12 недель
            week_plan = {
                'week_number': week + 1,
                'total_hours': min(25, max(5, hours_per_week)),  # Ограничиваем 5-25 часов в неделю
                'focus_areas': self._get_weekly_focus(week, weeks_until_exam, weak_areas, profile),
                'activities': self._get_weekly_activities(week, weeks_until_exam, profile),
                'assessment': f"Самооценка после недели {week + 1}"
            }
            schedule.append(week_plan)
        
        return schedule
    
    def _get_weekly_focus(self, week: int, total_weeks: int, weak_areas: List[str], profile: 'UserProfile') -> List[str]:
        """Определяет фокус недели"""
        if week < total_weeks * 0.6:  # Первые 60% времени - работа со слабыми областями
            return weak_areas[:2] if weak_areas else ['diagnosis', 'communication']
        elif week < total_weeks * 0.8:  # Следующие 20% - комплексная практика
            return ['clinical_reasoning', 'patient_management']
        else:  # Последние 20% - повторение и закрепление
            return ['review', 'mock_exams']
    
    def _get_weekly_activities(self, week: int, total_weeks: int, profile: 'UserProfile') -> List[Dict]:
        """Определяет активности недели"""
        base_activities = [
            {'type': 'virtual_patients', 'hours': 3, 'description': 'Практика с виртуальными пациентами'},
            {'type': 'learning_cards', 'hours': 2, 'description': 'Изучение образовательных карточек'},
            {'type': 'tests', 'hours': 1, 'description': 'Прохождение тестов'}
        ]
        
        # Адаптируем под стиль обучения
        if profile.learning_style == LearningStyle.VISUAL:
            base_activities.append({'type': 'visual_materials', 'hours': 1, 'description': 'Изучение визуальных материалов'})
        elif profile.learning_style == LearningStyle.ANALYTICAL:
            base_activities.append({'type': 'case_analysis', 'hours': 2, 'description': 'Детальный анализ случаев'})
        elif profile.learning_style == LearningStyle.SYSTEMATIC:
            base_activities.append({'type': 'protocols', 'hours': 1, 'description': 'Изучение протоколов и руководств'})
        
        return base_activities
    
    def _generate_study_milestones(self, days_until_exam: int, prediction: Dict) -> List[Dict]:
        """Генерирует ключевые точки контроля"""
        milestones = []
        weeks_until_exam = max(1, days_until_exam // 7)
        
        # Милестоуны в зависимости от времени до экзамена
        if weeks_until_exam >= 12:  # Долгосрочная подготовка
            milestones = [
                {'week': 4, 'goal': 'Завершить изучение основных слабых областей', 'target_score': 0.6},
                {'week': 8, 'goal': 'Достичь стабильных результатов в тестах', 'target_score': 0.7},
                {'week': 10, 'goal': 'Пройти пробный экзамен', 'target_score': 0.75},
                {'week': 12, 'goal': 'Финальная подготовка и повторение', 'target_score': 0.8}
            ]
        elif weeks_until_exam >= 8:  # Средняя подготовка
            milestones = [
                {'week': 3, 'goal': 'Улучшить основные навыки', 'target_score': 0.65},
                {'week': 6, 'goal': 'Комплексная практика', 'target_score': 0.75},
                {'week': 8, 'goal': 'Готовность к экзамену', 'target_score': 0.8}
            ]
        else:  # Интенсивная подготовка
            milestones = [
                {'week': 2, 'goal': 'Интенсивная работа со слабыми областями', 'target_score': 0.7},
                {'week': weeks_until_exam, 'goal': 'Максимальная готовность', 'target_score': 0.75}
            ]
        
        return milestones
    
    def _get_adaptive_adjustments(self, profile: 'UserProfile', prediction: Dict) -> List[Dict]:
        """Получает рекомендации по адаптации плана"""
        adjustments = []
        
        success_prob = prediction.get('success_probability', 0.5)
        emotional_state = prediction.get('emotional_state', {}).get('state', 'neutral')
        
        if success_prob < 0.4:
            adjustments.append({
                'type': 'intensity',
                'recommendation': 'Увеличить интенсивность обучения на 30%',
                'reason': 'Низкая вероятность успеха требует дополнительных усилий'
            })
        
        if emotional_state == 'stressed':
            adjustments.append({
                'type': 'stress_management',
                'recommendation': 'Добавить техники релаксации и сократить ежедневные сессии',
                'reason': 'Обнаружены признаки стресса'
            })
        
        if emotional_state == 'motivated':
            adjustments.append({
                'type': 'challenge',
                'recommendation': 'Можно увеличить сложность заданий',
                'reason': 'Высокий уровень мотивации позволяет увеличить нагрузку'
            })
        
        # Адаптация под стиль обучения
        if profile.learning_style == LearningStyle.EMPATHETIC:
            adjustments.append({
                'type': 'learning_style',
                'recommendation': 'Больше времени уделить сценариям с эмоциональным аспектом',
                'reason': 'Соответствует эмпатическому стилю обучения'
            })
        
        return adjustments
    
    def _fallback_study_plan(self, user_id: int, target_exam_date: str = None) -> Dict[str, Any]:
        """Базовый план обучения при ошибках"""
        return {
            'user_id': user_id,
            'target_exam_date': target_exam_date or (datetime.utcnow() + timedelta(weeks=12)).strftime('%Y-%m-%d'),
            'days_until_exam': 84,
            'total_required_hours': 100,
            'hours_per_week': 12,
            'current_readiness': 0.5,
            'success_probability': 0.5,
            'weak_areas': [],
            'weekly_schedule': [
                {
                    'week_number': i,
                    'total_hours': 12,
                    'focus_areas': ['general_practice'],
                    'activities': [
                        {'type': 'virtual_patients', 'hours': 4, 'description': 'Практика с виртуальными пациентами'},
                        {'type': 'learning_cards', 'hours': 3, 'description': 'Изучение материалов'},
                        {'type': 'tests', 'hours': 2, 'description': 'Тестирование'}
                    ]
                } for i in range(1, 13)
            ],
            'milestones': [
                {'week': 4, 'goal': 'Базовая подготовка', 'target_score': 0.6},
                {'week': 8, 'goal': 'Углубленная практика', 'target_score': 0.7},
                {'week': 12, 'goal': 'Готовность к экзамену', 'target_score': 0.8}
            ],
            'adaptive_adjustments': [],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def track_study_progress(self, user_id: int, study_session: Dict) -> Dict[str, Any]:
        """
        Отслеживает прогресс обучения и обновляет план
        
        Args:
            user_id: ID пользователя
            study_session: Данные сессии обучения
            
        Returns:
            Dict: Обновленная информация о прогрессе
        """
        try:
            # Получаем текущее предсказание
            current_prediction = self.get_big_exam_prediction(user_id)
            
            # Анализируем сессию
            session_analysis = {
                'session_score': study_session.get('score', 0),
                'time_spent': study_session.get('time_spent', 0),
                'areas_practiced': study_session.get('areas', []),
                'difficulty_level': study_session.get('difficulty', 'medium'),
                'emotional_feedback': study_session.get('emotional_state', 'neutral')
            }
            
            # Обновляем профиль пользователя
            updated_profile = self.update_user_profile(user_id)
            
            # Проверяем, нужна ли адаптация плана
            adaptation_needed = self._check_adaptation_needed(
                current_prediction, session_analysis, updated_profile
            )
            
            return {
                'updated_prediction': current_prediction,
                'session_analysis': session_analysis,
                'adaptation_needed': adaptation_needed,
                'next_recommendations': self._get_next_session_recommendations(
                    updated_profile, session_analysis
                ),
                'progress_trend': self._calculate_progress_trend(user_id),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error tracking study progress for user {user_id}: {e}")
            return {'error': 'Failed to track progress', 'timestamp': datetime.utcnow().isoformat()}
    
    def _check_adaptation_needed(self, prediction: Dict, session: Dict, profile: 'UserProfile') -> Dict[str, Any]:
        """Проверяет, нужна ли адаптация плана обучения"""
        adaptations = []
        
        # Проверяем результаты сессии
        session_score = session.get('session_score', 0)
        if session_score < 0.4:  # Низкие результаты
            adaptations.append({
                'type': 'difficulty_reduction',
                'description': 'Рекомендуется снизить сложность заданий',
                'priority': 'high'
            })
        elif session_score > 0.85:  # Очень высокие результаты
            adaptations.append({
                'type': 'difficulty_increase',
                'description': 'Можно увеличить сложность для лучшего прогресса',
                'priority': 'medium'
            })
        
        # Проверяем эмоциональное состояние
        emotional_state = session.get('emotional_feedback', 'neutral')
        if emotional_state == 'frustrated':
            adaptations.append({
                'type': 'support',
                'description': 'Добавить мотивационную поддержку и перерывы',
                'priority': 'high'
            })
        
        # Проверяем время обучения
        time_spent = session.get('time_spent', 0)
        if time_spent > 120:  # Более 2 часов
            adaptations.append({
                'type': 'session_length',
                'description': 'Рекомендуется сократить длительность сессий',
                'priority': 'medium'
            })
        
        return {
            'needed': len(adaptations) > 0,
            'adaptations': adaptations,
            'confidence': 0.8 if adaptations else 0.3
        }
    
    def _get_next_session_recommendations(self, profile: 'UserProfile', last_session: Dict) -> List[Dict]:
        """Получает рекомендации для следующей сессии"""
        recommendations = []
        
        # Базовые рекомендации на основе последней сессии
        last_score = last_session.get('session_score', 0)
        
        if last_score < 0.5:
            recommendations.append({
                'type': 'review',
                'description': 'Повторите материал из последней сессии',
                'priority': 'high'
            })
        
        # Рекомендации на основе слабых областей
        for weakness in profile.weakness_areas[:2]:  # Топ 2 слабые области
            recommendations.append({
                'type': 'skill_focus',
                'description': f'Сосредоточьтесь на улучшении навыков: {weakness}',
                'priority': 'high'
            })
        
        # Рекомендации по стилю обучения
        if profile.learning_style == LearningStyle.VISUAL:
            recommendations.append({
                'type': 'learning_style',
                'description': 'Используйте визуальные материалы и диаграммы',
                'priority': 'medium'
            })
        elif profile.learning_style == LearningStyle.ANALYTICAL:
            recommendations.append({
                'type': 'learning_style',
                'description': 'Углубленно анализируйте каждый случай',
                'priority': 'medium'
            })
        
        return recommendations[:4]  # Максимум 4 рекомендации
    
    def _calculate_progress_trend(self, user_id: int) -> Dict[str, Any]:
        """Рассчитывает тренд прогресса пользователя"""
        try:
            from models import VirtualPatientAttempt
            
            # Получаем последние 10 попыток
            recent_attempts = self.db.query(VirtualPatientAttempt).filter_by(
                user_id=user_id,
                completed=True
            ).order_by(VirtualPatientAttempt.completed_at.desc()).limit(10).all()
            
            if len(recent_attempts) < 3:
                return {'trend': 'insufficient_data', 'confidence': 0.1}
            
            # Анализируем тренд
            scores = []
            for attempt in reversed(recent_attempts):  # От старых к новым
                if attempt.max_score and attempt.max_score > 0:
                    scores.append(attempt.score / attempt.max_score)
            
            if len(scores) < 3:
                return {'trend': 'insufficient_data', 'confidence': 0.2}
            
            # Простой анализ тренда
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = np.mean(first_half)
            second_avg = np.mean(second_half)
            
            if second_avg > first_avg + 0.1:
                trend = 'improving'
                confidence = 0.8
            elif second_avg < first_avg - 0.1:
                trend = 'declining'
                confidence = 0.8
            else:
                trend = 'stable'
                confidence = 0.6
            
            return {
                'trend': trend,
                'confidence': confidence,
                'recent_average': second_avg,
                'improvement_rate': second_avg - first_avg,
                'consistency': 1.0 - np.std(scores) if len(scores) > 1 else 0.5
            }
            
        except Exception as e:
            logging.error(f"Error calculating progress trend for user {user_id}: {e}")
            return {'trend': 'error', 'confidence': 0.0}