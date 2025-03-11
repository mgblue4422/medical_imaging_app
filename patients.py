from flask import Blueprint, render_template, request, redirect, url_for ,jsonify, current_app
from decorators import login_required
from db1 import db1  # Adjust the import based on your project structure
from patientsdatabase2 import StrokeCase , Session, NiiFile # Adjust the import based on your project structure
import nibabel as nib  # Add this line
import matplotlib.pyplot as plt
import os

# Initialize the Blueprint
patients_bp = Blueprint('patients', __name__)
# Path to your NIfTI file
NIFTI_FILE = '/Users/g/Desktop/isles24_train_b/derivatives/sub-stroke0003/ses-01/sub-stroke0003_ses-01_space-ncct_cta.nii.gz'
@patients_bp.route('/')
@login_required
def patients():
    return render_template('patients.html')  # Render patients.html

@patients_bp.route('/static/<path:filename>')
def serve_static(filename):
    return patients_bp.send_static_file(filename)
@patients_bp.route('/list')
def list_patients():
    patients = StrokeCase.query.all()  # Fetch all patients from the database

    print(f"Patients fetched: {patients}")  # Debugging line
    return render_template('list_patients.html', patients=patients)  # Render the list of patients


@patients_bp.route('/upload', methods=['GET', 'POST'])
def upload_patient():
    if request.method == 'POST':
        patient_name = request.form['name']
        # Here you would typically save the patient to a database
        return redirect(url_for('patients.list_patients'))  # Redirect to the list of patients
    return render_template('zoom.html')  # Render the upload form

@patients_bp.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        search_name = request.form['search']
        # Here you would typically search for the patient in a database
        return render_template('search_results.html', search_name=search_name)  # Render search results
    return render_template('search_patient.html')  # Render the search form


@patients_bp.route('/stroke_case/<int:case_id>')
@login_required  # Protect this route with login_required
def stroke_case(case_id):
    case = StrokeCase.query.get_or_404(case_id)  # Fetch the stroke case by ID
    sessions = Session.query.filter_by(case_id=case.id).all()  # Fetch related sessions
    nii_files = NiiFile.query.filter(Session.id == NiiFile.session_id, Session.case_id == case.id).all()  # Fetch related NIfTI files  # Fetch related NIfTI files
    # You can also fetch related data here, e.g., sessions or files
    # Fetch the first session related to the stroke case
    first_session = Session.query.filter_by(case_id=case.id).first()  # Get the first session

    # Fetch the first NIfTI file related to the first session
    first_nii_file = None
    if first_session:
        first_nii_file = NiiFile.query.filter_by(session_id=first_session.id).first()  # Get the first NIfTI file
    return render_template('patientviewer3.html', case=case, sessions=sessions ,nii_files=nii_files, first_session=first_session, first_nii_file=first_nii_file )  # Pass the case to the template


@patients_bp.route('/drop_table/<table_name>')
def drop_table(table_name):
    with current_app.app_context():  # Use current_app to get the main app context
        if table_name == 'stroke_case':
            StrokeCase.__table__.drop(db1.engine)  # Drop the StrokeCase table
        elif table_name == 'session':
            Session.__table__.drop(db1.engine)  # Drop the Session table
        elif table_name == 'nii_file':
            NiiFile.__table__.drop(db1.engine)  # Drop the NiiFile table
        else:
            return "Table not found!", 404
    return f"Table '{table_name}' has been dropped successfully!"

#I commented this out for now but it workss
# Example function to get the NIfTI file path based on case ID
#def get_nifti_file_path(case_id):
    # Replace this with your logic to retrieve the NIfTI file path based on the case ID
    # For example, you might query a database to get the file path
 #   return '/Users/g/Desktop/isles24_train_b/derivatives/sub-stroke0003/ses-01/sub-stroke0003_ses-01_space-ncct_cta.nii.gz'

