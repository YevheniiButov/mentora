# routes/virtual_patient_routes.py

from flask import (
    Blueprint, render_template, request, jsonify, session,
    redirect, url_for, flash, current_app, g
)
from flask_babel import gettext as _ # Используем gettext для переводов
from flask_login import login_required, current_user
from models import db, VirtualPatientScenario, VirtualPatientAttempt, Achievement, UserAchievement
import json
from datetime import datetime, timezone, timedelta # Добавлен timedelta, если он используется для started_at fallback
import random
from utils.mobile_detection import get_mobile_detector
from utils.translations import t, DEFAULT_LANGUAGE
from translations_modules.virtual_patient import optimized_translations  # Добавляем импорт

# Определение Blueprint
virtual_patient_bp = Blueprint(
    "virtual_patient_bp", # Это имя должно совпадать с тем, что импортируется в app.py
    __name__,
    url_prefix='/<string:lang>/virtual-patient',
    template_folder='../templates' # Убедитесь, что путь к шаблонам правильный
)

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'ru' # Установите ваш язык по умолчанию

# Новая функция из Шага 7.3 (размещаем после импортов)
def calculate_base_experience_points(score_percentage: float) -> int:
    """Рассчитывает базовые очки опыта за сценарий"""
    if score_percentage >= 90:
        return 50
    elif score_percentage >= 80:
        return 40
    elif score_percentage >= 70:
        return 30
    elif score_percentage >= 60:
        return 25
    elif score_percentage >= 50:
        return 20
    else:
        return 15

@virtual_patient_bp.before_request
def before_request_virtual_patient():
    """Устанавливает язык из URL для этого Blueprint."""
    lang_from_url = request.view_args.get('lang')
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang', DEFAULT_LANGUAGE)
    
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@virtual_patient_bp.context_processor
def inject_lang_virtual_patient():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    return dict(lang=getattr(g, 'lang', DEFAULT_LANGUAGE))

# --- Вспомогательные функции ---

def create_fallback_scenario_data():
    """Создает структуру данных сценария по умолчанию при ошибках загрузки."""
    current_app.logger.warning("Using fallback scenario data due to a previous error.")
    return {
        "patient_info": {
            "name": _("Error Patient"),
            "medical_history": _("Patient data loading error.")
        },
        "initial_state": {
            "patient_statement": _("Error: Could not load initial patient statement."),
            "patient_emotion": "concerned",
            "notes": _("Please contact support.")
        },
        "dialogue_nodes": [{
            "id": "error_node",
            "title": _("Error Node"),
            "patient_statement": _("An error occurred in the scenario. Please try again or contact support."),
            "patient_emotion": "confused",
            "is_final": True,
            "options": []
        }],
        "outcomes": {
            "good": {"title": _("Good Outcome (Error)"), "text": _("Scenario completed despite errors.")},
            "average": {"title": _("Average Outcome (Error)"), "text": _("Scenario completed with issues.")},
            "poor": {"title": _("Poor Outcome (Error)"), "text": _("Scenario could not be properly evaluated.")}
        }
    }

def find_current_node(scenario_data_for_lang, current_node_id, history):
    """
    Находит текущий узел диалога в данных для конкретного языка.
    """
    if not scenario_data_for_lang:
        current_app.logger.error(f"Cannot find current node: scenario_data_for_lang is empty. Node ID: {current_node_id}")
        return {
            "id": "error_empty_lang_data",
            "patient_statement": _("Error: Language data for scenario is missing."),
            "patient_emotion": "confused",
            "is_final": True,
            "options": []
        }

    if current_node_id == "start":
        initial_state = scenario_data_for_lang.get("initial_state", {})
        options_for_start_node = []
        dialogue_nodes = scenario_data_for_lang.get("dialogue_nodes", [])
        if dialogue_nodes and len(dialogue_nodes) > 0:
            first_dialogue_node = dialogue_nodes[0]
            options_for_start_node = first_dialogue_node.get("options", [])
        
        return {
            "id": "start",
            "title": _("Initial State"),
            "patient_statement": initial_state.get("patient_statement", _("Welcome to the scenario!")),
            "patient_emotion": initial_state.get("patient_emotion", "neutral"),
            "notes": initial_state.get("notes", ""),
            "is_final": False,
            "options": options_for_start_node
        }

    for node in scenario_data_for_lang.get("dialogue_nodes", []):
        if node.get("id") == current_node_id:
            return node
    
    current_app.logger.warning(f"Node with ID '{current_node_id}' not found in language-specific scenario data. History: {history}")
    return {
        "id": "error_node_not_found",
        "title": _("Error: Node Not Found"),
        "patient_statement": _("Error: Dialogue node not found. Please check scenario configuration or contact support."),
        "patient_emotion": "confused",
        "is_final": True,
        "options": []
    }

