from flask import Flask, request, jsonify, redirect
from PIL import Image
from ultralytics import YOLO
from flask_cors import CORS  # Import the CORS package

app = Flask(__name__, static_folder='static')

model1 = None
CORS(app)

@app.route('/')
def home():
    return "This is Backend of WasteWise!"

@app.route('/upload', methods=['POST'])
def upload_file():
    global model1

    # Model config
    confidence = float(request.form.get('confidence', 40))
    confidence = confidence / 100  # Convert to percentage

    # Load model if not already loaded
    if model1 is None:
        try:
            model1 = YOLO('weights/model1/yoloooo.pt')
        except Exception as ex:
            return jsonify({'status': 'error', 'message': f'Error loading model: {str(ex)}'}), 500

    # Handling image file upload
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    # Process the image
    try:
        # Save the original uploaded image
        original_image_path = 'static/results/original_image.jpg'
        uploaded_file.save(original_image_path)

        # Model inference
        img = Image.open(uploaded_file)
        res = model1.predict(img, conf=confidence)

        # Extract detected classes
        detected_classes = set()  # Use a set to avoid duplicates
        for box in res[0].boxes:
            class_id = int(box.cls[0])  # Extract the class ID
            detected_classes.add(res[0].names[class_id])  # Map class ID to class name

        # Create comma-separated string of detected objects
        detected_objects_text = ', '.join(detected_classes)

        # Plot the detected image
        res_plotted = res[0].plot()[:, :, ::-1]  # Inverse the colors for saving as an image
        result_image_path = 'static/results/detected_image.jpg'
        Image.fromarray(res_plotted).save(result_image_path)

        # Return a successful response with image URLs
        return jsonify({
            'status': 'success',
            'message': 'File uploaded and processed successfully',
            # 'uploaded_image': uploaded_image_url,
            # 'result_image': result_image_url,
            # 'detected_objects_text': detected_objects_text
        })

    except Exception as ex:
        # Catch any unexpected errors and return an error response
        return jsonify({'status': 'error', 'message': f'Error processing the image: {str(ex)}'}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
