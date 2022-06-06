# from crypt import methods
import bcrypt as bcrypt
from flask import Flask, render_template, url_for, flash, redirect, request
from sqlalchemy import func

from forms import RegistrationForm, LoginForm, PostForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)

app.config["SECRET_KEY"] = "29b88f280b5ab6fbc8996226930c6e0b"  # secrets.token_hex(16)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# posts = [
#     {
#         "author": "Guillermo N",
#         "title": "Blog Post 1",
#         "content": "First post content",
#         "date_posted": "May 29, 2022",
#     },
#     {
#         "author": "Tulio Fra",
#         "title": "Blog Post 2",
#         "content": "Second post content",
#         "date_posted": "May 30, 2022",
#     }
# ]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    # connection to Posts table
    posts = relationship("Post", back_populates="author")


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime(), nullable=False, default=db.func.current_timestamp())
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # connection to the Users table
    author = relationship("User", back_populates="posts")
    # connection to the comments table
    category = relationship("Categories", back_populates="post", cascade="delete")


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Text, nullable=False)
    # foreign key for Posts
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    # connection to the Posts table
    post = relationship("Post", back_populates="category")


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)



@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/categories")
def shop():
    return render_template("shop.html", title="About")


@app.route("/product/<int:id>")
def product(id):
    # Get random post from posts
    post = Post.query.get_or_404(id)
    return render_template("product-details.html", title="Product", post=post)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(name=form.username.data, email=form.email.data, password=bcrypt.hashpw(form.password.data.encode("utf-8"),
                                                                                           bcrypt.gensalt()))
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", "success")
        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.checkpw(form.password.data, user.password):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template("login.html", title="LogIn", form=form)


@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, subtitle=form.subtitle.data,
                    description=form.description.data, img_url=form.img_url.data, price=form.price.data, author_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash("Post created!", "success")
        return redirect(url_for("index"))
    return render_template("create_post.html", title="Create Post", form=form)


if __name__ == '__main__':
    app.run(debug=True)
