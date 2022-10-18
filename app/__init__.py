from flask import Flask, g, request, current_app
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from celery import Celery
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_babel import Babel

# Create instance of packages
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin()
mail = Mail()
moment = Moment()
ckeditor = CKEditor()
babel = Babel()


# Initialize Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

# Set login view and message
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

# Create application factory
def create_app(config_name):
    # Initialize the flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize the configuration object
    config[config_name].init_app(app)
    
    # Initialize all instances
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    babel.init_app(app)
    celery.conf.update(app.config)
    
    from models import MyAdminIndexView
    admin.init_app(app, index_view=MyAdminIndexView())
    
    # Attach Blueprints
    from app.dashboard import dashboard as dashboard_blueprint
    from app.auth import auth as auth_blueprint
    from app.main import main as main_blueprint
    from app.errors import errors as errors_blueprint
    from app.api import api as api_blueprint
    
    # Register Blueprints
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(errors_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')
    
    
    return app

@babel.localeselector
def get_locale():
    return 'es'

