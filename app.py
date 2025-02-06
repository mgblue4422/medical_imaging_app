from flask import Flask, render_template, jsonify, request
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import io
import base64


app = Flask(__name__)


# Sample data for cases
cases = [
    {'id': 1, 'name': 'Case 1', 'image': 'case2.jpeg', 'segmentation': 'segmentation1.npy' ,'overlay': 'case3.jpeg'},
    {'id': 2, 'name': 'Case 2', 'image': 'case2.png', 'segmentation': 'segmentation2.npy'},
    {'id': 3, 'name': 'Case 3', 'image': 'case3.png', 'segmentation': 'segmentation3.npy'},
]




# Set the upload folder path to the static/images directory
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'images')

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Assuming 'cases' is defined somewhere in your code

