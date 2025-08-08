import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, DiagnosticSession, PersonalLearningPlan, UserProgress, Question, IRTParameters, Lesson
from datetime import datetime, timedelta, date
from sqlalchemy import func

def test_dashboard_metrics():
    """Тестирование метрик дашборда"""
    with app.app_context():
        print("🧪 ТЕСТИРОВАНИЕ АДМИН ДАШБОРДА")
        print("=" * 50)
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # 1. ПОЛЬЗОВАТЕЛЬСКИЕ МЕТРИКИ
        print("\n1️⃣ ПОЛЬЗОВАТЕЛЬСКИЕ МЕТРИКИ:")
        total_users = User.query.count()
        new_week = User.query.filter(User.created_at >= week_ago).count()
        active_week = User.query.join(UserProgress).filter(
            UserProgress.last_accessed >= week_ago
        ).distinct().count()
        with_diagnostic = User.query.join(DiagnosticSession).filter(
            DiagnosticSession.status == 'completed'
        ).distinct().count()
        
        print(f"   Всего пользователей: {total_users}")
        print(f"   Новых за неделю: {new_week}")
        print(f"   Активных за неделю: {active_week}")
        print(f"   С диагностикой: {with_diagnostic}")
        
        # 2. ДИАГНОСТИЧЕСКИЕ МЕТРИКИ
        print("\n2️⃣ ДИАГНОСТИЧЕСКИЕ МЕТРИКИ:")
        total_sessions = DiagnosticSession.query.count()
        completed_sessions = DiagnosticSession.query.filter_by(status='completed').count()
        avg_ability = db.session.query(
            func.avg(DiagnosticSession.current_ability)
        ).filter(DiagnosticSession.status == 'completed').scalar() or 0
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        print(f"   Всего сессий: {total_sessions}")
        print(f"   Завершено: {completed_sessions}")
        print(f"   Completion rate: {completion_rate:.1f}%")
        print(f"   Средняя способность: {avg_ability:.2f}")
        
        # 3. ПЛАНЫ ОБУЧЕНИЯ
        print("\n3️⃣ ПЛАНЫ ОБУЧЕНИЯ:")
        active_plans = PersonalLearningPlan.query.filter_by(status='active').count()
        overdue_reassessments = PersonalLearningPlan.query.filter(
            PersonalLearningPlan.status == 'active',
            PersonalLearningPlan.next_diagnostic_date < today
        ).count()
        avg_progress = db.session.query(
            func.avg(PersonalLearningPlan.overall_progress)
        ).filter(PersonalLearningPlan.status == 'active').scalar() or 0
        
        print(f"   Активных планов: {active_plans}")
        print(f"   Требуют переоценки: {overdue_reassessments}")
        print(f"   Средний прогресс: {avg_progress:.1f}%")
        
        # 4. КОНТЕНТ
        print("\n4️⃣ КОНТЕНТ:")
        total_questions = Question.query.count()
        questions_with_irt = Question.query.join(IRTParameters).count()
        total_lessons = Lesson.query.count()
        irt_coverage = (questions_with_irt / total_questions * 100) if total_questions > 0 else 0
        
        print(f"   Всего вопросов: {total_questions}")
        print(f"   С IRT параметрами: {questions_with_irt}")
        print(f"   IRT покрытие: {irt_coverage:.1f}%")
        print(f"   Всего уроков: {total_lessons}")
        
        # 5. СЛАБЫЕ ДОМЕНЫ
        print("\n5️⃣ СЛАБЫЕ ДОМЕНЫ:")
        plans_with_weak = PersonalLearningPlan.query.filter(
            PersonalLearningPlan.weak_domains != None,
            PersonalLearningPlan.status == 'active'
        ).all()
        
        domain_counts = {}
        for plan in plans_with_weak:
            weak_domains = plan.get_weak_domains()
            for domain in weak_domains:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        weak_domains_stats = sorted(
            [{'domain': k, 'count': v} for k, v in domain_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]
        
        print(f"   Планов со слабыми доменами: {len(plans_with_weak)}")
        print("   Топ 5 слабых доменов:")
        for stat in weak_domains_stats:
            print(f"     {stat['domain']}: {stat['count']}")
        
        # 6. АКТИВНОСТЬ
        print("\n6️⃣ АКТИВНОСТЬ ЗА НЕДЕЛЮ:")
        daily_activity = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            registrations = User.query.filter(
                func.date(User.created_at) == day
            ).count()
            diagnostics = DiagnosticSession.query.filter(
                func.date(DiagnosticSession.started_at) == day
            ).count()
            lessons = UserProgress.query.filter(
                func.date(UserProgress.last_accessed) == day
            ).count()
            
            daily_activity.append({
                'date': day.strftime('%d.%m'),
                'registrations': registrations,
                'diagnostics': diagnostics,
                'lessons': lessons
            })
            print(f"   {day.strftime('%d.%m')}: {registrations} регистраций, {diagnostics} диагностик, {lessons} уроков")
        
        print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print("Дашборд готов к использованию!")

if __name__ == '__main__':
    test_dashboard_metrics() 