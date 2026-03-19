import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, redirect, url_for, jsonify, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func
import pandas as pd
import io

from extensions import db
from models import User, DiagnosticSession
from routes.admin_users_export import _build_query

logger = logging.getLogger(__name__)

hub_bp = Blueprint('hub', __name__, url_prefix='/hub')


def _require_admin():
    """Return 403 JSON if caller is not an admin."""
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    return None


# ─── Dashboard ────────────────────────────────────────────────────────────────
@hub_bp.route('/')
@hub_bp.route('/dashboard')
@login_required
def dashboard():
    err = _require_admin()
    if err:
        return err

    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    stats = {
        'total_users':    User.query.filter_by(is_deleted=False, role='user').count(),
        'new_this_week':  User.query.filter(
                              User.is_deleted == False,
                              User.role == 'user',
                              User.created_at >= week_ago,
                          ).count(),
        'with_big':       User.query.filter(
                              User.is_deleted == False,
                              User.role == 'user',
                              User.big_exam_registered == 'registered',
                          ).count(),
        'need_housing':   User.query.filter(
                              User.is_deleted == False,
                              User.role == 'user',
                              User.housing_needed == 'yes',
                          ).count(),
        # Add Diagnostic statistics
        'sessions_completed': DiagnosticSession.query.filter_by(status='completed').count(),
    }

    # Average readiness score across users
    avg_readiness = db.session.query(func.avg(DiagnosticSession.current_ability)).filter_by(status='completed').scalar() or 0
    stats['avg_readiness'] = round((avg_readiness + 1.5) / 3 * 100, 1) if avg_readiness else 0

    # Profession breakdown for mini chart
    professions = (
        db.session.query(User.profession, func.count(User.id))
        .filter(User.is_deleted == False, User.role == 'user', User.profession.isnot(None))
        .group_by(User.profession)
        .order_by(func.count(User.id).desc())
        .limit(6)
        .all()
    )

    # Dutch level breakdown
    dutch_levels = (
        db.session.query(User.dutch_level, func.count(User.id))
        .filter(User.is_deleted == False, User.role == 'user', User.dutch_level.isnot(None))
        .group_by(User.dutch_level)
        .all()
    )

    return render_template(
        'hub/dashboard.html',
        stats=stats,
        professions=professions,
        dutch_levels=dutch_levels,
    )


# ─── Users list ───────────────────────────────────────────────────────────────
@hub_bp.route('/users')
@login_required
def users():
    err = _require_admin()
    if err:
        return err

    args = request.args
    query = _build_query(args)

    # Pagination
    page = args.get('page', 1, type=int)
    per_page = 20
    
    # Base query for users
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Attach diagnostic scores to each user object (optimized for the current page)
    user_ids = [u.id for u in pagination.items]
    latest_sessions = db.session.query(
        DiagnosticSession.user_id,
        func.max(DiagnosticSession.completed_at).label('max_date')
    ).filter(
        DiagnosticSession.user_id.in_(user_ids),
        DiagnosticSession.status == 'completed'
    ).group_by(DiagnosticSession.user_id).subquery()

    scores = db.session.query(
        DiagnosticSession.user_id,
        DiagnosticSession.current_ability
    ).join(
        latest_sessions,
        (DiagnosticSession.user_id == latest_sessions.c.user_id) &
        (DiagnosticSession.completed_at == latest_sessions.c.max_date)
    ).all()

    scores_map = {s.user_id: round((s.current_ability + 1.5) / 3 * 100, 1) for s in scores}
    
    for user in pagination.items:
        user.latest_readiness = scores_map.get(user.id)


    # Unique values for filter dropdowns
    def distinct_values(col):
        rows = db.session.query(col).filter(col.isnot(None)).distinct().all()
        return sorted([r[0] for r in rows if r[0]])

    filter_options = {
        'professions':    distinct_values(User.profession),
        'dutch_levels':   ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'native'],
        'legal_statuses': distinct_values(User.legal_status),
        'housing_opts':   distinct_values(User.housing_needed),
        'big_exam_opts':  distinct_values(User.big_exam_registered),
    }

    return render_template(
        'hub/users.html',
        users=pagination.items,
        pagination=pagination,
        filter_options=filter_options,
        active_filters=args,
        total_filtered=pagination.total,
    )


