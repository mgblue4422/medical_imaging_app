import os
from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from db1 import db1  # Import the db1 instance
from sqlalchemy import LargeBinary

app = Flask(__name__)
EXTERNAL_DRIVE_PATH = '/Volumes/Seagate Bac/Thesis project 2025/database.db'  # Update this path accordingly
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + EXTERNAL_DRIVE_PATH
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)

# Model for storing image metadata and image data
class ImageModel(db1.Model):
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(150), nullable=False)
    synthetic_patient_id = db1.Column(db1.String(50), nullable=False)  # To store synthetic patient ID
    image_data = db1.Column(db1.LargeBinary, nullable=False)  # To store the image data

# Create the database tables if they do not exist
with app.app_context():
        # Drop the specific table if it exists


    db1.create_all()

def process_images():
    patient_data_folder = '/Volumes/Seagate Bac/Syth_data/Data_Synthetic/GAN_project_2024/HA-GAN/Results/Stroke/'  # Update this path
    try:
        for patient_folder in os.listdir(patient_data_folder):
            patient_path = os.path.join(patient_data_folder, patient_folder)
            if os.path.isdir(patient_path):  # Check if it's a directory
                for filename in os.listdir(patient_path):
                    if allowed_file(filename):
                        file_path = os.path.join(patient_path, filename)

                        # Read the image data
                        with open(file_path, 'rb') as file:
                            image_data = file.read()  # Read the binary data of the image

                        # Save metadata and image data to the database
                        new_image = ImageModel(
                            filename=filename,
                            synthetic_patient_id=patient_folder,
                            image_data=image_data  # Store the image data
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
    return "Patient data uploaded successfully!"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'tiff', 'tif'}

if __name__ == '__main__':
    app.run(debug=True)
