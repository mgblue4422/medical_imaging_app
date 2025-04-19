import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from db1 import db1  # Import the db1 instance

app = Flask(__name__)
# Get the directory of the current file (this file)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the database URI using a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database.db")}'
app.config['SECRET_KEY'] = 'your_secret_key'

db1.init_app(app)

# New model for storing images
class CTPExampleModel(db1.Model):
    __tablename__ = 'ctpexample'  # Specify the table name
    id = db1.Column(db1.Integer, primary_key=True)
    filename = db1.Column(db1.String(150), nullable=False)
    image_data = db1.Column(db1.LargeBinary, nullable=False)  # To store the image data

# Create the database tables if they do not exist
with app.app_context():
    db1.create_all()  # Create new tables if they do not exist

def process_images():
    image_folder = '/Users/g/Desktop/ctp_images_temp_folder/example'  # Update this path
    try:
        for root, dirs, files in os.walk(image_folder):
            for filename in files:
                if allowed_file(filename):
                    file_path = os.path.join(root, filename)

                    # Read the image data
                    with open(file_path, 'rb') as file:
                        image_data = file.read()  # Read the binary data of the image

                    # Save metadata and image data to the database
                    new_image = CTPExampleModel(
                        filename=filename,
                        image_data=image_data  # Store the image data
                    )
                    db1.session.add(new_image)
            db1.session.commit()  # Commit after processing all images in a folder
    except Exception as e:
        print(f"An error occurred: {e}")  # Log the error message

@app.route('/add_images', methods=['GET'])  # Keep as GET
def add_images():
    process_images()  # Call the function to process and add images to the database
    return jsonify({"message": "Images uploaded successfully!"}), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    app.run(debug=True)
