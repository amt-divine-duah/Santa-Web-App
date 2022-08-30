from flask import render_template, redirect, url_for
from app.dashboard import dashboard

@dashboard.route('/')
def dashboard_home():
    
    context = {
        'title': 'Home',
        
    }
    return render_template('dashboard/dashboard.html', **context)