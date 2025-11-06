# utils/database_cleanup.py - Database cleanup utilities for Brevo compliance

from models import User, db
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

def cleanup_inactive_users(days_inactive=90):
    """
    Remove users who haven't logged in for specified days
    This helps maintain a clean database for Brevo compliance
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_inactive)
        
        # Find inactive users
        inactive_users = User.query.filter(
            User.last_login_at < cutoff_date,
            User.email_confirmed == False
        ).all()
        
        count = len(inactive_users)
        
        if count > 0:
            # Delete inactive users
            for user in inactive_users:
                db.session.delete(user)
            
            db.session.commit()
            logger.info(f"Cleaned up {count} inactive users")
            return count
        else:
            logger.info("No inactive users found for cleanup")
            return 0
            
    except Exception as e:
        logger.error(f"Error during user cleanup: {e}")
        db.session.rollback()
        return 0

def cleanup_unconfirmed_users(days_unconfirmed=7):
    """
    Remove users who haven't confirmed their email within specified days
    """
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_unconfirmed)
        
        # Find unconfirmed users
        unconfirmed_users = User.query.filter(
            User.email_confirmed == False,
            User.created_at < cutoff_date
        ).all()
        
        count = len(unconfirmed_users)
        
        if count > 0:
            # Delete unconfirmed users
            for user in unconfirmed_users:
                db.session.delete(user)
            
            db.session.commit()
            logger.info(f"Cleaned up {count} unconfirmed users")
            return count
        else:
            logger.info("No unconfirmed users found for cleanup")
            return 0
            
    except Exception as e:
        logger.error(f"Error during unconfirmed user cleanup: {e}")
        db.session.rollback()
        return 0

def get_database_stats():
    """
    Get database statistics for monitoring
    """
    try:
        total_users = User.query.count()
        confirmed_users = User.query.filter(User.email_confirmed == True).count()
        unconfirmed_users = total_users - confirmed_users
        
        # Users created in last 30 days
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_users = User.query.filter(User.created_at >= thirty_days_ago).count()
        
        # Users who logged in last 30 days
        active_users = User.query.filter(
            User.last_login_at >= thirty_days_ago
        ).count()
        
        stats = {
            'total_users': total_users,
            'confirmed_users': confirmed_users,
            'unconfirmed_users': unconfirmed_users,
            'recent_users': recent_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}

def validate_email_addresses():
    """
    Check for invalid email addresses in the database
    """
    try:
        import re
        
        # Get all users
        users = User.query.all()
        invalid_emails = []
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for user in users:
            if not re.match(email_pattern, user.email):
                invalid_emails.append({
                    'id': user.id,
                    'email': user.email,
                    'created_at': user.created_at
                })
        
        return invalid_emails
        
    except Exception as e:
        logger.error(f"Error validating email addresses: {e}")
        return []

def run_full_cleanup():
    """
    Run all cleanup operations
    """
    logger.info("Starting full database cleanup...")
    
    # Cleanup operations
    inactive_removed = cleanup_inactive_users()
    unconfirmed_removed = cleanup_unconfirmed_users()
    
    # Get stats
    stats = get_database_stats()
    invalid_emails = validate_email_addresses()
    
    result = {
        'inactive_removed': inactive_removed,
        'unconfirmed_removed': unconfirmed_removed,
        'stats': stats,
        'invalid_emails': invalid_emails
    }
    
    logger.info(f"Cleanup completed: {result}")
    return result
