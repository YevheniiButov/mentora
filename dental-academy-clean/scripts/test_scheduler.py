#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for diagnostic reassessment scheduler
Тестовый скрипт для планировщика напоминаний о переоценке
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from utils.scheduler_service import diagnostic_scheduler
from datetime import datetime, timedelta, timezone, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scheduler_functionality():
    """Test scheduler functionality"""
    
    with app.app_context():
        try:
            logger.info("🧪 Testing Diagnostic Reassessment Scheduler...")
            
            # Test 1: Get scheduler stats
            logger.info("\n=== Test 1: Scheduler Statistics ===")
            stats = diagnostic_scheduler.get_scheduler_stats()
            logger.info(f"Scheduler stats: {stats}")
            
            # Test 2: Check for reminders
            logger.info("\n=== Test 2: Check for Reminders ===")
            reminder_stats = diagnostic_scheduler.check_diagnostic_reminders()
            logger.info(f"Reminder check results: {reminder_stats}")
            
            # Test 3: Analyze existing plans
            logger.info("\n=== Test 3: Analyze Existing Plans ===")
            
            # Get all active plans
            active_plans = PersonalLearningPlan.query.filter_by(status='active').all()
            logger.info(f"Total active plans: {len(active_plans)}")
            
            # Analyze plans with diagnostic dates
            plans_with_dates = [p for p in active_plans if p.next_diagnostic_date]
            logger.info(f"Plans with diagnostic dates: {len(plans_with_dates)}")
            
            today = date.today()
            
            # Categorize plans
            upcoming_plans = []
            overdue_plans = []
            today_reminders = []
            
            for plan in plans_with_dates:
                days_until = (plan.next_diagnostic_date - today).days
                
                if days_until > 0:
                    upcoming_plans.append({
                        'plan_id': plan.id,
                        'user_id': plan.user_id,
                        'days_until': days_until,
                        'diagnostic_date': plan.next_diagnostic_date
                    })
                elif days_until < 0:
                    overdue_plans.append({
                        'plan_id': plan.id,
                        'user_id': plan.user_id,
                        'days_overdue': abs(days_until),
                        'diagnostic_date': plan.next_diagnostic_date
                    })
                else:
                    today_reminders.append({
                        'plan_id': plan.id,
                        'user_id': plan.user_id,
                        'diagnostic_date': plan.next_diagnostic_date
                    })
            
            logger.info(f"Upcoming diagnostics: {len(upcoming_plans)}")
            logger.info(f"Overdue diagnostics: {len(overdue_plans)}")
            logger.info(f"Today reminders: {len(today_reminders)}")
            
            # Show sample upcoming plans
            if upcoming_plans:
                logger.info("\nSample upcoming diagnostics:")
                for plan in upcoming_plans[:5]:
                    user = User.query.get(plan['user_id'])
                    user_name = user.get_display_name() if user else f"User {plan['user_id']}"
                    logger.info(f"  - {user_name}: {plan['days_until']} days until {plan['diagnostic_date']}")
            
            # Show sample overdue plans
            if overdue_plans:
                logger.info("\nSample overdue diagnostics:")
                for plan in overdue_plans[:5]:
                    user = User.query.get(plan['user_id'])
                    user_name = user.get_display_name() if user else f"User {plan['user_id']}"
                    logger.info(f"  - {user_name}: {plan['days_overdue']} days overdue since {plan['diagnostic_date']}")
            
            # Test 4: Test reminder intervals
            logger.info("\n=== Test 4: Reminder Intervals ===")
            intervals = diagnostic_scheduler.reminder_intervals
            logger.info(f"Current intervals: {intervals}")
            
            # Calculate reminder dates
            first_reminder_date = today + timedelta(days=intervals['first_reminder'])
            second_reminder_date = today + timedelta(days=intervals['second_reminder'])
            final_reminder_date = today + timedelta(days=intervals['final_reminder'])
            
            logger.info(f"First reminder date: {first_reminder_date}")
            logger.info(f"Second reminder date: {second_reminder_date}")
            logger.info(f"Final reminder date: {final_reminder_date}")
            
            # Test 5: Check specific user plans
            logger.info("\n=== Test 5: User-Specific Analysis ===")
            
            # Get a sample user with active plan
            sample_plan = PersonalLearningPlan.query.filter_by(status='active').first()
            if sample_plan:
                user = User.query.get(sample_plan.user_id)
                logger.info(f"Sample user: {user.get_display_name() if user else f'User {sample_plan.user_id}'}")
                logger.info(f"Plan ID: {sample_plan.id}")
                logger.info(f"Next diagnostic date: {sample_plan.next_diagnostic_date}")
                logger.info(f"Current ability: {sample_plan.current_ability}")
                logger.info(f"Target ability: {sample_plan.target_ability}")
                logger.info(f"Progress: {sample_plan.overall_progress}%")
                
                if sample_plan.next_diagnostic_date:
                    days_until = (sample_plan.next_diagnostic_date - today).days
                    logger.info(f"Days until diagnostic: {days_until}")
                    
                    if days_until > 0:
                        if days_until == intervals['first_reminder']:
                            logger.info("  -> Should receive FIRST reminder")
                        elif days_until == intervals['second_reminder']:
                            logger.info("  -> Should receive SECOND reminder")
                        elif days_until == intervals['final_reminder']:
                            logger.info("  -> Should receive FINAL reminder")
                        else:
                            logger.info("  -> No reminder scheduled")
                    else:
                        logger.info("  -> OVERDUE - should receive overdue reminder")
            
            # Test 6: Test notification system integration
            logger.info("\n=== Test 6: Notification System Integration ===")
            
            # Check if notification system is available
            try:
                from utils.notification_system import LearningNotificationSystem
                notification_system = LearningNotificationSystem()
                logger.info("✅ Notification system is available")
                
                # Check email templates
                templates = notification_system.email_templates
                logger.info(f"Available templates: {list(templates.keys())}")
                
                if 'diagnostic_reminder' in templates:
                    logger.info("✅ Diagnostic reminder template is available")
                else:
                    logger.warning("❌ Diagnostic reminder template is missing")
                    
                if 'diagnostic_overdue' in templates:
                    logger.info("✅ Diagnostic overdue template is available")
                else:
                    logger.warning("❌ Diagnostic overdue template is missing")
                    
            except ImportError as e:
                logger.error(f"❌ Notification system not available: {e}")
            
            logger.info("\n✅ All tests completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}", exc_info=True)
            return False

