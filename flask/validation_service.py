from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# --- CORS Configuration for Validation Microservice ---
# This allows your main Flask app (on port 5000) to communicate with this service (on port 5052).
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# --- End CORS Configuration ---

def validate_head_to_head_data(headers, rows):
    errors = []

    # Basic structural checks
    if not headers or len(headers) < 2:
        errors.append("Headers are missing or insufficient. At least two players are required.")
        # If headers are missing or malformed, further checks might lead to IndexErrors
        return errors # Exit early

    if not rows:
        errors.append("No data rows found. The table is empty.")
        return errors # Exit early

    player_names_in_rows = [row.get('name') for row in rows]
    
    # Check if all player names in rows are unique
    if len(set(player_names_in_rows)) != len(player_names_in_rows):
        errors.append("All player names in the first column must be unique.")

    # Check if all headers correspond to valid player names (and vice-versa, implicitly)
    for header in headers:
        if header not in player_names_in_rows:
            errors.append(f"Header '{header}' does not correspond to a player name in the first column.")

    # Main data validation loop
    for i, row in enumerate(rows):
        current_player_name = row.get('name')
        if not current_player_name:
            errors.append(f"Row {i+1} has no player name (first column).")
            continue # Cannot proceed with this row's validation without a name

        if 'data' not in row or not isinstance(row['data'], list):
            errors.append(f"Row for '{current_player_name}' is malformed: missing or invalid 'data' list.")
            continue

        if len(row['data']) != len(headers):
            errors.append(f"Row for '{current_player_name}' has {len(row['data'])} data points, but expected {len(headers)} based on headers.")
            continue # Skip further detailed cell checks for this row if lengths don't match

        for j, cell_value in enumerate(row['data']):
            opponent_name = headers[j]
            
            # --- Self-play cell check (diagonal) ---
            if current_player_name == opponent_name:
                # Self-play cells are typically 'X', '-', or 0.
                # Allow non-numeric for self-play, but if numeric, enforce 0.
                try:
                    num_val = float(cell_value)
                    if num_val != 0:
                        errors.append(f"Cell ({current_player_name} vs {opponent_name}): Self-play cell should be 0 or a non-numeric indicator (e.g., 'X', '-'), but found '{cell_value}'.")
                except ValueError:
                    # It's a non-numeric string, which is acceptable for self-play
                    pass
            # --- Non-self-play cell check ---
            else:
                # Find the opponent's row for reciprocal check
                opponent_row = None
                for p_row in rows:
                    if p_row.get('name') == opponent_name:
                        opponent_row = p_row
                        break
                
                if opponent_row is None:
                    # This case should be caught by the header/player name mismatch check earlier,
                    # but it's a safe guard for structural issues.
                    errors.append(f"Internal error: Could not find row for opponent '{opponent_name}' when checking '{current_player_name}' vs '{opponent_name}'.")
                    continue

                # Find the current player's column in the opponent's row
                current_player_col_index = -1
                try:
                    current_player_col_index = headers.index(current_player_name)
                except ValueError:
                    errors.append(f"Internal error: Could not find column for current player '{current_player_name}' in headers.")
                    continue

                if current_player_col_index >= len(opponent_row['data']):
                    errors.append(f"Internal error: Reciprocal data index out of bounds for '{opponent_name}' vs '{current_player_name}'.")
                    continue

                reciprocal_value = opponent_row['data'][current_player_col_index]

                # Validate the 'X -- Y' format for both current and reciprocal values
                try:
                    # Parse current cell value (e.g., '2 -- 3')
                    parts_current = [p.strip() for p in str(cell_value).split('--')]
                    if len(parts_current) != 2:
                        raise ValueError("Invalid format: not 'X -- Y'")

                    # Parse reciprocal cell value (e.g., '3 -- 2')
                    parts_reciprocal = [p.strip() for p in str(reciprocal_value).split('--')]
                    if len(parts_reciprocal) != 2:
                        raise ValueError("Invalid format: reciprocal not 'X -- Y'")

                    # Ensure both parts are integers (e.g., '2' and '3')
                    # This will catch cases like 'hello -- world'
                    try:
                        int(parts_current[0])
                        int(parts_current[1])
                        int(parts_reciprocal[0])
                        int(parts_reciprocal[1])
                    except ValueError:
                        raise ValueError("Non-numeric parts in 'X -- Y' format")

                    # Symmetry check: If current is 'X -- Y', reciprocal must be 'Y -- X'
                    if not (parts_current[0] == parts_reciprocal[1] and parts_current[1] == parts_reciprocal[0]):
                        errors.append(f"Cell ({current_player_name} vs {opponent_name}): Reciprocal score mismatch. Expected '{parts_current[1]} -- {parts_current[0]}', but found '{reciprocal_value}'.")

                except ValueError as e:
                    # Catch all parsing and format errors
                    errors.append(f"Cell ({current_player_name} vs {opponent_name}): Invalid score format '{cell_value}'. Expected 'X -- Y' with numeric X and Y. Details: {e}")

    # Return unique errors only
    return list(set(errors))


@app.route('/validate_data', methods=['POST'])
def validate_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    headers = data.get('headers')
    rows = data.get('rows')

    # Ensure headers and rows are lists, even if empty
    if not isinstance(headers, list) or not isinstance(rows, list):
        return jsonify({"error": "Headers and rows must be lists"}), 400

    validation_errors = validate_head_to_head_data(headers, rows)
    
    return jsonify({"errors": validation_errors}), 200

if __name__ == '__main__':
    # The validation microservice runs on port 5052
    app.run(port=5052, debug=True)