# ─── Import Candidates ────────────────────────────────────────────────────────
@hub_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_candidates():
    err = _require_admin()
    if err:
        return err

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file uploaded', 'error')
            return redirect(request.url)

        try:
            filename = file.filename.lower()
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                flash('Unsupported file format. Please use CSV or Excel.', 'error')
                return redirect(request.url)

            # Enhanced mapping with exact multi-language headers from the user
            mapping = {
                'email': [
                    'Адрес электронной почты', 
                    'Email Address', 'Email', 'Электронная почта', 'E-mail'
                ],
                'full_name': [
                    'Full Name | Volledige naam | Повне ім\'я',
                    'Full Name', 'Name', 'ФИО', 'Имя и фамилия'
                ],
                'phone': [
                    'Contact Number | Telefoonnummer | Номер телефону (WhatsApp)',
                    'Phone Number', 'Phone', 'Номер телефона', 'Телефон'
                ],
                'city': [
                    'Current Location in NL (City) | Huidige woonplaats | Місце проживання в Нідерландах',
                    'City', 'Location', 'Город', 'Місто'
                ],
                'diploma_status': [
                    'Do you have your original Diploma with you? | Heeft u uw originele diploma bij u? | Чи маєте ви оригінал диплома з собою?',
                    'Diploma', 'Original Diploma'
                ],
                'work_as_assistant': [
                    'Are you willing to work as a Medical Assistant while studying for your license? | Bent u bereid om als medisch assistent te werken tijdens uw studie? | Чи готові ви працювати асистентом лікаря під час підготовки до іспитів?',
                    'Medical Assistant', 'Work as assistant'
                ],
                'housing_needed': [
                    'Do you require housing support from a partner hospital? | Heeft u huisvesting nodig via een partnerziekenhuis? | Чи потребуєте ви житлової поддержки від лікарні-партнера?',
                    'Housing', 'Housing support'
                ],
                'profession': ['What is your profession?', 'Profession', 'Профессия'],
                'dutch_level': [
                    'Dutch Language Level | Nederlands taalniveau | Рівень володіння нідерландською мовою',
                    'What is your level of Dutch?', 'Dutch level', 'Уровень голландского'
                ],
                'legal_status': ['What is your legal status in the Netherlands?', 'Legal status', 'Легальный статус']
            }

            def find_col(aliases, df_cols):
                # Try exact match first
                for alias in aliases:
                    for col in df_cols:
                        if alias.lower() == str(col).strip().lower():
                            return col
                # Try partial match if no exact match found
                for alias in aliases:
                    for col in df_cols:
                        if alias.lower() in str(col).lower():
                            return col
                return None

            # Resolve actual column names from the file
            resolved_mapping = {}
            for key, aliases in mapping.items():
                resolved_mapping[key] = find_col(aliases, df.columns)

            imported = 0
            updated = 0

            for _, row in df.iterrows():
                email_col = resolved_mapping.get('email')
                email = row.get(email_col) if email_col else None
                
                if not email or pd.isna(email):
                    continue
                
                email = str(email).strip().lower()
                user = User.query.filter_by(email=email).first()
                if not user:
                    user = User(email=email)
                    db.session.add(user)
                    imported += 1
                else:
                    updated += 1

                # Full Name logic
                fn_col = resolved_mapping.get('full_name')
                full_name = str(row.get(fn_col, '')) if fn_col else ''
                if full_name and full_name != 'nan':
                    parts = full_name.split(' ', 1)
                    user.first_name = parts[0]
                    user.last_name = parts[1] if len(parts) > 1 else ''

                # Map other fields
                for field in ['profession', 'specialization', 'dutch_level', 'work_experience', 'legal_status', 'phone', 'city', 'diploma_status']:
                    col = resolved_mapping.get(field)
                    if col and not pd.isna(row.get(col)):
                        setattr(user, field, str(row.get(col)))
                
                # Boolean-ish fields (mapping variants of Yes/No)
                def map_boolean(col_name, user_attr):
                    col = resolved_mapping.get(col_name)
                    if col:
                        val = str(row.get(col, '')).lower()
                        if any(x in val for x in ['yes', 'да', 'так', 'true', '1']):
                            setattr(user, user_attr, 'yes')
                        elif any(x in val for x in ['no', 'нет', 'ні', 'false', '0']):
                            setattr(user, user_attr, 'no')

                map_boolean('housing_needed', 'housing_needed')
                map_boolean('work_as_assistant', 'work_as_assistant')
                
                # Mark as imported from Google Form
                user.motivation = f"[Google Form Import] {filename}"
                user.registration_completed = False

            db.session.commit()
            if imported == 0 and updated == 0:
                flash('No candidates found in the file. Please check column headers.', 'warning')
            else:
                flash(f'Successfully imported {imported} and updated {updated} candidates.', 'success')
            return redirect(url_for('hub.users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f'Import error: {str(e)}')
            flash(f'Error during import: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('hub/import.html')

