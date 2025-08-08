#!/usr/bin/env python3
"""
Скрипт для синхронизации планировщика обучения с ежедневным планом
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from utils.learning_plan_generator import LearningPlanGenerator
from datetime import datetime, timezone, timedelta
import json

def fix_learning_planner_sync():
    """Синхронизирует планировщик обучения с ежедневным планом"""
    
    with app.app_context():
        print("🔧 СИНХРОНИЗАЦИЯ ПЛАНИРОВЩИКА ОБУЧЕНИЯ")
        print("=" * 60)
        
        # Проверяем пользователя Demo Gebruiker (ID: 6)
        user = User.query.get(6)
        if not user:
            print("❌ Пользователь Demo Gebruiker не найден")
            return
        
        print(f"👤 Пользователь: {user.get_display_name()} (ID: {user.id})")
        print("-" * 50)
        
        # Получаем активный план
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if not active_plan:
            print("❌ Активный план не найден")
            return
        
        print(f"📋 Активный план: ID {active_plan.id}")
        
        # Получаем последнюю диагностику
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=user.id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_diagnostic:
            print("❌ Диагностика не найдена")
            return
        
        print(f"🔬 Диагностика: ID {latest_diagnostic.id}")
        
        # Создаем генератор планов
        generator = LearningPlanGenerator(user_id=user.id)
        
        # Генерируем новый план на основе диагностики
        print("\n🔄 ГЕНЕРАЦИЯ НОВОГО ПЛАНА:")
        print("-" * 30)
        
        try:
            # Получаем данные диагностики
            diagnostic_data = {
                'session_id': latest_diagnostic.id,
                'overall_score': latest_diagnostic.current_ability,
                'domain_scores': {},
                'weak_domains': [],
                'strong_domains': []
            }
            
            # Анализируем ответы диагностики
            if latest_diagnostic.session_data:
                session_data = json.loads(latest_diagnostic.session_data)
                print(f"   📄 Session data: {session_data}")
            
            # Получаем ответы диагностики
            responses = latest_diagnostic.responses.all()
            print(f"   📊 Количество ответов: {len(responses)}")
            
            # Анализируем ответы по доменам
            domain_stats = {}
            for response in responses:
                if response.question and response.question.big_domain:
                    domain_name = response.question.big_domain.name
                    if domain_name not in domain_stats:
                        domain_stats[domain_name] = {
                            'total': 0,
                            'correct': 0,
                            'score': 0.0
                        }
                    
                    domain_stats[domain_name]['total'] += 1
                    if response.is_correct:
                        domain_stats[domain_name]['correct'] += 1
                    
                    domain_stats[domain_name]['score'] = (
                        domain_stats[domain_name]['correct'] / 
                        domain_stats[domain_name]['total'] * 100
                    )
            
            print(f"   📈 Статистика по доменам:")
            for domain, stats in domain_stats.items():
                print(f"      • {domain}: {stats['correct']}/{stats['total']} ({stats['score']:.1f}%)")
            
            # Определяем слабые домены (score < 70%)
            weak_domains = [
                domain for domain, stats in domain_stats.items() 
                if stats['score'] < 70.0
            ]
            
            print(f"   ⚠️ Слабые домены: {weak_domains}")
            
            # Обновляем план
            print("\n📝 ОБНОВЛЕНИЕ ПЛАНА:")
            print("-" * 25)
            
            # Обновляем domain_analysis
            updated_domain_analysis = {}
            for domain, stats in domain_stats.items():
                updated_domain_analysis[domain] = {
                    'domain_code': f'domain_{list(domain_stats.keys()).index(domain) + 1}',
                    'score': stats['score'],
                    'questions_answered': stats['total'],
                    'correct_answers': stats['correct'],
                    'accuracy': stats['score'],
                    'target': 85,
                    'hours': 24.0 if stats['score'] < 70.0 else 8.0
                }
            
            active_plan.domain_analysis = json.dumps(updated_domain_analysis)
            print(f"   ✅ Domain analysis обновлен")
            
            # Обновляем weak_domains
            active_plan.weak_domains = json.dumps(weak_domains)
            print(f"   ✅ Weak domains обновлен: {len(weak_domains)} доменов")
            
            # Генерируем study_schedule
            if active_plan.exam_date:
                exam_date = active_plan.exam_date
            else:
                # Если нет даты экзамена, устанавливаем через 6 месяцев
                exam_date = datetime.now(timezone.utc).date() + timedelta(days=180)
                active_plan.exam_date = exam_date
                print(f"   📅 Установлена дата экзамена: {exam_date}")
            
            # Создаем расписание обучения
            study_schedule = generator._create_study_schedule(weak_domains, exam_date)
            active_plan.study_schedule = json.dumps(study_schedule)
            print(f"   ✅ Study schedule обновлен")
            
            # Обновляем прогресс
            total_domains = len(domain_stats)
            completed_domains = len([d for d, s in domain_stats.items() if s['score'] >= 70.0])
            active_plan.overall_progress = (completed_domains / total_domains) * 100 if total_domains > 0 else 0
            
            # Обновляем готовность
            active_plan.current_ability = latest_diagnostic.current_ability
            active_plan.estimated_readiness = latest_diagnostic.current_ability / 100.0
            
            # Сохраняем изменения
            db.session.commit()
            print(f"   💾 Изменения сохранены в базе данных")
            
            print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
            print("-" * 30)
            print(f"   📈 Общий прогресс: {active_plan.overall_progress:.1f}%")
            print(f"   🎯 Текущая готовность: {active_plan.current_ability:.2f}")
            print(f"   📊 Оценка готовности: {active_plan.estimated_readiness:.1%}")
            print(f"   ⚠️ Слабых доменов: {len(weak_domains)}")
            print(f"   📅 Дата экзамена: {active_plan.exam_date}")
            
            print(f"\n✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА!")
            print("Теперь планировщик и ежедневный план должны работать согласованно.")
            
        except Exception as e:
            print(f"❌ Ошибка при синхронизации: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_learning_planner_sync() 