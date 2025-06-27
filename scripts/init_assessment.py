#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт инициализации базы данных для системы предварительной оценки знаний
Адаптировано под существующую структуру проекта Dental Academy

Запуск:
    $ python scripts/init_assessment.py
    
    Или через Flask CLI:
    $ flask shell
    >>> from scripts.init_assessment import initialize_assessment_system
    >>> initialize_assessment_system()
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

try:
    from app import app, db
    from models import (
        User, AssessmentCategory, AssessmentQuestion, 
        PreAssessmentAttempt, PreAssessmentAnswer, LearningPlan
    )
except ImportError as e:
    print(f"❌ Ошибка импорта модулей приложения: {e}")
    print(f"Убедитесь, что вы находитесь в корневой директории проекта")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Данные для инициализации системы оценивания
ASSESSMENT_CATEGORIES = [
    {
        'name': 'Основы медицинских наук',
        'slug': 'basic_medical_sciences',
        'description': 'Фундаментальные биомедицинские концепции для стоматологии',
        'icon': 'activity',
        'color': '#3ECDC1',
        'min_questions': 10,
        'order': 1
    },
    {
        'name': 'Терапевтическая стоматология I',
        'slug': 'therapeutic_dentistry_1',
        'description': 'Кариология, эндодонтия, пародонтология, детская стоматология',
        'icon': 'tool',
        'color': '#6C5CE7',
        'min_questions': 15,
        'order': 2
    },
    {
        'name': 'Терапевтическая стоматология II',
        'slug': 'therapeutic_dentistry_2',
        'description': 'Ортопедическая стоматология, хирургическая стоматология, ортодонтия',
        'icon': 'grid',
        'color': '#FDCB6E',
        'min_questions': 12,
        'order': 3
    },
    {
        'name': 'Рентгенология',
        'slug': 'radiology',
        'description': 'Методы стоматологической визуализации и интерпретация',
        'icon': 'camera',
        'color': '#00B894',
        'min_questions': 8,
        'order': 4
    },
    {
        'name': 'Статистика',
        'slug': 'statistics',
        'description': 'Статистические методы для медицинских исследований',
        'icon': 'bar-chart-2',
        'color': '#E17055',
        'min_questions': 6,
        'order': 5
    },
    {
        'name': 'Методология',
        'slug': 'methodology',
        'description': 'Методология исследований в стоматологии',
        'icon': 'layers',
        'color': '#74B9FF',
        'min_questions': 5,
        'order': 6
    }
]

