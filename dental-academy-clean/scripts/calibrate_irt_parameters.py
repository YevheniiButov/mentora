"""
Скрипт для генерации реалистичных IRT параметров на основе статистики ответов
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question, IRTParameters, TestAttempt, DiagnosticResponse
import numpy as np
from datetime import datetime, timezone

def calculate_empirical_difficulty(question_id):
    """Рассчитать эмпирическую сложность на основе процента правильных ответов"""
    # Получаем все ответы на вопрос
    total_attempts = TestAttempt.query.filter_by(question_id=question_id).count()
    correct_attempts = TestAttempt.query.filter_by(
        question_id=question_id, 
        is_correct=True
    ).count()
    
    # Добавляем ответы из диагностических сессий
    diag_total = DiagnosticResponse.query.filter_by(question_id=question_id).count()
    diag_correct = DiagnosticResponse.query.filter_by(
        question_id=question_id,
        is_correct=True
    ).count()
    
    total = total_attempts + diag_total
    correct = correct_attempts + diag_correct
    
    if total == 0:
        return None
    
    # Процент правильных ответов
    p_correct = correct / total
    
    # Преобразуем в IRT difficulty (b-параметр)
    # Используем логит преобразование
    if p_correct <= 0.05:
        difficulty = 3.0  # Очень сложный
    elif p_correct >= 0.95:
        difficulty = -3.0  # Очень легкий
    else:
        # Логит: b = -ln(p/(1-p))
        difficulty = -np.log(p_correct / (1 - p_correct))
        difficulty = np.clip(difficulty, -3.0, 3.0)
    
    return difficulty, total

def estimate_discrimination(question, sample_size):
    """Оценить дискриминацию на основе домена и типа вопроса"""
    # Базовая дискриминация
    base_discrimination = 1.0
    
    # Корректировка по домену (некоторые домены более дискриминативны)
    domain_factors = {
        'MED': 1.2,    # Медицинская этика - высокая дискриминация
        'ANAT': 0.9,   # Анатомия - средняя
        'PHARMA': 1.1, # Фармакология - выше средней
        'PATH': 1.15,  # Патология - высокая
        'THER': 1.1,   # Терапевтическая стоматология
        'SURG': 1.05,  # Хирургическая стоматология
        'ORTH': 1.0,   # Ортодонтия
        'PEDO': 0.95,  # Детская стоматология
        'PERI': 1.1,   # Пародонтология
        'ENDO': 1.15,  # Эндодонтия
        'RAD': 1.0,    # Радиология
        'PHAR': 1.1,   # Фармакология
        'COMM': 1.2,   # Коммуникация
    }
    
    if question.domain in domain_factors:
        base_discrimination *= domain_factors[question.domain]
    
    # Корректировка по типу вопроса
    if question.question_type == 'clinical_case':
        base_discrimination *= 1.1  # Клинические случаи более дискриминативны
    elif question.question_type == 'theory':
        base_discrimination *= 0.95  # Теоретические вопросы менее дискриминативны
    
    # Корректировка по уровню сложности
    if question.difficulty_level == 1:
        base_discrimination *= 0.9  # Легкие вопросы менее дискриминативны
    elif question.difficulty_level == 3:
        base_discrimination *= 1.1  # Сложные вопросы более дискриминативны
    
    # Добавляем случайную вариацию
    discrimination = base_discrimination + np.random.normal(0, 0.2)
    discrimination = np.clip(discrimination, 0.5, 2.5)
    
    return discrimination

def estimate_guessing_parameter(question):
    """Оценить параметр угадывания на основе количества вариантов ответа"""
    # Базовый параметр угадывания для 4 вариантов ответа
    base_guessing = 0.25
    
    # Корректировка по типу вопроса
    if question.question_type == 'clinical_case':
        # Клинические случаи сложнее угадать
        base_guessing *= 0.8
    elif question.question_type == 'theory':
        # Теоретические вопросы легче угадать
        base_guessing *= 1.1
    
    # Корректировка по домену
    domain_guessing_factors = {
        'ANAT': 0.9,   # Анатомия - сложнее угадать
        'PHARMA': 1.1, # Фармакология - легче угадать
        'COMM': 0.85,  # Коммуникация - сложнее угадать
    }
    
    if question.domain in domain_guessing_factors:
        base_guessing *= domain_guessing_factors[question.domain]
    
    # Добавляем небольшую случайную вариацию
    guessing = base_guessing + np.random.normal(0, 0.02)
    guessing = np.clip(guessing, 0.1, 0.4)
    
    return guessing

def calculate_reliability(sample_size, discrimination):
    """Рассчитать надежность параметра на основе размера выборки и дискриминации"""
    if sample_size == 0:
        return 0.0
    
    # Базовая надежность зависит от размера выборки
    base_reliability = min(1.0, sample_size / 100.0)
    
    # Корректировка по дискриминации
    if discrimination > 1.5:
        reliability = base_reliability * 1.1
    elif discrimination < 0.8:
        reliability = base_reliability * 0.9
    else:
        reliability = base_reliability
    
    return np.clip(reliability, 0.0, 1.0)

def calibrate_all_questions():
    """Калибровать IRT параметры для всех вопросов"""
    with app.app_context():
        questions = Question.query.all()
        calibrated_count = 0
        skipped_count = 0
        updated_count = 0
        created_count = 0
        
        print(f"Найдено {len(questions)} вопросов для калибровки")
        print("=" * 50)
        
        for i, question in enumerate(questions, 1):
            try:
                # Проверяем, есть ли уже параметры
                existing_params = IRTParameters.query.filter_by(question_id=question.id).first()
                
                # Рассчитываем эмпирическую сложность
                result = calculate_empirical_difficulty(question.id)
                
                if result is None:
                    # Нет данных - используем случайные параметры
                    difficulty = np.random.normal(0, 1)
                    difficulty = np.clip(difficulty, -2.5, 2.5)
                    sample_size = 0
                    print(f"[{i:4d}] Вопрос {question.id}: нет данных, случайные параметры")
                else:
                    difficulty, sample_size = result
                    print(f"[{i:4d}] Вопрос {question.id}: сложность={difficulty:.2f}, выборка={sample_size}")
                
                # Оцениваем дискриминацию
                discrimination = estimate_discrimination(question, sample_size)
                
                # Оцениваем параметр угадывания
                guessing = estimate_guessing_parameter(question)
                
                # Рассчитываем надежность
                reliability = calculate_reliability(sample_size, discrimination)
                
                # Рассчитываем стандартные ошибки
                if sample_size > 50:
                    se_difficulty = 0.1
                    se_discrimination = 0.15
                elif sample_size > 20:
                    se_difficulty = 0.2
                    se_discrimination = 0.25
                else:
                    se_difficulty = 0.3
                    se_discrimination = 0.4
                
                se_guessing = 0.05
                
                if existing_params:
                    # Обновляем существующие параметры
                    existing_params.difficulty = difficulty
                    existing_params.discrimination = discrimination
                    existing_params.guessing = guessing
                    existing_params.calibration_sample_size = sample_size
                    existing_params.calibration_date = datetime.now(timezone.utc)
                    existing_params.reliability = reliability
                    existing_params.se_difficulty = se_difficulty
                    existing_params.se_discrimination = se_discrimination
                    existing_params.se_guessing = se_guessing
                    updated_count += 1
                else:
                    # Создаем новые параметры
                    new_params = IRTParameters(
                        question_id=question.id,
                        difficulty=difficulty,
                        discrimination=discrimination,
                        guessing=guessing,
                        calibration_sample_size=sample_size,
                        calibration_date=datetime.now(timezone.utc),
                        reliability=reliability,
                        se_difficulty=se_difficulty,
                        se_discrimination=se_discrimination,
                        se_guessing=se_guessing
                    )
                    db.session.add(new_params)
                    created_count += 1
                
                calibrated_count += 1
                
                # Периодически сохраняем изменения
                if calibrated_count % 50 == 0:
                    db.session.commit()
                    print(f"Сохранено {calibrated_count} вопросов...")
                
            except Exception as e:
                print(f"Ошибка при калибровке вопроса {question.id}: {e}")
                skipped_count += 1
                continue
        
        # Финальное сохранение
        db.session.commit()
        
        print("=" * 50)
        print(f"Калибровка завершена!")
        print(f"Всего вопросов: {len(questions)}")
        print(f"Калибровано: {calibrated_count}")
        print(f"Создано новых: {created_count}")
        print(f"Обновлено: {updated_count}")
        print(f"Пропущено: {skipped_count}")
        
        # Статистика по сложности
        all_params = IRTParameters.query.all()
        difficulties = [p.difficulty for p in all_params]
        discriminations = [p.discrimination for p in all_params]
        
        print(f"\nСтатистика сложности:")
        print(f"Средняя сложность: {np.mean(difficulties):.2f}")
        print(f"Стандартное отклонение: {np.std(difficulties):.2f}")
        print(f"Мин/Макс: {np.min(difficulties):.2f} / {np.max(difficulties):.2f}")
        
        print(f"\nСтатистика дискриминации:")
        print(f"Средняя дискриминация: {np.mean(discriminations):.2f}")
        print(f"Стандартное отклонение: {np.std(discriminations):.2f}")
        print(f"Мин/Макс: {np.min(discriminations):.2f} / {np.max(discriminations):.2f}")

def validate_irt_parameters():
    """Проверить валидность IRT параметров"""
    with app.app_context():
        params = IRTParameters.query.all()
        invalid_count = 0
        
        print("Проверка валидности IRT параметров...")
        
        for param in params:
            is_valid = True
            issues = []
            
            # Проверяем диапазоны
            if not (-4.0 <= param.difficulty <= 4.0):
                issues.append(f"difficulty={param.difficulty:.2f} вне диапазона")
                is_valid = False
            
            if not (0.1 <= param.discrimination <= 3.0):
                issues.append(f"discrimination={param.discrimination:.2f} вне диапазона")
                is_valid = False
            
            if not (0.0 <= param.guessing <= 0.5):
                issues.append(f"guessing={param.guessing:.2f} вне диапазона")
                is_valid = False
            
            if not is_valid:
                print(f"Вопрос {param.question_id}: {', '.join(issues)}")
                invalid_count += 1
        
        print(f"Найдено {invalid_count} невалидных параметров из {len(params)}")

if __name__ == '__main__':
    print("Запуск калибровки IRT параметров...")
    calibrate_all_questions()
    print("\nПроверка валидности...")
    validate_irt_parameters() 