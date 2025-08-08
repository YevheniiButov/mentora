import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Lesson, Module, Subject
import numpy as np

def set_lesson_difficulties():
    """Установить сложность уроков на основе их позиции в модулях"""
    with app.app_context():
        # Базовая сложность по типам предметов
        subject_base_difficulty = {
            'anatomy': -0.5,      # Базовая анатомия - проще
            'physiology': 0.0,    # Физиология - средняя
            'pathology': 0.5,     # Патология - сложнее
            'pharmacology': 0.3,  # Фармакология - выше средней
            'biochemistry': 0.7,  # Биохимия - сложная
            'microbiology': 0.2,  # Микробиология - чуть выше средней
            'clinical': 0.4,      # Клинические предметы - сложные
            'preventive': -0.2,   # Профилактика - проще
            'ethics': -0.3,       # Этика - относительно простая
            'communication': -0.4, # Коммуникация - простая
        }
        
        lessons_updated = 0
        
        # Получаем все уроки с их модулями
        lessons = Lesson.query.join(Module).join(Subject).all()
        
        print(f"Найдено {len(lessons)} уроков для установки сложности")
        print("=" * 60)
        
        for i, lesson in enumerate(lessons, 1):
            module = lesson.module
            subject = module.subject
            
            # Определяем базовую сложность по типу предмета
            subject_type = 'clinical'  # по умолчанию
            subject_name_lower = subject.name.lower()
            
            for key in subject_base_difficulty:
                if key in subject_name_lower:
                    subject_type = key
                    break
            
            base_difficulty = subject_base_difficulty.get(subject_type, 0.0)
            
            # Добавляем сложность в зависимости от позиции урока в модуле
            module_lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
            lesson_position = next((i for i, l in enumerate(module_lessons) if l.id == lesson.id), 0)
            total_lessons = len(module_lessons)
            
            if total_lessons > 0:
                # Прогрессия сложности внутри модуля (от -0.3 до +0.3)
                position_factor = (lesson_position / total_lessons) * 0.6 - 0.3
            else:
                position_factor = 0.0
            
            # Добавляем сложность в зависимости от позиции модуля в предмете
            subject_modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
            module_position = next((i for i, m in enumerate(subject_modules) if m.id == module.id), 0)
            total_modules = len(subject_modules)
            
            if total_modules > 0:
                # Прогрессия сложности между модулями (от -0.2 до +0.2)
                module_factor = (module_position / total_modules) * 0.4 - 0.2
            else:
                module_factor = 0.0
            
            # Итоговая сложность
            difficulty = base_difficulty + position_factor + module_factor
            
            # Добавляем небольшую случайную вариацию
            difficulty += np.random.normal(0, 0.1)
            
            # Ограничиваем диапазон [-2.5, 2.5]
            difficulty = np.clip(difficulty, -2.5, 2.5)
            
            # Обновляем урок
            lesson.difficulty = round(difficulty, 2)
            lessons_updated += 1
            
            # Выводим информацию о первых 10 уроках для отладки
            if i <= 10:
                print(f"[{i:3d}] Урок '{lesson.title[:30]}...'")
                print(f"     Предмет: {subject.name} (тип: {subject_type})")
                print(f"     Модуль: {module.title}")
                print(f"     Позиция в модуле: {lesson_position + 1}/{total_lessons}")
                print(f"     Позиция модуля: {module_position + 1}/{total_modules}")
                print(f"     Сложность: {lesson.difficulty:.2f} (базовая: {base_difficulty:.2f}, позиция: {position_factor:.2f}, модуль: {module_factor:.2f})")
                print("-" * 40)
            
            if lessons_updated % 100 == 0:
                print(f"Обновлено {lessons_updated} уроков...")
                db.session.commit()
        
        db.session.commit()
        
        # Статистика
        print(f"\n✅ Установлена сложность для {lessons_updated} уроков")
        
        # Проверяем распределение
        difficulty_stats = db.session.query(
            db.func.min(Lesson.difficulty).label('min'),
            db.func.max(Lesson.difficulty).label('max'),
            db.func.avg(Lesson.difficulty).label('avg'),
            db.func.count(Lesson.id).label('count')
        ).first()
        
        print(f"\n📊 Статистика сложности:")
        print(f"   Минимальная: {difficulty_stats.min:.2f}")
        print(f"   Максимальная: {difficulty_stats.max:.2f}")
        print(f"   Средняя: {difficulty_stats.avg:.2f}")
        print(f"   Всего уроков: {difficulty_stats.count}")
        
        # Распределение по диапазонам
        ranges = [
            ('Очень легкие', -2.5, -1.5),
            ('Легкие', -1.5, -0.5),
            ('Средние', -0.5, 0.5),
            ('Сложные', 0.5, 1.5),
            ('Очень сложные', 1.5, 2.5)
        ]
        
        print("\n📈 Распределение:")
        for name, min_val, max_val in ranges:
            count = Lesson.query.filter(
                Lesson.difficulty >= min_val,
                Lesson.difficulty < max_val
            ).count()
            percentage = (count / difficulty_stats.count * 100) if difficulty_stats.count > 0 else 0
            print(f"   {name}: {count} ({percentage:.1f}%)")
        
        # Статистика по предметам
        print("\n📚 Сложность по предметам:")
        subjects = Subject.query.all()
        for subject in subjects:
            subject_lessons = Lesson.query.join(Module).filter(Module.subject_id == subject.id).all()
            if subject_lessons:
                avg_difficulty = sum(l.difficulty for l in subject_lessons) / len(subject_lessons)
                print(f"   {subject.name}: {avg_difficulty:.2f} ({len(subject_lessons)} уроков)")

def validate_lesson_difficulties():
    """Проверить корректность установленной сложности"""
    with app.app_context():
        print("\n🔍 ПРОВЕРКА КОРРЕКТНОСТИ СЛОЖНОСТИ")
        print("=" * 50)
        
        # Проверяем уроки без сложности
        lessons_without_difficulty = Lesson.query.filter(Lesson.difficulty.is_(None)).count()
        if lessons_without_difficulty > 0:
            print(f"⚠️ Найдено {lessons_without_difficulty} уроков без установленной сложности")
        else:
            print("✅ Все уроки имеют установленную сложность")
        
        # Проверяем диапазон значений
        lessons_out_of_range = Lesson.query.filter(
            (Lesson.difficulty < -2.5) | (Lesson.difficulty > 2.5)
        ).count()
        
        if lessons_out_of_range > 0:
            print(f"⚠️ Найдено {lessons_out_of_range} уроков со сложностью вне диапазона [-2.5, 2.5]")
        else:
            print("✅ Все уроки имеют корректный диапазон сложности")
        
        # Проверяем прогрессию в модулях
        print("\n📈 Проверка прогрессии сложности в модулях:")
        modules = Module.query.limit(5).all()  # Проверяем первые 5 модулей
        
        for module in modules:
            lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
            if len(lessons) > 1:
                difficulties = [l.difficulty for l in lessons]
                print(f"   Модуль '{module.title}': {difficulties}")
                
                # Проверяем, что сложность растет
                is_increasing = all(difficulties[i] <= difficulties[i+1] for i in range(len(difficulties)-1))
                if is_increasing:
                    print(f"     ✅ Прогрессия корректна")
                else:
                    print(f"     ⚠️ Прогрессия нарушена")

if __name__ == '__main__':
    print("🚀 Установка сложности уроков")
    print("=" * 60)
    
    set_lesson_difficulties()
    validate_lesson_difficulties()
    
    print("\n🎉 Установка сложности завершена!") 