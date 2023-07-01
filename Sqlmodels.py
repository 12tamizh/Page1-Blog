from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from forms import *
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'log_in'


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("APP_SECRET_KEY")
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    posts = db.relationship("PostData", back_populates="author")
    comments = db.relationship("Comments", lazy='subquery', back_populates="comment_author")


class PostData(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", lazy='subquery', back_populates="posts"   )
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(500), nullable=False)
    post_date = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    comments = db.relationship("Comments", lazy='subquery', back_populates="parent_post")


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_post = db.relationship("PostData", lazy='subquery', back_populates="comments")
    comment_author = db.relationship("User", lazy='subquery', back_populates="comments")
    comment = db.Column(db.String(500), nullable=False)


# with app.app_context():
#     db.create_all()
