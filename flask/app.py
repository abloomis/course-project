from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import requests
import tempfile

# Import the functions from your client_socket.py
# Ensure client_socket.py is in the same directory as app.py
from client_socket import upload_csv, request_heatmap

app = Flask(__name__)

# --- CORS Configuration ---
# This allows your React frontend (on port 5173) to communicate with this Flask backend (on port 5000).
# In development, it's often easiest to allow all origins for all routes.
# For production, you would restrict 'origins' to your frontend's actual domain.
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# --- End CORS Configuration ---

# Directory for temporary file uploads (e.g., for heatmap CSV before sending to remote)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --- Microservice Communication Functions ---

# Algorithm microservice communication (assuming it's on localhost:5050)
def get_ranking_from_microservice(table, algorithm_type='default'):
    try:
        response = requests.post(
            'http://localhost:5050/rank',
            json={'table': table, 'algorithm': algorithm_type}
        )
        if response.status_code != 200:
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


# Export microservice communication (assuming it's on localhost:5051)
def get_exported_ranking_data(table, ranking_scores, player_names):
    try:
        response = requests.post(
            'http://localhost:5051/export_ranking_data',
            json={
                'table': table,
                'ranking': ranking_scores,
                'playerNames': player_names
            }
        )
        if response.status_code != 200:
            error_data = response.json()
            return None, error_data.get('error', f'Unknown error from export microservice (Status: {response.status_code})')
        
        return response.content, None
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the export microservice. Is it running on port 5051?"
    except requests.exceptions.Timeout:
        return None, "Export microservice request timed out."
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred during request to export microservice: {str(e)}"
    except Exception as e:
        return None, str(e)

# Validation microservice communication (assuming it's on localhost:5052)
def validate_data_with_microservice(headers, rows):
    try:
        response = requests.post(
            'http://localhost:5052/validate_data',
            json={
                'headers': headers,
                'rows': rows
            }
        )
        if response.status_code != 200:
            error_data = response.json()
            return None, error_data.get('error', f'Unknown error from validation microservice (Status: {response.status_code})')
        
        return response.json()['errors'], None
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the validation microservice. Is it running on port 5052?"
    except requests.exceptions.Timeout:
        return None, "Validation microservice request timed out."
    except requests.exceptions.RequestException as e:
        return None, f"An error occurred during request to validation microservice: {str(e)}"
    except Exception as e:
        return None, str(e)


# --- Flask Routes (Endpoints for Frontend) ---

@app.route('/upload_heatmap_csv', methods=['POST'])
def upload_heatmap_csv_endpoint():
    """
    Receives a CSV file from the frontend, saves it locally, and sends it
    to the remote heatmap upload server via client_socket.py.
    """
    if 'file' not in request.files:
        return jsonify({"error":"No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error":"No selected file"}), 400

    temp_dir = None
    local_filepath = None
    try:
        # Use tempfile to securely create a temporary file and directory
        temp_dir = tempfile.mkdtemp()
        # Secure filename to prevent directory traversal attacks
        local_filepath = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(local_filepath)
        print(f"Saved local temp file for heatmap upload: {local_filepath}")

        # Use the imported upload_csv function from client_socket.py
        upload_csv(local_filepath)
        
        # Return the basename of the file so the frontend can use it for the heatmap request
        return jsonify({"message": "CSV uploaded to heatmap server successfully", "filename": os.path.basename(local_filepath)}), 200
    except ConnectionError as e: # Catch custom ConnectionError from client_socket.py
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to connect to or upload CSV to remote heatmap server: {str(e)}"}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during CSV upload for heatmap: {str(e)}"}), 500
    finally:
        # Clean up the temporary file and directory
        if local_filepath and os.path.exists(local_filepath):
            os.remove(local_filepath)
        if temp_dir and os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@app.route('/request_heatmap_image', methods=['POST'])
def request_heatmap_image_endpoint():
    """
    Requests a heatmap image from the remote heatmap generator server
    via client_socket.py, using the filename previously uploaded.
    """
    data = request.json
    filename = data.get('filename') # This is the original filename (basename)
    color_string = data.get('color', '')

    if not filename:
        return jsonify({"error": "Missing filename for heatmap request"}), 400

    try:
        # Use the imported request_heatmap function from client_socket.py
        image_data = request_heatmap(filename, color_string)
        
        # Flask's send_file can be used, but for raw bytes, creating a response directly is fine
        response = app.make_response(image_data)
        response.headers["Content-Type"] = "image/png"
        return response

    except ConnectionError as e: # Catch custom ConnectionError from client_socket.py
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to connect to or retrieve heatmap from remote server: {str(e)}"}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred during heatmap generation: {str(e)}"}), 500


@app.route('/rank', methods=['POST'])
def rank_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    table = data.get('table')
    algorithm = data.get('algorithm', 'default')

    if not table:
        return jsonify({"error": "Missing 'table' data for ranking"}), 400

    ranking, error = get_ranking_from_microservice(table, algorithm)

    if error:
        return jsonify({"error": error}), 500
    return jsonify({"ranking": ranking}), 200


@app.route('/export_ranking', methods=['POST'])
def export_ranking_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    table = data.get('table')
    ranking = data.get('ranking')
    player_names = data.get('playerNames')

    if not all([table, ranking, player_names]):
        return jsonify({"error": "Missing table, ranking, or playerNames data for export"}), 400

    exported_data, error = get_exported_ranking_data(table, ranking, player_names)

    if error:
        return jsonify({"error": error}), 500
    
    # Assuming exported_data is bytes (e.g., CSV content)
    response = app.make_response(exported_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=league_ranking_data.csv"
    return response


@app.route('/validate', methods=['POST'])
def validate_data_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    headers = data.get('headers')
    rows = data.get('rows')

    if not all([headers, rows is not None]): # rows can be empty, but not None
        return jsonify({"error": "Missing headers or rows data for validation"}), 400
    
    errors, error_message = validate_data_with_microservice(headers, rows)

    if error_message:
        return jsonify({"error": error_message}), 500
    
    return jsonify({"errors": errors}), 200 # Return the list of errors


if __name__ == '__main__':
    # Flask app runs on port 5000, listening for requests from your React frontend
    app.run(port=5000, debug=True) # debug=True provides more detailed error messages