def process_dentist_notes(current_node, previous_choices=None):
    """Обрабатывает заметки стоматолога (если они есть в узле)."""
    if not current_node:
        return {'should_display': False}

    notes_data = {
        'clinical_observations': current_node.get('notes_dentist'),
        'diagnostic_hints': current_node.get('diagnostic_hints'),
        'examination_results': current_node.get('examination_results'),
        'should_display': False,
        'display_timing': current_node.get('notes_display_timing', 'immediate') 
    }
    if any(notes_data.get(key) for key in ['clinical_observations', 'diagnostic_hints', 'examination_results']):
        notes_data['should_display'] = True
        
    return notes_data

def calculate_empathy_score(history):
    """Улучшенный расчет эмпатии"""
    if not history or 'decisions' not in history:
        return 0
    
    total_score = 0
    decisions = history['decisions']
    
    if not decisions:
        return 0
    
    for decision in decisions:
        score_awarded = decision.get('score_awarded', 0)
        
        # Для плохих ответов (-10 и ниже) эмпатия очень низкая
        if score_awarded <= -10:
            total_score += 0  # 0 баллов за эмпатию
        elif score_awarded < 0:
            total_score += 10  # Очень низкая эмпатия
        elif score_awarded < 10:
            total_score += 30  # Низкая эмпатия
        elif score_awarded >= 15:
            total_score += 80  # Высокая эмпатия
        else:
            total_score += 50  # Средняя эмпатия
    
    return min(100, total_score // len(decisions))

def calculate_clinical_score(history):
    """Улучшенный расчет клинических навыков"""
    if not history or 'decisions' not in history:
        return 0
    
    total_score = 0
    decisions = history['decisions']
    
    if not decisions:
        return 0
    
    for decision in decisions:
        score_awarded = decision.get('score_awarded', 0)
        
        # Строгая оценка клинических навыков
        if score_awarded <= -10:
            total_score += 5  # Очень плохие клинические решения
        elif score_awarded < 0:
            total_score += 15
        elif score_awarded < 10:
            total_score += 40
        elif score_awarded >= 20:
            total_score += 90
        else:
            total_score += 60
    
    return min(100, total_score // len(decisions))

def calculate_communication_score(history):
    """Улучшенный расчет коммуникации"""
    if not history or 'decisions' not in history:
        return 0
    
    total_score = 0
    decisions = history['decisions']
    
    if not decisions:
        return 0
    
    for decision in decisions:
        score_awarded = decision.get('score_awarded', 0)
        option_text = decision.get('option_text', '').lower()
        
        # Анализ плохой коммуникации
        bad_phrases = ['быстро', 'давайте начнем', 'без объяснений', 'просто']
        has_bad_communication = any(phrase in option_text for phrase in bad_phrases)
        
        if score_awarded <= -10 or has_bad_communication:
            total_score += 0  # Ужасная коммуникация
        elif score_awarded < 0:
            total_score += 5
        elif score_awarded < 10:
            total_score += 25
        elif score_awarded >= 20:
            total_score += 85
        else:
            total_score += 50
    
    return min(100, total_score // len(decisions))

def calculate_efficiency_score(history, time_spent):
    if time_spent is None: return 50
    if time_spent < 300: return 90
    if time_spent < 600: return 70
    return 50

def calculate_decision_quality_score(history):
    total_score_awarded = 0
    num_decisions = 0
    if history and 'decisions' in history:
        for decision in history['decisions']:
            total_score_awarded += decision.get('score_awarded', 0)
            num_decisions +=1
    if num_decisions == 0: return 0
    return total_score_awarded * 5 if num_decisions > 0 else 60

def generate_recommendations(history, current_score, max_score):
    recommendations = []
    if (current_score / max_score if max_score > 0 else 0) < 0.7:
        recommendations.append({
            "icon": "book",
            "title": _("Review Clinical Guidelines"),
            "description": _("Consider reviewing the latest clinical guidelines related to this scenario.")
        })
    # Используем существующую функцию, если она доступна и работает
    try:
        if calculate_communication_score(history) < 70:
             recommendations.append({
                "icon": "chat-dots",
                "title": _("Practice Communication"),
                "description": _("Work on your communication skills, especially active listening.")
            })
    except NameError: # На случай если calculate_communication_score еще не определена глобально
        current_app.logger.warning("calculate_communication_score not available for recommendations.")

    if not recommendations:
        recommendations.append({
            "icon": "check-circle",
            "title": _("Good Work!"),
            "description": _("You've demonstrated solid skills. Keep practicing to maintain them.")
        })
    return recommendations

def get_template_for_device(desktop_template, mobile_template):
    """Возвращает подходящий шаблон для устройства."""
    detector = get_mobile_detector()
    if detector.is_mobile_device:
        return mobile_template
    return desktop_template

# --- Маршруты ---

@virtual_patient_bp.route("/") # Список сценариев
@login_required
def scenarios_list(lang):
    all_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).order_by(VirtualPatientScenario.title).all()
    for scenario_item in all_scenarios:
        best_attempt = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_item.id,
            completed=True
        ).order_by(VirtualPatientAttempt.score.desc()).first()
        
        attempts_count = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id, 
            scenario_id=scenario_item.id
        ).count()

        percentage = 0
        best_attempt_id_for_results = None
        if best_attempt:
            best_attempt_id_for_results = best_attempt.id
            if scenario_item.max_score and scenario_item.max_score > 0:
                percentage = round((best_attempt.score / scenario_item.max_score) * 100)
        
        scenario_item.user_progress = {
            'completed': bool(best_attempt),
            'score': best_attempt.score if best_attempt else 0,
            'max_score': scenario_item.max_score,
            'percentage': percentage,
            'attempts_count': attempts_count,
            'best_attempt_id': best_attempt_id_for_results
        }
    
    # Выбираем шаблон в зависимости от устройства
    template = get_template_for_device(
        "virtual_patient/scenarios_list.html", 
        "mobile/virtual_patient/virtual_patient_mobile_list.html"
    )
    
    return render_template(template, scenarios=all_scenarios, title=_("Virtual Patient Scenarios"))

