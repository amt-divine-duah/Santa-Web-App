from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.auth import auth 
from app.auth.forms import LoginForm, RegisterForm
from models import User

# login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
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
        flash("Account registered successfully", "success")
        return redirect(url_for('auth.register'))
    
    
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