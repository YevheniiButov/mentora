#!/usr/bin/env python3
"""
Анализ текущей структуры доменов в базе данных
Выявляет проблемы с дублированием и потерей данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, BIGDomain, Question, DiagnosticResponse, PersonalLearningPlan
import json
from collections import defaultdict

def analyze_domain_structure():
    """Анализ текущей структуры доменов"""
    
    with app.app_context():
        print("🔍 АНАЛИЗ СТРУКТУРЫ ДОМЕНОВ")
        print("=" * 50)
        
        # 1. Анализ доменов в базе данных
        print("\n1. ДОМЕНЫ В БАЗЕ ДАННЫХ:")
        domains = BIGDomain.query.all()
        print(f"   Всего доменов: {len(domains)}")
        
        domain_info = {}
        for domain in domains:
            domain_info[domain.code] = {
                'id': domain.id,
                'name': domain.name,
                'code': domain.code,
                'category': domain.category,
                'weight': domain.weight_percentage,
                'is_active': domain.is_active
            }
            print(f"   - {domain.code}: {domain.name} (ID: {domain.id}, вес: {domain.weight_percentage}%)")
        
        # 2. Анализ вопросов по доменам
        print("\n2. ВОПРОСЫ ПО ДОМЕНАМ:")
        questions_by_domain = defaultdict(list)
        questions = Question.query.all()
        
        for question in questions:
            domain_code = question.domain
            questions_by_domain[domain_code].append(question.id)
        
        print(f"   Всего вопросов: {len(questions)}")
        for domain_code, question_ids in questions_by_domain.items():
            print(f"   - {domain_code}: {len(question_ids)} вопросов")
        
        # 3. Анализ диагностических ответов
        print("\n3. ДИАГНОСТИЧЕСКИЕ ОТВЕТЫ ПО ДОМЕНАМ:")
        responses_by_domain = defaultdict(int)
        responses = DiagnosticResponse.query.all()
        
        for response in responses:
            if response.question and response.question.domain:
                responses_by_domain[response.question.domain] += 1
        
        print(f"   Всего диагностических ответов: {len(responses)}")
        for domain_code, count in responses_by_domain.items():
            print(f"   - {domain_code}: {count} ответов")
        
        # 4. Анализ планов обучения
        print("\n4. ПЛАНЫ ОБУЧЕНИЯ:")
        plans = PersonalLearningPlan.query.all()
        print(f"   Всего планов обучения: {len(plans)}")
        
        domain_analysis_stats = defaultdict(int)
        weak_domains_stats = defaultdict(int)
        strong_domains_stats = defaultdict(int)
        
        for plan in plans:
            if plan.domain_analysis:
                try:
                    analysis = plan.get_domain_analysis()
                    if analysis:
                        for domain_code in analysis.keys():
                            domain_analysis_stats[domain_code] += 1
                except:
                    pass
            
            if plan.weak_domains:
                try:
                    weak_domains = plan.get_weak_domains()
                    if weak_domains:
                        for domain_code in weak_domains:
                            weak_domains_stats[domain_code] += 1
                except:
                    pass
            
            if plan.strong_domains:
                try:
                    strong_domains = plan.get_strong_domains()
                    if strong_domains:
                        for domain_code in strong_domains:
                            strong_domains_stats[domain_code] += 1
                except:
                    pass
        
        print("   Домены в анализе:")
        for domain_code, count in domain_analysis_stats.items():
            print(f"     - {domain_code}: {count} планов")
        
        print("   Слабые домены:")
        for domain_code, count in weak_domains_stats.items():
            print(f"     - {domain_code}: {count} планов")
        
        print("   Сильные домены:")
        for domain_code, count in strong_domains_stats.items():
            print(f"     - {domain_code}: {count} планов")
        
        # 5. Выявление проблем
        print("\n5. ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ:")
        
        # Проверка дублирования
        domain_codes = [d.code for d in domains]
        duplicates = [code for code in set(domain_codes) if domain_codes.count(code) > 1]
        if duplicates:
            print(f"   ❌ ДУБЛИРУЮЩИЕСЯ ДОМЕНЫ: {duplicates}")
        else:
            print("   ✅ Дублирующихся доменов не найдено")
        
        # Проверка отсутствующих доменов
        expected_domains = set(BIGDomain.DOMAIN_CODES.keys())
        existing_domains = set(domain_codes)
        missing_domains = expected_domains - existing_domains
        
        if missing_domains:
            print(f"   ❌ ОТСУТСТВУЮЩИЕ ДОМЕНЫ: {list(missing_domains)}")
        else:
            print("   ✅ Все ожидаемые домены присутствуют")
        
        # Проверка неактивных доменов
        inactive_domains = [d.code for d in domains if not d.is_active]
        if inactive_domains:
            print(f"   ⚠️  НЕАКТИВНЫЕ ДОМЕНЫ: {inactive_domains}")
        
        # 6. Статистика потери данных
        print("\n6. СТАТИСТИКА ПОТЕРИ ДАННЫХ:")
        
        # Подсчет доменов с данными
        domains_with_questions = len(questions_by_domain)
        domains_with_responses = len(responses_by_domain)
        domains_in_plans = len(domain_analysis_stats)
        
        print(f"   Домены с вопросами: {domains_with_questions}")
        print(f"   Домены с диагностическими ответами: {domains_with_responses}")
        print(f"   Домены в планах обучения: {domains_in_plans}")
        
        if domains_in_plans < 30:
            print(f"   ❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Только {domains_in_plans} доменов в планах обучения из 30!")
        
        # 7. Рекомендации
        print("\n7. РЕКОМЕНДАЦИИ:")
        
        if missing_domains:
            print("   - Создать отсутствующие домены")
        
        if duplicates:
            print("   - Объединить дублирующиеся домены")
        
        if domains_in_plans < 30:
            print("   - Обновить все планы обучения для включения всех 30 доменов")
        
        if inactive_domains:
            print("   - Активировать неактивные домены или удалить их")
        
        # Сохранение отчета
        report = {
            'total_domains': len(domains),
            'expected_domains': 30,
            'missing_domains': list(missing_domains),
            'duplicate_domains': duplicates,
            'inactive_domains': inactive_domains,
            'domains_with_questions': domains_with_questions,
            'domains_with_responses': domains_with_responses,
            'domains_in_plans': domains_in_plans,
            'domain_details': domain_info,
            'questions_by_domain': dict(questions_by_domain),
            'responses_by_domain': dict(responses_by_domain),
            'plans_analysis': dict(domain_analysis_stats)
        }
        
        with open('analysis/domain_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Отчет сохранен в: analysis/domain_analysis_report.json")
        
        return report

if __name__ == '__main__':
    analyze_domain_structure() 