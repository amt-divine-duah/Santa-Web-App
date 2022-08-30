from flask import Blueprint

# Create Blueprint name
dashboard = Blueprint('dashboard', __name__)

# Import routes
from app.dashboard import routes