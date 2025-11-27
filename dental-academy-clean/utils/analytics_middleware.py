# utils/analytics_middleware.py - Middleware for automatic analytics tracking

from flask import request, session, current_app, g
from utils.analytics import track_page_view, get_or_create_session
from extensions import db
import time
import json

def init_analytics_middleware(app):
    """Initialize analytics middleware"""
    
    @app.before_request
    def before_request():
        """Track request start time"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Track page view after request"""
        try:
            # Skip tracking for certain paths
            skip_paths = [
                '/static/',
                '/favicon.ico',
                '/robots.txt',
                '/sitemap.xml',
                '/admin/analytics',  # Avoid tracking analytics page itself
                '/api/analytics',    # Avoid tracking API calls
                '/analytics/track-event',  # Analytics endpoint - not a real page view
            ]
            
            if any(request.path.startswith(path) for path in skip_paths):
                return response
            
            # Skip tracking for non-GET requests (except important ones)
            if request.method != 'GET' and request.path not in ['/auth/login', '/auth/register']:
                return response
            
            # Get page title from response or use path
            page_title = None
            if hasattr(response, 'data') and response.data:
                try:
                    # Try to extract title from HTML
                    content = response.data.decode('utf-8')
                    if '<title>' in content:
                        start = content.find('<title>') + 7
                        end = content.find('</title>', start)
                        if end > start:
                            page_title = content[start:end].strip()
                except:
                    pass
            
            # Calculate time on page (if available from JavaScript)
            time_on_page = None
            if hasattr(g, 'start_time'):
                time_on_page = int((time.time() - g.start_time) * 1000)  # milliseconds
            
            # Track the page view
            track_page_view(
                page_url=request.url,
                page_title=page_title or request.path,
                time_on_page=time_on_page
            )
            
        except Exception as e:
            current_app.logger.error(f"Error in analytics middleware: {str(e)}")
        
        return response

def track_custom_event(event_name, event_data=None, request_obj=None):
    """Track custom events (can be called from JavaScript)"""
    try:
        from flask_login import current_user
        from models import AnalyticsEvent, UserActivityLog
        from utils.analytics import parse_user_agent, get_client_ip
        from datetime import datetime, timezone
        
        # Use provided request or default to Flask's request
        if request_obj is None:
            from flask import request as flask_request
            request_obj = flask_request
        
        # Extract page information from event_data
        page_url = None
        if isinstance(event_data, dict):
            page_url = event_data.get('page_url')
            referrer_url = event_data.get('referrer')
        else:
            referrer_url = request_obj.referrer
        
        # If no page_url in event data, try to get from referrer
        if not page_url:
            page_url = referrer_url or request_obj.url
        
        # Get user info
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Get request info
        ip_address = get_client_ip()
        user_agent = request_obj.headers.get('User-Agent', '')
        if isinstance(event_data, dict) and 'user_agent' in event_data:
            user_agent = event_data.get('user_agent', user_agent)
        
        parsed_ua = parse_user_agent(user_agent)
        
        # Save to AnalyticsEvent table
        try:
            analytics_event = AnalyticsEvent(
                user_id=user_id,
                event_name=event_name,
                event_category='user',  # Default category
                event_action='custom',
                event_label=str(event_data) if event_data else None,
                event_data=json.dumps(event_data) if isinstance(event_data, dict) else str(event_data) if event_data else None,
                page_url=page_url,
                referrer_url=referrer_url,
                user_agent=user_agent,
                ip_address=ip_address,
                device_type=parsed_ua.get('device_type'),
                browser=parsed_ua.get('browser'),
                os=parsed_ua.get('os'),
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(analytics_event)
            db.session.flush()
        except Exception as e:
            current_app.logger.error(f"Error saving AnalyticsEvent: {str(e)}")
        
        # Also log to UserActivityLog for activity tracking (with correct page info)
        if user_id:
            try:
                from flask import session
                session_id = session.get('analytics_session_id') or session.get('session_id')
                
                # Extract page title from URL
                page_title = None
                if page_url:
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(page_url)
                        path = parsed.path.strip('/')
                        if path:
                            page_title = path.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                    except:
                        pass
                
                activity_log = UserActivityLog(
                    user_id=user_id,
                    action_type='event',  # Use 'event' instead of 'page_view'
                    page_url=page_url,  # Real page URL from event data
                    page_title=page_title or event_name,  # Page title or event name
                    action_description=f"Event: {event_name}",  # Description
                    ip_address=ip_address,
                    user_agent=user_agent,
                    referrer=referrer_url,
                    session_id=session_id,
                    browser=parsed_ua.get('browser'),
                    os=parsed_ua.get('os'),
                    device_type=parsed_ua.get('device_type'),
                    timestamp=datetime.now(timezone.utc),
                    action_metadata=event_data if isinstance(event_data, dict) else {'event_data': str(event_data)} if event_data else None
                )
                db.session.add(activity_log)
            except Exception as e:
                current_app.logger.error(f"Error saving UserActivityLog: {str(e)}")
        
        db.session.commit()
        current_app.logger.info(f"Custom event tracked: {event_name}, page: {page_url}, user: {user_id}")
        
    except Exception as e:
        current_app.logger.error(f"Error tracking custom event: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass

def track_user_action(action, details=None):
    """Track user actions (login, registration, etc.)"""
    try:
        # Get current session
        user_session = get_or_create_session()
        
        # Log the action
        current_app.logger.info(f"User action: {action}, session: {user_session.session_id}, details: {details}")
        
        # You could extend this to store user actions in the database
        
    except Exception as e:
        current_app.logger.error(f"Error tracking user action: {str(e)}")













