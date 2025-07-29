#!/usr/bin/env python3
"""
Скрипт загрузки данных для production деплоя
Автоматически загружает все необходимые данные при первом запуске
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

from app import app
from extensions import db
from models import (
    BIGDomain, LearningPath, Subject, Module, Lesson,
    Question, IRTParameters, VirtualPatientScenario,
    Achievement, User, UserProgress
)

def load_bi_toets_structure():
    """Загружает структуру BI-toets путей обучения"""
    print("🔄 Загружаем BI-toets структуру...")
    
    # Создаем пути обучения (9 путей)
    learning_paths = [
        {
            'id': 'theoretical',
            'name': 'Theoretische Kennis',
            'name_nl': 'Theoretische Kennis',
            'name_ru': 'Теоретические знания',
            'description': 'Теоретические основы стоматологии',
            'exam_component': 'THEORETICAL',
            'exam_weight': 40.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 12,
            'total_estimated_hours': 120
        },
        {
            'id': 'methodology',
            'name': 'Methodologie',
            'name_nl': 'Methodologie',
            'name_ru': 'Методология',
            'description': 'Методологические подходы',
            'exam_component': 'METHODOLOGY',
            'exam_weight': 25.0,
            'exam_type': 'open_book',
            'duration_weeks': 8,
            'total_estimated_hours': 80
        },
        {
            'id': 'practical',
            'name': 'Praktische Vaardigheden',
            'name_nl': 'Praktische Vaardigheden',
            'name_ru': 'Практические навыки',
            'description': 'Практические навыки',
            'exam_component': 'PRACTICAL',
            'exam_weight': 20.0,
            'exam_type': 'practical_theory',
            'duration_weeks': 10,
            'total_estimated_hours': 100
        },
        {
            'id': 'clinical',
            'name': 'Klinische Competenties',
            'name_nl': 'Klinische Competenties',
            'name_ru': 'Клинические компетенции',
            'description': 'Клинические компетенции',
            'exam_component': 'CLINICAL',
            'exam_weight': 15.0,
            'exam_type': 'case_study',
            'duration_weeks': 6,
            'total_estimated_hours': 60
        }
    ]
    
    for path_data in learning_paths:
        existing = LearningPath.query.get(path_data['id'])
        if not existing:
            path = LearningPath(**path_data)
            db.session.add(path)
            print(f"✅ Создан путь: {path_data['name']}")
    
    db.session.commit()

def load_domains():
    """Загружает 30 доменов BI-toets"""
    print("🔄 Загружаем домены BI-toets...")
    
    # Инициализируем домены через модель
    BIGDomain.initialize_domains()
    print("✅ Домены загружены")

def load_questions():
    """Загружает вопросы из JSON файлов"""
    print("🔄 Загружаем вопросы...")
    
    # Загружаем основные вопросы
    questions_path = Path(__file__).parent / '160_2.json'
    if questions_path.exists():
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        for q_data in questions_data:
            # Создаем вопрос
            question = Question(
                text=q_data['text'],
                options=q_data['options'],
                correct_answer_index=q_data['correct_answer_index'],
                correct_answer_text=q_data['correct_answer_text'],
                explanation=q_data['explanation'],
                category=q_data.get('category', 'general'),
                domain=q_data.get('domain', 'general'),
                difficulty_level=q_data.get('difficulty_level', 2)
            )
            db.session.add(question)
            db.session.flush()  # Получаем ID
            
            # Создаем IRT параметры
            if 'irt_params' in q_data:
                irt_params = IRTParameters(
                    question_id=question.id,
                    difficulty=q_data['irt_params'].get('difficulty', 0.0),
                    discrimination=q_data['irt_params'].get('discrimination', 1.0),
                    guessing=q_data['irt_params'].get('guessing', 0.25)
                )
                db.session.add(irt_params)
        
        print(f"✅ Загружено {len(questions_data)} вопросов")

def load_virtual_patients():
    """Загружает виртуальных пациентов"""
    print("🔄 Загружаем виртуальных пациентов...")
    
    vp_dir = Path(__file__).parent.parent / 'cards' / 'virtual_patient'
    if vp_dir.exists():
        for vp_file in vp_dir.glob('*.json'):
            with open(vp_file, 'r', encoding='utf-8') as f:
                vp_data = json.load(f)
            
            scenario = VirtualPatientScenario(
                title=vp_data['title'],
                description=vp_data.get('description', ''),
                difficulty=vp_data.get('difficulty', 'medium'),
                category=vp_data.get('category', 'diagnosis'),
                scenario_data=json.dumps(vp_data['scenario_data']),
                is_published=True
            )
            db.session.add(scenario)
        
        print(f"✅ Загружено виртуальных пациентов")

def load_achievements():
    """Загружает систему достижений"""
    print("🔄 Загружаем достижения...")
    
    # Используем существующий скрипт
    try:
        from scripts.init_achievements_simple import init_achievements
        init_achievements()
        print("✅ Достижения загружены")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки достижений: {e}")

def create_admin_user():
    """Создает администратора по умолчанию"""
    print("🔄 Создаем администратора...")
    
    admin_email = "admin@mentora.nl"
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            email=admin_email,
            username="admin",
            password_hash=generate_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True,
            registration_completed=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Администратор создан: admin@mentora.nl / admin123")
    else:
        print("✅ Администратор уже существует")

def main():
    """Основная функция загрузки данных"""
    with app.app_context():
        try:
            print("🚀 Начинаем загрузку данных для production...")
            
            # Создаем таблицы
            db.create_all()
            print("✅ Таблицы созданы")
            
            # Загружаем данные
            load_bi_toets_structure()
            load_domains()
            load_questions()
            load_virtual_patients()
            load_achievements()
            create_admin_user()
            
            # Коммитим все изменения
            db.session.commit()
            print("🎉 Все данные загружены успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main() 