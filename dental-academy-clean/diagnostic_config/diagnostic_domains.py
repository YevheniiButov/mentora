#!/usr/bin/env python3
"""
Diagnostic Domains Configuration

This module defines the top areas for Quick Diagnostic Tests for different professions.
- Tandarts: Uses BIG domains (dental specialties)
- Huisarts: Uses categories (medical specialties)
"""

# Quick Test configuration
QUICK_TEST_TOTAL_QUESTIONS = 30
QUICK_SCAN_10_TOTAL_QUESTIONS = 10 
QUICK_TEST_TIME_LIMIT = 20  # minutes
QUICK_TEST_DESCRIPTION = "Snelle diagnostische test - Top 10 belangrijkste gebieden"
QUICK_SCAN_10_DESCRIPTION = "Quick Scan 10 - Focus op belangrijkste competenties"

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
# Priority domains for Quick Scan 10
PRIORITY_DOMAINS_HUISARTS = [
    'Internal Medicine',  # Huisartsgeneeskunde
    'Pharmacology',       # Farmacotherapie
    'Medical Ethics',     # Ethiek
    'Communication Skills' # Communicatie
]

PRIORITY_DOMAINS_TANDARTS = [
    'Therapeutic Dentistry',
    'Pharmacology',
    'Ethics and Law',
    'Communication Skills'
]

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

def get_quick_test_config(profession, diagnostic_type='quick_30'):
    """
    Get complete Quick Test configuration for a profession.
    
    Args:
        profession (str): Profession code
        diagnostic_type (str): 'quick_30' or 'quick_scan_10'
        
    Returns:
        dict: Complete configuration including areas, timing, description
    """
    areas_config = get_top_areas_for_profession(profession)
    
    total_q = QUICK_SCAN_10_TOTAL_QUESTIONS if diagnostic_type == 'quick_scan_10' else QUICK_TEST_TOTAL_QUESTIONS
    desc = QUICK_SCAN_10_DESCRIPTION if diagnostic_type == 'quick_scan_10' else QUICK_TEST_DESCRIPTION
    
    priority_domains = PRIORITY_DOMAINS_HUISARTS if profession == 'huisarts' else PRIORITY_DOMAINS_TANDARTS
    
    return {
        'profession': profession,
        'total_questions': total_q,
        'time_limit': QUICK_TEST_TIME_LIMIT,
        'description': desc,
        'explanation': QUICK_TEST_EXPLANATION.get(profession, QUICK_TEST_EXPLANATION['huisarts']),
        'filter_type': areas_config['type'],
        'areas': areas_config['areas'],
        'priority_domains': priority_domains
    }

def get_questions_per_area(profession, diagnostic_type='quick_30'):
    """
    Get the distribution of questions per area for a profession.
    
    Args:
        profession (str): Profession code
        diagnostic_type (str): Test type
        
    Returns:
        list: List of (area_name, questions_count) tuples
    """
    config = get_quick_test_config(profession, diagnostic_type)
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
    tandarts_config = get_quick_test_config('tandarts', 'quick_30')
    print(f"   Filter type: {tandarts_config['filter_type']}")
    print(f"   Areas count: {len(tandarts_config['areas'])}")
    print(f"   Total questions: {sum(area['questions_count'] for area in tandarts_config['areas'])}")
    print(f"   Description: {tandarts_config['explanation']}")
    
    # Test for huisarts
    print("\n🩺 HUISARTS CONFIGURATION:")
    huisarts_config = get_quick_test_config('huisarts', 'quick_30')
    print(f"   Filter type: {huisarts_config['filter_type']}")
    print(f"   Areas count: {len(huisarts_config['areas'])}")
    print(f"   Total questions: {sum(area['questions_count'] for area in huisarts_config['areas'])}")
    print(f"   Description: {huisarts_config['explanation']}")
    
    # Test for Quick Scan 10
    print("\n⚡️ QUICK SCAN 10 CONFIGURATION (huisarts):")
    qs10_config = get_quick_test_config('huisarts', 'quick_scan_10')
    print(f"   Total questions: {qs10_config['total_questions']}")
    print(f"   Priority domains: {qs10_config['priority_domains']}")
    
    # Validate configuration
    print("\n✅ VALIDATION:")
    validation = validate_config()
    for profession, result in validation.items():
        status = "✅ VALID" if result['valid'] else "❌ INVALID"
        print(f"   {profession}: {status} ({result['total_questions']} questions, {result['areas_count']} areas)")
    
    print("\n🎯 FILTERING LOGIC:")
    print("   Tandarts: Question.query.filter_by(profession='tandarts', big_domain_id=domain_id)")
    print("   Huisarts: Question.query.filter_by(profession='huisarts', category='Internal Medicine')")
