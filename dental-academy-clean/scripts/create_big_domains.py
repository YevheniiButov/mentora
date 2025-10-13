#!/usr/bin/env python3
"""
Скрипт для создания доменов BIG в базе данных
Читает домены из domains_config.json (30 доменов)
"""
import os
import sys
import json
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, BIGDomain

def create_big_domains():
    """Создает домены BIG из конфигурационного файла"""
    
    with app.app_context():
        try:
            print("🏗️ Создаем домены BIG...")
            
            # Проверяем, есть ли уже домены
            existing_domains = BIGDomain.query.count()
            if existing_domains > 0:
                print(f"✅ Домены уже существуют ({existing_domains}), пропускаем создание")
                return
            
            # Читаем домены из конфигурационного файла
            config_file = Path(__file__).parent / 'unified_system' / 'domains_config.json'
            
            if not config_file.exists():
                print(f"⚠️ Файл конфигурации не найден: {config_file}")
                print("📝 Используем базовый набор доменов...")
                domains_data = get_basic_domains()
            else:
                print(f"📖 Читаем домены из: {config_file}")
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    domains_data = config.get('domains', [])
                    print(f"📊 Найдено {len(domains_data)} доменов в конфигурации")
            
            created_count = 0
            for domain_data in domains_data:
                # Используем weight вместо weight_percentage если есть
                weight = domain_data.get('weight', domain_data.get('weight_percentage', 5.0))
                
                domain = BIGDomain(
                    code=domain_data['code'],
                    name=domain_data.get('name_nl') or domain_data.get('name'),
                    description=domain_data.get('description', ''),
                    weight_percentage=weight,
                    category=domain_data.get('category', 'THEORETICAL'),
                    exam_type=domain_data.get('exam_type', 'multiple_choice'),
                    is_critical=domain_data.get('is_critical', False)
                )
                db.session.add(domain)
                created_count += 1
                print(f"   ✅ {domain_data['code']}: {domain.name}")
            
            db.session.commit()
            print(f"\n✅ Создано {created_count} доменов BIG!")
            
        except Exception as e:
            print(f"❌ Ошибка создания доменов: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)

def get_basic_domains():
    """Возвращает базовый набор из 15 доменов если JSON недоступен"""
    return [
        {'code': 'THER', 'name': 'Therapeutische stomatologie', 'weight': 15.0, 'is_critical': True},
        {'code': 'SURG', 'name': 'Chirurgische stomatologie', 'weight': 12.0, 'is_critical': True},
        {'code': 'PROTH', 'name': 'Prothetische stomatologie', 'weight': 12.0, 'is_critical': True},
        {'code': 'PEDI', 'name': 'Pediatrische stomatologie', 'weight': 10.0, 'is_critical': True},
        {'code': 'PARO', 'name': 'Parodontologie', 'weight': 10.0, 'is_critical': True},
        {'code': 'ORTHO', 'name': 'Orthodontie', 'weight': 8.0, 'is_critical': True},
        {'code': 'PREV', 'name': 'Preventie', 'weight': 8.0, 'is_critical': True},
        {'code': 'ETHIEK', 'name': 'Ethiek en recht', 'weight': 5.0, 'is_critical': False},
        {'code': 'ANATOMIE', 'name': 'Anatomie', 'weight': 5.0, 'is_critical': False},
        {'code': 'FYSIOLOGIE', 'name': 'Fysiologie', 'weight': 5.0, 'is_critical': False},
        {'code': 'PATHOLOGIE', 'name': 'Pathologie', 'weight': 5.0, 'is_critical': False},
        {'code': 'MICROBIOLOGIE', 'name': 'Microbiologie', 'weight': 5.0, 'is_critical': False},
        {'code': 'MATERIAALKUNDE', 'name': 'Materiaalkunde', 'weight': 3.0, 'is_critical': False},
        {'code': 'RADIOLOGIE', 'name': 'Radiologie', 'weight': 4.0, 'is_critical': False},
        {'code': 'ALGEMENE_GENEESKUNDE', 'name': 'Algemene geneeskunde', 'weight': 3.0, 'is_critical': False}
    ]

if __name__ == "__main__":
    create_big_domains()
