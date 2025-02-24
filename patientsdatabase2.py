from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
from db1 import db1
import os

app = Flask(__name__)

# Portable database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)



# Define the StrokeCase model (was "Case", renamed)
class StrokeCase(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    case_name = db1.Column(db1.String(100), nullable=False, unique=True)
    sessions = db1.relationship('Session', backref='stroke_case', lazy=True)

# Define the Session model (ses-01, ses-02)
class Session(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    session_name = db1.Column(db1.String(50), nullable=False)
    case_id = db1.Column(db1.Integer, db1.ForeignKey('stroke_case.id'), nullable=False)
    nii_files = db1.relationship('NiiFile', backref='session', lazy=True)

# Define the NiiFile model (stores .nii.gz files)
class NiiFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    session_id = db1.Column(db1.Integer, db1.ForeignKey('session.id'), nullable=False)
    is_perfusion = db1.Column(db1.Boolean, default=False)  # Flag for perfusion maps
    file_data = db1.Column(LargeBinary)  # Field to store the binary data of the NIFTI file

# Create the database tables
with app.app_context():
    db1.create_all()

# Function to store case and session data
def store_patient_data(base_folder_path):
    derivatives_path = os.path.join(base_folder_path, "derivatives")
    if not os.path.isdir(derivatives_path):
        return

    for case_folder in os.listdir(derivatives_path):
        case_path = os.path.join(derivatives_path, case_folder)
        if os.path.isdir(case_path):
            # Check if case already exists
            case_entry = StrokeCase.query.filter_by(case_name=case_folder).first()
            if not case_entry:
                case_entry = StrokeCase(case_name=case_folder)
                db1.session.add(case_entry)
                db1.session.commit()

            for session_folder in os.listdir(case_path):
                session_path = os.path.join(case_path, session_folder)
                if os.path.isdir(session_path) and session_folder.startswith("ses-"):
                    # Check if session already exists
                    session_entry = Session.query.filter_by(session_name=session_folder, case_id=case_entry.id).first()
                    if not session_entry:
                        session_entry = Session(session_name=session_folder, case_id=case_entry.id)
                        db1.session.add(session_entry)
                        db1.session.commit()

                    # Add all .nii.gz files in the session folder
                    for file in os.listdir(session_path):
                        if file.endswith('.nii.gz'):
                            file_path = os.path.join(session_path, file)  # Get the full path to the file
                            with open(file_path, 'rb') as f:  # Open the file in binary read mode
                                file_data = f.read()  # Read the binary data
                            #nii_file = NiiFile(filename=file, session_id=session_entry.id, is_perfusion=False,file_data=file_data)

                                nii_file = NiiFile(filename=file, session_id=session_entry.id, is_perfusion=False)

                            db1.session.add(nii_file)

                    # Handle perfusion maps separately
                    perfusion_path = os.path.join(session_path, "perfusion-maps")
                    if os.path.isdir(perfusion_path):
                        for file in os.listdir(perfusion_path):
                            file_path = os.path.join(perfusion_path, file)
                            with open(file_path, 'rb') as f:
                                file_data = f.read()  # Read the binary data
                            nii_file = NiiFile(filename=file, session_id=session_entry.id, is_perfusion=True)

                            #nii_file = NiiFile(filename=file, session_id=session_entry.id, is_perfusion=True,file_data=file_data)

                            db1.session.add(nii_file)



    db1.session.commit()

# Route to upload data
@app.route('/upload_patients')
def upload_patients():
    base_folder_path = '/Users/g/Desktop/isles24_train_b'
    store_patient_data(base_folder_path)
    return "Patient data uploaded successfully!"

# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
