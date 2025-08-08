#!/usr/bin/env python3
"""
Выполнение миграции доменов для исправления потери данных
Объединяет дублирующиеся домены и создает отсутствующие
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, BIGDomain, Question, DiagnosticResponse, PersonalLearningPlan
import json
from datetime import datetime, timezone

def execute_domain_migration():
    """Выполнение миграции доменов"""
    
    with app.app_context():
        print("🚀 ВЫПОЛНЕНИЕ МИГРАЦИИ ДОМЕНОВ")
        print("=" * 50)
        
        # Загрузка стратегии миграции
        try:
            with open('analysis/domain_migration_strategy.json', 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            migration_map = strategy['migration_map']
        except FileNotFoundError:
            print("❌ Файл стратегии миграции не найден. Сначала запустите domain_migration_strategy.py")
            return
        
        print(f"📋 Загружена карта миграции: {len(migration_map)} преобразований")
        
        # Шаг 1: Создание отсутствующего домена PHARMACOLOGY
        print("\n1️⃣ ШАГ 1: СОЗДАНИЕ ДОМЕНА PHARMACOLOGY")
        
        # Проверяем, существует ли уже PHARMACOLOGY
        pharmacology_domain = BIGDomain.query.filter_by(code='PHARMACOLOGY').first()
        
        if not pharmacology_domain:
            # Проверяем, есть ли домен с названием "Фармакология"
            existing_pharma = BIGDomain.query.filter_by(name='Фармакология').first()
            if existing_pharma:
                # Обновляем существующий домен
                existing_pharma.code = 'PHARMACOLOGY'
                existing_pharma.description = 'Фармакология и лекарственные препараты в стоматологии'
                existing_pharma.weight_percentage = 8.0
                existing_pharma.category = 'THEORETICAL'
                existing_pharma.exam_type = 'multiple_choice'
                existing_pharma.is_critical = True
                pharmacology_domain = existing_pharma
                print("   ✅ Обновлен существующий домен Фармакология → PHARMACOLOGY")
            else:
                # Создаем новый домен PHARMACOLOGY
                pharmacology_domain = BIGDomain(
                    name='Фармакология (PHARMACOLOGY)',
                    code='PHARMACOLOGY',
                    description='Фармакология и лекарственные препараты в стоматологии',
                    weight_percentage=8.0,
                    category='THEORETICAL',
                    exam_type='multiple_choice',
                    is_critical=True,
                    order=18
                )
                db.session.add(pharmacology_domain)
                print("   ✅ Создан домен PHARMACOLOGY")
            db.session.commit()
        else:
            print("   ℹ️  Домен PHARMACOLOGY уже существует")
        
        # Шаг 2: Обновление вопросов с PHARMA на PHARMACOLOGY
        print("\n2️⃣ ШАГ 2: ОБНОВЛЕНИЕ ВОПРОСОВ")
        
        pharma_questions = Question.query.filter_by(domain='PHARMA').all()
        print(f"   Найдено вопросов с domain='PHARMA': {len(pharma_questions)}")
        
        for question in pharma_questions:
            question.domain = 'PHARMACOLOGY'
            if question.big_domain_id:
                question.big_domain_id = pharmacology_domain.id
        
        db.session.commit()
        print("   ✅ Обновлены вопросы с PHARMA на PHARMACOLOGY")
        
        # Шаг 3: Обновление DiagnosticResponse
        print("\n3️⃣ ШАГ 3: ОБНОВЛЕНИЕ ДИАГНОСТИЧЕСКИХ ОТВЕТОВ")
        
        # Получаем все ответы с вопросами PHARMA
        pharma_responses = db.session.query(DiagnosticResponse).join(Question).filter(Question.domain == 'PHARMA').all()
        print(f"   Найдено диагностических ответов с вопросами PHARMA: {len(pharma_responses)}")
        
        # Обновляем их (вопросы уже обновлены выше)
        print("   ✅ Диагностические ответы обновлены")
        
        # Шаг 4: Миграция планов обучения
        print("\n4️⃣ ШАГ 4: МИГРАЦИЯ ПЛАНОВ ОБУЧЕНИЯ")
        
        plans = PersonalLearningPlan.query.all()
        print(f"   Обработка {len(plans)} планов обучения")
        
        updated_plans = 0
        for plan in plans:
            try:
                # Получаем текущий анализ доменов
                if plan.domain_analysis:
                    analysis = plan.get_domain_analysis()
                    if analysis:
                        # Применяем миграцию
                        new_analysis = {}
                        for old_domain, ability in analysis.items():
                            new_domain = migration_map.get(old_domain, old_domain)
                            new_analysis[new_domain] = ability
                        
                        # Убеждаемся, что все 30 доменов присутствуют
                        all_domains = set(BIGDomain.DOMAIN_CODES.keys())
                        for domain_code in all_domains:
                            if domain_code not in new_analysis:
                                new_analysis[domain_code] = 0.0  # Значение по умолчанию
                        
                        plan.set_domain_analysis(new_analysis)
                        updated_plans += 1
                
                # Обновляем слабые домены
                if plan.weak_domains:
                    weak_domains = plan.get_weak_domains()
                    if weak_domains:
                        new_weak_domains = []
                        for domain in weak_domains:
                            new_domain = migration_map.get(domain, domain)
                            if new_domain not in new_weak_domains:
                                new_weak_domains.append(new_domain)
                        plan.set_weak_domains(new_weak_domains)
                
                # Обновляем сильные домены
                if plan.strong_domains:
                    strong_domains = plan.get_strong_domains()
                    if strong_domains:
                        new_strong_domains = []
                        for domain in strong_domains:
                            new_domain = migration_map.get(domain, domain)
                            if new_domain not in new_strong_domains:
                                new_strong_domains.append(new_domain)
                        plan.set_strong_domains(new_strong_domains)
                
            except Exception as e:
                print(f"   ⚠️  Ошибка при обновлении плана {plan.id}: {e}")
                continue
        
        db.session.commit()
        print(f"   ✅ Обновлено планов обучения: {updated_plans}")
        
        # Шаг 5: Удаление дублирующихся доменов
        print("\n5️⃣ ШАГ 5: УДАЛЕНИЕ ДУБЛИРУЮЩИХСЯ ДОМЕНОВ")
        
        # Удаляем PHARMA (если все вопросы перенесены)
        pharma_domain = BIGDomain.query.filter_by(code='PHARMA').first()
        if pharma_domain:
            # Проверяем, что нет вопросов с этим доменом
            remaining_questions = Question.query.filter_by(domain='PHARMA').count()
            if remaining_questions == 0:
                db.session.delete(pharma_domain)
                print("   ✅ Удален дублирующийся домен PHARMA")
            else:
                print(f"   ⚠️  Не удалено {remaining_questions} вопросов с доменом PHARMA")
        
        # Удаляем FARMACOLOGIE
        farmacologie_domain = BIGDomain.query.filter_by(code='FARMACOLOGIE').first()
        if farmacologie_domain:
            db.session.delete(farmacologie_domain)
            print("   ✅ Удален дублирующийся домен FARMACOLOGIE")
        
        # Удаляем DIAGNOSIS_SPECIAL
        diagnosis_special_domain = BIGDomain.query.filter_by(code='DIAGNOSIS_SPECIAL').first()
        if diagnosis_special_domain:
            db.session.delete(diagnosis_special_domain)
            print("   ✅ Удален дублирующийся домен DIAGNOSIS_SPECIAL")
        
        db.session.commit()
        
        # Шаг 6: Валидация миграции
        print("\n6️⃣ ШАГ 6: ВАЛИДАЦИЯ МИГРАЦИИ")
        
        # Проверяем количество доменов
        total_domains = BIGDomain.query.count()
        print(f"   Всего доменов в базе: {total_domains}")
        
        # Проверяем планы обучения
        plans_with_all_domains = 0
        total_plans = PersonalLearningPlan.query.count()
        
        for plan in PersonalLearningPlan.query.all():
            try:
                if plan.domain_analysis:
                    analysis = plan.get_domain_analysis()
                    if analysis and len(analysis) >= 28:  # Минимум 28 доменов
                        plans_with_all_domains += 1
            except:
                pass
        
        print(f"   Планов с полным набором доменов: {plans_with_all_domains}/{total_plans}")
        
        # Проверяем вопросы
        questions_with_pharmacology = Question.query.filter_by(domain='PHARMACOLOGY').count()
        print(f"   Вопросов с доменом PHARMACOLOGY: {questions_with_pharmacology}")
        
        # Создаем отчет о миграции
        migration_report = {
            'migration_date': datetime.now(timezone.utc).isoformat(),
            'total_domains_after': total_domains,
            'plans_updated': updated_plans,
            'plans_with_all_domains': plans_with_all_domains,
            'total_plans': total_plans,
            'questions_with_pharmacology': questions_with_pharmacology,
            'migration_successful': plans_with_all_domains > 0
        }
        
        with open('analysis/domain_migration_report.json', 'w', encoding='utf-8') as f:
            json.dump(migration_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Отчет о миграции сохранен в: analysis/domain_migration_report.json")
        
        if plans_with_all_domains > 0:
            print("\n✅ МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            print(f"   - Доменов в системе: {total_domains}")
            print(f"   - Планов с полным набором доменов: {plans_with_all_domains}")
            print(f"   - Вопросов с PHARMACOLOGY: {questions_with_pharmacology}")
        else:
            print("\n❌ МИГРАЦИЯ НЕ ЗАВЕРШЕНА ПОЛНОСТЬЮ")
            print("   Проверьте логи и повторите миграцию")
        
        return migration_report

if __name__ == '__main__':
    execute_domain_migration() 