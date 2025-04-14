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


            return redirect(url_for('syntheticdata.syntheticdatapage'))  # Redirect to the synthetic blue print



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


@app.route('/get_image', methods=['GET'])
def get_image():
    patient_category = request.args.get('patient_category')  # e.g., 'LVO', 'NonLVO', 'All'
    value1 = request.args.get('value1')  # First value being plotted
    value2 = request.args.get('value2')  # Second value being plotted
    dimension = request.args.get('dimension')  # e.g., '2D' or '3D'

    print(f"Received parameters: patient_category={patient_category}, value1={value1}, value2={value2}, dimension={dimension}")

    # Query the database for the image based on the parameters
    image = HistogramImageModel.query.filter_by(
        category=patient_category,
        value1=value1,
        value2=value2,
        dimension=dimension
    ).first()

    if image:
        print(f"Found image: {image.filename}")
        return send_file(io.BytesIO(image.image_data), mimetype='image/png', as_attachment=False)

    # If no image found, switch value1 and value2 and query again
    print("No image found, switching value1 and value2.")
    image = HistogramImageModel.query.filter_by(
        category=patient_category,
        value1=value2,
        value2=value1,
        dimension=dimension
    ).first()

    if image:
        print(f"Found image after switching: {image.filename}")
        return send_file(io.BytesIO(image.image_data), mimetype='image/png', as_attachment=False)

    print("No image found after switching values.")
    return jsonify({'error': 'Image not found'}), 404


def find_matching_histogram_images(folder_path, patient_category, value1, value2, dimension):
    matching_images = []

    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                # Check for patient category
                if patient_category and patient_category not in filename:
                    continue

                # Check for value1 and value2
                if value1 and value1 not in filename:
                    continue
                if value2 and value2 not in filename:
                    continue

                # Check for dimension
                if dimension and dimension not in filename:
                    continue

                # If all conditions are met, add the file path to the list
                file_path = os.path.join(root, filename)
                matching_images.append(file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

    return matching_images


@app.route('/search_images', methods=['GET'])
def search_images():
    folder_path = '/Volumes/Seagate Bac/analysis_imgs/3D Histogram curves/'  # Update this path
    patient_category = request.args.get('patient_category')  # e.g., 'LVO', 'NonLVO', 'All'
    value1 = request.args.get('value1')  # First value being plotted
    value2 = request.args.get('value2')  # Second value being plotted
    dimension = request.args.get('dimension')  # e.g., '2D' or '3D'

    matching_files = find_matching_histogram_images(folder_path, patient_category, value1, value2, dimension)

    return jsonify(matching_files)  # Return the list of matching files as JSON




@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        patient_name = form.patient_name.data
        patient = Patient(patient_name=patient_name)
        db1.session.add(patient)
        db1.session.commit()

        # Handle CSV file
        if form.csv_file.data:  # Check if a CSV file has been uploaded
            csv_file = form.csv_file.data  # Get the uploaded file object
            new_csv = CSVFile(filename=csv_file.filename, patient_id=patient.id,
                              file_data=csv_file.read())  # Create a new CSVFile object with filename, patient ID, and file data

            # Add the new CSVFile object to the session and commit
            db1.session.add(new_csv)  # Add the new_csv object to the database session
            db1.session.commit()  # Commit the session to save the new_csv object to the database

            # Define the target path for the CSV file
            csv_file_path = os.path.join(BASE_FOLDER_PATH,
                                         csv_file.filename)  # Create a file path for saving the uploaded file on the file system
            # Save the file to the target path (optional, if you want to keep a copy on the file system)
            csv_file.save(csv_file_path)  # Save the uploaded file to the specified path on the file system

        # Handle other files
        file_types = {
            'ctp_file': CTPFile,
            'mri_file': MRIFile,
            'mtt_file': MTTFile,
            'cbv_file': CBVFile,
            'cbf_file': CBFFile,
            'tmax_file': TMAXFile,
            'ground_truth_file': GroundTruthFile
        }

        for field_name, model in file_types.items():
            file = getattr(form, field_name).data
            if file:
                # Define the target path for the file
                file_path = os.path.join(BASE_FOLDER_PATH, file.filename)

                # Save the file to the target path
                file.save(file_path)

                # Create a new instance of the corresponding model
                new_file = model(filename=file.filename, patient_id=patient.id, file_path=file_path)
                db1.session.add(new_file)

                # Commit the session to save the record in the database
                try:
                    db1.session.commit()
                except Exception as e:
                    print(f"Error committing to the database: {e}")
                    db1.session.rollback()  # Rollback in case of error

        flash('Patient data added successfully!', 'success')
        return redirect(url_for('add_patient'))

    return render_template('add_patient.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
