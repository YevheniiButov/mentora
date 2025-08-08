import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import PersonalLearningPlan, DiagnosticSession

def fix_missing_links():
    with app.app_context():
        # Находим планы без diagnostic_session_id
        plans_without_diagnostic = PersonalLearningPlan.query.filter(
            PersonalLearningPlan.diagnostic_session_id == None
        ).all()
        
        print(f"Найдено {len(plans_without_diagnostic)} планов без связи с диагностикой")
        
        fixed_count = 0
        for plan in plans_without_diagnostic:
            # Ищем последнюю завершенную диагностику пользователя
            latest_diagnostic = DiagnosticSession.query.filter_by(
                user_id=plan.user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            if latest_diagnostic:
                plan.diagnostic_session_id = latest_diagnostic.id
                fixed_count += 1
                print(f"План #{plan.id} связан с диагностикой #{latest_diagnostic.id}")
            else:
                print(f"⚠️ Для плана #{plan.id} пользователя {plan.user_id} не найдена диагностика")
        
        db.session.commit()
        print(f"\n✅ Исправлено {fixed_count} планов")

if __name__ == '__main__':
    fix_missing_links() 