"""
Domain Category Helper Functions

Helper functions for working with DomainCategory and BIGDomain models.
Provides utilities for calculating progress, getting categories, and analyzing user performance.
"""

from typing import List, Dict, Any, Optional
from models import DomainCategory, BIGDomain, UserProgress, Question
from sqlalchemy import func


def get_categories_for_profession(profession: str) -> List[DomainCategory]:
    """
    Get all domain categories for a profession, ordered by order field.
    
    Args:
        profession (str): Profession code (tandarts, huisarts, etc.)
        
    Returns:
        list: List of DomainCategory objects
    """
    return DomainCategory.query.filter_by(
        profession=profession
    ).order_by(DomainCategory.order).all()


def get_domains_by_category(category_id: int) -> List[BIGDomain]:
    """
    Get all BIG domains for a specific category.
    
    Args:
        category_id (int): ID of the category
        
    Returns:
        list: List of BIGDomain objects
    """
    return BIGDomain.query.filter_by(
        category_id=category_id
    ).order_by(BIGDomain.name).all()


def get_question_categories_for_category(category_name: str) -> List[str]:
    """
    Get question categories for a Huisarts domain category.
    This mapping comes from seed_huisarts_categories.py.
    
    Args:
        category_name (str): Name of the domain category
        
    Returns:
        list: List of question category names
    """
    # Hardcoded mapping from seed_huisarts_categories.py
    mapping = {
        'Internal Medicine': [
            'Internal Medicine', 'Cardiology', 'Endocrinology',
            'Gastroenterology', 'Nephrology', 'Rheumatology'
        ],
        'Basic Medical Sciences': [
            'Anatomy', 'Physiology', 'Pathology', 'Biochemistry', 'Microbiology'
        ],
        'Pharmacology & Therapeutics': ['Pharmacology'],
        'Surgery & Procedures': ['Surgery', 'Orthopedics', 'Urology'],
        'Pediatrics & Women\'s Health': ['Pediatrics', 'Gynecology and Obstetrics'],
        'Neurology & Mental Health': ['Neurology', 'Psychiatry', 'Psychology'],
        'Diagnostics & Emergency': ['Epidemiology', 'Emergency Medicine', 'Infectious Diseases'],
        'Dermatology & Sensory Systems': ['Dermatology', 'Ophthalmology', 'Otolaryngology']
    }
    
    return mapping.get(category_name, [])


def calculate_category_progress(user, category_id: int) -> Dict[str, Any]:
    """
    Calculate user's progress for a category.
    Works for both Tandarts (BIG domains) and Huisarts (question categories).
    
    Args:
        user: User object
        category_id (int): ID of the category
        
    Returns:
        dict: {
            'total_domains': int,
            'completed_domains': int,
            'percentage': float,
            'domains': [
                {
                    'id': int or str,
                    'name': str,
                    'progress': float,
                    'completed': bool
                }
            ]
        }
    """
    category = DomainCategory.query.get(category_id)
    if not category:
        return {
            'total_domains': 0,
            'completed_domains': 0,
            'percentage': 0.0,
            'domains': []
        }
    
    if category.profession == 'tandarts':
        # For Tandarts: use BIG domains
        domains = get_domains_by_category(category_id)
        
        if not domains:
            return {
                'total_domains': 0,
                'completed_domains': 0,
                'percentage': 0.0,
                'domains': []
            }
        
        # Import models for progress calculation
        from models import DiagnosticResponse, PersonalLearningPlan, StudySession
        
        domain_progress = []
        completed_count = 0
        
        for domain in domains:
            # Calculate actual progress based on user's diagnostic and practice sessions
            diagnostic_correct = DiagnosticResponse.query.join(
                DiagnosticResponse.session
            ).join(Question).filter(
                DiagnosticResponse.session.has(user_id=user.id),
                Question.big_domain_id == domain.id,
                DiagnosticResponse.is_correct == True
            ).count()
            
            diagnostic_total = DiagnosticResponse.query.join(
                DiagnosticResponse.session
            ).join(Question).filter(
                DiagnosticResponse.session.has(user_id=user.id),
                Question.big_domain_id == domain.id
            ).count()
            
            # Get user's practice responses for this domain from StudySessionResponse
            # Join through StudySession and Question to get domain information
            from models import StudySessionResponse
            
            practice_responses = StudySessionResponse.query.join(
                StudySession
            ).join(PersonalLearningPlan).join(Question).filter(
                PersonalLearningPlan.user_id == user.id,
                Question.big_domain_id == domain.id,
                StudySession.status == 'completed'
            ).all()
            
            practice_correct = sum(1 for resp in practice_responses if resp.is_correct)
            practice_total = len(practice_responses)
            
            # Calculate percentage
            total_correct = diagnostic_correct + practice_correct
            total_questions = diagnostic_total + practice_total
            
            domain_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0.0
            is_completed = domain_percentage >= 80.0
            
            if is_completed:
                completed_count += 1
            
            domain_progress.append({
                'id': domain.id,
                'name': domain.name,
                'progress': domain_percentage,
                'completed': is_completed
            })
        
        # Calculate overall category percentage
        total_percentage = sum(d['progress'] for d in domain_progress) / len(domains) if domains else 0.0
        
        return {
            'total_domains': len(domains),
            'completed_domains': completed_count,
            'percentage': round(total_percentage, 1),
            'domains': domain_progress
        }
    
    elif category.profession == 'huisarts':
        # For Huisarts: use question categories
        question_categories = get_question_categories_for_category(category.name)
        
        if not question_categories:
            return {
                'total_domains': 0,
                'completed_domains': 0,
                'percentage': 0.0,
                'domains': []
            }
        
        category_progress = []
        completed_count = 0
        
        for qcat in question_categories:
            # Count questions in this category
            total_questions = Question.query.filter_by(
                profession='huisarts',
                category=qcat
            ).count()
            
            # Count answered questions (placeholder - would need actual user progress)
            answered_questions = 0  # TODO: Query from user's answered questions
            
            qcat_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0.0
            is_completed = qcat_percentage >= 80.0
            
            if is_completed:
                completed_count += 1
            
            category_progress.append({
                'id': qcat,  # Using category name as ID for now
                'name': qcat,
                'progress': qcat_percentage,
                'completed': is_completed
            })
        
        # Calculate overall category percentage
        total_percentage = sum(c['progress'] for c in category_progress) / len(question_categories) if question_categories else 0.0
        
        return {
            'total_domains': len(question_categories),
            'completed_domains': completed_count,
            'percentage': round(total_percentage, 1),
            'domains': category_progress
        }
    
    # Unknown profession
    return {
        'total_domains': 0,
        'completed_domains': 0,
        'percentage': 0.0,
        'domains': []
    }


