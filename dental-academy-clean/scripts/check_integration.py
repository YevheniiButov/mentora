#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки интеграции всех компонентов системы адаптивного обучения
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, DiagnosticSession, PersonalLearningPlan, IRTParameters, Question
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from datetime import datetime, date, timedelta
import json

class IntegrationChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_steps = []
        
    def log_error(self, step, message):
        self.errors.append(f"❌ [{step}] {message}")
        
    def log_warning(self, step, message):
        self.warnings.append(f"⚠️ [{step}] {message}")
        
    def log_success(self, step, message):
        self.success_steps.append(f"✅ [{step}] {message}")
        
    def check_user_registration_flow(self, user_id):
        """Проверка flow регистрации и диагностики"""
        print("\n1️⃣ ПРОВЕРКА РЕГИСТРАЦИИ И ДИАГНОСТИКИ")
        print("-" * 50)
        
        user = db.session.get(User, user_id)
        if not user:
            self.log_error("USER", f"Пользователь {user_id} не найден")
            return False
            
        self.log_success("USER", f"Пользователь найден: {user.email}")
        
        # Проверка флага диагностики
        if hasattr(user, 'requires_diagnostic'):
            self.log_success("USER", f"Флаг requires_diagnostic = {user.requires_diagnostic}")
        else:
            self.log_error("USER", "Отсутствует поле requires_diagnostic в модели User")
            
        # Проверка диагностических сессий
        diagnostic_sessions = DiagnosticSession.query.filter_by(
            user_id=user_id
        ).order_by(DiagnosticSession.started_at.desc()).all()
        
        if not diagnostic_sessions:
            self.log_warning("DIAGNOSTIC", "Нет диагностических сессий")
            return False
        else:
            self.log_success("DIAGNOSTIC", f"Найдено {len(diagnostic_sessions)} сессий")
            
        # Проверка завершенной диагностики
        completed_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).first()
        
        if not completed_session:
            self.log_error("DIAGNOSTIC", "Нет завершенных диагностических сессий")
            return False
        else:
            self.log_success("DIAGNOSTIC", f"Завершенная сессия #{completed_session.id}, ability: {completed_session.current_ability:.2f}")
            
        return True
        
    def check_learning_plan_generation(self, user_id):
        """Проверка генерации плана обучения"""
        print("\n2️⃣ ПРОВЕРКА ПЛАНА ОБУЧЕНИЯ")
        print("-" * 50)
        
        # Проверка активного плана
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not active_plan:
            self.log_error("PLAN", "Нет активного плана обучения")
            return False
        else:
            self.log_success("PLAN", f"Активный план #{active_plan.id}")
            
        # Проверка связи с диагностикой
        if not active_plan.diagnostic_session_id:
            self.log_error("PLAN", "План не связан с диагностической сессией")
        else:
            self.log_success("PLAN", f"План связан с диагностикой #{active_plan.diagnostic_session_id}")
            
        # Проверка weak domains
        weak_domains = active_plan.get_weak_domains()
        if not weak_domains:
            self.log_warning("PLAN", "Нет слабых доменов в плане")
        else:
            self.log_success("PLAN", f"Слабые домены: {', '.join(weak_domains)}")
            
        # Проверка domain analysis
        domain_analysis = active_plan.get_domain_analysis()
        if not domain_analysis:
            self.log_error("PLAN", "Нет анализа доменов")
        else:
            self.log_success("PLAN", f"Анализ доменов содержит {len(domain_analysis)} записей")
            
        # Проверка даты переоценки
        if not active_plan.next_diagnostic_date:
            self.log_warning("PLAN", "Не установлена дата переоценки")
        else:
            days_until = (active_plan.next_diagnostic_date - date.today()).days
            self.log_success("PLAN", f"Дата переоценки: {active_plan.next_diagnostic_date} (через {days_until} дней)")
            
        return True
        
    def check_daily_tasks_generation(self, user_id):
        """Проверка генерации ежедневных задач"""
        print("\n3️⃣ ПРОВЕРКА ЕЖЕДНЕВНЫХ ЗАДАЧ")
        print("-" * 50)
        
        algorithm = DailyLearningAlgorithm()
        
        try:
            result = algorithm.generate_daily_plan(user_id, target_minutes=30)
            
            if not result.get('success'):
                self.log_error("DAILY", f"Ошибка генерации: {result.get('error')}")
                
                if result.get('requires_diagnostic'):
                    self.log_warning("DAILY", "Требуется диагностика")
                elif result.get('requires_reassessment'):
                    self.log_warning("DAILY", "Требуется переоценка")
                    
                return False
            else:
                self.log_success("DAILY", "План успешно сгенерирован")
                
            # Проверка содержимого плана
            daily_plan = result.get('daily_plan', {})
            if not daily_plan:
                self.log_error("DAILY", "Пустой ежедневный план")
                return False
                
            # Проверка секций
            sections = ['theory', 'practice', 'review']
            for section in sections:
                if section in daily_plan:
                    items = daily_plan[section].get('items', [])
                    self.log_success("DAILY", f"Секция {section}: {len(items)} элементов")
                else:
                    self.log_warning("DAILY", f"Отсутствует секция {section}")
                    
            # Проверка слабых доменов
            weak_domains = result.get('weak_domains', [])
            if weak_domains:
                self.log_success("DAILY", f"Используются слабые домены: {', '.join(weak_domains)}")
            else:
                self.log_warning("DAILY", "Нет слабых доменов в daily plan")
                
        except Exception as e:
            self.log_error("DAILY", f"Исключение при генерации: {str(e)}")
            return False
            
        return True
        
    def check_irt_parameters(self):
        """Проверка IRT параметров"""
        print("\n4️⃣ ПРОВЕРКА IRT ПАРАМЕТРОВ")
        print("-" * 50)
        
        total_questions = Question.query.count()
        questions_with_irt = Question.query.join(IRTParameters).count()
        
        if total_questions == 0:
            self.log_error("IRT", "Нет вопросов в базе")
            return False
            
        coverage = (questions_with_irt / total_questions) * 100
        
        if coverage < 50:
            self.log_error("IRT", f"Только {coverage:.1f}% вопросов имеют IRT параметры")
        elif coverage < 80:
            self.log_warning("IRT", f"{coverage:.1f}% вопросов имеют IRT параметры")
        else:
            self.log_success("IRT", f"{coverage:.1f}% вопросов имеют IRT параметры")
            
        # Проверка качества параметров
        default_params = IRTParameters.query.filter(
            IRTParameters.difficulty == 0.0,
            IRTParameters.discrimination == 1.0
        ).count()
        
        if default_params > 0:
            self.log_warning("IRT", f"{default_params} вопросов используют дефолтные параметры")
            
        # Проверка калибровки
        calibrated = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size > 0
        ).count()
        
        if calibrated > 0:
            self.log_success("IRT", f"{calibrated} параметров откалиброваны на реальных данных")
        else:
            self.log_warning("IRT", "Нет откалиброванных параметров")
            
        return True
        
    def check_reassessment_flow(self, user_id):
        """Проверка процесса переоценки"""
        print("\n5️⃣ ПРОВЕРКА ПЕРЕОЦЕНКИ")
        print("-" * 50)
        
        # Имитация просроченной переоценки
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_plan:
            # Временно устанавливаем прошедшую дату
            old_date = active_plan.next_diagnostic_date
            active_plan.next_diagnostic_date = date.today() - timedelta(days=1)
            db.session.commit()
            
            # Проверяем генерацию daily plan
            algorithm = DailyLearningAlgorithm()
            result = algorithm.generate_daily_plan(user_id)
            
            if result.get('requires_reassessment'):
                self.log_success("REASSESS", "Система корректно требует переоценку")
                self.log_success("REASSESS", f"Redirect URL: {result.get('redirect_url')}")
            else:
                self.log_error("REASSESS", "Система не требует переоценку при истекшей дате")
                
            # Восстанавливаем дату
            active_plan.next_diagnostic_date = old_date
            db.session.commit()
        else:
            self.log_warning("REASSESS", "Нет активного плана для проверки")
            
        return True
        
    def check_lesson_difficulty_field(self):
        """Проверка поля difficulty в модели Lesson"""
        print("\n6️⃣ ПРОВЕРКА ПОЛЯ DIFFICULTY В LESSON")
        print("-" * 50)
        
        from models import Lesson
        
        # Проверяем наличие поля в модели
        if hasattr(Lesson, 'difficulty'):
            self.log_success("LESSON", "Поле difficulty присутствует в модели Lesson")
        else:
            self.log_error("LESSON", "Поле difficulty отсутствует в модели Lesson")
            return False
            
        # Проверяем данные в базе
        lessons_with_difficulty = Lesson.query.filter(Lesson.difficulty.isnot(None)).count()
        total_lessons = Lesson.query.count()
        
        if total_lessons == 0:
            self.log_warning("LESSON", "Нет уроков в базе данных")
        else:
            coverage = (lessons_with_difficulty / total_lessons) * 100
            if coverage > 0:
                self.log_success("LESSON", f"{coverage:.1f}% уроков имеют установленную сложность")
            else:
                self.log_warning("LESSON", "Ни один урок не имеет установленной сложности")
                
        return True
        
    def check_dashboard_integration(self, user_id):
        """Проверка интеграции с дашбордом"""
        print("\n7️⃣ ПРОВЕРКА ИНТЕГРАЦИИ С ДАШБОРДОМ")
        print("-" * 50)
        
        from routes.dashboard_routes import index
        
        # Имитируем запрос к дашборду
        try:
            # Проверяем наличие активного плана
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if active_plan:
                # Проверяем логику переоценки
                if active_plan.next_diagnostic_date:
                    days_until = (active_plan.next_diagnostic_date - date.today()).days
                    
                    if days_until <= 0:
                        self.log_success("DASHBOARD", "Система корректно определяет просроченную переоценку")
                    elif days_until <= 3:
                        self.log_success("DASHBOARD", "Система корректно определяет приближающуюся переоценку")
                    else:
                        self.log_success("DASHBOARD", "Дата переоценки в будущем")
                else:
                    self.log_warning("DASHBOARD", "Не установлена дата переоценки")
            else:
                self.log_warning("DASHBOARD", "Нет активного плана для проверки")
                
        except Exception as e:
            self.log_error("DASHBOARD", f"Ошибка при проверке дашборда: {str(e)}")
            
        return True
        
    def print_report(self):
        """Вывод итогового отчета"""
        print("\n" + "=" * 70)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 70)
        
        if self.success_steps:
            print(f"\n✅ УСПЕШНО ({len(self.success_steps)}):")
            for step in self.success_steps:
                print(f"  {step}")
                
        if self.warnings:
            print(f"\n⚠️ ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.errors:
            print(f"\n❌ ОШИБКИ ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
                
        # Общая оценка
        total_checks = len(self.success_steps) + len(self.warnings) + len(self.errors)
        success_rate = (len(self.success_steps) / total_checks * 100) if total_checks > 0 else 0
        
        print("\n" + "-" * 70)
        print(f"ОБЩАЯ ГОТОВНОСТЬ: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ Система готова к использованию")
        elif success_rate >= 60:
            print("⚠️ Система работает, но требует доработки")
        else:
            print("❌ Система требует серьезной доработки")
            
        # Рекомендации
        print("\n📋 РЕКОМЕНДАЦИИ:")
        if len(self.errors) > 0:
            print("  • Исправьте критические ошибки перед использованием")
        if len(self.warnings) > 0:
            print("  • Обратите внимание на предупреждения")
        if success_rate >= 80:
            print("  • Система готова к продакшену")
        elif success_rate >= 60:
            print("  • Проведите дополнительное тестирование")
        else:
            print("  • Требуется значительная доработка")
            
def run_integration_check(user_email=None):
    """Запустить полную проверку интеграции"""
    with app.app_context():
        checker = IntegrationChecker()
        
        # Найти тестового пользователя
        if user_email:
            user = User.query.filter_by(email=user_email).first()
        else:
            # Берем первого пользователя с диагностикой
            user = User.query.join(DiagnosticSession).first()
            
        if not user:
            print("❌ Не найден подходящий пользователь для тестирования")
            print("💡 Создайте пользователя и пройдите диагностику")
            return
            
        print(f"🧪 ТЕСТИРОВАНИЕ НА ПОЛЬЗОВАТЕЛЕ: {user.email}")
        print("=" * 70)
        
        # Запускаем проверки
        checker.check_user_registration_flow(user.id)
        checker.check_learning_plan_generation(user.id)
        checker.check_daily_tasks_generation(user.id)
        checker.check_irt_parameters()
        checker.check_reassessment_flow(user.id)
        checker.check_lesson_difficulty_field()
        checker.check_dashboard_integration(user.id)
        
        # Выводим отчет
        checker.print_report()

if __name__ == '__main__':
    # Можно указать email конкретного пользователя
    run_integration_check() 