import os
from app import create_app, db, cli
from flask_migrate import Migrate
from models import User, Role, Permission, Post, Follow
from flask import redirect, url_for, session
from flask_babel import get_locale

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
cli.register(app)


@app.route('/')
def home():
    if not session.get('lang_code', None):
        get_locale()
    return redirect(url_for('main.home'))

# Make shell context
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Follow=Follow)

# unit test launcher
@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