@patients_bp.route('/get_nifti_file/<case_name>/<session_name>/<file_type>')
def get_nifti_file_path(case_id, session_name, file_type):
    # Query the database for the stroke case
    stroke_case = StrokeCase.query.get(case_id)
    if not stroke_case:
        print(f"Stroke case with ID {case_id} not found.")
        return None
    else:
        print(f"Stroke case with ID {case_id} found: {stroke_case}")

    session_record = Session.query.filter_by(session_name=session_name, case_id=stroke_case.id).first()
    if not session_record:
        print(f"Session '{session_name}' not found for case ID {case_id}.")
        return None
    else:
        print(f"Session case with ID {case_id} found: {stroke_case}")

    filename = f"{stroke_case.case_name}_{session_record.session_name}_{file_type}.nii.gz"
    nii_file = NiiFile.query.filter_by(filename=filename, session_id=session_record.id).first()
    if not nii_file:
        print(f"NIFTI file '{filename}' not found in session ID {session_record.id}.")
        return None
    else:
        print(f"Session case with ID {filename} found")

    if nii_file.file_data:
        print(f"NIFTI file path: {filename}")
    else:
        print("NIFTI file not found. here")

    return nii_file.file_data


@patients_bp.route('/get_nifti_file2/<case_id>/<session_name>/<file_type>')
def get_nifti_file_path2(case_id):
    # Query the database for the stroke case
    stroke_case = StrokeCase.query.get(case_id)
    if not stroke_case:
        print(f"Stroke case with ID {case_id} not found.")
        return jsonify({'error': 'Stroke case not found'}), 404

    print(f"Stroke case with ID {case_id} found: {stroke_case}")

    session_record = Session.query.filter_by(case_id=stroke_case.id).first()
    if not session_record:
        print(f"No sessions found for case ID {case_id}.")
        return jsonify({'error': 'Session not found'}), 404

    print(f"First session case with ID {case_id} found: {session_record}")
    # Construct the filename based on the expected format

    nii_file = NiiFile.query.filter_by(session_id=session_record.id).first()
    if not nii_file:
        print(f"No NIFTI files found for session ID {session_record.id}.")
        return jsonify({'error': 'NIFTI file not found'}), 404

    print(f"First NIFTI file found: {nii_file.filename}")
    filename = nii_file.filename
    print(f"First NIFTI file found: {filename}")
    #filename = f"{stroke_case.case_name}_{session_record.session_name}_{file_type}.nii.gz"

    # Construct the full path to the NIFTI file
    derivatives_path = os.path.join('/Users/g/Desktop/isles24_train_b', 'derivatives', stroke_case.case_name,
                                    session_record.session_name, filename)

    # Check if the file exists
    if not os.path.isfile(derivatives_path):
        print(f"NIFTI file '{filename}' not found at path: {derivatives_path}.")
        return jsonify({'error': 'NIFTI file not found'}), 404

    print(f"NIFTI file path: {derivatives_path}")
    #return jsonify({'file_path': derivatives_path}), 200
    return derivatives_path

@patients_bp.route('/slices/<int:case_id>')
def get_slices(case_id):
    # Get the NIfTI file path for the given case ID
    #nifti_file = get_nifti_file_path(case_id)
    nifti_file = get_nifti_file_path2(case_id)

    # Check if the NIfTI file exists
    if not os.path.exists(nifti_file):
        return jsonify({'error': 'NIfTI file not found'}), 404

    # Load the NIfTI file
    img = nib.load(nifti_file)
    data = img.get_fdata()

    # Generate paths for all slices
    slice_paths = []
    for slice_index in range(data.shape[2]):
        slice_data = data[:, :, slice_index]
        plt.imshow(slice_data, cmap='gray')
        plt.axis('off')
        image_path = f'static/slice_{case_id}_{slice_index}.png'  # Unique image path for each case
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        slice_paths.append(image_path)

    return jsonify({'slices': slice_paths})  # Return the slice paths as JSON
