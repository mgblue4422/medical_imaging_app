from flask import Blueprint, render_template, request, redirect, url_for ,jsonify, abort , send_from_directory
from ctpexampledb import *
from db1 import db1  # Adjust the import based on your project structure
from syntheticdatabase import ImageModel
from patientdatabase import *
import numpy as np
from PIL import Image
import pandas as pd
from io import BytesIO
import io
import base64
import os
import paramiko
from config import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD  # Import credentials
from flask_cors import CORS

syntheticdata = Blueprint('syntheticdata', __name__, static_folder='static')
CORS(app)  # This will enable CORS for all routes
@syntheticdata.route('/')
def syntheticdatapage():
    return render_template('syntheticdata.html')

@syntheticdata.route('/static/<path:filename>')
def serve_static(filename):
    return syntheticdata.send_static_file(filename)

@syntheticdata.route('/temp_files/<path:filename>')
def serve_temp(filename):
    return send_from_directory('temp_files', filename)


@syntheticdata.route('/stroke_case/temp_files/<path:filename>')
def serve_temp_with_case(filename):
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


    return render_template('syntheticviewer.html', case=case,  case_id = case_id)  # Pass the case to the template


#function to  get images from tiff to jpeg
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

# Define the temporary directory to save JPEG files relative to the location of root.py
current_directory = os.path.dirname(os.path.abspath(__file__))  # Get the directory of root.py
temp_jpeg_directory = os.path.join(current_directory, 'temp_files')

# Ensure the temporary directory exists
os.makedirs(temp_jpeg_directory, exist_ok=True)

from flask import jsonify
from PIL import Image
import paramiko
import io
import base64
import os

@syntheticdata.route('/patients/<int:patient_id>/ctp_files/tiff_slices', methods=['GET'])
def get_tiff_slices_from_ctp(patient_id):
    print(f"Received request for patient ID: {patient_id}")

    # Query the patient by ID
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    # Retrieve the CTP files associated with the patient
    ctp_files = CTPFile.query.filter_by(patient_id=patient_id).all()
    if not ctp_files:
        return jsonify({'message': 'No CTP files found for this patient'}), 404

    jpeg_images = []  # Store base64 JPEG images

    # Iterate through each CTP file to get the TIFF files from the remote folder
    for ctp_file in ctp_files:
        remote_folder_path = ctp_file.file_path  # Assuming this is the remote folder path

        try:
            # Connect to the SFTP server
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # List all folders in the remote directory
            all_folders = sftp.listdir(remote_folder_path)
            folders_to_process = all_folders  # Modify here if you want to limit folders

            for index, folder in enumerate(folders_to_process):
                folder_path = os.path.join(remote_folder_path, folder)

                # Check if the path is a directory
                if sftp.stat(folder_path).st_mode & 0o40000:
                    remote_files = sftp.listdir(folder_path)


                    # Filter for TIFF files
                    tiff_files = [f for f in remote_files if f.endswith('.tiff') or f.endswith('.tif')]
                    print(f"TIFF files found in folder {folder}: {tiff_files}")

                    # Limit images per folder
                    max_images = 16 if index == 12 else 20
                    tiff_files = tiff_files[:max_images]

                    for tiff_file in tiff_files:
                        tiff_file_path = os.path.join(folder_path, tiff_file)
                        try:
                            with sftp.open(tiff_file_path, 'rb') as remote_file:
                                tiff_bytes = remote_file.read()

                            tiff_stream = io.BytesIO(tiff_bytes)
                            with Image.open(tiff_stream) as img:
                                img = img.convert('RGB')
                                jpeg_stream = io.BytesIO()
                                img.save(jpeg_stream, format='JPEG')
                                jpeg_stream.seek(0)

                                jpeg_base64 = base64.b64encode(jpeg_stream.read()).decode('utf-8')
                                jpeg_images.append({
                                    'filename': f"{folder}_{tiff_file}",
                                    'base64_jpeg': jpeg_base64
                                })
                        except Exception as e:
                            print(f"Error processing {tiff_file}: {e}")
                            continue

            sftp.close()
            transport.close()

        except Exception as e:
            print(f"Error accessing SFTP server: {e}")
            return jsonify({'error': 'Failed to access the SFTP server'}), 500

    if not jpeg_images:
        return jsonify({'message': 'No TIFF images could be processed'}), 404
    print(f"Returning {len(jpeg_images)} images")

    return jsonify({'patient_id': patient.id, 'images': jpeg_images}), 200

#function to show example ctp images
@syntheticdata.route('/get_images', methods=['GET'])
def get_images():
    try:
        # Query the database to get all images, ordered by filename
        images = CTPExampleModel.query.order_by(CTPExampleModel.filename).all()
        print(f"Fetched {len(images)} images from the database.")

        # Prepare a list of image data to return
        image_list = []
        for image in images:

            if image.image_data:
                encoded_image_data = base64.b64encode(image.image_data).decode('utf-8')
                print(f"Image ID {image.id} has data.")
            else:
                print(f"Image ID {image.id} has no data.")
                continue

            # Encode the image data to Base64
            encoded_image_data = base64.b64encode(image.image_data).decode('utf-8')
            image_list.append({
                'id': image.id,
                'filename': image.filename,
                'image_data': encoded_image_data  # Store the Base64 encoded image data
            })

        return jsonify(image_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@syntheticdata.route('/patients/<int:patient_id>/ctp_files/view_tiff_slices', methods=['GET'])
def view_tiff_slices_from_ctp(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    ctp_files = CTPFile.query.filter_by(patient_id=patient_id).all()
    if not ctp_files:
        return jsonify({'message': 'No CTP files found for this patient'}), 404

    jpeg_images = []

    for ctp_file in ctp_files:
        remote_folder_path = ctp_file.file_path

        try:
            transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
            transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
            sftp = paramiko.SFTPClient.from_transport(transport)

            all_folders = sftp.listdir(remote_folder_path)
            folders_to_process = all_folders[:13]  # Only process first 13 folders

            for index, folder in enumerate(folders_to_process):
                folder_path = os.path.join(remote_folder_path, folder)

                if sftp.stat(folder_path).st_mode & 0o40000:
                    remote_files = sftp.listdir(folder_path)
                    tiff_files = [f for f in remote_files if f.endswith('.tiff') or f.endswith('.tif')]

                    max_images = 16 if index == 12 else 20

                    for tiff_file in tiff_files[:max_images]:
                        tiff_file_path = os.path.join(folder_path, tiff_file)

                        try:
                            with sftp.open(tiff_file_path, 'rb') as remote_file:
                                tiff_bytes = remote_file.read()

                            tiff_stream = io.BytesIO(tiff_bytes)
                            with Image.open(tiff_stream) as img:
                                img = img.convert('RGB')
                                jpeg_stream = io.BytesIO()
                                img.save(jpeg_stream, format='JPEG')
                                jpeg_stream.seek(0)
                                jpeg_base64 = base64.b64encode(jpeg_stream.read()).decode('utf-8')
                                jpeg_images.append({
                                    'filename': f"{folder}_{tiff_file}",
                                    'base64': jpeg_base64
                                })

                        except Exception as e:
                            print(f"TIFF processing error: {e}")
                            continue

            sftp.close()
            transport.close()
        except Exception as e:
            print(f"SFTP error: {e}")
            return jsonify({'error': 'Failed to access the SFTP server'}), 500

    return render_template('view_images.html', patient_id=patient_id, images=jpeg_images)