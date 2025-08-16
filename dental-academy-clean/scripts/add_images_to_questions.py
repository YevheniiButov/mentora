#!/usr/bin/env python3
"""
Скрипт для добавления изображений к вопросам
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Question
from extensions import db

def add_images_to_questions():
    """Добавить изображения к вопросам"""
    
    print('🖼️  ДОБАВЛЕНИЕ ИЗОБРАЖЕНИЙ К ВОПРОСАМ')
    print('=' * 50)
    
    # Маппинг изображений к вопросам
    image_mapping = {
        # COMMUNICATION вопросы
        1: 'xray_healthy_teeth.jpg',  # Вопрос о коммуникации с пациентом
        2: 'xray_filling.jpg',        # Вопрос об информированном согласии
        3: 'xray_healthy_teeth.jpg',  # Вопрос о культурной чувствительности
        4: 'xray_endodontic.jpg',     # Вопрос о передаче плохих новостей
        5: 'xray_healthy_teeth.jpg',  # Вопрос о коммуникации с коллегами
        
        # PRACTICAL_SKILLS вопросы
        6: 'xray_filling.jpg',        # Интерпретация рентгенограмм
        7: 'xray_endodontic.jpg',     # Клинические техники
        8: 'xray_healthy_teeth.jpg',  # Контроль инфекции
        9: 'xray_healthy_teeth.jpg',  # Экстренные процедуры
        10: 'xray_healthy_teeth.jpg', # Практические навыки
        
        # STATISTICS вопросы
        11: 'xray_filling.jpg',       # Методология исследований
        12: 'xray_healthy_teeth.jpg', # Интерпретация данных
        13: 'xray_healthy_teeth.jpg', # Эпидемиологические концепции
        14: 'xray_healthy_teeth.jpg', # Основанная на доказательствах стоматология
        15: 'xray_healthy_teeth.jpg', # Статистическая значимость
        
        # TREATMENT_PLANNING вопросы
        16: 'xray_endodontic.jpg',    # Анализ случая и диагностика
        17: 'xray_filling.jpg',       # Последовательность лечения
        18: 'xray_healthy_teeth.jpg', # Оценка рисков
        19: 'xray_filling.jpg',       # Оценка прогноза
        20: 'xray_endodontic.jpg',    # Мультидисциплинарная помощь
    }
    
    with app.app_context():
        updated_count = 0
        
        for question_id, image_filename in image_mapping.items():
            question = Question.query.get(question_id)
            
            if question:
                old_image = question.image_url
                question.image_url = image_filename
                
                print(f'✅ Вопрос {question_id}: {old_image or "нет"} -> {image_filename}')
                updated_count += 1
            else:
                print(f'❌ Вопрос {question_id} не найден')
        
        # Сохраняем изменения
        try:
            db.session.commit()
            print(f'\n📊 РЕЗУЛЬТАТ:')
            print(f'   Обновлено вопросов: {updated_count}')
            print(f'   Изображений добавлено: {updated_count}')
            return True
            
        except Exception as e:
            print(f'❌ Ошибка при сохранении: {e}')
            db.session.rollback()
            return False

def verify_images():
    """Проверить добавленные изображения"""
    
    print('\n🔍 ПРОВЕРКА ИЗОБРАЖЕНИЙ')
    print('=' * 40)
    
    with app.app_context():
        questions_with_images = Question.query.filter(Question.image_url.isnot(None)).all()
        
        print(f'📊 Вопросов с изображениями: {len(questions_with_images)}')
        
        if questions_with_images:
            print('\n📋 СПИСОК ВОПРОСОВ С ИЗОБРАЖЕНИЯМИ:')
            for question in questions_with_images:
                print(f'   Вопрос {question.id}: {question.image_url}')
        
        # Проверяем, что изображения существуют в папке static
        static_images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images')
        
        if os.path.exists(static_images_dir):
            print(f'\n📁 Папка изображений: {static_images_dir}')
            
            # Список требуемых изображений
            required_images = ['xray_healthy_teeth.jpg', 'xray_filling.jpg', 'xray_endodontic.jpg']
            
            for image in required_images:
                image_path = os.path.join(static_images_dir, image)
                if os.path.exists(image_path):
                    print(f'   ✅ {image} - найден')
                else:
                    print(f'   ❌ {image} - НЕ НАЙДЕН')
        else:
            print(f'\n❌ Папка изображений не найдена: {static_images_dir}')

if __name__ == '__main__':
    print('🚀 Запуск добавления изображений к вопросам...')
    
    success = add_images_to_questions()
    
    if success:
        verify_images()
        print('\n✅ Добавление изображений завершено успешно!')
    else:
        print('\n❌ Добавление изображений завершилось с ошибками!')