def create_test_plan():
    """Create a test plan for testing"""
    
    with app.app_context():
        try:
            # Get a test user
            test_user = User.query.first()
            if not test_user:
                logger.error("No users found in database")
                return False
            
            # Check if user already has an active plan
            existing_plan = PersonalLearningPlan.query.filter_by(
                user_id=test_user.id,
                status='active'
            ).first()
            
            if existing_plan:
                logger.info(f"User {test_user.id} already has an active plan: {existing_plan.id}")
                return True
            
            # Create a test plan
            from datetime import date, timedelta
            
            test_plan = PersonalLearningPlan(
                user_id=test_user.id,
                status='active',
                current_ability=0.3,
                target_ability=0.7,
                overall_progress=25.0,
                next_diagnostic_date=date.today() + timedelta(days=5),  # 5 days from now
                study_hours_per_week=20.0
            )
            
            db.session.add(test_plan)
            db.session.commit()
            
            logger.info(f"✅ Created test plan {test_plan.id} for user {test_user.id}")
            logger.info(f"Next diagnostic date: {test_plan.next_diagnostic_date}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create test plan: {e}")
            return False

def main():
    """Main function"""
    logger.info("🚀 Starting Scheduler Tests...")
    
    # Create test plan if needed
    logger.info("\n=== Creating Test Plan ===")
    create_test_plan()
    
    # Run tests
    success = test_scheduler_functionality()
    
    if success:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.error("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 