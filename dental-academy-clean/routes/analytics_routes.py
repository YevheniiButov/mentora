# routes/analytics_routes.py - Analytics and statistics routes

from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from models import db, WebsiteVisit, PageView, UserSession
from utils.analytics import get_analytics_data, get_recent_visits, get_ip_analytics, cleanup_old_data
from utils.analytics_middleware import track_custom_event, track_user_action
import json

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
def track_event():
    """Track custom events from JavaScript"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            # Try to parse as JSON from form data
            try:
                data = json.loads(request.form.get('data', '{}'))
            except (json.JSONDecodeError, TypeError):
                data = request.form.to_dict()
        
        event_name = data.get('event_name')
        event_data = data.get('event_data')
        
        if not event_name:
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

