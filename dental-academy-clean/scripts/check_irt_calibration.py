import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import IRTParameters, Question

def check_calibration():
    with app.app_context():
        total_questions = Question.query.count()
        total_irt = IRTParameters.query.count()
        
        # Проверяем дефолтные параметры
        default_params = IRTParameters.query.filter(
            IRTParameters.difficulty == 0.0,
            IRTParameters.discrimination == 1.0,
            IRTParameters.guessing == 0.25
        ).count()
        
        # Проверяем откалиброванные
        calibrated = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size > 0
        ).count()
        
        # Статистика по difficulty
        difficulty_stats = db.session.query(
            db.func.min(IRTParameters.difficulty).label('min'),
            db.func.max(IRTParameters.difficulty).label('max'),
            db.func.avg(IRTParameters.difficulty).label('avg')
        ).first()
        
        # Статистика по discrimination
        discrimination_stats = db.session.query(
            db.func.min(IRTParameters.discrimination).label('min'),
            db.func.max(IRTParameters.discrimination).label('max'),
            db.func.avg(IRTParameters.discrimination).label('avg')
        ).first()
        
        # Статистика по guessing
        guessing_stats = db.session.query(
            db.func.min(IRTParameters.guessing).label('min'),
            db.func.max(IRTParameters.guessing).label('max'),
            db.func.avg(IRTParameters.guessing).label('avg')
        ).first()
        
        print("📊 РЕЗУЛЬТАТЫ КАЛИБРОВКИ IRT:")
        print("=" * 50)
        print(f"   Всего вопросов: {total_questions}")
        print(f"   С IRT параметрами: {total_irt} ({total_irt/total_questions*100:.1f}%)")
        print(f"   Дефолтные параметры: {default_params}")
        print(f"   Откалиброванные: {calibrated}")
        
        print(f"\n📈 Диапазон сложности (difficulty):")
        print(f"   Мин: {difficulty_stats.min:.2f}")
        print(f"   Макс: {difficulty_stats.max:.2f}")
        print(f"   Средняя: {difficulty_stats.avg:.2f}")
        
        print(f"\n📈 Диапазон дискриминации (discrimination):")
        print(f"   Мин: {discrimination_stats.min:.2f}")
        print(f"   Макс: {discrimination_stats.max:.2f}")
        print(f"   Средняя: {discrimination_stats.avg:.2f}")
        
        print(f"\n📈 Диапазон угадывания (guessing):")
        print(f"   Мин: {guessing_stats.min:.2f}")
        print(f"   Макс: {guessing_stats.max:.2f}")
        print(f"   Средняя: {guessing_stats.avg:.2f}")
        
        # Распределение по диапазонам сложности
        ranges = [
            ('Очень легкие', -3.0, -1.5),
            ('Легкие', -1.5, -0.5),
            ('Средние', -0.5, 0.5),
            ('Сложные', 0.5, 1.5),
            ('Очень сложные', 1.5, 3.0)
        ]
        
        print(f"\n📊 Распределение сложности:")
        for name, min_val, max_val in ranges:
            count = IRTParameters.query.filter(
                IRTParameters.difficulty >= min_val,
                IRTParameters.difficulty < max_val
            ).count()
            percentage = (count / total_irt * 100) if total_irt > 0 else 0
            print(f"   {name}: {count} ({percentage:.1f}%)")
        
        # Проверяем качество калибровки
        print(f"\n🔍 КАЧЕСТВО КАЛИБРОВКИ:")
        
        # Вопросы с очень маленькой выборкой
        small_sample = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size < 5
        ).count()
        print(f"   Вопросы с выборкой < 5: {small_sample}")
        
        # Вопросы с хорошей выборкой
        good_sample = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size >= 10
        ).count()
        print(f"   Вопросы с выборкой >= 10: {good_sample}")
        
        # Вопросы с отличной выборкой
        excellent_sample = IRTParameters.query.filter(
            IRTParameters.calibration_sample_size >= 20
        ).count()
        print(f"   Вопросы с выборкой >= 20: {excellent_sample}")
        
        # Проверяем надежность параметров
        high_reliability = IRTParameters.query.filter(
            IRTParameters.reliability >= 0.8
        ).count()
        print(f"   Вопросы с надежностью >= 0.8: {high_reliability}")
        
        if default_params == 0:
            print(f"\n✅ Все параметры откалиброваны!")
        else:
            print(f"\n⚠️ Осталось {default_params} вопросов с дефолтными параметрами")
        
        # Общая оценка
        coverage = (total_irt / total_questions * 100) if total_questions > 0 else 0
        calibration_quality = (calibrated / total_irt * 100) if total_irt > 0 else 0
        
        print(f"\n🎯 ОБЩАЯ ОЦЕНКА:")
        print(f"   Покрытие IRT параметрами: {coverage:.1f}%")
        print(f"   Качество калибровки: {calibration_quality:.1f}%")
        
        if coverage >= 95 and calibration_quality >= 80:
            print(f"   🎉 Отличное качество калибровки!")
        elif coverage >= 80 and calibration_quality >= 60:
            print(f"   ✅ Хорошее качество калибровки")
        else:
            print(f"   ⚠️ Требуется доработка калибровки")

if __name__ == '__main__':
    check_calibration() 