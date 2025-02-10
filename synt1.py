@app.route('/upload', methods=['POST'])
def upload_image():
    # Hent bildene fra form-data
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file1 = request.files['image1']
    file2 = request.files['image2']

    # Les bildene
    image1_data = file1.read()
    image2_data = file2.read()

    # Analyser bildene
    result_image1 = analyze_image(image1_data)
    result_image2 = analyze_image(image2_data)

    # Konverter resultatene tilbake til bilder for visning (kan også returnere som data)
    _, img_encoded1 = cv2.imencode('.png', result_image1)
    _, img_encoded2 = cv2.imencode('.png', result_image2)

    result_image1_base64 = img_encoded1.tobytes()
    result_image2_base64 = img_encoded2.tobytes()

    print("Resultat bilde 1:", result_image1_base64[:20])  # Logg en del av bildet for debugging
    print("Resultat bilde 2:", result_image2_base64[:20])  # Logg en del av bildet for debugging

    return jsonify({
        'image1_result': result_image1_base64,
        'image2_result': result_image2_base64
    })
