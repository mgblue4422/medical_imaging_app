from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file, flash
from patients import patients_bp  # Import the patients blueprint
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin , login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from db1 import db1
from flask_migrate import Migrate
from patientdatabase import *
from syntheticdata import syntheticdata
from analysisdatabase import HistogramImageModel
from forms import PatientForm

import io

app = Flask(__name__)

# Get the directory of the current file (this file)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the database URI using a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SECRET_KEY'] = 'your_secret_key'
print(app.config['SQLALCHEMY_DATABASE_URI'])



db1.init_app(app)  # Initialize the first db1 instance with the app
bcrypt = Bcrypt(app)
migrate = Migrate(app, db1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Get the directory of the current file
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the upload folder path relative to the application directory
BASE_FOLDER_PATH = os.path.join(basedir, 'uploads')  # 'uploads' is a subdirectory

# Create the uploads directory if it doesn't exist
if not os.path.exists(BASE_FOLDER_PATH):
    os.makedirs(BASE_FOLDER_PATH)



app.config['UPLOAD_FOLDER'] = BASE_FOLDER_PATH

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db1.Model, UserMixin):
    id = db1.Column(db1.Integer, primary_key=True)
    username = db1.Column(db1.String(20), nullable=False, unique=True)
    password = db1.Column(db1.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def index():
    form = LoginForm()
    return render_template('login.html', form=form)  # Din login.html




if __name__ == '__main__':
    app.run(debug=True)
