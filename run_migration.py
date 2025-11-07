#!/usr/bin/env python3
"""
Скрипт для миграции IRT параметров из Question в IRTParameters
"""

from app import app
from models import Question, IRTParameters
from extensions import db

def run_migration():
    """Запуск миграции IRT параметров"""
    
    print("🔄 ЗАПУСК МИГРАЦИИ IRT ПАРАМЕТРОВ")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Проверяем текущее состояние
            questions_count = Question.query.count()
            irt_count = IRTParameters.query.count()
            
            print(f"📊 Текущее состояние:")
            print(f"   Вопросов: {questions_count}")
            print(f"   IRT параметров: {irt_count}")
            
            if irt_count > 0:
                print("⚠️ IRT параметры уже существуют, пропускаем миграцию")
                return
            
            # Получаем все вопросы
            questions = Question.query.all()
            print(f"📝 Обрабатываем {len(questions)} вопросов...")
            
            # Создаем IRT параметры
            created_count = 0
            skipped_count = 0
            
            for question in questions:
                try:
                    # Проверяем, есть ли IRT параметры в Question
                    if hasattr(question, 'irt_difficulty') and question.irt_difficulty is not None:
                        # Создаем IRT параметры
                        irt_params = IRTParameters(
                            question_id=question.id,
                            difficulty=question.irt_difficulty,
                            discrimination=question.irt_discrimination,
                            guessing=question.irt_guessing
                        )
                        
                        # Валидируем параметры
                        irt_params.validate_parameters()
                        
                        db.session.add(irt_params)
                        created_count += 1
                        
                        if created_count % 50 == 0:
                            print(f"   📝 Создано {created_count} IRT параметров...")
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Ошибка при создании IRT параметров для вопроса {question.id}: {e}")
                    skipped_count += 1
                    continue
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"\n✅ МИГРАЦИЯ ЗАВЕРШЕНА:")
            print(f"   Создано IRT параметров: {created_count}")
            print(f"   Пропущено вопросов: {skipped_count}")
            
            # Проверяем результат
            final_irt_count = IRTParameters.query.count()
            print(f"   Всего IRT параметров в БД: {final_irt_count}")
            
        except Exception as e:
            print(f"❌ ОШИБКА МИГРАЦИИ: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    run_migration() 