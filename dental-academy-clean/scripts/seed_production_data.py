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
    """Загружает структуру BI-toets путей обучения согласно BI-toets 2025"""
    print("🔄 Загружаем BI-toets структуру...")
    
    # Создаем пути обучения согласно BI-toets 2025 (9 путей)
    learning_paths = [
        {
            'id': 'basic_medical_sciences',
            'name': 'Basic Medical Sciences',
            'name_nl': 'Basic Medical Sciences',
            'name_ru': 'Базовые медицинские науки',
            'description': 'Общие медицинские науки - Multiple choice формат',
            'exam_component': 'THEORETICAL',
            'exam_weight': 15.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 8,
            'total_estimated_hours': 80
        },
        {
            'id': 'thk_1',
            'name': 'THK I - Tandheelkunde Kern I',
            'name_nl': 'THK I - Tandheelkunde Kern I',
            'name_ru': 'THK I - Основы стоматологии I',
            'description': 'Кариология, Слюна, Эндодонтия, Детская стоматология, Пародонтология',
            'exam_component': 'THEORETICAL',
            'exam_weight': 25.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 12,
            'total_estimated_hours': 120
        },
        {
            'id': 'thk_2',
            'name': 'THK II - Tandheelkunde Kern II',
            'name_nl': 'THK II - Tandheelkunde Kern II',
            'name_ru': 'THK II - Основы стоматологии II',
            'description': 'Протезирование, Ортодонтия, Челюстно-лицевая хирургия, Кинезиология',
            'exam_component': 'THEORETICAL',
            'exam_weight': 25.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 12,
            'total_estimated_hours': 120
        },
        {
            'id': 'radiology',
            'name': 'Radiologie',
            'name_nl': 'Radiologie',
            'name_ru': 'Рентгенология',
            'description': 'Рентгенология - Multiple choice формат',
            'exam_component': 'THEORETICAL',
            'exam_weight': 10.0,
            'exam_type': 'multiple_choice',
            'duration_weeks': 6,
            'total_estimated_hours': 60
        },
        {
            'id': 'statistics',
            'name': 'Statistiek voor tandheelkunde',
            'name_nl': 'Statistiek voor tandheelkunde',
            'name_ru': 'Статистика для стоматологии',
            'description': 'Статистика - Multiple choice, Open book',
            'exam_component': 'METHODOLOGY',
            'exam_weight': 8.0,
            'exam_type': 'open_book',
            'duration_weeks': 4,
            'total_estimated_hours': 40
        },
        {
            'id': 'research_methodology',
            'name': 'Onderzoeksmethodologie',
            'name_nl': 'Onderzoeksmethodologie',
            'name_ru': 'Методология исследований',
            'description': 'Методология - Short answer, Open book (PICO, дизайн исследований)',
            'exam_component': 'METHODOLOGY',
            'exam_weight': 7.0,
            'exam_type': 'open_book',
            'duration_weeks': 4,
            'total_estimated_hours': 40
        },
        {
            'id': 'simodont_training',
            'name': 'Praktische vaardigheden (Simodont voorbereiding)',
            'name_nl': 'Praktische vaardigheden (Simodont voorbereiding)',
            'name_ru': 'Практические навыки (подготовка к Simodont)',
            'description': 'Практические экзамены - Manual vaardigheden, Caries excavation, Endodontic preparation, Kroon preparation',
            'exam_component': 'PRACTICAL',
            'exam_weight': 20.0,
            'exam_type': 'practical',
            'duration_weeks': 10,
            'total_estimated_hours': 100
        },
        {
            'id': 'communication_ethics',
            'name': 'Communicatie en ethiek',
            'name_nl': 'Communicatie en ethiek',
            'name_ru': 'Коммуникация и этика',
            'description': 'Intake gesprek, Ethics & Social Dentistry',
            'exam_component': 'COMMUNICATION',
            'exam_weight': 10.0,
            'exam_type': 'interview',
            'duration_weeks': 6,
            'total_estimated_hours': 60
        },
        {
            'id': 'treatment_planning',
            'name': 'Behandelplanning',
            'name_nl': 'Behandelplanning',
            'name_ru': 'Планирование лечения',
            'description': 'Treatment Planning - Casus 1, 2, 3, Endodontics casus, Gebits reiniging',
            'exam_component': 'CLINICAL',
            'exam_weight': 15.0,
            'exam_type': 'case_study',
            'duration_weeks': 8,
            'total_estimated_hours': 80
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
    
    # Проверяем, есть ли уже домены
    existing_domains = BIGDomain.query.count()
    if existing_domains > 0:
        print(f"✅ Домены уже существуют ({existing_domains} доменов)")
        return
    
    # Инициализируем домены через модель
    BIGDomain.initialize_domains()
    print("✅ Домены загружены")

def load_questions():
    """Загружает вопросы из JSON файлов"""
    print("🔄 Загружаем вопросы...")
    
    # Проверяем, есть ли уже вопросы
    existing_questions = Question.query.count()
    if existing_questions > 0:
        print(f"✅ Вопросы уже существуют ({existing_questions} вопросов)")
        return
    
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
        
        db.session.commit()
        print(f"✅ Загружено {len(questions_data)} вопросов")
    else:
        print("⚠️ Файл с вопросами не найден")

def load_learning_cards():
    """Загружает обучающие карточки из всех папок cards"""
    print("🔄 Загружаем обучающие карточки...")
    
    cards_dir = Path(__file__).parent.parent / 'cards'
    if not cards_dir.exists():
        print("⚠️ Папка cards не найдена")
        return
    
    total_cards = 0
    
    # Проходим по всем папкам в cards
    for category_dir in cards_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        print(f"📁 Обрабатываем категорию: {category_name}")
        
        # Ищем файлы с карточками
        card_files = list(category_dir.glob('*.json')) + list(category_dir.glob('*.txt'))
        
        for card_file in card_files:
            try:
                if card_file.suffix == '.json':
                    with open(card_file, 'r', encoding='utf-8') as f:
                        cards_data = json.load(f)
                        
                    if isinstance(cards_data, list):
                        for card in cards_data:
                            # Здесь можно добавить логику сохранения карточек в БД
                            # Пока просто считаем
                            total_cards += 1
                    else:
                        total_cards += 1
                        
                elif card_file.suffix == '.txt':
                    # Для текстовых файлов просто считаем строки как карточки
                    with open(card_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        total_cards += len([line for line in lines if line.strip()])
                        
            except json.JSONDecodeError as e:
                print(f"⚠️ Ошибка JSON в {card_file.name}: {e}")
            except Exception as e:
                print(f"⚠️ Ошибка при обработке {card_file.name}: {e}")
    
    print(f"✅ Найдено {total_cards} обучающих карточек в {len(list(cards_dir.iterdir()))} категориях")

def load_tests_from_cards():
    """Загружает тесты из папок cards"""
    print("🔄 Загружаем тесты из папок cards...")
    
    cards_dir = Path(__file__).parent.parent / 'cards'
    if not cards_dir.exists():
        print("⚠️ Папка cards не найдена")
        return
    
    total_tests = 0
    
    # Проходим по всем папкам в cards
    for category_dir in cards_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        category_name = category_dir.name
        print(f"📁 Ищем тесты в категории: {category_name}")
        
        # Ищем файлы с тестами
        test_files = list(category_dir.glob('*test*.json')) + list(category_dir.glob('*tests*.json'))
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    
                if isinstance(test_data, list):
                    total_tests += len(test_data)
                else:
                    total_tests += 1
                    
                print(f"✅ Загружен тест: {test_file.name}")
                        
            except Exception as e:
                print(f"⚠️ Ошибка при обработке теста {test_file}: {e}")
    
    print(f"✅ Найдено {total_tests} тестов в папках cards")

def load_virtual_patients():
    """Загружает виртуальных пациентов"""
    print("🔄 Загружаем виртуальных пациентов...")
    
    # Проверяем, есть ли уже виртуальные пациенты
    existing_vp = VirtualPatientScenario.query.count()
    if existing_vp > 0:
        print(f"✅ Виртуальные пациенты уже существуют ({existing_vp} пациентов)")
        return
    
    vp_dir = Path(__file__).parent.parent / 'cards' / 'virtual_patient'
    if vp_dir.exists():
        loaded_count = 0
        for vp_file in vp_dir.glob('*.json'):
            try:
                with open(vp_file, 'r', encoding='utf-8') as f:
                    vp_data = json.load(f)
                
                # Проверяем структуру данных
                if isinstance(vp_data, dict) and 'title' in vp_data:
                    # Обрабатываем title (может быть строкой или словарем с переводами)
                    title = vp_data['title']
                    if isinstance(title, dict):
                        # Берем первый доступный перевод или английский
                        title = title.get('en', title.get('nl', title.get('ru', str(title))))
                    
                    # Обрабатываем description (может быть строкой или словарем с переводами)
                    description = vp_data.get('description', '')
                    if isinstance(description, dict):
                        # Берем первый доступный перевод или английский
                        description = description.get('en', description.get('nl', description.get('ru', str(description))))
                    
                    scenario = VirtualPatientScenario(
                        title=title,
                        description=description,
                        difficulty=vp_data.get('difficulty', 'medium'),
                        category=vp_data.get('category', 'diagnosis'),
                        scenario_data=json.dumps(vp_data.get('scenario_data', {})),
                        is_published=True
                    )
                    db.session.add(scenario)
                    loaded_count += 1
                    print(f"✅ Загружен виртуальный пациент: {title}")
                else:
                    print(f"⚠️ Неверная структура данных в {vp_file.name}")
                    
            except Exception as e:
                print(f"⚠️ Ошибка при обработке {vp_file.name}: {e}")
        
        db.session.commit()
        print(f"✅ Загружено {loaded_count} виртуальных пациентов")
    else:
        print("⚠️ Папка virtual_patient не найдена")

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

def create_learning_structure():
    """Создает правильную структуру обучения, связывая карточки из папки cards с путями обучения"""
    print("🔄 Создаем структуру обучения...")
    
    # Маппинг папок cards к путям обучения согласно BI-toets 2025
    cards_to_paths_mapping = {
        # Basic Medical Sciences (Теоретические экзамены)
        'anatomy': 'basic_medical_sciences',  # Анатомия
        'saliva': 'basic_medical_sciences',   # Слюна и биохимия
        
        # THK I - Tandheelkunde Kern I (Теоретические экзамены)
        'caries': 'thk_1',        # Кариология (Cariology)
        'endodontic': 'thk_1',    # Эндодонтия (Endodontics)
        'pediatric': 'thk_1',     # Детская стоматология (Paediatric dentistry)
        'periodontic': 'thk_1',   # Пародонтология (Periodontology)
        
        # THK II - Tandheelkunde Kern II (Теоретические экзамены)
        # Примечание: В THK II протезирование, ортодонтия, хирургия, но у нас нет этих папок в cards/
        
        # Radiologie (Теоретические экзамены)
        # Примечание: У нас нет папки radiology в cards/
        
        # Statistiek voor tandheelkunde (Теоретические экзамены)
        'statistics': 'statistics', # Статистика (Multiple choice, Open book)
        
        # Onderzoeksmethodologie (Теоретические экзамены)
        'Methodology': 'research_methodology', # Методология (Short answer, Open book)
        
        # Communicatie en ethiek (Коммуникация и этика)
        'virtual_patient': 'communication_ethics', # Виртуальные пациенты для коммуникации
        
        # Simodont Training (Практические экзамены)
        # Примечание: У нас нет папки simodont в cards/
        
        # Behandelplanning (Планирование лечения)
        # Примечание: У нас нет папки treatment_planning в cards/
    }
    
    # Создаем предметы для каждого пути обучения
    for cards_folder, path_id in cards_to_paths_mapping.items():
        print(f"📁 Обрабатываем папку {cards_folder} для пути {path_id}")
        
        # Получаем путь обучения
        learning_path = LearningPath.query.get(path_id)
        if not learning_path:
            print(f"⚠️ Путь обучения {path_id} не найден")
            continue
        
        # Создаем предмет для этой папки
        subject_name = cards_folder.replace('_', ' ').title()
        subject = Subject.query.filter_by(
            name=subject_name,
            learning_path_id=learning_path.id
        ).first()
        
        if not subject:
            subject = Subject(
                name=subject_name,
                description=f"Subject {subject_name} for {learning_path.name}",
                learning_path_id=learning_path.id,
                order=len(Subject.query.filter_by(learning_path_id=learning_path.id).all()) + 1
            )
            db.session.add(subject)
            db.session.flush()
            print(f"✅ Создан предмет: {subject_name}")
        
        # Создаем модули на основе файлов в папке
        cards_dir = Path(__file__).parent.parent / 'cards' / cards_folder
        if cards_dir.exists():
            # Создаем модуль для обучающих карточек
            learning_module = Module.query.filter_by(
                title=f"Learning Cards {subject_name}",
                subject_id=subject.id
            ).first()
            
            if not learning_module:
                learning_module = Module(
                    title=f"Learning Cards {subject_name}",
                    description=f"Learning materials for {subject_name}",
                    subject_id=subject.id,
                    order=1,
                    module_type='learning_cards'
                )
                db.session.add(learning_module)
                db.session.flush()
                print(f"✅ Создан модуль: Learning Cards {subject_name}")
            
            # Создаем модуль для тестов
            test_module = Module.query.filter_by(
                title=f"Tests {subject_name}",
                subject_id=subject.id
            ).first()
            
            if not test_module:
                test_module = Module(
                    title=f"Tests {subject_name}",
                    description=f"Tests for {subject_name}",
                    subject_id=subject.id,
                    order=2,
                    module_type='tests'
                )
                db.session.add(test_module)
                db.session.flush()
                print(f"✅ Создан модуль: Tests {subject_name}")
            
            # Создаем уроки на основе файлов
            for file_path in cards_dir.iterdir():
                if file_path.is_file():
                    file_name = file_path.stem
                    file_ext = file_path.suffix
                    
                    if file_ext in ['.json', '.txt']:
                        # Определяем тип контента
                        if 'test' in file_name.lower():
                            module = test_module
                            lesson_type = 'test'
                        else:
                            module = learning_module
                            lesson_type = 'learning_card'
                        
                        # Создаем урок
                        lesson = Lesson.query.filter_by(
                            title=file_name.replace('_', ' ').title(),
                            module_id=module.id
                        ).first()
                        
                        if not lesson:
                            lesson = Lesson(
                                title=file_name.replace('_', ' ').title(),
                                content=f"Content from file {file_path.name}",
                                content_type=lesson_type,
                                module_id=module.id,
                                order=len(Lesson.query.filter_by(module_id=module.id).all()) + 1
                            )
                            db.session.add(lesson)
                            print(f"✅ Создан урок: {lesson.title}")
    
    db.session.commit()
    print("✅ Структура обучения создана")

def main():
    """Основная функция загрузки данных"""
    with app.app_context():
        try:
            print("🚀 Начинаем загрузку данных для production...")
            
            # Создаем таблицы
            db.create_all()
            
            # Загружаем структуру
            load_bi_toets_structure()
            load_domains()
            
            # Создаем структуру обучения
            create_learning_structure()
            
            # Загружаем контент
            load_questions()
            load_learning_cards()
            load_tests_from_cards()
            load_virtual_patients()
            load_achievements()
            
            # Создаем администратора
            create_admin_user()
            
            print("🎉 Загрузка данных завершена успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка при загрузке данных: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    main() 