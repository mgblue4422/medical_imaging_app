from flask import Blueprint, render_template, request, redirect, url_for
from decorators import login_required

# Initialize the Blueprint
patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/')
@login_required
def patients():
    return render_template('patients.html')  # Render patients.html

@patients_bp.route('/list')
def list_patients():
    # Here you would typically fetch the list of patients from a database
    return render_template('list_patients.html')  # Render the list of patients

@patients_bp.route('/upload', methods=['GET', 'POST'])
def upload_patient():
    if request.method == 'POST':
        patient_name = request.form['name']
        # Here you would typically save the patient to a database
        return redirect(url_for('patients.list_patients'))  # Redirect to the list of patients
    return render_template('upload_patient.html')  # Render the upload form

@patients_bp.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        search_name = request.form['search']
        # Here you would typically search for the patient in a database
        return render_template('search_results.html', search_name=search_name)  # Render search results
    return render_template('search_patient.html')  # Render the search form
