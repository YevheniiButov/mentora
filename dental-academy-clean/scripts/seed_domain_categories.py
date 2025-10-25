#!/usr/bin/env python3
"""
Seed Domain Categories Script

Creates 7 categories for BIG domains and assigns each domain to a category.
This script is idempotent and can be run multiple times safely.
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, DomainCategory, BIGDomain

# Category definitions
CATEGORIES = [
    {
        'name': 'Clinical Foundations',
        'name_nl': 'Klinische Basis',
        'description': 'Core clinical dental specialties and procedures',
        'icon': '🦷',
        'color': '#0066cc',
        'order': 1,
        'domains': [
            'Therapeutic Dentistry',
            'Surgical Dentistry',
            'Pediatric Dentistry',
            'Periodontology',
            'Prosthetic Dentistry',
            'Orthodontics'
        ]
    },
    {
        'name': 'Medical Sciences',
        'name_nl': 'Medische Wetenschappen',
        'description': 'Medical knowledge and pharmacology',
        'icon': '💊',
        'color': '#28a745',
        'order': 2,
        'domains': [
            'Pharmacology',
            'General Medicine',
            'Emergency Care',
            'Systemic Diseases',
            'Infection Control'
        ]
    },
    {
        'name': 'Diagnostics & Imaging',
        'name_nl': 'Diagnostiek & Beeldvorming',
        'description': 'Diagnostic methods and imaging techniques',
        'icon': '🔬',
        'color': '#17a2b8',
        'order': 3,
        'domains': [
            'Diagnostics',
            'Radiology',
            'Special Diagnosis',
            'Pathology'
        ]
    },
    {
        'name': 'Basic Sciences',
        'name_nl': 'Basiswetenschappen',
        'description': 'Fundamental scientific knowledge',
        'icon': '🧬',
        'color': '#6f42c1',
        'order': 4,
        'domains': [
            'Anatomy',
            'Physiology',
            'Microbiology',
            'Materials Science'
        ]
    },
    {
        'name': 'Research & Methodology',
        'name_nl': 'Onderzoek & Methodologie',
        'description': 'Research methods and data analysis',
        'icon': '📊',
        'color': '#fd7e14',
        'order': 5,
        'domains': [
            'Statistics and Data Analysis',
            'Research Methodology'
        ]
    },
    {
        'name': 'Clinical Practice',
        'name_nl': 'Klinische Praktijk',
        'description': 'Practical clinical skills and patient care',
        'icon': '👨‍⚕️',
        'color': '#20c997',
        'order': 6,
        'domains': [
            'Treatment Planning',
            'Practical Skills',
            'Communication Skills',
            'Special Patient Groups'
        ]
    },
    {
        'name': 'Professional Development',
        'name_nl': 'Professionele Ontwikkeling',
        'description': 'Professional skills and healthcare system knowledge',
        'icon': '🎓',
        'color': '#6c757d',
        'order': 7,
        'domains': [
            'Dutch Healthcare System',
            'Ethics and Law',
            'Prevention',
            'Professional Development'
        ]
    }
]

def get_statistics():
    """Get current statistics about categories and domains"""
    with app.app_context():
        categories_count = DomainCategory.query.filter_by(profession='tandarts').count()
        domains_count = BIGDomain.query.count()
        domains_with_category = BIGDomain.query.filter(BIGDomain.category_id.isnot(None)).count()
        domains_without_category = domains_count - domains_with_category
        
        return {
            'categories_count': categories_count,
            'domains_count': domains_count,
            'domains_with_category': domains_with_category,
            'domains_without_category': domains_without_category
        }

def create_categories(dry_run=True):
    """Create or update domain categories"""
    print("🏗️  СОЗДАНИЕ КАТЕГОРИЙ ДОМЕНОВ")
    print("=" * 50)
    
    categories_created = 0
    categories_updated = 0
    
    for category_data in CATEGORIES:
        # Check if category already exists
        existing_category = DomainCategory.query.filter_by(
            name=category_data['name'],
            profession='tandarts'
        ).first()
        
        if existing_category:
            print(f"📋 Категория '{category_data['name']}' уже существует")
            categories_updated += 1
        else:
            if not dry_run:
                category = DomainCategory(
                    name=category_data['name'],
                    name_nl=category_data['name_nl'],
                    description=category_data['description'],
                    icon=category_data['icon'],
                    profession='tandarts',
                    order=category_data['order'],
                    color=category_data['color'],
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.session.add(category)
                db.session.flush()  # Get the ID
                print(f"✅ Создана категория: {category_data['name']} (ID: {category.id})")
            else:
                print(f"🔍 [DRY RUN] Создана категория: {category_data['name']}")
            categories_created += 1
    
    if not dry_run:
        db.session.commit()
    
    return categories_created, categories_updated

def assign_domains_to_categories(dry_run=True):
    """Assign BIG domains to their categories"""
    print("\n🔗 НАЗНАЧЕНИЕ ДОМЕНОВ К КАТЕГОРИЯМ")
    print("=" * 50)
    
    domains_assigned = 0
    domains_not_found = 0
    categories_stats = {}
    
    for category_data in CATEGORIES:
        # Get the category
        category = DomainCategory.query.filter_by(
            name=category_data['name'],
            profession='tandarts'
        ).first()
        
        if not category:
            print(f"❌ Категория '{category_data['name']}' не найдена!")
            continue
        
        category_domains_assigned = 0
        category_domains_not_found = 0
        
        print(f"\n📂 Категория: {category.name} ({category.icon})")
        
        for domain_name in category_data['domains']:
            # Find the domain
            domain = BIGDomain.query.filter_by(name=domain_name).first()
            
            if domain:
                if not dry_run:
                    domain.category_id = category.id
                    db.session.add(domain)
                
                print(f"  ✅ {domain_name} -> {category.name}")
                domains_assigned += 1
                category_domains_assigned += 1
            else:
                print(f"  ❌ Домен '{domain_name}' не найден в базе данных")
                domains_not_found += 1
                category_domains_not_found += 1
        
        categories_stats[category.name] = {
            'assigned': category_domains_assigned,
            'not_found': category_domains_not_found
        }
    
    if not dry_run:
        db.session.commit()
    
    return domains_assigned, domains_not_found, categories_stats

def print_final_statistics():
    """Print final statistics"""
    print("\n📊 ФИНАЛЬНАЯ СТАТИСТИКА")
    print("=" * 50)
    
    stats = get_statistics()
    
    print(f"📋 Категорий создано: {stats['categories_count']}")
    print(f"🏥 Всего доменов: {stats['domains_count']}")
    print(f"✅ Доменов с категорией: {stats['domains_with_category']}")
    print(f"❌ Доменов без категории: {stats['domains_without_category']}")
    
    # Show categories with domain counts
    print(f"\n📂 КАТЕГОРИИ И ИХ ДОМЕНЫ:")
    categories = DomainCategory.query.filter_by(profession='tandarts').order_by(DomainCategory.order).all()
    
    for category in categories:
        domain_count = category.big_domains.count()
        print(f"  {category.icon} {category.name}: {domain_count} доменов")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Seed domain categories for tandarts')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Preview changes without saving (default: True)')
    parser.add_argument('--commit', action='store_true',
                       help='Actually save changes to database')
    
    args = parser.parse_args()
    
    # If --commit is specified, turn off dry-run
    if args.commit:
        dry_run = False
    else:
        dry_run = True
    
    print("🌱 СКРИПТ ЗАПОЛНЕНИЯ КАТЕГОРИЙ ДОМЕНОВ")
    print("=" * 60)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Режим: {'DRY RUN (предварительный просмотр)' if dry_run else 'COMMIT (сохранение изменений)'}")
    print()
    
    # Get initial statistics
    initial_stats = get_statistics()
    print("📊 НАЧАЛЬНАЯ СТАТИСТИКА:")
    print(f"  Категорий: {initial_stats['categories_count']}")
    print(f"  Доменов: {initial_stats['domains_count']}")
    print(f"  Доменов с категорией: {initial_stats['domains_with_category']}")
    print(f"  Доменов без категории: {initial_stats['domains_without_category']}")
    print()
    
    with app.app_context():
        try:
            # Create categories
            categories_created, categories_updated = create_categories(dry_run)
            
            # Assign domains to categories
            domains_assigned, domains_not_found, categories_stats = assign_domains_to_categories(dry_run)
            
            # Print results
            print(f"\n🎯 РЕЗУЛЬТАТЫ:")
            print(f"  📋 Категорий создано: {categories_created}")
            print(f"  📝 Категорий обновлено: {categories_updated}")
            print(f"  🔗 Доменов назначено: {domains_assigned}")
            print(f"  ❌ Доменов не найдено: {domains_not_found}")
            
            # Print category statistics
            print(f"\n📂 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
            for category_name, stats in categories_stats.items():
                print(f"  {category_name}: {stats['assigned']} назначено, {stats['not_found']} не найдено")
            
            # Print final statistics
            print_final_statistics()
            
            if dry_run:
                print(f"\n💡 Для применения изменений запустите:")
                print(f"   python scripts/seed_domain_categories.py --commit")
            else:
                print(f"\n✅ ИЗМЕНЕНИЯ СОХРАНЕНЫ В БАЗЕ ДАННЫХ!")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
