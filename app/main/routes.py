from flask import redirect, url_for
from app.main import main

# Homepage route
@main.route('/')
def home():
    return redirect(url_for('dashboard.dashboard_home'))