#!/usr/bin/env python3
"""
Production Startup Script for Mentora
Handles production-specific initialization and validation
"""

import os
import sys
import logging
from datetime import datetime

def setup_logging():
    """Setup production logging"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    log_file = os.environ.get('LOG_FILE', '/var/log/mentora/app.log')
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Mentora production startup at {datetime.now()}")
    return logger

def validate_environment():
    """Validate production environment"""
    logger = logging.getLogger(__name__)
    
    # Check required environment variables
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Check Flask environment
    if os.environ.get('FLASK_ENV') != 'production':
        logger.warning("⚠️ FLASK_ENV is not set to 'production'")
    
    logger.info("✅ Environment validation passed")
    return True

def initialize_database():
    """Initialize database connection and run migrations"""
    logger = logging.getLogger(__name__)
    
    try:
        from run_local import app
        from models import db
        
        with app.app_context():
            # Test database connection
            db.engine.execute('SELECT 1')
            logger.info("✅ Database connection successful")
            
            # Check if migrations are needed
            from flask_migrate import current
            try:
                current_revision = current()
                logger.info(f"📊 Current database revision: {current_revision}")
            except Exception as e:
                logger.warning(f"⚠️ Could not get current revision: {e}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def check_critical_data():
    """Check that critical data is present"""
    logger = logging.getLogger(__name__)
    
    try:
        from run_local import app
        from models import User, DomainCategory, Question, PersonalLearningPlan
        
        with app.app_context():
            # Check users
            user_count = User.query.count()
            logger.info(f"👥 Users in database: {user_count}")
            
            # Check domain categories
            tandarts_cats = DomainCategory.query.filter_by(profession='tandarts').count()
            huisarts_cats = DomainCategory.query.filter_by(profession='huisarts').count()
            logger.info(f"🏷️ Domain categories: Tandarts={tandarts_cats}, Huisarts={huisarts_cats}")
            
            # Check questions
            total_questions = Question.query.count()
            tandarts_questions = Question.query.filter_by(profession='tandarts').count()
            huisarts_questions = Question.query.filter_by(profession='huisarts').count()
            logger.info(f"❓ Questions: Total={total_questions}, Tandarts={tandarts_questions}, Huisarts={huisarts_questions}")
            
            # Check learning plans
            plan_count = PersonalLearningPlan.query.count()
            logger.info(f"📚 Learning plans: {plan_count}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Critical data check failed: {e}")
        return False

def start_application():
    """Start the Flask application"""
    logger = logging.getLogger(__name__)
    
    try:
        from run_local import app
        
        # Get server configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"🔧 Debug mode: {debug}")
        
        # Start the application
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main production startup function"""
    # Setup logging
    logger = setup_logging()
    
    logger.info("🚀 Starting Mentora production application...")
    
    # Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        logger.error("❌ Database initialization failed")
        sys.exit(1)
    
    # Check critical data
    if not check_critical_data():
        logger.error("❌ Critical data check failed")
        sys.exit(1)
    
    logger.info("✅ All checks passed. Starting application...")
    
    # Start the application
    start_application()

if __name__ == '__main__':
    main()








