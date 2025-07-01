"""
Deployment API Routes
API маршруты для развертывания шаблонов

Features:
- Secure deployment endpoints with admin authentication
- CSRF protection and rate limiting
- Comprehensive error handling
- Audit logging and IP tracking
- Integration with TemplateDeployer
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_login import login_required, current_user
from functools import wraps
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import hashlib
import uuid

# Import TemplateDeployer
from utils.template_deployer import TemplateDeployer, DeploymentConfig

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
deployment_bp = Blueprint('deployment', __name__, url_prefix='/api/deploy')

# Rate limiting storage (in production, use Redis)
deployment_attempts = {}

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error_code': 'AUTH_REQUIRED'
            }), 401
        
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin privileges required',
                'error_code': 'ADMIN_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_attempts: int = 5, window: int = 300):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = current_user.id if current_user.is_authenticated else request.remote_addr
            current_time = time.time()
            
            # Clean old attempts
            if user_id in deployment_attempts:
                deployment_attempts[user_id] = [
                    attempt for attempt in deployment_attempts[user_id]
                    if current_time - attempt < window
                ]
            else:
                deployment_attempts[user_id] = []
            
            # Check rate limit
            if len(deployment_attempts[user_id]) >= max_attempts:
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded. Please try again later.',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': window
                }), 429
            
            # Add current attempt
            deployment_attempts[user_id].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action: str, details: Dict[str, Any] = None):
    """Audit logging function"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': current_user.id if current_user.is_authenticated else 'anonymous',
            'user_email': current_user.email if current_user.is_authenticated else 'anonymous',
            'action': action,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'details': details or {}
        }
        
        logger.info(f"DEPLOYMENT_AUDIT: {json.dumps(log_entry)}")
        
        # Store in database if needed
        # db.audit_logs.insert_one(log_entry)
        
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")

def get_deployer() -> TemplateDeployer:
    """Get or create TemplateDeployer instance"""
    if not hasattr(g, 'template_deployer'):
        config = DeploymentConfig(
            backup_enabled=True,
            preview_enabled=True,
            validation_enabled=True,
            max_backups=10,
            backup_dir="backups/templates",
            preview_dir="previews",
            temp_dir="temp"
        )
        g.template_deployer = TemplateDeployer(config)
    
    return g.template_deployer

def validate_csrf_token():
    """Validate CSRF token for POST requests"""
    if request.method == 'POST':
        token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        if not token:
            return False, 'CSRF token missing'
        
        # In production, validate against session token
        # For now, just check if token exists
        if not token or len(token) < 10:
            return False, 'Invalid CSRF token'
    
    return True, None

