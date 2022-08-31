from flask import render_template, redirect, url_for
from flask_login import login_required
from app.dashboard import dashboard

@dashboard.route('/')
@login_required
def dashboard_home():
    
    context = {
        'title': 'Home',
        
    }
    return render_template('dashboard/dashboard.html', **context)