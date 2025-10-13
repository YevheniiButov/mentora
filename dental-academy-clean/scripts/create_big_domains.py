#!/usr/bin/env python3
"""
Скрипт для создания доменов BIG в базе данных
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, BIGDomain

def create_big_domains():
    """Создает базовые домены BIG"""
    
    with app.app_context():
        try:
            print("🏗️ Создаем домены BIG...")
            
            # Проверяем, есть ли уже домены
            existing_domains = BIGDomain.query.count()
            if existing_domains > 0:
                print(f"✅ Домены уже существуют ({existing_domains}), пропускаем создание")
                return
            
            # Базовые домены BIG на основе ACTA программы
            domains_data = [
                {
                    'code': 'THER',
                    'name': 'Therapeutische stomatologie',
                    'description': 'Conserverende tandheelkunde en endodontie',
                    'weight_percentage': 15.0,
                    'is_core': True
                },
                {
                    'code': 'SURG',
                    'name': 'Chirurgische stomatologie',
                    'description': 'Orale chirurgie en implantologie',
                    'weight_percentage': 12.0,
                    'is_core': True
                },
                {
                    'code': 'PROTH',
                    'name': 'Prothetische stomatologie',
                    'description': 'Prothetische tandheelkunde',
                    'weight_percentage': 12.0,
                    'is_core': True
                },
                {
                    'code': 'PEDI',
                    'name': 'Pediatrische stomatologie',
                    'description': 'Kindertandheelkunde',
                    'weight_percentage': 10.0,
                    'is_core': True
                },
                {
                    'code': 'PARO',
                    'name': 'Parodontologie',
                    'description': 'Parodontologie en implantologie',
                    'weight_percentage': 10.0,
                    'is_core': True
                },
                {
                    'code': 'ORTHO',
                    'name': 'Orthodontie',
                    'description': 'Orthodontie en dentofaciale orthopaedie',
                    'weight_percentage': 8.0,
                    'is_core': True
                },
                {
                    'code': 'PREV',
                    'name': 'Preventie',
                    'description': 'Preventieve tandheelkunde en gezondheidsbevordering',
                    'weight_percentage': 8.0,
                    'is_core': True
                },
                {
                    'code': 'ETHIEK',
                    'name': 'Ethiek en recht',
                    'description': 'Beroepsethiek en gezondheidsrecht',
                    'weight_percentage': 5.0,
                    'is_core': False
                },
                {
                    'code': 'ANATOMIE',
                    'name': 'Anatomie',
                    'description': 'Hoofd-hals anatomie',
                    'weight_percentage': 5.0,
                    'is_core': False
                },
                {
                    'code': 'FYSIOLOGIE',
                    'name': 'Fysiologie',
                    'description': 'Orale fysiologie',
                    'weight_percentage': 5.0,
                    'is_core': False
                },
                {
                    'code': 'PATHOLOGIE',
                    'name': 'Pathologie',
                    'description': 'Orale pathologie',
                    'weight_percentage': 5.0,
                    'is_core': False
                },
                {
                    'code': 'MICROBIOLOGIE',
                    'name': 'Microbiologie',
                    'description': 'Orale microbiologie',
                    'weight_percentage': 5.0,
                    'is_core': False
                },
                {
                    'code': 'MATERIAALKUNDE',
                    'name': 'Materiaalkunde',
                    'description': 'Dentale materialen',
                    'weight_percentage': 3.0,
                    'is_core': False
                },
                {
                    'code': 'RADIOLOGIE',
                    'name': 'Radiologie',
                    'description': 'Dentale radiologie',
                    'weight_percentage': 4.0,
                    'is_core': False
                },
                {
                    'code': 'ALGEMENE_GENEESKUNDE',
                    'name': 'Algemene geneeskunde',
                    'description': 'Relevante algemene geneeskunde',
                    'weight_percentage': 3.0,
                    'is_core': False
                }
            ]
            
            created_count = 0
            for domain_data in domains_data:
                domain = BIGDomain(
                    code=domain_data['code'],
                    name=domain_data['name'],
                    description=domain_data['description'],
                    weight_percentage=domain_data['weight_percentage'],
                    is_core=domain_data['is_core']
                )
                db.session.add(domain)
                created_count += 1
                print(f"   ✅ {domain_data['code']}: {domain_data['name']}")
            
            db.session.commit()
            print(f"\n✅ Создано {created_count} доменов BIG!")
            
        except Exception as e:
            print(f"❌ Ошибка создания доменов: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    create_big_domains()

