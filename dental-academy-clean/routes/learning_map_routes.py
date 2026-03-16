# routes/learning_map_routes.py

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, g, flash, 
    jsonify, current_app
)
from flask_login import login_required, current_user
from extensions import db
from models import (
    VirtualPatientScenario, VirtualPatientAttempt, LearningPath, Subject, Module, Lesson, UserProgress, Test, UserExamDate, ContentCategory, ContentSubcategory, ContentTopic,
    User, Question, TestAttempt, QuestionCategory, DiagnosticSession, PersonalLearningPlan, StudySession
)
from translations import get_translation as t  # предполагаем, что функция называется get_translation
from sqlalchemy import func
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from utils.unified_stats import get_unified_user_stats, get_module_stats_unified, get_subject_stats_unified, clear_stats_cache

# Создаем Blueprint для карты обучения
learning_map_bp = Blueprint(
    "learning_map_bp",
    __name__,
    url_prefix='/<string:lang>/learning-map',
    template_folder='../templates'
    )

# Обработка CSRF токена из JSON для API запросов
@learning_map_bp.before_request
def handle_json_csrf():
    """Извлекает CSRF токен из JSON тела запроса и устанавливает в заголовок"""
    if request.method == 'POST' and request.is_json:
        try:
            # Используем get_data с cache=True чтобы можно было прочитать данные несколько раз
            raw_data = request.get_data(cache=True)
            if raw_data:
                data = json.loads(raw_data)
                if 'csrf_token' in data and 'X-CSRFToken' not in request.headers:
                    # Устанавливаем токен в заголовок через environ (Flask-WTF проверяет заголовки)
                    request.environ['HTTP_X_CSRFTOKEN'] = data['csrf_token']
        except (json.JSONDecodeError, TypeError):
            pass  # Если не удалось распарсить, продолжаем без изменений


def _rebuild_study_schedule_from_sessions(plan):
    """
    Attempt to rebuild a minimal study schedule from existing StudySession records.
    Returns schedule dict or None if rebuild not possible.
    """
    try:
        sessions = plan.study_sessions.order_by(StudySession.id).all()
        if not sessions:
            current_app.logger.warning(f"Schedule rebuild: plan {plan.id} has no study sessions")
            return None

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_schedule = []
        current_week_sessions = []
        week_number = 1

        for idx, study_session in enumerate(sessions):
            day_index = idx % 7
            if day_index == 0 and current_week_sessions:
                estimated_hours = sum(
                    (session_entry.get('duration', 0) or 0) / 60.0
                    for session_entry in current_week_sessions
                )
                weekly_schedule.append({
                    'week_number': week_number,
                    'focus_domains': [],
                    'daily_sessions': current_week_sessions,
                    'milestone_test': False,
                    'estimated_hours': round(estimated_hours, 2)
                })
                week_number += 1
                current_week_sessions = []

            duration_minutes = study_session.planned_duration or getattr(plan, 'daily_goal_minutes', None) or 30
            session_entry = {
                'day': day_names[day_index],
                'type': study_session.session_type or 'practice',
                'duration': duration_minutes,
                'focus_domains': []
            }
            current_week_sessions.append(session_entry)

        if current_week_sessions:
            estimated_hours = sum(
                (session_entry.get('duration', 0) or 0) / 60.0
                for session_entry in current_week_sessions
            )
            weekly_schedule.append({
                'week_number': week_number,
                'focus_domains': [],
                'daily_sessions': current_week_sessions,
                'milestone_test': False,
                'estimated_hours': round(estimated_hours, 2)
            })

        if not weekly_schedule:
            current_app.logger.warning(f"Schedule rebuild produced empty weekly_schedule for plan {plan.id}")
            return None

        schedule = {
            'weekly_schedule': weekly_schedule,
            'total_weeks': len(weekly_schedule),
            'recovered_from': 'study_sessions'
        }
        return schedule
    except Exception as error:
        current_app.logger.error(f"Failed to rebuild study schedule for plan {plan.id}: {error}", exc_info=True)
        return None

# === ПРОФЕССИОНАЛЬНАЯ СИСТЕМА РОУТИНГА === #

# Создаем отдельный Blueprint для профессиональных карт
profession_map_bp = Blueprint(
    "profession_map_bp",
    __name__,
    url_prefix='/<string:lang>/leerkaart',
    template_folder='../templates'
)

@profession_map_bp.before_request
def load_profession_lang():
    """Обработчик языка для профессиональных роутов + Gatekeeper"""
    lang = request.view_args.get('lang', DEFAULT_LANGUAGE) if request.view_args else DEFAULT_LANGUAGE
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    g.lang = lang
    session['lang'] = lang

    # Gatekeeper: Запретить доступ всем, кроме админов или прошедших скрининг
    if request.endpoint and 'static' not in request.endpoint:
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            return redirect(url_for('auth.login', lang=lang))
            
        # Проверяем прохождение скрининга
        has_completed_screening = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.diagnostic_type == 'quick_scan_10',
            DiagnosticSession.completed_at.isnot(None)
        ).first() is not None
        
        if getattr(current_user, 'role', 'user') != 'admin' and not has_completed_screening:
            flash('Для доступа к профессиональной карте необходимо пройти первичную диагностику (Quick Scan 10).', 'info')
            return redirect(url_for('diagnostic.start_diagnostic_get', lang=lang))

@profession_map_bp.context_processor
def inject_lang_profession():
    """Добавляет lang в контекст шаблонов профессиональных роутов"""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

# Маппинг профессий
PROFESSION_MAPPINGS = {
    'tandheelkunde': 'tandarts',
    'farmacie': 'apotheker', 
    'huisartsgeneeskunde': 'huisarts',
    'verpleegkunde': 'verpleegkundige'
}

PROFESSION_NAMES = {
    'tandheelkunde': 'Tandheelkunde',
    'farmacie': '💊 Farmacie',
    'huisartsgeneeskunde': '🩺 Huisartsgeneeskunde', 
    'verpleegkunde': '👩‍⚕️ Verpleegkunde'
}

def get_pharmacy_learning_data(user_id):
    """Генерирует данные карты обучения для фармацевтов"""
    
    # Фармацевтические пути обучения
    pharmacy_paths = [
        {
            'id': 1,
            'name': 'BIG-toets Voorbereiding',
            'description': 'Подготовка к главному экзамену BIG для фармацевтов',
            'icon': 'certificate',
            'order': 1,
            'is_active': True,
            'css_class': 'big-preparation',
            'url': '/learning-map/subject/101/tests'  # Добавляем прямую ссылку на тесты
        },
        {
            'id': 2, 
            'name': 'Medicatiebegeleiding',
            'description': 'Сопровождение медикаментозного лечения пациентов',
            'icon': 'pill',
            'order': 2,
            'is_active': True,
            'css_class': 'medication-guidance'
        },
        {
            'id': 3,
            'name': 'Farmacologie',
            'description': 'Изучение действия лекарственных средств',
            'icon': 'flask',
            'order': 3,
            'is_active': True,
            'css_class': 'pharmacology'
        },
        {
            'id': 4,
            'name': 'Interacties & Contraindicaties',
            'description': 'Взаимодействия и противопоказания препаратов',
            'icon': 'warning-triangle',
            'order': 4,
            'is_active': True,
            'css_class': 'interactions'
        },
        {
            'id': 5,
            'name': 'Dosering & Berekeningen',
            'description': 'Дозировки и фармацевтические расчеты',
            'icon': 'calculator',
            'order': 5,
            'is_active': True,
            'css_class': 'dosage-calculations'
        },
        {
            'id': 6,
            'name': 'Patiëntcommunicatie',
            'description': 'Коммуникация с пациентами в аптеке',
            'icon': 'message-circle',
            'order': 6,
            'is_active': True,
            'css_class': 'patient-communication'
        },
        {
            'id': 7,
            'name': 'Wetgeving & Ethiek',
            'description': 'Законодательство и этика в фармации',
            'icon': 'shield-check',
            'order': 7,
            'is_active': True,
            'css_class': 'legislation-ethics'
        }
    ]
    
    # Фармацевтические предметы с модулями
    pharmacy_subjects = []
    
    # BIG-toets Voorbereiding предметы
    big_subjects = [
        {
            'id': 101,
            'name': 'Algemene Farmacologie',
            'description': 'Основы фармакологии для BIG экзамена',
            'learning_path_id': 1,
            'progress': 45,
            'modules': [
                {'id': 1001, 'title': 'Farmacokinetiek Basis', 'progress': 60, 'total_lessons': 12, 'completed_lessons': 7},
                {'id': 1002, 'title': 'Farmacodynamiek', 'progress': 30, 'total_lessons': 10, 'completed_lessons': 3},
                {'id': 1003, 'title': 'Bijwerkingen Herkenning', 'progress': 45, 'total_lessons': 8, 'completed_lessons': 4}
            ]
        },
        {
            'id': 102,
            'name': 'Medicijnkennis BIG',
            'description': 'Medicijnen voor BIG toets',
            'learning_path_id': 1,
            'progress': 35,
            'modules': [
                {'id': 1004, 'title': 'Cardiovasculaire Geneesmiddelen', 'progress': 40, 'total_lessons': 15, 'completed_lessons': 6},
                {'id': 1005, 'title': 'Antibiotica & Infectieziekten', 'progress': 25, 'total_lessons': 12, 'completed_lessons': 3},
                {'id': 1006, 'title': 'Pijnstilling & Ontstekingsremmers', 'progress': 50, 'total_lessons': 10, 'completed_lessons': 5}
            ]
        }
    ]
    
    # Medicatiebegeleiding предметы
    medication_subjects = [
        {
            'id': 201,
            'name': 'Medicatiegeschiedenis',
            'description': 'Анализ истории приема медикаментов',
            'learning_path_id': 2,
            'progress': 60,
            'modules': [
                {'id': 2001, 'title': 'Anamnese Technieken', 'progress': 70, 'total_lessons': 8, 'completed_lessons': 6},
                {'id': 2002, 'title': 'Medicatiereview', 'progress': 50, 'total_lessons': 10, 'completed_lessons': 5}
            ]
        },
        {
            'id': 202,
            'name': 'Therapietrouw',
            'description': 'Приверженность терапии пациентов',
            'learning_path_id': 2,
            'progress': 40,
            'modules': [
                {'id': 2003, 'title': 'Adherentie Assessment', 'progress': 35, 'total_lessons': 6, 'completed_lessons': 2},
                {'id': 2004, 'title': 'Motiverende Gespreksvoering', 'progress': 45, 'total_lessons': 8, 'completed_lessons': 4}
            ]
        }
    ]
    
    # Farmacologie предметы
    pharmacology_subjects = [
        {
            'id': 301,
            'name': 'Receptorfarmacologie',
            'description': 'Рецепторная фармакология',
            'learning_path_id': 3,
            'progress': 25,
            'modules': [
                {'id': 3001, 'title': 'G-proteïne Gekoppelde Receptoren', 'progress': 20, 'total_lessons': 12, 'completed_lessons': 2},
                {'id': 3002, 'title': 'Ionenkanalen', 'progress': 30, 'total_lessons': 10, 'completed_lessons': 3}
            ]
        }
    ]
    
    # Объединяем все предметы
    pharmacy_subjects = big_subjects + medication_subjects + pharmacology_subjects
    
    return {
        'learning_paths': pharmacy_paths,
        'subjects': pharmacy_subjects
    }

