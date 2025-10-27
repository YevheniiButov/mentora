#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Seed file for medical terminology flashcard system.
Imports 50 essential medical terms across 5 categories.

Usage:
    python scripts/medical_terms_seed.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from extensions import db
from models.medical_terms import MedicalTerm


# Basic terms data: (dutch_term, english_translation, category)
BASIC_TERMS = [
    # ANATOMY - 10 terms
    ('het hart', 'heart', 'anatomy'),
    ('de long', 'lung', 'anatomy'),
    ('de maag', 'stomach', 'anatomy'),
    ('de lever', 'liver', 'anatomy'),
    ('de nier', 'kidney', 'anatomy'),
    ('het brein', 'brain', 'anatomy'),
    ('het hart', 'heart', 'anatomy'),
    ('het bloedvat', 'blood vessel', 'anatomy'),
    ('de spier', 'muscle', 'anatomy'),
    ('het bot', 'bone', 'anatomy'),
    
    # SYMPTOMS - 10 terms
    ('de pijn', 'pain', 'symptoms'),
    ('de koorts', 'fever', 'symptoms'),
    ('de hoest', 'cough', 'symptoms'),
    ('de hoofdpijn', 'headache', 'symptoms'),
    ('de misselijkheid', 'nausea', 'symptoms'),
    ('het braken', 'vomiting', 'symptoms'),
    ('de diarree', 'diarrhea', 'symptoms'),
    ('de vermoeidheid', 'fatigue', 'symptoms'),
    ('de duizeligheid', 'dizziness', 'symptoms'),
    ('de kortademigheid', 'shortness of breath', 'symptoms'),
    
    # DISEASES - 10 terms
    ('de diabetes', 'diabetes', 'diseases'),
    ('de hypertensie', 'hypertension', 'diseases'),
    ('de pneumonie', 'pneumonia', 'diseases'),
    ('de griep', 'influenza', 'diseases'),
    ('het eczeem', 'eczema', 'diseases'),
    ('de asthma', 'asthma', 'diseases'),
    ('de artritis', 'arthritis', 'diseases'),
    ('de beroerte', 'stroke', 'diseases'),
    ('het hartinfarct', 'heart attack', 'diseases'),
    ('de kanker', 'cancer', 'diseases'),
    
    # TREATMENTS - 10 terms
    ('de behandeling', 'treatment', 'treatments'),
    ('de operatie', 'operation', 'treatments'),
    ('het medicijn', 'medicine', 'treatments'),
    ('het antibioticum', 'antibiotic', 'treatments'),
    ('de injectie', 'injection', 'treatments'),
    ('de pil', 'pill', 'treatments'),
    ('de zalf', 'ointment', 'treatments'),
    ('de fysiotherapie', 'physiotherapy', 'treatments'),
    ('de radiotherapie', 'radiotherapy', 'treatments'),
    ('de chirurgie', 'surgery', 'treatments'),
    
    # DENTAL - 10 terms (important for tandarts users)
    ('de tand', 'tooth', 'dental'),
    ('de kies', 'molar', 'dental'),
    ('de snijtand', 'incisor', 'dental'),
    ('het tandvlees', 'gum', 'dental'),
    ('de cariës', 'cavity', 'dental'),
    ('de parodontitis', 'periodontitis', 'dental'),
    ('de tandborstel', 'toothbrush', 'dental'),
    ('de tandpasta', 'toothpaste', 'dental'),
    ('de vulling', 'filling', 'dental'),
    ('de kroon', 'crown', 'dental'),
]

# Map of categories with descriptions
CATEGORY_DESCRIPTIONS = {
    'anatomy': {
        'description': 'Body structure and organs',
        'difficulty': 2,
        'frequency': 5
    },
    'symptoms': {
        'description': 'Patient symptoms and complaints',
        'difficulty': 1,
        'frequency': 5
    },
    'diseases': {
        'description': 'Medical conditions and diagnoses',
        'difficulty': 3,
        'frequency': 4
    },
    'treatments': {
        'description': 'Medical treatments and procedures',
        'difficulty': 3,
        'frequency': 4
    },
    'dental': {
        'description': 'Dental terminology',
        'difficulty': 2,
        'frequency': 5
    }
}


