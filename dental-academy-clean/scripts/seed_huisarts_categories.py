#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed Domain Categories for Huisarts profession
Maps question categories to domain categories
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from models import db, DomainCategory
from datetime import datetime
import argparse

# 8 Domain Categories for Huisarts
HUISARTS_CATEGORIES = [
    {
        'name': 'Internal Medicine',
        'name_nl': 'Interne Geneeskunde',
        'description': 'Internal medicine, cardiology, endocrinology, and related specialties',
        'icon': '❤️',  # Heart
        'color': '#dc3545',  # Red
        'order': 1,
        'question_categories': [
            'Internal Medicine',
            'Cardiology',
            'Endocrinology',
            'Gastroenterology',
            'Nephrology',
            'Rheumatology'
        ]
    },
    {
        'name': 'Basic Medical Sciences',
        'name_nl': 'Basiswetenschappen',
        'description': 'Anatomy, physiology, pathology, and biochemistry',
        'icon': '🧬',  # DNA
        'color': '#6f42c1',  # Purple
        'order': 2,
        'question_categories': [
            'Anatomy',
            'Physiology',
            'Pathology',
            'Biochemistry',
            'Microbiology'
        ]
    },
    {
        'name': 'Pharmacology & Therapeutics',
        'name_nl': 'Farmacologie',
        'description': 'Pharmacology and clinical therapeutics',
        'icon': '💊',  # Pill
        'color': '#28a745',  # Green
        'order': 3,
        'question_categories': [
            'Pharmacology'
        ]
    },
    {
        'name': 'Surgery & Procedures',
        'name_nl': 'Chirurgie',
        'description': 'Surgical specialties and procedures',
        'icon': '🔪',  # Knife (surgery)
        'color': '#fd7e14',  # Orange
        'order': 4,
        'question_categories': [
            'Surgery',
            'Orthopedics',
            'Urology'
        ]
    },
    {
        'name': 'Pediatrics & Women\'s Health',
        'name_nl': 'Kindergeneeskunde & Vrouwengezondheid',
        'description': 'Pediatrics, gynecology, and obstetrics',
        'icon': '👶',  # Baby
        'color': '#e83e8c',  # Pink
        'order': 5,
        'question_categories': [
            'Pediatrics',
            'Gynecology and Obstetrics'
        ]
    },
    {
        'name': 'Neurology & Mental Health',
        'name_nl': 'Neurologie & Geestelijke Gezondheid',
        'description': 'Neurology, psychiatry, and psychology',
        'icon': '🧠',  # Brain
        'color': '#17a2b8',  # Cyan
        'order': 6,
        'question_categories': [
            'Neurology',
            'Psychiatry',
            'Psychology'
        ]
    },
    {
        'name': 'Diagnostics & Emergency',
        'name_nl': 'Diagnostiek & Spoedeisende Hulp',
        'description': 'Epidemiology, emergency medicine, and infectious diseases',
        'icon': '🚨',  # Emergency
        'color': '#ffc107',  # Yellow
        'order': 7,
        'question_categories': [
            'Epidemiology',
            'Emergency Medicine',
            'Infectious Diseases'
        ]
    },
    {
        'name': 'Dermatology & Sensory Systems',
        'name_nl': 'Dermatologie & Zintuiglijke Systemen',
        'description': 'Dermatology, ophthalmology, and ENT',
        'icon': '👁️',  # Eye
        'color': '#20c997',  # Teal
        'order': 8,
        'question_categories': [
            'Dermatology',
            'Ophthalmology',
            'Otolaryngology'
        ]
    }
]


def seed_huisarts_categories(dry_run=True):
    """Create domain categories for Huisarts profession"""
    
    with app.app_context():
        print("\n" + "="*50)
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be saved")
        else:
            print("🚀 CREATING HUISARTS CATEGORIES")
        print("="*50 + "\n")
        
        stats = {
            'categories_created': 0,
            'categories_updated': 0,
            'categories_total': len(HUISARTS_CATEGORIES)
        }
        
        for cat_data in HUISARTS_CATEGORIES:
            # Check if category exists
            category = DomainCategory.query.filter_by(
                name=cat_data['name'],
                profession='huisarts'
            ).first()
            
            if category:
                print(f"📝 Updating: {cat_data['name']}")
                # Update existing
                category.name_nl = cat_data['name_nl']
                category.description = cat_data['description']
                category.icon = cat_data['icon']
                category.color = cat_data['color']
                category.order = cat_data['order']
                stats['categories_updated'] += 1
            else:
                print(f"✨ Creating: {cat_data['name']}")
                # Create new
                category = DomainCategory(
                    name=cat_data['name'],
                    name_nl=cat_data['name_nl'],
                    description=cat_data['description'],
                    icon=cat_data['icon'],
                    color=cat_data['color'],
                    profession='huisarts',
                    order=cat_data['order']
                )
                db.session.add(category)
                stats['categories_created'] += 1
            
            # Show mapped question categories
            print(f"   📋 Question categories: {len(cat_data['question_categories'])}")
            for qcat in cat_data['question_categories']:
                print(f"      - {qcat}")
            print()
        
        if not dry_run:
            db.session.commit()
            print("💾 Changes saved to database!\n")
        else:
            db.session.rollback()
            print("⚠️  Changes NOT saved (dry run mode)\n")
        
        # Print statistics
        print("="*50)
        print("📊 SUMMARY")
        print("="*50)
        print(f"Total categories: {stats['categories_total']}")
        print(f"Created: {stats['categories_created']}")
        print(f"Updated: {stats['categories_updated']}")
        
        if not dry_run:
            print("\n✅ HUISARTS CATEGORIES READY!")
        else:
            print("\n⚠️  Run with --commit to save changes")
        print("="*50 + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed Huisarts domain categories')
    parser.add_argument('--commit', action='store_true', help='Actually save changes to database')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Preview changes without saving (default)')
    
    args = parser.parse_args()
    
    # If --commit is passed, dry_run is False
    dry_run = not args.commit
    
    seed_huisarts_categories(dry_run=dry_run)