def get_gp_learning_data(user_id):
    """Генерирует данные карты обучения для врачей общей практики"""
    
    # Пути обучения для врачей общей практики
    gp_paths = [
        {
            'id': 1,
            'name': 'BIG-toets Voorbereiding',
            'description': 'Подготовка к главному экзамену BIG для врачей',
            'icon': 'certificate',
            'order': 1,
            'is_active': True,
            'css_class': 'gp-big-preparation'
        },
        {
            'id': 2,
            'name': 'NHG Richtlijnen',
            'description': 'Стандарты Nederlandse Huisartsen Genootschap',
            'icon': 'book-open',
            'order': 2,
            'is_active': True,
            'css_class': 'gp-nhg-guidelines'
        },
        {
            'id': 3,
            'name': 'Diagnostiek & Behandeling',
            'description': 'Диагностика и лечение в общей практике',
            'icon': 'stethoscope',
            'order': 3,
            'is_active': True,
            'css_class': 'gp-diagnostics'
        },
        {
            'id': 4,
            'name': 'Verwijsprotocollen',
            'description': 'Протоколы направления к специалистам',
            'icon': 'arrow-right-circle',
            'order': 4,
            'is_active': True,
            'css_class': 'gp-referral-protocols'
        },
        {
            'id': 5,
            'name': 'Preventieve Zorg',
            'description': 'Профилактическая медицина и скрининг',
            'icon': 'shield-heart',
            'order': 5,
            'is_active': True,
            'css_class': 'gp-preventive-care'
        },
        {
            'id': 6,
            'name': 'Chronische Ziekten',
            'description': 'Ведение хронических заболеваний',
            'icon': 'calendar-heart',
            'order': 6,
            'is_active': True,
            'css_class': 'gp-chronic-diseases'
        },
        {
            'id': 7,
            'name': 'Acute Zorg',
            'description': 'Неотложная помощь в общей практике',
            'icon': 'activity',
            'order': 7,
            'is_active': True,
            'css_class': 'gp-acute-care'
        }
    ]
    
    # Предметы для врачей общей практики
    gp_subjects = [
        # BIG-toets Voorbereiding
        {
            'id': 401,
            'name': 'Interne Geneeskunde Basis',
            'description': 'Основы внутренней медицины для BIG',
            'learning_path_id': 1,
            'progress': 55,
            'modules': [
                {'id': 4001, 'title': 'Cardiovasculaire Aandoeningen', 'progress': 65, 'total_lessons': 15, 'completed_lessons': 10},
                {'id': 4002, 'title': 'Respiratoire Ziekten', 'progress': 45, 'total_lessons': 12, 'completed_lessons': 5},
                {'id': 4003, 'title': 'Endocriene Stoornissen', 'progress': 55, 'total_lessons': 10, 'completed_lessons': 6}
            ]
        },
        {
            'id': 402,
            'name': 'Algemene Farmacologie GP',
            'description': 'Фармакология для врача общей практики',
            'learning_path_id': 1,
            'progress': 40,
            'modules': [
                {'id': 4004, 'title': 'Antibiotica in de Huisartspraktijk', 'progress': 50, 'total_lessons': 8, 'completed_lessons': 4},
                {'id': 4005, 'title': 'Pijnstilling & NSAID', 'progress': 30, 'total_lessons': 10, 'completed_lessons': 3}
            ]
        },
        
        # NHG Richtlijnen
        {
            'id': 501,
            'name': 'NHG Standaarden Implementatie',
            'description': 'Применение стандартов NHG в практике',
            'learning_path_id': 2,
            'progress': 70,
            'modules': [
                {'id': 5001, 'title': 'Diabetes Mellitus Type 2', 'progress': 80, 'total_lessons': 12, 'completed_lessons': 10},
                {'id': 5002, 'title': 'Hypertensie Richtlijn', 'progress': 60, 'total_lessons': 8, 'completed_lessons': 5}
            ]
        },
        
        # Diagnostiek & Behandeling
        {
            'id': 601,
            'name': 'Point-of-care Diagnostiek',
            'description': 'Диагностика в кабинете врача',
            'learning_path_id': 3,
            'progress': 30,
            'modules': [
                {'id': 6001, 'title': 'ECG Interpretatie', 'progress': 35, 'total_lessons': 15, 'completed_lessons': 5},
                {'id': 6002, 'title': 'Laboratorium Uitslagen', 'progress': 25, 'total_lessons': 10, 'completed_lessons': 3}
            ]
        }
    ]
    
    return {
        'learning_paths': gp_paths,
        'subjects': gp_subjects
    }

def get_nursing_learning_data(user_id):
    """Генерирует данные карты обучения для медсестер"""
    
    # Пути обучения для медсестер
    nursing_paths = [
        {
            'id': 1,
            'name': 'BIG-toets Voorbereiding',
            'description': 'Подготовка к главному экзамену BIG для медсестер',
            'icon': 'certificate',
            'order': 1,
            'is_active': True,
            'css_class': 'nursing-big-preparation'
        },
        {
            'id': 2,
            'name': 'SKV Accreditatie',
            'description': 'Аккредитация Stichting Kwaliteitsregister V&V',
            'icon': 'award',
            'order': 2,
            'is_active': True,
            'css_class': 'nursing-skv-accreditation'
        },
        {
            'id': 3,
            'name': 'Patiëntenzorg & Veiligheid',
            'description': 'Уход за пациентами и безопасность',
            'icon': 'heart-pulse',
            'order': 3,
            'is_active': True,
            'css_class': 'nursing-patient-care'
        },
        {
            'id': 4,
            'name': 'Specialisaties (ICU, OK, etc.)',
            'description': 'Специализированный уход в разных отделениях',
            'icon': 'hospital',
            'order': 4,
            'is_active': True,
            'css_class': 'nursing-specializations'
        },
        {
            'id': 5,
            'name': 'Medicatie Toediening',
            'description': 'Безопасное применение лекарственных средств',
            'icon': 'syringe',
            'order': 5,
            'is_active': True,
            'css_class': 'nursing-medication'
        },
        {
            'id': 6,
            'name': 'Communicatie & Ethiek',
            'description': 'Коммуникация с пациентами и этические вопросы',
            'icon': 'messages',
            'order': 6,
            'is_active': True,
            'css_class': 'nursing-communication'
        },
        {
            'id': 7,
            'name': 'Evidence Based Practice',
            'description': 'Научно-обоснованная сестринская практика',
            'icon': 'microscope',
            'order': 7,
            'is_active': True,
            'css_class': 'nursing-ebp'
        }
    ]
    
    # Предметы для медсестер
    nursing_subjects = [
        # BIG-toets Voorbereiding
        {
            'id': 701,
            'name': 'Anatomie & Fysiologie',
            'description': 'Анатомия и физиология для медсестер',
            'learning_path_id': 1,
            'progress': 50,
            'modules': [
                {'id': 7001, 'title': 'Cardiovasculair Systeem', 'progress': 60, 'total_lessons': 12, 'completed_lessons': 7},
                {'id': 7002, 'title': 'Respiratoir Systeem', 'progress': 40, 'total_lessons': 10, 'completed_lessons': 4},
                {'id': 7003, 'title': 'Zenuwstelsel Basis', 'progress': 50, 'total_lessons': 15, 'completed_lessons': 8}
            ]
        },
        {
            'id': 702,
            'name': 'Farmacologie voor Verpleegkundigen',
            'description': 'Фармакология в сестринской практике',
            'learning_path_id': 1,
            'progress': 35,
            'modules': [
                {'id': 7004, 'title': 'Medicatie Berekeningen', 'progress': 45, 'total_lessons': 8, 'completed_lessons': 4},
                {'id': 7005, 'title': 'Bijwerkingen Monitoring', 'progress': 25, 'total_lessons': 10, 'completed_lessons': 3}
            ]
        },
        
        # SKV Accreditatie
        {
            'id': 801,
            'name': 'Kwaliteitsmanagement',
            'description': 'Управление качеством в сестринском деле',
            'learning_path_id': 2,
            'progress': 65,
            'modules': [
                {'id': 8001, 'title': 'Kwaliteitsindicatoren', 'progress': 75, 'total_lessons': 6, 'completed_lessons': 5},
                {'id': 8002, 'title': 'Continue Verbetering', 'progress': 55, 'total_lessons': 8, 'completed_lessons': 4}
            ]
        },
        
        # Patiëntenzorg & Veiligheid
        {
            'id': 901,
            'name': 'Infectiepreventie',
            'description': 'Профилактика инфекций в медицинских учреждениях',
            'learning_path_id': 3,
            'progress': 80,
            'modules': [
                {'id': 9001, 'title': 'Handhygiëne Protocollen', 'progress': 90, 'total_lessons': 5, 'completed_lessons': 5},
                {'id': 9002, 'title': 'Isolatiemaatregelen', 'progress': 70, 'total_lessons': 8, 'completed_lessons': 6}
            ]
        },
        {
            'id': 902,
            'name': 'Patiënt Veiligheid',
            'description': 'Безопасность пациентов в сестринской практике',
            'learning_path_id': 3,
            'progress': 45,
            'modules': [
                {'id': 9003, 'title': 'Valpreventie', 'progress': 50, 'total_lessons': 6, 'completed_lessons': 3},
                {'id': 9004, 'title': 'Medicatie Veiligheid', 'progress': 40, 'total_lessons': 10, 'completed_lessons': 4}
            ]
        },
        
        # Specialisaties
        {
            'id': 1001,
            'name': 'Intensive Care Verpleegkunde',
            'description': 'Интенсивная терапия и реанимация',
            'learning_path_id': 4,
            'progress': 25,
            'modules': [
                {'id': 10001, 'title': 'Monitoring & Observatie', 'progress': 30, 'total_lessons': 15, 'completed_lessons': 5},
                {'id': 10002, 'title': 'Beademing Ondersteuning', 'progress': 20, 'total_lessons': 12, 'completed_lessons': 2}
            ]
        }
    ]
    
    return {
        'learning_paths': nursing_paths,
        'subjects': nursing_subjects
    }

def get_dentistry_learning_data(user_id):
    """Генерирует данные карты обучения для стоматологов (BI-toets структура)"""
    
    # Получаем пути обучения из базы данных
    from models import UserLearningProgress
    
    learning_paths = LearningPath.query.filter_by(is_active=True).order_by(LearningPath.exam_weight.desc()).all()
    
    dentistry_paths = []
    for path in learning_paths:
        # Получаем прогресс пользователя
        user_progress = UserLearningProgress.query.filter_by(
            user_id=user_id,
            learning_path_id=path.id
        ).first()
        
        progress_percent = user_progress.progress_percentage if user_progress else 0
        
        # Определяем иконку в зависимости от типа экзамена
        icon_map = {
            'multiple_choice': 'question-circle',
            'open_book': 'book-open',
            'practical_theory': 'hands',
            'interview': 'user-md',
            'case_study': 'clipboard-list'
        }
        
        icon = icon_map.get(path.exam_type, 'graduation-cap')
        
        # Определяем CSS класс на основе компонента экзамена
        css_class_map = {
            'THEORETICAL': 'knowledge-center',
            'METHODOLOGY': 'communication', 
            'PRACTICAL': 'preclinical',
            'CLINICAL': 'workstation'
        }
        
        # Словарь коротких названий для путей обучения
        short_names = {
            'THK I - Tandheelkunde Kern I': 'THK I',
            'THK II - Tandheelkunde Kern II': 'THK II',
            'Basic Medical Sciences': 'Basic Medical Sciences',
            'Praktische vaardigheden (Simodont voorbereiding)': 'Praktische vaardigheden',
            'Radiologie': 'Radiologie',
            'Statistiek voor tandheelkunde': 'Statistiek',
            'Onderzoeksmethodologie': 'Onderzoek',
            'Communicatie en ethiek': 'Communicatie & Ethiek',
            'Behandelplanning': 'Behandelplanning'
        }
        
        # Получаем короткое название или используем оригинальное
        short_name = short_names.get(path.name, path.name)
        
        path_data = {
            'id': path.id,
            'name': path.name,  # Полное название для tooltip
            'short_name': short_name,  # Короткое название для отображения
            'description': path.description or f'{path.exam_component} - {path.exam_weight}%',
            'icon': icon,
            'order': path.exam_weight,  # Используем вес как порядок
            'is_active': path.is_active,
            'css_class': css_class_map.get(path.exam_component, 'knowledge-center'),
            'progress_percent': progress_percent,
            'exam_component': path.exam_component,
            'exam_weight': path.exam_weight,
            'exam_type': path.exam_type,
            'total_hours': path.total_estimated_hours or 0,
            'duration_weeks': path.duration_weeks or 0
        }
        dentistry_paths.append(path_data)
    
    # Получаем реальные предметы из базы данных
    dentistry_subjects = []
    subjects = Subject.query.all()
    
    for subject in subjects:
        # Получаем модули для этого предмета
        modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
        
        # Обрабатываем модули
        processed_modules = []
        total_progress = 0
        
        for module in modules:
            # Получаем статистику модуля
            module_stats = get_module_stats_unified(module.id, user_id)
            
            # Добавляем модуль с прогрессом
            processed_modules.append({
                'id': module.id,
                'title': module.title,
                'description': module.description if hasattr(module, 'description') else '',
                'is_premium': module.is_premium if hasattr(module, 'is_premium') else False,
                'is_final_test': module.is_final_test if hasattr(module, 'is_final_test') else False,
                'icon': module.icon if hasattr(module, 'icon') else 'file-earmark-text',
                'progress': module_stats['progress'],
                'completed_lessons': module_stats['completed_lessons'],
                'total_lessons': module_stats['total_lessons']
            })
            
            total_progress += module_stats['progress']
        
        # Вычисляем средний прогресс предмета
        subject_progress = round(total_progress / len(modules)) if modules else 0
        
        # Создаем словарь с информацией о предмете
        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description if hasattr(subject, 'description') else '',
            'icon': subject.icon if hasattr(subject, 'icon') else 'folder2-open',
            'learning_path_id': subject.learning_path_id,
            'progress': subject_progress,
            'modules': processed_modules
        }
        
        dentistry_subjects.append(subject_data)
    
    # Привязываем предметы к путям обучения
    for path in dentistry_paths:
        path['subjects'] = [subject for subject in dentistry_subjects if subject['learning_path_id'] == path['id']]
    
    return {
        'learning_paths': dentistry_paths,
        'subjects': dentistry_subjects
    }

