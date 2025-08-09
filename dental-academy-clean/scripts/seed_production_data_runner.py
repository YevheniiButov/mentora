#!/usr/bin/env python3
"""
Улучшенный скрипт загрузки данных для production деплоя
Автоматически загружает все необходимые данные при первом запуске
С улучшенной обработкой ошибок и логированием
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('seed_production.log')
    ]
)
logger = logging.getLogger(__name__)

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

try:
    from app import app
    from extensions import db
    from models import (
        BIGDomain, LearningPath, Subject, Module, Lesson,
        Question, IRTParameters, VirtualPatientScenario,
        Achievement, User, UserProgress
    )
    logger.info("✅ Все модули импортированы успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта модулей: {e}")
    sys.exit(1)

def safe_json_load(file_path):
    """Безопасная загрузка JSON с обработкой ошибок"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.warning(f"⚠️ Ошибка JSON в {file_path.name}: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка чтения файла {file_path.name}: {e}")
        return None

def load_bi_toets_structure():
    """Загружает структуру BI-toets путей обучения согласно BI-toets 2025"""
    logger.info("🔄 Загружаем BI-toets структуру...")
    
    try:
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
                'id': 'communication_ethics',
                'name': 'Communicatie en ethiek',
                'name_nl': 'Communicatie en ethiek',
                'name_ru': 'Коммуникация и этика',
                'description': 'Коммуникация и этика - Multiple choice, Short answer',
                'exam_component': 'COMMUNICATION',
                'exam_weight': 5.0,
                'exam_type': 'multiple_choice',
                'duration_weeks': 3,
                'total_estimated_hours': 30
            },
            {
                'id': 'clinical_skills',
                'name': 'Klinische vaardigheden',
                'name_nl': 'Klinische vaardigheden',
                'name_ru': 'Клинические навыки',
                'description': 'Клинические навыки - OSCE формат',
                'exam_component': 'CLINICAL',
                'exam_weight': 5.0,
                'exam_type': 'osce',
                'duration_weeks': 3,
                'total_estimated_hours': 30
            }
        ]
        
        for path_data in learning_paths:
            try:
                # Используем Session.get() вместо Query.get()
                existing = db.session.get(LearningPath, path_data['id'])
                
                if not existing:
                    learning_path = LearningPath(**path_data)
                    db.session.add(learning_path)
                    logger.info(f"✅ Создан путь обучения: {path_data['name']}")
                else:
                    logger.info(f"ℹ️ Путь обучения уже существует: {path_data['name']}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка при создании пути обучения {path_data['name']}: {e}")
                continue
        
        db.session.commit()
        logger.info("✅ BI-toets структура загружена успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке BI-toets структуры: {e}")
        db.session.rollback()
        raise

def load_domains():
    """Загружает домены BI-toets"""
    logger.info("🔄 Загружаем домены BI-toets...")
    
    try:
        # Проверяем, есть ли уже домены
        existing_domains = BIGDomain.query.count()
        if existing_domains > 0:
            logger.info(f"✅ Домены уже существуют ({existing_domains} доменов)")
            return
        
        # Загружаем домены из файла domain_mapping.json
        domain_file = Path(__file__).parent.parent / 'cards' / 'domain_mapping.json'
        if not domain_file.exists():
            logger.error(f"❌ Файл доменов не найден: {domain_file}")
            return
        
        domains_data = safe_json_load(domain_file)
        if not domains_data:
            logger.error("❌ Не удалось загрузить данные доменов")
            return
        
        # Проверяем структуру файла
        if isinstance(domains_data, dict) and 'domain_mapping' in domains_data:
            # Файл имеет структуру {"domain_mapping": {...}}
            domain_mapping = domains_data['domain_mapping']
            domains_to_create = []
            
            for domain_name, domain_info in domain_mapping.items():
                if isinstance(domain_info, dict):
                    domain_data = {
                        'name': domain_name,
                        'description': domain_info.get('description', ''),
                        'weight': domain_info.get('weight', 1),
                        'priority': domain_info.get('priority', 'medium'),
                        'is_active': True
                    }
                    domains_to_create.append(domain_data)
        elif isinstance(domains_data, list):
            # Файл содержит список доменов
            domains_to_create = domains_data
        else:
            logger.error("❌ Неизвестная структура файла доменов")
            return
        
        for domain_data in domains_to_create:
            try:
                if isinstance(domain_data, dict):
                    domain = BIGDomain(**domain_data)
                    db.session.add(domain)
                    logger.info(f"✅ Создан домен: {domain_data.get('name', 'Unknown')}")
                else:
                    logger.warning(f"⚠️ Пропущен неверный формат домена: {domain_data}")
            except Exception as e:
                logger.error(f"❌ Ошибка при создании домена {domain_data.get('name', 'Unknown') if isinstance(domain_data, dict) else 'Unknown'}: {e}")
                continue
        
        db.session.commit()
        logger.info("✅ Домены загружены успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке доменов: {e}")
        db.session.rollback()
        raise

