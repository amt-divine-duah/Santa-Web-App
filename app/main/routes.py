from flask import redirect, url_for, render_template
from app.main import main

# Homepage route
@main.route('/')
def home():
    
    context = {
        'title': 'Blog Page'
    }
    return render_template('main/index.html', **context)