from flask import Flask, render_template, send_file, request
import nibabel as nib
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Path to your NIfTI file
NIFTI_FILE = '/Users/g/Desktop/isles24_train_b/derivatives/sub-stroke0003/ses-01/sub-stroke0003_ses-01_space-ncct_cta.nii.gz'

@app.route('/', methods=['GET', 'POST'])
def index():
    slice_index = None  # Initialize slice_index
    if request.method == 'POST':
        slice_index = int(request.form.get('slice', -1))  # Get the slice index from the form
    return render_template('nifty.html', slice_index=slice_index)

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

if __name__ == '__main__':
    # Create a static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
