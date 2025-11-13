# utils/helpers.py
"""
Helper functions for the Mentora application
"""

def get_user_profession_code(user):
    """
    Get profession code for question filtering.
    Maps various profession names to standard codes.
    
    Args:
        user: User object with profession field
        
    Returns:
        str: Profession code (tandarts, huisarts, etc.)
        
    Examples:
        >>> user = User(profession='tandarts')
        >>> get_user_profession_code(user)
        'tandarts'
        
        >>> user = User(profession='dentist')
        >>> get_user_profession_code(user)
        'tandarts'
        
        >>> user = User(profession='arts')
        >>> get_user_profession_code(user)
        'huisarts'
        
        >>> user = User(profession=None)
        >>> get_user_profession_code(user)
        'huisarts'
        
        >>> user = None
        >>> get_user_profession_code(user)
        'huisarts'
    """
    if not user or not user.profession:
        return 'huisarts'  # Default to huisarts (general practitioner)
        
    # Normalize profession value
    profession_lower = user.profession.lower().strip()
    
    # Direct matches for standard profession codes
    valid_professions = ['tandarts', 'huisarts', 'apotheker', 'verpleegkundige']
    if profession_lower in valid_professions:
        return profession_lower
        
    # Aliases/variations mapping
    mapping = {
        # Tandarts (Dentist) variations
        'mondhygiënist': 'tandarts',
        'dentist': 'tandarts',
        'dental': 'tandarts',
        'tandheelkunde': 'tandarts',
        
        # Huisarts (General Practitioner) variations
        'arts': 'huisarts',
        'gp': 'huisarts',
        'general practitioner': 'huisarts',
        'family doctor': 'huisarts',
        'primary care': 'huisarts',
        'huisarts': 'huisarts',  # Explicit match
        
        # Apotheker (Pharmacist) variations
        'pharmacist': 'apotheker',
        'pharmacy': 'apotheker',
        'apotheek': 'apotheker',
        
        # Verpleegkundige (Nurse) variations
        'nurse': 'verpleegkundige',
        'nursing': 'verpleegkundige',
        'verpleging': 'verpleegkundige',
        'verpleegkundige': 'verpleegkundige',  # Explicit match
        
        # Other medical professions (map to huisarts as default)
        'fysiotherapeut': 'huisarts',
        'psycholoog': 'huisarts',
        'dietist': 'huisarts',
        'logopedist': 'huisarts',
        'ergotherapeut': 'huisarts',
        'podotherapeut': 'huisarts',
        'other': 'huisarts'
    }
    
    return mapping.get(profession_lower, 'huisarts')


def get_profession_display_name(profession_code):
    """
    Get display name for profession code.
    
    Args:
        profession_code: Standard profession code
        
    Returns:
        str: Display name with emoji
        
    Examples:
        >>> get_profession_display_name('tandarts')
        '🦷 Tandarts'
        
        >>> get_profession_display_name('huisarts')
        '🩺 Huisarts'
        
        >>> get_profession_display_name('unknown')
        'Unknown'
    """
    display_names = {
        'tandarts': '🦷 Tandarts',
        'huisarts': '🩺 Huisarts',
        'apotheker': '💊 Apotheker',
        'verpleegkundige': '👩‍⚕️ Verpleegkundige'
    }
    
    return display_names.get(profession_code, 'Unknown')


def get_available_professions():
    """
    Get list of available profession codes.
    
    Returns:
        list: List of profession codes
        
    Examples:
        >>> get_available_professions()
        ['tandarts', 'huisarts', 'apotheker', 'verpleegkundige']
    """
    return ['tandarts', 'huisarts', 'apotheker', 'verpleegkundige']


def is_valid_profession(profession_code):
    """
    Check if profession code is valid.
    
    Args:
        profession_code: Profession code to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Examples:
        >>> is_valid_profession('tandarts')
        True
        
        >>> is_valid_profession('invalid')
        False
    """
    return profession_code in get_available_professions()








