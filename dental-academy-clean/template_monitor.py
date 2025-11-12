#!/usr/bin/env python3
"""
Template Monitor - Monitors and protects the automated_practice.html template
This script runs as a background service to ensure template integrity.
"""

import os
import time
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from template_protection import TemplateProtection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('template_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TemplateMonitor:
    def __init__(self, template_path, check_interval=30):
        self.template_path = Path(template_path)
        self.check_interval = check_interval
        self.protection = TemplateProtection(template_path)
        self.running = False
        self.last_check = None
        
    def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("🛡️  Starting template monitoring...")
        self.running = True
        
        try:
            while self.running:
                self.check_template()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
        finally:
            self.running = False
    
    def check_template(self):
        """Check template integrity and restore if needed"""
        try:
            if not self.template_path.exists():
                logger.warning("⚠️  Template not found, attempting to restore...")
                if self.protection.restore_template():
                    logger.info("✅ Template restored successfully")
                else:
                    logger.error("❌ Failed to restore template")
                return
            
            # Check if template has been modified
            if not self.protection.verify_template_integrity():
                logger.warning("⚠️  Template modification detected, restoring...")
                if self.protection.restore_template():
                    logger.info("✅ Template restored from protected backup")
                else:
                    logger.error("❌ Failed to restore template")
            else:
                logger.debug("✅ Template integrity verified")
            
            self.last_check = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Error checking template: {e}")
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        logger.info("🛑 Stopping template monitoring...")
        self.running = False
    
    def force_restore(self):
        """Force restore template from protected backup"""
        logger.info("🔄 Force restoring template...")
        if self.protection.restore_template():
            logger.info("✅ Template force restored successfully")
            return True
        else:
            logger.error("❌ Failed to force restore template")
            return False
    
    def get_status(self):
        """Get monitoring status"""
        status = {
            'running': self.running,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'template_exists': self.template_path.exists(),
            'protected_backup_exists': self.protection.protected_file.exists(),
            'integrity_ok': False
        }
        
        if self.template_path.exists():
            status['integrity_ok'] = self.protection.verify_template_integrity()
        
        return status

def create_monitor_service():
    """Create a systemd service file for template monitoring"""
    service_content = f"""[Unit]
Description=Template Protection Monitor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path("/etc/systemd/system/template-monitor.service")
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        logger.info(f"✅ Service file created: {service_file}")
        logger.info("To enable the service, run:")
        logger.info("  sudo systemctl daemon-reload")
        logger.info("  sudo systemctl enable template-monitor")
        logger.info("  sudo systemctl start template-monitor")
        
    except PermissionError:
        logger.error("❌ Permission denied. Run with sudo to create service file.")
    except Exception as e:
        logger.error(f"❌ Error creating service file: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Template Protection Monitor')
    parser.add_argument('--template', default='templates/learning/automated_practice.html',
                       help='Path to template file')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds')
    parser.add_argument('--create-service', action='store_true',
                       help='Create systemd service file')
    parser.add_argument('--force-restore', action='store_true',
                       help='Force restore template and exit')
    parser.add_argument('--status', action='store_true',
                       help='Show status and exit')
    
    args = parser.parse_args()
    
    if args.create_service:
        create_monitor_service()
        return
    
    monitor = TemplateMonitor(args.template, args.interval)
    
    if args.force_restore:
        monitor.force_restore()
        return
    
    if args.status:
        status = monitor.get_status()
        print(json.dumps(status, indent=2))
        return
    
    # Start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main()





