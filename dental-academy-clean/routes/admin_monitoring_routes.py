"""
Admin monitoring routes for registration logs and system health
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import SystemEvent, db
import json
import os
from datetime import datetime, timedelta, timezone
import re

# Create blueprint for monitoring
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/admin/monitoring')

@monitoring_bp.route('/logs')
@login_required
@admin_required
def logs():
    """View registration logs"""
    try:
        log_type = request.args.get('type', 'all')  # all, errors, notifications
        search_email = request.args.get('email', '').strip()  # Search by email
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        logs_data = []
        total_logs = 0
        
        if log_type == 'all':
            logs_data, total_logs = _get_registration_logs(page, per_page, search_email)
        elif log_type == 'errors':
            logs_data, total_logs = _get_error_logs(page, per_page, search_email)
        elif log_type == 'notifications':
            logs_data, total_logs = _get_notification_logs(page, per_page)
        
        # Calculate pagination
        total_pages = (total_logs + per_page - 1) // per_page
        
        return render_template('admin/monitoring/logs.html',
                             logs=logs_data,
                             log_type=log_type,
                             search_email=search_email,
                             page=page,
                             total_pages=total_pages,
                             total_logs=total_logs)
    
    except Exception as e:
        current_app.logger.error(f"Error loading logs: {str(e)}")
        return render_template('admin/monitoring/logs.html',
                             logs=[],
                             error=str(e))

@monitoring_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Monitoring dashboard with statistics"""
    try:
        # Get statistics for the last 24 hours
        stats = _get_registration_stats()
        
        # Get recent errors
        recent_errors = _get_recent_errors(limit=10)
        
        # Get recent notifications
        recent_notifications = _get_recent_notifications(limit=10)
        
        return render_template('admin/monitoring/dashboard.html',
                             stats=stats,
                             recent_errors=recent_errors,
                             recent_notifications=recent_notifications)
    
    except Exception as e:
        current_app.logger.error(f"Error loading monitoring dashboard: {str(e)}")
        return render_template('admin/monitoring/dashboard.html',
                             stats={},
                             recent_errors=[],
                             recent_notifications=[],
                             error=str(e))

@monitoring_bp.route('/api/logs/search')
@login_required
@admin_required
def api_logs_search():
    """API endpoint for searching logs"""
    try:
        query = request.args.get('q', '').strip()
        log_type = request.args.get('type', 'all')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        if not query and not date_from and not date_to:
            return jsonify({'error': 'Search query or date range required'}), 400
        
        results = _search_logs(query, log_type, date_from, date_to)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error searching logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/api/notifications/mark-read', methods=['POST'])
@login_required
@admin_required
def api_mark_notification_read():
    """Mark notification as read"""
    try:
        data = request.get_json()
        notification_id = data.get('id')
        
        if not notification_id:
            return jsonify({'error': 'Notification ID required'}), 400
        
        _mark_notification_read(notification_id)
        
        return jsonify({'success': True})
    
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _get_registration_logs(page, per_page, search_email=None):
    """Get registration logs with pagination from database"""
    try:
        from models import RegistrationLog
        
        # Get logs from database
        logs_query = RegistrationLog.query
        
        # Filter by email if provided
        if search_email:
            logs_query = logs_query.filter(RegistrationLog.user_email.ilike(f'%{search_email}%'))
        
        logs_query = logs_query.order_by(RegistrationLog.created_at.desc())
        total_logs = logs_query.count()
        
        # Pagination
        logs = logs_query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict format
        logs_data = [log.to_dict() for log in logs]
        
        return logs_data, total_logs
    
    except Exception as e:
        current_app.logger.error(f"Error reading registration logs from database: {str(e)}")
        # Fallback to file-based logging
        try:
            log_file = os.path.join(os.getcwd(), 'logs', 'registration.log')
            if not os.path.exists(log_file):
                return [], 0
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse log lines
            logs = []
            for line in lines:
                try:
                    # Extract JSON part from log line
                    json_start = line.find('{')
                    if json_start != -1:
                        json_part = line[json_start:]
                        log_data = json.loads(json_part)
                        logs.append(log_data)
                except:
                    continue
            
            # Reverse to show newest first
            logs.reverse()
            
            # Pagination
            total = len(logs)
            start = (page - 1) * per_page
            end = start + per_page
            page_logs = logs[start:end]
            
            return page_logs, total
        except Exception as fallback_error:
            current_app.logger.error(f"Error reading registration logs from file: {str(fallback_error)}")
            return [], 0

