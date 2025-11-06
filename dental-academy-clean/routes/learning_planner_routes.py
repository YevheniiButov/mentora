from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from models import DiagnosticSession, PersonalLearningPlan
from utils.serializers import clean_for_template
from translations import get_translation
from utils.domain_mapping import ALL_BIG_DOMAINS, OLD_TO_NEW_DOMAIN_MAPPING, get_domain_name
from utils.diagnostic_data_manager import DiagnosticDataManager
import json

learning_planner_bp = Blueprint('learning_planner', __name__)

@learning_planner_bp.route('/learning-planner/<int:plan_id>')
@login_required
def learning_planner(plan_id):
    """Redirect to coming soon page"""
    from flask import redirect, url_for, g
    # Redirect to learning map instead of coming soon
    return redirect(url_for('learning_map_bp.learning_map', lang=g.get('lang', 'nl', path_id='irt'))) 