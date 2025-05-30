from flask import Blueprint, render_template, request, redirect, url_for ,jsonify, current_app
from decorators import login_required
from db1 import db1  # Adjust the import based on your project structure
from patientdatabase import Patient ,CTAFile, CBFFile ,CBVFile ,CTPFile ,MRIFile  ,MTTFile , TMAXFile , GroundTruthFile ,DoctorNote
import nibabel as nib  # Add this line
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
import pydicom
import io
import base64
import os
import paramiko
from forms import PatientForm
from config import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD  # Import credentials



# Initialize the Blueprint
patients_bp = Blueprint('patients', __name__)


@patients_bp.route('/')
@login_required
def patients():
    return render_template('patients.html')  # Render patients.html

@patients_bp.route('/static/<path:filename>')
def serve_static(filename):
    return patients_bp.send_static_file(filename)
@patients_bp.route('/list')
def list_patients():
    patients = Patient.query.all()  # Fetch all patients from the database

    print(f"Patients fetched: {patients}")  # Debugging line
    return render_template('list_patients.html', patients=patients)  # Render the list of patients


@patients_bp.route('/upload', methods=['GET', 'POST'])
def upload_patient():
    if request.method == 'POST':
        patient_name = request.form['name']
        # Here you would typically save the patient to a database
        return redirect(url_for('patients.list_patients'))  # Redirect to the list of patients
    return redirect(url_for('add_patient'))

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
    case = Patient.query.get_or_404(case_id)  # Fetch the stroke case by ID
    csv_files = case.csv_files  # Fetch the associated CSV files

    # Read CSV data into a dictionary
    csv_data = {}  # Initialize a dictionary to store CSV data

    for csv_file in csv_files:
        # Check if file_data is None
        if csv_file.file_data is None:
            print(f"File data is None for file: {csv_file.filename}")
            csv_data[csv_file.filename] = "<p>Error: No data available for this file.</p>"
            continue  # Skip to the next file

        print(f"Processing file: {csv_file.filename}, Size: {len(csv_file.file_data)} bytes")
        try:
            # Use BytesIO to read the binary data as a CSV
            df = pd.read_csv(BytesIO(csv_file.file_data))

            # Clean the DataFrame by dropping columns with any missing values
            df_cleaned = df.dropna(axis=1, how='any')

            # Convert the cleaned DataFrame to an HTML table and store it in the dictionary
            csv_data[csv_file.filename] = df_cleaned.transpose().to_html(classes='table table-striped', index=True)

        except Exception as e:
            # Log the error message and continue to the next file
            print(f"Error processing file {csv_file.filename}: {e}")
            csv_data[
                csv_file.filename] = f"<p>Error processing this file: {e}</p>"  # Optional: Store the error message in the dictionary

    # Render the template with the case and CSV data
    return render_template('patientviewer8.html', case=case, patient_name=case.patient_name, csv_data=csv_data)


@patients_bp.route('/download_csv/<int:file_id>')
@login_required
def download_csv(file_id):
    csv_file = CSVFile.query.get_or_404(file_id)  # Fetch the CSV file by ID
    response = make_response(csv_file.file_data)
    response.headers['Content-Disposition'] = f'attachment; filename={csv_file.filename}'
    response.headers['Content-Type'] = 'text/csv'  # Adjust the content type if necessary
    return response


@patients_bp.route('/patients/<patient_name>/save_notes', methods=['POST'])
@login_required  # Protect this route with login_required
def save_notes_for_case(patient_name):
    data = request.json
    notes = data.get('notes', '')

    # Fetch the patient case by ID
    case = Patient.query.filter_by(patient_name=patient_name).first()
    patient = case.patient  # Assuming the case has a relationship to the Patient model

    if patient:
        # Create a new DoctorNote instance
        new_note = DoctorNote(patient_id=patient.id, note=notes)
        db1.session.add(new_note)  # Add the new note to the session
        try:
            db1.session.commit()  # Commit the changes to the database
            return jsonify({"message": "Doctor's notes saved successfully.", "note_id": new_note.id}), 200
        except Exception as e:
            db1.session.rollback()  # Rollback in case of error
            return jsonify({"message": "An error occurred while saving notes.", "error": str(e)}), 500
    else:
        return jsonify({"message": "Patient not found."}), 404


