from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os

app = Flask(__name__)
app.app_context().push()

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    def __repr__(self):
        return f'User {self.name}'
# Line below only required once, when creating DB.
# db.create_all()



@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method=="POST":
        if User.query.filter_by(email=request.form.get('email')).first():
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form['password'],
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("secrets",name=new_user.name))

    return render_template("register.html", logged_in=current_user.is_authenticated)

@app.route('/download')
@login_required
def download():
    return send_from_directory(directory='static', path='files/cheat_sheet.pdf')



@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        user_email = request.form['email']
        user_password = request.form['password']

        user = User.query.filter_by(email=user_email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        #Password incorrect
        elif not check_password_hash(user.password,user_password):
            flash('Password incorrect, please try again.')
        else:
            login_user(user)
            return redirect(url_for("secrets",name=user.name))

    return render_template("login.html", logged_in=current_user.is_authenticated)
#b@b.com
#bbbbbb

@app.route('/secrets')
@login_required
def secrets():
    name = request.args.get("name")
    return render_template("secrets.html",name=name, logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



if __name__ == "__main__":
    app.run(debug=True)