# Примеры вопросов для каждой категории
SAMPLE_QUESTIONS = {
    'basic_medical_sciences': [
        {
            'question': 'Какая из перечисленных желез является самой крупной слюнной железой?',
            'options': [
                'Околоушная железа',
                'Поднижнечелюстная железа', 
                'Подъязычная железа',
                'Малые слюнные железы'
            ],
            'correct_answer': 0,
            'explanation': 'Околоушная железа является самой крупной слюнной железой, расположена в околоушно-жевательной области.',
            'difficulty': 'medium',
            'time_limit': 60
        },
        {
            'question': 'Какой тип слюны преобладает в состоянии покоя?',
            'options': [
                'Серозная слюна',
                'Слизистая слюна',
                'Смешанная слюна',
                'Плазма крови'
            ],
            'correct_answer': 1,
            'explanation': 'В состоянии покоя преобладает слизистая слюна, которая обеспечивает увлажнение слизистой оболочки.',
            'difficulty': 'easy',
            'time_limit': 45
        }
    ],
    'therapeutic_dentistry_1': [
        {
            'question': 'Какая стадия кариеса характеризуется поражением только эмали?',
            'options': [
                'Кариес в стадии пятна',
                'Поверхностный кариес',
                'Средний кариес',
                'Глубокий кариес'
            ],
            'correct_answer': 1,
            'explanation': 'Поверхностный кариес характеризуется поражением только эмали без вовлечения дентина.',
            'difficulty': 'medium',
            'time_limit': 60
        },
        {
            'question': 'Какой метод диагностики кариеса является наиболее информативным?',
            'options': [
                'Визуальный осмотр',
                'Рентгенологическое исследование',
                'Лазерная флюоресценция',
                'Комбинация методов'
            ],
            'correct_answer': 3,
            'explanation': 'Наиболее информативным является комплексный подход с использованием нескольких методов диагностики.',
            'difficulty': 'hard',
            'time_limit': 90
        }
    ],
    'therapeutic_dentistry_2': [
        {
            'question': 'Какой тип протезирования показан при отсутствии одного зуба?',
            'options': [
                'Съемное протезирование',
                'Несъемное протезирование',
                'Имплантация',
                'Все перечисленные варианты'
            ],
            'correct_answer': 3,
            'explanation': 'При отсутствии одного зуба могут применяться различные методы в зависимости от клинической ситуации.',
            'difficulty': 'medium',
            'time_limit': 75
        }
    ],
    'radiology': [
        {
            'question': 'Какой вид рентгенологического исследования является стандартным для диагностики кариеса?',
            'options': [
                'Панорамная томография',
                'Прицельная рентгенография',
                'Компьютерная томография',
                'Магнитно-резонансная томография'
            ],
            'correct_answer': 1,
            'explanation': 'Прицельная рентгенография является стандартным методом для диагностики кариеса.',
            'difficulty': 'easy',
            'time_limit': 60
        }
    ],
    'statistics': [
        {
            'question': 'Какой тип переменной представляет собой "пол пациента"?',
            'options': [
                'Количественная непрерывная',
                'Количественная дискретная',
                'Качественная номинальная',
                'Качественная порядковая'
            ],
            'correct_answer': 2,
            'explanation': 'Пол пациента является качественной номинальной переменной, так как категории не имеют порядка.',
            'difficulty': 'medium',
            'time_limit': 60
        }
    ],
    'methodology': [
        {
            'question': 'Какой тип исследования является наиболее достоверным для установления причинно-следственных связей?',
            'options': [
                'Поперечное исследование',
                'Когортное исследование',
                'Рандомизированное контролируемое исследование',
                'Описательное исследование'
            ],
            'correct_answer': 2,
            'explanation': 'Рандомизированное контролируемое исследование является золотым стандартом для установления причинно-следственных связей.',
            'difficulty': 'hard',
            'time_limit': 90
        }
    ]
}

def create_app_context():
    """Создание контекста Flask приложения"""
    try:
        return app.app_context()
    except Exception as e:
        logger.error(f"❌ Ошибка создания контекста приложения: {e}")
        return None

def init_assessment_tables():
    """Создание таблиц для системы оценки"""
    logger.info("🔧 Создание таблиц для системы оценки...")
    
    try:
        # Создаем таблицы если их нет
        db.create_all()
        logger.info("✅ Таблицы созданы успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")
        return False