def get_profession_specific_data(profession, user_id):
    """Возвращает данные карты обучения в зависимости от профессии"""
    
    if profession == 'farmacie':
        return get_pharmacy_learning_data(user_id)
    elif profession == 'tandheelkunde':
        return get_dentistry_learning_data(user_id)
    elif profession == 'huisartsgeneeskunde':
        return get_gp_learning_data(user_id)
    elif profession == 'verpleegkunde':
        return get_nursing_learning_data(user_id)
    else:
        # Fallback на стоматологические данные
        return get_dentistry_learning_data(user_id)

@profession_map_bp.route('/')
@login_required 
def profession_redirect(lang):
    """Базовый роут - редирект на профессиональную карту пользователя"""
    if not current_user.profession:
        flash('Завершите регистрацию, чтобы получить доступ к карте обучения', 'warning')
        return redirect(url_for('digid.complete_registration', lang=lang))
    
    # Получаем URL профессиональной карты
    profession_slug = None
    for slug, prof_code in PROFESSION_MAPPINGS.items():
        if prof_code == current_user.profession:
            profession_slug = slug
            break
    
    if profession_slug:
        return redirect(url_for('profession_map_bp.profession_learning_map', lang=lang, profession=profession_slug))
    else:
        # Fallback на обычную карту обучения
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))

