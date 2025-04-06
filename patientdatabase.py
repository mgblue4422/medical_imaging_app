import os
import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
from db1 import db1  # Import the db1 instance
from datetime import datetime
#this is the vesrions of the database w the time stamp and doctors note
app = Flask(__name__)

# Please change these database paths
EXTERNAL_DRIVE_PATH = '/Volumes/Seagate Bac/Thesis project 2025/database.db'  # Update this path accordingly
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + EXTERNAL_DRIVE_PATH
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)
# Define the base folder path for patient data
BASE_FOLDER_PATH = '/Users/g/Desktop/isles24_train_b'  # Update this path accordingly

# Define the Patient model
class Patient(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    patient_name = db1.Column(db1.String(100), nullable=False, unique=True)
    ctp_files = db1.relationship('CTPFile', backref='patient', lazy=True)
    mri_files = db1.relationship('MRIFile', backref='patient', lazy=True)
    mtt_files = db1.relationship('MTTFile', backref='patient', lazy=True)
    cbv_files = db1.relationship('CBVFile', backref='patient', lazy=True)
    cbf_files = db1.relationship('CBFFile', backref='patient', lazy=True)
    tmax_files = db1.relationship('TMAXFile', backref='patient', lazy=True)
    ground_truth_files = db1.relationship('GroundTruthFile', backref='patient', lazy=True)
    csv_files = db1.relationship('CSVFile', backref='patient', lazy=True)


class DoctorNote(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    note = db1.Column(db1.Text, nullable=False)
    created_at = db1.Column(db1.DateTime, default=datetime.utcnow)  # Timestamp for when the note was created

    patient = db1.relationship('Patient', backref='doctor_notes', lazy=True)

class CSVFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_data = db1.Column(LargeBinary)  # Store binary data
    #patient = db1.relationship('Patient', backref='csv_files', lazy=True)

# Define models for each type of medical image
class CTPFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class MRIFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class MTTFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class CBVFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class CBFFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class TMAXFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class CTAFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path

class GroundTruthFile(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(255), nullable=False)
    patient_id = db1.Column(db1.Integer, db1.ForeignKey('patient.id'), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)  # Store file path


# Create the database tables
with app.app_context():
    db1.create_all()


# Route to upload data
@app.route('/upload_patients')
def upload_patients():
    store_patient_data(BASE_FOLDER_PATH)
    return "Patient data uploaded successfully!"



def store_patient_data(BASE_FOLDER_PATHh):
    phenotype_path = os.path.join(BASE_FOLDER_PATH, "phenotype")
    derivatives_path = os.path.join(BASE_FOLDER_PATH, "derivatives")

    if not os.path.isdir(phenotype_path) or not os.path.isdir(derivatives_path):
        return

    for patient_folder in os.listdir(phenotype_path):
        patient_path = os.path.join(phenotype_path, patient_folder)
        if os.path.isdir(patient_path):
            # Check if patient already exists
            patient_entry = Patient.query.filter_by(patient_name=patient_folder).first()
            if not patient_entry:
                patient_entry = Patient(patient_name=patient_folder)
                db1.session.add(patient_entry)
                db1.session.commit()

            # Process each session in the phenotype folder
            for session_folder in os.listdir(patient_path):
                session_path = os.path.join(patient_path, session_folder)
                if os.path.isdir(session_path):
                    # Read CSV files for patient data
                    for csv_file in os.listdir(session_path):
                        if csv_file.endswith('.csv'):
                            csv_file_path = os.path.join(session_path, csv_file)
                            with open(csv_file_path, 'rb') as f:
                                file_data = f.read()  # Read the binary data
                            # Save the CSV file to the database
                            csv_file_entry = CSVFile(filename=csv_file, patient_id=patient_entry.id, file_data=file_data)
                            db1.session.add(csv_file_entry)

                    # Now process the corresponding session in the derivatives folder
                    derivatives_session_path = os.path.join(derivatives_path, patient_folder, session_folder)
                    if os.path.isdir(derivatives_session_path):
                        # Process CTP and CTA files
                        for file in os.listdir(derivatives_session_path):
                            if file.endswith('.nii.gz'):
                                file_path = os.path.join(derivatives_session_path, file)

                                # Check the file type and save accordingly
                                if 'ctp' in file.lower():
                                    ctp_file = CTPFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                    db1.session.add(ctp_file)
                                    print(f"Added CTP file: {file}")  # Log the addition
                                elif 'cta' in file.lower():
                                    cta_file = CTAFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                    db1.session.add(cta_file)
                                    print(f"Added CTA file: {file}")  # Log the addition

                        # Process perfusion maps
                        perfusion_maps_path = os.path.join(derivatives_session_path, "perfusion-maps")
                        if os.path.isdir(perfusion_maps_path):
                            for file in os.listdir(perfusion_maps_path):
                                if file.endswith('.nii.gz'):
                                    file_path = os.path.join(perfusion_maps_path, file)

                                    # Save perfusion map files
                                    if 'tmax' in file.lower():
                                        tmax_file = TMAXFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                        db1.session.add(tmax_file)
                                        print(f"Added TMAX file: {file}")
                                    elif 'mtt' in file.lower():
                                        mtt_file = MTTFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                        db1.session.add(mtt_file)
                                        print(f"Added MTT file: {file}")
                                    elif 'cbv' in file.lower():
                                        cbv_file = CBVFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                        db1.session.add(cbv_file)
                                        print(f"Added CBV file: {file}")
                                    elif 'cbf' in file.lower():
                                        cbf_file = CBFFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                        db1.session.add(cbf_file)
                                        print(f"Added CBF file: {file}")

                        # Process ground truth files
                        for file in os.listdir(derivatives_session_path):
                            if file.endswith('.nii.gz') and 'lesion-msk' in file.lower():
                                file_path = os.path.join(derivatives_session_path, file)
                                ground_truth_file = GroundTruthFile(filename=file, patient_id=patient_entry.id, file_path=file_path)  # Store file path
                                db1.session.add(ground_truth_file)
                                print(f"Added Ground Truth file: {file}")  # Log the addition

    # Commit all changes to the database
    # Commit all changes to the database
    db1.session.commit()


# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
