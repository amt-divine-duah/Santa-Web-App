from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.auth import auth 
from app.auth.forms import LoginForm, RecoverPasswordForm, RegisterForm, ResetPasswordForm
from models import User
from app.auth.utils.emails import send_email 

# login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_home'))
    form = LoginForm()
    # Check for valid form submission
    if form.validate_on_submit():
        # Query for user
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # Get the next query parameter
            next = request.args.get('next')
            if next is None:
                next = url_for('dashboard.dashboard_home')
            return redirect(next)
        else:
            flash("Invalid user credentials. Try Again", "danger")
            return redirect(url_for('auth.login'))
    
    context = {
        'title': 'Login',
        'form': form,
    }
    return render_template('auth/login.html', **context)

# register route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_home'))
    form = RegisterForm()
    # Check for valid form submission and store data in db
    if form.validate_on_submit():
        username = form.username.data
        email=form.email.data
        password = form.password.data
        user_terms = form.terms.data
        
        # Create user object to and add to database
        user = User(username=username, email=email, password=password, user_terms=user_terms)
        db.session.add(user)
        db.session.commit()
        # Generate token
        token = user.generate_confirmation_token()
        # Send confirmation email
        send_email.delay(to=email, subject='Confirmation Email', template='auth/emails/confirm_email', 
                        user=username, token=token)
        flash("Account registered successfully", "success")
        return redirect(url_for('auth.login'))
    
    context = {
        'title': 'Register',
        'form':form
    }
    return render_template('auth/register.html', **context)

# Logout route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

# Account confirmation route
@auth.route('/confirm_account/<token>')
@login_required
def confirm_account(token):
    if current_user.confirmed:
        return redirect(url_for('dashboard.dashboard_home'))
    if current_user.confirm_token(token):
        db.session.commit()
        flash("Account has been successfully confirmed.", "success")
    else:
        flash("The confirmation link is invalid or has expired", "danger")
    return redirect(url_for('dashboard.dashboard_home'))

# Filter unconfirmed accounts
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed_account'))
    
# Unconfirmed accounts
@auth.route('/unconfirmed_account')
def unconfirmed_account():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('dashboard.dashboard_home'))
    
    context = {
        'title': 'Unconfirmed Account'
    }
    return render_template('auth/unconfirmed_account.html', **context)

# Resend confirmation email
@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email.delay(to=current_user.email, subject='Confirm Your Account', 
               template='auth/emails/confirm_email', user=current_user.username, token=token)
    flash("A new confirmation email has been sent to you by email", "success")
    return redirect(url_for('dashboard.dashboard_home'))

# Password recover route
@auth.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard.dashboard_home'))
    
    form = RecoverPasswordForm()
    # Check for valid form submission
    if form.validate_on_submit():
        email = form.email.data
        # Query for user
        user = User.query.filter_by(email=email.lower()).first()
        if user:
            # Generate token and send email to user
            token = user.generate_password_reset_token()
            send_email.delay(to=user.email, subject='Reset Password', 
                       template='auth/emails/reset_password', user=user.username, token=token)
            flash("An email with instructions to reset password has been sent", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Email address cannot be found. Please check and try again.", "danger")
            return redirect(url_for('auth.recover_password'))
    context = {
        'title': 'Recover Password',
        'form': form
    }
    return render_template('auth/recover_password.html', **context)

# Password reset route
@auth.route('/reset_password/<token>', methods=['GET', 'POST']) 
def reset_password(token):
    
    if not current_user.is_anonymous:
        return redirect(url_for('dashboard.dashboard_home'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.password.data
        if User.confirm_password_reset_token(token, new_password=new_password):
            db.session.commit()
            flash("Password reset completed successfully", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Password reset could not be completed. Try again", "success")
            return redirect(url_for('auth.login'))
    context = {
        'title': 'Reset Password',
        'form': form
    }
    return render_template('auth/reset_password.html', **context)