#!/usr/bin/env python3
"""
Template Protection System for automated_practice.html
This script protects the critical learning template from modifications.
"""

import os
import shutil
import hashlib
import json
from datetime import datetime
from pathlib import Path

class TemplateProtection:
    def __init__(self, template_path, backup_dir="protected_templates"):
        self.template_path = Path(template_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.protected_file = self.backup_dir / "automated_practice_protected.html"
        self.checksum_file = self.backup_dir / "template_checksums.json"
        self.load_checksums()
    
    def load_checksums(self):
        """Load existing checksums from file"""
        if self.checksum_file.exists():
            with open(self.checksum_file, 'r', encoding='utf-8') as f:
                self.checksums = json.load(f)
        else:
            self.checksums = {}
    
    def save_checksums(self):
        """Save checksums to file"""
        with open(self.checksum_file, 'w', encoding='utf-8') as f:
            json.dump(self.checksums, f, indent=2)
    
    def calculate_checksum(self, file_path):
        """Calculate SHA256 checksum of file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def create_protected_backup(self):
        """Create a protected backup of the template"""
        if not self.template_path.exists():
            print(f"❌ Template not found: {self.template_path}")
            return False
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"automated_practice_backup_{timestamp}.html"
        
        # Copy template to backup
        shutil.copy2(self.template_path, backup_file)
        
        # Create protected version
        shutil.copy2(self.template_path, self.protected_file)
        
        # Calculate and store checksums
        original_checksum = self.calculate_checksum(self.template_path)
        protected_checksum = self.calculate_checksum(self.protected_file)
        
        self.checksums['original'] = original_checksum
        self.checksums['protected'] = protected_checksum
        self.checksums['last_backup'] = timestamp
        self.checksums['backup_file'] = str(backup_file)
        
        self.save_checksums()
        
        print(f"✅ Protected backup created: {backup_file}")
        print(f"✅ Protected template saved: {self.protected_file}")
        return True
    
    def restore_template(self):
        """Restore template from protected backup"""
        if not self.protected_file.exists():
            print(f"❌ Protected template not found: {self.protected_file}")
            return False
        
        # Create backup of current template before restoration
        if self.template_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = self.backup_dir / f"current_template_backup_{timestamp}.html"
            shutil.copy2(self.template_path, current_backup)
            print(f"📁 Current template backed up to: {current_backup}")
        
        # Restore from protected version
        shutil.copy2(self.protected_file, self.template_path)
        
        # Verify restoration
        current_checksum = self.calculate_checksum(self.template_path)
        protected_checksum = self.checksums.get('protected', '')
        
        if current_checksum == protected_checksum:
            print("✅ Template successfully restored from protected backup")
            return True
        else:
            print("❌ Template restoration failed - checksum mismatch")
            return False
    
    def verify_template_integrity(self):
        """Verify that template hasn't been modified"""
        if not self.template_path.exists():
            print(f"❌ Template not found: {self.template_path}")
            return False
        
        current_checksum = self.calculate_checksum(self.template_path)
        original_checksum = self.checksums.get('original', '')
        protected_checksum = self.checksums.get('protected', '')
        
        if current_checksum == original_checksum:
            print("✅ Template integrity verified - no changes detected")
            return True
        elif current_checksum == protected_checksum:
            print("✅ Template matches protected version")
            return True
        else:
            print("⚠️  Template has been modified!")
            print(f"   Current:  {current_checksum[:16]}...")
            print(f"   Original: {original_checksum[:16]}...")
            print(f"   Protected: {protected_checksum[:16]}...")
            return False
    
    def auto_restore_if_modified(self):
        """Automatically restore template if it has been modified"""
        if not self.verify_template_integrity():
            print("🔄 Auto-restoring template from protected backup...")
            return self.restore_template()
        return True
    
    def add_protection_header(self):
        """Add protection header to the template"""
        if not self.template_path.exists():
            return False
        
        # Read current template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if protection header already exists
        if "<!-- PROTECTED TEMPLATE - DO NOT MODIFY -->" in content:
            print("✅ Protection header already exists")
            return True
        
        # Add protection header at the top
        protection_header = """<!-- PROTECTED TEMPLATE - DO NOT MODIFY -->
<!-- This template is protected by template_protection.py -->
<!-- Any modifications will be automatically reverted -->
<!-- Last protected: {timestamp} -->
<!-- Checksum: {checksum} -->

""".format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            checksum=self.checksums.get('protected', 'unknown')[:16]
        )
        
        # Insert protection header after DOCTYPE
        if content.startswith('<!DOCTYPE'):
            lines = content.split('\n')
            lines.insert(1, protection_header)
            new_content = '\n'.join(lines)
        else:
            new_content = protection_header + content
        
        # Write back to file
        with open(self.template_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Protection header added to template")
        return True

def main():
    """Main function to set up template protection"""
    template_path = "templates/learning/automated_practice.html"
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return
    
    protection = TemplateProtection(template_path)
    
    print("🛡️  Setting up template protection...")
    
    # Create protected backup
    if protection.create_protected_backup():
        print("✅ Protected backup created successfully")
    else:
        print("❌ Failed to create protected backup")
        return
    
    # Add protection header
    if protection.add_protection_header():
        print("✅ Protection header added")
    else:
        print("❌ Failed to add protection header")
    
    # Verify integrity
    if protection.verify_template_integrity():
        print("✅ Template protection setup complete")
    else:
        print("⚠️  Template protection setup completed with warnings")

if __name__ == "__main__":
    main()