def load_questions():
    """Загружает вопросы из файлов JSON"""
    logger.info("🔄 Загружаем вопросы...")
    
    try:
        # Проверяем, есть ли уже вопросы
        existing_questions = Question.query.count()
        if existing_questions > 0:
            logger.info(f"✅ Вопросы уже существуют ({existing_questions} вопросов)")
            return
        
        # Загружаем вопросы из файлов
        questions_files = [
            Path(__file__).parent / '160.json',
            Path(__file__).parent / '160_2.json'
        ]
        
        total_questions = 0
        for file_path in questions_files:
            if not file_path.exists():
                logger.warning(f"⚠️ Файл вопросов не найден: {file_path}")
                continue
            
            questions_data = safe_json_load(file_path)
            if not questions_data:
                continue
            
            for question_data in questions_data:
                try:
                    question = Question(**question_data)
                    db.session.add(question)
                    total_questions += 1
                except Exception as e:
                    logger.error(f"❌ Ошибка при создании вопроса: {e}")
                    continue
        
        db.session.commit()
        logger.info(f"✅ Загружено {total_questions} вопросов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке вопросов: {e}")
        db.session.rollback()
        raise

def load_learning_cards():
    """Загружает обучающие карточки из папки cards"""
    logger.info("🔄 Загружаем обучающие карточки...")
    
    try:
        cards_dir = Path(__file__).parent.parent / 'cards'
        if not cards_dir.exists():
            logger.error(f"❌ Папка cards не найдена: {cards_dir}")
            return
        
        total_cards = 0
        categories_processed = 0
        
        for category_dir in cards_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                logger.info(f"📁 Обрабатываем категорию: {category_dir.name}")
                
                # Ищем файлы с карточками
                for file_path in category_dir.glob('*.json'):
                    if 'learning_cards' in file_path.name.lower():
                        cards_data = safe_json_load(file_path)
                        if cards_data:
                            # Здесь можно добавить логику загрузки карточек
                            # Пока просто считаем
                            if isinstance(cards_data, list):
                                total_cards += len(cards_data)
                            elif isinstance(cards_data, dict):
                                total_cards += 1
                
                categories_processed += 1
        
        logger.info(f"✅ Найдено {total_cards} обучающих карточек в {categories_processed} категориях")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке обучающих карточек: {e}")
        raise

