from flask import render_template
from app.errors import errors


# Page not found error
@errors.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

# Error 500
@errors.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Error 403
@errors.app_errorhandler(403)
def forbidden_error(e):
    return render_template('errors/403.html'), 403