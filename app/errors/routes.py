from flask import render_template, jsonify, request
from app.errors import errors


# Page not found error(Using content negotiation to generate appropriate error responses)
@errors.app_errorhandler(404)
def page_not_found(e):
    # Check if the request accept json or html
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404

# Error 500 (Using content negotiation to generate appropriate error responses)
@errors.app_errorhandler(500)
def internal_server_error(e):
    # Check if the request accept json or html
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500

# Error 403
@errors.app_errorhandler(403)
def forbidden_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('errors/403.html'), 403