def load_tests_from_cards():
    """Загружает тесты из папок cards"""
    logger.info("🔄 Загружаем тесты из папок cards...")
    
    try:
        cards_dir = Path(__file__).parent.parent / 'cards'
        if not cards_dir.exists():
            logger.error(f"❌ Папка cards не найдена: {cards_dir}")
            return
        
        total_tests = 0
        
        for category_dir in cards_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                logger.info(f"📁 Ищем тесты в категории: {category_dir.name}")
                
                # Ищем файлы с тестами
                for file_path in category_dir.glob('*.json'):
                    if 'test' in file_path.name.lower():
                        test_data = safe_json_load(file_path)
                        if test_data:
                            # Здесь можно добавить логику загрузки тестов
                            # Пока просто считаем
                            if isinstance(test_data, list):
                                total_tests += len(test_data)
                            elif isinstance(test_data, dict):
                                total_tests += 1
                            logger.info(f"✅ Загружен тест: {file_path.name}")
        
        logger.info(f"✅ Найдено {total_tests} тестов в папках cards")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке тестов: {e}")
        raise

def load_virtual_patients():
    """Загружает виртуальных пациентов"""
    logger.info("🔄 Загружаем виртуальных пациентов...")
    
    try:
        # Проверяем, есть ли уже виртуальные пациенты
        existing_patients = VirtualPatientScenario.query.count()
        if existing_patients > 0:
            logger.info(f"✅ Виртуальные пациенты уже существуют ({existing_patients} пациентов)")
            return
        
        # Загружаем виртуальных пациентов из папки virtual_patient
        vp_dir = Path(__file__).parent.parent / 'cards' / 'virtual_patient'
        if not vp_dir.exists():
            logger.error(f"❌ Папка virtual_patient не найдена: {vp_dir}")
            return
        
        total_patients = 0
        for file_path in vp_dir.glob('*.json'):
            patient_data = safe_json_load(file_path)
            if patient_data:
                try:
                    patient = VirtualPatientScenario(**patient_data)
                    db.session.add(patient)
                    total_patients += 1
                    logger.info(f"✅ Создан виртуальный пациент: {patient_data.get('name', 'Unknown')}")
                except Exception as e:
                    logger.error(f"❌ Ошибка при создании виртуального пациента: {e}")
                    continue
        
        db.session.commit()
        logger.info(f"✅ Загружено {total_patients} виртуальных пациентов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке виртуальных пациентов: {e}")
        db.session.rollback()
        raise

def load_achievements():
    """Загружает достижения"""
    logger.info("🔄 Загружаем достижения...")
    
    try:
        # Проверяем, есть ли уже достижения
        existing_achievements = Achievement.query.count()
        if existing_achievements > 0:
            logger.info(f"✅ Достижения уже существуют ({existing_achievements} достижений)")
            return
        
        # Создаем базовые достижения
        achievements_data = [
            {
                'name': 'first_steps',
                'title': 'Первые шаги',
                'description': 'Завершите первый урок',
                'category': 'learning',
                'points': 10,
                'icon': '🎯'
            },
            {
                'name': 'dedicated_student',
                'title': 'Преданный студент',
                'description': 'Завершите 10 уроков',
                'category': 'learning',
                'points': 50,
                'icon': '📚'
            },
            {
                'name': 'time_master',
                'title': 'Мастер времени',
                'description': 'Потратьте 10 часов на обучение',
                'category': 'time',
                'points': 100,
                'icon': '⏰'
            }
        ]
        
        for achievement_data in achievements_data:
            try:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
                logger.info(f"✅ Создано достижение: {achievement_data['title']}")
            except Exception as e:
                logger.error(f"❌ Ошибка при создании достижения {achievement_data['title']}: {e}")
                continue
        
        db.session.commit()
        logger.info("✅ Достижения загружены успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке достижений: {e}")
        db.session.rollback()
        raise

