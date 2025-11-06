#!/usr/bin/env python3
"""
Diagnostic Domains Configuration

This module defines the top areas for Quick Diagnostic Tests for different professions.
- Tandarts: Uses BIG domains (dental specialties)
- Huisarts: Uses categories (medical specialties)
"""

# Quick Test configuration
QUICK_TEST_TOTAL_QUESTIONS = 30
QUICK_TEST_TIME_LIMIT = 20  # minutes
QUICK_TEST_DESCRIPTION = "Snelle diagnostische test - Top 10 belangrijkste gebieden"

# Explanation for different professions
QUICK_TEST_EXPLANATION = {
    'tandarts': 'This test focuses on the 10 most important BIG domains for dentists',
    'huisarts': 'This test focuses on the 10 most important medical specialties for GPs',
    'apotheker': 'This test focuses on the 10 most important medical specialties for pharmacists',
    'verpleegkundige': 'This test focuses on the 10 most important medical specialties for nurses'
}

# For dentists - use BIG domains (dental specialties)
TOP_10_DOMAINS_TANDARTS = [
    {
        'type': 'big_domain',  # Important: use BIG domain
        'name': 'Therapeutic Dentistry',  # Real name from DB
        'weight': 12.0,
        'questions_count': 5
    },
    {
        'type': 'big_domain',
        'name': 'Pharmacology',
        'weight': 8.0,
        'questions_count': 4
    },
    {
        'type': 'big_domain',
        'name': 'Surgical Dentistry',
        'weight': 8.0,
        'questions_count': 4
    },
    {
        'type': 'big_domain',
        'name': 'Treatment Planning',
        'weight': 10.0,
        'questions_count': 3
    },
    {
        'type': 'big_domain',
        'name': 'Periodontology',
        'weight': 7.0,
        'questions_count': 3
    },
    {
        'type': 'big_domain',
        'name': 'Prosthetic Dentistry',
        'weight': 7.0,
        'questions_count': 3
    },
    {
        'type': 'big_domain',
        'name': 'Research Methodology',
        'weight': 5.0,
        'questions_count': 3
    },
    {
        'type': 'big_domain',
        'name': 'Pediatric Dentistry',
        'weight': 6.0,
        'questions_count': 2
    },
    {
        'type': 'big_domain',
        'name': 'Emergency Care',
        'weight': 8.0,
        'questions_count': 2
    },
    {
        'type': 'big_domain',
        'name': 'Diagnostics',
        'weight': 8.0,
        'questions_count': 2
    }
]
# Total: 31 questions

# For general practitioners - use categories (medical specialties)
TOP_10_CATEGORIES_HUISARTS = [
    {
        'type': 'category',  # Important: use category, not BIG domain
        'name': 'Internal Medicine',
        'weight': 10.0,
        'questions_count': 5
    },
    {
        'type': 'category',
        'name': 'Pharmacology',
        'weight': 9.0,
        'questions_count': 4
    },
    {
        'type': 'category',
        'name': 'Pediatrics',
        'weight': 8.0,
        'questions_count': 4
    },
    {
        'type': 'category',
        'name': 'Neurology',
        'weight': 7.0,
        'questions_count': 3
    },
    {
        'type': 'category',
        'name': 'Anatomy',
        'weight': 7.0,
        'questions_count': 3
    },
    {
        'type': 'category',
        'name': 'Physiology',
        'weight': 7.0,
        'questions_count': 3
    },
    {
        'type': 'category',
        'name': 'Gynecology and Obstetrics',
        'weight': 6.0,
        'questions_count': 2
    },
    {
        'type': 'category',
        'name': 'Surgery',
        'weight': 6.0,
        'questions_count': 2
    },
    {
        'type': 'category',
        'name': 'Dermatology',
        'weight': 5.0,
        'questions_count': 2
    },
    {
        'type': 'category',
        'name': 'Epidemiology',
        'weight': 5.0,
        'questions_count': 2
    }
]
# Total: 30 questions

