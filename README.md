# Setup Instructions for Running the Application

To run the application, you need to update the paths in the code to reflect the correct locations for the database and the patient data. Please follow the instructions below:

## Step 1: Update Database Path in `patientsdatabase.py`

Locate the following line in the code:

EXTERNAL_DRIVE_PATH = '/folder/database.db'  # Update this path accordingly

Instructions:
- Change the value of `EXTERNAL_DRIVE_PATH` to the actual path where your SQLite database file is located.

Example:
EXTERNAL_DRIVE_PATH = 'C:\\Users\\YourUsername\\Documents\\database.db'

---

## Step 2: Update Patient Data Path in `patientsdatabase.py`

Next, locate the following line in the code:

BASE_FOLDER_PATH = '/Users/g/Desktop/isles24_train_b'  # Update this path accordingly

Instructions:
- Change the value of `BASE_FOLDER_PATH` to the actual path where your patient data is stored.

Example:
BASE_FOLDER_PATH = 'D:\\PatientData\\isles24_train_b'

---

## Step 3: Update Synth Data Path and Database Path in `syntheticdatabase.py`

Locate the following lines in the code:

SYNTH_DATA_FOLDER = '/Volumes/Seagate Bac/Syth_data/Data_Synthetic/GAN_project_2024/HA-GAN/Results/Stroke/'  # Update this path
EXTERNAL_DRIVE_PATH = 'C:\\Users\\YourUsername\\Documents\\database.db'  # Update this path

Instructions:
- Change the value of `SYNTH_DATA_FOLDER` to the actual path where your synthetic patient data is stored.
- Change the value of `EXTERNAL_DRIVE_PATH` to where the database is stored.

---

## Step 4: Create Synth Database Tables

1. Run the Application: Start your Flask application by executing the `syntheticdatabase.py` script. You can do this from your terminal or command prompt:

   python syntheticdatabase.py

2. Access the Create Tables Route: Open a web browser and navigate to the following URL:

   http://127.0.0.1:5000/create_tables

3. Check for Success Message: If the tables are created successfully, you should see the message:

   Tables created successfully!

---

## Step 5: Access the Add Images Route

1. Navigate to the Add Images Route: In the same web browser, go to:

   http://127.0.0.1:5000/add_images

2. Check for Success Message: If the synthetic data is uploaded successfully, you should see the message:

   Synthetic data uploaded successfully!

---

## Step 6: Upload Patient Data

1. Run the Application: Start your Flask application by executing the `patientdatabase.py` script:

   python patientdatabase.py

2. Access the Upload Patients Route: In the same web browser, navigate to:

   http://127.0.0.1:5000/upload_patients

3. Check for Success Message: If the patient data is uploaded successfully, you should see the message:

   Patient data uploaded successfully!

---

## Step 7: Run the Application

To run the application, execute the `login.py` script:

python login.py

---
