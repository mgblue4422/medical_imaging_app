from flask import Flask, render_template
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Load your own images
    real_data = plt.imread("static/images/case1.png")  # Replace with the path to your real image
    synthetic_data = plt.imread("static/images/case2.jpeg")  # Replace with the path to your synthetic image

    # Ensure the images are in the correct format (normalize if grayscale)
    if len(real_data.shape) == 2:  # Grayscale image
        real_data = real_data / 255.0  # Normalize intensity
    if len(synthetic_data.shape) == 2:  # Grayscale image
        synthetic_data = synthetic_data / 255.0

    # Plot Real Data
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(real_data, cmap="viridis", extent=[0, 10, 0, 10], origin="lower")
    plt.colorbar(label="Intensity")
    plt.title("Real Data (CTP)")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    # Plot Synthetic Data
    plt.subplot(1, 2, 2)
    plt.imshow(synthetic_data, cmap="viridis", extent=[0, 10, 0, 10], origin="lower")
    plt.colorbar(label="Intensity")
    plt.title("Synthetic Data (CTP)")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")

    plt.tight_layout()
    plt.savefig('static/images/plot.png')  # Save the plot as an image
    plt.close()  # Close the plot to free memory

    # Create a table to describe the differences
    data = {
        "Feature": ["Source", "Noise", "Pattern", "Realism"],
        "Real Data": ["Collected from actual CTP scans", "Contains noise and irregularities", "Irregular, patient-specific patterns", "High"],
        "Synthetic Data": ["Generated mathematically or via models", "Minimal to no noise", "Smooth and idealized patterns", "Low"]
    }

    # Create a DataFrame
    comparison_table = pd.DataFrame(data)

    # Convert the DataFrame to HTML
    table_html = comparison_table.to_html(index=False)

    return render_template('index.html', table=table_html)

if __name__ == '__main__':
    app.run(debug=True)