@patients_bp.route('/patients/<patient_name>/get_notes', methods=['GET'])
@login_required  # Protect this route with login_required
def get_notes_for_case(patient_name):
    case = Patient.query.filter_by(patient_name=patient_name).first()
   # case = Patient.query.get_or_404(case_id)
    patient = case.patient  # Assuming the case has a relationship to the Patient model

    if patient:
        notes = DoctorNote.query.filter_by(patient_id=patient.id).all()  # Fetch all notes for the patient
        notes_data = [{"id": note.id, "note": note.note, "created_at": note.created_at.isoformat()} for note in notes]
        return jsonify({"notes": notes_data}), 200
    else:
        return jsonify({"message": "Patient not found."}), 404

#slices  with no overlay
@patients_bp.route('/slices2/<patient_name>/<file_type>', methods=['GET'])
def get_slices2(patient_name, file_type):
    # Query the Patient by name
    patient = Patient.query.filter_by(patient_name=patient_name).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Determine which file type to query based on the file_type parameter
    if file_type == 'ctp':
        file_record = CTPFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'mri':
        file_record = MRIFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'mtt':
        file_record = MTTFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cbv':
        file_record = CBVFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cbf':
        file_record = CBFFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'tmax':
        file_record = TMAXFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cta':
        file_record = CTAFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'ground_truth':
        file_record = GroundTruthFile.query.filter_by(patient_id=patient.id).first()
    else:
        return jsonify({'error': 'Invalid file type'}), 400

    if not file_record:
        return jsonify({'error': f'{file_type.upper()} file not found for patient {patient_name}'}), 404
    # Use the file path directly from the file_record
    file_path = file_record.file_path

    # Check if the file path is remote
    if is_remote_file(file_path):
        return handle_remote_file(file_path, patient_name, file_type)


    if not os.path.isfile(file_path):
        return jsonify({'error': 'Provided path is not a valid file'}), 400

    # Check if it's a DICOM file
    if file_path.endswith('.dcm') or not os.path.splitext(file_path)[1]:  # handles no-extension
        return process_dicom_file(file_path)
    # Continue with the existing logic for local files


    # Load the NIfTI file
    img = nib.load(file_path)
    data = img.get_fdata()  # Load the data from the NIfTI file

    if file_type == 'ctp':
        data = data[:, :, :, 0]  # Use the first 3D volume from the 4D data

    # Print the shape of the data
    print(f"Data shape: {data.shape}")

    def normalize(data, vmin=None, vmax=None):
        if vmin is None:
            vmin = np.min(data)
        if vmax is None:
            vmax = np.max(data)
        return np.clip((data - vmin) / (vmax - vmin), 0, 1)

    # Inside your get_slices2 function, after loading the NIfTI file
    # Define normalization parameters for each file type
    normalization_params = {
        'cbf': (0, 100),
        'cbv': (0, 5),
        'mtt': (7, 13),
        'tmax': (2, 10),
        'cta':(0,100),
        'ctp': (0, 100)
    }

    # Generate paths for all slices
    slice_paths = []
    # Handle the ctp file type separately


        # For other file types, process as before
    for slice_index in range(data.shape[2]):  # Assuming the third dimension is the slice dimension
        slice_data = data[:, :, slice_index]
        print(f"Slice index: {slice_index}, Slice shape: {slice_data.shape}")

        # Check for empty slices
        if slice_data.size == 0 or slice_data.shape[0] == 0 or slice_data.shape[1] == 0:
            print(f"Skipping empty slice at index {slice_index}")
            continue

        # Normalize the slice data based on the file type
        if file_type in normalization_params:
            vmin, vmax = normalization_params[file_type]
            slice_data = normalize(slice_data, vmin=vmin, vmax=vmax)

        # Ensure the data type is appropriate for imshow
        slice_data = slice_data.astype(np.float32)  # or np.uint8, depending on your data

        # Set the colormap based on the file type
        if file_type in ('cta', 'ctp'):
            cmap = 'gray'
        else:
            cmap = 'jet'

        plt.imshow(slice_data, cmap=cmap)
        plt.axis('off')

        # Check if the colormap is 'jet' before adding the color bar
        if cmap == 'jet':
            cb = plt.colorbar(fraction=0.046, pad=0.04)  # Create a color bar
            cb.set_label("Value Scale")  # Set the label for the color bar


        image_path = f'static/slice_{patient_name}_{file_type}_{slice_index}.png'  # Unique image path for each slice
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        slice_paths.append(image_path)

    return jsonify({'slices': slice_paths})  # Return the slice paths as JSON




