#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler Routes for Diagnostic Reassessment Reminders
API маршруты для планировщика напоминаний о переоценке
"""

import logging
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_

from models import User, PersonalLearningPlan, DiagnosticSession
from extensions import db
from utils.scheduler_service import diagnostic_scheduler
from utils.decorators import admin_required, rate_limit

logger = logging.getLogger(__name__)

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')

@scheduler_bp.route('/check-reminders', methods=['POST'])
@admin_required
@rate_limit(requests_per_minute=10)
def check_diagnostic_reminders():
    """
    Manually trigger diagnostic reminder check
    Ручной запуск проверки напоминаний о диагностике
    """
    try:
        logger.info(f"Manual reminder check triggered by admin {current_user.id}")
        
        # Run reminder check
        stats = diagnostic_scheduler.check_diagnostic_reminders()
        
        return jsonify({
            'success': True,
            'message': 'Reminder check completed successfully',
            'stats': stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in manual reminder check: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to check reminders: {str(e)}'
        }), 500

@scheduler_bp.route('/stats', methods=['GET'])
@admin_required
def get_scheduler_stats():
    """
    Get scheduler statistics
    Получить статистику планировщика
    """
    try:
        stats = diagnostic_scheduler.get_scheduler_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scheduler stats: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        }), 500

@scheduler_bp.route('/upcoming-diagnostics', methods=['GET'])
@admin_required
def get_upcoming_diagnostics():
    """
    Get list of upcoming diagnostic dates
    Получить список предстоящих диагностик
    """
    try:
        # Get parameters
        days_ahead = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Calculate date range
        today = datetime.now(timezone.utc).date()
        end_date = today + timedelta(days=days_ahead)
        
        # Get plans with upcoming diagnostics
        plans = PersonalLearningPlan.query.filter(
            and_(
                PersonalLearningPlan.status == 'active',
                PersonalLearningPlan.next_diagnostic_date.isnot(None),
                PersonalLearningPlan.next_diagnostic_date >= today,
                PersonalLearningPlan.next_diagnostic_date <= end_date
            )
        ).order_by(PersonalLearningPlan.next_diagnostic_date).limit(limit).all()
        
        # Prepare response data
        upcoming_diagnostics = []
        for plan in plans:
            user = User.query.get(plan.user_id)
            if user:
                days_until = (plan.next_diagnostic_date - today).days
                
                upcoming_diagnostics.append({
                    'plan_id': plan.id,
                    'user_id': user.id,
                    'user_name': user.get_display_name(),
                    'user_email': user.email,
                    'diagnostic_date': plan.next_diagnostic_date.isoformat(),
                    'days_until': days_until,
                    'progress_percentage': plan.overall_progress or 0.0,
                    'current_ability': plan.current_ability or 0.0,
                    'target_ability': plan.target_ability or 0.5,
                    'weak_domains': plan.get_weak_domains() or [],
                    'reminder_sent': getattr(plan, 'diagnostic_reminder_sent', False),
                    'last_reminder_date': getattr(plan, 'last_reminder_date', None)
                })
        
        return jsonify({
            'success': True,
            'upcoming_diagnostics': upcoming_diagnostics,
            'total_count': len(upcoming_diagnostics),
            'date_range': {
                'from': today.isoformat(),
                'to': end_date.isoformat(),
                'days_ahead': days_ahead
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting upcoming diagnostics: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get upcoming diagnostics: {str(e)}'
        }), 500

@scheduler_bp.route('/overdue-diagnostics', methods=['GET'])
@admin_required
def get_overdue_diagnostics():
    """
    Get list of overdue diagnostic dates
    Получить список просроченных диагностик
    """
    try:
        # Get parameters
        days_overdue = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Calculate date range
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=days_overdue)
        
        # Get plans with overdue diagnostics
        plans = PersonalLearningPlan.query.filter(
            and_(
                PersonalLearningPlan.status == 'active',
                PersonalLearningPlan.next_diagnostic_date.isnot(None),
                PersonalLearningPlan.next_diagnostic_date < today,
                PersonalLearningPlan.next_diagnostic_date >= start_date
            )
        ).order_by(PersonalLearningPlan.next_diagnostic_date.desc()).limit(limit).all()
        
        # Prepare response data
        overdue_diagnostics = []
        for plan in plans:
            user = User.query.get(plan.user_id)
            if user:
                days_overdue_count = (today - plan.next_diagnostic_date).days
                
                overdue_diagnostics.append({
                    'plan_id': plan.id,
                    'user_id': user.id,
                    'user_name': user.get_display_name(),
                    'user_email': user.email,
                    'diagnostic_date': plan.next_diagnostic_date.isoformat(),
                    'days_overdue': days_overdue_count,
                    'progress_percentage': plan.overall_progress or 0.0,
                    'current_ability': plan.current_ability or 0.0,
                    'target_ability': plan.target_ability or 0.5,
                    'weak_domains': plan.get_weak_domains() or [],
                    'reminder_sent': getattr(plan, 'diagnostic_reminder_sent', False),
                    'last_reminder_date': getattr(plan, 'last_reminder_date', None)
                })
        
        return jsonify({
            'success': True,
            'overdue_diagnostics': overdue_diagnostics,
            'total_count': len(overdue_diagnostics),
            'date_range': {
                'from': start_date.isoformat(),
                'to': today.isoformat(),
                'days_overdue': days_overdue
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting overdue diagnostics: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get overdue diagnostics: {str(e)}'
        }), 500

@scheduler_bp.route('/send-test-reminder', methods=['POST'])
@admin_required
def send_test_reminder():
    """
    Send test reminder to specific user
    Отправить тестовое напоминание конкретному пользователю
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        reminder_type = data.get('reminder_type', 'first')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Get user's active plan
        plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'No active learning plan found for user'
            }), 404
        
        # Send test reminder
        success = diagnostic_scheduler._send_diagnostic_reminder(plan, reminder_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test reminder sent successfully (type: {reminder_type})',
                'user_id': user_id,
                'plan_id': plan.id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send test reminder'
            }), 500
        
    except Exception as e:
        logger.error(f"Error sending test reminder: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to send test reminder: {str(e)}'
        }), 500

