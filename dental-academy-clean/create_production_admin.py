#!/usr/bin/env python3
"""
Script to create an admin user on production
Run this on your production server
"""
import os
import sys

# Add current directory to path
sys.path.append('.')

from app import app
from models import User, db
from werkzeug.security import generate_password_hash

def create_production_admin():
    """Create admin user for production"""
    with app.app_context():
        print("🚀 Creating production admin user...")
        
        # Production admin details
        email = "admin@mentora.com.in"  # Use your production domain
        password = "MentoraAdmin2025!"  # Strong password
        first_name = "Admin"
        last_name = "User"
        
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        
        # Check if admin already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"⚠️  User {email} already exists!")
            
            # Make existing user admin
            if existing_user.role != 'admin':
                existing_user.role = 'admin'
                existing_user.is_active = True
                existing_user.email_confirmed = True
                db.session.commit()
                print(f"✅ User {email} is now an admin!")
            else:
                print(f"✅ User {email} is already an admin!")
            
            # Update password
            existing_user.set_password(password)
            db.session.commit()
            print(f"🔑 Password updated!")
            
        else:
            # Create new admin user
            try:
                admin_user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role='admin',
                    is_active=True,
                    email_confirmed=True,
                    registration_completed=True
                )
                
                # Set password
                admin_user.set_password(password)
                
                # Add to database
                db.session.add(admin_user)
                db.session.commit()
                
                print(f"✅ Production admin created successfully!")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin: {str(e)}")
                return
        
        print(f"\n🌐 Admin access:")
        print(f"   URL: https://www.mentora.com.in/admin/")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change password after first login!")

if __name__ == '__main__':
    create_production_admin()
