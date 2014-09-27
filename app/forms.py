from wtforms import Form, StringField, PasswordField
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta

class SecureForm(Form):
    class Meta:
        csrf=True
        csrf_class=SessionCSRF
        csrf_secret = b'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
        csrf_time_limit = timedelta(minutes=20)

class LoginForm(SecureForm):
    email = StringField('Email')
    password = PasswordField('Password')

class LogoutForm(SecureForm):
    pass

