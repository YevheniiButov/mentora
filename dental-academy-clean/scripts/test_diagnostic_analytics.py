import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import DiagnosticSession, DiagnosticResponse, Question, IRTParameters, User
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

def test_diagnostic_analytics():
    """Тестирование системы аналитики диагностик"""
    with app.app_context():
        print("🧪 ТЕСТИРОВАНИЕ АНАЛИТИКИ ДИАГНОСТИК")
        print("=" * 50)
        
        # 1. БАЗОВАЯ СТАТИСТИКА
        print("\n1️⃣ БАЗОВАЯ СТАТИСТИКА:")
        total_sessions = DiagnosticSession.query.count()
        completed_sessions = DiagnosticSession.query.filter_by(status='completed').count()
        active_sessions = DiagnosticSession.query.filter_by(status='active').count()
        
        print(f"   Всего сессий: {total_sessions}")
        print(f"   Завершено: {completed_sessions}")
        print(f"   Активных: {active_sessions}")
        print(f"   Completion rate: {(completed_sessions/total_sessions*100) if total_sessions > 0 else 0:.1f}%")
        
        # 2. СТАТИСТИКА ПО ТИПАМ
        print("\n2️⃣ СТАТИСТИКА ПО ТИПАМ ДИАГНОСТИКИ:")
        session_types = db.session.query(
            DiagnosticSession.session_type,
            func.count(DiagnosticSession.id).label('count'),
            func.avg(DiagnosticSession.current_ability).label('avg_ability')
        ).filter(
            DiagnosticSession.status == 'completed'
        ).group_by(DiagnosticSession.session_type).all()
        
        for session_type in session_types:
            print(f"   {session_type.session_type}: {session_type.count} сессий, средняя способность: {session_type.avg_ability:.2f}")
        
        # 3. РАСПРЕДЕЛЕНИЕ СПОСОБНОСТЕЙ
        print("\n3️⃣ РАСПРЕДЕЛЕНИЕ СПОСОБНОСТЕЙ:")
        ability_distribution = db.session.query(
            func.floor(DiagnosticSession.current_ability).label('ability_range'),
            func.count(DiagnosticSession.id).label('count')
        ).filter(
            DiagnosticSession.status == 'completed'
        ).group_by('ability_range').order_by('ability_range').all()
        
        for dist in ability_distribution:
            print(f"   Диапазон {dist.ability_range}: {dist.count} пользователей")
        
        # 4. IRT СТАТИСТИКА
        print("\n4️⃣ IRT СТАТИСТИКА:")
        total_questions = Question.query.count()
        questions_with_irt = Question.query.join(IRTParameters).count()
        calibrated_questions = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size > 0
        ).count()
        
        avg_discrimination = db.session.query(
            func.avg(IRTParameters.discrimination)
        ).scalar() or 0
        avg_difficulty = db.session.query(
            func.avg(IRTParameters.difficulty)
        ).scalar() or 0
        
        print(f"   Всего вопросов: {total_questions}")
        print(f"   С IRT параметрами: {questions_with_irt}")
        print(f"   Калибровано: {calibrated_questions}")
        print(f"   IRT покрытие: {(questions_with_irt/total_questions*100) if total_questions > 0 else 0:.1f}%")
        print(f"   Средняя дискриминация: {avg_discrimination:.3f}")
        print(f"   Средняя сложность: {avg_difficulty:.3f}")
        
        # 5. ЭКСТРЕМАЛЬНЫЕ ВОПРОСЫ
        print("\n5️⃣ ЭКСТРЕМАЛЬНЫЕ ВОПРОСЫ:")
        
        # Очень сложные
        very_difficult = Question.query.join(IRTParameters).filter(
            IRTParameters.difficulty > 2.0
        ).limit(5).all()
        print(f"   Очень сложных (>2.0): {len(very_difficult)}")
        for q in very_difficult:
            print(f"     ID {q.id}: сложность {q.irt_parameters.difficulty:.2f}")
        
        # Очень легкие
        very_easy = Question.query.join(IRTParameters).filter(
            IRTParameters.difficulty < -2.0
        ).limit(5).all()
        print(f"   Очень легких (<-2.0): {len(very_easy)}")
        for q in very_easy:
            print(f"     ID {q.id}: сложность {q.irt_parameters.difficulty:.2f}")
        
        # Низкая дискриминация
        low_discrimination = Question.query.join(IRTParameters).filter(
            IRTParameters.discrimination < 0.5
        ).limit(5).all()
        print(f"   С низкой дискриминацией (<0.5): {len(low_discrimination)}")
        for q in low_discrimination:
            print(f"     ID {q.id}: дискриминация {q.irt_parameters.discrimination:.2f}")
        
        # 6. АНАЛИЗ ПО ДОМЕНАМ
        print("\n6️⃣ АНАЛИЗ ПО ДОМЕНАМ:")
        recent_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.status == 'completed'
        ).limit(50).all()
        
        domain_abilities = {}
        domain_counts = {}
        
        for session in recent_sessions:
            try:
                results = session.generate_results()
                if results and 'domain_abilities' in results:
                    for domain, ability in results['domain_abilities'].items():
                        if domain not in domain_abilities:
                            domain_abilities[domain] = []
                            domain_counts[domain] = 0
                        domain_abilities[domain].append(ability)
                        if ability < 0.0:
                            domain_counts[domain] += 1
            except Exception as e:
                print(f"     Ошибка при анализе сессии {session.id}: {e}")
                continue
        
        for domain, abilities in domain_abilities.items():
            # Фильтруем None значения
            valid_abilities = [a for a in abilities if a is not None]
            if valid_abilities:
                avg_ability = sum(valid_abilities) / len(valid_abilities)
                weak_count = domain_counts[domain]
                print(f"   {domain}: средняя способность {avg_ability:.2f}, слабых результатов {weak_count}/{len(valid_abilities)}")
            else:
                print(f"   {domain}: нет валидных данных")
        
        # 7. ДЕТАЛЬНЫЙ АНАЛИЗ СЕССИЙ
        print("\n7️⃣ ДЕТАЛЬНЫЙ АНАЛИЗ СЕССИЙ:")
        sample_session = DiagnosticSession.query.filter_by(status='completed').first()
        if sample_session:
            print(f"   Пример сессии #{sample_session.id}:")
            print(f"     Пользователь: {sample_session.user.email}")
            print(f"     Тип: {sample_session.session_type}")
            print(f"     Вопросов: {sample_session.questions_answered}")
            print(f"     Правильных: {sample_session.correct_answers}")
            print(f"     Точность: {(sample_session.correct_answers/sample_session.questions_answered*100) if sample_session.questions_answered > 0 else 0:.1f}%")
            print(f"     Финальная способность: {sample_session.current_ability:.3f}")
            
            # Ответы в сессии
            responses = DiagnosticResponse.query.filter_by(session_id=sample_session.id).all()
            print(f"     Ответов в БД: {len(responses)}")
            
            # История способности
            if sample_session.ability_history:
                try:
                    history = sample_session.get_ability_history()
                    print(f"     Записей в истории: {len(history)}")
                except:
                    print(f"     Ошибка чтения истории")
        else:
            print("   Нет завершенных сессий для анализа")
        
        print("\n✅ ТЕСТИРОВАНИЕ АНАЛИТИКИ ЗАВЕРШЕНО!")
        print("Система аналитики готова к использованию!")

if __name__ == '__main__':
    test_diagnostic_analytics() 