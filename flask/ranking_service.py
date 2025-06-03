import sys
import os
from flask_cors import CORS
from flask import Flask, request, jsonify

current_dir = os.path.dirname(os.path.abspath(__file__))

microservices_path = os.path.abspath(os.path.join(current_dir, '..', 'microservices'))
sys.path.append(microservices_path)

from algorithm.algorithm import rank as compute_rank_default
from algorithm.elo import rank as compute_rank_elo

app = Flask(__name__)
CORS(app) # Enable CORS for this service, though app.py (server-side) calls it

@app.route('/rank', methods=['POST', 'OPTIONS'])
def rank_endpoint():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return '', 200

    try:
        data = request.get_json()
        table = data.get('table')
        algorithm_type = data.get('algorithm', 'default') # Default to existing algorithm if not specified

        if not table:
            return jsonify({'error': 'Missing "table" data'}), 400

        if algorithm_type == 'elo':
            ranks = compute_rank_elo(table)
        elif algorithm_type == 'default':
            ranks = compute_rank_default(table)
        else:
            return jsonify({'error': 'Invalid algorithm type specified. Choose "default" or "elo".'}), 400

        return jsonify({'ranking': ranks})
    except Exception as e:
        # It's good practice to log the full traceback for debugging
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5050) # use 5050 for the ranking microservice
