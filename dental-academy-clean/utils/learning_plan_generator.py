#!/usr/bin/env python3
"""
Генератор персонализированных планов обучения
Анализирует результаты диагностики и создает адаптивный план
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional
from models import User, PersonalLearningPlan, DiagnosticSession, BIGDomain, Question, Lesson, Module, Subject, StudySession
from extensions import db
import math
from utils.content_recommendations import get_smart_recommendations
from models import UserProgress, TestResult

# Конвертер из generate_results() в формат планировщика
def convert_diagnostic_to_planner_format(diagnostic_data):
    """Конвертирует данные диагностики в формат для планировщика"""
    print(f"🔍 ОТЛАДКА: convert_diagnostic_to_planner_format вызвана")
    print(f"🔍 ОТЛАДКА: diagnostic_data keys = {list(diagnostic_data.keys())}")
    
    # ВСЕ 25 доменов BIG экзамена
    ALL_BIG_DOMAINS = {
        'domain_1': 'Endodontics',
        'domain_2': 'Periodontics', 
        'domain_3': 'Orthodontics',
        'domain_4': 'Oral Surgery',
        'domain_5': 'Prosthodontics',
        'domain_6': 'Preventive Care',
        'domain_7': 'Dental Materials',
        'domain_8': 'Oral Pathology',
        'domain_9': 'Oral Medicine',
        'domain_10': 'Dental Radiology',
        'domain_11': 'Dental Anatomy',
        'domain_12': 'Dental Physiology',
        'domain_13': 'Dental Pharmacology',
        'domain_14': 'Dental Anesthesia',
        'domain_15': 'Dental Emergency',
        'domain_16': 'Dental Ethics',
        'domain_17': 'Dental Law',
        'domain_18': 'Practice Management',
        'domain_19': 'Patient Communication',
        'domain_20': 'Infection Control',
        'domain_21': 'Dental Implants',
        'domain_22': 'Cosmetic Dentistry',
        'domain_23': 'Pediatric Dentistry',
        'domain_24': 'Geriatric Dentistry',
        'domain_25': 'Special Needs Dentistry'
    }
    
    # Маппинг старых доменов на новые
    OLD_TO_NEW_DOMAIN_MAPPING = {
        'THER': 'domain_1',      # Терапевтическая стоматология -> Endodontics
        'SURG': 'domain_4',      # Хирургическая стоматология -> Oral Surgery
        'PROTH': 'domain_5',     # Ортопедическая стоматология -> Prosthodontics
        'PEDI': 'domain_23',     # Детская стоматология -> Pediatric Dentistry
        'PARO': 'domain_2',      # Пародонтология -> Periodontics
        'ORTHO': 'domain_3',     # Ортодонтия -> Orthodontics
        'PREV': 'domain_6',      # Профилактика -> Preventive Care
        'ETHIEK': 'domain_16',   # Этика и право -> Dental Ethics
        'ANATOMIE': 'domain_11', # Анатомия -> Dental Anatomy
        'FYSIOLOGIE': 'domain_12', # Физиология -> Dental Physiology
        'PATHOLOGIE': 'domain_8', # Патология -> Oral Pathology
        'MICROBIOLOGIE': 'domain_20', # Микробиология -> Infection Control
        'MATERIAALKUNDE': 'domain_7', # Материаловедение -> Dental Materials
        'RADIOLOGIE': 'domain_10', # Рентгенология -> Dental Radiology
        'ALGEMENE_GENEESKUNDE': 'domain_9', # Общая медицина -> Oral Medicine
        'EMERGENCY': 'domain_15', # Неотложная помощь -> Dental Emergency
        'SYSTEMIC': 'domain_9',  # Системные заболевания -> Oral Medicine
        'PHARMA': 'domain_13',   # Фармакология -> Dental Pharmacology
        'INFECTION': 'domain_20', # Инфекционный контроль -> Infection Control
        'SPECIAL': 'domain_25',  # Специальные группы пациентов -> Special Needs Dentistry
        'DIAGNOSIS': 'domain_8', # Сложная диагностика -> Oral Pathology
        'DUTCH': 'domain_18',    # Голландская система здравоохранения -> Practice Management
        'PROFESSIONAL': 'domain_17', # Профессиональное развитие -> Dental Law
        'FARMACOLOGIE': 'domain_13', # Фармакология (альтернативное название) -> Dental Pharmacology
        'DIAGNOSIS_SPECIAL': 'domain_8' # Специальная диагностика -> Oral Pathology
    }
    
    converted = {}
    
    print(f"🔍 ОТЛАДКА: Обрабатываем ВСЕ 25 доменов...")
    
    for domain_code, domain_name in ALL_BIG_DOMAINS.items():
        print(f"🔍 ОТЛАДКА: обрабатываем домен {domain_code} = {domain_name}")
        
        # Проверяем есть ли данные по этому домену (прямое совпадение)
        if (diagnostic_data.get('domain_statistics') and 
            domain_code in diagnostic_data['domain_statistics'] and
            diagnostic_data['domain_statistics'][domain_code].get('has_data', False)):
            
            # Есть прямые данные
            domain_data = diagnostic_data['domain_statistics'][domain_code]
            score = domain_data.get('accuracy_percentage', 0)
            questions_answered = domain_data.get('questions_answered', 0)
            correct_answers = domain_data.get('correct_answers', 0)
            print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет прямые данные: {score}%")
        else:
            # Проверяем маппинг старых доменов
            score = 0
            questions_answered = 0
            correct_answers = 0
            
            # Ищем старый домен, который маппится на этот новый
            for old_domain, new_domain in OLD_TO_NEW_DOMAIN_MAPPING.items():
                if new_domain == domain_code:
                    if (diagnostic_data.get('domain_statistics') and 
                        old_domain in diagnostic_data['domain_statistics'] and
                        diagnostic_data['domain_statistics'][old_domain].get('has_data', False)):
                        
                        # Нашли данные в старом домене
                        old_domain_data = diagnostic_data['domain_statistics'][old_domain]
                        score = old_domain_data.get('accuracy_percentage', 0)
                        questions_answered = old_domain_data.get('questions_answered', 0)
                        correct_answers = old_domain_data.get('correct_answers', 0)
                        print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет данные из старого домена {old_domain}: {score}%")
                        break
            
            if score == 0:
                print(f"🔍 ОТЛАДКА: Домен {domain_name} без данных: 0%")
        
        converted[domain_name] = {
            'domain_code': domain_code,
            'score': score,
            'questions_answered': questions_answered,
            'correct_answers': correct_answers,
            'accuracy': score,
            'target': 85,  # Целевой балл
            'hours': max(24 - score * 0.3, 8)  # Расчет часов
        }
        print(f"🔍 ОТЛАДКА: конвертирован домен {domain_name} = {converted[domain_name]}")
    
    print(f"🔍 ОТЛАДКА: итоговый converted = {converted}")
    print(f"🔍 ОТЛАДКА: всего доменов = {len(converted)}")
    return converted

class LearningPlanGenerator:
    """Генератор персонализированных планов обучения"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
        
    def generate_plan(self, exam_date: Optional[datetime] = None) -> PersonalLearningPlan:
        """Генерирует персонализированный план обучения"""
        
        # Получаем последнюю диагностическую сессию
        diagnostic_session = self._get_latest_diagnostic()
        if not diagnostic_session:
            raise ValueError("Не найдена диагностическая сессия. Сначала пройдите диагностику.")
        
        # Анализируем результаты диагностики
        domain_analysis = self._analyze_diagnostic_results(diagnostic_session)
        
        # Определяем слабые и сильные области
        weak_domains, strong_domains = self._identify_domain_strengths(domain_analysis)
        
        # Рассчитываем целевую способность
        target_ability = self._calculate_target_ability(exam_date)
        
        # Создаем расписание обучения
        study_schedule = self._create_study_schedule(weak_domains, exam_date)
        
        # Создаем вехи
        milestones = self._create_milestones(exam_date)
        
        # Создаем план обучения
        plan = PersonalLearningPlan(
            user_id=self.user_id,
            exam_date=exam_date.date() if exam_date else None,
            target_ability=target_ability,
            study_hours_per_week=20.0,  # Можно сделать настраиваемым
            current_ability=diagnostic_session.current_ability,
            overall_progress=0.0,
            estimated_readiness=self._calculate_readiness(diagnostic_session.current_ability, target_ability),
            status='active'
        )
        
        # Устанавливаем данные
        plan.set_domain_analysis(domain_analysis)
        plan.set_weak_domains(weak_domains)
        plan.set_strong_domains(strong_domains)
        plan.set_study_schedule(study_schedule)
        plan.set_milestones(milestones)
        
        return plan
    
    def _get_latest_diagnostic(self) -> Optional[DiagnosticSession]:
        """Получает последнюю диагностическую сессию пользователя"""
        return DiagnosticSession.query.filter_by(
            user_id=self.user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
    
    def _analyze_diagnostic_results(self, diagnostic_session: DiagnosticSession) -> Dict:
        """Анализирует результаты диагностики по доменам"""
        
        # Получаем все ответы пользователя
        responses = diagnostic_session.responses.all()
        
        # Группируем ответы по доменам
        domain_results = {}
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        for domain in domains:
            # Ищем вопросы этого домена через связь с вопросами
            domain_questions = []
            for response in responses:
                question = response.question
                if question and hasattr(question, 'big_domain_id') and question.big_domain_id == domain.id:
                    domain_questions.append(response)
            
            if domain_questions:
                correct_count = sum(1 for r in domain_questions if r.is_correct)
                total_count = len(domain_questions)
                accuracy = correct_count / total_count
                
                # Рассчитываем среднюю способность для домена
                abilities = [r.ability_after for r in domain_questions if r.ability_after is not None]
                avg_ability = sum(abilities) / len(abilities) if abilities else 0.0
                
                domain_results[domain.name] = {
                    'domain_id': domain.id,
                    'domain_code': domain.code,
                    'questions_answered': total_count,
                    'correct_answers': correct_count,
                    'accuracy': accuracy,
                    'average_ability': avg_ability,
                    'weight_percentage': domain.weight_percentage,
                    "difficulty_level": "medium",
                    'recommended_focus': accuracy < 0.7,  # Фокус если точность < 70%
                    'estimated_hours_needed': self._estimate_hours_needed(accuracy, domain.weight_percentage)
                }
            else:
                # Если нет вопросов для домена, создаем базовую запись
                domain_results[domain.name] = {
                    'domain_id': domain.id,
                    'domain_code': domain.code,
                    'questions_answered': 0,
                    'correct_answers': 0,
                    'accuracy': 0.0,
                    'average_ability': 0.0,
                    'weight_percentage': domain.weight_percentage,
                    "difficulty_level": "medium",
                    'recommended_focus': True,  # Фокус если нет данных
                    'estimated_hours_needed': self._estimate_hours_needed(0.0, domain.weight_percentage)
                }
        
        return domain_results
    
    def _identify_domain_strengths(self, domain_analysis: Dict) -> Tuple[List[str], List[str]]:
        """Определяет слабые и сильные области"""
        
        weak_domains = []
        strong_domains = []
        
        for domain_name, analysis in domain_analysis.items():
            if analysis['recommended_focus']:
                weak_domains.append(domain_name)
            else:
                strong_domains.append(domain_name)
        
        return weak_domains, strong_domains
    
    def _calculate_target_ability(self, exam_date: Optional[datetime]) -> float:
        """Рассчитывает целевую способность для экзамена"""
        
        # Базовая целевая способность для BIG экзамена
        base_target = 0.7  # 70% вероятность успешной сдачи
        
        if exam_date:
            # Преобразуем exam_date в datetime если это date
            from datetime import date
            if isinstance(exam_date, date):
                exam_datetime = datetime.combine(exam_date, datetime.min.time())
            else:
                exam_datetime = exam_date
            
            days_until_exam = (exam_datetime - datetime.now(timezone.utc)).days
            
            # Корректируем цель в зависимости от времени до экзамена
            if days_until_exam < 30:
                base_target = 0.8  # Высокая цель для близкого экзамена
            elif days_until_exam < 90:
                base_target = 0.75  # Средняя цель
            else:
                base_target = 0.7  # Базовая цель для далекого экзамена
        
        return base_target
    
    def _create_study_schedule(self, weak_domains: List[str], exam_date: Optional[datetime]) -> Dict:
        """Создает расписание обучения"""
        
        # Определяем количество недель
        if exam_date:
            # Преобразуем exam_date в datetime если это date
            from datetime import date
            if isinstance(exam_date, date):
                exam_datetime = datetime.combine(exam_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            else:
                exam_datetime = exam_date
            
            weeks_until_exam = max(1, (exam_datetime - datetime.now(timezone.utc)).days // 7)
        else:
            weeks_until_exam = 12  # По умолчанию 12 недель
        
        # Распределяем слабые области по неделям
        weekly_schedule = []
        
        for week_num in range(1, weeks_until_exam + 1):
            week_domains = self._assign_domains_to_week(weak_domains, week_num, weeks_until_exam)
            
            # Создаем ежедневные сессии
            daily_sessions = self._create_daily_sessions(week_domains, week_num)
            
            weekly_schedule.append({
                'week_number': week_num,
                'focus_domains': week_domains,
                'daily_sessions': daily_sessions,
                'milestone_test': week_num % 2 == 0,  # Тест каждые 2 недели
                'estimated_hours': sum(session['duration'] for session in daily_sessions)
            })
        
        return {
            'total_weeks': weeks_until_exam,
            'weekly_schedule': weekly_schedule,
            'total_hours': sum(week['estimated_hours'] for week in weekly_schedule)
        }
    
    def _assign_domains_to_week(self, weak_domains: List[str], week_num: int, total_weeks: int) -> List[str]:
        """Распределяет домены по неделям"""
        
        if not weak_domains:
            return []
        
        # Простое распределение: каждую неделю фокусируемся на 1-2 доменах
        domains_per_week = max(1, len(weak_domains) // total_weeks)
        start_idx = (week_num - 1) * domains_per_week
        end_idx = min(start_idx + domains_per_week, len(weak_domains))
        
        return weak_domains[start_idx:end_idx]
    
    def _create_daily_sessions(self, week_domains: List[str], week_num: int) -> List[Dict]:
        """Создает ежедневные сессии для недели"""
        
        sessions = []
        session_types = ['theory', 'practice', 'theory', 'practice', 'review', 'test', 'review']
        
        for day, session_type in enumerate(session_types, 1):
            session = {
                'day': day,
                'type': session_type,
                'duration': self._get_session_duration(session_type),
                'focus_domains': week_domains if session_type in ['theory', 'practice'] else [],
                'description': self._get_session_description(session_type, week_domains)
            }
            sessions.append(session)
        
        return sessions
    
    def _get_session_duration(self, session_type: str) -> float:
        """Возвращает длительность сессии в часах"""
        durations = {
            'theory': 2.0,
            'practice': 2.0,
            'review': 1.0,
            'test': 1.5
        }
        return durations.get(session_type, 1.5)
    
    def _get_session_description(self, session_type: str, domains: List[str]) -> str:
        """Возвращает описание сессии"""
        domain_names = ', '.join(domains) if domains else 'общие темы'
        
        descriptions = {
            'theory': f'Изучение теории по темам: {domain_names}',
            'practice': f'Практические упражнения по темам: {domain_names}',
            'review': f'Повторение изученного материала',
            'test': f'Проверка знаний по пройденным темам'
        }
        return descriptions.get(session_type, 'Учебная сессия')
    
    def _create_milestones(self, exam_date: Optional[datetime]) -> List[Dict]:
        """Создает реальные вехи на основе прогресса пользователя"""
        
        milestones = []
        
        # Получаем реальный прогресс пользователя
        user_progress = self._get_user_real_progress()
        
        # Веха 1: Первые уроки (5 завершенных уроков)
        if user_progress['completed_lessons'] >= 5:
            milestones.append({
                'title': 'Первые шаги',
                'description': f'Завершено {user_progress["completed_lessons"]} уроков',
                'target_date': user_progress.get('first_completion_date'),
                'type': 'first_lessons',
                'week': 1,
                'completed': True,
                'progress': min(100, (user_progress['completed_lessons'] / 5) * 100)
            })
        else:
            milestones.append({
                'title': 'Первые шаги',
                'description': f'Завершите 5 уроков (прогресс: {user_progress["completed_lessons"]}/5)',
                'target_date': None,
                'type': 'first_lessons',
                'week': 1,
                'completed': False,
                'progress': (user_progress['completed_lessons'] / 5) * 100
            })
        
        # Веха 2: Время обучения (10 часов)
        if user_progress['total_time_spent'] >= 600:  # 600 минут = 10 часов
            milestones.append({
                'title': 'Время обучения',
                'description': f'Потрачено {user_progress["total_time_spent"] // 60} часов на обучение',
                'target_date': user_progress.get('time_milestone_date'),
                'type': 'study_time',
                'week': 2,
                'completed': True,
                'progress': 100
            })
        else:
            hours_spent = user_progress['total_time_spent'] // 60
            milestones.append({
                'title': 'Время обучения',
                'description': f'Потратьте 10 часов на обучение (прогресс: {hours_spent}/10 ч)',
                'target_date': None,
                'type': 'study_time',
                'week': 2,
                'completed': False,
                'progress': (hours_spent / 10) * 100
            })
        
        # Веха 3: Модули (завершить 3 модуля)
        if user_progress['completed_modules'] >= 3:
            milestones.append({
                'title': 'Освоение модулей',
                'description': f'Завершено {user_progress["completed_modules"]} модулей',
                'target_date': user_progress.get('modules_milestone_date'),
                'type': 'modules',
                'week': 3,
                'completed': True,
                'progress': 100
            })
        else:
            milestones.append({
                'title': 'Освоение модулей',
                'description': f'Завершите 3 модуля (прогресс: {user_progress["completed_modules"]}/3)',
                'target_date': None,
                'type': 'modules',
                'week': 3,
                'completed': False,
                'progress': (user_progress['completed_modules'] / 3) * 100
            })
        
        # Веха 4: Тесты (пройти 5 тестов с результатом >70%)
        if user_progress['good_tests'] >= 5:
            milestones.append({
                'title': 'Тестирование',
                'description': f'Пройдено {user_progress["good_tests"]} тестов с результатом >70%',
                'target_date': user_progress.get('tests_milestone_date'),
                'type': 'testing',
                'week': 4,
                'completed': True,
                'progress': 100
            })
        else:
            milestones.append({
                'title': 'Тестирование',
                'description': f'Пройдите 5 тестов с результатом >70% (прогресс: {user_progress["good_tests"]}/5)',
                'target_date': None,
                'type': 'testing',
                'week': 4,
                'completed': False,
                'progress': (user_progress['good_tests'] / 5) * 100
            })
        
        # Веха 5: Домены (изучить 5 доменов)
        if user_progress['studied_domains'] >= 5:
            milestones.append({
                'title': 'Изучение доменов',
                'description': f'Изучено {user_progress["studied_domains"]} доменов BIG',
                'target_date': user_progress.get('domains_milestone_date'),
                'type': 'domains',
                'week': 5,
                'completed': True,
                'progress': 100
            })
        else:
            milestones.append({
                'title': 'Изучение доменов',
                'description': f'Изучите 5 доменов BIG (прогресс: {user_progress["studied_domains"]}/5)',
                'target_date': None,
                'type': 'domains',
                'week': 5,
                'completed': False,
                'progress': (user_progress['studied_domains'] / 5) * 100
            })
        
        # Веха 6: Диагностика (пройти диагностический тест)
        if user_progress['diagnostic_completed']:
            milestones.append({
                'title': 'Диагностика',
                'description': f'Диагностический тест пройден с результатом {user_progress["diagnostic_score"]:.1f}%',
                'target_date': user_progress.get('diagnostic_date'),
                'type': 'diagnostic',
                'week': 6,
                'completed': True,
                'progress': 100
            })
        else:
            milestones.append({
                'title': 'Диагностика',
                'description': 'Пройдите диагностический тест для оценки готовности',
                'target_date': None,
                'type': 'diagnostic',
                'week': 6,
                'completed': False,
                'progress': 0
            })
        
        return milestones
    
    def _get_user_real_progress(self) -> Dict:
        """Получает реальный прогресс пользователя"""
        
        # Завершенные уроки
        completed_lessons = UserProgress.query.filter_by(
            user_id=self.user_id,
            completed=True
        ).count()
        
        # Общее время обучения (в минутах)
        total_time_spent = db.session.query(
            db.func.sum(UserProgress.time_spent)
        ).filter_by(
            user_id=self.user_id
        ).scalar() or 0
        
        # Завершенные модули
        completed_modules = 0
        modules = Module.query.all()
        for module in modules:
            module_progress = module.get_progress_for_user(self.user_id)
            if module_progress['progress_percent'] == 100:
                completed_modules += 1
        
        # Тесты с хорошим результатом (>70%)
        good_tests = 0
        test_results = TestResult.query.filter_by(user_id=self.user_id).all()
        for result in test_results:
            if result.percentage_score > 70:
                good_tests += 1
        
        # Изученные домены (через диагностику)
        studied_domains = 0
        diagnostic_sessions = DiagnosticSession.query.filter_by(
            user_id=self.user_id,
            status='completed'
        ).all()
        
        for session in diagnostic_sessions:
            results = session.generate_results()
            domain_abilities = results.get('domain_abilities', {})
            studied_domains = len(domain_abilities)
            break  # Берем последнюю диагностику
        
        # Диагностический тест
        diagnostic_completed = False
        diagnostic_score = 0
        diagnostic_date = None
        
        if diagnostic_sessions:
            latest_diagnostic = diagnostic_sessions[-1]
            diagnostic_completed = True
            results = latest_diagnostic.generate_results()
            diagnostic_score = results.get('accuracy', 0) * 100
            diagnostic_date = latest_diagnostic.completed_at
        
        # Даты достижения вех
        first_completion = UserProgress.query.filter_by(
            user_id=self.user_id,
            completed=True
        ).order_by(UserProgress.completed_at.asc()).first()
        
        first_completion_date = first_completion.completed_at if first_completion else None
        
        return {
            'completed_lessons': completed_lessons,
            'total_time_spent': total_time_spent,
            'completed_modules': completed_modules,
            'good_tests': good_tests,
            'studied_domains': studied_domains,
            'diagnostic_completed': diagnostic_completed,
            'diagnostic_score': diagnostic_score,
            'diagnostic_date': diagnostic_date,
            'first_completion_date': first_completion_date,
            'time_milestone_date': None,  # Можно добавить логику определения
            'modules_milestone_date': None,
            'tests_milestone_date': None,
            'domains_milestone_date': None
        }
    
    def _calculate_domain_difficulty(self, domain_questions: List) -> str:
        """Рассчитывает сложность домена на основе вопросов"""
        
        if not domain_questions:
            return 'medium'
        
        # Используем среднюю сложность вопросов
        difficulties = []
        for q in domain_questions:
            if hasattr(q.question, 'irt_parameters') and q.question.irt_parameters:
                irt_params = q.question.irt_parameters
                if hasattr(irt_params, 'difficulty'):
                    difficulties.append(irt_params.difficulty)
        
        if not difficulties:
            return 'medium'
        
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        if avg_difficulty < -0.5:
            return 'easy'
        elif avg_difficulty > 0.5:
            return 'hard'
        else:
            return 'medium'
    
    def _estimate_hours_needed(self, accuracy: float, weight_percentage: float) -> float:
        """Оценивает количество часов, необходимых для изучения домена"""
        
        # Базовое время зависит от веса домена
        base_hours = weight_percentage * 0.2  # 20% от веса домена
        
        # Корректируем на основе точности
        if accuracy < 0.5:
            multiplier = 2.0  # Нужно больше времени
        elif accuracy < 0.7:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        return base_hours * multiplier
    
    def _calculate_readiness(self, current_ability: float, target_ability: float) -> float:
        """Рассчитывает готовность к экзамену"""
        
        if current_ability >= target_ability:
            return 1.0
        
        # Простая линейная интерполяция
        readiness = current_ability / target_ability
        return min(1.0, max(0.0, readiness))
    
    def get_recommended_lessons(self, domain_names: List[str], limit: int = 5) -> List[Lesson]:
        """Получает рекомендованные уроки для доменов"""
        
        # Используем умную систему рекомендаций
        return get_smart_recommendations(self.user_id, domain_names, limit)
    
    def update_plan_progress(self, plan: PersonalLearningPlan) -> None:
        """Обновляет прогресс плана на основе выполненных сессий"""
        
        # Получаем выполненные сессии
        completed_sessions = plan.study_sessions.filter_by(status='completed').all()
        
        if not completed_sessions:
            return
        
        # Рассчитываем общий прогресс
        total_sessions = plan.study_sessions.count()
        completed_count = len(completed_sessions)
        
        progress_percent = (completed_count / total_sessions * 100) if total_sessions > 0 else 0
        
        # Обновляем план
        plan.overall_progress = progress_percent
        plan.last_updated = datetime.now(timezone.utc)
        
        # Пересчитываем готовность
        plan.estimated_readiness = self._calculate_readiness(
            plan.current_ability, 
            plan.target_ability
        )
        
        db.session.commit()

def create_learning_plan_from_diagnostic(
    user_id: int, 
    exam_date: Optional[datetime] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    intensity: str = 'moderate',
    study_time: str = 'afternoon',
    diagnostic_session_id: Optional[int] = None
) -> PersonalLearningPlan:
    """Создает план обучения на основе диагностики"""
    
    print(f"🔍 ОТЛАДКА: create_learning_plan_from_diagnostic вызвана")
    print(f"🔍 ОТЛАДКА: user_id = {user_id}")
    print(f"🔍 ОТЛАДКА: diagnostic_session_id = {diagnostic_session_id}")
    
    # ВСЕ 25 доменов BIG экзамена
    ALL_BIG_DOMAINS = {
        'domain_1': 'Endodontics',
        'domain_2': 'Periodontics', 
        'domain_3': 'Orthodontics',
        'domain_4': 'Oral Surgery',
        'domain_5': 'Prosthodontics',
        'domain_6': 'Preventive Care',
        'domain_7': 'Dental Materials',
        'domain_8': 'Oral Pathology',
        'domain_9': 'Oral Medicine',
        'domain_10': 'Dental Radiology',
        'domain_11': 'Dental Anatomy',
        'domain_12': 'Dental Physiology',
        'domain_13': 'Dental Pharmacology',
        'domain_14': 'Dental Anesthesia',
        'domain_15': 'Dental Emergency',
        'domain_16': 'Dental Ethics',
        'domain_17': 'Dental Law',
        'domain_18': 'Practice Management',
        'domain_19': 'Patient Communication',
        'domain_20': 'Infection Control',
        'domain_21': 'Dental Implants',
        'domain_22': 'Cosmetic Dentistry',
        'domain_23': 'Pediatric Dentistry',
        'domain_24': 'Geriatric Dentistry',
        'domain_25': 'Special Needs Dentistry'
    }
    
    # Маппинг старых доменов на новые
    OLD_TO_NEW_DOMAIN_MAPPING = {
        'THER': 'domain_1',      # Терапевтическая стоматология -> Endodontics
        'SURG': 'domain_4',      # Хирургическая стоматология -> Oral Surgery
        'PROTH': 'domain_5',     # Ортопедическая стоматология -> Prosthodontics
        'PEDI': 'domain_23',     # Детская стоматология -> Pediatric Dentistry
        'PARO': 'domain_2',      # Пародонтология -> Periodontics
        'ORTHO': 'domain_3',     # Ортодонтия -> Orthodontics
        'PREV': 'domain_6',      # Профилактика -> Preventive Care
        'ETHIEK': 'domain_16',   # Этика и право -> Dental Ethics
        'ANATOMIE': 'domain_11', # Анатомия -> Dental Anatomy
        'FYSIOLOGIE': 'domain_12', # Физиология -> Dental Physiology
        'PATHOLOGIE': 'domain_8', # Патология -> Oral Pathology
        'MICROBIOLOGIE': 'domain_20', # Микробиология -> Infection Control
        'MATERIAALKUNDE': 'domain_7', # Материаловедение -> Dental Materials
        'RADIOLOGIE': 'domain_10', # Рентгенология -> Dental Radiology
        'ALGEMENE_GENEESKUNDE': 'domain_9', # Общая медицина -> Oral Medicine
        'EMERGENCY': 'domain_15', # Неотложная помощь -> Dental Emergency
        'SYSTEMIC': 'domain_9',  # Системные заболевания -> Oral Medicine
        'PHARMA': 'domain_13',   # Фармакология -> Dental Pharmacology
        'INFECTION': 'domain_20', # Инфекционный контроль -> Infection Control
        'SPECIAL': 'domain_25',  # Специальные группы пациентов -> Special Needs Dentistry
        'DIAGNOSIS': 'domain_8', # Сложная диагностика -> Oral Pathology
        'DUTCH': 'domain_18',    # Голландская система здравоохранения -> Practice Management
        'PROFESSIONAL': 'domain_17', # Профессиональное развитие -> Dental Law
        'FARMACOLOGIE': 'domain_13', # Фармакология (альтернативное название) -> Dental Pharmacology
        'DIAGNOSIS_SPECIAL': 'domain_8' # Специальная диагностика -> Oral Pathology
    }
    
    # Получаем КОНКРЕТНУЮ сессию, а не последнюю
    if diagnostic_session_id:
        diagnostic_session = DiagnosticSession.query.get(diagnostic_session_id)
        print(f"🔍 ОТЛАДКА: diagnostic_session = {diagnostic_session}")
        print(f"🔍 ОТЛАДКА: diagnostic_session.id = {diagnostic_session.id if diagnostic_session else 'None'}")
        print(f"🔍 ОТЛАДКА: diagnostic_session.status = {diagnostic_session.status if diagnostic_session else 'None'}")
        
        if not diagnostic_session:
            raise ValueError(f"Diagnostic session {diagnostic_session_id} not found")
        if diagnostic_session.user_id != user_id:
            raise ValueError("Diagnostic session does not belong to user")
        if diagnostic_session.status != 'completed':
            raise ValueError("Diagnostic session is not completed")
    else:
        # Fallback: получаем последнюю сессию
        print(f"🔍 ОТЛАДКА: diagnostic_session_id не указан, ищем последнюю сессию")
        diagnostic_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        print(f"🔍 ОТЛАДКА: найдена последняя сессия = {diagnostic_session}")
        
        if not diagnostic_session:
            raise ValueError("No completed diagnostic session found")
    
    # Используем generate_results() вместо _analyze_diagnostic_results()
    print(f"🔍 ОТЛАДКА: вызываем diagnostic_session.generate_results()")
    diagnostic_data = diagnostic_session.generate_results()
    print(f"🔍 ОТЛАДКА: diagnostic_data = {diagnostic_data}")
    print(f"🔍 ОТЛАДКА: domain_statistics = {diagnostic_data.get('domain_statistics', {})}")
    
    # Создаем данные для ВСЕХ 25 доменов
    print(f"🔍 ОТЛАДКА: создаем данные для ВСЕХ 25 доменов")
    all_domains_data = {}
    
    for domain_code, domain_name in ALL_BIG_DOMAINS.items():
        print(f"🔍 ОТЛАДКА: обрабатываем домен {domain_code} = {domain_name}")
        
        # Проверяем есть ли данные по этому домену (прямое совпадение)
        if (diagnostic_data.get('domain_statistics') and 
            domain_code in diagnostic_data['domain_statistics'] and
            diagnostic_data['domain_statistics'][domain_code].get('has_data', False)):
            
            # Есть прямые данные
            domain_data = diagnostic_data['domain_statistics'][domain_code]
            score = domain_data.get('accuracy_percentage', 0)
            questions_answered = domain_data.get('questions_answered', 0)
            correct_answers = domain_data.get('correct_answers', 0)
            print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет прямые данные: {score}%")
        else:
            # Проверяем маппинг старых доменов
            score = 0
            questions_answered = 0
            correct_answers = 0
            
            # Ищем старый домен, который маппится на этот новый
            for old_domain, new_domain in OLD_TO_NEW_DOMAIN_MAPPING.items():
                if new_domain == domain_code:
                    if (diagnostic_data.get('domain_statistics') and 
                        old_domain in diagnostic_data['domain_statistics'] and
                        diagnostic_data['domain_statistics'][old_domain].get('has_data', False)):
                        
                        # Нашли данные в старом домене
                        old_domain_data = diagnostic_data['domain_statistics'][old_domain]
                        score = old_domain_data.get('accuracy_percentage', 0)
                        questions_answered = old_domain_data.get('questions_answered', 0)
                        correct_answers = old_domain_data.get('correct_answers', 0)
                        print(f"🔍 ОТЛАДКА: Домен {domain_name} имеет данные из старого домена {old_domain}: {score}%")
                        break
            
            if score == 0:
                print(f"🔍 ОТЛАДКА: Домен {domain_name} без данных: 0%")
        
        all_domains_data[domain_name] = {
            'domain_code': domain_code,
            'score': score,
            'questions_answered': questions_answered,
            'correct_answers': correct_answers,
            'accuracy': score,
            'target': 85,  # Целевой балл
            'hours': max(24 - score * 0.3, 8)  # Расчет часов
        }
    
    print(f"🔍 ОТЛАДКА: all_domains_data = {all_domains_data}")
    
    # Определяем слабые и сильные области
    weak_domains = []
    strong_domains = []
    for domain_name, domain_data in all_domains_data.items():
        if domain_data['score'] < 70:
            weak_domains.append(domain_name)
        elif domain_data['score'] >= 80:
            strong_domains.append(domain_name)
    
    print(f"🔍 ОТЛАДКА: weak_domains = {weak_domains}")
    print(f"🔍 ОТЛАДКА: strong_domains = {strong_domains}")
    
    # Рассчитываем целевую способность
    target_ability = 0.7  # Базовая цель для BIG экзамена
    if exam_date:
        days_until_exam = (exam_date - datetime.now(timezone.utc)).days
        if days_until_exam < 30:
            target_ability = 0.8
        elif days_until_exam < 90:
            target_ability = 0.75
    
    # Создаем план обучения
    print(f"🔍 ОТЛАДКА: создаем PersonalLearningPlan")
    plan = PersonalLearningPlan(
        user_id=user_id,
        exam_date=exam_date.date() if exam_date else None,
        start_date=start_date.date() if start_date else None,
        end_date=end_date.date() if end_date else None,
        intensity=intensity,
        study_time=study_time,
        diagnostic_session_id=diagnostic_session.id,
        target_ability=target_ability,
        study_hours_per_week=20.0,
        current_ability=diagnostic_session.current_ability,
        overall_progress=0.0,
        estimated_readiness=diagnostic_data.get('readiness_percentage', 0) / 100.0,
        status='active'
    )
    
    # Устанавливаем данные в ПРАВИЛЬНОМ формате
    print(f"🔍 ОТЛАДКА: устанавливаем domain_analysis = {all_domains_data}")
    plan.set_domain_analysis(all_domains_data)
    plan.set_weak_domains(weak_domains)
    plan.set_strong_domains(strong_domains)
    
    # Создаем базовое расписание
    study_schedule = {
        'weekly_schedule': [],
        'total_weeks': max(len(weak_domains) * 2, 8),
        'study_hours_per_week': 20.0
    }
    plan.set_study_schedule(study_schedule)
    
    # Создаем вехи
    milestones = []
    if exam_date:
        milestones = [
            {'week': 1, 'title': 'Start of preparation', 'description': 'Begin intensive study'},
            {'week': max(len(weak_domains) * 2, 8) // 2, 'title': 'Mid-term review', 'description': 'Assess progress'},
            {'week': max(len(weak_domains) * 2, 8), 'title': 'Final preparation', 'description': 'Final review before exam'}
        ]
    plan.set_milestones(milestones)
    
    # Сохраняем план в базе данных
    print(f"🔍 ОТЛАДКА: сохраняем план в БД")
    db.session.add(plan)
    db.session.commit()
    
    print(f"🔍 ОТЛАДКА: план сохранен, ID = {plan.id}")
    print(f"🔍 ОТЛАДКА: plan.domain_analysis = {plan.domain_analysis}")
    print(f"🔍 ОТЛАДКА: plan.get_domain_analysis() = {plan.get_domain_analysis()}")
    
    # Создаем сессии обучения для плана
    create_study_sessions_for_plan(plan)
    
    return plan

def update_user_learning_plan(user_id: int) -> Optional[PersonalLearningPlan]:
    """Обновляет план обучения пользователя"""
    
    # Получаем активный план
    plan = PersonalLearningPlan.query.filter_by(
        user_id=user_id,
        status='active'
    ).first()
    
    if not plan:
        return None
    
    # Обновляем прогресс
    generator = LearningPlanGenerator(user_id)
    generator.update_plan_progress(plan)
    
    return plan 

def create_study_sessions_for_plan(plan: PersonalLearningPlan) -> List[StudySession]:
    """Создает сессии обучения для плана"""
    
    study_schedule = plan.get_study_schedule()
    if not study_schedule or not study_schedule.get('weekly_schedule'):
        return []
    
    sessions = []
    weak_domains = plan.get_weak_domains()
    
    for week_data in study_schedule['weekly_schedule']:
        week_number = week_data['week_number']
        focus_domains = week_data['focus_domains']
        
        for daily_session in week_data['daily_sessions']:
            # Создаем сессию обучения
            session = StudySession(
                learning_plan_id=plan.id,
                session_type=daily_session['type'],
                domain_id=get_domain_id_by_name(focus_domains[0]) if focus_domains else None,
                planned_duration=int(daily_session['duration'] * 60),  # Конвертируем в минуты
                status='planned',
                progress_percent=0.0
            )
            
            # Устанавливаем контент для сессии
            if focus_domains:
                recommended_lessons = get_smart_recommendations(
                    plan.user_id, 
                    focus_domains, 
                    limit=3
                )
                lesson_ids = [lesson.id for lesson in recommended_lessons]
                session.set_content_ids(lesson_ids)
            
            db.session.add(session)
            sessions.append(session)
    
    db.session.commit()
    return sessions

def get_domain_id_by_name(domain_name: str) -> Optional[int]:
    """Получает ID домена по названию"""
    domain = BIGDomain.query.filter_by(name=domain_name).first()
    return domain.id if domain else None 