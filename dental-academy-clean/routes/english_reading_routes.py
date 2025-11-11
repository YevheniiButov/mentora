# routes/english_reading_routes.py
# English Reading Page Routes (non-API)

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from flask_login import login_required, current_user
from extensions import db
from models import EnglishPassage, EnglishQuestion, UserEnglishProgress
from utils.individual_plan_helpers import select_english_passage_for_today

english_reading_bp = Blueprint('english_reading', __name__, url_prefix='/english')

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@english_reading_bp.before_request
def before_request_english_reading():
    """Обработка языка для всех маршрутов english_reading"""
    # Получаем язык из сессии или используем дефолт
    lang = session.get('lang') or getattr(g, 'lang', None) or DEFAULT_LANGUAGE
    
    # Валидируем язык
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # Устанавливаем в g и session
    g.lang = lang
    if session.get('lang') != lang:
        session['lang'] = lang

@english_reading_bp.route('/practice')
@english_reading_bp.route('/practice/<int:passage_id>')
@login_required
def practice(passage_id=None):
    """English Reading practice page"""
    # Получаем язык из сессии или g
    lang = getattr(g, 'lang', None) or session.get('lang', DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # If no passage_id provided, get today's fixed assignment
    if passage_id is None:
        # Use fixed daily assignment to ensure same passage for the day
        passage = select_english_passage_for_today(current_user, use_fixed_assignments=True)
        if not passage:
            # Use direct path instead of url_for to avoid BuildError
            return redirect(f'/{lang}/learning-map/irt')
        passage_id = passage.id
    else:
        passage = EnglishPassage.query.get_or_404(passage_id)
    
    # Check if user has already completed this passage today
    from datetime import datetime, timezone, timedelta
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    completed_today = UserEnglishProgress.query.filter(
        UserEnglishProgress.user_id == current_user.id,
        UserEnglishProgress.passage_id == passage_id,
        UserEnglishProgress.completed_at >= today_start,
        UserEnglishProgress.completed_at < today_end
    ).first()
    
    # If completed, show results or allow retry
    if completed_today:
        # Option: redirect to results or show message
        # For now, allow practice again
        pass
    
    # Получаем язык из g или session
    lang = getattr(g, 'lang', None) or session.get('lang', DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    return render_template(
        'english_reading.html',
        passage=passage,
        lang=lang
    )

