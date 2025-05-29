# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField 
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    """Форма для входа пользователя."""
    email = StringField('Email',
                        validators=[DataRequired(message="Please enter your email address."),
                                    Email(message="Please enter a valid email address.")])
    password = PasswordField('Password',
                             validators=[DataRequired(message="Please enter your password.")])

    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Форма для регистрации нового пользователя."""
    name = StringField('Name',
                       validators=[DataRequired(message="Please enter your name.")])
    email = StringField('Email',
                        validators=[DataRequired(message="Please enter your email address."),
                                    Email(message="Please enter a valid email address.")])
    password = PasswordField('Password',
                             validators=[DataRequired(message="Please enter a password."),
                                         Length(min=6, message="Password must be at least 6 characters long.")])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(message="Please confirm your password."),
                                                 EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

# --- Форма для смены пароля ---
class ChangePasswordForm(FlaskForm):
    """Форма для смены пароля пользователя."""
    current_password = PasswordField('Current Password',
                                    validators=[DataRequired(message="Please enter your current password.")])
    new_password = PasswordField('New Password',
                                validators=[DataRequired(message="Please enter a new password."),
                                            Length(min=6, message="Password must be at least 6 characters long.")])
    confirm_password = PasswordField('Confirm New Password',
                                    validators=[DataRequired(message="Please confirm your new password."),
                                                EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')

# --- Другие формы (если понадобятся позже) ---
