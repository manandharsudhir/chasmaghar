from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField
from wtforms.validators import Email,DataRequired,Length,Regexp

class LoginForm(FlaskForm):
     email=EmailField('Email',validators=[DataRequired(),Email()])
     password=PasswordField('Password',validators=[DataRequired()])
     submit = SubmitField("Login")