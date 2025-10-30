"""
Flashcard routes for medical terminology learning
Provides study sessions, reviews, and progress tracking

Routes:
- GET /flashcards/daily-session - Daily study session (shows all terms from all categories)
- GET /flashcards/categories - List all categories
- GET /flashcards/study/<category> - Start study session
- GET /flashcards/study-simple/<category> - Start simplified study session
- GET /flashcards/due-reviews - Terms due for review
- POST /flashcards/review/<int:term_id> - Submit review
- GET /flashcards/stats - User statistics
- GET /flashcards/category-stats/<category> - Category stats
- POST /flashcards/api/session-complete - Mark session complete
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app, session
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from models import MedicalTerm, UserTermProgress, db
from utils.flashcard_helpers import (
    get_session_terms, 
    calculate_flashcard_xp,
    get_mastery_distribution,
    get_category_progress,
    get_due_reviews_by_category
)

flashcard_bp = Blueprint('flashcards', __name__, url_prefix='/flashcards')


@flashcard_bp.route('/daily-session')
@login_required
def daily_session():
    """
    Daily study session - shows all terms from all categories
    Used by learning map
    """
    try:
        current_app.logger.info(f"Daily session started for user: {current_user.id}")
        
        # Get all available categories
        categories = db.session.query(MedicalTerm.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        if not categories:
            return render_template('flashcards/study_simple.html',
                                 category='all',
                                 terms=[],
                                 total_terms=0,
                                 message='No terms available in the database')
        
        # Collect terms from all categories (mix of new and review)
        from utils.flashcard_helpers import get_session_terms
        all_selected_terms = []
        
        # Get terms from each category and combine
        terms_per_category = max(3, 10 // max(len(categories), 1))  # Distribute 10 terms across categories
        for category in categories[:3]:  # Limit to first 3 categories to avoid too many
            category_terms = get_session_terms(current_user, category, count=terms_per_category)
            all_selected_terms.extend(category_terms)
        
        # If still not enough, get any terms
        if len(all_selected_terms) < 10:
            remaining = 10 - len(all_selected_terms)
            if all_selected_terms:
                any_terms = MedicalTerm.query.filter(
                    ~MedicalTerm.id.in_([t.id for t in all_selected_terms])
                ).limit(remaining).all()
            else:
                any_terms = MedicalTerm.query.limit(remaining).all()
            all_selected_terms.extend(any_terms)
        
        # Limit to 10 total
        all_terms = all_selected_terms[:10]
        
        if not all_terms:
            return render_template('flashcards/study_simple.html',
                                 category='all',
                                 terms=[],
                                 total_terms=0,
                                 message='No terms available in the database')
        
        # Get user's progress for all terms
        terms_data = []
        for term in all_terms:
            # Get or create progress
            progress = UserTermProgress.query.filter_by(
                user_id=current_user.id,
                term_id=term.id
            ).first()
            
            if not progress:
                progress = UserTermProgress(
                    user_id=current_user.id,
                    term_id=term.id
                )
                db.session.add(progress)
            
            # Get language from session, fallback to user preference, then to 'en'
            user_lang = session.get('lang')
            if not user_lang:
                user_lang = current_user.language or 'en'
            if not user_lang or user_lang == '':
                user_lang = 'en'
            
            # Get translated term or fallback to English
            term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
            
            terms_data.append({
                'id': term.id,
                'term_nl': term.term_nl,
                'term_translated': term_translated,
                'definition': term.definition_nl,
                'category': term.category,
                'difficulty': term.difficulty,
                'progress_id': progress.id
            })
        
        db.session.commit()
        current_app.logger.info(f"Daily session data prepared: {len(terms_data)} terms from all categories")
        
        return render_template('flashcards/study_simple.html',
                             category='all',
                             terms=terms_data,
                             total_terms=len(terms_data))
    
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error starting daily session: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to start daily session: {str(e)}'}), 500


@flashcard_bp.route('/categories')
@login_required
def categories():
    """
    Display all flashcard categories with progress overview
    
    Shows:
    - Total terms per category
    - User's progress (new/learning/mastered)
    - Terms due for review today
    """
    try:
        # Get all categories
        categories_data = db.session.query(
            MedicalTerm.category,
            func.count(MedicalTerm.id).label('total_terms')
        ).group_by(MedicalTerm.category).all()
        
        categories_with_progress = []
        
        for category_name, total_terms in categories_data:
            # Get user's progress for this category
            # Fixed: Join properly with term table
            user_progress = db.session.query(UserTermProgress).join(
                MedicalTerm, UserTermProgress.term_id == MedicalTerm.id
            ).filter(
                UserTermProgress.user_id == current_user.id,
                MedicalTerm.category == category_name
            ).all()
            
            # Count by status
            new_count = total_terms - len(user_progress)
            learning_count = sum(1 for p in user_progress if 0 < p.mastery_level < 4)
            mastered_count = sum(1 for p in user_progress if p.mastery_level >= 4)
            
            # Count due reviews
            due_count = sum(1 for p in user_progress if p.is_due)
            
            categories_with_progress.append({
                'name': category_name,
                'total': total_terms,
                'new': new_count,
                'learning': learning_count,
                'mastered': mastered_count,
                'due_today': due_count,
                'progress_percent': int((len(user_progress) / total_terms * 100)) if total_terms > 0 else 0
            })
        
        # Sort by most progress
        categories_with_progress.sort(key=lambda x: x['progress_percent'], reverse=True)
        
        return render_template('flashcards/study_simple.html', 
                             category='anatomy_basic',  # Default category
                             terms=[], 
                             total_terms=0,
                             message='Please select a category to start studying')
    
    except Exception as e:
        current_app.logger.error(f"Error loading categories: {e}")
        return jsonify({'error': 'Failed to load categories'}), 500


@flashcard_bp.route('/study/<category>')
@login_required
def study_category(category):
    """
    Start a study session for a specific category
    
    Returns 10 terms:
    - 5 new (user hasn't seen)
    - 5 due for review
    """
    try:
        current_app.logger.info(f"Study session started for category: {category}, user: {current_user.id}")
        
        # Validate category
        category_exists = MedicalTerm.query.filter_by(category=category).first()
        if not category_exists:
            current_app.logger.warning(f"Category not found: {category}")
            return jsonify({'error': 'Category not found'}), 404
        
        # Get session terms
        current_app.logger.info(f"Getting session terms for category: {category}")
        session_terms = get_session_terms(current_user, category, count=10)
        current_app.logger.info(f"Got {len(session_terms)} terms for session")
        
        if not session_terms:
            current_app.logger.warning(f"No terms available for category: {category}")
            return render_template('flashcards/study_simple.html',
                                 category=category,
                                 terms=[],
                                 total_terms=0,
                                 message='No terms available for this category')
        
        # Serialize terms for frontend
        terms_data = []
        for term in session_terms:
            # Get or create progress
            progress = UserTermProgress.query.filter_by(
                user_id=current_user.id,
                term_id=term.id
            ).first()
            
            if not progress:
                progress = UserTermProgress(
                    user_id=current_user.id,
                    term_id=term.id
                )
                db.session.add(progress)
            
            # Get language from session, fallback to user preference, then to 'en'
            user_lang = session.get('lang')
            if not user_lang:
                user_lang = current_user.language or 'en'
            if not user_lang or user_lang == '':
                user_lang = 'en'
            
            # Get translated term or fallback to English
            term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
            
            terms_data.append({
                'id': term.id,
                'term_nl': term.term_nl,
                'term_translated': term_translated,
                'definition': term.definition_nl,
                'category': term.category,
                'difficulty': term.difficulty,
                'progress_id': progress.id
            })
        
        db.session.commit()
        current_app.logger.info(f"Study session data prepared: {len(terms_data)} terms")
        
        return render_template('flashcards/study_simple.html',
                             category=category,
                             terms=terms_data,
                             total_terms=len(terms_data))
    
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error starting study session: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to start study session: {str(e)}'}), 500


@flashcard_bp.route('/study-simple/<category>')
@login_required
def study_simple(category):
    """
    Start a simplified study session for a specific category
    Uses the new study_simple.html template with Alpine.js
    """
    try:
        current_app.logger.info(f"Simple study session started for category: {category}, user: {current_user.id}")
        
        # Validate category
        category_exists = MedicalTerm.query.filter_by(category=category).first()
        if not category_exists:
            current_app.logger.warning(f"Category not found: {category}")
            return jsonify({'error': 'Category not found'}), 404
        
        # Get session terms
        current_app.logger.info(f"Getting session terms for category: {category}")
        session_terms = get_session_terms(current_user, category, count=10)
        current_app.logger.info(f"Got {len(session_terms)} terms for session")
        
        if not session_terms:
            current_app.logger.warning(f"No terms available for category: {category}")
            return render_template('flashcards/study_simple.html',
                                 category=category,
                                 terms=[],
                                 total_terms=0,
                                 message='No terms available for this category')
        
        # Serialize terms for frontend
        terms_data = []
        for term in session_terms:
            # Get or create progress
            progress = UserTermProgress.query.filter_by(
                user_id=current_user.id,
                term_id=term.id
            ).first()
            
            if not progress:
                progress = UserTermProgress(
                    user_id=current_user.id,
                    term_id=term.id
                )
                db.session.add(progress)
            
            # Get language from session, fallback to user preference, then to 'en'
            user_lang = session.get('lang')
            if not user_lang:
                user_lang = current_user.language or 'en'
            if not user_lang or user_lang == '':
                user_lang = 'en'
            
            # Get translated term or fallback to English
            term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
            
            terms_data.append({
                'id': term.id,
                'term_nl': term.term_nl,
                'term_translated': term_translated,
                'definition': term.definition_nl,
                'category': term.category,
                'difficulty': term.difficulty,
                'progress_id': progress.id
            })
        
        db.session.commit()
        current_app.logger.info(f"Simple study session data prepared: {len(terms_data)} terms")
        
        return render_template('flashcards/study_simple.html',
                             category=category,
                             terms=terms_data,
                             total_terms=len(terms_data))
    
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error starting simple study session: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to start simple study session: {str(e)}'}), 500


@flashcard_bp.route('/study/term/<int:term_id>')
@login_required
def study_single_term(term_id):
    """
    Start a study session for a single term (quick review)
    Used when clicking "Review" on a specific term from due-reviews list
    """
    try:
        term = MedicalTerm.query.get_or_404(term_id)
        
        # Get or create progress
        progress = UserTermProgress.query.filter_by(
            user_id=current_user.id,
            term_id=term_id
        ).first()
        
        if not progress:
            progress = UserTermProgress(
                user_id=current_user.id,
                term_id=term_id
            )
            db.session.add(progress)
            db.session.flush()
        
        # Get user's language, default to 'en' if not set
        user_lang = current_user.language or 'en'
        if not user_lang or user_lang == '':
            user_lang = 'en'
        
        # Get translated term or fallback to English
        term_translated = getattr(term, f'term_{user_lang}', None) or term.term_en
        
        # Prepare single term for display
        terms_data = [{
            'id': term.id,
            'term_nl': term.term_nl,
            'term_translated': term_translated,
            'definition': term.definition_nl,
            'category': term.category,
            'difficulty': term.difficulty,
            'progress_id': progress.id
        }]
        
        db.session.commit()
        
        return render_template('flashcards/study_simple.html',
                             category=term.category,
                             terms=terms_data,
                             total_terms=1)
    
    except Exception as e:
        current_app.logger.error(f"Error starting single term review: {e}")
        return jsonify({'error': 'Failed to start review'}), 500


@flashcard_bp.route('/review/<int:term_id>', methods=['POST'])
@login_required
def review_term(term_id):
    """
    Process user's review of a term (Premium UX with 4-point confidence rating)
    
    Input (JSON):
    {
        "quality": 1-4,  // 1=Again (forgot), 2=Hard, 3=Good, 4=Easy
        "time_spent": 10 // seconds
    }
    
    Returns:
    {
        "success": true,
        "xp_earned": 15,
        "next_review": "2025-10-30",
        "mastery_level": 2,
        "accuracy": 75.5
    }
    """
    try:
        data = request.get_json()
        confidence = data.get('quality', 3)  # New: 1,2,3,4 confidence rating
        time_spent = data.get('time_spent', 0)
        
        # Validate confidence rating
        if not 1 <= confidence <= 4:
            return jsonify({'error': 'Confidence must be 1-4'}), 400
        
        # Convert new 4-point to SM-2 quality scale (0-5)
        # 1 (Again) -> 0 (complete failure)
        # 2 (Hard) -> 2 (difficulty understanding)
        # 3 (Good) -> 3 (correct with hesitation)  
        # 4 (Easy) -> 5 (perfect recall)
        quality_mapping = {1: 0, 2: 2, 3: 3, 4: 5}
        quality = quality_mapping.get(confidence, 3)
        
        # Get term
        term = MedicalTerm.query.get_or_404(term_id)
        
        # Get or create progress
        progress = UserTermProgress.query.filter_by(
            user_id=current_user.id,
            term_id=term_id
        ).first()
        
        if not progress:
            progress = UserTermProgress(
                user_id=current_user.id,
                term_id=term_id
            )
            db.session.add(progress)
            db.session.flush()
        
        is_first_time = progress.times_reviewed == 0
        
        # Update progress with SM-2
        progress.update_progress_sm2(quality)
        
        # Calculate XP
        xp_earned = calculate_flashcard_xp(quality, is_first_time)
        
        # Award XP to user
        if hasattr(current_user, 'xp'):
            current_user.xp += xp_earned
        if hasattr(current_user, 'level'):
            # Level up every 100 XP (optional)
            if current_user.xp % 100 < xp_earned:
                if hasattr(current_user, 'level'):
                    current_user.level += 1
        
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.id} reviewed term {term_id}: quality={quality}, xp={xp_earned}")
        
        return jsonify({
            'success': True,
            'xp_earned': xp_earned,
            'next_review': progress.next_review.isoformat(),
            'mastery_level': progress.mastery_level,
            'accuracy': round(progress.accuracy_rate, 1),
            'times_reviewed': progress.times_reviewed,
            'is_mastered': progress.mastery_level >= 4
        })
    
    except Exception as e:
        current_app.logger.error(f"Error reviewing term: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to process review'}), 500


@flashcard_bp.route('/due-reviews')
@login_required
def due_reviews():
    """
    Show all terms due for review today, grouped by category
    """
    try:
        due_by_category = get_due_reviews_by_category(current_user)
        
        if not due_by_category:
            return render_template('flashcards/study_simple.html',
                                 category='anatomy_basic',
                                 terms=[],
                                 total_terms=0,
                                 message='No reviews due today. Keep up the good work!')
        
        total_due = sum(len(terms) for terms in due_by_category.values())
        
        # Format for template
        categories_with_due = []
        for category, terms in due_by_category.items():
            categories_with_due.append({
                'name': category,
                'count': len(terms),
                'terms': terms
            })
        
        return render_template('flashcards/study_simple.html',
                             category='anatomy_basic',
                             terms=[],
                             total_terms=0,
                             message=f'Found {total_due} terms due for review. Please use the new study interface.')
    
    except Exception as e:
        current_app.logger.error(f"Error loading due reviews: {e}")
        return jsonify({'error': 'Failed to load due reviews'}), 500


@flashcard_bp.route('/stats')
@login_required
def user_stats():
    """
    Overall user statistics for medical terminology learning
    """
    try:
        # Get all progress for user
        all_progress = UserTermProgress.query.filter_by(
            user_id=current_user.id
        ).all()
        
        # Count by mastery level
        mastery_dist = get_mastery_distribution(current_user)
        
        # Calculate accuracy
        total_reviewed = sum(p.times_reviewed for p in all_progress)
        total_correct = sum(p.times_correct for p in all_progress)
        accuracy = (total_correct / total_reviewed * 100) if total_reviewed > 0 else 0
        
        # Count streaks
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
        yesterday_start = datetime.combine(yesterday, datetime.min.time()).replace(tzinfo=timezone.utc)
        
        today_reviewed = sum(1 for p in all_progress if p.last_reviewed and p.last_reviewed >= today_start)
        yesterday_reviewed = sum(1 for p in all_progress if p.last_reviewed and p.last_reviewed >= yesterday_start and p.last_reviewed < today_start)
        
        current_streak = 1 if today_reviewed > 0 else 0
        if today_reviewed > 0 and yesterday_reviewed > 0:
            current_streak = 2  # Simplified - can be enhanced
        
        # Get category breakdown
        category_stats = []
        categories = db.session.query(MedicalTerm.category).distinct().all()
        
        for (cat,) in categories:
            cat_progress = get_category_progress(current_user, cat)
            if cat_progress:
                category_stats.append({
                    'category': cat,
                    'total': cat_progress['total'],
                    'studied': cat_progress['studied'],
                    'mastered': cat_progress['mastered'],
                    'accuracy': cat_progress['accuracy']
                })
        
        return render_template('flashcards/study_simple.html',
                             category='anatomy_basic',
                             terms=[],
                             total_terms=0,
                             message=f'Statistics: {len(all_progress)} studied, {round(accuracy, 1)}% accuracy. Please use the new study interface.')
    
    except Exception as e:
        current_app.logger.error(f"Error loading stats: {e}")
        return jsonify({'error': 'Failed to load statistics'}), 500


@flashcard_bp.route('/category-stats/<category>')
@login_required
def category_stats(category):
    """
    Detailed statistics for a specific category
    """
    try:
        # Validate category
        if not MedicalTerm.query.filter_by(category=category).first():
            return jsonify({'error': 'Category not found'}), 404
        
        cat_stats = get_category_progress(current_user, category)
        
        if not cat_stats:
            return render_template('flashcards/study_simple.html',
                                 category=category,
                                 terms=[],
                                 total_terms=0,
                                 message='No data for this category yet. Please use the new study interface.')
        
        return render_template('flashcards/study_simple.html',
                             category=category,
                             terms=[],
                             total_terms=0,
                             message=f'Category stats: {cat_stats["studied"]}/{cat_stats["total"]} studied, {cat_stats["accuracy"]}% accuracy. Please use the new study interface.')
    
    except Exception as e:
        current_app.logger.error(f"Error loading category stats: {e}")
        return jsonify({'error': 'Failed to load category statistics'}), 500


@flashcard_bp.route('/api/due-count')
@login_required
def api_due_count():
    """
    API endpoint to get count of terms due for review (for dashboard badge)
    """
    try:
        due_count = UserTermProgress.query.filter(
            UserTermProgress.user_id == current_user.id,
            UserTermProgress.next_review <= datetime.now(timezone.utc)
        ).count()
        
        return jsonify({'due_count': due_count})
    
    except Exception as e:
        current_app.logger.error(f"Error getting due count: {e}")
        return jsonify({'error': 'Failed to get due count'}), 500


@flashcard_bp.route('/api/session-complete', methods=['POST'])
@login_required
def api_session_complete():
    """
    API endpoint to mark session as complete
    Used by the simplified study interface
    """
    try:
        data = request.get_json()
        terms_studied = data.get('terms_studied', 0)
        total_xp = data.get('total_xp', 0)
        time_spent = data.get('time_spent', 0)
        
        current_app.logger.info(f"Session completed: user={current_user.id}, terms={terms_studied}, xp={total_xp}, time={time_spent}")
        
        # Here you could add additional session tracking logic
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': 'Session completed successfully'
        })
    
    except Exception as e:
        current_app.logger.error(f"Error completing session: {e}")
        return jsonify({'error': 'Failed to complete session'}), 500
