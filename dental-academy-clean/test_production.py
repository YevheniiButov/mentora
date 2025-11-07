#!/usr/bin/env python3
"""
Production Environment Test Script
Tests critical functionality before deployment
"""

import os
import sys
import requests
from datetime import datetime

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔧 Testing environment variables...")
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_database_connection():
    """Test database connection"""
    print("🗄️ Testing database connection...")
    
    try:
        from run_local import app
        from models import db, User
        
        with app.app_context():
            # Test basic query
            user_count = User.query.count()
            print(f"✅ Database connected. Users in database: {user_count}")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_static_files():
    """Test that all required static files exist"""
    print("📁 Testing static files...")
    
    required_files = [
        'static/animations/flame.json',
        'static/animations/fist.json', 
        'static/animations/arm.json',
        'static/animations/brain.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing static files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required static files present")
        return True

def test_learning_plan_data():
    """Test that learning plan data is properly initialized"""
    print("📊 Testing learning plan data...")
    
    try:
        from run_local import app
        from models import User, PersonalLearningPlan
        
        with app.app_context():
            # Get first user
            user = User.query.first()
            if not user:
                print("❌ No users found in database")
                return False
            
            # Check learning plan
            plan = PersonalLearningPlan.query.filter_by(user_id=user.id).first()
            if not plan:
                print("❌ No learning plan found for user")
                return False
            
            # Check that plan has proper values (not all None)
            if (plan.overall_progress is not None and 
                plan.time_invested is not None and 
                plan.retention_rate is not None):
                print(f"✅ Learning plan data OK: progress={plan.overall_progress}%, time={plan.time_invested}min")
                return True
            else:
                print("❌ Learning plan has null values")
                return False
                
    except Exception as e:
        print(f"❌ Learning plan test failed: {e}")
        return False

def test_domain_categories():
    """Test that domain categories are properly seeded"""
    print("🏷️ Testing domain categories...")
    
    try:
        from run_local import app
        from models import DomainCategory
        
        with app.app_context():
            # Check tandarts categories
            tandarts_cats = DomainCategory.query.filter_by(profession='tandarts').count()
            huisarts_cats = DomainCategory.query.filter_by(profession='huisarts').count()
            
            print(f"✅ Domain categories: Tandarts={tandarts_cats}, Huisarts={huisarts_cats}")
            
            if tandarts_cats >= 7 and huisarts_cats >= 8:
                return True
            else:
                print("❌ Insufficient domain categories")
                return False
                
    except Exception as e:
        print(f"❌ Domain categories test failed: {e}")
        return False

def test_question_professions():
    """Test that questions have profession assignments"""
    print("❓ Testing question professions...")
    
    try:
        from run_local import app
        from models import Question
        
        with app.app_context():
            # Check questions with professions
            tandarts_questions = Question.query.filter_by(profession='tandarts').count()
            huisarts_questions = Question.query.filter_by(profession='huisarts').count()
            no_profession = Question.query.filter(Question.profession.is_(None)).count()
            
            print(f"✅ Question professions: Tandarts={tandarts_questions}, Huisarts={huisarts_questions}, None={no_profession}")
            
            if no_profession == 0 and (tandarts_questions > 0 or huisarts_questions > 0):
                return True
            else:
                print("❌ Questions missing profession assignments")
                return False
                
    except Exception as e:
        print(f"❌ Question professions test failed: {e}")
        return False

def test_production_config():
    """Test production configuration"""
    print("⚙️ Testing production configuration...")
    
    try:
        from config import ProductionConfig
        
        config = ProductionConfig()
        
        # Check critical settings
        if config.DEBUG:
            print("❌ DEBUG is enabled in production config")
            return False
        
        if not config.SESSION_COOKIE_SECURE:
            print("❌ SESSION_COOKIE_SECURE is disabled")
            return False
        
        if not config.WTF_CSRF_ENABLED:
            print("❌ CSRF protection is disabled")
            return False
        
        print("✅ Production configuration looks good")
        return True
        
    except Exception as e:
        print(f"❌ Production config test failed: {e}")
        return False

def main():
    """Run all production tests"""
    print("🚀 Mentora Production Environment Test")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_database_connection,
        test_static_files,
        test_learning_plan_data,
        test_domain_categories,
        test_question_professions,
        test_production_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Empty line for readability
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for production deployment.")
        return 0
    else:
        print("⚠️ Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == '__main__':
    sys.exit(main())





