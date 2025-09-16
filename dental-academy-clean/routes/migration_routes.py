"""
Routes for database migrations
"""

from flask import Blueprint, jsonify, request
from flask_migrate import upgrade, current, history
from extensions import db
import os

migration_bp = Blueprint('migration', __name__, url_prefix='/migrate')

@migration_bp.route('/status')
def migration_status():
    """Check current migration status"""
    try:
        current_rev = current()
        history_rev = history()
        
        return jsonify({
            'success': True,
            'current_revision': str(current_rev) if current_rev else None,
            'history': [str(rev) for rev in history_rev] if history_rev else [],
            'database_url': os.environ.get('DATABASE_URL', 'Not set')[:20] + '...' if os.environ.get('DATABASE_URL') else 'Not set',
            'timestamp': '2025-09-16-09-00'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@migration_bp.route('/upgrade', methods=['POST'])
def run_migration():
    """Run database migration"""
    try:
        # Проверяем что это продакшен
        if not os.environ.get('DATABASE_URL'):
            return jsonify({
                'success': False,
                'error': 'Not in production environment'
            }), 400
        
        # Применяем миграцию
        upgrade()
        
        return jsonify({
            'success': True,
            'message': 'Migration completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@migration_bp.route('/init', methods=['POST'])
def init_migration():
    """Initialize migration table"""
    try:
        # Проверяем что это продакшен
        if not os.environ.get('DATABASE_URL'):
            return jsonify({
                'success': False,
                'error': 'Not in production environment'
            }), 400
        
        # Инициализируем таблицу миграций
        from flask_migrate import stamp
        stamp()
        
        return jsonify({
            'success': True,
            'message': 'Migration table initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@migration_bp.route('/fix-user-fields', methods=['POST'])
def fix_user_fields():
    """Fix user table field sizes directly"""
    try:
        # Проверяем что это продакшен
        if not os.environ.get('DATABASE_URL'):
            return jsonify({
                'success': False,
                'error': 'Not in production environment'
            }), 400
        
        # Выполняем SQL команды напрямую
        from sqlalchemy import text
        
        with db.engine.connect() as conn:
            # Увеличиваем размер password_hash
            conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(255)"))
            
            # Увеличиваем размер email_confirmation_token
            conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN email_confirmation_token TYPE VARCHAR(255)"))
            
            # Увеличиваем размер password_reset_token
            conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_reset_token TYPE VARCHAR(255)"))
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'User table fields updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