@profession_map_bp.route('/<string:profession>')
@login_required
def profession_learning_map(lang, profession):
    """Отображает карту обучения для конкретной профессии"""
    
    # Проверяем валидность профессии
    if profession not in PROFESSION_MAPPINGS:
        flash('Неизвестная профессия', 'error')
        return redirect(url_for('profession_map_bp.profession_redirect', lang=lang))
    
    user_profession = current_user.profession
    requested_profession = PROFESSION_MAPPINGS[profession]
    
    # Проверяем права доступа
    if user_profession != requested_profession:
        # Пользователь пытается зайти на чужую карту
        if request.args.get('readonly') == '1':
            # Режим только для чтения
            flash(f'Вы просматриваете карту {PROFESSION_NAMES[profession]} в режиме только для чтения', 'info')
            readonly_mode = True
        else:
            # Блокируем доступ и предлагаем свою карту
            flash(f'У вас нет доступа к карте {PROFESSION_NAMES[profession]}. Перенаправлено на вашу карту.', 'warning')
            return redirect(url_for('profession_map_bp.profession_redirect', lang=lang))
    else:
        readonly_mode = False
    
    try:
        # Получаем профессиональные данные
        profession_data = get_profession_specific_data(profession, current_user.id)
        
        # Статистика пользователя
        stats = get_unified_user_stats(current_user.id)

        # Загружаем общие категории контента
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        # Обрабатываем категории для отображения в карте обучения
        processed_categories = []
        for category in content_categories:
            subcategories = []
            for subcategory in category.subcategories.order_by(ContentSubcategory.order).all():
                topics = []
                for topic in subcategory.topics.order_by(ContentTopic.order).all():
                    lessons_count = Lesson.query.filter_by(topic_id=topic.id).count()
                    topics.append({
                        'id': topic.id,
                        'name': topic.name,
                        'slug': topic.slug,
                        'lessons_count': lessons_count,
                        'url': url_for('content_nav.view_topic', 
                                     lang=lang, 
                                     category_slug=category.slug,
                                     subcategory_slug=subcategory.slug,
                                     topic_slug=topic.slug)
                    })
                
                subcategories.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'topics': topics,
                    'topics_count': len(topics),
                    'url': url_for('content_nav.view_subcategory',
                                 lang=lang,
                                 category_slug=category.slug,
                                 subcategory_slug=subcategory.slug)
                })
            
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'icon': category.icon or 'bi-book',
                'subcategories': subcategories,
                'subcategories_count': len(subcategories),
                'url': url_for('content_nav.view_category',
                             lang=lang,
                             category_slug=category.slug)
            }
            processed_categories.append(category_data)

        # Дополнительный контекст для профессиональных карт
        profession_context = {
            'profession_slug': profession,
            'profession_name': PROFESSION_NAMES[profession],
            'readonly_mode': readonly_mode,
            'user_profession': user_profession,
            'is_own_profession': user_profession == requested_profession
        }
        
        has_completed_diagnostic = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.completed_at.isnot(None),
            DiagnosticSession.session_type != 'daily_practice'
        ).first() is not None

        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()

        schedule = active_plan.get_study_schedule() if active_plan else {}
        schedule_valid = bool(schedule and schedule.get('weekly_schedule'))

        diagnostic_required = (
            not has_completed_diagnostic
            or getattr(current_user, 'requires_diagnostic', False)
            or (active_plan and not schedule_valid)
        )
        
        # Получаем состояние обучения пользователя
        learning_state = get_user_learning_state(current_user.id)
        print(f"🔍 DEBUG: profession_learning_map - learning_state = {learning_state}")
        
        return render_template(
            "learning/learning_map_modern_style.html",
            title=f'Leerkaart - {PROFESSION_NAMES[profession]}',
            lang=lang,
            learning_paths=profession_data['learning_paths'],
            current_path=profession_data['learning_paths'][0] if profession_data['learning_paths'] else None,
            subjects=profession_data['subjects'],
            selected_subject=None,
            user=current_user,
            has_subscription=current_user.has_subscription,
            stats=stats,
            recommendations=get_user_recommendations(current_user.id),
            content_categories=processed_categories,
            content_categories_for_hierarchy=processed_categories,  # Добавляем эту переменную
            profession_context=profession_context,
            learning_state=learning_state,
            diagnostic_completed=has_completed_diagnostic,
            diagnostic_required=diagnostic_required
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash("Произошла ошибка при загрузке карты обучения: " + str(e), "danger")
        return redirect(url_for('main.index', lang=lang))

# --- Языковые и защитные обработчики ---
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

# Import profile check utility
from utils.profile_check import check_profile_complete

@learning_map_bp.before_request
def before_request_learning_map():
    """Выполняется перед каждым запросом к learning_map"""
    # ВАЖНО: Проверяем путь, чтобы не блокировать запросы других blueprints
    # В before_request endpoint еще не установлен, поэтому проверяем путь
    path = request.path or ''
    
    # КРИТИЧНО: Если путь не относится к learning-map, сразу выходим БЕЗ обработки
    # Это предотвращает блокировку запросов к другим blueprints (например, /en/)
    if not path.startswith('/') or '/learning-map' not in path:
        return  # Пропускаем обработку - Flask продолжит поиск правильного endpoint
    
    # Извлекаем язык для редиректов
    lang = request.view_args.get('lang', DEFAULT_LANGUAGE) if request.view_args else DEFAULT_LANGUAGE
    g.lang = lang

    # Gatekeeper: Запретить доступ всем, кроме админов
    if request.endpoint and 'static' not in request.endpoint:
        if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
            # Для неавторизованных либо пусть работает штатный login_required, либо редиректим
            pass 
        elif getattr(current_user, 'role', 'user') != 'admin':
            flash('Обучающий модуль находится в разработке.', 'info')
            return redirect(url_for('profile.profile', lang=lang))
    
    # Очищаем кэш статистики при каждом запросе для актуальности данных
    # Проверяем, что пользователь авторизован перед вызовом функции
    try:
        if hasattr(current_user, 'id') and current_user.is_authenticated:
            clear_user_stats_cache(current_user.id)
    except Exception as e:
        # Игнорируем ошибки очистки кэша, если пользователь не авторизован
        pass
    
    # Извлекаем и валидируем язык из URL
    lang_from_url = request.view_args.get('lang') if request.view_args else None

    # Валидация и установка языка в g
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        # Если в URL нет валидного языка, берем из сессии или accept_languages
        g.lang = session.get('lang') \
                 or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                 or DEFAULT_LANGUAGE

    # Обновляем сессию, если язык отличается
    if session.get('lang') != g.lang:
        session['lang'] = g.lang
    
    # Сохраняем проверку профиля в g для использования в routes
    # Но не блокируем доступ к странице complete-profile
    if (current_user.is_authenticated and 
        request.endpoint != 'learning_map_bp.complete_profile'):
        g.profile_check = check_profile_complete(current_user)

@learning_map_bp.context_processor
def inject_lang_learning_map():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

@learning_map_bp.route("/check-categories")
@login_required
def check_categories(lang):
    """Проверяет категории и создает тестовые данные если их нет"""
    try:
        from models import ContentCategory, ContentSubcategory, ContentTopic
        
        # Проверяем существующие категории
        categories = ContentCategory.query.all()
        
        output = "<h1>Проверка категорий</h1>"
        
        if not categories:
            output += "<p style='color:red'>Категории не найдены. Создаем тестовые данные...</p>"
            
            # Создаем тестовую категорию
            cat = ContentCategory(
                name="Анатомия зуба",
                slug="tooth-anatomy",
                icon="bi-book",
                order=1
            )
            db.session.add(cat)
            db.session.flush()
            
            # Создаем подкатегорию
            subcat = ContentSubcategory(
                name="Строение зуба",
                slug="tooth-structure",
                category_id=cat.id,
                icon="bi-diagram-3",
                order=1
            )
            db.session.add(subcat)
            db.session.flush()
            
            # Создаем тему
            topic = ContentTopic(
                name="Коронка зуба",
                slug="tooth-crown",
                subcategory_id=subcat.id,
                description="Строение коронки зуба",
                order=1
            )
            db.session.add(topic)
            db.session.commit()
            
            output += "<p style='color:green'>Тестовые данные успешно созданы!</p>"
        else:
            output += f"<p>Найдено категорий: {len(categories)}</p>"
            
            for cat in categories:
                output += f"<h2>{cat.name} (ID: {cat.id})</h2>"
                subcats = cat.subcategories.all() if hasattr(cat.subcategories, 'all') else []
                output += f"<p>Подкатегорий: {len(subcats)}</p>"
        
        # Проверяем, правильно ли загружаются категории
        check_cat = ContentCategory.query.first()
        if check_cat:
            output += f"<h3>Тестовая категория загружена:</h3>"
            output += f"<p>ID: {check_cat.id}, Название: {check_cat.name}</p>"
        
        return output
    except Exception as e:
        return f"<h1>Ошибка</h1><p>{str(e)}</p><p>Тип: {type(e).__name__}</p>"

# --- Маршрут отображения карты обучения (обновленный) ---
@learning_map_bp.route("/complete-profile")
@login_required
def complete_profile(lang):
    """Страница с призывом заполнить профиль перед доступом к карте обучения"""
    from utils.profile_check import check_profile_complete, calculate_profile_completion_percentage
    
    profile_check = check_profile_complete(current_user)
    profile_completion_percentage = calculate_profile_completion_percentage(current_user)
    
    return render_template(
        'learning/complete_profile_required.html',
        lang=lang,
        user=current_user,
        profile_check=profile_check,
        profile_completion_percentage=profile_completion_percentage
    )

@learning_map_bp.route("", strict_slashes=False)  # Allow /en/learning-map without trailing slash
@learning_map_bp.route("/", strict_slashes=False)
@learning_map_bp.route("/<string:path_id>", strict_slashes=False)
@login_required
def learning_map(lang, path_id=None):
    """Отображает интерактивную карту обучения."""
    current_lang = g.lang
    
    # Проверка полноты профиля - если неполный, перенаправляем на страницу заполнения
    profile_check = getattr(g, 'profile_check', None)
    if not profile_check:
        profile_check = check_profile_complete(current_user)
    
    if not profile_check['is_complete']:
        flash('Please complete your profile before accessing the learning map.', 'warning')
        return redirect(url_for('learning_map_bp.complete_profile', lang=current_lang))
    
    try:
        # Добавьте явный импорт ContentCategory
        from models import ContentCategory
        
        # Добавьте загрузку категорий
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        print(f"DEBUG: Загружено категорий: {len(content_categories)}")

        for cat in content_categories:
            print(f"DEBUG: Категория: {cat.name}, подкатегорий: {cat.subcategories.count()}")
            for subcat in cat.subcategories.all():
                print(f"DEBUG:   Подкатегория: {subcat.name}, тем: {subcat.topics.count()}")
                for topic in subcat.topics.all():
                    print(f"DEBUG:     Тема: {topic.name}")
        # Определяем, прошел ли пользователь основной скрининг (Gatekeeper)
        has_completed_screening = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.diagnostic_type == 'quick_scan_10',
            DiagnosticSession.completed_at.isnot(None)
        ).first() is not None
        
        has_completed_any_diagnostic = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.completed_at.isnot(None),
            DiagnosticSession.session_type != 'daily_practice'
        ).first() is not None

        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()

        schedule = active_plan.get_study_schedule() if active_plan else {}
        schedule_valid = bool(schedule and schedule.get('weekly_schedule'))

        plan_updated = False
        if active_plan and not schedule_valid:
            rebuilt_schedule = _rebuild_study_schedule_from_sessions(active_plan)
            if rebuilt_schedule:
                active_plan.set_study_schedule(rebuilt_schedule)
                schedule = rebuilt_schedule
                schedule_valid = True
                plan_updated = True
                current_app.logger.info(f"Rebuilt study schedule for plan {active_plan.id} from existing sessions")

        diagnostic_flag_updated = False
        requires_diagnostic_flag = getattr(current_user, 'requires_diagnostic', False)
        if has_completed_diagnostic and requires_diagnostic_flag:
            current_user.requires_diagnostic = False
            diagnostic_flag_updated = True
            current_app.logger.info(f"Diagnostic requirement flag cleared for user {current_user.id}")

        if plan_updated or diagnostic_flag_updated:
            try:
                db.session.commit()
            except Exception as commit_error:
                current_app.logger.error(f"Failed to persist learning map updates for user {current_user.id}: {commit_error}", exc_info=True)
                db.session.rollback()

        diagnostic_required = (
            not has_completed_screening
            or getattr(current_user, 'requires_diagnostic', False)
            or (active_plan and not schedule_valid)
        )
        
        # КРИТИЧНО: Если скрининг не пройден, перенаправляем на диагностику (Gatekeeper)
        if not has_completed_screening and getattr(current_user, 'role', 'user') != 'admin':
            flash('Для начала обучения необходимо пройти диагностический тест Quick Scan 10. Это поможет создать персонализированный план обучения.', 'info')
            current_app.logger.info(f"User {current_user.id} redirected to diagnostic - screening not completed")
            # Используем правильный URL для диагностики
            return redirect(url_for('diagnostic.start_diagnostic_get', lang=lang))

        # Получаем все пути обучения
        learning_paths = LearningPath.query.filter_by(is_active=True).all()
        for path in learning_paths:
            if path.id == 6:  # Virtual Patients
                vp_stats = get_virtual_patients_stats(current_user.id)
                path.vp_stats = vp_stats        
        
        # Если path_id не указан или не найден, используем первый путь
        current_path = None
        if path_id:
            # Если path_id - это строка 'irt', игнорируем её
            if isinstance(path_id, str) and path_id.isdigit():
                current_path = LearningPath.query.get(int(path_id))
            elif isinstance(path_id, int):
                current_path = LearningPath.query.get(path_id)
        
        # Если путь не найден, используем первый доступный
        if not current_path and learning_paths:
            current_path = learning_paths[0]
            path_id = current_path.id
        
        # Получаем выбранный предмет из параметра URL
        selected_subject_id = request.args.get('subject', type=int)
        selected_subject = None
        subject_modules = []
        
        if selected_subject_id:
            selected_subject = Subject.query.get(selected_subject_id)
            if selected_subject:
                # Получаем модули для выбранного предмета
                modules = Module.query.filter_by(subject_id=selected_subject.id).order_by(Module.order).all()
                for module in modules:
                    module_stats = get_module_stats_unified(module.id, current_user.id)
                    subject_modules.append({
                        'id': module.id,
                        'title': module.title,
                        'description': module.description if hasattr(module, 'description') else '',
                        'is_premium': module.is_premium if hasattr(module, 'is_premium') else False,
                        'is_final_test': module.is_final_test if hasattr(module, 'is_final_test') else False,
                        'icon': module.icon if hasattr(module, 'icon') else 'file-earmark-text',
                        'progress': module_stats['progress'],
                        'completed_lessons': module_stats['completed_lessons'],
                        'total_lessons': module_stats['total_lessons']
                    })
        
        # Получаем все предметы с предзагрузкой модулей
        all_subjects = []
        
        # Обрабатываем предметы и их модули
        subjects_query = Subject.query.all()
        for subject in subjects_query:
            # Получаем все модули для этого предмета
            modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
            
            # Обрабатываем каждый модуль
            processed_modules = []
            total_progress = 0
            
            for module in modules:
                # Получаем статистику модуля
                module_stats = get_module_stats_unified(module.id, current_user.id)
                
                # Добавляем модуль с прогрессом
                processed_modules.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description if hasattr(module, 'description') else '',
                    'is_premium': module.is_premium if hasattr(module, 'is_premium') else False,
                    'is_final_test': module.is_final_test if hasattr(module, 'is_final_test') else False,
                    'icon': module.icon if hasattr(module, 'icon') else 'file-earmark-text',
                    'progress': module_stats['progress'],
                    'completed_lessons': module_stats['completed_lessons'],
                    'total_lessons': module_stats['total_lessons']
                })
                
                total_progress += module_stats['progress']
            
            # Вычисляем средний прогресс предмета
            subject_progress = round(total_progress / len(modules)) if modules else 0
            
            # Создаем словарь с информацией о предмете
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description if hasattr(subject, 'description') else '',
                'icon': subject.icon if hasattr(subject, 'icon') else 'folder2-open',
                'learning_path_id': subject.learning_path_id,
                'progress': subject_progress,
                'modules': processed_modules
            }
            
            all_subjects.append(subject_data)
        
        # Статистика пользователя
        stats = get_unified_user_stats(current_user.id)

        # Загружаем категории контента с подкатегориями и темами
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        print(f"🔍 DEBUG: Загружено категорий из БД: {len(content_categories)}")
        
        # Обрабатываем категории для отображения в карте обучения
        processed_categories = []
        for category in content_categories:
            subcategories = []
            for subcategory in category.subcategories.order_by(ContentSubcategory.order).all():
                topics = []
                for topic in subcategory.topics.order_by(ContentTopic.order).all():
                    # Подсчитываем уроки для темы
                    lessons_count = Lesson.query.filter_by(topic_id=topic.id).count()
                    topics.append({
                        'id': topic.id,
                        'name': topic.name,
                        'slug': topic.slug,
                        'lessons_count': lessons_count,
                        'url': url_for('content_nav.view_topic', 
                                     lang=lang, 
                                     category_slug=category.slug,
                                     subcategory_slug=subcategory.slug,
                                     topic_slug=topic.slug)
                    })
                
                subcategories.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'slug': subcategory.slug,
                    'topics': topics,
                    'topics_count': len(topics),
                    'url': url_for('content_nav.view_subcategory',
                                 lang=lang,
                                 category_slug=category.slug,
                                 subcategory_slug=subcategory.slug)
                })
            
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'icon': category.icon or 'bi-book',
                'subcategories': subcategories,
                'subcategories_count': len(subcategories),
                'url': url_for('content_nav.view_category',
                             lang=lang,
                             category_slug=category.slug)
            }
            processed_categories.append(category_data)
            print(f"✅ DEBUG: Обработана категория ID={category.id}, name='{category.name}', подкатегорий={len(subcategories)}")

        
        # Add flashcard data
        try:
            from models import UserTermProgress, MedicalTerm
            from datetime import datetime, timezone, timedelta
            
            # Calculate due reviews count
            due_reviews_count = UserTermProgress.query.filter(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.next_review <= datetime.now(timezone.utc)
            ).count()
            
            # Calculate total terms studied
            total_terms_studied = UserTermProgress.query.filter(
                UserTermProgress.user_id == current_user.id
            ).count()
            
            # Calculate language streak (simplified - terms reviewed in last 7 days)
            from sqlalchemy import func
            last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
            current_language_streak = db.session.query(
                func.count(func.distinct(func.date(UserTermProgress.last_reviewed)))
            ).filter(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.last_reviewed >= last_7_days
            ).scalar() or 0
            
        except Exception as e:
            current_app.logger.error(f"Error loading flashcard data: {e}")
            due_reviews_count = 0
            total_terms_studied = 0
            current_language_streak = 0
        
        # КРИТИЧНО: Обновляем объект пользователя из БД перед рендерингом
        # Это гарантирует, что learning_map_tour_completed загружается актуально
        db.session.refresh(current_user)
        
        return render_template(
                    "learning/learning_map_modern_style.html",  # Новая современная карта обучения
                    title='Learning Map',
                    lang=lang,
                    learning_paths=learning_paths,
                    current_path=current_path,
                    subjects=all_subjects,
                    selected_subject=selected_subject,
                    subject_modules=subject_modules,
                    user=current_user,
                    has_subscription=current_user.has_subscription,
                    stats=stats,
                    recommendations=get_user_recommendations(current_user.id),
                    content_categories=processed_categories,
                    due_reviews_count=due_reviews_count,
                    total_terms_studied=total_terms_studied,
                    current_language_streak=current_language_streak,
                    diagnostic_completed=has_completed_any_diagnostic,
                    diagnostic_required=diagnostic_required
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash("An error occurred while loading the learning map: " + str(e), "danger")
        return redirect(url_for('main.index', lang=current_lang))

# --- НОВЫЙ API-маршрут для запуска модуля ---
@learning_map_bp.route("/api/tour/status", methods=['GET', 'POST'])
@login_required
def tour_status(lang):
    """Get or update learning map tour completion status for user"""
    if request.method == 'GET':
        # Return current tour status - обновляем объект из БД для актуальности
        db.session.refresh(current_user)
        tour_completed = getattr(current_user, 'learning_map_tour_completed', False)
        current_app.logger.debug(f"Tour status GET for user {current_user.id}: {tour_completed}")
        return jsonify({
            'success': True,
            'tour_completed': tour_completed
        })
    else:
        # POST - update tour status
        try:
            data = request.get_json()
            completed = data.get('completed', False)
            
            current_app.logger.info(f"Tour status update request for user {current_user.id}: completed={completed}")
            
            # Обновляем значение в БД
            old_value = getattr(current_user, 'learning_map_tour_completed', False)
            current_user.learning_map_tour_completed = bool(completed)
            db.session.commit()
            
            # Обновляем объект из БД для подтверждения сохранения
            db.session.refresh(current_user)
            new_value = current_user.learning_map_tour_completed
            
            current_app.logger.info(f"Tour status updated for user {current_user.id}: {old_value} -> {new_value}")
            
            return jsonify({
                'success': True,
                'tour_completed': current_user.learning_map_tour_completed
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating tour status for user {current_user.id}: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

@learning_map_bp.route("/api/start-module/<int:module_id>")
@login_required
def start_module(lang, module_id):
    """Начать или продолжить изучение модуля через API"""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Проверяем доступность для пользователя
        if module.is_premium and not current_user.has_subscription:
            return jsonify({
                'success': False, 
                'message': 'This module is only available to premium subscribers'
            }), 403
        
        # Находим первый урок или незавершенный урок
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        lesson = lessons[0] if lessons else None
        
        if lesson:
            redirect_url = url_for('lesson_bp.lesson_view', 
                                   lang=g.lang, 
                                   module_id=module.id, 
                                   lesson_index=0)
            return jsonify({
                'success': True,
                'redirect_url': redirect_url
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No lessons found in this module'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_map_bp.route("/manage-test-data")
@login_required
def manage_test_data(lang):
    """Диагностика и управление тестовыми данными"""
    try:
        # Импортируем здесь явно, чтобы увидеть ошибки импорта
        from models import ContentCategory, ContentSubcategory, ContentTopic
        
        # Проверка существующих данных
        categories = ContentCategory.query.all()
        subcategories = ContentSubcategory.query.all()
        topics = ContentTopic.query.all()
        
        # Если нет данных, создаем тестовые
        if not categories:
            category = ContentCategory(
                name="Анатомия зуба",
                slug="dental-anatomy",
                icon="bi-book",
                order=1
            )
            db.session.add(category)
            db.session.flush()
            
            flash("✅ Создана категория: Анатомия зуба", "success")
        else:
            # Используем существующую категорию
            category = categories[0]
            flash(f"ℹ️ Найдена категория: {category.name}", "info")
        
        if not subcategories:
            subcategory = ContentSubcategory(
                name="Строение зуба",
                slug="tooth-structure",
                category_id=category.id,
                icon="bi-diagram-3",
                order=1
            )
            db.session.add(subcategory)
            db.session.flush()
            
            flash("✅ Создана подкатегория: Строение зуба", "success")
        else:
            # Используем существующую подкатегорию
            subcategory = subcategories[0]
            flash(f"ℹ️ Найдена подкатегория: {subcategory.name}", "info")
        
        if not topics:
            topic = ContentTopic(
                name="Коронка зуба",
                slug="tooth-crown",
                subcategory_id=subcategory.id,
                description="Изучение строения коронки зуба",
                order=1
            )
            db.session.add(topic)
            db.session.flush()
            
            flash("✅ Создана тема: Коронка зуба", "success")
        else:
            # Используем существующую тему
            topic = topics[0]
            flash(f"ℹ️ Найдена тема: {topic.name}", "info")
        
        # Создаем урок, связанный с темой
        modules = Module.query.all()
        if modules:
            module = modules[0]
            
            # Проверяем, есть ли уже уроки в этой теме
            existing_lesson = Lesson.query.filter_by(content_topic_id=topic.id).first()
            
            if not existing_lesson:
                lesson = Lesson(
                    title=f"Урок по теме {topic.name}",
                    module_id=module.id,
                    content_type="learning_card",
                    content_topic_id=topic.id,
                    order=1,
                    content=json.dumps({
                        "cards": [
                            {"title": "Введение", "content": "Содержимое карточки"}
                        ]
                    })
                )
                db.session.add(lesson)
                
                flash(f"✅ Создан урок для темы: {topic.name}", "success")
            else:
                flash(f"ℹ️ Урок для темы {topic.name} уже существует", "info")
        else:
            flash("⚠️ Не найдено ни одного модуля для создания урока", "warning")
        
        # Сохраняем изменения
        db.session.commit()
        
        # Готовим данные для отчета
        report = {
            "categories_count": len(categories),
            "categories": [{"id": c.id, "name": c.name, "subcategories_count": c.subcategories.count() if hasattr(c.subcategories, 'count') else '?'} for c in categories],
            "subcategories_count": len(subcategories),
            "subcategories": [{"id": s.id, "name": s.name, "category_id": s.category_id, "topics_count": s.topics.count() if hasattr(s.topics, 'count') else '?'} for s in subcategories],
            "topics_count": len(topics),
            "topics": [{"id": t.id, "name": t.name, "subcategory_id": t.subcategory_id} for t in topics],
        }
        
        # Возвращаем страницу с отчетом о данных
        return render_template(
            "diagnostic.html",  # Создайте простой шаблон для отображения диагностики
            title="Диагностика данных",
            report=report
        )
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Ошибка: {str(e)}", "danger")
        
        # Возвращаем страницу с информацией об ошибке
        return render_template(
            "diagnostic.html",
            title="Ошибка диагностики",
            error=str(e),
            error_type=type(e).__name__
        )

# --- Существующий маршрут перенаправления ---
@learning_map_bp.route("/start-module/<int:module_id>")
@login_required
def start_module_redirect(lang, module_id):
    """Перенаправляет на правильную страницу модуля"""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Проверяем доступность для пользователя
        if module.is_premium and not current_user.has_subscription:
            flash('This module is only available to premium subscribers', 'warning')
            return redirect(url_for('learning_map_bp.learning_map', lang=g.lang, path_id='irt'))

        # Если это финальный тест
        if module.is_final_test:
            subject = Subject.query.get(module.subject_id)
            return redirect(url_for('tests.start_final_test', lang=g.lang, subject_id=subject.id))
            
        # Перенаправляем на новую страницу модуля
        return redirect(url_for('modules_bp.module_view', lang=g.lang, module_id=module.id))
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error starting module: {str(e)}', 'danger')
        return redirect(url_for('learning_map_bp.learning_map', lang=g.lang, path_id='irt'))

# --- API-эндпоинт ---
@learning_map_bp.route("/api/data/<string:path_id>")
@login_required
def get_learning_map_data(lang, path_id):
    """API-эндпоинт для получения данных карты обучения"""
    try:
        # Получаем запрашиваемый путь обучения
        learning_path = LearningPath.query.get_or_404(path_id)
        
        # Формируем базовый ответ
        result = {
            "path": {
                "id": learning_path.id,
                "name": learning_path.name,
                "description": learning_path.description
            },
            "subjects": []
        }
        
        # Получаем все предметы для этого пути
        subjects = Subject.query.filter_by(learning_path_id=path_id).order_by(subject.order).all()
        
        # Добавляем информацию о каждом предмете
        for subject in subjects:
            # Рассчитываем прогресс предмета
            subject_progress = calculate_subject_progress(subject.id, current_user.id)
            
            subject_data = {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "icon": subject.icon,
                "progress": subject_progress,
                "modules": []
            }
            
            # Получаем модули для предмета
            modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
            
            # Добавляем информацию о каждом модуле
            for module in modules:
                # Получаем статистику для модуля
                module_stats = get_module_stats_unified(module.id, current_user.id)
                
                module_data = {
                    "id": module.id,
                    "title": module.title,
                    "description": module.description,
                    "icon": module.icon,
                    "order": module.order,
                    "is_premium": module.is_premium,
                    "is_final_test": module.is_final_test,
                    "progress": module_stats["progress"],
                    "completed_lessons": module_stats["completed_lessons"],
                    "total_lessons": module_stats["total_lessons"]
                }
                
                subject_data["modules"].append(module_data)
            
            result["subjects"].append(subject_data)
        
        return jsonify(result)
    except Exception as e:
        # Логируем ошибку
        current_app.logger.error(f"Общая ошибка API: {str(e)}")
        # Возвращаем информацию об ошибке в ответе
        return jsonify({
            "error": "Внутренняя ошибка сервера",
            "details": str(e),
            "type": type(e).__name__
        }), 500


# Полная версия функций для расчета и отображения прогресса
def calculate_subject_progress(subject_id, user_id):
    """
    Обертка для обратной совместимости
    Использует унифицированную систему статистики
    """
    return get_subject_stats_unified(subject_id, user_id)

def get_user_recommendations(user_id, limit=3):
    """
    Возвращает рекомендуемые модули для пользователя
    """
    try:
        # Получаем уроки, которые пользователь начал, но не завершил
        in_progress_lesson_ids = db.session.query(UserProgress.lesson_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == False
        ).all()
        in_progress_lesson_ids = [lesson_id[0] for lesson_id in in_progress_lesson_ids]
        
        # Получаем модули для этих уроков
        in_progress_modules = []
        
        if in_progress_lesson_ids:
            in_progress_modules = db.session.query(
                Module, Lesson, Subject.name.label('subject_name')
            ).join(
                Lesson, Lesson.module_id == Module.id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                Lesson.id.in_(in_progress_lesson_ids)
            ).group_by(Module.id).limit(limit).all()
        
        # Если нет незавершенных модулей, рекомендуем популярные или следующие в порядке
        if len(in_progress_modules) < limit:
            # Получаем модули, которые пользователь еще не начал
            remaining_limit = limit - len(in_progress_modules)
            
            completed_module_ids = db.session.query(Module.id).join(
                Lesson, Lesson.module_id == Module.id
            ).join(
                UserProgress, UserProgress.lesson_id == Lesson.id
            ).filter(
                UserProgress.user_id == user_id,
                UserProgress.completed == True
            ).group_by(Module.id).having(
                db.func.count(Lesson.id) == db.func.count(UserProgress.id)
            ).all()
            
            completed_module_ids = [module_id[0] for module_id in completed_module_ids]
            
            # Исключаем модули, которые уже в процессе
            in_progress_module_ids = [module[0].id for module in in_progress_modules]
            
            # Формируем список исключаемых ID
            exclude_ids = completed_module_ids + in_progress_module_ids
            
            # Получаем следующие модули для рекомендации
            next_modules_query = db.session.query(
                Module, Subject.name.label('subject_name')
            ).join(
                Subject, Subject.id == Module.subject_id
            )
            
            # Добавляем фильтр только если есть что исключать
            if exclude_ids:
                next_modules_query = next_modules_query.filter(
                    ~Module.id.in_(exclude_ids)
                )
            
            next_modules = next_modules_query.order_by(
                Module.id
            ).limit(remaining_limit).all()
            
            # Форматируем данные
            next_modules_formatted = [
                {
                    'module_id': module.id,
                    'title': module.title, 
                    'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                    'subject_name': subject_name
                } for module, subject_name in next_modules
            ]
        else:
            next_modules_formatted = []
        
        # Форматируем данные для модулей в процессе
        in_progress_formatted = [
            {
                'module_id': module.id,
                'title': module.title, 
                'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                'subject_name': subject_name
            } for module, lesson, subject_name in in_progress_modules
        ]
        
        # Объединяем результаты
        recommendations = in_progress_formatted + next_modules_formatted
        
        return recommendations[:limit]  # Ограничиваем количество рекомендаций
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении рекомендаций: {str(e)}", exc_info=True)
        return []
    
def get_module_stats(module_id, user_id):
    """
    Обертка для обратной совместимости
    Использует унифицированную систему статистики
    """
    return get_module_stats_unified(module_id, user_id)

# Простое кэширование для get_user_stats
_user_stats_cache = {}

def clear_user_stats_cache(user_id=None):
    """Очищает кэш статистики пользователя"""
    global _user_stats_cache
    if user_id is None:
        _user_stats_cache.clear()
    else:
        _user_stats_cache.pop(user_id, None)

def get_user_stats(user_id):
    """
    Обертка для обратной совместимости
    Использует унифицированную систему статистики
    """
    return get_unified_user_stats(user_id)

def get_virtual_patients_stats(user_id):
    """Получает статистику виртуальных пациентов для пользователя"""
    try:
        # Общее количество сценариев
        total_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).count()
        
        # Завершенные сценарии
        completed_scenarios = db.session.query(VirtualPatientAttempt.scenario_id).filter_by(
            user_id=user_id,
            completed=True
        ).distinct().count()
        
        # Средний балл
        avg_score_data = db.session.query(
            db.func.avg(VirtualPatientAttempt.score).label('avg_score'),
            db.func.avg(VirtualPatientScenario.max_score).label('avg_max_score')
        ).join(
            VirtualPatientScenario,
            VirtualPatientAttempt.scenario_id == VirtualPatientScenario.id
        ).filter(
            VirtualPatientAttempt.user_id == user_id,
            VirtualPatientAttempt.completed == True
        ).first()
        
        avg_percentage = 0
        if avg_score_data and avg_score_data.avg_score and avg_score_data.avg_max_score:
            avg_percentage = round((avg_score_data.avg_score / avg_score_data.avg_max_score) * 100)
        
        return {
            'total': total_scenarios,
            'completed': completed_scenarios,
            'percentage': round((completed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0),
            'avg_score': avg_percentage
        }
    except Exception as e:
        current_app.logger.error(f"Error getting virtual patients stats: {e}")
        return {
            'total': 0,
            'completed': 0,
            'percentage': 0,
            'avg_score': 0
        }

# Добавляем отладочный маршрут для быстрого добавления тестового прогресса
@learning_map_bp.route("/debug/add-progress")
@login_required
def debug_add_progress(lang):
    """Временный маршрут для добавления тестового прогресса"""
    try:
        # Получаем несколько уроков для тестирования
        lessons = Lesson.query.limit(5).all()
        
        if not lessons:
            flash("Уроки не найдены в базе данных", "warning")
            return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
            
        added_count = 0
        lesson_info = []
        
        for lesson in lessons:
            # Проверяем, есть ли уже запись прогресса
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            
            status = 'existing'
            
            if not progress:
                # Создаем новую запись
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=lesson.id,
                    completed=True,
                    time_spent=10.0  # Тестовое значение времени
                )
                db.session.add(progress)
                added_count += 1
                status = 'created'
            elif not progress.completed:
                # Обновляем существующую запись
                progress.completed = True
                progress.time_spent = (progress.time_spent or 0.0) + 10.0
                added_count += 1
                status = 'updated'
                
            # Собираем информацию об уроке для отладки
            module = Module.query.get(lesson.module_id)
            lesson_info.append({
                'id': lesson.id,
                'title': lesson.title,
                'module_id': lesson.module_id,
                'module_title': module.title if module else 'Unknown',
                'status': status
            })
                
        # Сохраняем изменения в базе данных
        db.session.commit()
        
        # Получаем обновленную статистику пользователя
        stats = get_unified_user_stats(current_user.id)
        
        # Отображаем подробную страницу с информацией о прогрессе
        return render_template(
            "debug_progress.html",
            stats=stats,
            lessons=lesson_info,
            added_count=added_count
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении тестового прогресса: {str(e)}", exc_info=True)
        flash(f"❌ Ошибка при добавлении тестового прогресса: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
    
    
@learning_map_bp.route("/debug/progress-status")
@login_required
def debug_progress_status(lang):
    """Отладочный маршрут для отображения текущего состояния прогресса"""
    try:
        # Получаем все записи прогресса для текущего пользователя
        progress_entries = UserProgress.query.filter_by(
            user_id=current_user.id
        ).all()
        
        # Группируем по статусу
        completed_entries = [p for p in progress_entries if p.completed]
        incomplete_entries = [p for p in progress_entries if not p.completed]
        
        # Получаем статистику
        stats = get_unified_user_stats(current_user.id)
        
        # Подробная информация о прогрессе уроков
        lessons_progress = []
        for entry in progress_entries:
            lesson = Lesson.query.get(entry.lesson_id)
            if lesson:
                module = Module.query.get(lesson.module_id)
                lessons_progress.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'module_id': lesson.module_id,
                    'module_title': module.title if module else 'Unknown',
                    'completed': entry.completed,
                    'time_spent': entry.time_spent,
                    'last_accessed': entry.last_accessed
                })
        
        # Статистика модулей
        modules_stats = []
        for module in Module.query.all():
            module_stats = get_module_stats_unified(module.id, current_user.id)
            modules_stats.append({
                'id': module.id,
                'title': module.title,
                'progress': module_stats['progress'],
                'completed_lessons': module_stats['completed_lessons'],
                'total_lessons': module_stats['total_lessons']
            })
        
        # Сортируем модули по прогрессу (от наибольшего к наименьшему)
        modules_stats.sort(key=lambda x: x['progress'], reverse=True)
        
        # Сортируем уроки по времени доступа (последние сверху)
        lessons_progress.sort(key=lambda x: x['last_accessed'] if x.get('last_accessed') else datetime.min, reverse=True)
        
        return render_template(
            "debug_progress_status.html",
            stats=stats,
            lessons_progress=lessons_progress,
            modules_stats=modules_stats,
            completed_count=len(completed_entries),
            incomplete_count=len(incomplete_entries),
            total_count=len(progress_entries)
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении статистики прогресса: {str(e)}", exc_info=True)
        flash(f"❌ Ошибка при получении статистики прогресса: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
    
@learning_map_bp.route('/api/path/<string:path_id>/subjects')
def get_path_subjects(path_id):
    # Получаем язык из g, установленный в middleware
    lang = g.lang
    
    # Получаем путь по ID
    path = LearningPath.query.get_or_404(path_id)
    
    # Получаем предметы этого пути
    subjects = Subject.query.filter_by(learning_path_id=path_id).all()
    
    # Формируем ответ в JSON
    subjects_data = []
    for subject in subjects:
        # Вычисляем прогресс для данного пользователя
        progress = 0
        if current_user.is_authenticated:
            # Получаем прогресс предмета (адаптируйте этот код согласно вашей системе)
            # Пример расчета прогресса (замените на свою логику):
            lessons_complete = UserProgress.query.join(Lesson).join(Module).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.completed == True,
                Module.subject_id == subject.id
            ).count()
            
            # Общее количество уроков в предмете
            total_lessons = Lesson.query.join(Module).filter(
                Module.subject_id == subject.id
            ).count()
            
            if total_lessons > 0:
                progress = round((lessons_complete / total_lessons) * 100)
        
        subjects_data.append({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'progress': progress
        })
    
    return jsonify({
        'path_id': path_id,
        'path_name': path.name,
        'path_description': path.description,
        'subjects': subjects_data,
        'learning_map_text': t('learning_map', lang)
    })

@learning_map_bp.route('/path/<string:path_id>')
@login_required  # Добавляем декоратор для авторизации
def view_path(lang, path_id):
    """Отображает предметы выбранного учебного пути."""
    try:
        # Получаем путь по ID
        path = LearningPath.query.get_or_404(path_id)
        
        # Логирование вместо print
        current_app.logger.info(f"Запрошен путь ID: {path_id}, название: {path.name}")
        
        # Получаем предметы этого пути
        path_subjects = Subject.query.filter_by(learning_path_id=path_id).all()
        
        # Логирование информации о предметах
        current_app.logger.info(f"Найдено предметов: {len(path_subjects)}")
        for subject in path_subjects:
            current_app.logger.info(f"  - Предмет: {subject.id}, {subject.name}")
        
        # Получаем все пути (для левой колонки)
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        
        # Получаем все предметы (с сортировкой для предсказуемости)
        subjects = Subject.query.order_by(Subject.name).all()
        
        # Получаем категории контента
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        # Получаем статистику пользователя
        stats = get_unified_user_stats(current_user.id)
        
        # Получаем рекомендации
        recommendations = get_user_recommendations(current_user.id)
        
        # Добавляем скрипт для активации категории
        extra_scripts = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Активируем выбранную категорию
            const pathId = "%s";
            
            // Активируем соответствующую кнопку в левом меню
            const pathButton = document.querySelector(`.learning-path-button[data-path="${pathId}"]`);
            if (pathButton) {
                // Программно нажимаем на кнопку
                pathButton.click();
            }
            
            // Активируем кнопку в мобильном меню
            const mobileButton = document.querySelector(`.mobile-nav-item[data-path="${pathId}"]`);
            if (mobileButton) {
                mobileButton.classList.add('active');
            }
        });
        </script>
        """ % path_id
        
        has_completed_diagnostic = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.completed_at.isnot(None),
            DiagnosticSession.session_type != 'daily_practice'
        ).first() is not None

        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()

        schedule = active_plan.get_study_schedule() if active_plan else {}
        schedule_valid = bool(schedule and schedule.get('weekly_schedule'))

        diagnostic_required = (
            not has_completed_diagnostic
            or getattr(current_user, 'requires_diagnostic', False)
            or (active_plan and not schedule_valid)
        )
        
        return render_template(
            'learning/learning_map_modern_style.html',
            lang=lang,
            learning_paths=learning_paths,
            subjects=subjects,
            selected_path=path,
            selected_subject=None,
            subject_modules=None,
            stats=stats,
            recommendations=recommendations,
            content_categories=content_categories,
            extra_scripts=extra_scripts,  # Передаем скрипт в шаблон
            diagnostic_completed=has_completed_diagnostic,
            diagnostic_required=diagnostic_required
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка при отображении пути {path_id}: {str(e)}", exc_info=True)
        flash(f"Ошибка при загрузке данных: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
    
@learning_map_bp.route("/debug/post-rollback-check")
@login_required
def post_rollback_check(lang):
    """Диагностика после отката"""
    try:
        html = ["<h1>🔍 Диагностика после отката</h1>"]
        
        # 1. Проверяем Git состояние
        try:
            # Текущий коммит
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
            current_commit = result.stdout.strip()[:8]
            
            # Текущая ветка
            result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
            current_branch = result.stdout.strip()
            
            # Последний коммит
            result = subprocess.run(['git', 'log', '-1', '--oneline'], capture_output=True, text=True)
            last_commit = result.stdout.strip()
            
            html.append(f"""
            <h2>1. Git состояние</h2>
            <ul>
                <li><strong>Текущая ветка:</strong> {current_branch}</li>
                <li><strong>Текущий коммит:</strong> {current_commit}</li>
                <li><strong>Последний коммит:</strong> {last_commit}</li>
            </ul>
            """)
        except Exception as e:
            html.append(f"<h2>1. Git состояние</h2><p style='color:red'>Ошибка получения Git информации: {e}</p>")
        
        # 2. Проверяем базу данных
        html.append("<h2>2. Состояние базы данных</h2>")
        
        paths = LearningPath.query.all()
        subjects = Subject.query.all()
        modules = Module.query.all()
        lessons = Lesson.query.all()
        
        html.append(f"""
        <table border='1' style='border-collapse: collapse;'>
            <tr><th>Таблица</th><th>Количество записей</th></tr>
            <tr><td>LearningPath</td><td>{len(paths)}</td></tr>
            <tr><td>Subject</td><td>{len(subjects)}</td></tr>
            <tr><td>Module</td><td>{len(modules)}</td></tr>
            <tr><td>Lesson</td><td>{len(lessons)}</td></tr>
        </table>
        """)
        
        # 3. Детальная проверка структуры
        html.append("<h2>3. Структура данных</h2>")
        
        if not paths:
            html.append("<p style='color:red;'>❌ <strong>ПРОБЛЕМА: Нет путей обучения!</strong></p>")
        elif not subjects:
            html.append("<p style='color:red;'>❌ <strong>ПРОБЛЕМА: Нет предметов!</strong></p>")
        elif not modules:
            html.append("<p style='color:red;'>❌ <strong>ПРОБЛЕМА: Нет модулей!</strong></p>")
        elif not lessons:
            html.append("<p style='color:red;'>❌ <strong>ПРОБЛЕМА: Нет уроков!</strong></p>")
        else:
            html.append("<p style='color:green;'>✅ Все таблицы содержат данные</p>")
            
            # Детальная структура
            for path in paths[:3]:  # Показываем первые 3 пути
                path_subjects = Subject.query.filter_by(learning_path_id=path.id).all()
                html.append(f"<h4>Path: {path.name} ({len(path_subjects)} предметов)</h4>")
                
                if path_subjects:
                    html.append("<ul>")
                    for subject in path_subjects[:3]:  # Первые 3 предмета
                        subject_modules = Module.query.filter_by(subject_id=subject.id).all()
                        html.append(f"<li>{subject.name} ({len(subject_modules)} модулей)")
                        
                        if subject_modules:
                            html.append("<ul>")
                            for module in subject_modules[:2]:  # Первые 2 модуля
                                module_lessons = Lesson.query.filter_by(module_id=module.id).all()
                                html.append(f"<li>{module.title} ({len(module_lessons)} уроков)</li>")
                            html.append("</ul>")
                        html.append("</li>")
                    html.append("</ul>")
        
        # 4. Проверяем файл базы данных
        html.append("<h2>4. Файл базы данных</h2>")
        
        db_files = []
        for filename in ['database.db', 'app.db', 'dental_academy.db', 'instance/database.db']:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                db_files.append(f"{filename} ({size} bytes)")
        
        if db_files:
            html.append("<ul>")
            for db_file in db_files:
                html.append(f"<li>{db_file}</li>")
            html.append("</ul>")
        else:
            html.append("<p style='color:red;'>❌ Файлы базы данных не найдены!</p>")
        
        # 5. Проверяем конфигурацию
        html.append("<h2>5. Конфигурация Flask</h2>")
        html.append(f"""
        <ul>
            <li><strong>DATABASE_URL:</strong> {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Не установлен')}</li>
            <li><strong>DEBUG:</strong> {current_app.config.get('DEBUG', False)}</li>
            <li><strong>ENV:</strong> {current_app.config.get('ENV', 'Не установлен')}</li>
        </ul>
        """)
        
        # 6. Действия для исправления
        html.append("<h2>6. Возможные решения</h2>")
        html.append(f"""
        <ul>
            <li><a href="{url_for('learning_map_bp.recreate_database', lang=lang)}" style="color: red;">🗑️ Пересоздать базу данных</a> (удалит все данные!)</li>
            <li><a href="{url_for('learning_map_bp.create_sample_data', lang=lang)}" style="color: green;">➕ Создать тестовые данные</a></li>
            <li><a href="{url_for('learning_map_bp.import_github_data', lang=lang)}" style="color: blue;">📥 Импортировать данные из GitHub</a></li>
        </ul>
        """)
        
        return "".join(html)
        
    except Exception as e:
        import traceback
        return f"<h1>❌ Ошибка диагностики</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

@learning_map_bp.route("/debug/recreate-database")
@login_required
def recreate_database(lang):
    """ОПАСНО: Пересоздает базу данных"""
    try:
        # Удаляем все таблицы
        db.drop_all()
        
        # Создаем заново
        db.create_all()
        
        flash("⚠️ База данных пересоздана! Все данные удалены.", "warning")
        return redirect(url_for('learning_map_bp.create_sample_data', lang=lang))
        
    except Exception as e:
        flash(f"❌ Ошибка пересоздания БД: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.post_rollback_check', lang=lang))

@learning_map_bp.route("/debug/create-sample-data")
@login_required
def create_sample_data(lang):
    """Создает тестовые данные для проверки"""
    try:
        # Проверяем, есть ли уже данные
        if LearningPath.query.first():
            flash("⚠️ Данные уже существуют. Создание отменено.", "warning")
            return redirect(url_for('learning_map_bp.post_rollback_check', lang=lang))
        
        # Создаем тестовые данные
        # Learning Paths
        path1 = LearningPath(name="Theory (MCQ)", description="Multiple choice questions", order=1, is_active=True)
        path2 = LearningPath(name="Виртуальные пациенты", description="Virtual patient cases", order=2, is_active=True)
        
        db.session.add_all([path1, path2])
        db.session.flush()
        
        # Subjects
        subject1 = Subject(name="THK I: Cariology/Endo/Perio/Pedo", description="Basic dental subjects", learning_path_id=path1.id, order=1)
        subject2 = Subject(name="THK II: Prostho/Surgery/Ortho", description="Advanced dental subjects", learning_path_id=path1.id, order=2)
        
        db.session.add_all([subject1, subject2])
        db.session.flush()
        
        # Modules
        module1 = Module(title="Основы кариологии", description="Изучение кариеса", subject_id=subject1.id, order=1)
        module2 = Module(title="Эндодонтия", description="Лечение корневых каналов", subject_id=subject1.id, order=2)
        module3 = Module(title="Ортопедия", description="Протезирование", subject_id=subject2.id, order=1)
        
        db.session.add_all([module1, module2, module3])
        db.session.flush()
        
        # Lessons
        lesson1 = Lesson(title="Урок 1: Что такое кариес", content="Основы понимания кариеса", module_id=module1.id, order=1)
        lesson2 = Lesson(title="Урок 2: Стадии кариеса", content="Развитие кариозного процесса", module_id=module1.id, order=2)
        lesson3 = Lesson(title="Урок 1: Анатомия корневых каналов", content="Строение корней", module_id=module2.id, order=1)
        
        db.session.add_all([lesson1, lesson2, lesson3])
        db.session.commit()
        
        flash("✅ Тестовые данные успешно созданы!", "success")
        return redirect(url_for('learning_map_bp.post_rollback_check', lang=lang))
        
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Ошибка создания тестовых данных: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.post_rollback_check', lang=lang))

@learning_map_bp.route("/debug/import-github-data")
@login_required
def import_github_data(lang):
    """Заглушка для импорта данных из GitHub"""
    flash("📥 Функция импорта данных из GitHub пока не реализована.", "info")
    return redirect(url_for('learning_map_bp.post_rollback_check', lang=lang))

@learning_map_bp.route("/debug/test-caries")
@login_required
def test_caries(lang):
    """Тест отображения Caries"""
    try:
        # Находим Caries
        caries_subject = Subject.query.filter_by(name="Caries").first()
        
        if not caries_subject:
            return "<h1>❌ Предмет Caries не найден!</h1>"
        
        # Получаем модули Caries
        caries_modules = Module.query.filter_by(subject_id=caries_subject.id).all()
        
        # Получаем уроки первого модуля
        first_module = caries_modules[0] if caries_modules else None
        lessons = Lesson.query.filter_by(module_id=first_module.id).all() if first_module else []
        
        html = f"""
        <h1>🧪 Тест Caries</h1>
        
        <h2>Предмет Caries</h2>
        <p><strong>ID:</strong> {caries_subject.id}</p>
        <p><strong>Name:</strong> {caries_subject.name}</p>
        <p><strong>Learning Path ID:</strong> {caries_subject.learning_path_id}</p>
        
        <h2>Модули ({len(caries_modules)})</h2>
        """
        
        if caries_modules:
            for module in caries_modules:
                module_lessons = Lesson.query.filter_by(module_id=module.id).all()
                html += f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
                    <h3>{module.title}</h3>
                    <p><strong>ID:</strong> {module.id}</p>
                    <p><strong>Уроков:</strong> {len(module_lessons)}</p>
                    <p><strong>Описание:</strong> {getattr(module, 'description', 'Нет описания')}</p>
                    
                    <h4>Первые 5 уроков:</h4>
                    <ul>
                """
                
                for lesson in module_lessons[:5]:
                    html += f"<li>{lesson.title}</li>"
                
                html += "</ul></div>"
        else:
            html += "<p style='color: red;'>❌ Нет модулей!</p>"
        
        # Тест прямой ссылки
        if caries_subject:
            html += f"""
            <h2>Прямая ссылка</h2>
            <p><a href="{url_for('subject_view_bp.view_subject', lang=lang, subject_id=caries_subject.id)}" 
                  style="background: green; color: white; padding: 10px; text-decoration: none;">
                🎯 Открыть Caries напрямую
            </a></p>
            """
        
        # Тест через карту обучения
        html += f"""
        <h2>Через карту обучения</h2>
        <p><a href="{url_for('learning_map_bp.learning_map', lang=lang, path_id='irt')}" 
              style="background: blue; color: white; padding: 10px; text-decoration: none;">
            🗺️ Открыть карту обучения
        </a></p>
        
        <h3>Инструкции:</h3>
        <ol>
            <li>Кликните на <strong>"Exams"</strong> в левом меню</li>
            <li>Найдите <strong>"Caries"</strong> в списке предметов</li>
            <li>Кликните на <strong>"Caries"</strong></li>
            <li>Должен появиться модуль с 19 уроками</li>
        </ol>
        """
        
        return html
        
    except Exception as e:
        import traceback
        return f"<h1>❌ Ошибка теста</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"
    
@learning_map_bp.route("/subject/<int:subject_id>/tests")
@login_required
def subject_tests(lang, subject_id):
    """Отображает тесты для конкретного предмета"""
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Получаем все тесты для предмета
        tests = Test.query.filter_by(subject_final_test_id=subject_id).all()
        
        # Получаем все категории вопросов для предмета
        categories = QuestionCategory.query.filter_by(subject_id=subject_id).all()
        
        # Собираем статистику по тестам
        test_stats = {}
        if current_user.is_authenticated:
            for test in tests:
                attempts = TestAttempt.query.filter_by(
                    user_id=current_user.id,
                    test_id=test.id
                ).all()
                
                if attempts:
                    best_score = max(attempt.score for attempt in attempts)
                    total_attempts = len(attempts)
                else:
                    best_score = 0
                    total_attempts = 0
                
                test_stats[test.id] = {
                    'best_score': best_score,
                    'total_attempts': total_attempts,
                    'passed': best_score >= test.passing_score if test.passing_score else False
                }
        
        return render_template(
            'learning/subject_tests.html',
            subject=subject,
            tests=tests,
            categories=categories,
            test_stats=test_stats
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при отображении тестов: {str(e)}")
        flash("Er is een fout opgetreden bij het laden van de tests.", "error")
        return redirect(url_for('learning_map_bp.learning_map', lang=g.lang, path_id='irt'))

# === ФУНКЦИИ ПРОВЕРКИ СОСТОЯНИЯ === #

def check_diagnostic_completed(user_id):
    """Проверить, прошел ли пользователь диагностику"""
    try:
        # Проверяем наличие завершенной диагностической сессии
        diagnostic_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.started_at.desc()).first()
        
        return diagnostic_session is not None
    except Exception as e:
        print(f"Error checking diagnostic completion: {e}")
        return False

def check_learning_progress(user_id):
    """Проверить, есть ли прогресс в обучении"""
    try:
        # Проверяем наличие ЗАВЕРШЕННОГО прогресса в уроках
        lesson_progress = UserProgress.query.filter_by(
            user_id=user_id,
            completed=True
        ).first()
        
        # Проверяем наличие ЗАВЕРШЕННЫХ попыток тестов (с положительным результатом)
        test_progress = TestAttempt.query.filter_by(
            user_id=user_id,
            is_correct=True
        ).first()
        
        # Проверяем наличие ЗАВЕРШЕННЫХ попыток виртуальных пациентов
        vp_progress = VirtualPatientAttempt.query.filter_by(
            user_id=user_id,
            completed=True
        ).first()
        
        return lesson_progress is not None or test_progress is not None or vp_progress is not None
    except Exception as e:
        print(f"Error checking learning progress: {e}")
        return False

def get_user_learning_state(user_id):
    """Получить полное состояние обучения пользователя"""
    print(f"🔍 DEBUG: get_user_learning_state called for user_id = {user_id}")
    
    # Отладочная информация
    debug_user_state(user_id)
    
    diagnostic_completed = check_diagnostic_completed(user_id)
    learning_progress = check_learning_progress(user_id)
    
    # ИСПРАВЛЕННАЯ ЛОГИКА:
    # Этап 1 (pre_diagnostic): Нет диагностики
    # Этап 2 (post_diagnostic): Есть диагностика (независимо от прогресса)
    stage = 'post_diagnostic' if diagnostic_completed else 'pre_diagnostic'
    
    result = {
        'diagnostic_completed': diagnostic_completed,
        'learning_progress': learning_progress,
        'stage': stage
    }
    
    print(f"🔍 DEBUG: get_user_learning_state result = {result}")
    return result

def debug_user_state(user_id):
    """Отладочная функция для проверки состояния пользователя"""
    print(f"🔍 DEBUG: Checking user state for user_id = {user_id}")
    
    # Проверяем диагностические сессии
    diagnostic_sessions = DiagnosticSession.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: Diagnostic sessions count: {len(diagnostic_sessions)}")
    for session in diagnostic_sessions:
        print(f"🔍 DEBUG: Diagnostic session - status: {session.status}, started_at: {session.started_at}")
    
    # Проверяем прогресс обучения
    lesson_progress = UserProgress.query.filter_by(user_id=user_id, completed=True).all()
    print(f"🔍 DEBUG: Completed lesson progress count: {len(lesson_progress)}")
    
    test_progress = TestAttempt.query.filter_by(user_id=user_id, is_correct=True).all()
    print(f"🔍 DEBUG: Correct test attempts count: {len(test_progress)}")
    
    vp_progress = VirtualPatientAttempt.query.filter_by(user_id=user_id, completed=True).all()
    print(f"🔍 DEBUG: Completed VP attempts count: {len(vp_progress)}")
    
    # Проверяем все попытки тестов (включая неправильные)
    all_test_attempts = TestAttempt.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: All test attempts count: {len(all_test_attempts)}")
    
    # Проверяем все попытки VP (включая незавершенные)
    all_vp_attempts = VirtualPatientAttempt.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: All VP attempts count: {len(all_vp_attempts)}")
    
    return {
        'diagnostic_sessions': len(diagnostic_sessions),
        'completed_lessons': len(lesson_progress),
        'correct_tests': len(test_progress),
        'completed_vp': len(vp_progress),
        'all_tests': len(all_test_attempts),
        'all_vp': len(all_vp_attempts)
    }

@learning_map_bp.route("/subject/<int:subject_id>/topics")
@login_required
def subject_topics(lang, subject_id):
    """Отображает темы предмета напрямую, минуя промежуточную страницу с модулями."""
    current_lang = g.lang
    
    try:
        # Получаем предмет
        subject = Subject.query.get_or_404(subject_id)
        
        # Получаем модули предмета
        modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
        
        # Собираем все темы из всех модулей
        all_topics = []
        
        for module in modules:
            lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
            
            for lesson in lessons:
                if lesson.content:
                    try:
                        content_data = json.loads(lesson.content)
                        
                        # Извлекаем module_title из контента
                        if 'cards' in content_data and content_data['cards']:
                            first_card = content_data['cards'][0]
                            topic_title = first_card.get('module_title', lesson.title)
                        elif 'questions' in content_data and content_data['questions']:
                            first_question = content_data['questions'][0]
                            topic_title = first_question.get('module_title', lesson.title)
                        else:
                            topic_title = lesson.title
                        
                        # Проверяем, что контент соответствует предмету
                        # Для всех предметов - все темы из их модулей подходят
                        # Фильтрация не нужна, так как контент уже правильно загружен в соответствующие модули
                        pass  # Не фильтруем, все темы из модулей предмета подходят
                        
                        # Создаем slug для темы
                        from routes.modules_routes import create_slug
                        topic_slug = create_slug(topic_title)
                        
                        # Получаем статистику урока
                        lesson_stats = get_module_stats_unified(lesson.id, current_user.id)
                        
                        topic_data = {
                            'id': lesson.id,
                            'title': topic_title,
                            'slug': topic_slug,
                            'module_id': module.id,
                            'module_title': module.title,
                            'content_type': lesson.content_type,
                            'progress': lesson_stats['progress'],
                            'completed_lessons': lesson_stats['completed_lessons'],
                            'total_lessons': lesson_stats['total_lessons']
                        }
                        
                        all_topics.append(topic_data)
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        current_app.logger.warning(f"Error parsing lesson {lesson.id}: {e}")
                        continue
        
        # Убираем дубликаты тем (если есть)
        unique_topics = []
        seen_titles = set()
        
        for topic in all_topics:
            if topic['title'] not in seen_titles:
                unique_topics.append(topic)
                seen_titles.add(topic['title'])
        
        # Получаем статистику пользователя
        stats = get_unified_user_stats(current_user.id)
        
        # Получаем рекомендации
        from routes.subject_view_routes import get_user_recommendations
        recommendations = get_user_recommendations(current_user.id)
        
        return render_template(
            "learning/subject_topics.html",
            title=f'{subject.name} - Topics',
            subject=subject,
            topics=unique_topics,
            user=current_user,
            has_subscription=current_user.has_subscription,
            stats=stats,
            recommendations=recommendations,
            lang=lang
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in subject_topics: {e}", exc_info=True)
        flash("Error loading subject topics", "error")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))

def get_diagnostic_based_recommendations(user_id, limit=5):
    """
    Возвращает рекомендуемые модули на основе результатов диагностики
    Фокусируется на слабых доменах (показатели < 50%)
    """
    try:
        # Получаем последнюю завершенную диагностическую сессию
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_diagnostic:
            # Если нет диагностики, возвращаем обычные рекомендации
            return get_user_recommendations(user_id, limit)
        
        # Получаем результаты диагностики
        diagnostic_results = latest_diagnostic.generate_results()
        weak_domains = diagnostic_results.get('weak_domains', [])
        
        if not weak_domains:
            # Если нет слабых доменов, возвращаем обычные рекомендации
            return get_user_recommendations(user_id, limit)
        
        # Получаем домены BIG
        from models import BIGDomain
        weak_domain_objects = BIGDomain.query.filter(
            BIGDomain.code.in_(weak_domains)
        ).all()
        
        # Получаем модули, связанные со слабыми доменами
        recommended_modules = []
        
        for domain in weak_domain_objects:
            # Ищем модули, связанные с этим доменом через ContentDomainMapping
            from models import ContentDomainMapping, Module, Subject
            
            domain_modules = db.session.query(
                Module, Subject.name.label('subject_name')
            ).join(
                ContentDomainMapping, ContentDomainMapping.module_id == Module.id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                ContentDomainMapping.domain_id == domain.id,
                ContentDomainMapping.relevance_score >= 0.5  # Только релевантные модули
            ).order_by(
                ContentDomainMapping.relevance_score.desc()
            ).limit(limit // len(weak_domain_objects) + 1).all()
            
            for module, subject_name in domain_modules:
                # Проверяем, не завершил ли пользователь уже этот модуль
                completed_lessons = db.session.query(UserProgress).join(
                    Lesson, Lesson.id == UserProgress.lesson_id
                ).filter(
                    UserProgress.user_id == user_id,
                    UserProgress.completed == True,
                    Lesson.module_id == module.id
                ).count()
                
                total_lessons = module.lessons.count()
                
                if total_lessons > 0 and (completed_lessons / total_lessons) < 0.8:  # Не завершен на 80%
                    recommended_modules.append({
                        'module_id': module.id,
                        'title': module.title,
                        'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                        'subject_name': subject_name,
                        'domain_name': domain.name,
                        'domain_code': domain.code,
                        'relevance_score': 0.8,  # Высокая релевантность для слабых доменов
                        'completion_percentage': (completed_lessons / total_lessons) * 100,
                        'priority': 'high'  # Высокий приоритет для слабых доменов
                    })
        
        # Сортируем по приоритету и релевантности
        recommended_modules.sort(
            key=lambda x: (x['priority'] == 'high', x['relevance_score'], -x['completion_percentage']),
            reverse=True
        )
        
        return recommended_modules[:limit]
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении рекомендаций на основе диагностики: {str(e)}", exc_info=True)
        # В случае ошибки возвращаем обычные рекомендации
        return get_user_recommendations(user_id, limit)

@learning_map_bp.route("/start-diagnostic-learning")
@login_required
def start_diagnostic_learning(lang):
    """
    Начинает обучение с модулей, соответствующих слабым доменам из диагностики
    """
    try:
        # Получаем рекомендации на основе диагностики
        recommendations = get_diagnostic_based_recommendations(current_user.id, limit=1)
        
        if not recommendations:
            # Если нет рекомендаций, перенаправляем на обычную карту обучения
            flash(t('no_diagnostic_recommendations', lang) | default('No diagnostic recommendations available. Please complete a knowledge assessment first.'), 'info')
            return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
        
        # Берем первый рекомендуемый модуль
        recommended_module = recommendations[0]
        module_id = recommended_module['module_id']
        
        # Перенаправляем на первый урок этого модуля
        module = Module.query.get(module_id)
        if not module:
            flash(t('module_not_found', lang) | default('Module not found.'), 'error')
            return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
        
        # Получаем первый урок модуля
        first_lesson = module.lessons.order_by(Lesson.order).first()
        if not first_lesson:
            flash(t('no_lessons_in_module', lang) | default('No lessons found in this module.'), 'error')
            return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))
        
        # Перенаправляем на интерактивный урок
        return redirect(url_for('modules_bp.subtopic_lessons_list', 
                               lang=lang, 
                               module_id=module_id, 
                               slug=first_lesson.subtopic_slug or 'learning-materials'))
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при начале обучения на основе диагностики: {str(e)}", exc_info=True)
        flash(t('error_starting_diagnostic_learning', lang) | default('Error starting diagnostic-based learning.'), 'error')
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))


    stage = 'post_diagnostic' if diagnostic_completed else 'pre_diagnostic'
    
    result = {
        'diagnostic_completed': diagnostic_completed,
        'learning_progress': learning_progress,
        'stage': stage
    }
    
    print(f"🔍 DEBUG: get_user_learning_state result = {result}")
    return result

