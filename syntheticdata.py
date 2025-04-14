from flask import Blueprint, render_template, request, redirect, url_for ,jsonify, current_app , send_from_directory

from db1 import db1  # Adjust the import based on your project structure
from syntheticdatabase import ImageModel

import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
import os
import paramiko
from config import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD  # Import credentials

syntheticdata = Blueprint('syntheticdata', __name__, static_folder='static')

@syntheticdata.route('/')
def syntheticdatapage():
    return render_template('syntheticdata.html')

@syntheticdata.route('/static/<path:filename>')
def serve_static(filename):
    return syntheticdata.send_static_file(filename)

@syntheticdata.route('/temp_files/<path:filename>')
def serve_temp(filename):
    return send_from_directory('temp_files', filename)
@syntheticdata.route('/list')
def list_synthetic_patients():
    # Fetch unique synthetic patient IDs from the ImageModel
    unique_synthetic_patients = ImageModel.query.with_entities(ImageModel.synthetic_patient_id).distinct().all()

    # Extract the synthetic patient IDs from the query result
    synthetic_patient_ids = [patient[0] for patient in unique_synthetic_patients]

    print(f"Unique synthetic patients fetched: {synthetic_patient_ids}")  # Debugging line
    return render_template('list_synthetic_patients.html', synthetic_patient_ids=synthetic_patient_ids)  # Render the list of unique synthetic patient IDs



@syntheticdata.route('/stroke_case/<string:case_id>')

def stroke_case(case_id):

    case = ImageModel.query.filter_by(synthetic_patient_id=case_id).first_or_404()  # Fetch the synthetic case by ID


    return render_template('syntheticviewer1.html', case=case,  case_id = case_id)  # Pass the case to the template



@syntheticdata.route('/tiff_slices/<synthetic_patient_id>', methods=['GET'])
def get_tiff_slices(synthetic_patient_id):
    print(f"Received request for patient ID: {synthetic_patient_id}")

    image_record = ImageModel.query.filter_by(synthetic_patient_id=synthetic_patient_id).first()
    if not image_record:
        return jsonify({'error': 'No images found for the specified synthetic patient ID'}), 404

    # Create a temporary directory to store the downloaded file
    base_folder_path = os.path.join('temp_files')
    os.makedirs(base_folder_path, exist_ok=True)

    # Get the file path from the database
    remote_file_path = image_record.file_path  # This should be the remote path
    local_file_path = os.path.join(base_folder_path, os.path.basename(remote_file_path))

    # Download the file from the SFTP server
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(remote_file_path, local_file_path)  # Download the file
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"Error downloading file: {e}")
        return jsonify({'error': 'Failed to download the file from the SFTP server'}), 500

    # Open the TIFF image from the local file path
    img = Image.open(local_file_path)

    # Check the number of frames in the TIFF image
    num_frames = img.n_frames
    print(f"Number of frames (slices): {num_frames}")

    slice_paths = []

    for slice_index in range(num_frames):
        img.seek(slice_index)  # Move to the desired frame
        slice_data = np.array(img)  # Convert the current frame to a NumPy array

        print(f"Slice {slice_index} shape: {slice_data.shape}")  # Print the shape of the slice

        # Save the slice as a JPEG
        slice_filename = os.path.join(base_folder_path, f'slice_{synthetic_patient_id}_{slice_index}.jpg')
        Image.fromarray(slice_data).convert('RGB').save(slice_filename, 'JPEG')  # Convert to RGB before saving as JPEG
        slice_paths.append(slice_filename)

        if os.path.exists(slice_filename):
            print(f"Successfully saved: {slice_filename}")
        else:
            print(f"Failed to save: {slice_filename}")

    return jsonify({'slices': slice_paths})  # Return the slice paths as JSON