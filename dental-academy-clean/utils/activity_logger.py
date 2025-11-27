"""
Activity Logger - Logs detailed user activity
"""

import logging
from flask import request, current_app, session
from datetime import datetime, timezone
from extensions import db
from utils.analytics import parse_user_agent, get_client_ip

logger = logging.getLogger(__name__)

# Pages/actions to skip logging (to reduce noise)
SKIP_PATTERNS = [
    '/static/',
    '/api/health',
    '/favicon.ico',
    '/robots.txt',
    '/sitemap.xml',
    '/analytics/track-event',  # Analytics endpoint - not a real page view
    '/api/',  # All API endpoints - skip logging
]

def should_log_activity(path):
    """Check if activity should be logged"""
    if not path:
        return False
    
    # Skip static files and common non-user actions
    for pattern in SKIP_PATTERNS:
        if pattern in path:
            return False
    
    return True

def log_user_activity(action_type='page_view', action_description=None, metadata=None):
    """
    Log user activity to database
    
    Args:
        action_type: Type of action (page_view, login, logout, action, etc.)
        action_description: Human-readable description of the action
        metadata: Additional JSON data about the action
    """
    try:
        from flask_login import current_user
        from models import UserActivityLog
        
        # Only log for authenticated users
        if not current_user or not current_user.is_authenticated:
            return
        
        # Get request info
        path = request.path
        if not should_log_activity(path):
            return
        
        # Parse user agent
        user_agent = request.headers.get('User-Agent', '')
        parsed_ua = parse_user_agent(user_agent)
        
        # Get IP address
        ip_address = get_client_ip()
        
        # Get session ID
        session_id = session.get('analytics_session_id') or session.get('session_id')
        
        # Get page title from referrer or path
        page_title = None
        if action_type == 'page_view':
            # Try to extract meaningful title from path
            path_parts = path.strip('/').split('/')
            if path_parts:
                page_title = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
        
        # Create activity log entry
        activity_log = UserActivityLog(
            user_id=current_user.id,
            action_type=action_type,
            page_url=path,
            page_title=page_title or action_description,
            action_description=action_description,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=request.referrer,
            session_id=session_id,
            browser=parsed_ua.get('browser'),
            os=parsed_ua.get('os'),
            device_type=parsed_ua.get('device_type'),
            timestamp=datetime.now(timezone.utc),
            action_metadata=metadata  # Use action_metadata (metadata is reserved in SQLAlchemy)
        )
        
        db.session.add(activity_log)
        db.session.commit()
        
    except Exception as e:
        # Don't fail the request if logging fails
        logger.error(f"Error logging user activity: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass

def get_user_activity_summary(user_id, days=7):
    """
    Get summary of user activity for the last N days
    
    Args:
        user_id: User ID
        days: Number of days to look back
        
    Returns:
        dict: Summary statistics
    """
    try:
        from models import UserActivityLog
        from datetime import timedelta
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get activity logs
        logs = UserActivityLog.query.filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.timestamp >= cutoff_date
        ).order_by(UserActivityLog.timestamp.desc()).all()
        
        # Calculate statistics
        total_actions = len(logs)
        unique_pages = len(set(log.page_url for log in logs if log.page_url))
        action_types = {}
        for log in logs:
            action_types[log.action_type] = action_types.get(log.action_type, 0) + 1
        
        # Get online time (approximate - based on activity timestamps)
        online_time = 0
        if logs:
            first_activity = min(log.timestamp for log in logs)
            last_activity = max(log.timestamp for log in logs)
            online_time = (last_activity - first_activity).total_seconds() / 3600  # hours
        
        return {
            'total_actions': total_actions,
            'unique_pages': unique_pages,
            'action_types': action_types,
            'online_time_hours': round(online_time, 2),
            'first_activity': logs[-1].timestamp if logs else None,
            'last_activity': logs[0].timestamp if logs else None,
            'logs': [log.to_dict() for log in logs[:100]]  # Last 100 logs
        }
    except Exception as e:
        logger.error(f"Error getting user activity summary: {str(e)}")
        return {
            'total_actions': 0,
            'unique_pages': 0,
            'action_types': {},
            'online_time_hours': 0,
            'first_activity': None,
            'last_activity': None,
            'logs': []
        }

