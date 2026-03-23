from flask import Blueprint, render_template, redirect, url_for, g

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html', lang=g.get('lang', 'en'))

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html', lang=g.get('lang', 'en'))

@auth_bp.route('/quick-register')
def quick_register():
    return render_template('auth/quick_register.html', lang=g.get('lang', 'en'))

@auth_bp.route('/logout')
def logout():
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))
