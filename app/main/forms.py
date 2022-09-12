from ast import Sub
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_login import current_user

class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')
    
    
    def validate_body(self, field):
        if current_user.is_anonymous:
            raise ValidationError("You are required to login")