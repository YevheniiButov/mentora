# utils/analytics_middleware.py - Middleware for automatic analytics tracking

from flask import request, session, current_app, g
from utils.analytics import track_page_view, get_or_create_session
import time

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
                '/api/analytics'     # Avoid tracking API calls
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

def track_custom_event(event_name, event_data=None):
    """Track custom events (can be called from JavaScript)"""
    try:
        # This would be called from JavaScript via AJAX
        # For now, we'll just log it
        current_app.logger.info(f"Custom event: {event_name}, data: {event_data}")
        
        # You could extend this to store custom events in the database
        # For example, create a CustomEvent model
        
    except Exception as e:
        current_app.logger.error(f"Error tracking custom event: {str(e)}")

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


