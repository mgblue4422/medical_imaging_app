import os
import csv
from flask import Flask , request , jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary
from db1 import db1  # Import the db1 instance
from datetime import datetime
from config import *
import paramiko
import re

app = Flask(__name__)

# Get the directory of the current file (this file)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the database URI using a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SECRET_KEY'] = 'your_secret_key'
print(app.config['SQLALCHEMY_DATABASE_URI'])

db1.init_app(app)

BASE_FOLDER_PATH = '/Users/g/Desktop/isles24_train_b'  # Update this path accordingly



# SFTP server details for the upload
SFTP_UPLOAD_HOST = 'ssh2.ux.uis.no'
SFTP_UPLOAD_PORT = 22
SFTP_UPLOAD_USERNAME = SFTP_USERNAME
SFTP_UPLOAD_PASSWORD = SFTP_PASSWORD  # Replace with your actual password
REMOTE_UPLOAD_FOLDER_PATH = '/nfs/prosjekt/IschemicStroke/Data/CTP/Pre-processed/SUS2020/Dataset/IMAGES_1_1_1_0.5'  # Change to your desired upload path


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
    is_folder = db1.Column(db1.Boolean, default=False)

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

@app.route('/upload_patient_folders', methods=['GET'])
def upload_patient_folders():
    # Get the remote folder path from the request
    remote_folder_path = REMOTE_UPLOAD_FOLDER_PATH
    print(f"Received remote folder path: {remote_folder_path}")

    if not remote_folder_path:
        print("Error: Remote folder path is required.")
        return jsonify({"error": "Remote folder path is required"}), 400

    try:
        # Create an SFTP client
        print("Connecting to SFTP server...")
        transport = paramiko.Transport((SFTP_UPLOAD_HOST, SFTP_UPLOAD_PORT))
        transport.connect(username=SFTP_UPLOAD_USERNAME, password=SFTP_UPLOAD_PASSWORD)
        print("Connected to SFTP server.")

        with paramiko.SFTPClient.from_transport(transport) as sftp:
            print(f"Listing folders in remote directory: {remote_folder_path}")
            patient_folders = sftp.listdir(remote_folder_path)
            print(f"Found patient folders: {patient_folders}")

            if not patient_folders:
                print("No patient folders found.")
                return jsonify({"message": "No patient folders found."}), 200

            for patient_folder in patient_folders:
                folder_path = os.path.join(remote_folder_path, patient_folder)
                print(f"Checking if {folder_path} is a directory...")

                # Check if the item is a directory
                if sftp.stat(folder_path).st_mode & 0o40000:  # Check if it's a directory

                    # Extract all numeric parts from the patient_folder name
                    matches = re.findall(r'\d+', patient_folder)  # Find all sequences of digits
                    if matches:
                        # Concatenate the numeric parts and convert to an integer
                        patient_idnr = int(''.join(matches))  # Join all matched numeric parts together and convert to int
                    else:
                        print(f"Error: No numeric ID found in patient folder name '{patient_folder}'.")
                        continue  # Skip this folder if no numeric ID is found

                    patient_id = patient_folder  # Assuming the folder name is the patient ID
                    print(f"Adding patient folder: {patient_id} with path: {folder_path}")

                    # Check if the patient already exists in the database
                    existing_patient = db1.session.query(Patient).filter_by(id=patient_idnr ).first()

                    if not existing_patient:
                        # Create a new Patient entry if it doesn't exist
                        new_patient = Patient(id=patient_idnr , patient_name=patient_id)
                        db1.session.add(new_patient)
                        print(f"Created new patient entry for: {patient_id}")

                    # Create a new CTPFile entry for the patient folder
                    new_ctp_file = CTPFile(
                        patient_id=patient_idnr,
                        file_path=folder_path,  # Store the path to the patient folder
                        is_folder=True,  # Indicate that this is a folder
                        filename = patient_folder
                    )
                    db1.session.add(new_ctp_file)

            # Commit the session to save the CTPFile entries
            print("Committing changes to the database...")
            db1.session.commit()
            print("Changes committed successfully.")

        return jsonify({"message": "Patient folders uploaded successfully!"}), 200

    except paramiko.SSHException as ssh_error:
        print(f"SSH error: {str(ssh_error)}")
        return jsonify({"error": f"SSH error: {str(ssh_error)}"}), 500
    except FileNotFoundError as fnf_error:
        print(f"File not found: {str(fnf_error)}")
        return jsonify({"error": f"File not found: {str(fnf_error)}"}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500



def upload_patients_from_csv(csv_path):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header row

        for row in reader:
            ctp_path = row[0]
            if not ctp_path:
                continue

            # Extract patient name from path (CTP_XX_XXX) and append '_DCM'
            try:
                base_name = next(part for part in ctp_path.split('/') if part.startswith('CTP_'))
                patient_name = f"{base_name}_DCM"
            except StopIteration:
                print(f"Could not extract patient name from path: {ctp_path}")
                continue

            # Check if patient already exists
            existing_patient = Patient.query.filter_by(patient_name=patient_name).first()
            if existing_patient:
                print(f"Patient {patient_name} already exists, skipping.")
                continue

            # Create and add the new patient
            patient = Patient(patient_name=patient_name)
            db1.session.add(patient)
            db1.session.flush()  # Get patient.id without committing yet

            # Add the CTP file entry
            ctp_file = CTPFile(
                filename=os.path.basename(ctp_path),
                patient_id=patient.id,
                file_path=ctp_path,
                is_folder=True
            )
            db1.session.add(ctp_file)

        try:
            db1.session.commit()
            print("Upload completed successfully.")
        except Exception as e:
            print(f"Error committing to database: {e}")
            db1.session.rollback()


@app.route('/upload_patients_from_csv')
def upload_patients_from_csv_route():
    csv_path = '/Users/g/Desktop/sus_ctp_foldernames(in).csv'  # Replace with your actual CSV path
    try:
        upload_patients_from_csv(csv_path)
        return 'Patients and CTP folders uploaded successfully.', 200
    except Exception as e:
        return f'Error during upload: {str(e)}', 500




if __name__ == '__main__':
    app.run(debug=True)
