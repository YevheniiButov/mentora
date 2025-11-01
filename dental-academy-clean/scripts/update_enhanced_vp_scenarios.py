#!/usr/bin/env python3
"""
Скрипт для обновления Enhanced версий Virtual Patient сценариев

Этот скрипт:
1. Находит старые сценарии по title (частичное совпадение)
2. Загружает новые Enhanced версии
3. Удаляет старые сценарии

Использование:
    python scripts/update_enhanced_vp_scenarios.py
"""

import json
import os
import sys
from datetime import datetime, timezone

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import VirtualPatientScenario, VirtualPatientAttempt

# Маппинг: старые title patterns → новые Enhanced файлы
ENHANCED_SCENARIOS = [
    {
        'old_title_patterns': ['Complex Probleem', 'complex_problem', 'Complex Dental'],
        'new_file': 'cards/virtual_patient/complex_problem_complete.json',
        'description': 'Complex Dental Problem (Enhanced with all features)'
    },
    {
        'old_title_patterns': ['Slaapproblemen', 'slaapproblemen', 'Slaap'],
        'new_file': 'cards/virtual_patient/slaapproblemen_enhanced.json',
        'description': 'Slaapproblemen & Angst (Enhanced)'
    },
    {
        'old_title_patterns': ['Acute Pijn op de Borst', 'Pijn op de Borst', 'chest pain', 'STEMI'],
        'new_file': 'cards/virtual_patient/chest_pain_stemi_enhanced.json',
        'description': 'Acute Chest Pain STEMI (Enhanced)'
    },
    {
        'old_title_patterns': ['Chronische Rugpijn', 'Rugpijn', 'chronische_rugpijn', 'lage rugpijn'],
        'new_file': 'cards/virtual_patient/chronic_back_pain_enhanced.json',
        'description': 'Chronische Rugpijn (Enhanced)'
    }
]


def find_old_scenarios(pattern):
    """Найти старые сценарии по паттерну в title"""
    scenarios = VirtualPatientScenario.query.all()
    matched = []
    
    pattern_lower = pattern.lower()
    
    for scenario in scenarios:
        title_lower = scenario.title.lower()
        # Проверяем частичное совпадение
        if pattern_lower in title_lower or title_lower in pattern_lower:
            # Исключаем уже Enhanced версии (содержат "Enhanced" в title)
            if 'enhanced' not in title_lower:
                matched.append(scenario)
    
    return matched


def extract_title_from_json(data):
    """Извлечь title из JSON данных"""
    if 'title' in data:
        if isinstance(data['title'], dict) and 'nl' in data['title']:
            return data['title']['nl']
        elif isinstance(data['title'], str):
            return data['title']
    return None


def extract_description_from_json(data):
    """Извлечь description из JSON данных"""
    if 'description' in data:
        if isinstance(data['description'], dict) and 'nl' in data['description']:
            return data['description']['nl']
        elif isinstance(data['description'], str):
            return data['description']
    return ''


def extract_keywords_from_json(data):
    """Извлечь keywords из JSON данных"""
    keywords = []
    if 'scenario_info' in data and 'keywords' in data['scenario_info']:
        keywords = data['scenario_info']['keywords']
    elif 'keywords' in data:
        keywords = data['keywords']
    else:
        # Попробуем извлечь из title
        title = extract_title_from_json(data)
        if title:
            keywords = [title.lower().replace(' ', '_').replace('🎯', '').replace('🌙', '').replace('🚨', '').replace('💪', '').strip()]
    
    return keywords if keywords else []


