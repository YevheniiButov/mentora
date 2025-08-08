#!/usr/bin/env python3
"""
Анализ проблемы с маппингом уроков к доменам BIG
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Lesson, Module, Subject, ContentDomainMapping, Question
import json
from datetime import datetime, timezone

def analyze_domain_mapping():
    """Анализ текущего состояния маппинга доменов"""
    
    print("🔍 АНАЛИЗ ПРОБЛЕМЫ С МАППИНГОМ УРОКОВ К ДОМЕНАМ BIG")
    print("=" * 60)
    
    with app.app_context():
        
        # 1. Проверяем количество доменов
        domains = BIGDomain.query.filter_by(is_active=True).all()
        print(f"\n📊 ДОМЕНЫ BIG:")
        print(f"   Всего активных доменов: {len(domains)}")
        
        for domain in domains:
            questions_count = len(domain.questions) if hasattr(domain, 'questions') else 0
            print(f"   • {domain.code}: {domain.name} ({domain.weight_percentage}%) - {questions_count} вопросов")
        
        # 2. Проверяем количество уроков
        lessons = Lesson.query.all()
        print(f"\n📚 УРОКИ:")
        print(f"   Всего уроков: {len(lessons)}")
        
        # 3. Проверяем количество модулей
        modules = Module.query.all()
        print(f"   Всего модулей: {len(modules)}")
        
        # 4. Проверяем количество предметов
        subjects = Subject.query.all()
        print(f"   Всего предметов: {len(subjects)}")
        
        # 5. Проверяем маппинги контента к доменам
        content_mappings = ContentDomainMapping.query.all()
        print(f"\n🔗 МАППИНГИ КОНТЕНТА К ДОМЕНАМ:")
        print(f"   Всего маппингов: {len(content_mappings)}")
        
        lesson_mappings = [m for m in content_mappings if m.lesson_id]
        module_mappings = [m for m in content_mappings if m.module_id]
        subject_mappings = [m for m in content_mappings if m.subject_id]
        
        print(f"   • Маппингов уроков: {len(lesson_mappings)}")
        print(f"   • Маппингов модулей: {len(module_mappings)}")
        print(f"   • Маппингов предметов: {len(subject_mappings)}")
        
        # 6. Проверяем уроки без маппинга
        lessons_with_mapping = set(m.lesson_id for m in lesson_mappings)
        lessons_without_mapping = [l for l in lessons if l.id not in lessons_with_mapping]
        
        print(f"\n❌ УРОКИ БЕЗ МАППИНГА:")
        print(f"   Уроков без маппинга: {len(lessons_without_mapping)}")
        
        if lessons_without_mapping:
            print("   Примеры уроков без маппинга:")
            for lesson in lessons_without_mapping[:10]:  # Показываем первые 10
                module_name = lesson.module.title if lesson.module else "Нет модуля"
                print(f"     • {lesson.title} (Модуль: {module_name})")
        
        # 7. Проверяем модули без маппинга
        modules_with_mapping = set(m.module_id for m in module_mappings)
        modules_without_mapping = [m for m in modules if m.id not in modules_with_mapping]
        
        print(f"\n❌ МОДУЛИ БЕЗ МАППИНГА:")
        print(f"   Модулей без маппинга: {len(modules_without_mapping)}")
        
        if modules_without_mapping:
            print("   Примеры модулей без маппинга:")
            for module in modules_without_mapping[:10]:  # Показываем первые 10
                subject_name = module.subject.name if module.subject else "Нет предмета"
                print(f"     • {module.title} (Предмет: {subject_name})")
        
        # 8. Анализ по доменам
        print(f"\n📈 АНАЛИЗ ПО ДОМЕНАМ:")
        for domain in domains:
            domain_mappings = [m for m in content_mappings if m.domain_id == domain.id]
            lesson_count = len([m for m in domain_mappings if m.lesson_id])
            module_count = len([m for m in domain_mappings if m.module_id])
            subject_count = len([m for m in domain_mappings if m.subject_id])
            
            print(f"   • {domain.code}: {lesson_count} уроков, {module_count} модулей, {subject_count} предметов")
        
        # 9. Рекомендации
        print(f"\n💡 РЕКОМЕНДАЦИИ:")
        print(f"   1. Создать автоматический маппинг уроков к доменам на основе ключевых слов")
        print(f"   2. Добавить ручной маппинг для сложных случаев")
        print(f"   3. Создать скрипт для массового маппинга")
        print(f"   4. Добавить валидацию маппинга в админ-панели")

def create_auto_mapping():
    """Создание автоматического маппинга на основе ключевых слов"""
    
    print("\n🔧 СОЗДАНИЕ АВТОМАТИЧЕСКОГО МАППИНГА")
    print("=" * 60)
    
    with app.app_context():
        
        # Ключевые слова для каждого домена на английском
        domain_keywords = {
            'THER': ['caries', 'cavity', 'filling', 'endodontics', 'therapeutic', 'treatment'],
            'SURG': ['surgery', 'surgical', 'extraction', 'implant', 'implantation'],
            'PROTH': ['prosthesis', 'crown', 'bridge', 'prosthodontics'],
            'PEDI': ['pediatric', 'pediatrics', 'child', 'children', 'milk teeth'],
            'PARO': ['periodont', 'periodontal', 'gingiva', 'gum', 'periodontitis'],
            'ORTHO': ['orthodontics', 'orthodontic', 'braces', 'bite', 'malocclusion'],
            'ANATOMIE': ['anatomy', 'anatomical', 'structure', 'tooth', 'jaw'],
            'FYSIOLOGIE': ['physiology', 'physiological', 'function', 'process'],
            'PATHOLOGIE': ['pathology', 'pathological', 'disease', 'tumor'],
            'RADIOLOGIE': ['radiology', 'radiographic', 'x-ray', 'imaging'],
            'MICROBIOLOGIE': ['microbiology', 'bacterial', 'infection', 'virus'],
            'MATERIAALKUNDE': ['material', 'cement', 'composite', 'amalgam'],
            'ALGEMENE_GENEESKUNDE': ['general medicine', 'systemic disease'],
            'EMERGENCY': ['emergency', 'urgent', 'trauma', 'bleeding'],
            'PHARMACOLOGY': ['pharmacology', 'drug', 'medication', 'antibiotic'],
            'INFECTION': ['infection', 'antibiotic', 'sterilization'],
            'ETHIEK': ['ethics', 'ethical', 'law', 'legal'],
            'DUTCH': ['dutch', 'netherlands', 'healthcare system'],
            'PROFESSIONAL': ['professional', 'development', 'competency'],
            'DIAGNOSIS': ['diagnosis', 'diagnostic', 'examination'],
            'TREATMENT_PLANNING': ['planning', 'treatment plan', 'strategy'],
            'SPECIAL': ['special', 'special needs', 'groups'],
            'STATISTICS': ['statistics', 'statistical', 'data analysis'],
            'RESEARCH_METHOD': ['research', 'methodology', 'study design'],
            'PRACTICAL_SKILLS': ['practical', 'skills', 'manual'],
            'COMMUNICATION': ['communication', 'communicative', 'patient']
        }
        
        # Получаем все уроки без маппинга
        lessons_with_mapping = set(m.lesson_id for m in ContentDomainMapping.query.filter_by(lesson_id=db.not_(None)).all())
        lessons_without_mapping = Lesson.query.filter(~Lesson.id.in_(lessons_with_mapping)).all()
        
        print(f"Найдено {len(lessons_without_mapping)} уроков без маппинга")
        
        mapped_count = 0
        
        for lesson in lessons_without_mapping:
            lesson_text = f"{lesson.title} {lesson.content or ''}".lower()
            
            # Ищем подходящий домен
            best_domain = None
            best_score = 0
            
            for domain_code, keywords in domain_keywords.items():
                domain = BIGDomain.query.filter_by(code=domain_code).first()
                if not domain:
                    continue
                
                score = sum(1 for keyword in keywords if keyword.lower() in lesson_text)
                if score > best_score:
                    best_score = score
                    best_domain = domain
            
            # Создаем маппинг если нашли подходящий домен
            if best_domain and best_score > 0:
                mapping = ContentDomainMapping(
                    lesson_id=lesson.id,
                    domain_id=best_domain.id,
                    relevance_score=min(best_score / 5.0, 1.0),  # Нормализуем до 1.0
                    relationship_type='auto_mapped'
                )
                db.session.add(mapping)
                mapped_count += 1
                print(f"   ✅ {lesson.title} -> {best_domain.code} (score: {best_score})")
        
        db.session.commit()
        print(f"\n✅ Автоматически создано {mapped_count} маппингов")

def create_manual_mapping_template():
    """Создание шаблона для ручного маппинга"""
    
    print("\n📝 СОЗДАНИЕ ШАБЛОНА ДЛЯ РУЧНОГО МАППИНГА")
    print("=" * 60)
    
    with app.app_context():
        
        # Получаем уроки без маппинга
        lessons_with_mapping = set(m.lesson_id for m in ContentDomainMapping.query.filter_by(lesson_id=db.not_(None)).all())
        lessons_without_mapping = Lesson.query.filter(~Lesson.id.in_(lessons_with_mapping)).all()
        
        # Получаем все домены
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        # Создаем JSON шаблон
        template = {
            "manual_mappings": [],
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_lessons": len(lessons_without_mapping),
                "total_domains": len(domains)
            }
        }
        
        for lesson in lessons_without_mapping[:50]:  # Ограничиваем первыми 50 для примера
            module_name = lesson.module.title if lesson.module else "Нет модуля"
            subject_name = lesson.module.subject.name if lesson.module and lesson.module.subject else "Нет предмета"
            
            mapping_entry = {
                "lesson_id": lesson.id,
                "lesson_title": lesson.title,
                "module": module_name,
                "subject": subject_name,
                "suggested_domain": None,
                "manual_domain": None,
                "relevance_score": 0.5,
                "notes": ""
            }
            
            template["manual_mappings"].append(mapping_entry)
        
        # Сохраняем шаблон
        with open('scripts/manual_mapping_template.json', 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Создан шаблон для ручного маппинга: scripts/manual_mapping_template.json")
        print(f"   Содержит {len(template['manual_mappings'])} уроков для маппинга")

if __name__ == "__main__":
    print("🚀 Запуск анализа маппинга доменов...")
    
    try:
        analyze_domain_mapping()
        
        # Спрашиваем пользователя что делать дальше
        print("\n" + "=" * 60)
        print("Выберите действие:")
        print("1. Создать автоматический маппинг")
        print("2. Создать шаблон для ручного маппинга")
        print("3. Выход")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            create_auto_mapping()
        elif choice == "2":
            create_manual_mapping_template()
        elif choice == "3":
            print("Выход...")
        else:
            print("Неверный выбор")
        
        print("\n✅ Анализ завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 