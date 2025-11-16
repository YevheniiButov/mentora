"""
Medical Terms Review Routes
Public routes for reviewing medical terms by difficulty level
Designed for content review and quality assessment
"""

from flask import Blueprint, render_template, request, jsonify, make_response, g, session
from models import MedicalTerm, db
from sqlalchemy import func
import csv
from io import StringIO

# Create blueprint with language support
medical_terms_bp = Blueprint('medical_terms', __name__, url_prefix='/<string:lang>/medical-terms')

SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@medical_terms_bp.before_request
def before_request_medical_terms():
    """Handle language for all medical terms routes"""
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') or DEFAULT_LANGUAGE
    
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@medical_terms_bp.context_processor
def inject_lang_medical_terms():
    """Add lang to template context"""
    return dict(lang=getattr(g, 'lang', DEFAULT_LANGUAGE))


@medical_terms_bp.route('/')
def index(lang):
    """
    Main page - select difficulty level and view mode
    Public access - no login required
    """
    # Get statistics by difficulty
    stats = db.session.query(
        MedicalTerm.difficulty,
        func.count(MedicalTerm.id).label('count')
    ).group_by(MedicalTerm.difficulty).all()
    
    difficulty_stats = {stat.difficulty: stat.count for stat in stats}
    
    # Get all categories
    categories = db.session.query(MedicalTerm.category).distinct().all()
    category_list = [cat[0] for cat in categories]
    
    return render_template('medical_terms/index.html',
                         difficulty_stats=difficulty_stats,
                         categories=category_list,
                         lang=lang)


@medical_terms_bp.route('/review')
def review(lang):
    """
    Review terms in table format
    Filters: difficulty, category
    """
    difficulty = request.args.get('difficulty', type=int)
    category = request.args.get('category', type=str)
    
    # Build query
    query = MedicalTerm.query
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    # Order by term
    terms = query.order_by(MedicalTerm.term_nl).all()
    
    # Get available categories for filter
    categories = db.session.query(MedicalTerm.category).distinct().all()
    category_list = [cat[0] for cat in categories]
    
    return render_template('medical_terms/review.html',
                         terms=terms,
                         selected_difficulty=difficulty,
                         selected_category=category,
                         categories=category_list,
                         lang=lang)


@medical_terms_bp.route('/cards')
def cards(lang):
    """
    Review terms in flashcard format
    One term at a time, can flip to see translations
    """
    difficulty = request.args.get('difficulty', type=int)
    category = request.args.get('category', type=str)
    
    # Build query
    query = MedicalTerm.query
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    # Order by term
    terms = query.order_by(MedicalTerm.term_nl).all()
    
    # Convert to dicts for JSON serialization
    terms_dicts = [
        {
            'id': term.id,
            'term_nl': term.term_nl,
            'definition_nl': term.definition_nl,
            'term_en': term.term_en,
            'term_ru': term.term_ru,
            'term_uk': term.term_uk,
            'term_es': term.term_es,
            'term_pt': term.term_pt,
            'term_tr': term.term_tr,
            'term_fa': term.term_fa,
            'term_ar': term.term_ar,
            'category': term.category,
            'difficulty': term.difficulty,
            'frequency': term.frequency
        }
        for term in terms
    ]
    
    return render_template('medical_terms/cards.html',
                         terms=terms_dicts,
                         selected_difficulty=difficulty,
                         selected_category=category,
                         lang=lang)


@medical_terms_bp.route('/export')
def export(lang):
    """
    Export terms to CSV
    Includes all translations and metadata
    """
    difficulty = request.args.get('difficulty', type=int)
    category = request.args.get('category', type=str)
    
    # Build query
    query = MedicalTerm.query
    
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    
    if category:
        query = query.filter_by(category=category)
    
    terms = query.order_by(MedicalTerm.term_nl).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Term (NL)',
        'Definition (NL)',
        'English',
        'Russian',
        'Ukrainian',
        'Spanish',
        'Portuguese',
        'Turkish',
        'Persian',
        'Arabic',
        'Category',
        'Difficulty',
        'Frequency'
    ])
    
    # Data
    for term in terms:
        writer.writerow([
            term.term_nl,
            term.definition_nl or '',
            term.term_en or '',
            term.term_ru or '',
            term.term_uk or '',
            term.term_es or '',
            term.term_pt or '',
            term.term_tr or '',
            term.term_fa or '',
            term.term_ar or '',
            term.category,
            term.difficulty,
            term.frequency
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    
    # Filename
    filename_parts = ['medical_terms']
    if difficulty:
        filename_parts.append(f'difficulty_{difficulty}')
    if category:
        filename_parts.append(category)
    filename = '_'.join(filename_parts) + '.csv'
    
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


@medical_terms_bp.route('/api/stats')
def api_stats(lang):
    """
    API endpoint for statistics
    Returns term counts by difficulty and category
    """
    # Stats by difficulty
    difficulty_stats = db.session.query(
        MedicalTerm.difficulty,
        func.count(MedicalTerm.id).label('count')
    ).group_by(MedicalTerm.difficulty).all()
    
    # Stats by category
    category_stats = db.session.query(
        MedicalTerm.category,
        func.count(MedicalTerm.id).label('count')
    ).group_by(MedicalTerm.category).all()
    
    return jsonify({
        'difficulty': {str(stat.difficulty): stat.count for stat in difficulty_stats},
        'category': {stat.category: stat.count for stat in category_stats},
        'total': MedicalTerm.query.count()
    })