def update_scenarios():
    """Обновить Enhanced сценарии"""
    
    print("🔄 Обновление Enhanced Virtual Patient сценариев")
    print("=" * 70)
    print()
    
    total_updated = 0
    total_deleted = 0
    
    with app.app_context():
        for config in ENHANCED_SCENARIOS:
            new_file = config['new_file']
            old_patterns = config['old_title_patterns']
            
            print(f"\n📦 Обработка: {new_file}")
            print("-" * 70)
            
            # Проверяем существование нового файла
            if not os.path.exists(new_file):
                print(f"❌ Новый файл не найден: {new_file}")
                continue
            
            # Загружаем новый JSON
            try:
                with open(new_file, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                
                # Извлекаем метаданные
                new_title = extract_title_from_json(new_data)
                if not new_title:
                    print(f"❌ Не удалось извлечь title из {new_file}")
                    continue
                
                new_description = extract_description_from_json(new_data)
                new_keywords = extract_keywords_from_json(new_data)
                new_specialty = new_data.get('specialty', 'general_medicine')
                new_difficulty = new_data.get('difficulty', 'medium')
                new_max_score = new_data.get('scenario_info', {}).get('max_score', 150)
                
                print(f"   📝 Новый title: {new_title}")
                print(f"   🏥 Specialty: {new_specialty}")
                print(f"   ⭐ Difficulty: {new_difficulty}")
                
                # Проверяем, не существует ли уже Enhanced версия
                existing_enhanced = VirtualPatientScenario.query.filter_by(title=new_title).first()
                
                if existing_enhanced:
                    print(f"   ⚠️  Enhanced версия уже существует в БД. Пропускаем.")
                    continue
                
                # Ищем старые сценарии
                old_scenarios = []
                for pattern in old_patterns:
                    found = find_old_scenarios(pattern)
                    for scenario in found:
                        if scenario not in old_scenarios:
                            old_scenarios.append(scenario)
                
                # Удаляем старые сценарии
                deleted_ids = []
                if old_scenarios:
                    print(f"   🗑️  Найдено {len(old_scenarios)} старых сценариев для замены:")
                    for old_scenario in old_scenarios:
                        print(f"      - ID {old_scenario.id}: '{old_scenario.title}' ({old_scenario.specialty})")
                        
                        # Проверяем, есть ли попытки (attempts) у этого сценария
                        attempts_count = VirtualPatientAttempt.query.filter_by(
                            scenario_id=old_scenario.id
                        ).count()
                        
                        if attempts_count > 0:
                            print(f"         ⚠️  ВНИМАНИЕ: У сценария {attempts_count} попыток. "
                                  f"Они останутся в БД (связь через scenario_id), но сценарий будет удален.")
                        
                        # Удаляем сценарий
                        db.session.delete(old_scenario)
                        deleted_ids.append(old_scenario.id)
                        total_deleted += 1
                else:
                    print(f"   ℹ️  Старые сценарии не найдены (возможно, уже обновлены)")
                
                # Создаем новый Enhanced сценарий
                new_scenario = VirtualPatientScenario(
                    title=new_title,
                    description=new_description,
                    specialty=new_specialty,
                    difficulty=new_difficulty,
                    max_score=new_max_score,
                    is_published=True,
                    scenario_data=json.dumps(new_data, ensure_ascii=False),
                    target_keywords=json.dumps(new_keywords, ensure_ascii=False),
                    created_at=datetime.now(timezone.utc)
                )
                
                db.session.add(new_scenario)
                db.session.flush()  # Получаем ID нового сценария
                
                print(f"   ✅ Создан новый Enhanced сценарий (ID: {new_scenario.id})")
                total_updated += 1
                
                # Коммитим изменения
                try:
                    db.session.commit()
                    print(f"   💾 Изменения сохранены в БД")
                except Exception as e:
                    print(f"   ❌ Ошибка при сохранении: {str(e)}")
                    db.session.rollback()
                    continue
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {str(e)}")
                continue
            except Exception as e:
                print(f"   ❌ Ошибка при обработке: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    print("\n" + "=" * 70)
    print(f"✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО")
    print(f"   📊 Обновлено сценариев: {total_updated}")
    print(f"   🗑️  Удалено старых: {total_deleted}")
    print()


def list_current_scenarios():
    """Показать текущие сценарии в БД"""
    print("\n📋 Текущие сценарии в БД:")
    print("-" * 70)
    
    scenarios = VirtualPatientScenario.query.order_by(VirtualPatientScenario.id).all()
    
    if not scenarios:
        print("   (БД пуста)")
        return
    
    for scenario in scenarios:
        attempts_count = VirtualPatientAttempt.query.filter_by(
            scenario_id=scenario.id
        ).count()
        
        enhanced_marker = "✅ Enhanced" if 'enhanced' in scenario.title.lower() or '🎯' in scenario.title or '🌙' in scenario.title or '🚨' in scenario.title or '💪' in scenario.title else ""
        
        print(f"   ID {scenario.id:3d} | {scenario.title[:50]:50s} | {scenario.specialty:20s} | "
              f"Попыток: {attempts_count:3d} {enhanced_marker}")


if __name__ == '__main__':
    with app.app_context():
        # Показываем текущее состояние
        print("🔍 Проверка текущего состояния БД...")
        list_current_scenarios()
        
        print("\n" + "=" * 70)
        response = input("\n❓ Продолжить обновление? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y', 'да', 'д']:
            update_scenarios()
            
            # Показываем финальное состояние
            print("\n🔍 Финальное состояние БД:")
            list_current_scenarios()
        else:
            print("\n❌ Обновление отменено пользователем")

