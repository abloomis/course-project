from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import csv
import io
import math # For handling potential division by zero in win rate

app = Flask(__name__)
CORS(app) # Enable CORS for all routes by default

# Function to safely parse 'X -- Y' string
def parse_score_string(score_str):
    try:
        parts = [p.strip() for p in str(score_str).split('--')]
        if len(parts) == 2:
            return float(parts[0]), float(parts[1])
    except (ValueError, AttributeError):
        pass # Not in 'X -- Y' format or not parseable
    return None, None

@app.route('/export_ranking_data', methods=['POST'])
def export_ranking_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    table_data = data.get('table') # This is the 2D array of scores (just numbers)
    ranking_scores = data.get('ranking') # The ranking scores from the ranking service
    player_names = data.get('playerNames') # The list of player names (headers from frontend)

    if not all([table_data, ranking_scores, player_names]):
        return jsonify({"error": "Missing table, ranking, or playerNames data"}), 400

    output = io.StringIO()
    writer = csv.writer(output)

    # Define the new headers for the CSV
    headers = ["Rank", "Player Name", "Ranking Score", "Win Rate", "Matches Played"]
    writer.writerow(headers)

    # Prepare player data for calculation
    # Create a map from player name to their index in table_data/ranking_scores
    player_name_to_index = {name: i for i, name in enumerate(player_names)}

    # Calculate Win Rate and Matches Played for each player
    player_stats = {}
    for i, player_name in enumerate(player_names):
        total_wins = 0
        total_losses = 0 # Using 'losses' for the reciprocal score
        matches_played = 0

        # Iterate through the row data for the current player
        # Note: table_data contains only the scores, not the player names on the left.
        # So table_data[i] is the row for player_names[i]
        current_player_row_scores = table_data[i] 

        for j, opponent_name in enumerate(player_names):
            if player_name == opponent_name:
                continue # Skip self-play cell

            # Get the score of current_player vs opponent_name
            score_current_vs_opponent_str = current_player_row_scores[j]
            
            # Parse 'X -- Y' format
            player_score, opponent_score_against_player = parse_score_string(score_current_vs_opponent_str)
            
            if player_score is not None and opponent_score_against_player is not None:
                # If both parts are numeric and represent a valid match
                total_wins += player_score
                total_losses += opponent_score_against_player # opponent's score against current player is current player's loss
                matches_played += 1 # Count as one match

        win_rate = 0.0
        if matches_played > 0:
            # Assuming 'total_wins' represents points won, and 'total_losses' represents points lost.
            # Win rate could be total_wins / (total_wins + total_losses) if 1-0 or 0-1.
            # If 'X -- Y' means X points scored by player, Y points scored by opponent in that matchup,
            # then total_wins / (total_wins + total_losses) is a reasonable 'score rate'.
            # If it's pure win/loss, it's total_wins / matches_played.
            # Let's assume X is wins for player, Y is wins for opponent in the game.
            # So, player_score is player's wins in that match, opponent_score_against_player is opponent's wins.
            # Total matches played is simply the count of valid encounters.
            # Total wins is sum of X's where player is current_player.
            # Total losses is sum of Y's where player is current_player.
            
            # Recalculate based on total points or total wins.
            # If X is wins and Y is losses, then win rate is total_X / matches_played.
            # If X is points and Y is points, then win rate is total_X / (total_X + total_Y).
            # Given "2 -- 3" format, it's more likely points or small scores.
            # Let's use total_wins / matches_played for win rate, where a 'win' contributes 1.
            # This is tricky without strict definition. Let's make a common assumption:
            # For 'X -- Y', X is player's points/games won, Y is opponent's points/games won.
            # A 'win' means X > Y. A 'loss' means X < Y. A 'draw' means X == Y.
            
            player_total_wins = 0
            player_total_draws = 0
            player_total_losses = 0
            
            for j, opponent_name in enumerate(player_names):
                if player_name == opponent_name:
                    continue
                
                score_str = current_player_row_scores[j]
                p_score, o_score = parse_score_string(score_str)
                
                if p_score is not None and o_score is not None:
                    if p_score > o_score:
                        player_total_wins += 1
                    elif p_score < o_score:
                        player_total_losses += 1
                    else: # p_score == o_score
                        player_total_draws += 1
            
            # Recalculate matches_played based on actual games recorded
            actual_matches_played = player_total_wins + player_total_losses + player_total_draws

            if actual_matches_played > 0:
                # Common formula for win rate (wins + 0.5*draws) / total_games
                win_rate = (player_total_wins + 0.5 * player_total_draws) / actual_matches_played
            else:
                win_rate = 0.0 # No matches played

            matches_played = actual_matches_played # Update matches_played

        player_stats[player_name] = {
            'win_rate': win_rate,
            'matches_played': matches_played
        }

    # Combine ranking data with calculated stats and write to CSV
    # The ranking_scores list is already sorted by the ranking service.
    # We need to correctly map the ranking_scores to player names.
    # The `ranking` array from the ranking service is simply the scores.
    # We assumed player_names are in the same order as rows/ranking_scores.
    
    # Create a list of tuples (ranking_score, player_name_index)
    # This assumes ranking_scores returned from the microservice is a flat list
    # corresponding to the order of players in `player_names` and `table_data`.
    # It's better to sort based on the ranking score here.
    
    ranked_players_with_scores = []
    for i, score in enumerate(ranking_scores):
        ranked_players_with_scores.append({
            'name': player_names[i],
            'score': score,
            'win_rate': player_stats[player_names[i]]['win_rate'],
            'matches_played': player_stats[player_names[i]]['matches_played']
        })
    
    # Sort by ranking score (highest first)
    ranked_players_with_scores.sort(key=lambda x: x['score'], reverse=True)

    for rank, player_info in enumerate(ranked_players_with_scores):
        writer.writerow([
            rank + 1, # Rank (1-based)
            player_info['name'],
            f"{player_info['score']:.3f}", # Truncate ranking score to 3 decimal places
            f"{player_info['win_rate']:.3f}", # Truncate win rate to 3 decimal places
            player_info['matches_played']
        ])

    csv_data = output.getvalue()
    
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=league_ranking_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(port=5051, debug=True)