#!/usr/bin/env python3
"""
Mentora Clean - Application Entry Point
Simple script to run the Flask application
"""

import os
import sys
import logging
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    
    # Get configuration from environment
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Initialize database tables
    with app.app_context():
        try:
            from extensions import db
            db.create_all()
            logger.info("✅ Database tables created/verified")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            sys.exit(1)
    
    # Display startup information
    logger.info(f"🦷 Starting Mentora Clean")
    logger.info(f"🌐 Server: http://{host}:{port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🗄️ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    
    if debug:
        logger.info("📋 Available routes:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
                logger.info(f"  {methods:10} {rule.rule}")
    
    try:
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Application failed to start: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 