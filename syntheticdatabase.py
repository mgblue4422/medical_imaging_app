import os
import paramiko
from flask import Flask, redirect, url_for, render_template, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from db1 import db1  # Import the db1 instance
from config import *

app = Flask(__name__)
# Get the directory of the current file (this file)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the database URI using a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SECRET_KEY'] = 'your_secret_key'
print(app.config['SQLALCHEMY_DATABASE_URI'])

db1.init_app(app)

# SFTP server details
SFTP_HOST = 'ssh2.ux.uis.no'
SFTP_PORT = 22
SFTP_USERNAME = SFTP_USERNAME
SFTP_PASSWORD = SFTP_PASSWORD  # Replace with your actual password
REMOTE_FOLDER_PATH = '/nfs/prosjekt/IschemicStroke/Program/Data_Synthetic/GAN_project_2024/HA-GAN/Results/Stroke/990500'

# Model for storing image metadata and image file path
class ImageModel(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(150), nullable=False)
    synthetic_patient_id = db1.Column(db1.String(50), nullable=False)
    file_path = db1.Column(db1.String(255), nullable=False)

@app.route('/create_tables', methods=['GET'])
def create_tables():
    with app.app_context():
        db1.create_all()
    return "Tables created successfully!"

def process_images():
    try:
        # Create an SFTP client
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # List files in the remote directory
        try:
            remote_files = sftp.listdir(REMOTE_FOLDER_PATH)
            print(f"Files in {REMOTE_FOLDER_PATH}: {remote_files}")  # Debug print
        except FileNotFoundError:
            print(f"Error: The remote directory {REMOTE_FOLDER_PATH} does not exist.")
            return
        except Exception as e:
            print(f"Error listing files: {e}")
            return

        for filename in remote_files:
            if allowed_file(filename):
                file_path = os.path.join(REMOTE_FOLDER_PATH, filename)

                # Extract patient ID from the filename
                patient_id = os.path.splitext(filename)[0]

                # Save metadata and file path to the database
                new_image = ImageModel(
                    filename=filename,
                    synthetic_patient_id=patient_id,
                    file_path=file_path
                )
                db1.session.add(new_image)
                db1.session.commit()

        # Close the SFTP connection
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/add_images', methods=['GET'])
def add_images():
    process_images()
    return "Synthetic data uploaded successfully!"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'tiff', 'tif'}

@app.route('/image', methods=['GET'])
def get_image():
    try:
        # Create an SFTP client
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Specify the remote file path (you may want to get this from the database)
        remote_file_path = '/nfs/prosjekt/IschemicStroke/Data/Region_Analysis/Plots/NO_holes/Core_CTP_and_NOTCore_DWI/histogram3D/100/CBF_COV/2D/Clear/CBF_COV_LVO.png'

        # Open the remote file
        with sftp.file(remote_file_path, 'rb') as remote_file:
            image_data = remote_file.read()

        # Close the SFTP connection
        sftp.close()
        transport.close()

        # Serve the image
        return send_file(BytesIO(image_data), mimetype='image/png')
    except Exception as e:
        print(f"Error: {e}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
