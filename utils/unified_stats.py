"""
Единая система статистики для всего приложения
Унифицирует расчет и отображение статистики на всех страницах
"""

from flask import current_app
from flask_login import current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from models import db, UserProgress, Lesson, Module, Subject, LearningPath, UserStats
import logging

# Кэш для статистики
_stats_cache = {}

def clear_stats_cache(user_id=None):
    """Очищает кэш статистики"""
    global _stats_cache
    if user_id is None:
        _stats_cache.clear()
    else:
        _stats_cache.pop(user_id, None)

def get_unified_user_stats(user_id):
    """
    Единая функция получения статистики пользователя
    Используется на всех страницах приложения
    """
    # Проверяем кэш
    if user_id in _stats_cache:
        return _stats_cache[user_id]
    
    try:
        current_app.logger.info(f"=== Получение унифицированной статистики для пользователя {user_id} ===")
        
        # 1. Общее количество завершенных уроков
        completed_lessons_count = UserProgress.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        # 2. Общее количество уроков
        total_lessons_count = Lesson.query.count()
        
        # 3. Расчет общего прогресса
        overall_progress = round((completed_lessons_count / total_lessons_count) * 100) if total_lessons_count > 0 else 0
        
        # 4. Общее время обучения (в минутах)
        total_time_spent = db.session.query(
            func.sum(UserProgress.time_spent)
        ).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # 5. Количество дней активности
        active_days_count = db.session.query(
            func.count(func.distinct(func.date(UserProgress.last_accessed)))
        ).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # 6. Статистика по путям обучения
        learning_paths_stats = []
        for path in LearningPath.query.all():
            # Получаем все уроки для данного пути обучения
            path_lessons = db.session.query(Lesson.id).join(
                Module, Module.id == Lesson.module_id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                Subject.learning_path_id == path.id
            ).all()
            
            path_lesson_ids = [lesson[0] for lesson in path_lessons]
            path_total_lessons = len(path_lesson_ids)
            
            # Количество завершенных уроков для этого пути
            path_completed_lessons = UserProgress.query.filter(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id.in_(path_lesson_ids),
                UserProgress.completed == True
            ).count() if path_lesson_ids else 0
            
            # Расчет прогресса для данного пути
            path_progress = round((path_completed_lessons / path_total_lessons) * 100) if path_total_lessons > 0 else 0
            
            learning_paths_stats.append({
                'id': path.id,
                'name': path.name,
                'progress': path_progress,
                'completed_lessons': path_completed_lessons,
                'total_lessons': path_total_lessons
            })
        
        # 7. Дополнительная статистика
        # Последняя активность
        last_activity = db.session.query(
            func.max(UserProgress.last_accessed)
        ).filter_by(
            user_id=user_id
        ).scalar()
        
        # Сегодняшняя активность
        today = datetime.now().date()
        today_lessons = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            func.date(UserProgress.last_accessed) == today
        ).count()
        
        # Недельная активность
        week_ago = today - timedelta(days=7)
        weekly_lessons = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed >= week_ago
        ).count()
        
        # Формируем итоговую статистику
        stats = {
            'overall_progress': overall_progress,
            'completed_lessons': completed_lessons_count,
            'total_lessons': total_lessons_count,
            'total_time_spent': round(float(total_time_spent), 1),
            'active_days': active_days_count,
            'learning_paths': learning_paths_stats,
            'last_activity': last_activity.isoformat() if last_activity else None,
            'today_lessons': today_lessons,
            'weekly_lessons': weekly_lessons,
            'level': min(completed_lessons_count // 10 + 1, 10),
            'experience_points': completed_lessons_count * 10,
            'next_level_progress': (completed_lessons_count % 10) * 10
        }
        
        current_app.logger.info(f"=== Унифицированная статистика получена: {stats} ===")
        
        # Сохраняем в кэш
        _stats_cache[user_id] = stats
        
        return stats
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_unified_user_stats: {str(e)}", exc_info=True)
        return {
            'overall_progress': 0,
            'completed_lessons': 0,
            'total_lessons': 0,
            'total_time_spent': 0,
            'active_days': 0,
            'learning_paths': [],
            'last_activity': None,
            'today_lessons': 0,
            'weekly_lessons': 0,
            'level': 1,
            'experience_points': 0,
            'next_level_progress': 0
        }

def track_lesson_progress(user_id, lesson_id, time_spent=None, completed=False):
    """
    Унифицированная функция отслеживания прогресса урока
    Вызывается при завершении урока
    """
    print(f"🔥 ВЫЗВАНА track_lesson_progress: user={user_id}, lesson={lesson_id}, time_spent={time_spent}, completed={completed}")
    current_app.logger.info(f"🔥 ВЫЗВАНА track_lesson_progress: user={user_id}, lesson={lesson_id}, time_spent={time_spent}, completed={completed}")
    
    try:
        # Найти существующую запись прогресса или создать новую
        progress = UserProgress.query.filter_by(
            user_id=user_id, 
            lesson_id=lesson_id
        ).first()
        
        print(f"🔍 Поиск существующего прогресса: {progress}")
        
        if not progress:
            print(f"📝 Создаем новую запись прогресса для урока {lesson_id}")
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                completed=False,
                time_spent=0
            )
            db.session.add(progress)
        else:
            print(f"📝 Обновляем существующую запись прогресса: {progress}")
        
        # Обновляем время последнего доступа
        progress.last_accessed = datetime.utcnow()
        print(f"⏰ Обновлено last_accessed: {progress.last_accessed}")
        
        # Обновляем время, если оно предоставлено
        if time_spent is not None:
            old_time = progress.time_spent or 0
            progress.time_spent = old_time + float(time_spent)
            print(f"⏱️ Обновлено time_spent: {old_time} -> {progress.time_spent}")
        
        # Если урок должен быть отмечен как завершенный
        if completed:
            old_completed = progress.completed
            progress.completed = True
            print(f"✅ Отмечен как завершенный: {old_completed} -> {progress.completed}")
        
        # Сохраняем изменения
        print(f"💾 Сохраняем в БД...")
        db.session.commit()
        print(f"✅ Прогресс сохранен в БД для урока {lesson_id}")
        current_app.logger.info(f"✅ Прогресс сохранен в БД для урока {lesson_id}")
        
        # Очищаем кэш статистики пользователя
        clear_stats_cache(user_id)
        print(f"🗑️ Кэш статистики очищен для пользователя {user_id}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ОШИБКА сохранения прогресса: {e}")
        current_app.logger.error(f"❌ ОШИБКА в track_lesson_progress: {str(e)}", exc_info=True)
        return False

