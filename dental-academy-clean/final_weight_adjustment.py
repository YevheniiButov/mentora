#!/usr/bin/env python3
"""
Финальная настройка весов для точного соответствия целевым показателям
"""

from app import app
from models import BIGDomain
from extensions import db
from sqlalchemy import text

def final_weight_adjustment():
    with app.app_context():
        print("🎯 ФИНАЛЬНАЯ НАСТРОЙКА ВЕСОВ")
        print("=" * 50)
        
        # Целевые показатели:
        # THEORETICAL: 70% (22 домена)
        # METHODOLOGY: 10% (2 домена) 
        # PRACTICAL: 15% (1 домен)
        # CLINICAL: 5% (3 домена)
        
        # Текущее состояние:
        # THEORETICAL: 77.1% (24 домена) - нужно уменьшить на 7.1%
        # METHODOLOGY: 10.0% (2 домена) - OK
        # PRACTICAL: 12.0% (1 домен) - нужно увеличить на 3%
        # CLINICAL: 0.9% (1 домен) - нужно увеличить на 4.1%
        
        print("📋 План корректировки:")
        print("   • Уменьшить THEORETICAL на 7.1%")
        print("   • Увеличить PRACTICAL на 3%")
        print("   • Увеличить CLINICAL на 4.1%")
        
        # Корректируем веса
        try:
            # Уменьшаем веса теоретических доменов (кроме критических)
            theoretical_non_critical = [
                'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 'ANATOMIE', 'FYSIOLOGIE',
                'PATHOLOGIE', 'MICROBIOLOGIE', 'MATERIAALKUNDE', 'RADIOLOGIE',
                'ALGEMENE_GENEESKUNDE', 'INFECTION', 'SPECIAL', 'DUTCH', 'PROFESSIONAL'
            ]
            
            # Уменьшаем вес некритических теоретических доменов
            new_theoretical_weight = 0.3  # Было 0.88, уменьшаем до 0.3
            for code in theoretical_non_critical:
                db.session.execute(text(
                    "UPDATE big_domain SET weight_percentage = :weight WHERE code = :code"
                ), {'weight': new_theoretical_weight, 'code': code})
                print(f"✅ {code}: {new_theoretical_weight:.1f}%")
            
            # Увеличиваем вес PRACTICAL_SKILLS
            db.session.execute(text(
                "UPDATE big_domain SET weight_percentage = 15.0 WHERE code = 'PRACTICAL_SKILLS'"
            ))
            print("✅ PRACTICAL_SKILLS: 15.0%")
            
            # Увеличиваем вес ETHIEK
            db.session.execute(text(
                "UPDATE big_domain SET weight_percentage = 5.0 WHERE code = 'ETHIEK'"
            ))
            print("✅ ETHIEK: 5.0%")
            
            db.session.commit()
            print("\n✅ Веса скорректированы!")
            
        except Exception as e:
            print(f"❌ Ошибка при корректировке: {e}")
            db.session.rollback()
            return
        
        # Проверяем результат
        print("\n📊 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
        print("=" * 50)
        
        domains = BIGDomain.query.filter_by(is_active=True).all()
        total_weight = sum(d.weight_percentage for d in domains)
        print(f"Общий вес: {total_weight:.1f}%")
        
        # Группируем по категориям
        categories = {}
        for domain in domains:
            cat = domain.category or 'UNCATEGORIZED'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(domain)
        
        for category, domain_list in categories.items():
            cat_weight = sum(d.weight_percentage for d in domain_list)
            print(f"\n📋 {category} ({len(domain_list)} доменов, {cat_weight:.1f}%):")
            for domain in sorted(domain_list, key=lambda x: x.weight_percentage, reverse=True):
                critical = "⭐" if domain.is_critical else "  "
                print(f"   {critical} {domain.code:15} | {domain.name:35} | {domain.weight_percentage:5.1f}%")
        
        # Проверяем соответствие целевым показателям
        print(f"\n🎯 СООТВЕТСТВИЕ ЦЕЛЕВЫМ ПОКАЗАТЕЛЯМ:")
        theoretical_weight = sum(d.weight_percentage for d in domains if d.category == 'THEORETICAL')
        methodology_weight = sum(d.weight_percentage for d in domains if d.category == 'METHODOLOGY')
        practical_weight = sum(d.weight_percentage for d in domains if d.category == 'PRACTICAL')
        clinical_weight = sum(d.weight_percentage for d in domains if d.category == 'CLINICAL')
        
        print(f"   • THEORETICAL: {theoretical_weight:.1f}% (цель: 70%) {'✅' if abs(theoretical_weight - 70) < 1 else '❌'}")
        print(f"   • METHODOLOGY: {methodology_weight:.1f}% (цель: 10%) {'✅' if abs(methodology_weight - 10) < 1 else '❌'}")
        print(f"   • PRACTICAL: {practical_weight:.1f}% (цель: 15%) {'✅' if abs(practical_weight - 15) < 1 else '❌'}")
        print(f"   • CLINICAL: {clinical_weight:.1f}% (цель: 5%) {'✅' if abs(clinical_weight - 5) < 1 else '❌'}")
        
        # Проверяем количество доменов
        theoretical_count = len([d for d in domains if d.category == 'THEORETICAL'])
        methodology_count = len([d for d in domains if d.category == 'METHODOLOGY'])
        practical_count = len([d for d in domains if d.category == 'PRACTICAL'])
        clinical_count = len([d for d in domains if d.category == 'CLINICAL'])
        
        print(f"\n📊 КОЛИЧЕСТВО ДОМЕНОВ:")
        print(f"   • THEORETICAL: {theoretical_count} (цель: 22) {'✅' if theoretical_count == 22 else '❌'}")
        print(f"   • METHODOLOGY: {methodology_count} (цель: 2) {'✅' if methodology_count == 2 else '❌'}")
        print(f"   • PRACTICAL: {practical_count} (цель: 1) {'✅' if practical_count == 1 else '❌'}")
        print(f"   • CLINICAL: {clinical_count} (цель: 3) {'✅' if clinical_count == 3 else '❌'}")
        print(f"   • ВСЕГО: {len(domains)} доменов")
        
        # Проверяем критические домены
        critical = [d for d in domains if d.is_critical]
        critical_weight = sum(d.weight_percentage for d in critical)
        print(f"\n⭐ КРИТИЧЕСКИЕ ДОМЕНЫ ({len(critical)} доменов, {critical_weight:.1f}%):")
        for domain in sorted(critical, key=lambda x: x.weight_percentage, reverse=True):
            print(f"   {domain.code:15} | {domain.name:35} | {domain.weight_percentage:5.1f}%")
        
        # Финальная валидация
        if abs(total_weight - 100.0) < 0.1:
            print(f"\n✅ ФИНАЛЬНАЯ ВАЛИДАЦИЯ ПРОЙДЕНА: Общий вес = {total_weight:.1f}%")
        else:
            print(f"\n❌ ФИНАЛЬНАЯ ВАЛИДАЦИЯ НЕ ПРОЙДЕНА: Общий вес = {total_weight:.1f}% (должен быть 100%)")

if __name__ == "__main__":
    final_weight_adjustment() 