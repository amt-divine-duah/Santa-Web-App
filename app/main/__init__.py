from flask import Blueprint, session
from models import Permission

main = Blueprint("main", __name__)

@main.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', session['lang_code'])
    
@main.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['lang_code'] = values.pop('lang_code')

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from app.main import routes