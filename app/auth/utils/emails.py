from app import mail, celery
from flask import current_app, render_template
from flask_mail import Message


# Asynchronous Email Support
# Define function to send confirmation emails
@celery.task
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=app.config['MAIL_SUBJECT_PREFIX'] + subject, recipients=[to], 
                  sender=app.config['MAIL_SENDER'],)
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
    