@virtual_patient_bp.route("/<int:scenario_id>/start") # Запуск сценария
@login_required
def start_scenario(lang, scenario_id):
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    if scenario.is_premium and not current_user.has_subscription:
        flash(_("This scenario requires a premium subscription."), "warning")
        return redirect(url_for('.scenarios_list', lang=lang))

    attempt = VirtualPatientAttempt(
        user_id=current_user.id,
        scenario_id=scenario_id,
        max_score=scenario.max_score,
        started_at=datetime.now(timezone.utc),
        dialogue_history=json.dumps({
            "nodes": ["start"],
            "score": 0,
            "decisions": [],
            "decision_times": []
        })
    )
    db.session.add(attempt)
    db.session.commit()
    return redirect(url_for('.interact', lang=lang, attempt_id=attempt.id))

@virtual_patient_bp.route("/interact/<int:attempt_id>")
@login_required
def interact(lang, attempt_id):
    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        flash(_("You don't have access to this attempt."), "danger")
        return redirect(url_for('.scenarios_list', lang=lang))
    
    if attempt.completed:
        return redirect(url_for('.results', lang=lang, attempt_id=attempt.id))
    
    scenario_model = attempt.scenario
    scenario_data_for_lang = {}
    global_patient_info = {}

    try:
        if not scenario_model.scenario_data:
            raise ValueError("scenario_model.scenario_data is empty or None")
        scenario_data_from_db = json.loads(scenario_model.scenario_data)
        global_patient_info = scenario_data_from_db.get('patient_info', {}).copy()
        if not global_patient_info.get('image'):
            global_patient_info['image'] = 'patient_default.jpg'

        translations_data = scenario_data_from_db.get('translations', {})
        current_lang_code = getattr(g, 'lang', DEFAULT_LANGUAGE)
        if current_lang_code in translations_data:
            scenario_data_for_lang = translations_data[current_lang_code]
        else:
            default_lang_key_from_json = scenario_data_from_db.get('default', DEFAULT_LANGUAGE)
            scenario_data_for_lang = translations_data.get(default_lang_key_from_json, {})
            if not scenario_data_for_lang and DEFAULT_LANGUAGE in translations_data:
                 scenario_data_for_lang = translations_data[DEFAULT_LANGUAGE]
        if not scenario_data_for_lang:
            current_app.logger.warning(f"No language data found for lang '{current_lang_code}' or default. Using fallback. Scenario ID: {scenario_model.id}")
            scenario_data_for_lang = create_fallback_scenario_data()
    except (json.JSONDecodeError, KeyError, AttributeError, TypeError, ValueError) as e:
        current_app.logger.error(f"Error loading or parsing scenario_data for scenario ID {scenario_model.id}, attempt ID {attempt_id}: {e}", exc_info=True)
        scenario_data_for_lang = create_fallback_scenario_data()
        if not global_patient_info.get('image'):
            global_patient_info = {'image': 'patient_default.jpg', 'name': _('Error Patient'), 'age': 'N/A', 'gender': 'N/A'}

    try:
        history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else {"nodes": ["start"], "score": 0, "decisions": []}
    except json.JSONDecodeError:
        current_app.logger.error(f"Error parsing dialogue_history for attempt ID {attempt_id}", exc_info=True)
        history = {"nodes": ["start"], "score": 0, "decisions": []}

    current_node_id = history.get("nodes", ["start"])[-1] if history.get("nodes") else "start"
    current_node = find_current_node(scenario_data_for_lang, current_node_id, history)
    dentist_notes = process_dentist_notes(current_node, history.get('decisions', []))
    is_final = not current_node.get("options") or len(current_node.get("options", [])) == 0
    clinical_context = {
        'phase': current_node.get('clinical_phase', 'initial'),
        'required_actions': current_node.get('required_actions', []),
        'available_tools': current_node.get('available_tools', []),
        'contraindications': current_node.get('contraindications', [])
    }
    
    # Выбираем шаблон в зависимости от устройства
    template = get_template_for_device(
        "virtual_patient/interact.html",
        "mobile/virtual_patient/virtual_patient_mobile_interact.html"
    )
    
    # Сохраняем attempt_id в сессию для мобильной версии
    session['current_attempt_id'] = attempt.id
    
    return render_template(
        template,
        scenario_model_obj=scenario_model,
        attempt=attempt,
        scenario_data_for_lang=scenario_data_for_lang, 
        global_patient_info=global_patient_info,     
        current_node=current_node,
        history=history,
        is_final=is_final,
        dentist_notes=dentist_notes,
        clinical_context=clinical_context,
        current_language=getattr(g, 'lang', DEFAULT_LANGUAGE)
    )