def populate_assessment_categories():
    """Заполнение категорий оценки"""
    logger.info("📂 Создание категорий оценки...")
    
    categories_created = 0
    categories_skipped = 0
    
    try:
        for cat_data in ASSESSMENT_CATEGORIES:
            existing = AssessmentCategory.query.filter_by(slug=cat_data['slug']).first()
            
            if not existing:
                category = AssessmentCategory(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    description=cat_data['description'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    min_questions=cat_data['min_questions'],
                    order=cat_data['order'],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(category)
                categories_created += 1
                logger.info(f"  ➕ Создана категория: {cat_data['name']}")
            else:
                categories_skipped += 1
                logger.info(f"  ⚠️  Категория уже существует: {cat_data['name']}")
        
        db.session.commit()
        logger.info(f"✅ Категории созданы успешно. Создано: {categories_created}, Пропущено: {categories_skipped}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания категорий: {e}")
        db.session.rollback()
        return False

def populate_assessment_questions():
    """Заполнение вопросов оценки"""
    logger.info("❓ Создание вопросов оценки...")
    
    # Создаем маппинг категорий
    categories = AssessmentCategory.query.all()
    category_map = {cat.slug: cat.id for cat in categories}
    
    questions_created = 0
    questions_skipped = 0
    
    try:
        for category_slug, questions in SAMPLE_QUESTIONS.items():
            category_id = category_map.get(category_slug)
            
            if not category_id:
                logger.warning(f"  ⚠️  Категория не найдена: {category_slug}")
                continue
            
            for q_data in questions:
                # Проверяем, существует ли уже такой вопрос
                existing = AssessmentQuestion.query.filter_by(
                    question_text=q_data['question'][:100]  # Сравниваем первые 100 символов
                ).first()
                
                if existing:
                    questions_skipped += 1
                    continue
                
                question = AssessmentQuestion(
                    category_id=category_id,
                    question_text=q_data['question'],
                    question_type='multiple_choice',
                    correct_answer=q_data['correct_answer'],
                    explanation=q_data['explanation'],
                    difficulty_level=q_data['difficulty'],
                    time_limit=q_data['time_limit'],
                    points=1,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                # Устанавливаем опции
                question.set_options(q_data['options'])
                
                db.session.add(question)
                questions_created += 1
        
        db.session.commit()
        logger.info(f"✅ Создано вопросов: {questions_created}")
        logger.info(f"⚠️  Пропущено (уже существуют): {questions_skipped}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания вопросов: {e}")
        db.session.rollback()
        return False

def validate_assessment_data():
    """Валидация данных оценки"""
    logger.info("🔍 Валидация данных оценки...")
    
    try:
        # Проверяем категории
        total_categories = AssessmentCategory.query.count()
        logger.info(f"  📊 Категорий в базе: {total_categories}")
        
        # Проверяем вопросы
        total_questions = AssessmentQuestion.query.filter_by(is_active=True).count()
        logger.info(f"  ❓ Активных вопросов: {total_questions}")
        
        # Проверяем распределение по категориям
        for category in AssessmentCategory.query.all():
            questions_count = AssessmentQuestion.query.filter_by(
                category_id=category.id,
                is_active=True
            ).count()
            logger.info(f"    {category.name}: {questions_count} вопросов")
        
        # Проверяем валидность вопросов
        invalid_questions = []
        
        for question in AssessmentQuestion.query.filter_by(is_active=True):
            options = question.get_options()
            
            if len(options) < 2:
                invalid_questions.append(f"Вопрос {question.id}: мало вариантов ответов")
            
            if question.correct_answer >= len(options):
                invalid_questions.append(f"Вопрос {question.id}: неверный индекс правильного ответа")
            
            if not question.explanation:
                invalid_questions.append(f"Вопрос {question.id}: отсутствует объяснение")
        
        if invalid_questions:
            logger.error("  ❌ Найдены проблемы:")
            for issue in invalid_questions:
                logger.error(f"    {issue}")
            return False
        else:
            logger.info("  ✅ Все вопросы валидны")
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка валидации: {e}")
        return False

def create_sample_users():
    """Создание тестовых пользователей"""
    logger.info("👥 Создание тестовых пользователей...")
    
    sample_users = [
        {
            'username': 'test_student',
            'email': 'student@dentalacademy.test',
            'first_name': 'Тест',
            'last_name': 'Студент',
            'role': 'student'
        },
        {
            'username': 'test_admin',
            'email': 'admin@dentalacademy.test',
            'first_name': 'Администратор',
            'last_name': 'Тестовый',
            'role': 'admin'
        }
    ]
    
    users_created = 0
    
    try:
        for user_data in sample_users:
            existing = User.query.filter_by(email=user_data['email']).first()
            
            if not existing:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                # Устанавливаем простой пароль для тестирования
                user.set_password('password123')
                
                db.session.add(user)
                users_created += 1
                logger.info(f"  ➕ Создан пользователь: {user_data['email']}")
            else:
                logger.info(f"  ⚠️  Пользователь уже существует: {user_data['email']}")
        
        db.session.commit()
        logger.info(f"✅ Создано пользователей: {users_created}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания пользователей: {e}")
        db.session.rollback()
        return False

def create_sample_assessment_attempt():
    """Создание примера прохождения оценки"""
    logger.info("📝 Создание примера оценки...")
    
    try:
        test_user = User.query.filter_by(username='test_student').first()
        if not test_user:
            logger.warning("  ⚠️  Тестовый пользователь не найден, пропускаем создание примера")
            return True
        
        # Проверяем, есть ли уже попытки
        existing_attempt = PreAssessmentAttempt.query.filter_by(user_id=test_user.id).first()
        if existing_attempt:
            logger.info("  ⚠️  Пример уже существует")
            return True
        
        # Создаем попытку
        attempt = PreAssessmentAttempt(
            user_id=test_user.id,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            total_questions=10,  # Упрощенный пример
            correct_answers=7,
            total_score=70.0,
            time_spent=1800,  # 30 минут
            is_completed=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(attempt)
        db.session.flush()
        
        # Создаем примеры ответов
        questions = AssessmentQuestion.query.filter_by(is_active=True).limit(10).all()
        
        for i, question in enumerate(questions):
            is_correct = i < 7  # Первые 7 правильные
            user_answer = question.correct_answer if is_correct else (question.correct_answer + 1) % 4
            
            answer = PreAssessmentAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                user_answer=user_answer,
                is_correct=is_correct,
                points_earned=1.0 if is_correct else 0.0,
                time_spent=180,  # 3 минуты на вопрос
                answered_at=datetime.utcnow()
            )
            
            db.session.add(answer)
        
        # Устанавливаем результаты по категориям
        category_scores = {
            "1": {"score": 80.0, "correct": 4, "total": 5},
            "2": {"score": 60.0, "correct": 3, "total": 5}
        }
        attempt.set_category_scores(category_scores)
        
        db.session.commit()
        logger.info("✅ Пример оценки создан успешно")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания примера оценки: {e}")
        db.session.rollback()
        return False

def generate_statistics():
    """Генерация статистики системы"""
    logger.info("📈 Генерация статистики...")
    
    try:
        stats = {
            'categories': AssessmentCategory.query.count(),
            'questions': AssessmentQuestion.query.filter_by(is_active=True).count(),
            'users': User.query.count(),
            'attempts': PreAssessmentAttempt.query.count(),
            'completed_attempts': PreAssessmentAttempt.query.filter_by(is_completed=True).count()
        }
        
        logger.info("📊 Статистика системы:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        return stats
    except Exception as e:
        logger.error(f"❌ Ошибка генерации статистики: {e}")
        return None

def backup_database():
    """Создание резервной копии базы данных"""
    import shutil
    
    try:
        db_path = Path('dental_academy.db')
        if not db_path.exists():
            logger.warning("  ⚠️  Файл базы данных не найден, пропускаем резервное копирование")
            return None
        
        backup_path = db_path.parent / f'dental_academy_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        shutil.copy2(db_path, backup_path)
        logger.info(f"✅ Резервная копия создана: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"❌ Ошибка создания резервной копии: {e}")
        return None

def initialize_assessment_system():
    """Главная функция инициализации системы оценивания"""
    logger.info("🚀 Инициализация системы предварительной оценки знаний")
    logger.info("=" * 60)
    
    # Создаем резервную копию
    backup_database()
    
    try:
        # 1. Создание таблиц
        if not init_assessment_tables():
            return False
        
        # 2. Заполнение категорий
        if not populate_assessment_categories():
            return False
        
        # 3. Заполнение вопросов
        if not populate_assessment_questions():
            return False
        
        # 4. Валидация данных
        if not validate_assessment_data():
            logger.error("❌ Валидация не пройдена. Исправьте ошибки.")
            return False
        
        # 5. Создание тестовых пользователей
        if not create_sample_users():
            return False
        
        # 6. Создание примера оценки
        if not create_sample_assessment_attempt():
            return False
        
        # 7. Генерация статистики
        generate_statistics()
        
        logger.info("=" * 60)
        logger.info("🎉 Инициализация завершена успешно!")
        logger.info("\n📌 Следующие шаги:")
        logger.info("1. Запустите приложение: python app.py")
        logger.info("2. Перейдите в раздел /assessment/")
        logger.info("3. Войдите как test_student@dentalacademy.test (пароль: password123)")
        logger.info("4. Пройдите предварительную оценку")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при инициализации: {e}")
        db.session.rollback()
        return False

def run_validation():
    """Запуск валидации системы оценивания"""
    logger.info("🔍 Запуск валидации системы оценивания...")
    
    try:
        validation_results = {
            'database_structure': validate_database_structure(),
            'question_quality': validate_question_quality(),
            'category_balance': validate_category_balance(),
            'user_flow': validate_user_flow()
        }
        
        logger.info("\n📊 Результаты валидации:")
        for category, result in validation_results.items():
            status = "✅" if result['passed'] else "❌"
            logger.info(f"  {status} {category}: {result['message']}")
        
        return all(result['passed'] for result in validation_results.values())
    except Exception as e:
        logger.error(f"❌ Ошибка валидации: {e}")
        return False

def validate_database_structure():
    """Валидация структуры базы данных"""
    try:
        # Проверяем наличие всех необходимых таблиц
        required_tables = [
            'assessment_categories',
            'assessment_questions', 
            'pre_assessment_attempts',
            'pre_assessment_answers',
            'learning_plans'
        ]
        
        for table in required_tables:
            # Простая проверка через выполнение запроса
            db.session.execute(f"SELECT 1 FROM {table} LIMIT 1")
        
        return {'passed': True, 'message': 'Структура БД корректна'}
    except Exception as e:
        return {'passed': False, 'message': f'Ошибка структуры БД: {e}'}

def validate_question_quality():
    """Валидация качества вопросов"""
    try:
        questions = AssessmentQuestion.query.filter_by(is_active=True).all()
        
        if len(questions) < 10:
            return {'passed': False, 'message': f'Недостаточно вопросов: {len(questions)}'}
        
        problematic_questions = 0
        
        for question in questions:
            options = question.get_options()
            
            # Проверки качества
            if len(options) < 3:
                problematic_questions += 1
            elif question.correct_answer >= len(options):
                problematic_questions += 1
            elif len(question.explanation) < 20:
                problematic_questions += 1
        
        if problematic_questions > len(questions) * 0.1:  # Более 10% проблемных
            return {'passed': False, 'message': f'Много проблемных вопросов: {problematic_questions}'}
        
        return {'passed': True, 'message': f'Качество вопросов удовлетворительное'}
    except Exception as e:
        return {'passed': False, 'message': f'Ошибка валидации вопросов: {e}'}

def validate_category_balance():
    """Валидация баланса категорий"""
    try:
        categories = AssessmentCategory.query.all()
        
        if len(categories) < 3:
            return {'passed': False, 'message': 'Недостаточно категорий'}
        
        # Проверяем распределение вопросов
        unbalanced_categories = 0
        
        for category in categories:
            questions_count = AssessmentQuestion.query.filter_by(
                category_id=category.id,
                is_active=True
            ).count()
            
            if questions_count < category.min_questions:
                unbalanced_categories += 1
        
        if unbalanced_categories > 0:
            return {'passed': False, 'message': f'Несбалансированных категорий: {unbalanced_categories}'}
        
        return {'passed': True, 'message': 'Баланс категорий корректен'}
    except Exception as e:
        return {'passed': False, 'message': f'Ошибка валидации баланса: {e}'}

def validate_user_flow():
    """Валидация пользовательского потока"""
    try:
        # Проверяем наличие тестового пользователя
        test_user = User.query.filter_by(username='test_student').first()
        
        if not test_user:
            return {'passed': False, 'message': 'Тестовый пользователь не найден'}
        
        # Проверяем возможность создания попытки оценки
        attempt = PreAssessmentAttempt(
            user_id=test_user.id,
            started_at=datetime.utcnow(),
            total_questions=5
        )
        
        db.session.add(attempt)
        db.session.flush()
        db.session.rollback()  # Откатываем тестовые изменения
        
        return {'passed': True, 'message': 'Пользовательский поток корректен'}
    except Exception as e:
        return {'passed': False, 'message': f'Ошибка валидации потока: {e}'}

def main():
    """Главная функция для запуска из командной строки"""
    app_context = create_app_context()
    if not app_context:
        return False
    
    with app_context:
        return initialize_assessment_system()

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Скрипт выполнен успешно")
        sys.exit(0)
    else:
        logger.error("❌ Скрипт завершился с ошибками")
        sys.exit(1) 