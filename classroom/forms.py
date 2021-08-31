from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from classroom.models import User

from string import ascii_letters, digits
from datetime import date

class Sign_up_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(min=3, max=20)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    mobile = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Get In Board')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The Username is already taken')
        else:
            for i in username.data:
                print(i)
                if i not in ascii_letters+digits:
                    raise ValidationError('Username should contain only Alphanumeric characters')    

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Account already exists')

    def validate_dob(self, dob):
        if dob.data >= date.today():
            raise ValidationError('Invaid Date of Birth')

class Login_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Reset_request_form(FlaskForm):
    email = StringField('EMail', validators=[DataRequired(), Email()])
    submit = SubmitField('Get Reset Link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No such account exists')

class Reset_password_form(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', "Password doesn't match")])

    submit = SubmitField('Reset')

class Create_class(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(min=3, max=30)])

    submit = SubmitField('Create')   

class Join_class(FlaskForm):
    id = StringField('Class ID', validators=[DataRequired(), Length(min=10, max=10)])

    submit = SubmitField('Join')

class Assign_assignment(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=30)])
    description = StringField('Description')
    due = DateField('Due Date', validators=[DataRequired()])

    submit = SubmitField('Assign')

    def validate_due(self, due):
        if due.data < date.today():
            raise ValidationError('Invaid Due, Past Date')