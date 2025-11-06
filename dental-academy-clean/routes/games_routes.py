# routes/games_routes.py
from flask import Blueprint, render_template, session, g
from flask_login import login_required

games_bp = Blueprint('games', __name__, url_prefix='/games')

SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@games_bp.before_request
def before_request():
    """Set language for all game routes"""
    lang = session.get('lang', DEFAULT_LANGUAGE)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    g.lang = lang

@games_bp.route('/sudoku')
@login_required
def sudoku():
    """Sudoku game page"""
    return render_template('games/sudoku.html', lang=g.lang)

@games_bp.route('/memory')
@login_required
def memory():
    """Medical Memory game page"""
    return render_template('games/memory.html', lang=g.lang)

@games_bp.route('/quiz')
@login_required
def quiz():
    """Quick Quiz game page"""
    return render_template('games/quiz.html', lang=g.lang)

@games_bp.route('/dentist-dash')
@login_required
def dentist_dash():
    """Dentist Dash - 8-bit platformer game"""
    return render_template('games/dentist_dash.html', lang=g.lang)
