from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import EqualTo, ValidationError
from models import User

# Registration Form
class RegisterForm(FlaskForm):
    username = StringField('Username')
    email = EmailField('Email')
    password = PasswordField('Password', validators=[EqualTo('confirm_password', 
                                                             message="Passwords must match")])
    confirm_password = PasswordField('Confirm Password')
    terms = BooleanField('Terms')
    
    # Prevent duplicate username
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError("Username already exists. Choose a different one")
        
    # Prevent duplicate email
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("Email already exists. Choose a different one")

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = StringField('Password')
    remember_me = BooleanField('Remember Me')
    
# Recover Password Form
class RecoverPasswordForm(FlaskForm):
    email = EmailField('Email')
    
# Password Reset Form
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Pasword', 
                                     validators=[EqualTo('password', message="Passwords must match")])
    
# Change Email form
class ChangeEmailForm(FlaskForm):
    old_email = EmailField('Old Email')
    password = PasswordField('Password')
    new_email = EmailField('New Email')
    
    def validate_old_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError("Email address cannot be found")
    
    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email address has been already registered")
        
# Update Password Form
class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password')
    new_password = PasswordField('New Password')
    confirm_new_password = PasswordField('Confirm New Password', 
                                         validators=[EqualTo('new_password')])