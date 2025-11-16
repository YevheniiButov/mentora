# routes/dutch_reading_routes.py
# Dutch Reading Page Routes (non-API)

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from flask_login import login_required, current_user
from extensions import db
from models import DutchPassage, DutchQuestion, UserDutchProgress
from datetime import datetime, timezone, timedelta

dutch_reading_bp = Blueprint('dutch_reading', __name__, url_prefix='/dutch')

# Поддерживаемые языки интерфейса
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'nl'  # По умолчанию нидерландский интерфейс

@dutch_reading_bp.before_request
def before_request_dutch_reading():
    """Обработка языка для всех маршрутов dutch_reading"""
    # Получаем язык из сессии или используем дефолт
    lang = session.get('lang') or getattr(g, 'lang', None) or DEFAULT_LANGUAGE
    
    # Валидируем язык
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # Устанавливаем в g и session
    g.lang = lang
    if session.get('lang') != lang:
        session['lang'] = lang

@dutch_reading_bp.route('/practice')
@dutch_reading_bp.route('/practice/<int:passage_id>')
@login_required
def practice(passage_id=None):
    """Dutch Reading practice page"""
    # Проверяем премиум-доступ (если premium=true в URL, пропускаем проверку диагностики)
    is_premium_access = request.args.get('premium') == 'true'
    
    # Получаем язык из сессии или g
    lang = getattr(g, 'lang', None) or session.get('lang', DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # КРИТИЧНО: Проверяем, прошёл ли пользователь диагностику (если не премиум)
    if not is_premium_access:
        from utils.diagnostic_check import check_diagnostic_completed, get_diagnostic_redirect_url
        if not check_diagnostic_completed(current_user.id):
            from flask import flash, current_app
            flash('Voor het lezen van Nederlandse teksten moet je eerst de diagnostische test doen.', 'info')
            current_app.logger.info(f"User {current_user.id} redirected to diagnostic from dutch practice (not premium)")
            return redirect(get_diagnostic_redirect_url(lang))
    
    # If no passage_id provided, get today's assignment or random passage
    if passage_id is None:
        # For premium access, skip assignment logic and get random passage
        if is_premium_access:
            # Get any available passage for premium users
            available_passages = DutchPassage.query.all()
            if not available_passages:
                from flask import flash
                flash('Er zijn nog geen Nederlandse teksten beschikbaar.', 'warning')
                return redirect(f'/{lang}/learning-map')
            import random
            passage = random.choice(available_passages)
        else:
            # Try to get today's fixed assignment for Dutch
            from utils.individual_plan_helpers import select_dutch_passage_for_today
            passage = select_dutch_passage_for_today(current_user)
            if not passage:
                # No assignment - get a random passage user hasn't completed recently
                # Get passages user hasn't done in last 7 days
                week_ago = datetime.now(timezone.utc) - timedelta(days=7)
                completed_passage_ids = [p.passage_id for p in UserDutchProgress.query.filter(
                    UserDutchProgress.user_id == current_user.id,
                    UserDutchProgress.completed_at >= week_ago
                ).all()]
                
                # Get a passage that's not in completed list
                available_passages = DutchPassage.query.filter(
                    ~DutchPassage.id.in_(completed_passage_ids) if completed_passage_ids else True
                ).all()
                
                if not available_passages:
                    # All passages done recently - pick any
                    available_passages = DutchPassage.query.all()
                
                if not available_passages:
                    # No passages in DB yet
                    from flask import flash
                    flash('Er zijn nog geen Nederlandse teksten beschikbaar.', 'warning')
                    return redirect(f'/{lang}/learning-map')
                
                # Pick random passage
                import random
                passage = random.choice(available_passages)
        
        passage_id = passage.id
    else:
        passage = DutchPassage.query.get_or_404(passage_id)
    
    # Check if user has already completed this passage today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    completed_today = UserDutchProgress.query.filter(
        UserDutchProgress.user_id == current_user.id,
        UserDutchProgress.passage_id == passage_id,
        UserDutchProgress.completed_at >= today_start,
        UserDutchProgress.completed_at < today_end
    ).first()
    
    # If completed, allow practice again (no restriction)
    # User can practice the same passage multiple times
    
    return render_template(
        'dutch_reading.html',
        passage=passage,
        lang=lang,
        completed_today=completed_today
    )


@dutch_reading_bp.route('/list')
@login_required
def list_passages():
    """List all available Dutch passages"""
    lang = getattr(g, 'lang', None) or session.get('lang', DEFAULT_LANGUAGE)
    
    # Get all passages
    passages = DutchPassage.query.order_by(DutchPassage.difficulty, DutchPassage.title).all()
    
    # Get user's progress for each passage
    user_progress = {}
    for passage in passages:
        progress = UserDutchProgress.query.filter_by(
            user_id=current_user.id,
            passage_id=passage.id
        ).order_by(UserDutchProgress.completed_at.desc()).first()
        
        if progress:
            user_progress[passage.id] = {
                'completed': True,
                'score': progress.score,
                'total': progress.total_questions,
                'percentage': int((progress.score / progress.total_questions * 100)) if progress.total_questions > 0 else 0
            }
        else:
            user_progress[passage.id] = {'completed': False}
    
    return render_template(
        'dutch_reading_list.html',
        passages=passages,
        user_progress=user_progress,
        lang=lang
    )