def _get_error_logs(page, per_page, search_email=None):
    """Get error logs with pagination from database"""
    try:
        from models import RegistrationLog
        
        # Get error logs from database
        logs_query = RegistrationLog.query.filter(
            RegistrationLog.level.in_(['ERROR', 'WARNING'])
        )
        
        # Filter by email if provided
        if search_email:
            logs_query = logs_query.filter(RegistrationLog.user_email.ilike(f'%{search_email}%'))
        
        logs_query = logs_query.order_by(RegistrationLog.created_at.desc())
        total_logs = logs_query.count()
        
        # Pagination
        logs = logs_query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dict format
        logs_data = [log.to_dict() for log in logs]
        
        return logs_data, total_logs
    
    except Exception as e:
        current_app.logger.error(f"Error reading error logs from database: {str(e)}")
        # Rollback any failed transaction
        try:
            db.session.rollback()
        except:
            pass
        # Fallback to file-based logging
        try:
            log_file = os.path.join(os.getcwd(), 'logs', 'registration_errors.log')
            if not os.path.exists(log_file):
                return [], 0
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse log lines
            logs = []
            for line in lines:
                try:
                    # Extract JSON part from log line
                    json_start = line.find('{')
                    if json_start != -1:
                        json_part = line[json_start:]
                        log_data = json.loads(json_part)
                        logs.append(log_data)
                except:
                    continue
            
            # Reverse to show newest first
            logs.reverse()
            
            # Pagination
            total = len(logs)
            start = (page - 1) * per_page
            end = start + per_page
            page_logs = logs[start:end]
            
            return page_logs, total
        except Exception as fallback_error:
            current_app.logger.error(f"Error reading error logs from file: {str(fallback_error)}")
            return [], 0

def _get_notification_logs(page, per_page):
    """Get notification logs with pagination"""
    try:
        notifications_file = os.path.join(os.getcwd(), 'logs', 'admin_notifications.json')
        if not os.path.exists(notifications_file):
            return [], 0
        
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        # Reverse to show newest first
        notifications.reverse()
        
        # Pagination
        total = len(notifications)
        start = (page - 1) * per_page
        end = start + per_page
        page_notifications = notifications[start:end]
        
        return page_notifications, total
    
    except Exception as e:
        current_app.logger.error(f"Error reading notification logs: {str(e)}")
        return [], 0