def create_admin_user():
    """Создает администратора"""
    logger.info("🔄 Создаем администратора...")
    
    try:
        # Проверяем, есть ли уже администратор
        admin = User.query.filter_by(email='admin@mentora.com').first()
        if admin:
            logger.info("✅ Администратор уже существует")
            return
        
        admin = User(
            email='admin@mentora.com',
            username='admin',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        # Устанавливаем пароль
        admin.set_password('admin123')
        
        # Устанавливаем флаг администратора через атрибут
        admin._is_admin = True
        
        db.session.add(admin)
        db.session.commit()
        logger.info("✅ Администратор создан успешно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании администратора: {e}")
        db.session.rollback()
        # Не прерываем выполнение скрипта из-за ошибки с администратором
        logger.warning("⚠️ Продолжаем выполнение скрипта без создания администратора")

def create_learning_structure():
    """Создает структуру обучения на основе папок cards"""
    logger.info("🔄 Создаем структуру обучения...")
    
    try:
        cards_dir = Path(__file__).parent.parent / 'cards'
        if not cards_dir.exists():
            logger.error(f"❌ Папка cards не найдена: {cards_dir}")
            return
        
        # Маппинг папок к путям обучения
        folder_to_path = {
            'anatomy': 'basic_medical_sciences',
            'saliva': 'basic_medical_sciences',
            'caries': 'thk_1',
            'endodontic': 'thk_1',
            'pediatric': 'thk_1',
            'periodontic': 'thk_1',
            'statistics': 'statistics',
            'Methodology': 'research_methodology',
            'virtual_patient': 'communication_ethics'
        }
        
        for folder_name, path_id in folder_to_path.items():
            folder_path = cards_dir / folder_name
            if not folder_path.exists():
                logger.warning(f"⚠️ Папка {folder_name} не найдена")
                continue
            
            logger.info(f"📁 Обрабатываем папку {folder_name} для пути {path_id}")
            
            try:
                # Используем Session.get() вместо Query.get()
                learning_path = db.session.get(LearningPath, path_id)
                if not learning_path:
                    logger.warning(f"⚠️ Путь обучения {path_id} не найден")
                    continue
                
                # Создаем предмет
                subject = Subject.query.filter_by(
                    name=folder_name.replace('_', ' ').title(),
                    learning_path_id=learning_path.id
                ).first()
                
                if not subject:
                    subject = Subject(
                        name=folder_name.replace('_', ' ').title(),
                        description=f"Subject for {folder_name}",
                        learning_path_id=learning_path.id,
                        order=1
                    )
                    db.session.add(subject)
                    db.session.flush()
                    logger.info(f"✅ Создан предмет: {subject.name}")
                
                # Создаем модули для карточек и тестов
                learning_module = Module.query.filter_by(
                    title=f"Learning Cards {subject.name}",
                    subject_id=subject.id
                ).first()
                
                if not learning_module:
                    learning_module = Module(
                        title=f"Learning Cards {subject.name}",
                        description=f"Learning materials for {subject.name}",
                        subject_id=subject.id,
                        order=1,
                        module_type='learning_cards'
                    )
                    db.session.add(learning_module)
                    db.session.flush()
                    logger.info(f"✅ Создан модуль: Learning Cards {subject.name}")
                
                test_module = Module.query.filter_by(
                    title=f"Tests {subject.name}",
                    subject_id=subject.id
                ).first()
                
                if not test_module:
                    test_module = Module(
                        title=f"Tests {subject.name}",
                        description=f"Tests for {subject.name}",
                        subject_id=subject.id,
                        order=2,
                        module_type='tests'
                    )
                    db.session.add(test_module)
                    db.session.flush()
                    logger.info(f"✅ Создан модуль: Tests {subject.name}")
                
                # Создаем уроки на основе файлов
                for file_path in folder_path.iterdir():
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
                                logger.info(f"✅ Создан урок: {lesson.title}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при обработке папки {folder_name}: {e}")
                continue
        
        db.session.commit()
        logger.info("✅ Структура обучения создана")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при создании структуры обучения: {e}")
        db.session.rollback()
        raise

def main():
    """Основная функция загрузки данных"""
    logger.info("🚀 Начинаем загрузку данных для production...")
    
    try:
        with app.app_context():
            # Создаем таблицы
            db.create_all()
            logger.info("✅ Таблицы созданы")
            
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
            
            logger.info("🎉 Загрузка данных завершена успешно!")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при загрузке данных: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
