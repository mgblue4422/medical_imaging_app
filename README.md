#  Web-based DICOM/NIfTI Viewer using Flask + JavaScript

This project is a web app to view raw DICOM (`.dcm`) and NIfTI (`.nii` / `.nii.gz`) medical images **directly in the browser**  converting them to PNG/JPEG. It uses a **Flask backend** to serve files and a **JavaScript frontend** to render the images.

---

## 📌 Features


- Simple Python Flask backend
-  Quick to launch and lightweight


![Analysis](https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/analysis.png)
![Dashboard](https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/dash.png)
![Info patients](https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/info.png)
![List](https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/list.png)
![Manual Annotation](https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/manual%20annotation.png)


---

## 🛠 Requirements

### Backend (Python)
- Python 3.7+
- Flask

Install with:
```bash
pip install flask
```

---



# Setup Instructions for Running the Application

To run the application, you need to update the paths in the code to reflect the correct locations for the isles patient data. Please follow the instructions below:

## Step 1: Update user Data  `config.py`

Change the user and pass code to your login details for the Uis Server.

SFTP_USERNAME = 'u123456' - replace with actual username 

SFTP_PASSWORD = 'examplepassword' - Replace with your actual password


---


## Step 2: Update Patient Data Path in `patientsdatabase.py`

Next, locate the following line in the code:

BASE_FOLDER_PATH = '/Users/g/Desktop/isles24_train_b'  # Update this path accordingly

Instructions:
- Change the value of `BASE_FOLDER_PATH` to the actual path where your patient data is stored.

Example:
BASE_FOLDER_PATH = 'D:\\PatientData\\isles24_train_b'

---


## Step 3: Upload Patient Data

1. Run the Application: Start your Flask application by executing the `patientdatabase.py` script:

   python patientdatabase.py

2. Access the Upload Patients Route: In the same web browser, navigate to:

   http://127.0.0.1:5000/upload_patients

3. Check for Success Message: If the patient data is uploaded successfully, you should see the message:

   Patient data uploaded successfully!

---

## Step 4:    run the application using login.py



To run the application, execute the `login.py` script:

python login.py

---
