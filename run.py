from pickle import TRUE
from app import create_app
import os

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')


