from flask import render_template, redirect
from app.dashboard import dashboard

@dashboard.route('/')
def dashboard_home():
    return "Hey there"