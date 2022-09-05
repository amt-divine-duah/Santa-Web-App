from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField
from flask_wtf.file import FileField, FileAllowed

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