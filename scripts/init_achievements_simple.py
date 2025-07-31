#!/usr/bin/env python3
"""
Simple Achievement Initialization Script
"""

import sys
import os
from datetime import datetime, date, timedelta

# Add the parent directory to the path so we can import from our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import Achievement

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

def main():
    """Main initialization function"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Initializing Achievement System...")
        print("=" * 50)
        
        # Create database tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        # Initialize achievements
        init_achievements()
        
        print("\n" + "=" * 50)
        print("✅ Achievement system initialized!")
        print("\nNext steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Create a user account through registration")
        print("3. Visit /dashboard to see the enhanced dashboard")
        print("4. Check /dashboard/achievements for achievements")

if __name__ == '__main__':
    main() 