def _get_registration_stats():
    """Get registration statistics for the last 24 hours"""
    try:
        from models import User, RegistrationVisitor, db
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        stats = {
            'total_registrations': 0,
            'successful_registrations': 0,
            'failed_registrations': 0,
            'validation_errors': 0,
            'database_errors': 0,
            'email_errors': 0,
            'critical_errors': 0,
            'registration_types': {
                'full_registration': 0,
                'quick_registration': 0,
                'invite_registration': 0
            }
        }
        
        # Get data from database (last 24 hours)
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Get user registrations from last 24 hours
        recent_users = User.query.filter(User.created_at >= cutoff_time).all()
        stats['total_registrations'] = len(recent_users)
        stats['successful_registrations'] = len(recent_users)
        
        # Get registration visitor data (with error handling)
        try:
            recent_visitors = RegistrationVisitor.query.filter(
                RegistrationVisitor.entry_time >= cutoff_time
            ).all()
            
            # Count registration types
            for visitor in recent_visitors:
                if visitor.page_type == 'quick_register':
                    stats['registration_types']['quick_registration'] += 1
                elif visitor.page_type == 'register':
                    stats['registration_types']['full_registration'] += 1
                elif visitor.page_type == 'invite_register':
                    stats['registration_types']['invite_registration'] += 1
            
            # Count form abandonments as failed registrations
            abandoned_forms = RegistrationVisitor.query.filter(
                RegistrationVisitor.entry_time >= cutoff_time,
                RegistrationVisitor.form_abandoned == True
            ).count()
            stats['failed_registrations'] = abandoned_forms
            
        except Exception as db_error:
            current_app.logger.warning(f"Database error in registration stats: {str(db_error)}")
            # Continue with default values if database query fails
        
        # Read registration logs
        log_file = os.path.join(os.getcwd(), 'logs', 'registration.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filter logs from last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            for line in lines:
                try:
                    json_start = line.find('{')
                    if json_start != -1:
                        json_part = line[json_start:]
                        log_data = json.loads(json_part)
                        
                        # Check if log is from last 24 hours
                        log_time = datetime.fromisoformat(log_data.get('request_context', {}).get('timestamp', '').replace('Z', '+00:00'))
                        if log_time.replace(tzinfo=None) < cutoff_time:
                            continue
                        
                        event = log_data.get('event', '')
                        registration_type = log_data.get('registration_type', '')
                        
                        stats['total_registrations'] += 1
                        
                        if event == 'registration_success':
                            stats['successful_registrations'] += 1
                        elif event == 'validation_error':
                            stats['validation_errors'] += 1
                        elif event == 'database_error':
                            stats['database_errors'] += 1
                        elif event == 'email_error':
                            stats['email_errors'] += 1
                        elif event == 'unexpected_error':
                            stats['critical_errors'] += 1
                        
                        if registration_type in stats['registration_types']:
                            stats['registration_types'][registration_type] += 1
                        
                except:
                    continue
        
        stats['failed_registrations'] = stats['total_registrations'] - stats['successful_registrations']
        
        return stats
    
    except Exception as e:
        current_app.logger.error(f"Error calculating registration stats: {str(e)}")
        return {
            'total_registrations': 0,
            'successful_registrations': 0,
            'failed_registrations': 0,
            'validation_errors': 0,
            'database_errors': 0,
            'email_errors': 0,
            'critical_errors': 0,
            'registration_types': {
                'full_registration': 0,
                'quick_registration': 0,
                'invite_registration': 0
            }
        }

def _get_recent_errors(limit=10):
    """Get recent errors"""
    try:
        error_logs, _ = _get_error_logs(1, limit)
        return error_logs
    except Exception as e:
        current_app.logger.error(f"Error getting recent errors: {str(e)}")
        return []

def _get_recent_notifications(limit=10):
    """Get recent notifications"""
    try:
        notifications, _ = _get_notification_logs(1, limit)
        return notifications
    except Exception as e:
        current_app.logger.error(f"Error getting recent notifications: {str(e)}")
        return []

def _search_logs(query, log_type, date_from, date_to):
    """Search logs by query and date range"""
    try:
        results = []
        
        # Determine which log files to search
        log_files = []
        if log_type in ['all', 'registration']:
            log_files.append(os.path.join(os.getcwd(), 'logs', 'registration.log'))
        if log_type in ['all', 'errors']:
            log_files.append(os.path.join(os.getcwd(), 'logs', 'registration_errors.log'))
        if log_type in ['all', 'notifications']:
            log_files.append(os.path.join(os.getcwd(), 'logs', 'admin_notifications.json'))
        
        for log_file in log_files:
            if not os.path.exists(log_file):
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                if log_file.endswith('.json'):
                    # JSON file (notifications)
                    try:
                        data = json.load(f)
                        for item in data:
                            if _matches_search_criteria(item, query, date_from, date_to):
                                results.append(item)
                    except:
                        continue
                else:
                    # Text log file
                    lines = f.readlines()
                    for line in lines:
                        try:
                            json_start = line.find('{')
                            if json_start != -1:
                                json_part = line[json_start:]
                                log_data = json.loads(json_part)
                                if _matches_search_criteria(log_data, query, date_from, date_to):
                                    results.append(log_data)
                        except:
                            continue
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get('request_context', {}).get('timestamp', ''), reverse=True)
        
        return results[:100]  # Limit to 100 results
    
    except Exception as e:
        current_app.logger.error(f"Error searching logs: {str(e)}")
        return []

def _matches_search_criteria(log_data, query, date_from, date_to):
    """Check if log data matches search criteria"""
    try:
        # Text search
        if query:
            search_text = json.dumps(log_data).lower()
            if query.lower() not in search_text:
                return False
        
        # Date range search
        if date_from or date_to:
            timestamp = log_data.get('request_context', {}).get('timestamp', '')
            if timestamp:
                try:
                    log_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                    if date_from:
                        from_time = datetime.fromisoformat(date_from)
                        if log_time.replace(tzinfo=None) < from_time:
                            return False
                    
                    if date_to:
                        to_time = datetime.fromisoformat(date_to)
                        if log_time.replace(tzinfo=None) > to_time:
                            return False
                except:
                    return False
        
        return True
    
    except:
        return False