def debug_user_state(user_id):
    """Отладочная функция для проверки состояния пользователя"""
    print(f"🔍 DEBUG: Checking user state for user_id = {user_id}")
    
    # Проверяем диагностические сессии
    diagnostic_sessions = DiagnosticSession.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: Diagnostic sessions count: {len(diagnostic_sessions)}")
    for session in diagnostic_sessions:
        print(f"🔍 DEBUG: Diagnostic session - status: {session.status}, started_at: {session.started_at}")
    
    # Проверяем прогресс обучения
    lesson_progress = UserProgress.query.filter_by(user_id=user_id, completed=True).all()
    print(f"🔍 DEBUG: Completed lesson progress count: {len(lesson_progress)}")
    
    test_progress = TestAttempt.query.filter_by(user_id=user_id, is_correct=True).all()
    print(f"🔍 DEBUG: Correct test attempts count: {len(test_progress)}")
    
    vp_progress = VirtualPatientAttempt.query.filter_by(user_id=user_id, completed=True).all()
    print(f"🔍 DEBUG: Completed VP attempts count: {len(vp_progress)}")
    
    # Проверяем все попытки тестов (включая неправильные)
    all_test_attempts = TestAttempt.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: All test attempts count: {len(all_test_attempts)}")
    
    # Проверяем все попытки VP (включая незавершенные)
    all_vp_attempts = VirtualPatientAttempt.query.filter_by(user_id=user_id).all()
    print(f"🔍 DEBUG: All VP attempts count: {len(all_vp_attempts)}")
    
    return {
        'diagnostic_sessions': len(diagnostic_sessions),
        'completed_lessons': len(lesson_progress),
        'correct_tests': len(test_progress),
        'completed_vp': len(vp_progress),
        'all_tests': len(all_test_attempts),
        'all_vp': len(all_vp_attempts)
    }

