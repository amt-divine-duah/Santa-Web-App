from flask import request, jsonify
from app.api import api
from app.exceptions import ValidationError


# Error handler for status code 403
def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

# Status code 400
def bad_request(message):
    response = jsonify({'error':'bad request', 'message': message})
    response.status_code = 400
    return response

# Status code 401
def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])

