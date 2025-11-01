# routes/analytics_routes.py - Analytics and statistics routes

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import csrf
from utils.decorators import admin_required
from models import db, WebsiteVisit, PageView, UserSession, ProfessionClick
from utils.analytics import get_analytics_data, get_recent_visits, get_ip_analytics, cleanup_old_data
from utils.analytics_middleware import track_custom_event, track_user_action
import json
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def dashboard():
    """Analytics dashboard"""
    try:
        # Get analytics data for last 30 days
        analytics_data = get_analytics_data(days=30)
        
        if not analytics_data:
            analytics_data = {
                'total_visits': 0,
                'unique_visitors': 0,
                'total_page_views': 0,
                'active_sessions': 0,
                'top_pages': [],
                'browser_stats': [],
                'os_stats': [],
                'device_stats': [],
                'daily_visits': []
            }
        
        return render_template('admin/analytics_dashboard.html', 
                             analytics_data=analytics_data)
        
    except Exception as e:
        current_app.logger.error(f"Analytics dashboard error: {str(e)}")
        return render_template('admin/analytics_dashboard.html', 
                             analytics_data=None, error=str(e))

@analytics_bp.route('/api/data')
@login_required
def api_data():
    """API endpoint for analytics data"""
    try:
        days = request.args.get('days', 30, type=int)
        analytics_data = get_analytics_data(days=days)
        
        if not analytics_data:
            return jsonify({'error': 'Failed to get analytics data'}), 500
        
        return jsonify(analytics_data)
        
    except Exception as e:
        current_app.logger.error(f"Analytics API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/recent-visits')
@login_required
def api_recent_visits():
    """API endpoint for recent visits"""
    try:
        limit = request.args.get('limit', 50, type=int)
        visits = get_recent_visits(limit=limit)
        
        return jsonify({'visits': visits})
        
    except Exception as e:
        current_app.logger.error(f"Recent visits API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/ip-analytics')
@login_required
def api_ip_analytics():
    """API endpoint for IP analytics"""
    try:
        ip_address = request.args.get('ip')
        days = request.args.get('days', 30, type=int)
        
        ip_data = get_ip_analytics(ip_address=ip_address, days=days)
        
        return jsonify({'ip_analytics': ip_data})
        
    except Exception as e:
        current_app.logger.error(f"IP analytics API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/visitors')
@login_required
def visitors():
    """Visitors page with IP details"""
    try:
        return render_template('admin/analytics_visitors.html')
        
    except Exception as e:
        current_app.logger.error(f"Visitors page error: {str(e)}")
        return render_template('admin/analytics_visitors.html', error=str(e))

@analytics_bp.route('/pages')
@login_required
def pages():
    """Page analytics"""
    try:
        return render_template('admin/analytics_pages.html')
        
    except Exception as e:
        current_app.logger.error(f"Pages analytics error: {str(e)}")
        return render_template('admin/analytics_pages.html', error=str(e))

@analytics_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup():
    """Clean up old analytics data"""
    try:
        days_to_keep = request.json.get('days_to_keep', 90)
        
        result = cleanup_old_data(days_to_keep=days_to_keep)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'Cleaned up {result["deleted_visits"]} visits and {result["deleted_sessions"]} sessions',
                'result': result
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to cleanup data'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Cleanup error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/track-event', methods=['POST'])
@csrf.exempt
def track_event():
    """Track custom events from JavaScript"""
    try:
        data = None
        
        # Log request details for debugging
        current_app.logger.info(f"Track event request - Content-Type: {request.content_type}, Content-Length: {request.content_length}")
        
        # Handle different content types
        if request.is_json:
            data = request.get_json()
            current_app.logger.debug(f"Parsed JSON data: {data}")
        elif request.content_type and ('text/plain' in request.content_type or 'application/octet-stream' in request.content_type):
            # Handle sendBeacon requests (text/plain, text/plain;charset=UTF-8, or Blob)
            raw_data = request.get_data(as_text=True)
            current_app.logger.debug(f"Raw sendBeacon data (first 200 chars): {raw_data[:200] if raw_data else 'empty'}")
            try:
                if raw_data:
                    data = json.loads(raw_data)
                    current_app.logger.debug(f"Parsed sendBeacon data: {data}")
                else:
                    current_app.logger.debug("Empty sendBeacon data received")
                    return jsonify({'error': 'Empty data received'}), 400
            except (json.JSONDecodeError, TypeError) as e:
                current_app.logger.debug(f"Failed to parse sendBeacon data: {str(e)}")
                return jsonify({'error': 'Invalid JSON data'}), 400
        elif request.data:
            # Try to parse raw request data as JSON
            try:
                raw_data = request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
                    current_app.logger.debug(f"Parsed raw data as JSON: {data}")
                else:
                    data = None
            except (json.JSONDecodeError, TypeError):
                data = None
        else:
            # Try to parse as JSON from form data
            try:
                form_data = request.form.get('data', '{}')
                if form_data and form_data != '{}':
                    data = json.loads(form_data)
                    current_app.logger.debug(f"Parsed form JSON data: {data}")
                else:
                    data = request.form.to_dict() if request.form else None
                    if data:
                        current_app.logger.debug(f"Parsed form data: {data}")
            except (json.JSONDecodeError, TypeError):
                data = request.form.to_dict() if request.form else None
                if data:
                    current_app.logger.debug(f"Parsed form data as dict: {data}")
        
        if not data:
            current_app.logger.debug("No data received in track-event request")
            return jsonify({'error': 'No data received'}), 400
        
        event_name = data.get('event_name')
        event_data = data.get('event_data')
        
        if not event_name:
            current_app.logger.debug(f"Event name missing in data: {data}")
            return jsonify({'error': 'Event name is required'}), 400
        
        track_custom_event(event_name, event_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Track event error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export')
@login_required
def export_data():
    """Export analytics data"""
    try:
        days = request.args.get('days', 30, type=int)
        format_type = request.args.get('format', 'json')
        
        analytics_data = get_analytics_data(days=days)
        
        if not analytics_data:
            return jsonify({'error': 'Failed to get analytics data'}), 500
        
        if format_type == 'csv':
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write basic stats
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Visits', analytics_data['total_visits']])
            writer.writerow(['Unique Visitors', analytics_data['unique_visitors']])
            writer.writerow(['Total Page Views', analytics_data['total_page_views']])
            writer.writerow(['Active Sessions', analytics_data['active_sessions']])
            
            # Write top pages
            writer.writerow([])
            writer.writerow(['Top Pages'])
            writer.writerow(['URL', 'Views'])
            for page in analytics_data['top_pages']:
                writer.writerow([page['url'], page['views']])
            
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=analytics_{days}days.csv'
            }
        
        else:
            # Return JSON
            return jsonify(analytics_data)
        
    except Exception as e:
        current_app.logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/track-profession-click', methods=['POST'])
def track_profession_click():
    """Track profession card clicks on BIG info page"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['profession', 'type', 'url', 'page_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract data
        profession = data.get('profession', '').strip()
        profession_type = data.get('type', '').strip()  # 'eu' or 'non-eu'
        target_url = data.get('url', '').strip()
        page_url = data.get('page_url', '').strip()
        user_agent = data.get('user_agent', '')
        timestamp = data.get('timestamp', '')
        language = data.get('language', 'unknown')
        
        # Get IP address
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # Log the profession click
        current_app.logger.info(f"PROFESSION_CLICK: {profession} ({profession_type}) -> {target_url} from {page_url} | IP: {ip_address} | Lang: {language}")
        
        # Save to database
        try:
            profession_click = ProfessionClick(
                profession=profession,
                profession_type=profession_type,
                target_url=target_url,
                page_url=page_url,
                ip_address=ip_address,
                user_agent=user_agent,
                language=language,
                user_id=current_user.id if current_user.is_authenticated else None,
                user_email=current_user.email if current_user.is_authenticated else None,
                clicked_at=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.utcnow()
            )
            db.session.add(profession_click)
            db.session.commit()
        except Exception as db_error:
            current_app.logger.error(f"Error saving profession click to database: {str(db_error)}")
            db.session.rollback()
        
        return jsonify({
            'status': 'success',
            'message': 'Profession click tracked',
            'profession': profession,
            'type': profession_type,
            'url': target_url
        })
        
    except Exception as e:
        current_app.logger.error(f"Error tracking profession click: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/profession-clicks')
@login_required
@admin_required
def profession_clicks():
    """Show profession click tracking dashboard"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        profession_filter = request.args.get('profession', '')
        type_filter = request.args.get('type', '')
        language_filter = request.args.get('language', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = ProfessionClick.query
        
        # Apply filters
        if profession_filter:
            query = query.filter(ProfessionClick.profession.ilike(f'%{profession_filter}%'))
        if type_filter:
            query = query.filter(ProfessionClick.profession_type == type_filter)
        if language_filter:
            query = query.filter(ProfessionClick.language == language_filter)
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(ProfessionClick.clicked_at >= date_from_obj)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(ProfessionClick.clicked_at <= date_to_obj)
            except ValueError:
                pass
        
        # Order by most recent first
        query = query.order_by(ProfessionClick.clicked_at.desc())
        
        # Paginate
        clicks = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        stats = _get_profession_click_stats()
        
        # Get unique values for filters
        unique_professions = db.session.query(ProfessionClick.profession).distinct().all()
        unique_professions = [p[0] for p in unique_professions]
        
        unique_types = db.session.query(ProfessionClick.profession_type).distinct().all()
        unique_types = [t[0] for t in unique_types]
        
        unique_languages = db.session.query(ProfessionClick.language).distinct().all()
        unique_languages = [l[0] for l in unique_languages if l[0]]
        
        return render_template('admin/analytics/profession_clicks.html',
                             clicks=clicks,
                             stats=stats,
                             unique_professions=unique_professions,
                             unique_types=unique_types,
                             unique_languages=unique_languages,
                             current_filters={
                                 'profession': profession_filter,
                                 'type': type_filter,
                                 'language': language_filter,
                                 'date_from': date_from,
                                 'date_to': date_to
                             })
        
    except Exception as e:
        current_app.logger.error(f"Error loading profession clicks: {str(e)}")
        return render_template('admin/analytics/profession_clicks.html',
                             error=str(e))


def _get_profession_click_stats():
    """Get profession click statistics"""
    try:
        # Total clicks
        total_clicks = ProfessionClick.query.count()
        
        # Clicks by profession
        profession_stats = db.session.query(
            ProfessionClick.profession,
            db.func.count(ProfessionClick.id).label('count')
        ).group_by(ProfessionClick.profession).order_by(db.func.count(ProfessionClick.id).desc()).all()
        
        # Clicks by type
        type_stats = db.session.query(
            ProfessionClick.profession_type,
            db.func.count(ProfessionClick.id).label('count')
        ).group_by(ProfessionClick.profession_type).all()
        
        # Clicks by language
        language_stats = db.session.query(
            ProfessionClick.language,
            db.func.count(ProfessionClick.id).label('count')
        ).group_by(ProfessionClick.language).order_by(db.func.count(ProfessionClick.id).desc()).all()
        
        # Recent clicks (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_clicks = ProfessionClick.query.filter(
            ProfessionClick.clicked_at >= yesterday
        ).count()
        
        # Unique IPs
        unique_ips = db.session.query(ProfessionClick.ip_address).distinct().count()
        
        return {
            'total_clicks': total_clicks,
            'recent_clicks': recent_clicks,
            'unique_ips': unique_ips,
            'profession_stats': profession_stats,
            'type_stats': type_stats,
            'language_stats': language_stats
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting profession click stats: {str(e)}")
        return {
            'total_clicks': 0,
            'recent_clicks': 0,
            'unique_ips': 0,
            'profession_stats': [],
            'type_stats': [],
            'language_stats': []
        }

