# utils/virtual_patient_analytics.py
"""
Функции для анализа результатов виртуальных пациентов
"""

import json
from typing import Dict, List, Any
from datetime import datetime

def calculate_empathy_score(history: Dict) -> int:
    """
    Рассчитывает оценку эмпатии на основе принятых решений
    
    Args:
        history: История диалога с решениями
        
    Returns:
        int: Оценка эмпатии (0-100)
    """
    decisions = history.get('decisions', [])
    if not decisions:
        return 0
    
    empathy_points = 0
    empathy_decisions = 0
    
    for decision in decisions:
        if 'factors' in decision and 'empathy' in decision['factors']:
            empathy_factor = decision['factors']['empathy']
            empathy_decisions += 1
            
            if empathy_factor >= 1.1:
                empathy_points += 100
            elif empathy_factor >= 1.0:
                empathy_points += 80
            elif empathy_factor >= 0.9:
                empathy_points += 60
            else:
                empathy_points += 30
    
    if empathy_decisions == 0:
        return 70  # Средняя оценка, если нет данных об эмпатии
    
    return min(100, empathy_points // empathy_decisions)

def calculate_clinical_score(history: Dict) -> int:
    """
    Рассчитывает оценку клинических навыков
    
    Args:
        history: История диалога с решениями
        
    Returns:
        int: Оценка клинических навыков (0-100)
    """
    decisions = history.get('decisions', [])
    if not decisions:
        return 0
    
    clinical_points = 0
    total_decisions = len(decisions)
    
    for decision in decisions:
        if 'factors' in decision and 'consistency' in decision['factors']:
            consistency_factor = decision['factors']['consistency']
            
            if consistency_factor >= 1.2:
                clinical_points += 100
            elif consistency_factor >= 1.1:
                clinical_points += 85
            elif consistency_factor >= 1.0:
                clinical_points += 70
            elif consistency_factor >= 0.9:
                clinical_points += 55
            else:
                clinical_points += 30
        else:
            # Базовая оценка по баллам
            base_score = decision.get('base_score', 0)
            if base_score > 10:
                clinical_points += 90
            elif base_score > 5:
                clinical_points += 75
            elif base_score > 0:
                clinical_points += 60
            else:
                clinical_points += 30
    
    return min(100, clinical_points // total_decisions) if total_decisions > 0 else 0

def calculate_communication_score(history: Dict) -> int:
    """
    Рассчитывает оценку коммуникативных навыков
    
    Args:
        history: История диалога с решениями
        
    Returns:
        int: Оценка коммуникации (0-100)
    """
    decisions = history.get('decisions', [])
    if not decisions:
        return 0
    
    communication_keywords = [
        'объясни', 'расскажи', 'понимаю', 'сочувствую', 'выслушать',
        'согласие', 'информирован', 'вопрос', 'беспокойство'
    ]
    
    communication_points = 0
    total_decisions = len(decisions)
    
    for decision in decisions:
        option_text = decision.get('option_text', '').lower()
        
        # Проверяем наличие коммуникативных ключевых слов
        keyword_bonus = sum(1 for keyword in communication_keywords if keyword in option_text)
        
        # Базовая оценка
        base_points = 50
        
        # Бонус за коммуникативные слова
        base_points += min(30, keyword_bonus * 10)
        
        # Учитываем баллы решения
        if decision.get('final_score', 0) > 0:
            base_points += 20
        
        communication_points += min(100, base_points)
    
    return min(100, communication_points // total_decisions) if total_decisions > 0 else 0

def calculate_efficiency_score(history: Dict, total_time_spent: float) -> int:
    """
    Рассчитывает оценку эффективности
    
    Args:
        history: История диалога
        total_time_spent: Общее время, потраченное на сценарий (секунды)
        
    Returns:
        int: Оценка эффективности (0-100)
    """
    decisions = history.get('decisions', [])
    decision_times = history.get('decision_times', [])
    
    if not decisions or not decision_times:
        return 70  # Средняя оценка по умолчанию
    
    # Идеальное время для принятия решения (секунды)
    ideal_time_per_decision = 25
    
    # Рассчитываем среднее время принятия решения
    avg_decision_time = sum(decision_times) / len(decision_times)
    
    # Оценка на основе времени принятия решений
    if avg_decision_time <= ideal_time_per_decision:
        time_score = 100
    elif avg_decision_time <= ideal_time_per_decision * 1.5:
        time_score = 85
    elif avg_decision_time <= ideal_time_per_decision * 2:
        time_score = 70
    else:
        time_score = 50
    
    # Учитываем общее время сценария
    ideal_total_time = len(decisions) * ideal_time_per_decision
    if total_time_spent <= ideal_total_time * 1.2:
        total_time_score = 100
    elif total_time_spent <= ideal_total_time * 1.5:
        total_time_score = 80
    else:
        total_time_score = 60
    
    # Комбинированная оценка
    return min(100, int((time_score * 0.6 + total_time_score * 0.4)))

def calculate_decision_quality_score(history: Dict) -> int:
    """
    Рассчитывает качество принятых решений
    
    Args:
        history: История диалога
        
    Returns:
        int: Оценка качества решений (0-100)
    """
    decisions = history.get('decisions', [])
    if not decisions:
        return 0
    
    total_score = sum(decision.get('final_score', 0) for decision in decisions)
    positive_decisions = sum(1 for decision in decisions if decision.get('final_score', 0) > 0)
    
    # Базовая оценка на основе соотношения положительных решений
    positive_ratio = positive_decisions / len(decisions)
    
    if positive_ratio >= 0.8:
        quality_score = 95
    elif positive_ratio >= 0.6:
        quality_score = 80
    elif positive_ratio >= 0.4:
        quality_score = 65
    else:
        quality_score = 40
    
    # Корректировка на основе общего счета
    if total_score > 0:
        quality_score = min(100, quality_score + 10)
    elif total_score < -10:
        quality_score = max(0, quality_score - 20)
    
    return quality_score

def generate_recommendations(history: Dict, final_score: int, max_score: int) -> List[Dict]:
    """
    Генерирует персонализированные рекомендации
    
    Args:
        history: История диалога
        final_score: Финальный счет
        max_score: Максимальный возможный счет
        
    Returns:
        List[Dict]: Список рекомендаций
    """
    recommendations = []
    
    # Рассчитываем метрики
    empathy_score = calculate_empathy_score(history)
    clinical_score = calculate_clinical_score(history)
    communication_score = calculate_communication_score(history)
    efficiency_score = calculate_efficiency_score(history, 0)  # Время не учитываем в рекомендациях
    
    # Рекомендации на основе эмпатии
    if empathy_score < 60:
        recommendations.append({
            'icon': 'heart',
            'title': 'Развитие эмпатии',
            'description': 'Уделите больше внимания эмоциональному состоянию пациента. Покажите понимание и сочувствие.'
        })
    
    # Рекомендации на основе клинических навыков
    if clinical_score < 60:
        recommendations.append({
            'icon': 'stethoscope',
            'title': 'Клинический протокол',
            'description': 'Следуйте систематическому подходу: анамнез → осмотр → диагностика → лечение.'
        })
    
    # Рекомендации на основе коммуникации
    if communication_score < 60:
        recommendations.append({
            'icon': 'chat-dots',
            'title': 'Коммуникативные навыки',
            'description': 'Используйте открытые вопросы, активно слушайте и объясняйте процедуры понятным языком.'
        })
    
    # Рекомендации на основе эффективности
    if efficiency_score < 60:
        recommendations.append({
            'icon': 'clock',
            'title': 'Эффективность решений',
            'description': 'Принимайте решения более уверенно, но не торопитесь с важными диагностическими шагами.'
        })
    
    # Общие рекомендации на основе общего счета
    score_percentage = (final_score / max_score) * 100 if max_score > 0 else 0
    
    if score_percentage < 50:
        recommendations.append({
            'icon': 'book',
            'title': 'Углубленное изучение',
            'description': 'Рекомендуется изучить теоретические основы по данной теме перед повторным прохождением.'
        })
    elif score_percentage < 70:
        recommendations.append({
            'icon': 'arrow-repeat',
            'title': 'Практика',
            'description': 'Попробуйте пройти похожие сценарии для закрепления навыков.'
        })
    else:
        recommendations.append({
            'icon': 'trophy',
            'title': 'Отличная работа!',
            'description': 'Вы показали хороший уровень. Попробуйте более сложные сценарии для дальнейшего развития.'
        })
    
    return recommendations

def analyze_scenario_difficulty(scenario_data: Dict) -> Dict[str, Any]:
    """
    Анализирует сложность сценария
    
    Args:
        scenario_data: Данные сценария
        
    Returns:
        Dict: Анализ сложности
    """
    dialogue_nodes = scenario_data.get('dialogue_nodes', [])
    
    # Подсчитываем различные метрики сложности
    total_nodes = len(dialogue_nodes)
    total_options = sum(len(node.get('options', [])) for node in dialogue_nodes)
    avg_options_per_node = total_options / total_nodes if total_nodes > 0 else 0
    
    # Анализируем распределение баллов
    all_scores = []
    for node in dialogue_nodes:
        for option in node.get('options', []):
            all_scores.append(option.get('score', 0))
    
    score_range = max(all_scores) - min(all_scores) if all_scores else 0
    
    # Определяем уровень сложности
    if total_nodes <= 5 and avg_options_per_node <= 3:
        difficulty = 'easy'
    elif total_nodes <= 10 and avg_options_per_node <= 4:
        difficulty = 'medium'
    else:
        difficulty = 'hard'
    
    return {
        'difficulty': difficulty,
        'total_nodes': total_nodes,
        'total_options': total_options,
        'avg_options_per_node': round(avg_options_per_node, 1),
        'score_range': score_range,
        'estimated_time_minutes': total_nodes * 2  # Примерно 2 минуты на узел
    }

# Jinja2 фильтры для использования в шаблонах
def register_analytics_filters(app):
    """Регистрирует фильтры аналитики в приложении Flask"""
    
    @app.template_filter('empathy_score')
    def empathy_score_filter(history):
        return calculate_empathy_score(history)
    
    @app.template_filter('clinical_score')
    def clinical_score_filter(history):
        return calculate_clinical_score(history)
    
    @app.template_filter('communication_score')
    def communication_score_filter(history):
        return calculate_communication_score(history)
    
    @app.template_filter('efficiency_score')
    def efficiency_score_filter(history, time_spent=0):
        return calculate_efficiency_score(history, time_spent)
    
    @app.template_filter('decision_quality_score')
    def decision_quality_score_filter(history):
        return calculate_decision_quality_score(history)
    
    @app.template_global('generate_recommendations')
    def recommendations_global(history, final_score, max_score):
        return generate_recommendations(history, final_score, max_score)
    
    @app.template_global('calculate_empathy_score')
    def empathy_score_global(history):
        return calculate_empathy_score(history)
    
    @app.template_global('calculate_clinical_score')
    def clinical_score_global(history):
        return calculate_clinical_score(history)
    
    @app.template_global('calculate_communication_score')
    def communication_score_global(history):
        return calculate_communication_score(history)
    
    @app.template_global('calculate_efficiency_score')
    def efficiency_score_global(history, time_spent=0):
        return calculate_efficiency_score(history, time_spent)
    
    @app.template_global('calculate_decision_quality_score')
    def decision_quality_score_global(history):
        return calculate_decision_quality_score(history)