import os
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from db1 import db1  # Import the db1 instance

app = Flask(__name__)
EXTERNAL_DRIVE_PATH = '/Volumes/Seagate Bac/Thesis project 2025/database.db'  # Update this path accordingly
# Define the patient data folder path
SYNTH_DATA_FOLDER = '/Volumes/Seagate Bac/Syth_data/Data_Synthetic/GAN_project_2024/HA-GAN/Results/Stroke/'  # Update this path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + EXTERNAL_DRIVE_PATH
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)

# Model for storing image metadata and image file path
class ImageModel(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(150), nullable=False)
    synthetic_patient_id = db1.Column(db1.String(50), nullable=False)  # To store synthetic patient ID
    file_path = db1.Column(db1.String(255), nullable=False)  # To store the file path

# Create the database tables if they do not exist
@app.route('/create_tables', methods=['GET'])
def create_tables():
    with app.app_context():
        db1.create_all()  # Create tables
    return "Tables created successfully!"


def process_images():
    try:
        for patient_folder in os.listdir(SYNTH_DATA_FOLDER):
            patient_path = os.path.join(SYNTH_DATA_FOLDER, patient_folder)
            if os.path.isdir(patient_path):  # Check if it's a directory
                for filename in os.listdir(patient_path):
                    if allowed_file(filename):
                        file_path = os.path.join(patient_path, filename)

                        # Save metadata and file path to the database
                        new_image = ImageModel(
                            filename=filename,
                            synthetic_patient_id=patient_folder,
                            file_path=file_path  # Store the file path instead of image data
                        )
                        db1.session.add(new_image)
                        db1.session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_images', methods=['GET'])
def add_images():
    process_images()  # Call the function to process and add images to the database
    return "Synthetic data uploaded successfully!"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'tiff', 'tif'}

if __name__ == '__main__':
    app.run(debug=True)
