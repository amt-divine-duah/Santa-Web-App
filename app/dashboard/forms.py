from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class ProfileForm(FlaskForm):
    username = StringField('Username')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    middle_name = StringField('Middle Name')
    mobile_no = StringField('Mobile Number')
    email = EmailField('Email')
    bio = TextAreaField('Bio')
    address = StringField('Address')
    job_title = StringField('Job Title')

# Blog Post Form   
class PostForm(FlaskForm):
    title = StringField('Title')
    body = CKEditorField('What\'s on your mind?', validators=[DataRequired()])
    
# Admin Blog Post Form   
class AdminPostForm(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    body = CKEditorField('Blog Details', validators=[DataRequired()])