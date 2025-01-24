from flask import Flask, render_template
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image


app = Flask(__name__)


# Sample data for cases
cases = [
    {'id': 1, 'name': 'Case 1', 'image': 'case2.jpeg', 'segmentation': 'segmentation1.npy' ,'overlay': 'case3.jpeg'},
    {'id': 2, 'name': 'Case 2', 'image': 'case2.png', 'segmentation': 'segmentation2.npy'},
    {'id': 3, 'name': 'Case 3', 'image': 'case3.png', 'segmentation': 'segmentation3.npy'},
]

@app.route('/')
def index():
    print("Index route accessed")
    return render_template('index.html')




@app.route('/cases')
def case_list():
    print("Case list route accessed")
    return render_template('case_list.html', cases=cases)


# Set the upload folder path to the static/images directory
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'images')

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Assuming 'cases' is defined somewhere in your code

@app.route('/case/<int:case_id>')
def case_detail(case_id):
    case = next((case for case in cases if case['id'] == case_id), None)
    if case:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], case['image'])
        segmentation_path = os.path.join(app.config['UPLOAD_FOLDER'], case['segmentation'])
        
        # Load the main image using PIL
        main_image = Image.open(img_path).convert("RGBA")  # Convert to RGBA

        # Load the segmentation
        segmentation = np.load(segmentation_path)

        # Load the overlay image if it exists
        overlay = None
        if 'overlay' in case:
            overlay_path = os.path.join(app.config['UPLOAD_FOLDER'], case['overlay'])
            overlay = Image.open(overlay_path).convert("RGBA")  # Open overlay image and convert to RGBA

        # Convert segmentation to an image (assuming it's a 2D array)
        segmentation_img = Image.fromarray(segmentation).convert("L")  # Convert to grayscale

        # Create a figure to display the images
        fig, axes = plt.subplots(1, 3 if overlay else 2, figsize=(15, 5))
        axes[0].imshow(main_image)
        axes[0].set_title('Original Image')
        axes[0].axis('off')  # Hide axes
        axes[1].imshow(segmentation_img, cmap='gray')
        axes[1].set_title('Segmentation')
        axes[1].axis('off')  # Hide axes

        # If overlay exists, blend it with the main image
        if overlay:
            # Resize overlay to match main image size if necessary
            if overlay.size != main_image.size:
                overlay = overlay.resize(main_image.size)

            # Blend the main image and the overlay
            blended_image = Image.blend(main_image, overlay, alpha=0.5)  # Adjust alpha as needed

            # Display the blended image
            axes[2].imshow(blended_image)
            axes[2].set_title('Blended Image')
            axes[2].axis('off')  # Hide axes

            # Save the blended image to a file
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], f'result_{case_id}.png')
            blended_image.save(result_path)
        else:
            # Save the main image if no overlay is present
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], f'result_{case_id}.png')
            main_image.save(result_path)

        # Save the figure to a file
        plt.savefig(result_path)
        plt.close(fig)  # Close the figure to free memory

        return render_template('case_detail.html', case=case, result_image=f'result_{case_id}.png')
    
    return "Case not found", 404

if __name__ == '__main__':
    app.run(debug=True)