def get_top_areas_for_profession(profession):
    """
    Get top 10 domains/categories for a profession.
    
    For tandarts: returns BIG domains
    For huisarts: returns categories
    
    Args:
        profession (str): Profession code (tandarts, huisarts, etc.)
        
    Returns:
        dict: {
            'type': 'big_domain' or 'category',
            'areas': list of area configs
        }
    """
    mapping = {
        'tandarts': {
            'type': 'big_domain',
            'areas': TOP_10_DOMAINS_TANDARTS
        },
        'huisarts': {
            'type': 'category',
            'areas': TOP_10_CATEGORIES_HUISARTS
        },
        'apotheker': {
            'type': 'category',
            'areas': TOP_10_CATEGORIES_HUISARTS  # Use huisarts for now
        },
        'verpleegkundige': {
            'type': 'category', 
            'areas': TOP_10_CATEGORIES_HUISARTS  # Use huisarts for now
        }
    }
    return mapping.get(profession, {
        'type': 'category',
        'areas': TOP_10_CATEGORIES_HUISARTS
    })

def get_quick_test_config(profession):
    """
    Get complete Quick Test configuration for a profession.
    
    Args:
        profession (str): Profession code
        
    Returns:
        dict: Complete configuration including areas, timing, description
    """
    areas_config = get_top_areas_for_profession(profession)
    
    return {
        'profession': profession,
        'total_questions': QUICK_TEST_TOTAL_QUESTIONS,
        'time_limit': QUICK_TEST_TIME_LIMIT,
        'description': QUICK_TEST_DESCRIPTION,
        'explanation': QUICK_TEST_EXPLANATION.get(profession, QUICK_TEST_EXPLANATION['huisarts']),
        'filter_type': areas_config['type'],
        'areas': areas_config['areas']
    }

def get_questions_per_area(profession):
    """
    Get the distribution of questions per area for a profession.
    
    Args:
        profession (str): Profession code
        
    Returns:
        list: List of (area_name, questions_count) tuples
    """
    config = get_top_areas_for_profession(profession)
    return [(area['name'], area['questions_count']) for area in config['areas']]

def validate_config():
    """
    Validate that the configuration is correct.
    
    Returns:
        dict: Validation results
    """
    results = {
        'tandarts': {
            'total_questions': sum(area['questions_count'] for area in TOP_10_DOMAINS_TANDARTS),
            'areas_count': len(TOP_10_DOMAINS_TANDARTS),
            'valid': True
        },
        'huisarts': {
            'total_questions': sum(area['questions_count'] for area in TOP_10_CATEGORIES_HUISARTS),
            'areas_count': len(TOP_10_CATEGORIES_HUISARTS),
            'valid': True
        }
    }
    
    # Check if totals match expected
    results['tandarts']['valid'] = results['tandarts']['total_questions'] >= QUICK_TEST_TOTAL_QUESTIONS
    results['huisarts']['valid'] = results['huisarts']['total_questions'] >= QUICK_TEST_TOTAL_QUESTIONS
    
    return results

if __name__ == "__main__":
    # Test the configuration
    print("🔧 DIAGNOSTIC DOMAINS CONFIGURATION TEST")
    print("=" * 50)
    
    # Test for tandarts
    print("\n🦷 TANDARTS CONFIGURATION:")
    tandarts_config = get_quick_test_config('tandarts')
    print(f"   Filter type: {tandarts_config['filter_type']}")
    print(f"   Areas count: {len(tandarts_config['areas'])}")
    print(f"   Total questions: {sum(area['questions_count'] for area in tandarts_config['areas'])}")
    print(f"   Description: {tandarts_config['explanation']}")
    
    # Test for huisarts
    print("\n🩺 HUISARTS CONFIGURATION:")
    huisarts_config = get_quick_test_config('huisarts')
    print(f"   Filter type: {huisarts_config['filter_type']}")
    print(f"   Areas count: {len(huisarts_config['areas'])}")
    print(f"   Total questions: {sum(area['questions_count'] for area in huisarts_config['areas'])}")
    print(f"   Description: {huisarts_config['explanation']}")
    
    # Validate configuration
    print("\n✅ VALIDATION:")
    validation = validate_config()
    for profession, result in validation.items():
        status = "✅ VALID" if result['valid'] else "❌ INVALID"
        print(f"   {profession}: {status} ({result['total_questions']} questions, {result['areas_count']} areas)")
    
    print("\n🎯 FILTERING LOGIC:")
    print("   Tandarts: Question.query.filter_by(profession='tandarts', big_domain_id=domain_id)")
    print("   Huisarts: Question.query.filter_by(profession='huisarts', category='Internal Medicine')")
