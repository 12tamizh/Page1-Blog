from datetime import datetime
from functools import wraps
import smtplib
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, login_required, current_user, logout_user
from Sqlmodels import *
from forms import *
from werkzeug.security import generate_password_hash, check_password_hash


SENDER_EMAIL = os.getenv("SENDER_MAIL")
APP_PASSWORD = os.getenv("MAIL_APP_PASSWORD")
GMAIL_SMTP = "smtp.gmail.com"

# with app.app_context():
#     db.create_all()


# LOADING USER OBJECT
@login_manager.user_loader
def load_user(user_id):
    id_ = User.query.get(user_id)
    return id_


# ADMIN ONLY METHOD
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.id == 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# HOME PAGE
@app.route("/")
def home():
    with app.app_context():
        home_post_objects = db.session.execute(db.select(PostData)).scalars().all()[::-1]
    return render_template("index.html", top_posts=home_post_objects[:3], logged_in=current_user.is_authenticated)


# VIEW ABOUT
@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


# CONTACT US METHOD
@app.route("/contact", methods=["POST", "GET"])
def contact():
    message = False
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]
        print(name, email, phone, message)
        with smtplib.SMTP(GMAIL_SMTP) as connection:
            connection.starttls()
            connection.login(user=SENDER_EMAIL, password=APP_PASSWORD)
            connection.sendmail(from_addr=SENDER_EMAIL, to_addrs="test.tamizh12@yahoo.com",
                                msg=f"Subject: Message From Page1\n\nInformation:\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message} \nRegards,\n Page1 Bot")
            print(f"Mail Sent! at {datetime.now()}")
        message = True
    return render_template("contact.html", message=message, logged_in=current_user.is_authenticated)


# SIGN UP
@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    sign_up_form = Signup()
    user = User()
    if sign_up_form.validate_on_submit():
        user.name = sign_up_form.name.data
        user.email = sign_up_form.email.data
        user.password = generate_password_hash(sign_up_form.password.data)
        # print(check_password_hash(pwhash=user.password, password=sign_up_form.password.data))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("log_in"))
    return render_template("register.html", logged_in=False, form=sign_up_form)


# LOG IN
@app.route("/login", methods=["GET", "POST"])
def log_in():
    login_form = Login()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email address does not exist!")
        elif not check_password_hash(pwhash=user.password, password=password):
            flash("Password does not match!")
        else:
            login_user(user)
            return redirect(url_for("home", user=user.name))
    return render_template("login.html", logged_in=False, form=login_form)


# LOG OUT
@app.route("/logout")
@login_required
def log_out():
    logout_user()
    session.clear()
    if session.get('was_once_logged_in'):
        del session['was_once_logged_in']
    response = redirect(url_for('home'))
    response.delete_cookie('remember_token')
    return redirect(url_for("home"))


# ADD POST
@app.route("/add_new_post", methods=["GET", "POST"])
@login_required
@admin_only
def add_post():
    post_form = MakePostForm()
    if request.method == "POST":
        title = request.form["title"]
        subtitle = request.form["subtitle"]
        img_url = request.form["img_url"]
        body = request.form["body"]
        date = datetime.now().strftime('%B %d, %Y')
        new_post = PostData(title=title,
                            subtitle=subtitle,
                            img_url=img_url,
                            body=body,
                            author=current_user,
                            post_date=date)
        db.session.add(new_post)
        db.session.commit()
        return redirect("all_posts")
    return render_template("new_post.html", form=post_form, logged_in=current_user.is_authenticated)


# VIEW POST
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def post_content(post_id):
    with app.app_context():
        post_objects_contents = db.session.execute(db.select(PostData)).scalars().all()
    comment_form = CommentForm()
    read_post = None
    for post_ in post_objects_contents:
        if post_.id == post_id:
            read_post = post_
    if comment_form.validate_on_submit():
        new_comment = Comments(comment=comment_form.comment.data, comment_author=current_user, parent_post=read_post)
        local_object = db.session.merge(new_comment)
        db.session.add(local_object)
        db.session.commit()
    return render_template("post.html", post_content=read_post, logged_in=current_user.is_authenticated, current_user_id=current_user.id, form=comment_form)


# VIEW ALL POSTS
@app.route("/all_posts")
@login_required
def all_posts():
    with app.app_context():
        all_post_objects = db.session.execute(db.select(PostData)).scalars().all()[::-1]
    return render_template("all_posts.html", all_posts_objs=all_post_objects, logged_in=current_user.is_authenticated, current_user_id=current_user.id)


# EDIT POST
@app.route("/edit_post/<int:post_id>", methods=["GET", "POST", "PATCH"])
@login_required
@admin_only
def edit_post(post_id):
    update_post = db.session.query(PostData).get(post_id)
    edit_form = MakePostForm(title=update_post.title, subtitle=update_post.subtitle, img_url=update_post.img_url,
                             body=update_post.body, name=update_post.author.name)
    if edit_form.validate_on_submit():
        update_post.title = request.form["title"]
        update_post.subtitle = request.form["subtitle"]
        update_post.img_url = request.form["img_url"]
        update_post.body = request.form["body"]
        update_post.author = current_user
        db.session.commit()
        return redirect(url_for("all_posts"))
    return render_template("new_post.html", form=edit_form, post=update_post, isEdit=True, logged_in=current_user.is_authenticated)


# REMOVE POST
@app.route("/remove_post")
@login_required
@admin_only
def remove_post():
    post_id = request.args.get("post_id")
    delete_post = db.session.query(PostData).get(post_id)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for("all_posts", logged_in=current_user.is_authenticated))


# DELETE COMMENTS
@app.route("/delete_comment/comment")
def delete_comments():
    pass


if __name__ == "__main__":
    app.run(debug=True)