@scheduler_bp.route('/update-reminder-intervals', methods=['POST'])
@admin_required
def update_reminder_intervals():
    """
    Update reminder intervals configuration
    Обновить конфигурацию интервалов напоминаний
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['first_reminder', 'second_reminder', 'final_reminder']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Update intervals
        diagnostic_scheduler.reminder_intervals = {
            'first_reminder': int(data['first_reminder']),
            'second_reminder': int(data['second_reminder']),
            'final_reminder': int(data['final_reminder'])
        }
        
        logger.info(f"Reminder intervals updated by admin {current_user.id}: {diagnostic_scheduler.reminder_intervals}")
        
        return jsonify({
            'success': True,
            'message': 'Reminder intervals updated successfully',
            'intervals': diagnostic_scheduler.reminder_intervals
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating reminder intervals: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to update intervals: {str(e)}'
        }), 500

@scheduler_bp.route('/user-reminder-status', methods=['GET'])
@login_required
def get_user_reminder_status():
    """
    Get current user's reminder status
    Получить статус напоминаний текущего пользователя
    """
    try:
        # Get user's active plan
        plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not plan:
            return jsonify({
                'success': True,
                'has_plan': False,
                'message': 'No active learning plan found'
            }), 200
        
        today = datetime.now(timezone.utc).date()
        days_until_diagnostic = None
        reminder_status = 'none'
        
        if plan.next_diagnostic_date:
            days_until_diagnostic = (plan.next_diagnostic_date - today).days
            
            if days_until_diagnostic < 0:
                reminder_status = 'overdue'
            elif days_until_diagnostic <= diagnostic_scheduler.reminder_intervals['final_reminder']:
                reminder_status = 'final'
            elif days_until_diagnostic <= diagnostic_scheduler.reminder_intervals['second_reminder']:
                reminder_status = 'second'
            elif days_until_diagnostic <= diagnostic_scheduler.reminder_intervals['first_reminder']:
                reminder_status = 'first'
        
        return jsonify({
            'success': True,
            'has_plan': True,
            'plan_id': plan.id,
            'next_diagnostic_date': plan.next_diagnostic_date.isoformat() if plan.next_diagnostic_date else None,
            'days_until_diagnostic': days_until_diagnostic,
            'reminder_status': reminder_status,
            'reminder_sent': getattr(plan, 'diagnostic_reminder_sent', False),
            'last_reminder_date': getattr(plan, 'last_reminder_date', None),
            'progress_percentage': plan.overall_progress or 0.0,
            'current_ability': plan.current_ability or 0.0,
            'target_ability': plan.target_ability or 0.5
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user reminder status: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get reminder status: {str(e)}'
        }), 500 