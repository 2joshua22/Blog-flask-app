from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, FileField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username=StringField("Username: ",validators=[DataRequired()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Login")

class NameForm(FlaskForm):
    name=StringField("What is your Name?",validators=[DataRequired()])
    submit=SubmitField("Submit")

class PasswordForm(FlaskForm):
    email=StringField("Email: ",validators=[DataRequired()])
    password_hash=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Log In")

class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    # content=StringField('Content',validators=[DataRequired()],widget=TextArea())
    content=CKEditorField('Content',validators=[DataRequired()])
    slug=StringField("SlugField",validators=[DataRequired()])
    submit=SubmitField("Post")

class SearchForm(FlaskForm):
    searched=StringField("Searched: ",validators=[DataRequired()])
    submit=SubmitField("Submit")

class UserForm(FlaskForm):
    username=StringField("UserName: ",validators=[DataRequired()])
    name=StringField("Name: ",validators=[DataRequired()])
    email=StringField("Email ID: ",validators=[DataRequired()])
    about_author=StringField("About Author: ",validators=[DataRequired()],widget=TextArea())
    password_hash=PasswordField("Password: ",validators=[DataRequired(),EqualTo('password_hash2',message="Passwords Must Match!")])
    password_hash2=PasswordField("Confirm Password: ",validators=[DataRequired()])
    profile_pic=FileField("Profile Pic",)
    submit=SubmitField("Submit")