@patients_bp.route('/slices/<patient_name>/<file_type>', methods=['GET'])
def get_slices(patient_name, file_type):
    # Query the Patient by name
    print(f"Request made for patient: {patient_name}, file type: {file_type}")
    patient = Patient.query.filter_by(patient_name=patient_name).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Get the ground truth file if it exists
    ground_truth_file = GroundTruthFile.query.filter_by(patient_id=patient.id).first()

    # Determine which file type to query based on the file_type parameter
    file_record = None
    if file_type == 'ctp':
        file_record = CTPFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'mri':
        file_record = MRIFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'mtt':
        file_record = MTTFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cbv':
        file_record = CBVFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cbf':
        file_record = CBFFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'tmax':
        file_record = TMAXFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'cta':
        file_record = CTAFile.query.filter_by(patient_id=patient.id).first()
    elif file_type == 'ground_truth':
        file_record = ground_truth_file
    else:
        return jsonify({'error': 'Invalid file type'}), 400

    if not file_record:
        return jsonify({'error': f'{file_type.upper()} file not found for patient {patient_name}'}), 404

        # Check if the requested file type is 'ctp'
    if file_type != 'ctp':
        return jsonify({'error': f'{file_type.upper()} files are not available'}), 404

    # Use the file path directly from the file_record
    file_path = file_record.file_path

    # Check if the file path is remote
    if is_remote_file(file_path):
        return handle_remote_file(file_path, patient_name, file_type, ground_truth_file)
    else:
    # Continue with the existing logic for local files

        # Load the NIfTI file
        img = nib.load(file_path)
        data = img.get_fdata()  # Load the data from the NIfTI file

        if file_type == 'ctp':
            data = data[:, :, :, 0]  # Use the first 3D volume from the 4D data

        def normalize(data, vmin=None, vmax=None):
            if vmin is None:
                vmin = np.min(data)
            if vmax is None:
                vmax = np.max(data)
            return np.clip((data - vmin) / (vmax - vmin), 0, 1)

        # Define normalization parameters for each file type
        normalization_params = {
            'cbf': (0, 100),
            'cbv': (0, 5),
            'mtt': (7, 13),
            'tmax': (2, 10),
            'cta': (0, 100),
            'ctp': (0, 100)
        }

        # Generate paths for all slices
        slice_paths = []

        for slice_index in range(data.shape[2]):  # Assuming the third dimension is the slice dimension
            slice_data = data[:, :, slice_index]
            print(f"Slice index: {slice_index}, Slice shape: {slice_data.shape}")

            # Check for empty slices
            if slice_data.size == 0 or slice_data.shape[0] == 0 or slice_data.shape[1] == 0:
                print(f"Skipping empty slice at index {slice_index}")
                continue

            # Normalize the slice data based on the file type
            if file_type in normalization_params:
                vmin, vmax = normalization_params[file_type]

                slice_data = normalize(slice_data, vmin=vmin, vmax=vmax)
            else:
                # If no normalization parameters are defined for the file type, you can choose to skip normalization
                print(f"No normalization parameters for file type: {file_type}")

            # Ensure the data type is appropriate for imshow
            slice_data = (slice_data * 255).astype(np.uint8)  # Convert to 8-bit grayscale
            print("Slice data type:", type(slice_data))  # Check the type
            print("Slice data shape:", slice_data.shape)  # Check the shape
            print("Slice data content:", slice_data)  # Print the actual data
            print("Contains NaN:", np.isnan(slice_data).any())  # Check for NaN values
            print("Contains Inf:", np.isinf(slice_data).any())  # Check for Inf values

            # Create the base image
            plt.imshow(slice_data, cmap='gray', vmin=0, vmax=255)
            plt.axis('off')
            base_image_path = f'static/slice_{patient_name}_{file_type}_{slice_index}.png'
            plt.savefig(base_image_path, bbox_inches='tight', pad_inches=0)
            plt.close()

            # If the file type is not ground_truth, overlay the ground truth if it exists
            if file_type != 'ground_truth' and ground_truth_file:
                ground_truth_temp_path = os.path.join('temp_files', ground_truth_file.filename)
                # Open the source file and read its contents
                with open(ground_truth_file.file_path, 'rb') as source_file:
                    with open(ground_truth_temp_path, 'wb') as dest_file:
                        dest_file.write(source_file.read())  # Write the bytes to the destination file

                # Load the NIfTI image from the temporary file

                ground_truth_img = nib.load(ground_truth_temp_path)
                ground_truth_data = ground_truth_img.get_fdata()[:, :, slice_index].astype(np.float32)

                # Create an overlay
                overlay_image = Image.new('RGB', slice_data.shape[::-1])

                # Convert slice_data to an image
                base_image = Image.fromarray(slice_data).convert('RGBA')

                # Create a transparent overlay
                overlay = np.zeros((*ground_truth_data.shape, 4), dtype=np.uint8)  # (H, W, 4) for RGBA

                # Set the overlay color (e.g., red with 100 alpha)
                overlay_color = (255, 0, 0, 50)  # Semi-transparent red

                # Apply the overlay only where segmentation is white
                overlay[:, :, 3] = 0  # Ensure full transparency as default
                overlay[ground_truth_data > 0.5] = overlay_color

                # Convert overlay to an image
                overlay_image = Image.fromarray(overlay, mode='RGBA')

                combined_image = base_image.copy()
                combined_image.paste(overlay_image, (0, 0), overlay_image)  # Ensure proper transparency
                # Save the combined image
                combined_image_path = f'static/slice_{patient_name}_{file_type}_overlay_{slice_index}.png'
                combined_image.save(combined_image_path)

                # Use the combined image path for the overlay
                slice_paths.append(combined_image_path)
            else:
                # If it's a ground truth image, just use the base image
                slice_paths.append(base_image_path)

        return jsonify({'slices': slice_paths})  # Return the slice paths as JSON


