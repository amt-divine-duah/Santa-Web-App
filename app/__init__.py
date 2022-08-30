from flask import Flask
from config import config

# Create instance of packages

# Create application factory
def create_app(config_name):
    # Initialize the flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Initialize the configuration object
    config[config_name].init_app(app)
    
    
    # Attach Blueprints
    from app.dashboard import dashboard as dashboard_blueprint
    
    # Register Blueprints
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    
    
    return app