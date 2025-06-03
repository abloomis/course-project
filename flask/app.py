from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from client_socket import upload_csv, request_heatmap
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# upload csv file for heatmap microservice
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error":"No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error":"No selected file"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        print(f"Saved file to {filepath}")  # add this
        upload_csv(filepath)
    except Exception as e:
        print(f"upload_csv() failed: {e}")  # print error
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500
    
    return jsonify({"message": "CSV uploaded successfully", "filename": filename}), 200

@app.route('/heatmap', methods=['POST'])
def heatmap():
    data = request.json
    filename = data.get('filename')
    color_string = data.get('color', '')  # optional
    
    if not filename:
        return jsonify({"error": "Missing filename"}), 400
    
    try:
        image_data = request_heatmap(filename, color_string)
    except Exception as e:
        return jsonify({"error": f"Heatmap generation failed: {str(e)}"}), 500
    
    # Save image into your static folder (make sure it exists)
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    img_filename = f"heatmap_{filename}.png"
    img_path = os.path.join(static_folder, img_filename)
    
    with open(img_path, "wb") as f:
        f.write(image_data)
    
    # Return JSON with URL to image
    return jsonify({"url": f"/static/{img_filename}"})

if __name__ == '__main__':
    app.run(port=5000)