@learning_map_bp.route("/subject/<int:subject_id>/topics")
def get_diagnostic_based_recommendations(user_id, limit=5):
    """
    Возвращает рекомендуемые модули на основе результатов диагностики
    Фокусируется на слабых доменах (показатели < 50%)
    """
    try:
        # Получаем последнюю завершенную диагностическую сессию
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_diagnostic:
            # Если нет диагностики, возвращаем обычные рекомендации
            return get_user_recommendations(user_id, limit)
        
        # Получаем результаты диагностики
        diagnostic_results = latest_diagnostic.generate_results()
        weak_domains = diagnostic_results.get('weak_domains', [])
        
        if not weak_domains:
            # Если нет слабых доменов, возвращаем обычные рекомендации
            return get_user_recommendations(user_id, limit)
        
        # Получаем домены BIG
        from models import BIGDomain
        weak_domain_objects = BIGDomain.query.filter(
            BIGDomain.code.in_(weak_domains)
        ).all()
        
        # Получаем модули, связанные со слабыми доменами
        recommended_modules = []
        
        for domain in weak_domain_objects:
            # Ищем модули, связанные с этим доменом через ContentDomainMapping
            from models import ContentDomainMapping, Module, Subject
            
            domain_modules = db.session.query(
                Module, Subject.name.label('subject_name')
            ).join(
                ContentDomainMapping, ContentDomainMapping.module_id == Module.id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                ContentDomainMapping.domain_id == domain.id,
                ContentDomainMapping.relevance_score >= 0.5  # Только релевантные модули
            ).order_by(
                ContentDomainMapping.relevance_score.desc()
            ).limit(limit // len(weak_domain_objects) + 1).all()
            
            for module, subject_name in domain_modules:
                # Проверяем, не завершил ли пользователь уже этот модуль
                completed_lessons = db.session.query(UserProgress).join(
                    Lesson, Lesson.id == UserProgress.lesson_id
                ).filter(
                    UserProgress.user_id == user_id,
                    UserProgress.completed == True,
                    Lesson.module_id == module.id
                ).count()
                
                total_lessons = module.lessons.count()
                
                if total_lessons > 0 and (completed_lessons / total_lessons) < 0.8:  # Не завершен на 80%
                    recommended_modules.append({
                        'module_id': module.id,
                        'title': module.title,
                        'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                        'subject_name': subject_name,
                        'domain_name': domain.name,
                        'domain_code': domain.code,
                        'relevance_score': 0.8,  # Высокая релевантность для слабых доменов
                        'completion_percentage': (completed_lessons / total_lessons) * 100,
                        'priority': 'high'  # Высокий приоритет для слабых доменов
                    })
        
        # Сортируем по приоритету и релевантности
        recommended_modules.sort(
            key=lambda x: (x['priority'] == 'high', x['relevance_score'], -x['completion_percentage']),
            reverse=True
        )
        
        return recommended_modules[:limit]
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении рекомендаций на основе диагностики: {str(e)}", exc_info=True)
        # В случае ошибки возвращаем обычные рекомендации
        return get_user_recommendations(user_id, limit)

