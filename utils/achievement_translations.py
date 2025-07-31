#!/usr/bin/env python3
"""
Achievement Translation Utilities
"""

def get_achievement_translation_key(achievement_name):
    """
    Преобразует название достижения из базы данных в ключ перевода
    """
    # Маппинг названий достижений из базы данных на ключи переводов
    achievement_mapping = {
        # Learning achievements
        'Eerste stappen': 'achievement_first_steps',
        'Op weg': 'achievement_on_the_way',
        'Toegewijde leerling': 'achievement_dedicated_student',
        'Lesgever': 'achievement_teacher',
        'Master student': 'achievement_master_student',
        'Legende': 'achievement_legend',
        
        # Time achievements
        'Studietijd': 'achievement_study_time',
        'Marathonloper': 'achievement_marathon_runner',
        'Tijdmeester': 'achievement_time_master',
        'Eeuwige student': 'achievement_eternal_student',
        
        # Streak achievements
        'Regelmaat': 'achievement_regularity',
        'Leermeester': 'achievement_learning_master',
        'Serie kampioen': 'achievement_streak_champion',
        
        # Special achievements
        'Planner': 'achievement_planner',
        'Doelbereiker': 'achievement_goal_achiever',
        'Klaar voor examen': 'achievement_exam_ready',
        
        # Fallback для неизвестных достижений
        'default': 'achievement_unknown'
    }
    
    return achievement_mapping.get(achievement_name, 'achievement_unknown')

def get_achievement_description_translation_key(achievement_name):
    """
    Преобразует название достижения из базы данных в ключ перевода описания
    """
    # Маппинг названий достижений на ключи переводов описаний
    description_mapping = {
        # Learning achievements
        'Eerste stappen': 'achievement_first_steps_desc',
        'Op weg': 'achievement_on_the_way_desc',
        'Toegewijde leerling': 'achievement_dedicated_student_desc',
        'Lesgever': 'achievement_teacher_desc',
        'Master student': 'achievement_master_student_desc',
        'Legende': 'achievement_legend_desc',
        
        # Time achievements
        'Studietijd': 'achievement_study_time_desc',
        'Marathonloper': 'achievement_marathon_runner_desc',
        'Tijdmeester': 'achievement_time_master_desc',
        'Eeuwige student': 'achievement_eternal_student_desc',
        
        # Streak achievements
        'Regelmaat': 'achievement_regularity_desc',
        'Leermeester': 'achievement_learning_master_desc',
        'Serie kampioen': 'achievement_streak_champion_desc',
        
        # Special achievements
        'Planner': 'achievement_planner_desc',
        'Doelbereiker': 'achievement_goal_achiever_desc',
        'Klaar voor examen': 'achievement_exam_ready_desc',
        
        # Fallback для неизвестных достижений
        'default': 'achievement_unknown_desc'
    }
    
    return description_mapping.get(achievement_name, 'achievement_unknown_desc')

def translate_achievement(achievement_name, lang, t_function):
    """
    Переводит название достижения на указанный язык
    
    Args:
        achievement_name (str): Название достижения из базы данных
        lang (str): Код языка (en, ru, nl, fa, etc.)
        t_function: Функция перевода t(key, lang)
    
    Returns:
        str: Переведенное название достижения
    """
    translation_key = get_achievement_translation_key(achievement_name)
    return t_function(translation_key, lang) or achievement_name

def translate_achievement_description(achievement_name, lang, t_function):
    """
    Переводит описание достижения на указанный язык
    
    Args:
        achievement_name (str): Название достижения из базы данных
        lang (str): Код языка (en, ru, nl, fa, etc.)
        t_function: Функция перевода t(key, lang)
    
    Returns:
        str: Переведенное описание достижения
    """
    translation_key = get_achievement_description_translation_key(achievement_name)
    return t_function(translation_key, lang) or achievement_name 
"""
Achievement Translation Utilities
"""

def get_achievement_translation_key(achievement_name):
    """
    Преобразует название достижения из базы данных в ключ перевода
    """
    # Маппинг названий достижений из базы данных на ключи переводов
    achievement_mapping = {
        # Learning achievements
        'Eerste stappen': 'achievement_first_steps',
        'Op weg': 'achievement_on_the_way',
        'Toegewijde leerling': 'achievement_dedicated_student',
        'Lesgever': 'achievement_teacher',
        'Master student': 'achievement_master_student',
        'Legende': 'achievement_legend',
        
        # Time achievements
        'Studietijd': 'achievement_study_time',
        'Marathonloper': 'achievement_marathon_runner',
        'Tijdmeester': 'achievement_time_master',
        'Eeuwige student': 'achievement_eternal_student',
        
        # Streak achievements
        'Regelmaat': 'achievement_regularity',
        'Leermeester': 'achievement_learning_master',
        'Serie kampioen': 'achievement_streak_champion',
        
        # Special achievements
        'Planner': 'achievement_planner',
        'Doelbereiker': 'achievement_goal_achiever',
        'Klaar voor examen': 'achievement_exam_ready',
        
        # Fallback для неизвестных достижений
        'default': 'achievement_unknown'
    }
    
    return achievement_mapping.get(achievement_name, 'achievement_unknown')

def get_achievement_description_translation_key(achievement_name):
    """
    Преобразует название достижения из базы данных в ключ перевода описания
    """
    # Маппинг названий достижений на ключи переводов описаний
    description_mapping = {
        # Learning achievements
        'Eerste stappen': 'achievement_first_steps_desc',
        'Op weg': 'achievement_on_the_way_desc',
        'Toegewijde leerling': 'achievement_dedicated_student_desc',
        'Lesgever': 'achievement_teacher_desc',
        'Master student': 'achievement_master_student_desc',
        'Legende': 'achievement_legend_desc',
        
        # Time achievements
        'Studietijd': 'achievement_study_time_desc',
        'Marathonloper': 'achievement_marathon_runner_desc',
        'Tijdmeester': 'achievement_time_master_desc',
        'Eeuwige student': 'achievement_eternal_student_desc',
        
        # Streak achievements
        'Regelmaat': 'achievement_regularity_desc',
        'Leermeester': 'achievement_learning_master_desc',
        'Serie kampioen': 'achievement_streak_champion_desc',
        
        # Special achievements
        'Planner': 'achievement_planner_desc',
        'Doelbereiker': 'achievement_goal_achiever_desc',
        'Klaar voor examen': 'achievement_exam_ready_desc',
        
        # Fallback для неизвестных достижений
        'default': 'achievement_unknown_desc'
    }
    
    return description_mapping.get(achievement_name, 'achievement_unknown_desc')

def translate_achievement(achievement_name, lang, t_function):
    """
    Переводит название достижения на указанный язык
    
    Args:
        achievement_name (str): Название достижения из базы данных
        lang (str): Код языка (en, ru, nl, fa, etc.)
        t_function: Функция перевода t(key, lang)
    
    Returns:
        str: Переведенное название достижения
    """
    translation_key = get_achievement_translation_key(achievement_name)
    return t_function(translation_key, lang) or achievement_name

def translate_achievement_description(achievement_name, lang, t_function):
    """
    Переводит описание достижения на указанный язык
    
    Args:
        achievement_name (str): Название достижения из базы данных
        lang (str): Код языка (en, ru, nl, fa, etc.)
        t_function: Функция перевода t(key, lang)
    
    Returns:
        str: Переведенное описание достижения
    """
    translation_key = get_achievement_description_translation_key(achievement_name)
    return t_function(translation_key, lang) or achievement_name 