# !! ВАЖНО: Убедитесь, что у вас только ОДНА функция results !!
# Удалите дублирующуюся функцию results, если она все еще есть.
# Ниже представлена измененная функция results.

@virtual_patient_bp.route("/results/<int:attempt_id>") # Отображение результатов
@login_required
def results(lang, attempt_id): # Это единственная функция results, которую следует оставить
    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        flash(_("You don't have access to these results."), "danger")
        return redirect(url_for('.scenarios_list', lang=lang))

    scenario_model = attempt.scenario
    scenario_data_for_lang = {}
    global_patient_info = {}

    try:
        scenario_data_from_db = json.loads(scenario_model.scenario_data)
        global_patient_info = scenario_data_from_db.get('patient_info', {'image': 'patient_default.jpg'})
        
        translations_data = scenario_data_from_db.get('translations', {})
        current_lang_code = getattr(g, 'lang', DEFAULT_LANGUAGE)
        if current_lang_code in translations_data:
            scenario_data_for_lang = translations_data[current_lang_code]
        else:
            default_lang_key_from_json = scenario_data_from_db.get('default', DEFAULT_LANGUAGE)
            scenario_data_for_lang = translations_data.get(default_lang_key_from_json, {})
        
        if not scenario_data_for_lang: # Fallback
            current_app.logger.warning(f"No language data for {current_lang_code} or default for scenario {scenario_model.id}. Using fallback.")
            scenario_data_for_lang = create_fallback_scenario_data()

    except Exception as e:
        current_app.logger.error(f"Error loading scenario data for results page: {e}", exc_info=True)
        scenario_data_for_lang = create_fallback_scenario_data()
        if not global_patient_info.get('image'):
             global_patient_info = {'image': 'patient_default.jpg', 'name': _('Error Patient')}

    history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else {"decisions": [], "score": 0, "decision_times": []}
    
    final_score = attempt.score
    max_score_for_scenario = scenario_model.max_score if scenario_model.max_score and scenario_model.max_score > 0 else 100
    percentage_score = (final_score / max_score_for_scenario) * 100 if max_score_for_scenario > 0 else 0

    outcomes_data = scenario_data_for_lang.get("outcomes", {})
    result_display = {"title": _("Result"), "text": _("Your result is being processed.")}

    if percentage_score >= 70 and outcomes_data.get('good'):
        result_display = outcomes_data['good']
    elif percentage_score >= 40 and outcomes_data.get('average'):
        result_display = outcomes_data['average']
    elif outcomes_data.get('poor'):
        result_display = outcomes_data['poor']
    else: 
        result_display['title'] = _("Result for {score}/{max_score}").format(score=final_score, max_score=max_score_for_scenario)
        result_display['text'] = _("Thank you for completing the scenario.") # Согласовано с вашим файлом

    # === ДОБАВИТЬ ГЕЙМИФИКАЦИЮ НА СТРАНИЦУ РЕЗУЛЬТАТОВ (Шаг 7.1) ===
    gamification_data = {}
    try:
        from utils.gamification_engine import GamificationEngine # Локальный импорт
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        
        gamification_data = {
            'current_level': stats.current_level,
            'total_xp': stats.total_experience_points,
            'points_to_next_level': stats.points_to_next_level,
            'scenarios_completed': stats.total_scenarios_completed,
            'average_score': stats.average_score_percentage
        }

    except ImportError:
        current_app.logger.warning("Gamification engine not available")
        gamification_data = {
            'current_level': 1,
            'total_xp': 0,
            'points_to_next_level': 100,
            'scenarios_completed': 1,
            'average_score': percentage_score
        }
    except Exception as e:
        current_app.logger.error(f"Error loading gamification data: {e}")
        gamification_data = {
            'current_level': 1,
            'total_xp': 0,
            'points_to_next_level': 100,
            'scenarios_completed': 1,
            'average_score': percentage_score
        }

    # Выбираем шаблон в зависимости от устройства
    template = get_template_for_device(
        "virtual_patient/results.html",
        "mobile/virtual_patient/virtual_patient_mobile_results.html"
    )

    # Подготавливаем переводы для JavaScript
    js_translations = {
        'results_js': optimized_translations.get('results_js', {})
    }

    return render_template(
        template,
        attempt=attempt,
        scenario=scenario_model,
        scenario_model=scenario_model,
        scenario_data_for_lang=scenario_data_for_lang,
        global_patient_info=global_patient_info,
        history=history,
        result_display=result_display,
        gamification_data=gamification_data,
        calculate_empathy_score=calculate_empathy_score,
        calculate_clinical_score=calculate_clinical_score,
        calculate_communication_score=calculate_communication_score,
        calculate_base_experience_points=calculate_base_experience_points,
        translations=js_translations,  # Передаем только нужные переводы
        lang=lang
    )