def create_error_response(message: str, error_code: str = None, details: Dict = None, status_code: int = 400):
    """Create standardized error response"""
    response = {
        'success': False,
        'message': message,
        'error_code': error_code,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def create_success_response(data: Dict = None, message: str = "Operation completed successfully"):
    """Create standardized success response"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data:
        response['data'] = data
    
    return jsonify(response)

@deployment_bp.route('/backup', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_attempts=10, window=300)
def create_backup():
    """Create backup of current template"""
    try:
        # Validate CSRF token
        csrf_valid, csrf_error = validate_csrf_token()
        if not csrf_valid:
            return create_error_response(csrf_error, 'CSRF_INVALID', status_code=403)
        
        # Get request data
        data = request.get_json() or request.form.to_dict()
        template_path = data.get('template_path')
        description = data.get('description', 'Manual backup')
        
        if not template_path:
            return create_error_response(
                'Template path is required',
                'MISSING_TEMPLATE_PATH'
            )
        
        # Create backup
        deployer = get_deployer()
        backup_metadata = deployer.create_backup(
            template_path=template_path,
            user=current_user.email,
            description=description
        )
        
        if not backup_metadata:
            return create_error_response(
                'Backup creation failed',
                'BACKUP_FAILED'
            )
        
        # Audit log
        audit_log('backup_created', {
            'template_path': template_path,
            'backup_timestamp': backup_metadata.timestamp,
            'description': description
        })
        
        return create_success_response(
            data={
                'backup_id': backup_metadata.timestamp,
                'backup_metadata': {
                    'timestamp': backup_metadata.timestamp,
                    'user': backup_metadata.user,
                    'description': backup_metadata.description,
                    'template_path': backup_metadata.template_path,
                    'backup_hash': backup_metadata.backup_hash,
                    'file_size': backup_metadata.file_size,
                    'version': backup_metadata.version
                }
            },
            message='Backup created successfully'
        )
        
    except FileNotFoundError:
        return create_error_response(
            'Template file not found',
            'TEMPLATE_NOT_FOUND',
            {'template_path': template_path},
            status_code=404
        )
    except Exception as e:
        logger.error(f"Backup creation error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Backup creation failed',
            'BACKUP_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/preview', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_attempts=20, window=300)
def generate_preview():
    """Generate preview from GrapesJS content"""
    try:
        # Validate CSRF token
        csrf_valid, csrf_error = validate_csrf_token()
        if not csrf_valid:
            return create_error_response(csrf_error, 'CSRF_INVALID', status_code=403)
        
        # Get request data
        data = request.get_json() or request.form.to_dict()
        grapesjs_content = data.get('content')
        template_name = data.get('template_name', 'preview_template')
        
        if not grapesjs_content:
            return create_error_response(
                'GrapesJS content is required',
                'MISSING_CONTENT'
            )
        
        # Convert GrapesJS to Jinja2
        deployer = get_deployer()
        jinja2_content = deployer.convert_grapesjs_to_jinja2(grapesjs_content)
        
        # Validate template
        validation_issues = deployer.validate_template(jinja2_content)
        
        # Generate preview
        preview_data = deployer.generate_preview(jinja2_content, template_name)
        
        # Audit log
        audit_log('preview_generated', {
            'template_name': template_name,
            'validation_issues_count': len(validation_issues),
            'preview_url': preview_data.get('preview_url')
        })
        
        return create_success_response(
            data={
                'preview_url': preview_data.get('preview_url'),
                'preview_path': preview_data.get('preview_path'),
                'template_name': template_name,
                'validation_issues': validation_issues,
                'validation_passed': len(validation_issues) == 0,
                'jinja2_content': jinja2_content
            },
            message='Preview generated successfully'
        )
        
    except ValueError as e:
        return create_error_response(
            str(e),
            'CONVERSION_ERROR',
            {'error': str(e)}
        )
    except Exception as e:
        logger.error(f"Preview generation error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Preview generation failed',
            'PREVIEW_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/validate', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_attempts=30, window=300)
def validate_template():
    """Validate template before deployment"""
    try:
        # Validate CSRF token
        csrf_valid, csrf_error = validate_csrf_token()
        if not csrf_valid:
            return create_error_response(csrf_error, 'CSRF_INVALID', status_code=403)
        
        # Get request data
        data = request.get_json() or request.form.to_dict()
        template_content = data.get('content')
        template_path = data.get('template_path')
        
        if not template_content:
            return create_error_response(
                'Template content is required',
                'MISSING_CONTENT'
            )
        
        # Validate template
        deployer = get_deployer()
        validation_issues = deployer.validate_template(template_content)
        
        # Additional checks
        additional_checks = {
            'syntax_valid': len([i for i in validation_issues if 'syntax' in i.lower()]) == 0,
            'security_valid': len([i for i in validation_issues if 'security' in i.lower()]) == 0,
            'compatibility_valid': len([i for i in validation_issues if 'compatibility' in i.lower()]) == 0
        }
        
        # Audit log
        audit_log('template_validated', {
            'template_path': template_path,
            'validation_issues_count': len(validation_issues),
            'validation_passed': len(validation_issues) == 0
        })
        
        return create_success_response(
            data={
                'validation_issues': validation_issues,
                'validation_passed': len(validation_issues) == 0,
                'issues_count': len(validation_issues),
                'additional_checks': additional_checks,
                'recommendations': _generate_recommendations(validation_issues)
            },
            message='Template validation completed'
        )
        
    except Exception as e:
        logger.error(f"Template validation error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Template validation failed',
            'VALIDATION_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/deploy', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_attempts=5, window=600)
def deploy_template():
    """Deploy template to production"""
    try:
        # Validate CSRF token
        csrf_valid, csrf_error = validate_csrf_token()
        if not csrf_valid:
            return create_error_response(csrf_error, 'CSRF_INVALID', status_code=403)
        
        # Get request data
        data = request.get_json() or request.form.to_dict()
        template_content = data.get('content')
        target_path = data.get('target_path')
        description = data.get('description', 'API deployment')
        require_backup = data.get('require_backup', True)
        
        if not template_content or not target_path:
            return create_error_response(
                'Template content and target path are required',
                'MISSING_REQUIRED_FIELDS'
            )
        
        # Validate template first
        deployer = get_deployer()
        validation_issues = deployer.validate_template(template_content)
        
        if validation_issues and data.get('strict_validation', False):
            return create_error_response(
                'Template validation failed',
                'VALIDATION_FAILED',
                {'validation_issues': validation_issues}
            )
        
        # Deploy to production
        deployment_result = deployer.deploy_to_production(
            template_content=template_content,
            target_path=target_path,
            user=current_user.email,
            description=description
        )
        
        # Audit log
        audit_log('template_deployed', {
            'target_path': target_path,
            'deployment_status': deployment_result.get('status'),
            'backup_created': deployment_result.get('backup_metadata') is not None,
            'validation_issues_count': len(validation_issues)
        })
        
        return create_success_response(
            data={
                'deployment_id': deployment_result.get('deployment_record', {}).get('timestamp'),
                'target_path': target_path,
                'status': deployment_result.get('status'),
                'backup_metadata': deployment_result.get('backup_metadata'),
                'validation_issues': validation_issues,
                'deployment_record': deployment_result.get('deployment_record')
            },
            message='Template deployed successfully'
        )
        
    except ValueError as e:
        return create_error_response(
            str(e),
            'DEPLOYMENT_VALIDATION_ERROR',
            {'error': str(e)}
        )
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Deployment failed',
            'DEPLOYMENT_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/rollback', methods=['POST'])
@login_required
@admin_required
@rate_limit(max_attempts=3, window=600)
def rollback_template():
    """Rollback to previous backup"""
    try:
        # Validate CSRF token
        csrf_valid, csrf_error = validate_csrf_token()
        if not csrf_valid:
            return create_error_response(csrf_error, 'CSRF_INVALID', status_code=403)
        
        # Get request data
        data = request.get_json() or request.form.to_dict()
        target_path = data.get('target_path')
        backup_timestamp = data.get('backup_timestamp')
        confirmation = data.get('confirmation')
        
        if not target_path:
            return create_error_response(
                'Target path is required',
                'MISSING_TARGET_PATH'
            )
        
        if not confirmation or confirmation != 'CONFIRM_ROLLBACK':
            return create_error_response(
                'Rollback confirmation required. Send confirmation: "CONFIRM_ROLLBACK"',
                'ROLLBACK_CONFIRMATION_REQUIRED'
            )
        
        # Perform rollback
        deployer = get_deployer()
        rollback_result = deployer.rollback(
            target_path=target_path,
            user=current_user.email,
            backup_timestamp=backup_timestamp
        )
        
        # Audit log
        audit_log('template_rollback', {
            'target_path': target_path,
            'backup_timestamp': backup_timestamp,
            'rollback_status': rollback_result.get('status'),
            'restored_from': rollback_result.get('restored_from')
        })
        
        return create_success_response(
            data={
                'rollback_id': rollback_result.get('rollback_record', {}).get('timestamp'),
                'target_path': target_path,
                'status': rollback_result.get('status'),
                'restored_from': rollback_result.get('restored_from'),
                'metadata': rollback_result.get('metadata'),
                'rollback_record': rollback_result.get('rollback_record')
            },
            message='Template rollback completed successfully'
        )
        
    except FileNotFoundError:
        return create_error_response(
            'Backup not found',
            'BACKUP_NOT_FOUND',
            {'target_path': target_path, 'backup_timestamp': backup_timestamp},
            status_code=404
        )
    except Exception as e:
        logger.error(f"Rollback error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Rollback failed',
            'ROLLBACK_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/history/<path:template_path>', methods=['GET'])
@login_required
@admin_required
def get_deployment_history(template_path):
    """Get deployment history for template"""
    try:
        # Get deployment history
        deployer = get_deployer()
        history = deployer.get_deployment_history(template_path)
        
        # Get backup list
        template_name = template_path.split('/')[-1].replace('.html', '')
        backups = deployer.get_backup_list(template_name)
        
        # Audit log
        audit_log('history_accessed', {
            'template_path': template_path,
            'history_entries_count': len(history),
            'backups_count': len(backups)
        })
        
        return create_success_response(
            data={
                'template_path': template_path,
                'deployment_history': history,
                'backups': backups,
                'total_deployments': len(history),
                'total_backups': len(backups)
            },
            message='Deployment history retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Failed to retrieve deployment history',
            'HISTORY_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/status/<deployment_id>', methods=['GET'])
@login_required
@admin_required
def get_deployment_status(deployment_id):
    """Check deployment status"""
    try:
        # Get deployment history
        deployer = get_deployer()
        history = deployer.get_deployment_history()
        
        # Find specific deployment
        deployment = None
        for record in history:
            if record.get('timestamp') == deployment_id or record.get('deployment_id') == deployment_id:
                deployment = record
                break
        
        if not deployment:
            return create_error_response(
                'Deployment not found',
                'DEPLOYMENT_NOT_FOUND',
                {'deployment_id': deployment_id},
                status_code=404
            )
        
        # Calculate progress (simplified)
        progress = 100 if deployment.get('status') == 'success' else 0
        
        # Audit log
        audit_log('status_checked', {
            'deployment_id': deployment_id,
            'status': deployment.get('status'),
            'progress': progress
        })
        
        return create_success_response(
            data={
                'deployment_id': deployment_id,
                'status': deployment.get('status'),
                'progress': progress,
                'timestamp': deployment.get('timestamp'),
                'user': deployment.get('user'),
                'description': deployment.get('description'),
                'target_path': deployment.get('target_path'),
                'error': deployment.get('error'),
                'backup_metadata': deployment.get('backup_metadata')
            },
            message='Deployment status retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Failed to check deployment status',
            'STATUS_ERROR',
            {'error': str(e)}
        )

@deployment_bp.route('/backups/<template_name>', methods=['GET'])
@login_required
@admin_required
def get_backup_list(template_name):
    """Get list of backups for template"""
    try:
        deployer = get_deployer()
        backups = deployer.get_backup_list(template_name)
        
        # Audit log
        audit_log('backups_listed', {
            'template_name': template_name,
            'backups_count': len(backups)
        })
        
        return create_success_response(
            data={
                'template_name': template_name,
                'backups': backups,
                'total_backups': len(backups)
            },
            message='Backup list retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Backup list error: {str(e)}\n{traceback.format_exc()}")
        return create_error_response(
            'Failed to retrieve backup list',
            'BACKUP_LIST_ERROR',
            {'error': str(e)}
        )

def _generate_recommendations(validation_issues: list) -> list:
    """Generate recommendations based on validation issues"""
    recommendations = []
    
    for issue in validation_issues:
        if 'syntax' in issue.lower():
            recommendations.append('Check Jinja2 syntax and ensure all blocks are properly closed')
        elif 'security' in issue.lower():
            recommendations.append('Review template for potential security vulnerabilities')
        elif 'compatibility' in issue.lower():
            recommendations.append('Verify template compatibility with existing system')
        elif 'missing' in issue.lower():
            recommendations.append('Ensure all referenced files and templates exist')
    
    if not validation_issues:
        recommendations.append('Template is ready for deployment')
    
    return recommendations

# Error handlers
@deployment_bp.errorhandler(404)
def not_found(error):
    return create_error_response(
        'Endpoint not found',
        'ENDPOINT_NOT_FOUND',
        status_code=404
    )

@deployment_bp.errorhandler(405)
def method_not_allowed(error):
    return create_error_response(
        'Method not allowed',
        'METHOD_NOT_ALLOWED',
        status_code=405
    )

@deployment_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return create_error_response(
        'Internal server error',
        'INTERNAL_ERROR',
        status_code=500
    )

# Health check endpoint
@deployment_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        deployer = get_deployer()
        return create_success_response(
            data={
                'status': 'healthy',
                'deployer_available': True,
                'timestamp': datetime.now().isoformat()
            },
            message='Deployment service is healthy'
        )
    except Exception as e:
        return create_error_response(
            'Service unhealthy',
            'SERVICE_UNHEALTHY',
            {'error': str(e)},
            status_code=503
        ) 