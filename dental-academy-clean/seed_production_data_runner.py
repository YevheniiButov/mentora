#!/usr/bin/env python3
"""
Скрипт для запуска загрузки данных в продакшене
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

# Устанавливаем переменную окружения для продакшена
os.environ['FLASK_ENV'] = 'production'

def run_seed_production_data():
    """Запускает загрузку данных для продакшена"""
    try:
        print("🚀 Запускаем загрузку данных для продакшена...")
        
        # Импортируем и запускаем скрипт загрузки
        from scripts.seed_production_data import main
        
        main()
        
        print("✅ Загрузка данных завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке данных: {e}")
        raise

def check_data_status():
    """Проверяет статус данных в базе"""
    try:
        from app import app
        from models import Question, BIGDomain, LearningPath, Subject, Module, Lesson
        
        with app.app_context():
            print("🔍 Проверяем статус данных в базе...")
            
            questions_count = Question.query.count()
            domains_count = BIGDomain.query.count()
            paths_count = LearningPath.query.count()
            subjects_count = Subject.query.count()
            modules_count = Module.query.count()
            lessons_count = Lesson.query.count()
            
            print(f"📊 Статистика базы данных:")
            print(f"   - Вопросов: {questions_count}")
            print(f"   - Доменов: {domains_count}")
            print(f"   - Путей обучения: {paths_count}")
            print(f"   - Предметов: {subjects_count}")
            print(f"   - Модулей: {modules_count}")
            print(f"   - Уроков: {lessons_count}")
            
            if questions_count == 0:
                print("⚠️ Вопросы не найдены! Нужно запустить загрузку данных.")
                return False
            else:
                print("✅ Данные загружены корректно.")
                return True
                
    except Exception as e:
        print(f"❌ Ошибка при проверке данных: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Скрипт загрузки данных для продакшена")
    print("=" * 50)
    
    # Сначала проверяем текущий статус
    data_ok = check_data_status()
    
    if not data_ok:
        print("\n🔧 Данные отсутствуют. Запускаем загрузку...")
        run_seed_production_data()
        
        # Проверяем результат
        print("\n🔍 Проверяем результат загрузки...")
        check_data_status()
    else:
        print("\n✅ Данные уже загружены. Дополнительная загрузка не требуется.")
    
    print("\n✅ Скрипт завершен") 