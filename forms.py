from flask_wtf import FlaskForm
from wtforms import StringField, URLField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor, CKEditorField
from flask_bootstrap import Bootstrap
from flask import Flask
from flask_gravatar import Gravatar


app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=20, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)


class MakePostForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    img_url = URLField('Image Url', validators=[DataRequired()])
    body = CKEditorField('Content', validators=[DataRequired()])
    submit = SubmitField("Submit")


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Log in")


class Signup(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Sign up")


class CommentForm(FlaskForm):
    comment = TextAreaField('Comments', validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