def _mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notifications_file = os.path.join(os.getcwd(), 'logs', 'admin_notifications.json')
        if not os.path.exists(notifications_file):
            return
        
        with open(notifications_file, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        # Find and mark notification as read
        for notification in notifications:
            if str(notification.get('id', '')) == str(notification_id):
                notification['read'] = True
                break
        
        with open(notifications_file, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False, default=str)
    
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")


# ========================================
# SYSTEM EVENTS ROUTES (NEW MONITORING SYSTEM)
# ========================================

@monitoring_bp.route('/events')
@login_required
@admin_required
def events():
    """View system events from database"""
    try:
        event_type = request.args.get('type', 'all')  # all, error, login, registration, warning, info
        severity = request.args.get('severity', 'all')  # all, critical, error, warning, info
        resolved = request.args.get('resolved', 'all')  # all, true, false
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 50
        
        # Build query
        query = SystemEvent.query
        
        # Filter by event type
        if event_type != 'all':
            query = query.filter(SystemEvent.event_type == event_type)
        
        # Filter by severity
        if severity != 'all':
            query = query.filter(SystemEvent.severity == severity)
        
        # Filter by resolved status
        if resolved == 'true':
            query = query.filter(SystemEvent.resolved == True)
        elif resolved == 'false':
            query = query.filter(SystemEvent.resolved == False)
        
        # Search filter
        if search:
            query = query.filter(
                db.or_(
                    SystemEvent.title.ilike(f'%{search}%'),
                    SystemEvent.message.ilike(f'%{search}%'),
                    SystemEvent.user_email.ilike(f'%{search}%')
                )
            )
        
        # Order by created_at desc
        query = query.order_by(SystemEvent.created_at.desc())
        
        # Pagination
        total_events = query.count()
        events = query.offset((page - 1) * per_page).limit(per_page).all()
        
        total_pages = (total_events + per_page - 1) // per_page
        
        return render_template('admin/monitoring/events.html',
                             events=events,
                             event_type=event_type,
                             severity=severity,
                             resolved=resolved,
                             search=search,
                             page=page,
                             total_pages=total_pages,
                             total_events=total_events)
    
    except Exception as e:
        current_app.logger.error(f"Error loading system events: {str(e)}")
        return render_template('admin/monitoring/events.html',
                             events=[],
                             error=str(e))

@monitoring_bp.route('/events/<int:event_id>')
@login_required
@admin_required
def event_detail(event_id):
    """View detailed information about a specific event"""
    try:
        event = SystemEvent.query.get_or_404(event_id)
        return render_template('admin/monitoring/event_detail.html', event=event)
    except Exception as e:
        current_app.logger.error(f"Error loading event detail: {str(e)}")
        return render_template('admin/monitoring/event_detail.html',
                             event=None,
                             error=str(e))

@monitoring_bp.route('/events/<int:event_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_event(event_id):
    """Mark event as resolved"""
    try:
        event = SystemEvent.query.get_or_404(event_id)
        event.resolved = True
        event.resolved_at = datetime.now(timezone.utc)
        event.resolved_by = current_user.id
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Event marked as resolved'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resolving event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/events/<int:event_id>/unresolve', methods=['POST'])
@login_required
@admin_required
def unresolve_event(event_id):
    """Mark event as unresolved"""
    try:
        event = SystemEvent.query.get_or_404(event_id)
        event.resolved = False
        event.resolved_at = None
        event.resolved_by = None
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Event marked as unresolved'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unresolving event: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@monitoring_bp.route('/api/events/stats')
@login_required
@admin_required
def api_events_stats():
    """Get statistics about system events"""
    try:
        from sqlalchemy import func
        
        # Get stats for last 24 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        stats = {
            'total_events': SystemEvent.query.filter(SystemEvent.created_at >= cutoff_time).count(),
            'critical_errors': SystemEvent.query.filter(
                SystemEvent.severity == 'critical',
                SystemEvent.created_at >= cutoff_time
            ).count(),
            'errors': SystemEvent.query.filter(
                SystemEvent.severity == 'error',
                SystemEvent.created_at >= cutoff_time
            ).count(),
            'warnings': SystemEvent.query.filter(
                SystemEvent.severity == 'warning',
                SystemEvent.created_at >= cutoff_time
            ).count(),
            'logins': SystemEvent.query.filter(
                SystemEvent.event_type == 'login',
                SystemEvent.created_at >= cutoff_time
            ).count(),
            'registrations': SystemEvent.query.filter(
                SystemEvent.event_type == 'registration',
                SystemEvent.created_at >= cutoff_time
            ).count(),
            'unresolved_critical': SystemEvent.query.filter(
                SystemEvent.severity.in_(['critical', 'error']),
                SystemEvent.resolved == False
            ).count()
        }
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        current_app.logger.error(f"Error getting events stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
