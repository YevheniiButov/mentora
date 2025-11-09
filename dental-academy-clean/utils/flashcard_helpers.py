"""
Helper functions for medical terminology flashcard system
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from models import MedicalTerm, UserTermProgress, db
from utils.helpers import get_user_profession_code


def get_session_terms(user, category, count=10):
    """
    Get optimal mix of terms for a study session
    
    Returns 50% new terms + 50% due reviews
    Prioritizes by difficulty and frequency
    
    Args:
        user: Current user object
        category: Category name (e.g., 'anatomy')
        count: Total terms to return (default 10)
    
    Returns:
        list: MedicalTerm objects
    """
    try:
        # Get all terms in category
        all_category_terms = MedicalTerm.query.filter_by(category=category).all()
        
        if not all_category_terms:
            return []
        
        # Split terms into new and review
        new_terms = []
        review_terms = []
        
        for term in all_category_terms:
            progress = UserTermProgress.query.filter_by(
                user_id=user.id,
                term_id=term.id
            ).first()
            
            if not progress:
                new_terms.append(term)
            else:
                try:
                    # Check if term is due for review (with error handling for datetime issues)
                    if progress.is_due:
                        review_terms.append(term)
                except Exception as is_due_error:
                    print(f"Warning: Error checking is_due for progress {progress.id}: {is_due_error}")
                    # If error checking is_due, treat as not due
                    pass
        
        # Sort by difficulty and frequency (prioritize harder, more common terms)
        new_terms.sort(key=lambda t: (t.difficulty, t.frequency), reverse=True)
        review_terms.sort(key=lambda t: t.difficulty, reverse=True)
        
        # Mix: 50% new, 50% review
        new_count = max(count // 2, 1)
        review_count = count - new_count
        
        selected = []
        selected.extend(new_terms[:new_count])
        selected.extend(review_terms[:review_count])
        
        # If not enough terms, add more from either pool
        if len(selected) < count:
            remaining = count - len(selected)
            # Add leftover new terms
            selected.extend(new_terms[new_count:new_count + remaining])
            # Add non-due review terms
            non_due_reviews = [t for t in all_category_terms 
                              if t not in selected 
                              and any(p.user_id == user.id and p.term_id == t.id 
                                     for p in t.user_progress)]
            selected.extend(non_due_reviews[:remaining - len(selected) + new_count])
        
        return selected[:count]
    
    except Exception as e:
        import traceback
        print(f"Error getting session terms: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return []


def get_allowed_categories(user):
    """
    Return list of category names accessible for the given user.

    Dentists (tandarts) see only categories with prefix `dentistry_`.
    Other professions see all categories that do NOT have that prefix.
    If the preferred group is empty (e.g. data not imported yet), fall back
    to whatever is available so that the interface is still usable.
    """
    # Fetch all category names
    all_categories = [
        name
        for (name,) in db.session.query(MedicalTerm.category).distinct().all()
        if name
    ]

    if not all_categories:
        return []

    dentistry_categories = [c for c in all_categories if c.startswith('dentistry_')]
    general_categories = [c for c in all_categories if not c.startswith('dentistry_')]

    profession = get_user_profession_code(user)

    if profession == 'tandarts':
        return dentistry_categories or general_categories

    # Non-dentists should not see dental-specific categories
    return general_categories or dentistry_categories


def calculate_flashcard_xp(quality, is_first_time=False):
    """
    Calculate XP earned for a flashcard review
    
    Formula:
    - quality 1-2: 5 XP (failed)
    - quality 3: 10 XP (good)
    - quality 4-5: 15 XP (easy)
    - first_time_bonus: +5 XP
    
    Args:
        quality: User's response quality (1-5)
        is_first_time: Whether this is the first review of this term
    
    Returns:
        int: XP points earned
    """
    base_xp = {
        1: 5,
        2: 5,
        3: 10,
        4: 15,
        5: 15
    }
    
    xp = base_xp.get(quality, 10)
    
    # First time bonus
    if is_first_time:
        xp += 5
    
    return xp


def get_mastery_distribution(user):
    """
    Get breakdown of terms by mastery level
    
    Args:
        user: Current user object
    
    Returns:
        dict: {0: count, 1: count, ..., 5: count}
    """
    try:
        distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        progress_items = UserTermProgress.query.filter_by(user_id=user.id).all()
        
        for progress in progress_items:
            level = min(progress.mastery_level, 5)
            distribution[level] += 1
        
        return distribution
    
    except Exception as e:
        print(f"Error getting mastery distribution: {e}")
        return {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


def get_category_progress(user, category):
    """
    Get detailed progress statistics for a category
    
    Args:
        user: Current user object
        category: Category name
    
    Returns:
        dict: {
            'total': int,
            'studied': int,
            'mastered': int,
            'accuracy': float,
            'time_spent': int,
            'last_review': datetime
        }
    """
    try:
        # Get all terms in category
        all_terms = MedicalTerm.query.filter_by(category=category).all()
        total = len(all_terms)
        
        if total == 0:
            return None
        
        # Get user's progress for category
        studied = 0
        mastered = 0
        total_reviewed = 0
        total_correct = 0
        last_review = None
        
        for term in all_terms:
            progress = UserTermProgress.query.filter_by(
                user_id=user.id,
                term_id=term.id
            ).first()
            
            if progress:
                studied += 1
                if progress.mastery_level >= 4:
                    mastered += 1
                
                total_reviewed += progress.times_reviewed
                total_correct += progress.times_correct
                
                if progress.last_reviewed:
                    if not last_review or progress.last_reviewed > last_review:
                        last_review = progress.last_reviewed
        
        accuracy = (total_correct / total_reviewed * 100) if total_reviewed > 0 else 0
        
        return {
            'total': total,
            'studied': studied,
            'mastered': mastered,
            'accuracy': round(accuracy, 1),
            'total_reviewed': total_reviewed,
            'total_correct': total_correct,
            'last_review': last_review,
            'progress_percent': int((studied / total * 100)) if total > 0 else 0
        }
    
    except Exception as e:
        print(f"Error getting category progress: {e}")
        return None


def get_due_reviews_by_category(user):
    """
    Get all terms due for review today, grouped by category
    
    Args:
        user: Current user object
    
    Returns:
        dict: {
            'category_name': [
                {
                    'id': int,
                    'term_nl': str,
                    'term_translated': str,
                    'mastery_level': int,
                    'next_review': datetime
                },
                ...
            ],
            ...
        }
    """
    try:
        due_items = UserTermProgress.query.filter(
            UserTermProgress.user_id == user.id,
            UserTermProgress.next_review <= datetime.now(timezone.utc)
        ).all()
        
        due_by_category = {}
        
        allowed_categories = set(get_allowed_categories(user))

        for progress in due_items:
            term = progress.term
            category = term.category
            
            if allowed_categories and category not in allowed_categories:
                continue
            
            if category not in due_by_category:
                due_by_category[category] = []
            
            # Get user's language, default to 'en' if not set
            user_lang = user.language or 'en'
            if not user_lang or user_lang == '':
                user_lang = 'en'
            
            # Get translated term or fallback to English
            term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
            
            due_by_category[category].append({
                'id': term.id,
                'term_nl': term.term_nl,
                'term_translated': term_translated,
                'mastery_level': progress.mastery_level,
                'next_review': progress.next_review,
                'times_reviewed': progress.times_reviewed,
                'accuracy': round(progress.accuracy_rate, 1)
            })
        
        return due_by_category
    
    except Exception as e:
        print(f"Error getting due reviews: {e}")
        return {}


def get_study_streak(user):
    """
    Calculate current study streak (consecutive days of activity)
    
    Args:
        user: Current user object
    
    Returns:
        int: Current streak count
    """
    try:
        # Get unique dates of activity
        activity_dates = db.session.query(
            func.date(UserTermProgress.last_reviewed)
        ).filter(
            UserTermProgress.user_id == user.id,
            UserTermProgress.last_reviewed.isnot(None)
        ).distinct().all()
        
        if not activity_dates:
            return 0
        
        # Convert to sorted list of dates
        dates = sorted([d[0] for d in activity_dates], reverse=True)
        
        # Count consecutive days from today
        today = datetime.now(timezone.utc).date()
        streak = 0
        
        for i, date in enumerate(dates):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    except Exception as e:
        print(f"Error calculating streak: {e}")
        return 0