def translate_term(term, lang='en'):
    """
    Simple translation lookup (demo version).
    In production, this would use a translation API or database.
    """
    translations = {
        'en': {
            'heart': 'heart',
            'lung': 'lung',
            'stomach': 'stomach',
            'liver': 'liver',
            'kidney': 'kidney',
            'brain': 'brain',
            'blood vessel': 'blood vessel',
            'muscle': 'muscle',
            'bone': 'bone',
        }
    }
    
    return translations.get(lang, {}).get(term, term)


def seed_basic_terms(app):
    """
    Import basic medical terms into database.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        print("\n" + "="*70)
        print("🚀 Medical Terminology Seed - Phase 1")
        print("="*70)
        
        # Check for existing terms
        existing_count = MedicalTerm.query.count()
        if existing_count > 0:
            print(f"\n⚠️  Database already has {existing_count} terms!")
            response = input("Continue anyway? (y/n): ").lower()
            if response != 'y':
                print("❌ Seed cancelled")
                return False
        
        print(f"\n📚 Importing {len(BASIC_TERMS)} medical terms...")
        print("-" * 70)
        
        duplicates = set()
        imported = 0
        errors = 0
        
        for dutch_term, english_term, category in BASIC_TERMS:
            try:
                # Check for duplicates
                if dutch_term in duplicates:
                    print(f"⏭️  Skipping duplicate: {dutch_term}")
                    continue
                
                duplicates.add(dutch_term)
                
                # Check if term already exists
                existing = MedicalTerm.query.filter_by(term_nl=dutch_term).first()
                if existing:
                    print(f"✓ Already exists: {dutch_term}")
                    continue
                
                # Get category metadata
                cat_info = CATEGORY_DESCRIPTIONS.get(category, {
                    'description': category,
                    'difficulty': 2,
                    'frequency': 3
                })
                
                # Create new term
                term = MedicalTerm(
                    term_nl=dutch_term,
                    term_en=english_term,
                    definition_nl=cat_info.get('description'),
                    category=category,
                    difficulty=cat_info.get('difficulty', 2),
                    frequency=cat_info.get('frequency', 3)
                )
                
                db.session.add(term)
                imported += 1
                print(f"✅ Imported: {dutch_term} ({english_term})")
                
            except Exception as e:
                print(f"❌ Error importing {dutch_term}: {str(e)}")
                errors += 1
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "="*70)
            print(f"✅ SEED COMPLETED SUCCESSFULLY!")
            print(f"   📊 Imported: {imported} terms")
            print(f"   ⚠️  Errors: {errors}")
            print(f"   📚 Total in database: {MedicalTerm.query.count()}")
            print("="*70 + "\n")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ SEED FAILED: {str(e)}")
            return False


def print_stats(app):
    """Print statistics about imported terms"""
    with app.app_context():
        stats = {}
        
        for category in CATEGORY_DESCRIPTIONS.keys():
            count = MedicalTerm.query.filter_by(category=category).count()
            stats[category] = count
        
        print("\n📊 Statistics by Category:")
        print("-" * 40)
        for category, count in stats.items():
            print(f"   {category.upper():20} {count:3} terms")
        
        total = sum(stats.values())
        print("-" * 40)
        print(f"   {'TOTAL':20} {total:3} terms")
        print()


if __name__ == '__main__':
    # Create Flask app
    app = create_app()
    
    # Run seed
    success = seed_basic_terms(app)
    
    # Print stats
    if success:
        print_stats(app)
        sys.exit(0)
    else:
        sys.exit(1)
