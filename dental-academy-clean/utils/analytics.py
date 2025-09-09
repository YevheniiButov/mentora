# utils/analytics.py - Website analytics and tracking utilities

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import request, session, current_app
from models import db, WebsiteVisit, PageView, UserSession, User
import json

def get_client_ip():
    """Get client IP address from request"""
    # Check for forwarded IPs (behind proxy/load balancer)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def parse_user_agent(user_agent):
    """Parse user agent string to extract browser, OS, and device info"""
    if not user_agent:
        return {'browser': 'Unknown', 'os': 'Unknown', 'device_type': 'Unknown'}
    
    user_agent = user_agent.lower()
    
    # Browser detection
    browser = 'Unknown'
    if 'chrome' in user_agent and 'edg' not in user_agent:
        browser = 'Chrome'
    elif 'firefox' in user_agent:
        browser = 'Firefox'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        browser = 'Safari'
    elif 'edg' in user_agent:
        browser = 'Edge'
    elif 'opera' in user_agent:
        browser = 'Opera'
    
    # OS detection
    os = 'Unknown'
    if 'windows' in user_agent:
        os = 'Windows'
    elif 'mac' in user_agent:
        os = 'macOS'
    elif 'linux' in user_agent:
        os = 'Linux'
    elif 'android' in user_agent:
        os = 'Android'
    elif 'ios' in user_agent:
        os = 'iOS'
    
    # Device type detection
    device_type = 'desktop'
    if 'mobile' in user_agent or 'android' in user_agent:
        device_type = 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        device_type = 'tablet'
    
    return {
        'browser': browser,
        'os': os,
        'device_type': device_type
    }