def get_category_summary(user, profession: str) -> List[Dict[str, Any]]:
    """
    Get summary of all categories with progress for a user.
    
    Args:
        user: User object
        profession (str): Profession code
        
    Returns:
        list: List of category summaries with progress
    """
    categories = get_categories_for_profession(profession)
    
    summaries = []
    for category in categories:
        progress = calculate_category_progress(user, category.id)
        
        summaries.append({
            'id': category.id,
            'name': category.name,
            'name_nl': category.name_nl,
            'icon': category.icon,
            'color': category.color,
            'order': category.order,
            'domains_count': progress['total_domains'],
            'completed_domains': progress['completed_domains'],
            'percentage': progress['percentage']
        })
    
    return summaries


def get_user_weak_categories(user, profession: str, threshold: int = 60) -> List[Dict[str, Any]]:
    """
    Get categories where user has low performance.
    
    Args:
        user: User object
        profession (str): Profession code
        threshold (int): Percentage below which category is considered weak
        
    Returns:
        list: List of weak categories with progress
    """
    summary = get_category_summary(user, profession)
    
    weak_categories = [
        cat for cat in summary 
        if cat['percentage'] < threshold
    ]
    
    # Sort by lowest percentage first
    weak_categories.sort(key=lambda x: x['percentage'])
    
    return weak_categories


def get_user_strong_categories(user, profession: str, threshold: int = 80) -> List[Dict[str, Any]]:
    """
    Get categories where user has high performance.
    
    Args:
        user: User object
        profession (str): Profession code
        threshold (int): Percentage above which category is considered strong
        
    Returns:
        list: List of strong categories with progress
    """
    summary = get_category_summary(user, profession)
    
    strong_categories = [
        cat for cat in summary 
        if cat['percentage'] >= threshold
    ]
    
    # Sort by highest percentage first
    strong_categories.sort(key=lambda x: x['percentage'], reverse=True)
    
    return strong_categories


def get_category_by_id(category_id: int) -> Optional[DomainCategory]:
    """
    Get a specific category by ID.
    
    Args:
        category_id (int): ID of the category
        
    Returns:
        DomainCategory or None if not found
    """
    return DomainCategory.query.get(category_id)


def get_category_by_name(name: str, profession: str) -> Optional[DomainCategory]:
    """
    Get a specific category by name and profession.
    
    Args:
        name (str): Name of the category
        profession (str): Profession code
        
    Returns:
        DomainCategory or None if not found
    """
    return DomainCategory.query.filter_by(
        name=name,
        profession=profession
    ).first()


def get_domain_progress_summary(user, profession: str) -> Dict[str, Any]:
    """
    Get overall progress summary across all categories for a user.
    
    Args:
        user: User object
        profession (str): Profession code
        
    Returns:
        dict: Overall progress summary
    """
    categories = get_categories_for_profession(profession)
    
    total_domains = 0
    completed_domains = 0
    total_percentage = 0.0
    
    category_summaries = []
    
    for category in categories:
        progress = calculate_category_progress(user, category.id)
        
        total_domains += progress['total_domains']
        completed_domains += progress['completed_domains']
        total_percentage += progress['percentage']
        
        category_summaries.append({
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
            'color': category.color,
            'percentage': progress['percentage'],
            'domains_count': progress['total_domains'],
            'completed_domains': progress['completed_domains']
        })
    
    # Calculate overall percentage
    overall_percentage = total_percentage / len(categories) if categories else 0.0
    
    return {
        'total_categories': len(categories),
        'total_domains': total_domains,
        'completed_domains': completed_domains,
        'overall_percentage': round(overall_percentage, 1),
        'categories': category_summaries
    }


def get_recommended_categories(user, profession: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Get recommended categories for user to focus on (weakest categories).
    
    Args:
        user: User object
        profession (str): Profession code
        limit (int): Maximum number of categories to return
        
    Returns:
        list: List of recommended categories
    """
    weak_categories = get_user_weak_categories(user, profession, threshold=70)
    
    # Return top N weakest categories
    return weak_categories[:limit]


def get_category_statistics(profession: str) -> Dict[str, Any]:
    """
    Get general statistics about categories and domains for a profession.
    
    Args:
        profession (str): Profession code
        
    Returns:
        dict: Statistics about categories and domains
    """
    categories = get_categories_for_profession(profession)
    
    total_domains = 0
    categories_with_domains = 0
    
    for category in categories:
        domain_count = category.big_domains.count()
        total_domains += domain_count
        
        if domain_count > 0:
            categories_with_domains += 1
    
    return {
        'total_categories': len(categories),
        'categories_with_domains': categories_with_domains,
        'total_domains': total_domains,
        'average_domains_per_category': round(total_domains / len(categories), 1) if categories else 0
    }
