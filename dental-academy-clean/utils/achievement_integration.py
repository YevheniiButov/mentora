#!/usr/bin/env python3
"""
Интеграция планировщика обучения с системой достижений
"""

from datetime import datetime, timedelta, timezone
from models import User, PersonalLearningPlan, StudySession, Achievement, UserAchievement
from extensions import db

class LearningPlanAchievementSystem:
    """Система достижений для планировщика обучения"""
    
    def __init__(self):
        self.achievements = {
            'plan_creator': {
                'name': 'Планировщик',
                'description': 'Создал первый план обучения',
                'icon': 'calendar-check',
                'category': 'learning',
                'requirement_type': 'plans_created',
                'requirement_value': 1,
                'badge_color': 'primary'
            },
            'consistent_study': {
                'name': 'Регулярность',
                'description': 'Занимался 7 дней подряд',
                'icon': 'calendar-week',
                'category': 'streak',
                'requirement_type': 'consecutive_days',
                'requirement_value': 7,
                'badge_color': 'success'
            },
            'study_master': {
                'name': 'Мастер обучения',
                'description': 'Занимался 30 дней подряд',
                'icon': 'calendar-month',
                'category': 'streak',
                'requirement_type': 'consecutive_days',
                'requirement_value': 30,
                'badge_color': 'warning'
            },
            'goal_achiever': {
                'name': 'Достигатель целей',
                'description': 'Достиг 5 целей обучения',
                'icon': 'target',
                'category': 'learning',
                'requirement_type': 'goals_achieved',
                'requirement_value': 5,
                'badge_color': 'info'
            },
            'exam_ready': {
                'name': 'Готов к экзамену',
                'description': 'Достиг 80% готовности к экзамену',
                'icon': 'graduation-cap',
                'category': 'exam',
                'requirement_type': 'readiness_percentage',
                'requirement_value': 80,
                'badge_color': 'danger'
            },
            'domain_expert': {
                'name': 'Эксперт домена',
                'description': 'Достиг 90% в любом домене',
                'icon': 'award',
                'category': 'learning',
                'requirement_type': 'domain_mastery',
                'requirement_value': 90,
                'badge_color': 'purple'
            },
            'time_warrior': {
                'name': 'Воин времени',
                'description': 'Потратил 100 часов на обучение',
                'icon': 'clock',
                'category': 'time',
                'requirement_type': 'total_study_hours',
                'requirement_value': 100,
                'badge_color': 'secondary'
            },
            'perfect_week': {
                'name': 'Идеальная неделя',
                'description': 'Завершил все запланированные занятия за неделю',
                'icon': 'check-circle',
                'category': 'learning',
                'requirement_type': 'perfect_weeks',
                'requirement_value': 1,
                'badge_color': 'success'
            },
            'early_bird': {
                'name': 'Ранняя пташка',
                'description': 'Занимался 5 дней подряд в утренние часы',
                'icon': 'sunrise',
                'category': 'habit',
                'requirement_type': 'morning_study_days',
                'requirement_value': 5,
                'badge_color': 'warning'
            },
            'night_owl': {
                'name': 'Ночная сова',
                'description': 'Занимался 5 дней подряд в вечерние часы',
                'icon': 'moon',
                'category': 'habit',
                'requirement_type': 'evening_study_days',
                'requirement_value': 5,
                'badge_color': 'dark'
            }
        }
    
    def initialize_achievements(self):
        """Инициализирует достижения в базе данных"""
        try:
            for achievement_code, achievement_data in self.achievements.items():
                # Проверяем, существует ли уже достижение
                existing = Achievement.query.filter_by(
                    requirement_type=achievement_data['requirement_type'],
                    requirement_value=achievement_data['requirement_value']
                ).first()
                
                if not existing:
                    achievement = Achievement(
                        name=achievement_data['name'],
                        description=achievement_data['description'],
                        icon=achievement_data['icon'],
                        category=achievement_data['category'],
                        requirement_type=achievement_data['requirement_type'],
                        requirement_value=achievement_data['requirement_value'],
                        badge_color=achievement_data['badge_color'],
                        is_active=True
                    )
                    db.session.add(achievement)
                    print(f"✅ Создано достижение: {achievement_data['name']}")
            
            db.session.commit()
            print("✅ Все достижения инициализированы")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации достижений: {e}")
            db.session.rollback()
    
    def check_plan_creation_achievement(self, user_id):
        """Проверяет достижение за создание плана"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Подсчитываем количество созданных планов
            plans_count = PersonalLearningPlan.query.filter_by(user_id=user_id).count()
            
            # Проверяем достижение
            achievement = Achievement.query.filter_by(
                requirement_type='plans_created',
                requirement_value=1
            ).first()
            
            if achievement and plans_count >= 1:
                self._award_achievement(user, achievement)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения создания плана: {e}")
            return False
    
    def check_study_streak_achievements(self, user_id):
        """Проверяет достижения за серию занятий"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Получаем streak пользователя
            streak = user.get_or_create_streak()
            consecutive_days = streak.current_streak
            
            # Проверяем достижения за серию
            streak_achievements = [
                ('consecutive_days', 7, 'consistent_study'),
                ('consecutive_days', 30, 'study_master')
            ]
            
            awarded = False
            for req_type, req_value, achievement_code in streak_achievements:
                achievement = Achievement.query.filter_by(
                    requirement_type=req_type,
                    requirement_value=req_value
                ).first()
                
                if achievement and consecutive_days >= req_value:
                    if self._award_achievement(user, achievement):
                        awarded = True
            
            return awarded
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижений серии: {e}")
            return False
    
    def check_goal_achievement(self, user_id):
        """Проверяет достижение за выполнение целей"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Подсчитываем достигнутые цели
            plans = PersonalLearningPlan.query.filter_by(user_id=user_id).all()
            goals_achieved = 0
            
            for plan in plans:
                if plan.overall_progress and plan.overall_progress >= 80:
                    goals_achieved += 1
            
            # Проверяем достижение
            achievement = Achievement.query.filter_by(
                requirement_type='goals_achieved',
                requirement_value=5
            ).first()
            
            if achievement and goals_achieved >= 5:
                return self._award_achievement(user, achievement)
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения целей: {e}")
            return False
    
    def check_exam_readiness_achievement(self, user_id):
        """Проверяет достижение готовности к экзамену"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Получаем активный план
            plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not plan:
                return False
            
            # Проверяем готовность
            readiness_data = plan.calculate_readiness()
            readiness_percentage = readiness_data.get('readiness_percentage', 0)
            
            # Проверяем достижение
            achievement = Achievement.query.filter_by(
                requirement_type='readiness_percentage',
                requirement_value=80
            ).first()
            
            if achievement and readiness_percentage >= 80:
                return self._award_achievement(user, achievement)
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения готовности: {e}")
            return False
    
    def check_domain_mastery_achievement(self, user_id):
        """Проверяет достижение мастерства в домене"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Получаем активный план
            plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not plan:
                return False
            
            # Проверяем прогресс по доменам
            domain_analysis = plan.get_domain_analysis()
            
            for domain_code, domain_data in domain_analysis.items():
                if domain_data.get('has_data'):
                    accuracy = domain_data.get('accuracy_percentage', 0)
                    
                    if accuracy >= 90:
                        # Проверяем достижение
                        achievement = Achievement.query.filter_by(
                            requirement_type='domain_mastery',
                            requirement_value=90
                        ).first()
                        
                        if achievement:
                            return self._award_achievement(user, achievement)
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения мастерства: {e}")
            return False
    
    def check_study_time_achievement(self, user_id):
        """Проверяет достижение за время обучения"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Подсчитываем общее время обучения
            total_hours = 0
            plans = PersonalLearningPlan.query.filter_by(user_id=user_id).all()
            
            for plan in plans:
                sessions = plan.study_sessions.filter_by(status='completed').all()
                for session in sessions:
                    if session.actual_duration:
                        total_hours += session.actual_duration / 60  # Переводим в часы
            
            # Проверяем достижение
            achievement = Achievement.query.filter_by(
                requirement_type='total_study_hours',
                requirement_value=100
            ).first()
            
            if achievement and total_hours >= 100:
                return self._award_achievement(user, achievement)
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения времени: {e}")
            return False
    
    def check_perfect_week_achievement(self, user_id):
        """Проверяет достижение за идеальную неделю"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Получаем активный план
            plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not plan:
                return False
            
            # Проверяем последнюю неделю
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            week_sessions = plan.study_sessions.filter(
                StudySession.started_at >= week_ago
            ).all()
            
            planned_sessions = [s for s in week_sessions if s.status == 'planned']
            completed_sessions = [s for s in week_sessions if s.status == 'completed']
            
            # Идеальная неделя: все запланированные занятия завершены
            if planned_sessions and len(completed_sessions) == len(planned_sessions):
                achievement = Achievement.query.filter_by(
                    requirement_type='perfect_weeks',
                    requirement_value=1
                ).first()
                
                if achievement:
                    return self._award_achievement(user, achievement)
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижения идеальной недели: {e}")
            return False
    
    def check_study_time_habit_achievements(self, user_id):
        """Проверяет достижения за привычки времени обучения"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Получаем все завершенные сессии
            plans = PersonalLearningPlan.query.filter_by(user_id=user_id).all()
            morning_sessions = 0
            evening_sessions = 0
            
            for plan in plans:
                sessions = plan.study_sessions.filter_by(status='completed').all()
                
                for session in sessions:
                    if session.started_at:
                        hour = session.started_at.hour
                        
                        if 6 <= hour <= 12:  # Утренние часы
                            morning_sessions += 1
                        elif 18 <= hour <= 23:  # Вечерние часы
                            evening_sessions += 1
            
            awarded = False
            
            # Проверяем достижение "Ранняя пташка"
            if morning_sessions >= 5:
                achievement = Achievement.query.filter_by(
                    requirement_type='morning_study_days',
                    requirement_value=5
                ).first()
                
                if achievement:
                    if self._award_achievement(user, achievement):
                        awarded = True
            
            # Проверяем достижение "Ночная сова"
            if evening_sessions >= 5:
                achievement = Achievement.query.filter_by(
                    requirement_type='evening_study_days',
                    requirement_value=5
                ).first()
                
                if achievement:
                    if self._award_achievement(user, achievement):
                        awarded = True
            
            return awarded
            
        except Exception as e:
            print(f"❌ Ошибка проверки достижений привычек: {e}")
            return False
    
    def _award_achievement(self, user, achievement):
        """Выдает достижение пользователю"""
        try:
            # Проверяем, не получено ли уже достижение
            existing = UserAchievement.query.filter_by(
                user_id=user.id,
                achievement_id=achievement.id
            ).first()
            
            if existing:
                return False  # Уже получено
            
            # Выдаем достижение
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            db.session.commit()
            
            print(f"🏆 Пользователь {user.username} получил достижение: {achievement.name}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка выдачи достижения: {e}")
            db.session.rollback()
            return False
    
    def check_all_achievements(self, user_id):
        """Проверяет все достижения для пользователя"""
        try:
            awarded = False
            
            # Проверяем все типы достижений
            if self.check_plan_creation_achievement(user_id):
                awarded = True
            
            if self.check_study_streak_achievements(user_id):
                awarded = True
            
            if self.check_goal_achievement(user_id):
                awarded = True
            
            if self.check_exam_readiness_achievement(user_id):
                awarded = True
            
            if self.check_domain_mastery_achievement(user_id):
                awarded = True
            
            if self.check_study_time_achievement(user_id):
                awarded = True
            
            if self.check_perfect_week_achievement(user_id):
                awarded = True
            
            if self.check_study_time_habit_achievements(user_id):
                awarded = True
            
            return awarded
            
        except Exception as e:
            print(f"❌ Ошибка проверки всех достижений: {e}")
            return False
    
    def get_user_achievements(self, user_id):
        """Получает достижения пользователя"""
        try:
            user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
            achievements = []
            
            for ua in user_achievements:
                achievement = ua.achievement
                achievements.append({
                    'id': achievement.id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'icon': achievement.icon,
                    'category': achievement.category,
                    'badge_color': achievement.badge_color,
                    'earned_at': ua.earned_at.strftime('%d.%m.%Y')
                })
            
            return achievements
            
        except Exception as e:
            print(f"❌ Ошибка получения достижений: {e}")
            return []
    
    def get_achievement_progress(self, user_id):
        """Получает прогресс по достижениям"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {}
            
            progress = {}
            
            # Прогресс по созданию планов
            plans_count = PersonalLearningPlan.query.filter_by(user_id=user_id).count()
            progress['plans_created'] = min(plans_count, 1)
            
            # Прогресс по серии занятий
            streak = user.get_or_create_streak()
            progress['consecutive_days'] = streak.current_streak
            
            # Прогресс по целям
            plans = PersonalLearningPlan.query.filter_by(user_id=user_id).all()
            goals_achieved = sum(1 for plan in plans if plan.overall_progress and plan.overall_progress >= 80)
            progress['goals_achieved'] = goals_achieved
            
            # Прогресс по готовности
            active_plan = PersonalLearningPlan.query.filter_by(user_id=user_id, status='active').first()
            if active_plan:
                readiness_data = active_plan.calculate_readiness()
                progress['readiness_percentage'] = readiness_data.get('readiness_percentage', 0)
            else:
                progress['readiness_percentage'] = 0
            
            # Прогресс по времени обучения
            total_hours = 0
            for plan in plans:
                sessions = plan.study_sessions.filter_by(status='completed').all()
                for session in sessions:
                    if session.actual_duration:
                        total_hours += session.actual_duration / 60
            progress['total_study_hours'] = int(total_hours)
            
            return progress
            
        except Exception as e:
            print(f"❌ Ошибка получения прогресса: {e}")
            return {}

# Глобальный экземпляр системы достижений
achievement_system = LearningPlanAchievementSystem() 