def is_remote_file(file_path):
    return file_path.startswith('/nfs') or file_path.startswith('/home')

def handle_remote_file(file_path, patient_name, file_type, ground_truth_file=None):
    print("starting remote function")

    jpeg_images = []

    try:
        # Setup SFTP connection
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # List all folders in the remote directory
        all_folders = sorted(sftp.listdir(file_path))

        for folder in all_folders:
            folder_path = os.path.join(file_path, folder)

            # Check if it's a directory
            if sftp.stat(folder_path).st_mode & 0o40000:
                remote_files = sftp.listdir(folder_path)

                # Separate TIFF and DICOM (or no-extension) files
                tiff_files = sorted(
                    [f for f in remote_files if f.endswith('.tiff') or f.endswith('.tif')]
                )
                dicom_files = sorted(
                    [f for f in remote_files if not f.endswith(('.tiff', '.tif'))]
                )

                # Process TIFF files
                for tiff_file in tiff_files:
                    tiff_file_path = os.path.join(folder_path, tiff_file)
                    jpeg_images.extend(process_image_file(sftp, tiff_file_path, folder, tiff_file))

                # Process DICOM (or no-extension) files
                for dicom_file in dicom_files:
                    dicom_file_path = os.path.join(folder_path, dicom_file)
                    jpeg_images.extend(process_dicom_file_remote(sftp, dicom_file_path, folder, dicom_file))

            else:
                # If it's not a folder, just process the file as DICOM (for non-nested cases)
                dicom_file_path = os.path.join(file_path, folder)
                jpeg_images.extend(process_dicom_file_remote(sftp, dicom_file_path, "", folder))

        sftp.close()
        transport.close()

    except Exception as e:
        print(f"SFTP error: {e}")
        return jsonify({'error': 'Failed to access the SFTP server'}), 500

    # Return the base64-encoded JPEG images
    base64_images = [f"data:image/jpeg;base64,{img['base64']}" for img in jpeg_images]
    return jsonify(base64_images)


