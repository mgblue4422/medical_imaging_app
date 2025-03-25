from flask import Flask, render_template, request, redirect, url_for, jsonify, session
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
from patientdatabase5 import *
from syntheticdata import syntheticdata


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Volumes/Seagate Bac/Thesis project 2025/database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)  # Initialize the first db1 instance with the app
bcrypt = Bcrypt(app)
migrate = Migrate(app, db1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
# Register the patients blueprint
app.register_blueprint(patients_bp, url_prefix='/patients')
# Hjemmeside rute for login-skjemaet

app.register_blueprint(syntheticdata, url_prefix='/syntheticdata')



app.secret_key = 'your_secret_key'  # Replace with a strong secret key
#session['username'] = username
@app.route('/')
def index():
    form = LoginForm()
    return render_template('login.html', form=form)  # Din login.html




# Login rute som håndterer POST-forespørsel
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")  # This should print when the route is hit
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print(f"Username: {form.username.data}, Password: {form.password.data}, User Password: {user.password if user else 'No user found'}")

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("Login successful")
            login_user(user)
            session['logged_in'] = True  # Set the session variable
            #session['username'] = user  # Store the username in the session
            return redirect(url_for('bac'))
        else:
            print("Login failed")
            error = "Invalid login"
            return render_template('login.html', error=error, form=form)

    return render_template('login.html', form=form)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('index'))  # Redirect to login page if not logged in
        return f(*args, **kwargs)
    return decorated_function

# Rute for BAC.html
@app.route('/bac')
def bac():
    return render_template('BACtrial.html')  # Din BAC.html side



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()


    if form.validate_on_submit():
        print(f"Registering user: {form.username.data}")
        # Hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create a new user
        new_user = User(username=form.username.data, password=hashed_password)
        db1.session.add(new_user)
        db1.session.commit()
        return redirect(url_for('login'))  # Redirect to login page after registration
    return render_template('register.html', form=form)  # Render registration form

@app.route('/section/<section_name>')
def section(section_name):
    if section_name == 'home':
        return render_template('home.html')  # Render home.html

    elif section_name == 'patients':

        #return render_template('patients.html')
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        else:
            return redirect(url_for('patients.patients'))  # Redirect to the patients blueprint


        #return '<h2>Patients Section</h2><p>This is where you can manage patients.</p>'#render_template('patients.html')  # Render patients.html
    elif section_name == 'analysis':
        return   '<h2>Analysis Section</h2><p>This is where you can perform analysis.</p>'#render_template('analysis.html')  # Render analysis.html

    elif section_name == 'syntheticdata':


            return redirect(url_for('syntheticdata.syntheticdata'))  # Redirect to the patients blueprint



    else:
        return "Section not found", 404


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove the logged_in key from the session
    session.pop('username', None)  # Optionally remove the username
    return redirect(url_for('index'))  # Redirect to the login page

@app.route('/syntheticReal.html')
def synthetic_real():
    return render_template('syntheticReal.html')

@app.route('/userguide.html')
def user_guide():
    return render_template('userguide.html')

@app.route('/pen.html')
def pen():
    return render_template('pen.html')
@app.route('/zoom1.html')
def zoom_1():
    return render_template('zoom1.html')

@app.route('/Phdgraph.html')
def phd_graph():
    return render_template('Phdgraph.html')

if __name__ == '__main__':
    app.run(debug=True)
