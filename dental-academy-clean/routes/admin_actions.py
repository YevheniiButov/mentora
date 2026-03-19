"""
Admin Actions Routes
Handles administrative tasks like candidate import from Excel/CSV.
"""
import io
import logging
import pandas as pd
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from extensions import db
from models import User

logger = logging.getLogger(__name__)

admin_actions_bp = Blueprint('admin_actions', __name__, url_prefix='/admin')

@admin_actions_bp.route('/import-candidates', methods=['GET', 'POST'])
@login_required
def import_candidates():
    """Import candidates from Excel or CSV file."""
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        try:
            # Read file into pandas DataFrame
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                flash('Unsupported file format. Please upload CSV or Excel.', 'danger')
                return redirect(request.url)

            # Mapping configuration
            mapping = {
                'Email Address': 'email',
                'Full Name': 'full_name',
                'What is your profession?': 'profession',
                'Medical Specialization': 'specialization',
                'Current Dutch Level': 'dutch_level',
                'Work Experience (Years/Desc)': 'work_experience',
                'Legal Status in EU': 'legal_status',
                'Do you need housing?': 'housing_needed',
                'Registered for BIG-exam?': 'big_exam_registered',
                'Mobile Number': 'phone'
            }

            imported_count = 0
            updated_count = 0
            errors = []

            for _, row in df.iterrows():
                try:
                    email = str(row.get('Email Address', '')).strip().lower()
                    if not email or '@' not in email:
                        continue

                    # Find or create user
                    user = User.query.filter_by(email=email).first()
                    is_new = False
                    if not user:
                        user = User(email=email)
                        db.session.add(user)
                        is_new = True
                    
                    # Map fields
                    # 1. Full Name split
                    full_name = str(row.get('Full Name', '')).strip()
                    if full_name:
                        parts = full_name.split(' ', 1)
                        user.first_name = parts[0]
                        user.last_name = parts[1] if len(parts) > 1 else ''

                    # 2. Simple mappings
                    user.profession = str(row.get('What is your profession?', '')).strip() or user.profession
                    user.specialization = str(row.get('Medical Specialization', '')).strip() or user.specialization
                    user.dutch_level = str(row.get('Current Dutch Level', '')).strip() or user.dutch_level
                    user.work_experience = str(row.get('Work Experience (Years/Desc)', '')).strip() or user.work_experience
                    user.legal_status = str(row.get('Legal Status in EU', '')).strip() or user.legal_status
                    user.phone = str(row.get('Mobile Number', '')).strip() or user.phone
                    user.big_exam_registered = str(row.get('Registered for BIG-exam?', '')).strip() or user.big_exam_registered

                    # 3. Boolean mapping for housing
                    housing = str(row.get('Do you need housing?', '')).strip().lower()
                    if 'yes' in housing:
                        user.housing_needed = 'yes'
                    elif 'no' in housing:
                        user.housing_needed = 'no'
                    
                    # 4. Force onboarding
                    user.registration_completed = False
                    
                    if is_new:
                        imported_count += 1
                        # Set a default role
                        user.role = 'user'
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Error processing row {email}: {str(e)}")

            db.session.commit()
            flash(f'Successfully imported {imported_count} new and updated {updated_count} existing candidates.', 'success')
            if errors:
                for err in errors[:5]: # Show first 5 errors
                    flash(err, 'warning')

            return redirect(url_for('hub.users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Import error: {str(e)}", exc_info=True)
            flash(f'Import failed: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('admin/import_candidates.html')