def get_module_stats_unified(module_id, user_id):
    """
    Унифицированная функция получения статистики модуля
    """
    try:
        # Получаем все уроки в модуле
        lessons = Lesson.query.filter_by(module_id=module_id).with_entities(Lesson.id).all()
        lesson_ids = [lesson.id for lesson in lessons]
        total_lessons = len(lesson_ids)
        
        if total_lessons == 0:
            return {
                "progress": 0,
                "completed_lessons": 0,
                "total_lessons": 0
            }
        
        # Получаем количество завершенных уроков за один запрос
        completed_lessons = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        ).count()
        
        # Рассчитываем прогресс
        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        return {
            "progress": round(progress),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        }
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_module_stats_unified: {str(e)}", exc_info=True)
        return {
            "progress": 0,
            "completed_lessons": 0,
            "total_lessons": 0
        }

def get_subject_stats_unified(subject_id, user_id):
    """
    Унифицированная функция получения статистики предмета
    """
    try:
        # Получаем все уроки для данного предмета через JOIN
        subject_lessons = db.session.query(Lesson.id).join(
            Module, Module.id == Lesson.module_id
        ).filter(
            Module.subject_id == subject_id
        ).all()
        
        # Преобразуем результат в список ID уроков
        lesson_ids = [lesson[0] for lesson in subject_lessons]
        total_lessons = len(lesson_ids)
        
        if total_lessons == 0:
            return 0
        
        # Получаем все завершенные уроки за один запрос
        completed_lessons_count = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        ).count()
        
        # Расчет прогресса для данного предмета
        return round((completed_lessons_count / total_lessons) * 100) if total_lessons > 0 else 0
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_subject_stats_unified: {str(e)}", exc_info=True)
        return 0

# Экспортируем функции для использования в других модулях
__all__ = [
    'get_unified_user_stats',
    'track_lesson_progress', 
    'get_module_stats_unified',
    'get_subject_stats_unified',
    'clear_stats_cache'
] 