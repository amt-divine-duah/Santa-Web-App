from flask import Flask
from config import config, Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from celery import Celery

# Create instance of packages
db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin()
mail = Mail()
# Initialize Celery
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

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
    celery.conf.update(app.config)
    
    from models import MyAdminIndexView
    admin.init_app(app, index_view=MyAdminIndexView())
    
    # Attach Blueprints
    from app.dashboard import dashboard as dashboard_blueprint
    from app.auth import auth as auth_blueprint
    from app.main import main as main_blueprint
    
    # Register Blueprints
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    
    
    return app