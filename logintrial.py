from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from patients import patients_bp  # Import the patients blueprint
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://Users/ashvini12/PycharmProjects/medical_imaging_app/database.db'
app.config['SECRET_KEY'] = 'your_secret_key'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Register the patients blueprint
app.register_blueprint(patients_bp, url_prefix='/patients')
# Hjemmeside rute for login-skjemaet


app.secret_key = 'your_secret_key'  # Replace with a strong secret key
#session['username'] = username
@app.route('/')
def index():
    return render_template('login.html')  # Din login.html




# Login rute som håndterer POST-forespørsel
@app.route('/login', methods=['GET','POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username and password from the form
        username = request.form.get('username')
        password = request.form.get('password')

        # Simple check for username and password (can be replaced with database validation)
        if username == 'admin' and password == 'admin':  # Example hardcoded values
            session['logged_in'] = True  # Set the session variable
            session['username'] = username  # Store the username in the session
            return redirect(url_for('bac'))  # Redirect to BAC.html
        else:
            error = "Invalid login"  # Store the error message
            return render_template('login.html', error=error)  # Render the login form with error message

    return render_template('login.html')  # Render the login form for GET requests

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
    else:
        return "Section not found", 404


@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove the logged_in key from the session
    session.pop('username', None)  # Optionally remove the username
    return redirect(url_for('index'))  # Redirect to the login page


if __name__ == '__main__':
    app.run(debug=True)
