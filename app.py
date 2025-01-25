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

@app.route('/feature_examples')
def features():
    return render_template('feature_examples.html')

# Server side plotting example
@app.route('/plot_sin', methods=['POST'])
def plot_sin():
    data = request.get_json()  # Parse JSON body
    x_value = float(data['x_value'])

    # Generate the plot
    x = np.linspace(-10, 10, 100)
    y = np.sin(x * x_value)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title('Dynamic Sin(x) Plot')

    # Enable grid
    ax.grid(True)

    # Customize x-axis labels (multiples of pi)
    pi_ticks = np.pi * np.arange(-3, 4, 1)  # Ticks at -3π, -2π, ..., 2π, 3π
    ax.set_xticks(pi_ticks)  # Set x-ticks to multiples of π
    ax.set_xticklabels([f'{int(i / np.pi)}π' if i != 0 else '0' for i in pi_ticks])  # Label with multiples of π

    # Save plot to a BytesIO stream
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return jsonify({'plot': plot_data})

if __name__ == '__main__':
    app.run(debug=True)