def get_or_create_session():
    """Get or create user session"""
    session_id = session.get('analytics_session_id')
    
    if not session_id:
        # Generate new session ID
        session_id = secrets.token_urlsafe(32)
        session['analytics_session_id'] = session_id
    
    # Get or create session in database
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    
    if not user_session:
        # Create new session
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        parsed_ua = parse_user_agent(user_agent)
        
        user_session = UserSession(
            session_id=session_id,
            user_id=session.get('user_id') if session.get('user_id') else None,
            ip_address=ip_address,
            user_agent=user_agent,
            browser=parsed_ua['browser'],
            os=parsed_ua['os'],
            device_type=parsed_ua['device_type'],
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        db.session.add(user_session)
        db.session.commit()
    else:
        # Update last activity
        user_session.last_activity = datetime.utcnow()
        user_session.total_visits += 1
        db.session.commit()
    
    return user_session

def track_page_view(page_url, page_title=None, time_on_page=None, scroll_depth=None):
    """Track a page view"""
    try:
        # Get or create session
        user_session = get_or_create_session()
        
        # Get client info
        ip_address = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        referrer = request.headers.get('Referer', '')
        parsed_ua = parse_user_agent(user_agent)
        
        # Create visit record
        visit = WebsiteVisit(
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            page_url=page_url,
            page_title=page_title,
            session_id=user_session.session_id,
            user_id=user_session.user_id,
            browser=parsed_ua['browser'],
            os=parsed_ua['os'],
            device_type=parsed_ua['device_type'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(visit)
        db.session.flush()  # Get the visit ID
        
        # Create page view record
        page_view = PageView(
            visit_id=visit.id,
            page_url=page_url,
            page_title=page_title,
            time_on_page=time_on_page,
            scroll_depth=scroll_depth,
            created_at=datetime.utcnow()
        )
        
        db.session.add(page_view)
        db.session.commit()
        
        return visit
        
    except Exception as e:
        current_app.logger.error(f"Error tracking page view: {str(e)}")
        db.session.rollback()
        return None

def get_analytics_data(days=30):
    """Get analytics data for the specified number of days"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Basic stats
        total_visits = WebsiteVisit.query.filter(
            WebsiteVisit.created_at >= start_date
        ).count()
        
        unique_visitors = db.session.query(WebsiteVisit.ip_address).filter(
            WebsiteVisit.created_at >= start_date
        ).distinct().count()
        
        # Page views
        total_page_views = PageView.query.filter(
            PageView.created_at >= start_date
        ).count()
        
        # Active sessions
        active_sessions = UserSession.query.filter(
            UserSession.is_active == True,
            UserSession.last_activity >= start_date
        ).count()
        
        # Top pages
        top_pages = db.session.query(
            WebsiteVisit.page_url,
            db.func.count(WebsiteVisit.id).label('views')
        ).filter(
            WebsiteVisit.created_at >= start_date
        ).group_by(WebsiteVisit.page_url).order_by(
            db.desc('views')
        ).limit(10).all()
        
        # Browser stats
        browser_stats = db.session.query(
            WebsiteVisit.browser,
            db.func.count(WebsiteVisit.id).label('count')
        ).filter(
            WebsiteVisit.created_at >= start_date
        ).group_by(WebsiteVisit.browser).order_by(
            db.desc('count')
        ).all()
        
        # OS stats
        os_stats = db.session.query(
            WebsiteVisit.os,
            db.func.count(WebsiteVisit.id).label('count')
        ).filter(
            WebsiteVisit.created_at >= start_date
        ).group_by(WebsiteVisit.os).order_by(
            db.desc('count')
        ).all()
        
        # Device stats
        device_stats = db.session.query(
            WebsiteVisit.device_type,
            db.func.count(WebsiteVisit.id).label('count')
        ).filter(
            WebsiteVisit.created_at >= start_date
        ).group_by(WebsiteVisit.device_type).order_by(
            db.desc('count')
        ).all()
        
        # Daily visits
        daily_visits = db.session.query(
            db.func.date(WebsiteVisit.created_at).label('date'),
            db.func.count(WebsiteVisit.id).label('visits')
        ).filter(
            WebsiteVisit.created_at >= start_date
        ).group_by(
            db.func.date(WebsiteVisit.created_at)
        ).order_by('date').all()
        
        return {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'total_page_views': total_page_views,
            'active_sessions': active_sessions,
            'top_pages': [{'url': page[0], 'views': page[1]} for page in top_pages],
            'browser_stats': [{'browser': browser[0], 'count': browser[1]} for browser in browser_stats],
            'os_stats': [{'os': os[0], 'count': os[1]} for os in os_stats],
            'device_stats': [{'device': device[0], 'count': device[1]} for device in device_stats],
            'daily_visits': [{'date': visit[0].isoformat(), 'visits': visit[1]} for visit in daily_visits]
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting analytics data: {str(e)}")
        return None

def get_recent_visits(limit=50):
    """Get recent visits with details"""
    try:
        visits = WebsiteVisit.query.order_by(
            WebsiteVisit.created_at.desc()
        ).limit(limit).all()
        
        return [visit.to_dict() for visit in visits]
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent visits: {str(e)}")
        return []

def get_ip_analytics(ip_address=None, days=30):
    """Get analytics for specific IP or all IPs"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = WebsiteVisit.query.filter(
            WebsiteVisit.created_at >= start_date
        )
        
        if ip_address:
            query = query.filter(WebsiteVisit.ip_address == ip_address)
        
        visits = query.order_by(WebsiteVisit.created_at.desc()).all()
        
        # Group by IP
        ip_stats = {}
        for visit in visits:
            ip = visit.ip_address
            if ip not in ip_stats:
                ip_stats[ip] = {
                    'ip_address': ip,
                    'total_visits': 0,
                    'first_visit': visit.created_at,
                    'last_visit': visit.created_at,
                    'pages_visited': set(),
                    'user_agents': set(),
                    'countries': set()
                }
            
            ip_stats[ip]['total_visits'] += 1
            ip_stats[ip]['last_visit'] = max(ip_stats[ip]['last_visit'], visit.created_at)
            ip_stats[ip]['pages_visited'].add(visit.page_url)
            if visit.user_agent:
                ip_stats[ip]['user_agents'].add(visit.user_agent)
            if visit.country:
                ip_stats[ip]['countries'].add(visit.country)
        
        # Convert sets to lists for JSON serialization
        for ip in ip_stats:
            ip_stats[ip]['pages_visited'] = list(ip_stats[ip]['pages_visited'])
            ip_stats[ip]['user_agents'] = list(ip_stats[ip]['user_agents'])
            ip_stats[ip]['countries'] = list(ip_stats[ip]['countries'])
            ip_stats[ip]['first_visit'] = ip_stats[ip]['first_visit'].isoformat()
            ip_stats[ip]['last_visit'] = ip_stats[ip]['last_visit'].isoformat()
        
        return list(ip_stats.values())
        
    except Exception as e:
        current_app.logger.error(f"Error getting IP analytics: {str(e)}")
        return []

def cleanup_old_data(days_to_keep=90):
    """Clean up old analytics data"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old visits
        old_visits = WebsiteVisit.query.filter(
            WebsiteVisit.created_at < cutoff_date
        ).count()
        
        WebsiteVisit.query.filter(
            WebsiteVisit.created_at < cutoff_date
        ).delete()
        
        # Delete old sessions
        old_sessions = UserSession.query.filter(
            UserSession.started_at < cutoff_date
        ).count()
        
        UserSession.query.filter(
            UserSession.started_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return {
            'deleted_visits': old_visits,
            'deleted_sessions': old_sessions,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up old data: {str(e)}")
        db.session.rollback()
        return None

