import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from db1 import db1  # Import the db1 instance

app = Flask(__name__)
EXTERNAL_DRIVE_PATH = '/Volumes/Seagate Bac/Thesis project 2025/database.db'  # Update this path accordingly
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + EXTERNAL_DRIVE_PATH
app.config['SECRET_KEY'] = 'your_secret_key'
db1.init_app(app)

# New model for storing histogram images
class HistogramImageModel(db1.Model):
    __tablename__ = 'histogram_image'  # Specify the table name
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(150), nullable=False)
    dimension = db1.Column(db1.String(10), nullable=False)  # '2D' or '3D'
    value1 = db1.Column(db1.String(50), nullable=False)  # First value being plotted
    value2 = db1.Column(db1.String(50), nullable=False)  # Second value being plotted
    category = db1.Column(db1.String(50), nullable=False)  # 'LVO', 'NonLVO', or 'All'
    recanalization_status = db1.Column(db1.String(50), nullable=True)  # 'Recanalized' or 'NonRecanalized' (if applicable)
    image_data = db1.Column(db1.LargeBinary, nullable=False)  # To store the image data

# Create the database tables if they do not exist
with app.app_context():
    db1.create_all()  # Create new tables if they do not exist

def process_histogram_images():
    histogram_data_folder = '/Volumes/Seagate Bac/analysis_imgs/3D Histogram curves/'  # Update this path
    try:
        for root, dirs, files in os.walk(histogram_data_folder):
            for filename in files:
                if allowed_file(filename):
                    file_path = os.path.join(root, filename)
                    category = os.path.basename(root)  # Get the folder name as category

                    # Determine dimension and values being plotted from the filename
                    dimension = '2D' if '2D' in filename else '3D'
                    parts = filename.split('_')
                    value1 = parts[0]  # First value
                    value2 = parts[1]  # Second value

                    # Determine the category and recanalization status
                    if 'LVO' in filename:
                        category = 'LVO'
                        recanalization_status = 'Recanalized' if 'Recanalized' in filename else 'NonRecanalized'
                    elif 'NonLVO' in filename:
                        category = 'NonLVO'
                        recanalization_status = None
                    else:
                        category = 'All'
                        recanalization_status = None

                    # Read the image data
                    with open(file_path, 'rb') as file:
                        image_data = file.read()  # Read the binary data of the image

                    # Save metadata and image data to the database
                    new_histogram_image = HistogramImageModel(
                        filename=filename,
                        dimension=dimension,
                        value1=value1,
                        value2=value2,
                        category=category,
                        recanalization_status=recanalization_status,
                        image_data=image_data  # Store the image data
                    )
                    db1.session.add(new_histogram_image)
            db1.session.commit()  # Commit after processing all images in a folder
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error message


@app.route('/add_histogram_images', methods=['GET'])  # Keep as GET
def add_histogram_images():
    process_histogram_images()  # Call the function to process and add histogram images to the database
    return jsonify({"message": "Histogram images uploaded successfully!"}), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'tiff', 'tif'}

if __name__ == '__main__':
    app.run(debug=True)
