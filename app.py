import json

from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'some key'

# Config for Flask-Admin
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, template_mode='bootstrap3')

# Config for Flask-Login
login_manager = LoginManager()
# This line is required for Flask-Login when you're using using current_user in a template
login_manager.init_app(app)

# Config for Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def to_json(self):
        return {"name": self.name,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


categories = db.Table('categories',
                      db.Column('category_id', db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), primary_key=True),
                      db.Column('shop_id', db.Integer, db.ForeignKey('shop.id', ondelete='CASCADE'), primary_key=True)
                      )


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(120), nullable=False)
    icon = db.Column(db.String(120), nullable=False)
    categories = db.relationship('Category', secondary="categories",
                            backref=db.backref('shops', lazy='dynamic'))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return self.name


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Shop, db.session))
admin.add_view(ModelView(Category, db.session))


# admin.add_view(ModelView(Post, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/product')
def product():
    return render_template('product-details.html')


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/login')
def login_get():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user is None:
        return render_template('login.html', error='Invalid username or password')
    login_user(user)
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return render_template('login.html', error='Email already exists')
    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return render_template('login.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
