#  Web-based DICOM/NIfTI Viewer using Flask

This project is a web app to view raw DICOM (`.dcm`) and NIfTI (`.nii` / `.nii.gz`) medical images **directly in the browser**  converting them to PNG/JPEG. It uses a **Flask backend** to serve files and a **JavaScript frontend** to render the images.

---

## 📌 Features


- Simple Python Flask backend
-  Quick to launch and lightweight


### 1. Analysis
This page is designed to provide images generated from research investigations conducted at UiS. The **Analysis** feature offers a regional analysis of cerebral perfusion patterns across different patient populations. Users can explore these images to enhance their awareness and understanding of perfusion metrics in clinical practice.

<img src="https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/analysis.png?raw=true" alt="Analysis" width="500" height="300">

---

### 2. Dashboard
The **Dashboard** offers a user-friendly interface that displays key metrics and visualizations, enabling users to monitor their data effectively and access important information at a glance. This feature provides  tools for processing and interpreting medical images, allowing users to gain insights and make informed decisions based on the data presented.

<img src="https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/dash.png?raw=true" alt="Dashboard" width="500" height="300">

---

### 3. Info Patients
The **Info Patients** section allows users to manage and view patient information , ensuring that all relevant data is easily accessible.

<img src="https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/info.png?raw=true" alt="Info Patients" width="500" height="300">

---

### 4. List
The **List** feature provides a comprehensive overview of all patients, making it easy to navigate through records and find specific information quickly.

<img src="https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/list.png?raw=true" alt="List" width="1000" height="600">

---

### 5. Manual Annotation
The **Manual Annotation** tool enables users to annotate medical images directly, facilitating detailed analysis. 

<img src="https://github.com/mgblue4422/medical_imaging_app/blob/ec4015519de102097fe2fcc7f13b27fb5f5b919b/images/manual%20annotation.png?raw=true" alt="Manual Annotation" width="500" height="300">



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
