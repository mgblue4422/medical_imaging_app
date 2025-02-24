from flask import Flask, render_template, send_file, request
import nibabel as nib
import matplotlib.pyplot as plt
import os
import imageio  # Import imageio for GIF creation

app = Flask(__name__)

# Path to your NIfTI file
NIFTI_FILE = '/Users/g/Desktop/isles24_train_b/derivatives/sub-stroke0003/ses-01/sub-stroke0003_ses-01_space-ncct_cta.nii.gz'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('nifty2.html')


@app.route('/slice/<int:slice_index>')
def slice_image(slice_index):
    # Load the NIfTI file
    img = nib.load(NIFTI_FILE)
    data = img.get_fdata()

    # Get the specified slice
    if slice_index < 0 or slice_index >= data.shape[2]:
        return "Slice index out of range", 404

    slice_data = data[:, :, slice_index]

    # Create a PNG image from the slice
    plt.imshow(slice_data, cmap='gray')
    plt.axis('off')
    image_path = f'static/slice_{slice_index}.png'
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return send_file(image_path)


@app.route('/gif')
def create_gif():
    # Load the NIfTI file
    img = nib.load(NIFTI_FILE)
    data = img.get_fdata()

    # Create a temporary directory for images
    temp_dir = 'temp_images'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Generate images for each slice and save them
    images = []
    for i in range(data.shape[2]):
        slice_data = data[:, :, i]
        plt.imshow(slice_data, cmap='gray')
        plt.axis('off')
        image_path = f'{temp_dir}/slice_{i}.png'
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        images.append(image_path)

    # Create a GIF from the images
    gif_path = 'static/slices_animation.gif'
    with imageio.get_writer(gif_path, mode='I', duration=0.1) as writer:  # Adjust duration for speed
        for image in images:
            writer.append_data(imageio.imread(image))

    # Clean up temporary images
    for image in images:
        os.remove(image)
    os.rmdir(temp_dir)

    return send_file(gif_path)


if __name__ == '__main__':
    # Create a static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