@virtual_patient_bp.route("/api/select_option", methods=["POST"])
@login_required
def select_option(lang):
    # Проверяем тип запроса - JSON или FormData
    if request.is_json:
        data = request.get_json()
        attempt_id = data.get("attempt_id")
        option_index = data.get("option_index")
    else:
        # FormData для мобильной версии
        attempt_id = session.get('current_attempt_id')  # Получаем из сессии
        option_index = request.form.get("selected_option")

    if not attempt_id or option_index is None:
        if request.is_json:
            return jsonify({"status": "error", "message": "Missing required data"}), 400
        else:
            flash(_("Missing required data"), "error")
            return redirect(url_for('.scenarios_list', lang=lang))

    try:
        attempt_id = int(attempt_id)
        option_index = int(option_index)
    except ValueError:
        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid data format"}), 400
        else:
            flash(_("Invalid data format"), "error")
            return redirect(url_for('.scenarios_list', lang=lang))

    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id:
        if request.is_json:
            return jsonify({"status": "error", "message": "Access denied"}), 403
        else:
            flash(_("Access denied"), "error")
            return redirect(url_for('.scenarios_list', lang=lang))

    if attempt.completed:
        if request.is_json:
            return jsonify({"status": "error", "message": "Attempt already completed"}), 400
        else:
            return redirect(url_for('.results', lang=lang, attempt_id=attempt.id))

    scenario_model = attempt.scenario
    try:
        history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else {"nodes": ["start"], "score": 0, "decisions": []}
        current_node_id = history.get("nodes", ["start"])[-1]
    except (json.JSONDecodeError, KeyError):
        if request.is_json:
            return jsonify({"status": "error", "message": "Error parsing dialogue history"}), 500
        else:
            flash(_("Error parsing dialogue history"), "error")
            return redirect(url_for('.scenarios_list', lang=lang))

    scenario_data_for_lang = {}
    try:
        scenario_data_from_db = json.loads(scenario_model.scenario_data)
        translations_data = scenario_data_from_db.get('translations', {})
        current_lang_code = getattr(g, 'lang', DEFAULT_LANGUAGE)
        if current_lang_code in translations_data:
            scenario_data_for_lang = translations_data[current_lang_code]
        else:
            default_lang_key_from_json = scenario_data_from_db.get('default', DEFAULT_LANGUAGE)
            scenario_data_for_lang = translations_data.get(default_lang_key_from_json, {})
        if not scenario_data_for_lang: 
            scenario_data_for_lang = create_fallback_scenario_data()
    except Exception as e:
        current_app.logger.error(f"Error loading scenario data in select_option: {e}")
        scenario_data_for_lang = create_fallback_scenario_data()

    current_node = find_current_node(scenario_data_for_lang, current_node_id, history)

    if not current_node or 'options' not in current_node or option_index >= len(current_node["options"]):
        if request.is_json:
            return jsonify({"status": "error", "message": "Invalid option or node structure"}), 400
        else:
            flash(_("Invalid option or node structure"), "error")
            return redirect(url_for('.scenarios_list', lang=lang))

    selected_option = current_node["options"][option_index]
    score_change = selected_option.get("score", 0)

    history["nodes"].append(selected_option.get("next_node", "end"))
    history["score"] += score_change
    history.setdefault("decisions", []).append({
        "node_id": current_node_id,
        "option_text": selected_option.get("text"),
        "score_awarded": score_change,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    next_node_id_str = selected_option.get("next_node")
    next_node_obj = find_current_node(scenario_data_for_lang, next_node_id_str, history) if next_node_id_str else None
    is_final = not next_node_obj or not next_node_obj.get("options") or len(next_node_obj.get("options",[])) == 0

    attempt.score = history["score"]
    attempt.dialogue_history = json.dumps(history)
    if is_final:
        attempt.completed = True
        attempt.completed_at = datetime.now(timezone.utc)
        if attempt.started_at:
            if attempt.started_at.tzinfo is None:
                started_at_utc = attempt.started_at.replace(tzinfo=timezone.utc)
            else:
                started_at_utc = attempt.started_at
            time_spent_delta = attempt.completed_at - started_at_utc
            attempt.time_spent = time_spent_delta.total_seconds()
        else:
            # Fallback if started_at is somehow None
            attempt.started_at = datetime.now(timezone.utc) - timedelta(seconds=10) # Assign a recent past time
            attempt.time_spent = 10 # Assign a default duration

        try:
            from utils.gamification_engine import GamificationEngine
            gamification = GamificationEngine(db.session)
            attempt_data = {
                'score': attempt.score,
                'max_score': scenario_model.max_score or 100,
                'time_spent': attempt.time_spent or 0,
                'dialogue_history': attempt.dialogue_history
            }
            rewards = gamification.process_scenario_completion(current_user.id, attempt_data)
            current_app.logger.info(f"🎮 Gamification: user {current_user.id} received {rewards.get('points_awarded', 0)} XP. Level up: {rewards.get('level_up', False)}")
        except ImportError:
            current_app.logger.warning("GamificationEngine not found or import error. Skipping gamification processing.")
        except Exception as e:
            current_app.logger.error(f"Ошибка геймификации в select_option: {e}", exc_info=True)

    db.session.commit()

    if request.is_json:
        return jsonify({
            "status": "success",
            "score": attempt.score,
            "score_change": score_change,
            "is_final": is_final,
            "next_url": url_for('.results', lang=lang, attempt_id=attempt.id) if is_final else None,
            "feedback_text": selected_option.get("feedback")
        })
    else:
        # Для мобильной версии - перенаправляем на следующую страницу
        if is_final:
            return redirect(url_for('.results', lang=lang, attempt_id=attempt.id))
        else:
            return redirect(url_for('.interact', lang=lang, attempt_id=attempt.id))

@virtual_patient_bp.route("/achievements")
@login_required
def achievements(lang):
    """Страница достижений пользователя"""
    try:
        print("🔍 DEBUG: Starting achievements function")
        
        from utils.gamification_engine import GamificationEngine
        print("🔍 DEBUG: Imported GamificationEngine")
        
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        print(f"🔍 DEBUG: Got user stats for user {current_user.id}")
        
        # Проверяем импорт моделей
        from models import Achievement, UserAchievement
        print("🔍 DEBUG: Imported Achievement and UserAchievement models")
        
        # Получаем все достижения
        all_achievements = Achievement.query.filter_by(is_active=True).all()
        print(f"🔍 DEBUG: Found {len(all_achievements)} achievements")
        
        # Получаем достижения пользователя
        user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
        earned_achievement_ids = [ua.achievement_id for ua in user_achievements]
        print(f"🔍 DEBUG: User has {len(user_achievements)} achievements")
        
        gamification_data = {
            'current_level': stats.current_level,
            'total_xp': stats.total_experience_points,
            'points_to_next_level': stats.points_to_next_level,
            'scenarios_completed': stats.total_scenarios_completed,
            'average_score': stats.average_score_percentage
        }
        print("🔍 DEBUG: Created gamification_data")
        
        print("🔍 DEBUG: About to render template")
        return render_template(
            "virtual_patient/achievements.html",
            all_achievements=all_achievements,
            user_achievements=user_achievements,
            earned_achievement_ids=earned_achievement_ids,
            gamification_data=gamification_data,
            title=_("Achievements")
        )
        
    except Exception as e:
        print(f"🔍 DEBUG: Error in achievements function: {e}")
        import traceback
        traceback.print_exc()
        flash(_("Error loading achievements"), "error")
        return redirect(url_for('.scenarios_list', lang=lang))