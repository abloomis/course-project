from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
# Assuming client_socket and its functions (upload_csv, request_heatmap) are correctly defined elsewhere
# and handle communication with other microservices (e.g., for heatmap generation).
# For the purpose of this problem, we'll focus on the ranking logic.
# from client_socket import upload_csv, request_heatmap
from werkzeug.utils import secure_filename
import tempfile
import requests

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Placeholder for client_socket functions if they are not provided
# In a real scenario, you would have these implemented or imported.
def upload_csv(filepath):
    print(f"Simulating CSV upload for heatmap: {filepath}")
    # This would typically send the file to your heatmap microservice
    pass

def request_heatmap(filename, color_string):
    print(f"Simulating heatmap request for {filename} with color {color_string}")
    # This would typically make a request to your heatmap microservice
    # and return the image data. For now, returning dummy data.
    return b"dummy_image_data"


# algorithm microservice
# IMPORTANT CHANGE: Added algorithm_type parameter
def get_ranking_from_microservice(table, algorithm_type='default'):
    try:
        response = requests.post(
            'http://localhost:5050/rank',
            # IMPORTANT CHANGE: Pass the algorithm_type in the JSON body
            json={'table': table, 'algorithm': algorithm_type}
        )

        print(f"Ranking microservice responded with status: {response.status_code}")
        print(f"Ranking microservice response body: {response.text}")

        if response.status_code != 200:
            # Attempt to parse error message from microservice response
            error_data = response.json()
            return None, error_data.get('error', f'Unknown error from ranking microservice (Status: {response.status_code})')
        return response.json()['ranking'], None
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the ranking microservice. Is it running on port 5050?"
    except requests.exceptions.Timeout:
        return None, "Ranking microservice request timed out."
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred during request to ranking microservice: {str(e)}"
    except Exception as e:
        return None, str(e)

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
        print(f"Saved file to {filepath}")
        upload_csv(filepath)
    except Exception as e:
        print(f"upload_csv() failed: {e}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

    return jsonify({"message": "CSV uploaded successfully", "filename": filename}), 200

@app.route('/heatmap', methods=['POST'])
def heatmap():
    data = request.json
    filename = data.get('filename')
    color_string = data.get('color', '')

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

# Serve static files from the 'static' folder
@app.route('/static/<path:filename>')
def serve_static(filename):
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_file(os.path.join(static_folder, filename))


@app.route('/rank', methods=['POST', 'OPTIONS'])
def rank_endpoint_for_frontend():
    # Handle the CORS preflight OPTIONS request
    if request.method == 'OPTIONS':
        print("Received OPTIONS preflight request for /rank from frontend.")
        return '', 200 # Return 200 OK for preflight

    # Handle the actual POST request
    if request.method == 'POST':
        print("Received POST request for /rank from frontend.")
        try:
            data = request.get_json()
            table = data.get('table')
            # IMPORTANT CHANGE: Retrieve algorithm_type from frontend request
            algorithm_type = data.get('algorithm', 'default') # Default if not provided

            if not table:
                print("Error: 'table' data is missing in the request from frontend.")
                return jsonify({'error': 'Missing "table" data'}), 400

            # Call the internal function to get ranking from the microservice
            # IMPORTANT CHANGE: Pass the retrieved algorithm_type
            ranks, error = get_ranking_from_microservice(table, algorithm_type)

            if error:
                print(f"Error from ranking microservice call: {error}")
                return jsonify({'error': error}), 500

            print(f"Successfully received ranks from microservice: {ranks}")
            return jsonify({'ranking': ranks})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Internal server error processing rank request: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000)