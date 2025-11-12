#!/usr/bin/env python3
"""
Скрипт для загрузки сценариев виртуальных пациентов в базу данных
"""

import json
import os
import sys
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import VirtualPatientScenario

def load_scenarios():
    """Загрузить виртуальные пациенты сценарии в БД"""
    
    scenarios_config = [
        {
            'file': 'cards/virtual_patient/insulin-instructie.json',
            'specialty': 'verpleegkundige',
            'title': 'Insuline Instructie',
            'difficulty': 'medium'
        },
        {
            'file': 'cards/virtual_patient/perikoronorit.json',
            'specialty': 'dentistry',
            'title': 'Perikoronitis',
            'difficulty': 'medium'
        },
        {
            'file': 'cards/virtual_patient/slaapproblemen.json',
            'specialty': 'general_medicine',
            'title': 'Slaapproblemen',
            'difficulty': 'easy'
        },
        {
            'file': 'cards/virtual_patient/acute_pain.json',
            'specialty': 'dentistry',
            'title': 'Acute Pijn',
            'difficulty': 'hard'
        },
        {
            'file': 'cards/virtual_patient/anxious_pat.json',
            'specialty': 'dentistry',
            'title': 'Angstige Patiënt',
            'difficulty': 'medium'
        },
        {
            'file': 'cards/virtual_patient/complex_problem.json',
            'specialty': 'dentistry',
            'title': 'Complex Probleem',
            'difficulty': 'hard'
        },
        {
            'file': 'cards/virtual_patient/tooth_agony.json',
            'specialty': 'dentistry',
            'title': 'Tandpijn',
            'difficulty': 'easy'
        },
        {
            'file': 'cards/virtual_patient/retreat.json',
            'specialty': 'dentistry',
            'title': 'Retreat',
            'difficulty': 'medium'
        }
    ]
    
    loaded_count = 0
    
    for config in scenarios_config:
        filepath = config['file']
        specialty = config['specialty']
        title = config['title']
        difficulty = config['difficulty']
        
        if not os.path.exists(filepath):
            print(f"❌ Файл не найден: {filepath}")
            continue
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Проверить что сценарий ещё не загружен
            existing = VirtualPatientScenario.query.filter_by(title=title).first()
            
            if existing:
                print(f"⏭️  Сценарий уже существует: {title}")
                continue
            
            # Извлечь ключевые слова из данных
            keywords = []
            if 'scenario_info' in data and 'keywords' in data['scenario_info']:
                keywords = data['scenario_info']['keywords']
            elif 'keywords' in data:
                keywords = data['keywords']
            else:
                # Попробуем извлечь ключевые слова из текста
                keywords = [title.lower().replace(' ', '_')]
            
            # Создать новый сценарий
            scenario = VirtualPatientScenario(
                title=title,
                description=data.get('description', {}).get('nl', '') if isinstance(data.get('description'), dict) else data.get('description', ''),
                specialty=specialty,
                difficulty=difficulty,
                max_score=data.get('scenario_info', {}).get('max_score', 100),
                is_published=True,
                scenario_data=json.dumps(data),
                target_keywords=json.dumps(keywords)
            )
            
            db.session.add(scenario)
            loaded_count += 1
            print(f"✓ Добавлен: {title} ({specialty}) - {difficulty}")
        
        except Exception as e:
            print(f"❌ Ошибка при загрузке {filepath}: {str(e)}")
            continue
    
    try:
        db.session.commit()
        print(f"\n✅ Все сценарии загружены успешно! Загружено: {loaded_count}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении в БД: {str(e)}")
        db.session.rollback()

def check_existing_scenarios():
    """Проверить существующие сценарии в БД"""
    print("\n📊 Существующие сценарии в БД:")
    print("-" * 50)
    
    scenarios = VirtualPatientScenario.query.all()
    for scenario in scenarios:
        print(f"ID: {scenario.id} | {scenario.title} | {scenario.specialty} | {scenario.difficulty}")

if __name__ == '__main__':
    with app.app_context():
        print("🩺 Загрузка сценариев виртуальных пациентов")
        print("=" * 50)
        
        # Проверим существующие сценарии
        check_existing_scenarios()
        
        print("\n🚀 Начинаем загрузку...")
        load_scenarios()
        
        # Покажем результат
        check_existing_scenarios()