def process_image_file(sftp, file_path, folder, file_name):
    jpeg_images = []
    try:
        with sftp.open(file_path, 'rb') as remote_file:
            tiff_bytes = remote_file.read()

        tiff_stream = io.BytesIO(tiff_bytes)
        with Image.open(tiff_stream) as img:
            img = img.convert('RGB')
            jpeg_stream = io.BytesIO()
            img.save(jpeg_stream, format='JPEG')
            jpeg_stream.seek(0)
            jpeg_base64 = base64.b64encode(jpeg_stream.read()).decode('utf-8')
            jpeg_images.append({
                'filename': f"{folder}_{file_name}",
                'base64': jpeg_base64
            })

    except Exception as e:
        print(f"TIFF processing error: {e}")

    return jpeg_images

def process_dicom_file_remote(sftp, file_path, folder, file_name):
    jpeg_images = []

    try:
        # Check if the file has a DICOM-like format (without extension)
        dicom_file_path = file_path
        if len(file_name.split('.')[-1]) == 0:  # If there's no extension
            dicom_file_path = f"{file_path}.dcm"  # Add .dcm extension to the file path

        print(f"Attempting to open file: {dicom_file_path}")

        with sftp.open(dicom_file_path, 'rb') as remote_file:
            dicom_bytes = remote_file.read()

        dicom_stream = io.BytesIO(dicom_bytes)
        try:
            dicom_data = pydicom.dcmread(dicom_stream)
        except Exception as e:
            print(f"Failed to read DICOM data from {dicom_file_path}: {e}")
            return jpeg_images  # If it's not a valid DICOM file, skip

        # Check if it's a valid DICOM file with PixelData
        if 'PixelData' in dicom_data:
            print(f"Pixel data found in DICOM file: {dicom_file_path}")
            img_array = dicom_data.pixel_array
            img = Image.fromarray(img_array)
            img = img.convert('RGB')  # Ensure the image is in RGB format

            jpeg_stream = io.BytesIO()
            img.save(jpeg_stream, format='JPEG')
            jpeg_stream.seek(0)
            jpeg_base64 = base64.b64encode(jpeg_stream.read()).decode('utf-8')

            jpeg_images.append({
                'filename': f"{folder}_{file_name}_DCM",
                'base64': jpeg_base64
            })
            print(f"Converted DICOM to JPEG and encoded it to base64")

    except Exception as e:
        print(f"Error processing file {file_name} in folder {folder}: {e}")

    return jpeg_images


def process_dicom_file(file_path):
    try:
        dcm = pydicom.dcmread(file_path)
        pixel_array = dcm.pixel_array

        # Convert to PIL Image
        image = Image.fromarray(pixel_array).convert("L")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        base64_images = [f"data:image/jpeg;base64,{encoded_image}"]
        return jsonify(base64_images)

    except Exception as e:
        return jsonify({'error': f'Failed to process DICOM: {str(e)}'}), 500