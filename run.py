import os
from app import create_app, db
from flask_migrate import Migrate
from models import User, Role, Permission, Post

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


# Make shell context
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post)


