"""
Daily Lesson Routes
Provides daily lesson functionality for medical terminology learning
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from models import MedicalTerm, UserTermProgress, db
from utils.flashcard_helpers import get_session_terms, calculate_flashcard_xp
from sqlalchemy import func, and_

daily_lesson_bp = Blueprint('daily_lesson', __name__, url_prefix='/daily-lesson')


@daily_lesson_bp.route('/')
@login_required
def index():
    """
    Daily lesson overview - shows available categories and progress
    """
    try:
        # Get all categories with term counts
        categories_data = db.session.query(
            MedicalTerm.category,
            func.count(MedicalTerm.id).label('total_terms')
        ).group_by(MedicalTerm.category).all()
        
        categories_with_progress = []
        
        for category_name, total_terms in categories_data:
            # Get user's progress for this category
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
        
        # Get user's overall stats
        total_terms_studied = UserTermProgress.query.filter_by(user_id=current_user.id).count()
        total_terms_mastered = UserTermProgress.query.filter(
            and_(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.mastery_level >= 4
            )
        ).count()
        
        # Get today's due reviews
        today_due = UserTermProgress.query.join(
            MedicalTerm, UserTermProgress.term_id == MedicalTerm.id
        ).filter(
            and_(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.next_review <= datetime.now(timezone.utc)
            )
        ).count()
        
        return render_template('daily_lesson/index.html',
                             categories=categories_with_progress,
                             total_terms_studied=total_terms_studied,
                             total_terms_mastered=total_terms_mastered,
                             today_due=today_due)
    
    except Exception as e:
        current_app.logger.error(f"Error loading daily lesson index: {e}")
        flash('Error loading daily lesson overview', 'error')
        return redirect(url_for('dashboard.index'))


@daily_lesson_bp.route('/start/<category>')
@login_required
def start_lesson(category):
    """
    Start a daily lesson for a specific category
    Returns 10 terms: 5 new + 5 review
    """
    try:
        current_app.logger.info(f"Starting daily lesson for category: {category}, user: {current_user.id}")
        
        # Get session terms (5 new + 5 review)
        terms = get_session_terms(current_user, category, count=10)
        
        if not terms:
            flash(f'No terms available for category: {category}', 'warning')
            return redirect(url_for('daily_lesson.index'))
        
        # Convert terms to JSON-serializable format
        terms_data = []
        for term in terms:
            # Get user's progress for this term
            progress = UserTermProgress.query.filter_by(
                user_id=current_user.id,
                term_id=term.id
            ).first()
            
            # Get translation in user's language
            user_lang = current_user.language or 'en'
            term_translated = term.to_dict(lang=user_lang)
            
            terms_data.append({
                'id': term.id,
                'dutch_term': term.term_nl,
                'translated_term': term_translated['term'],
                'definition': term_translated['definition'],
                'category': term.category,
                'difficulty': term.difficulty,
                'is_new': progress is None,
                'mastery_level': progress.mastery_level if progress else 0,
                'times_reviewed': progress.times_reviewed if progress else 0,
                'accuracy_rate': progress.accuracy_rate if progress else 0
            })
        
        # Store lesson data in session
        session_data = {
            'category': category,
            'terms': terms_data,
            'started_at': datetime.now(timezone.utc).isoformat(),
            'current_index': 0,
            'correct_answers': 0,
            'total_answered': 0
        }
        
        # Store in Flask session
        from flask import session
        session['daily_lesson'] = session_data
        
        return render_template('daily_lesson/study.html',
                             category=category,
                             terms=terms_data,
                             session_data=session_data)
    
    except Exception as e:
        current_app.logger.error(f"Error starting daily lesson: {e}")
        import traceback
        traceback.print_exc()
        flash('Error starting daily lesson', 'error')
        return redirect(url_for('daily_lesson.index'))


@daily_lesson_bp.route('/answer', methods=['POST'])
@login_required
def submit_answer():
    """
    Submit answer for current term in daily lesson
    """
    try:
        data = request.get_json()
        term_id = data.get('term_id')
        quality = data.get('quality', 3)  # 1-5 scale
        time_spent = data.get('time_spent', 0)
        
        if not term_id:
            return jsonify({'error': 'Term ID required'}), 400
        
        if not 1 <= quality <= 5:
            return jsonify({'error': 'Quality must be 1-5'}), 400
        
        # Get the term
        term = MedicalTerm.query.get_or_404(term_id)
        
        # Get or create user progress
        progress = UserTermProgress.query.filter_by(
            user_id=current_user.id,
            term_id=term_id
        ).first()
        
        if not progress:
            progress = UserTermProgress(user_id=current_user.id, term_id=term_id)
            db.session.add(progress)
            db.session.flush()
        
        # Update progress using SM-2 algorithm
        is_first_time = progress.times_reviewed == 0
        progress.update_progress_sm2(quality)
        
        # Calculate XP earned
        xp_earned = calculate_flashcard_xp(quality, is_first_time)
        
        # Update user XP and level
        if hasattr(current_user, 'xp'):
            current_user.xp += xp_earned
            # Check for level up
            if hasattr(current_user, 'level'):
                new_level = current_user.xp // 100 + 1
                if new_level > current_user.level:
                    current_user.level = new_level
        
        # Update session data
        from flask import session
        if 'daily_lesson' in session:
            session['daily_lesson']['total_answered'] += 1
            if quality >= 3:
                session['daily_lesson']['correct_answers'] += 1
        
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.id} answered term {term_id}: quality={quality}, xp={xp_earned}")
        
        return jsonify({
            'success': True,
            'xp_earned': xp_earned,
            'next_review': progress.next_review.isoformat(),
            'mastery_level': progress.mastery_level,
            'accuracy': round(progress.accuracy_rate, 1),
            'times_reviewed': progress.times_reviewed,
            'is_mastered': progress.mastery_level >= 4,
            'is_correct': quality >= 3
        })
    
    except Exception as e:
        current_app.logger.error(f"Error submitting answer: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to process answer'}), 500


@daily_lesson_bp.route('/next')
@login_required
def next_term():
    """
    Get next term in daily lesson
    """
    try:
        from flask import session
        
        if 'daily_lesson' not in session:
            return jsonify({'error': 'No active lesson'}), 400
        
        lesson_data = session['daily_lesson']
        current_index = lesson_data.get('current_index', 0)
        terms = lesson_data.get('terms', [])
        
        if current_index >= len(terms):
            return jsonify({'error': 'No more terms'}), 400
        
        # Get next term
        next_term = terms[current_index]
        
        # Update current index
        session['daily_lesson']['current_index'] = current_index + 1
        
        return jsonify({
            'success': True,
            'term': next_term,
            'current_index': current_index + 1,
            'total_terms': len(terms),
            'is_last': current_index + 1 >= len(terms)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting next term: {e}")
        return jsonify({'error': 'Failed to get next term'}), 500


@daily_lesson_bp.route('/complete', methods=['POST'])
@login_required
def complete_lesson():
    """
    Complete the daily lesson and show results
    """
    try:
        from flask import session
        
        if 'daily_lesson' not in session:
            return jsonify({'error': 'No active lesson'}), 400
        
        lesson_data = session['daily_lesson']
        
        # Calculate results
        total_answered = lesson_data.get('total_answered', 0)
        correct_answers = lesson_data.get('correct_answers', 0)
        accuracy = (correct_answers / total_answered * 100) if total_answered > 0 else 0
        
        # Calculate total XP earned
        total_xp = 0
        for term_data in lesson_data.get('terms', []):
            if term_data.get('is_correct', False):
                total_xp += 10  # Base XP for correct answer
        
        # Clear session
        session.pop('daily_lesson', None)
        
        return jsonify({
            'success': True,
            'results': {
                'total_answered': total_answered,
                'correct_answers': correct_answers,
                'accuracy': round(accuracy, 1),
                'total_xp': total_xp,
                'category': lesson_data.get('category', 'Unknown')
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"Error completing lesson: {e}")
        return jsonify({'error': 'Failed to complete lesson'}), 500


@daily_lesson_bp.route('/stats')
@login_required
def stats():
    """
    Show user's daily lesson statistics
    """
    try:
        # Get user's overall progress
        total_terms = MedicalTerm.query.count()
        studied_terms = UserTermProgress.query.filter_by(user_id=current_user.id).count()
        mastered_terms = UserTermProgress.query.filter(
            and_(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.mastery_level >= 4
            )
        ).count()
        
        # Get progress by category
        categories_progress = []
        categories = db.session.query(MedicalTerm.category).distinct().all()
        
        for (category,) in categories:
            category_total = MedicalTerm.query.filter_by(category=category).count()
            category_studied = db.session.query(UserTermProgress).join(
                MedicalTerm, UserTermProgress.term_id == MedicalTerm.id
            ).filter(
                and_(
                    UserTermProgress.user_id == current_user.id,
                    MedicalTerm.category == category
                )
            ).count()
            
            categories_progress.append({
                'category': category,
                'total': category_total,
                'studied': category_studied,
                'progress_percent': int((category_studied / category_total * 100)) if category_total > 0 else 0
            })
        
        # Sort by progress
        categories_progress.sort(key=lambda x: x['progress_percent'], reverse=True)
        
        # Get recent activity
        recent_activity = UserTermProgress.query.filter_by(
            user_id=current_user.id
        ).order_by(UserTermProgress.last_reviewed.desc()).limit(10).all()
        
        recent_terms = []
        for progress in recent_activity:
            if progress.term:
                recent_terms.append({
                    'term': progress.term.term_nl,
                    'mastery_level': progress.mastery_level,
                    'last_reviewed': progress.last_reviewed.isoformat() if progress.last_reviewed else None,
                    'accuracy': round(progress.accuracy_rate, 1)
                })
        
        return render_template('daily_lesson/stats.html',
                             total_terms=total_terms,
                             studied_terms=studied_terms,
                             mastered_terms=mastered_terms,
                             categories_progress=categories_progress,
                             recent_terms=recent_terms)
    
    except Exception as e:
        current_app.logger.error(f"Error loading stats: {e}")
        flash('Error loading statistics', 'error')
        return redirect(url_for('daily_lesson.index'))


@daily_lesson_bp.route('/api/progress')
@login_required
def api_progress():
    """
    API endpoint for getting user's progress data
    """
    try:
        # Get overall progress
        total_terms = MedicalTerm.query.count()
        studied_terms = UserTermProgress.query.filter_by(user_id=current_user.id).count()
        mastered_terms = UserTermProgress.query.filter(
            and_(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.mastery_level >= 4
            )
        ).count()
        
        # Get today's due reviews
        today_due = UserTermProgress.query.filter(
            and_(
                UserTermProgress.user_id == current_user.id,
                UserTermProgress.next_review <= datetime.now(timezone.utc)
            )
        ).count()
        
        return jsonify({
            'success': True,
            'total_terms': total_terms,
            'studied_terms': studied_terms,
            'mastered_terms': mastered_terms,
            'today_due': today_due,
            'progress_percent': int((studied_terms / total_terms * 100)) if total_terms > 0 else 0
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting progress: {e}")
        return jsonify({'error': 'Failed to get progress'}), 500
