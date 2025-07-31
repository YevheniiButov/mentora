#!/usr/bin/env python3
"""
Initialize Achievements and Sample Data for Dashboard
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the parent directory to the path so we can import from our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import (
    User, Achievement, UserAchievement, UserActivity, UserStreak, 
    UserReminder, LearningPath, Subject, Module, Lesson
)

def init_achievements():
    """Initialize achievement templates"""
    
    achievements = [
        # Learning Achievements
        {
            'name': 'Eerste stappen',
            'description': 'Voltooi je eerste les',
            'icon': 'star',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 1,
            'badge_color': 'success',
            'sort_order': 1
        },
        {
            'name': 'Op weg',
            'description': 'Voltooi 5 lessen',
            'icon': 'bookmark-check',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 5,
            'badge_color': 'primary',
            'sort_order': 2
        },
        {
            'name': 'Toegewijde leerling',
            'description': 'Voltooi 10 lessen',
            'icon': 'book',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 10,
            'badge_color': 'primary',
            'sort_order': 3
        },
        {
            'name': 'Lesgever',
            'description': 'Voltooi 25 lessen',
            'icon': 'mortarboard',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 25,
            'badge_color': 'warning',
            'sort_order': 4
        },
        {
            'name': 'Master student',
            'description': 'Voltooi 50 lessen',
            'icon': 'trophy',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 50,
            'badge_color': 'warning',
            'sort_order': 5
        },
        {
            'name': 'Legende',
            'description': 'Voltooi 100 lessen',
            'icon': 'crown',
            'category': 'learning',
            'requirement_type': 'lessons_completed',
            'requirement_value': 100,
            'badge_color': 'warning',
            'sort_order': 6
        },
        
        # Time-based Achievements
        {
            'name': 'Studietijd',
            'description': 'Besteed 1 uur aan leren',
            'icon': 'clock',
            'category': 'time',
            'requirement_type': 'hours_studied',
            'requirement_value': 1,
            'badge_color': 'success',
            'sort_order': 10
        },
        {
            'name': 'Marathonloper',
            'description': 'Besteed 5 uur aan leren',
            'icon': 'stopwatch',
            'category': 'time',
            'requirement_type': 'hours_studied',
            'requirement_value': 5,
            'badge_color': 'primary',
            'sort_order': 11
        },
        {
            'name': 'Tijdmeester',
            'description': 'Besteed 20 uur aan leren',
            'icon': 'alarm',
            'category': 'time',
            'requirement_type': 'hours_studied',
            'requirement_value': 20,
            'badge_color': 'warning',
            'sort_order': 12
        },
        {
            'name': 'Tijd-expert',
            'description': 'Besteed 50 uur aan leren',
            'icon': 'hourglass-split',
            'category': 'time',
            'requirement_type': 'hours_studied',
            'requirement_value': 50,
            'badge_color': 'warning',
            'sort_order': 13
        },
        
        # Streak Achievements
        {
            'name': 'Eerste reeks',
            'description': 'Leer 2 dagen achtereen',
            'icon': 'fire',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 2,
            'badge_color': 'success',
            'sort_order': 20
        },
        {
            'name': 'Consistent',
            'description': 'Leer 7 dagen achtereen',
            'icon': 'calendar-check',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 7,
            'badge_color': 'primary',
            'sort_order': 21
        },
        {
            'name': 'Vastberaden',
            'description': 'Leer 14 dagen achtereen',
            'icon': 'lightning',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 14,
            'badge_color': 'warning',
            'sort_order': 22
        },
        {
            'name': 'Onverslaanbaar',
            'description': 'Leer 30 dagen achtereen',
            'icon': 'shield-check',
            'category': 'streak',
            'requirement_type': 'streak_days',
            'requirement_value': 30,
            'badge_color': 'warning',
            'sort_order': 23
        },
        
        # XP Achievements
        {
            'name': 'XP Verzamelaar',
            'description': 'Verdien 100 XP',
            'icon': 'gem',
            'category': 'xp',
            'requirement_type': 'xp_earned',
            'requirement_value': 100,
            'badge_color': 'success',
            'sort_order': 30
        },
        {
            'name': 'XP Meester',
            'description': 'Verdien 500 XP',
            'icon': 'star-fill',
            'category': 'xp',
            'requirement_type': 'xp_earned',
            'requirement_value': 500,
            'badge_color': 'primary',
            'sort_order': 31
        },
        {
            'name': 'XP Legende',
            'description': 'Verdien 1000 XP',
            'icon': 'award',
            'category': 'xp',
            'requirement_type': 'xp_earned',
            'requirement_value': 1000,
            'badge_color': 'warning',
            'sort_order': 32
        },
        
        # Level Achievements
        {
            'name': 'Level Up!',
            'description': 'Bereik level 5',
            'icon': 'arrow-up-circle',
            'category': 'level',
            'requirement_type': 'level_reached',
            'requirement_value': 5,
            'badge_color': 'primary',
            'sort_order': 40
        },
        {
            'name': 'Veteraan',
            'description': 'Bereik level 10',
            'icon': 'patch-check',
            'category': 'level',
            'requirement_type': 'level_reached',
            'requirement_value': 10,
            'badge_color': 'warning',
            'sort_order': 41
        },
        
        # Special Achievements
        {
            'name': 'Weekendstudent',
            'description': 'Leer in het weekend',
            'icon': 'calendar2-week',
            'category': 'special',
            'requirement_type': 'weekend_study',
            'requirement_value': 1,
            'badge_color': 'success',
            'sort_order': 50
        },
        {
            'name': 'Vroege vogel',
            'description': 'Leer voor 8:00 \'s ochtends',
            'icon': 'sunrise',
            'category': 'special',
            'requirement_type': 'early_bird',
            'requirement_value': 1,
            'badge_color': 'success',
            'sort_order': 51
        },
        {
            'name': 'Nachtbraker',
            'description': 'Leer na 22:00 \'s avonds',
            'icon': 'moon',
            'category': 'special',
            'requirement_type': 'night_owl',
            'requirement_value': 1,
            'badge_color': 'success',
            'sort_order': 52
        }
    ]
    
    print("Creating achievements...")
    for achievement_data in achievements:
        # Check if achievement already exists
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if not existing:
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)
            print(f"  ✓ Created: {achievement_data['name']}")
        else:
            print(f"  - Exists: {achievement_data['name']}")
    
    db.session.commit()
    print(f"\nTotal achievements in database: {Achievement.query.count()}")

def create_sample_reminders(user):
    """Create sample reminders for a user"""
    
    reminders = [
        {
            'title': 'BIG-toets aanmelden',
            'description': 'Vergeet niet je aan te melden voor de BIG-toets',
            'reminder_type': 'exam',
            'reminder_date': datetime.now() + timedelta(days=30)
        },
        {
            'title': 'Module 3 afronden',
            'description': 'Deadline voor het afronden van Module 3',
            'reminder_type': 'deadline',
            'reminder_date': datetime.now() + timedelta(days=7)
        },
        {
            'title': 'Wekelijkse doelen controleren',
            'description': 'Bekijk je voortgang en pas doelen aan',
            'reminder_type': 'general',
            'reminder_date': datetime.now() + timedelta(days=3)
        },
        {
            'title': 'Virtuele patiënt case studie',
            'description': 'Nieuwe case studies beschikbaar',
            'reminder_type': 'general',
            'reminder_date': datetime.now() + timedelta(days=1)
        }
    ]
    
    print(f"\nCreating sample reminders for {user.get_display_name()}...")
    for reminder_data in reminders:
        reminder = UserReminder(user_id=user.id, **reminder_data)
        db.session.add(reminder)
        print(f"  ✓ Created: {reminder_data['title']}")
    
    db.session.commit()

def create_sample_activity(user, days=14):
    """Create sample activity for a user"""
    
    print(f"\nCreating sample activity for {user.get_display_name()}...")
    
    # Create activity for the last `days` days
    for i in range(days):
        activity_date = date.today() - timedelta(days=i)
        
        # Vary the activity levels
        if i < 3:  # Recent days - higher activity
            lessons = 3 + (i % 2)
            time_spent = 45 + (i * 10)
            xp = lessons * 25
        elif i < 7:  # Week ago - moderate activity
            lessons = 1 + (i % 3)
            time_spent = 20 + (i * 5)
            xp = lessons * 20
        else:  # Older days - lower activity
            lessons = 0 if i % 3 == 0 else 1
            time_spent = 15 if lessons > 0 else 0
            xp = lessons * 15
        
        # Skip some days to make it realistic
        if i % 5 == 0 and i > 5:
            continue
            
        activity = UserActivity(
            user_id=user.id,
            activity_date=activity_date,
            lessons_completed=lessons,
            time_spent=time_spent,
            xp_earned=xp,
            modules_accessed=1 if lessons > 0 else 0,
            tests_taken=1 if lessons > 2 else 0,
            virtual_patients_completed=1 if lessons > 3 else 0
        )
        db.session.add(activity)
        
        # Update user XP
        user.xp += xp
        
        print(f"  ✓ Day {activity_date}: {lessons} lessons, {time_spent} min, {xp} XP")
    
    # Create streak
    streak = UserStreak(user_id=user.id, current_streak=5, longest_streak=12)
    db.session.add(streak)
    
    # Update user level based on XP
    user.level = max(1, user.xp // 100)
    
    db.session.commit()
    print(f"  ✓ User level: {user.level}, Total XP: {user.xp}")

def init_sample_data():
    """Initialize sample data for testing"""
    
    # Find a test user or create one
    user = User.query.filter_by(email='test@example.com').first()
    if not user:
        print("Creating test user...")
        user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='Gebruiker',
            is_active=True
        )
        
        # Set only fields that exist in the current schema
        if hasattr(user, 'profession'):
            user.profession = 'tandarts'
        if hasattr(user, 'big_number'):
            user.big_number = '99123456782'
        if hasattr(user, 'workplace'):
            user.workplace = 'Test Tandartspraktijk'
        if hasattr(user, 'registration_completed'):
            user.registration_completed = True
        
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print(f"  ✓ Created test user: {user.get_display_name()}")
    else:
        print(f"Using existing test user: {user.get_display_name()}")
    
    # Create sample activity
    create_sample_activity(user)
    
    # Create sample reminders
    create_sample_reminders(user)
    
    # Award some achievements
    print(f"\nChecking achievements for {user.get_display_name()}...")
    new_achievements = user.check_achievements()
    if new_achievements:
        db.session.commit()
        print(f"  ✓ Awarded {len(new_achievements)} achievements")
        for achievement in new_achievements:
            print(f"    - {achievement.name}")
    else:
        print("  - No new achievements to award")

def main():
    """Main initialization function"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing Dashboard Data...")
        print("=" * 50)
        
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        # Initialize achievements
        init_achievements()
        
        # Create sample data for testing
        print("\n" + "=" * 50)
        print("📊 Creating Sample Data...")
        init_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ Dashboard initialization complete!")
        print("\nYou can now:")
        print("1. Log in with test@example.com / password123")
        print("2. Visit /dashboard to see the enhanced dashboard")
        print("3. Check /dashboard/achievements for achievements")
        print("4. View /dashboard/activity for activity tracking")
        print("5. See /dashboard/reminders for reminders")

if __name__ == '__main__':
    main() 