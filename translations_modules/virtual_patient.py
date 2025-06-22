# Импортируем базовые переводы
from translations import translations

# Определяем переводы для страницы результатов
RESULTS_PAGE = {
    "en": {
        "clinical_case_analysis": "Clinical Case Analysis",
        "overall_performance": "Overall Performance",
        "points": "Points",
        "total_score": "Total Score",
        "decisions_made": "Decisions Made",
        "scenario_time": "Scenario Time",
        "avg_decision_time": "Average Decision Time",
        "total_score_tooltip": "Your total score for this scenario",
        "decisions_made_tooltip": "Number of decisions you made",
        "scenario_time_tooltip": "Time spent on the scenario",
        "avg_decision_time_tooltip": "Average time per decision",
        "decision_timeline": "Decision Timeline",
        "points_for_decision": "Points for this decision",
        "completion_rewards": "Completion Rewards",
        "xp_for_completion_tooltip": "Experience points earned",
        "current_level_tooltip": "Your current level",
        "completed_scenarios_tooltip": "Total scenarios completed",
        "experience_points": "Experience Points",
        "your_level": "Your Level",
        "scenarios_completed": "Scenarios Completed",
        "to_level": "To Level",
        "competency_analysis": "Competency Analysis",
        "empathy": "Empathy",
        "clinical_skills": "Clinical Skills",
        "communication": "Communication",
        "empathy_tooltip": "Your empathy score",
        "clinical_skills_tooltip": "Your clinical skills score",
        "communication_tooltip": "Your communication score",
        "system_loaded": "System loaded",
        "system_load_error": "Error loading system",
        "efficiency": "Efficiency",
        "decision_quality": "Decision Quality",
        "your_results": "Your Results",
        "reward_received": "Reward Received"
    },
    "ru": {
        "clinical_case_analysis": "Анализ клинического случая",
        "overall_performance": "Общая производительность",
        "points": "Баллы",
        "total_score": "Общий счет",
        "decisions_made": "Принятые решения",
        "scenario_time": "Время сценария",
        "avg_decision_time": "Среднее время решения",
        "total_score_tooltip": "Ваш общий счет за этот сценарий",
        "decisions_made_tooltip": "Количество принятых решений",
        "scenario_time_tooltip": "Время, затраченное на сценарий",
        "avg_decision_time_tooltip": "Среднее время на решение",
        "decision_timeline": "Временная шкала решений",
        "points_for_decision": "Баллы за это решение",
        "completion_rewards": "Награды за завершение",
        "xp_for_completion_tooltip": "Полученные очки опыта",
        "current_level_tooltip": "Ваш текущий уровень",
        "completed_scenarios_tooltip": "Всего завершенных сценариев",
        "experience_points": "Очки опыта",
        "your_level": "Ваш уровень",
        "scenarios_completed": "Завершенные сценарии",
        "to_level": "До уровня",
        "competency_analysis": "Анализ компетенций",
        "empathy": "Эмпатия",
        "clinical_skills": "Клинические навыки",
        "communication": "Коммуникация",
        "empathy_tooltip": "Ваш счет по эмпатии",
        "clinical_skills_tooltip": "Ваш счет по клиническим навыкам",
        "communication_tooltip": "Ваш счет по коммуникации",
        "system_loaded": "Система загружена",
        "system_load_error": "Ошибка загрузки системы",
        "efficiency": "Эффективность",
        "decision_quality": "Качество решений",
        "your_results": "Ваши результаты",
        "reward_received": "Награда получена"
    }
}

# Обновляем базовые переводы
for lang in RESULTS_PAGE:
    if lang not in translations:
        translations[lang] = {}
    translations[lang].update(RESULTS_PAGE[lang])

# Экспортируем оптимизированные переводы
optimized_translations = translations