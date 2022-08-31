from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create instance of packages
db = SQLAlchemy()
login_manager = LoginManager()

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
    
    # Attach Blueprints
    from app.dashboard import dashboard as dashboard_blueprint
    from app.auth import auth as auth_blueprint
    
    # Register Blueprints
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    
    return app