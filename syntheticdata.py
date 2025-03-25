from flask import Blueprint, render_template, request, redirect, url_for ,jsonify, current_app
from decorators import login_required
from db1 import db1  # Adjust the import based on your project structure
#from patientsdatabase2 import StrokeCase , Session, NiiFile # Adjust the import based on your project structure
from patientdatabase5 import Patient ,CTAFile, CBFFile ,CBVFile ,CTPFile ,MRIFile  ,MTTFile , TMAXFile , GroundTruthFile ,DoctorNote
import nibabel as nib  # Add this line
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
import os


syntheticdata = Blueprint('syntheticdata', __name__)

@syntheticdata.route('/data', methods=['GET'])
def get_data():
    # Example synthetic data
    data = {
        "name": "John Doe",
        "age": 30,
        "occupation": "Software Developer"
    }
    return jsonify(data)

@syntheticdata.route('/')
def patients():
    return render_template('syntheticdata.html.html')

@syntheticdata.route('/static/<path:filename>')
def serve_static(filename):
    return syntheticdata.send_static_file(filename)
@syntheticdata.route('/list')
def list_patients():
    patients = Patient.query.all()  # Fetch all patients from the database

    print(f"Patients fetched: {patients}")  # Debugging line
    return render_template('list_patients.html', patients=patients)  # Render the list of patients



@syntheticdata.route('/stroke_case/<int:case_id>')
@login_required  # Protect this route with login_required
def stroke_case(case_id):
    case = Patient.query.get_or_404(case_id)  # Fetch the stroke case by ID
    csv_files = case.csv_files  # Fetch the associated CSV files

    # Read CSV data into a dictionary
    csv_data = {}
    for csv_file in csv_files:
        # Use BytesIO to read the binary data as a CSV

        df = pd.read_csv(BytesIO(csv_file.file_data))
        df_cleaned = df.dropna(axis=1, how='any')

        csv_data[csv_file.filename] = df_cleaned.transpose().to_html(classes='table table-striped', index=True)  # Convert to HTML table

    return render_template('patientviewer8.html', case=case, patient_name=case.patient_name  , csv_data=csv_data)  # Pass the case to the template

