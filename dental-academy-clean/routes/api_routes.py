#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Routes for Daily Learning Plan Progress Tracking
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from models import db, UserProgress, SpacedRepetitionItem
from utils.simple_spaced_repetition import SimpleSpacedRepetition

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/progress/update', methods=['POST'])
@login_required
def update_progress():
    """Обновление прогресса пользователя"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        time_spent = data.get('time_spent', 0)
        completed = data.get('completed', False)
        was_correct = data.get('correct')
        is_review = data.get('is_review', False)
        
        if not content_id or not content_type:
            return jsonify({'error': 'content_id and content_type are required'}), 400
        
        # Update UserProgress
        if content_type == 'lesson':
            # Для уроков используем lesson_id
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=content_id
            ).first()
            
            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=content_id
                )
                db.session.add(progress)
        else:
            # Для других типов контента создаем запись в UserProgress
            # или используем существующую логику
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=content_id  # Временно используем lesson_id
            ).first()
            
            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=content_id
                )
                db.session.add(progress)
        
        # Обновляем прогресс
        progress.completed = completed
        progress.time_spent = (progress.time_spent or 0) + time_spent
        progress.last_accessed = datetime.now(timezone.utc)
        
        if was_correct is not None:
            progress.score = 1.0 if was_correct else 0.0
        
        # ✅ FIX: Update daily activity, streak, XP when lesson is completed
        if completed and content_type == 'lesson' and not progress.completed:
            xp_earned = 10
            current_user.update_daily_activity(
                lessons_completed=1,
                time_spent=time_spent,
                xp_earned=xp_earned
            )
        
        # Handle spaced repetition for questions
        if content_type == 'question' and is_review and was_correct is not None:
            try:
                sr_system = SimpleSpacedRepetition()
                # Конвертируем boolean в quality (0-5)
                quality = 5 if was_correct else 0
                sr_system.calculate_next_review(
                    user_id=current_user.id,
                    question_id=content_id,
                    quality=quality
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error updating spaced repetition: {e}")
        
        db.session.commit()
        
        # ✅ Clear cache after progress update
        from utils.diagnostic_data_manager import clear_cache
        clear_cache(current_user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'Progress updated successfully',
            'content_id': content_id,
            'content_type': content_type,
            'time_spent': time_spent,
            'completed': completed
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating progress: {str(e)}'}), 500

@api_bp.route('/daily-plan/progress')
@login_required
def get_daily_progress():
    """Получение прогресса ежедневного плана"""
    try:
        from utils.daily_learning_algorithm import DailyLearningAlgorithm
        
        algorithm = DailyLearningAlgorithm()
        today_plan = algorithm.generate_daily_plan(current_user.id)
        
        if not today_plan.get('success'):
            return jsonify({'error': 'Failed to generate daily plan'}), 500
        
        # Calculate completion
        daily_plan = today_plan.get('daily_plan', {})
        theory_items = daily_plan.get('theory_section', {}).get('items', [])
        practice_items = daily_plan.get('practice_section', {}).get('items', [])
        review_items = daily_plan.get('review_section', {}).get('items', [])
        
        total_items = len(theory_items) + len(practice_items) + len(review_items)
        
        # Get completed items for today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = UserProgress.query.filter(
            UserProgress.user_id == current_user.id,
            UserProgress.completed == True,
            UserProgress.last_accessed >= today_start
        ).all()
        
        completed_item_ids = [p.lesson_id for p in completed_today]
        completion_percentage = int((len(completed_item_ids) / max(total_items, 1)) * 100)
        
        return jsonify({
            'completion_percentage': completion_percentage,
            'completed_items': completed_item_ids,
            'total_items': total_items,
            'completed_today': len(completed_item_ids),
            'theory_items': len(theory_items),
            'practice_items': len(practice_items),
            'review_items': len(review_items)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting daily progress: {str(e)}'}), 500

@api_bp.route('/daily-plan/regenerate', methods=['POST'])
@login_required
def regenerate_daily_plan():
    """Перегенерация ежедневного плана с новыми параметрами"""
    try:
        data = request.get_json() or {}
        target_minutes = data.get('target_minutes', 30)
        
        from utils.daily_learning_algorithm import DailyLearningAlgorithm
        algorithm = DailyLearningAlgorithm()
        new_plan = algorithm.generate_daily_plan(current_user.id, target_minutes)
        
        return jsonify(new_plan)
        
    except Exception as e:
        return jsonify({'error': f'Error regenerating daily plan: {str(e)}'}), 500

@api_bp.route('/spaced-repetition/overdue')
@login_required
def get_overdue_reviews():
    """Получение просроченных повторений"""
    try:
        overdue_items = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == current_user.id,
            SpacedRepetitionItem.is_active == True,
            SpacedRepetitionItem.next_review < datetime.now(timezone.utc)
        ).all()
        
        overdue_data = []
        for item in overdue_items:
            overdue_data.append({
                'id': item.id,
                'question_id': item.question_id,
                'domain': item.domain,
                'overdue_days': (datetime.now(timezone.utc) - item.next_review).days,
                'ease_factor': item.ease_factor,
                'repetitions': item.repetitions,
                'next_review': item.next_review.isoformat() if item.next_review else None
            })
        
        return jsonify({
            'overdue_count': len(overdue_data),
            'overdue_items': overdue_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting overdue reviews: {str(e)}'}), 500

@api_bp.route('/user/stats')
@login_required
def get_user_stats():
    """Получение статистики пользователя"""
    try:
        # Get user progress stats
        total_lessons = UserProgress.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).count()
        
        # Get spaced repetition stats
        total_sr_items = SpacedRepetitionItem.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).count()
        
        # Get today's activity
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_lessons = UserProgress.query.filter(
            UserProgress.user_id == current_user.id,
            UserProgress.completed == True,
            UserProgress.last_accessed >= today_start
        ).count()
        
        return jsonify({
            'total_lessons_completed': total_lessons,
            'total_sr_items': total_sr_items,
            'today_lessons_completed': today_lessons,
            'user_id': current_user.id,
            'username': current_user.username or current_user.email
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting user stats: {str(e)}'}), 500 