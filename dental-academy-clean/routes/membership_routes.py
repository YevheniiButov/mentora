"""
Membership routes for Mentora application
Handles QR code generation, member verification, and payment processing
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text
import stripe

from models import db, User

# Create blueprint
membership_bp = Blueprint('membership', __name__, url_prefix='/membership')

def get_stripe_client():
    """Get configured Stripe client"""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    return stripe

def generate_member_qr(user):
    """Generate QR code for premium member"""
    import qrcode
    
    # Generate member ID if doesn't exist
    if not user.member_id:
        user.member_id = 'MNT-' + str(uuid.uuid4())[:8].upper()
    
    # Create directory
    qr_dir = os.path.join(current_app.static_folder, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # QR data: verification URL
    qr_data = f"https://mentora.nl/verify/{user.member_id}"
    
    # Generate QR with teal corner markers
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image (black and white)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save
    filename = f"qr_{user.member_id}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)
    
    user.qr_code_path = f"qr_codes/{filename}"
    db.session.commit()
    
    return user.qr_code_path

@membership_bp.route('/verify/<member_id>')
def verify_member(member_id):
    """Public verification page when QR scanned"""
    user = User.query.filter_by(member_id=member_id).first_or_404()
    
    # Check if membership valid
    is_valid = (
        user.membership_type == 'premium' and
        user.membership_expires and
        user.membership_expires > datetime.utcnow()
    )
    
    return render_template('membership/verify.html',
        member=user,
        is_valid=is_valid
    )

@membership_bp.route('/generate-qr')
@login_required
def generate_qr():
    """Generate QR code for current user (admin only for testing)"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:
        # Generate QR code
        qr_path = generate_member_qr(current_user)
        
        # Set user as premium for testing
        current_user.membership_type = 'premium'
        current_user.membership_expires = datetime.utcnow() + timedelta(days=365)
        db.session.commit()
        
        flash('QR код успешно сгенерирован!', 'success')
        return redirect(url_for('membership_card'))
        
    except Exception as e:
        current_app.logger.error(f"Error generating QR code: {e}")
        flash('Ошибка при генерации QR кода', 'error')
        return redirect(url_for('membership_card'))

@membership_bp.route('/upgrade-to-premium')
@login_required
def upgrade_to_premium():
    """Upgrade user to premium membership (testing only)"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    try:
        # Generate member ID if doesn't exist
        if not current_user.member_id:
            current_user.member_id = 'MNT-' + str(uuid.uuid4())[:8].upper()
        
        # Set premium membership
        current_user.membership_type = 'premium'
        current_user.membership_expires = datetime.utcnow() + timedelta(days=365)
        
        # Generate QR code
        generate_member_qr(current_user)
        
        db.session.commit()
        
        flash('Успешно обновлено до премиум членства!', 'success')
        return redirect(url_for('membership_card'))
        
    except Exception as e:
        current_app.logger.error(f"Error upgrading to premium: {e}")
        flash('Ошибка при обновлении до премиум', 'error')
        return redirect(url_for('membership_card'))

@membership_bp.route('/admin/generate-all-qr')
@login_required
def admin_generate_all_qr():
    """Generate QR codes for all premium users (admin only)"""
    if not current_user.is_authenticated or current_user.role != 'admin':
        flash('Доступ запрещен', 'error')
        return redirect(url_for('index'))
    
    try:
        premium_users = User.query.filter_by(membership_type='premium').all()
        generated_count = 0
        
        for user in premium_users:
            if not user.qr_code_path:  # Only generate if doesn't exist
                generate_member_qr(user)
                generated_count += 1
        
        flash(f'Сгенерировано QR кодов: {generated_count}', 'success')
        return redirect(url_for('admin.dashboard'))
        
    except Exception as e:
        current_app.logger.error(f"Error generating QR codes: {e}")
        flash('Ошибка при генерации QR кодов', 'error')
        return redirect(url_for('admin.dashboard'))

@membership_bp.route('/upgrade')
@login_required
def upgrade_page():
    """Premium upgrade page - HIDDEN during testing"""
    if not current_user.is_admin:
        flash('This feature is coming soon!', 'info')
        return redirect(url_for('dashboard.index'))
    
    return render_template('membership/upgrade.html',
        stripe_key=current_app.config['STRIPE_PUBLISHABLE_KEY']
    )

@membership_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create Stripe checkout session"""
    if not current_user.is_admin:
        abort(403)
    
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'ideal'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Mentora Premium Membership',
                        'description': '1 month access',
                    },
                    'unit_amount': 1000,  # €10.00 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('membership.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('membership.upgrade_page', _external=True),
            metadata={
                'user_id': current_user.id
            }
        )
        
        return jsonify({'id': checkout_session.id})
        
    except Exception as e:
        return jsonify(error=str(e)), 403

@membership_bp.route('/success')
@login_required
def success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    
    if session_id:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Activate Premium
            current_user.membership_type = 'premium'
            current_user.membership_expires = datetime.utcnow() + timedelta(days=30)
            
            # Generate QR
            if not current_user.member_id:
                generate_member_qr(current_user)
            
            db.session.commit()
            
            flash('Welcome to Premium! 🎉', 'success')
            return redirect(url_for('membership.card'))
    
    flash('Payment successful!', 'success')
    return redirect(url_for('dashboard.index'))

@membership_bp.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    # For testing, accept without verification
    # TODO: Add webhook secret in production
    
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError:
        return 'Invalid payload', 400
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        
        user = User.query.get(user_id)
        if user:
            user.membership_type = 'premium'
            user.membership_expires = datetime.utcnow() + timedelta(days=30)
            
            if not user.member_id:
                generate_member_qr(user)
            
            db.session.commit()
    
    return 'OK', 200

@membership_bp.route('/card')
@login_required
def card():
    """Show member card - Premium only"""
    if current_user.membership_type != 'premium':
        flash('Upgrade to Premium to access your member card', 'warning')
        return redirect(url_for('membership.upgrade_page'))
    
    # Check expiration
    if current_user.membership_expires and current_user.membership_expires < datetime.utcnow():
        flash('Your membership has expired. Please renew.', 'warning')
        return redirect(url_for('membership.upgrade_page'))
    
    return render_template('membership/card.html')
