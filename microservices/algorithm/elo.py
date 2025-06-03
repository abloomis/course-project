import math

# Initial Elo rating for new players
INITIAL_ELO = 1500
# K-factor: determines the maximum possible adjustment per game.
# A higher K-factor means ratings change more drastically.
K_FACTOR = 32

def calculate_expected_score(player_elo, opponent_elo):
    """
    Calculates the expected score (probability of winning) for player_elo
    against opponent_elo.
    The Elo rating system uses a logistic curve for this.
    """
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))

def update_elo(player_elo, opponent_elo, player_score):
    """
    Updates the Elo ratings for two players after a single match.

    Args:
        player_elo (float): The current Elo rating of the player.
        opponent_elo (float): The current Elo rating of the opponent.
        player_score (float): The actual score of the player in the match (1 for win, 0 for loss).

    Returns:
        tuple: A tuple containing the new Elo ratings for the player and opponent.
    """
    expected_score = calculate_expected_score(player_elo, opponent_elo)

    # Calculate the Elo change for the player
    elo_change = K_FACTOR * (player_score - expected_score)

    new_player_elo = player_elo + elo_change
    new_opponent_elo = opponent_elo - elo_change # Opponent's rating changes by the inverse amount

    return new_player_elo, new_opponent_elo

def initialize_elos(num_players):
    """
    Initializes Elo ratings for all players to the INITIAL_ELO.
    """
    return [float(INITIAL_ELO)] * num_players # Ensure floats from the start

def rank_elo(table, max_iters=100, tolerance=0.001):
    """
    Main function to compute Elo rankings iteratively based on head-to-head data.

    The 'table' is expected to be a 2D list where each cell (i, j) contains
    (wins_i_vs_j, losses_i_vs_j).

    Args:
        table (list of list of tuple): A 2D table representing head-to-head records.
                                      Each cell (i, j) is a tuple (wins, losses)
                                      for player i against player j.
        max_iters (int): Maximum number of iterations for the ranking process.
        tolerance (float): The convergence tolerance. If the change in all
                           player ratings is less than this, the iteration stops.

    Returns:
        list: A normalized list of Elo ratings for each player.
    """
    num_players = len(table)
    if num_players == 0:
        return []

    # Initialize all players with the initial Elo rating
    current_elos = initialize_elos(num_players)

    for iteration in range(max_iters):
        # We need to perform all updates based on the ratings at the START of the iteration
        # to prevent update order bias. Then apply all changes at once.
        temp_elos = list(current_elos) # Store new ratings here

        for i in range(num_players):
            for j in range(num_players):
                if i == j:
                    continue

                wins, losses = table[i][j]

                # Process each win and loss as a separate "match" for Elo update
                for _ in range(wins):
                    # Player i won against player j
                    new_elo_i, new_elo_j = update_elo(temp_elos[i], temp_elos[j], 1)
                    # Accumulate changes
                    temp_elos[i] = new_elo_i
                    temp_elos[j] = new_elo_j

                for _ in range(losses):
                    # Player i lost against player j
                    new_elo_i, new_elo_j = update_elo(temp_elos[i], temp_elos[j], 0)
                    # Accumulate changes
                    temp_elos[i] = new_elo_i
                    temp_elos[j] = new_elo_j
        
        # Check for convergence
        converged = True
        for i in range(num_players):
            if abs(current_elos[i] - temp_elos[i]) > tolerance:
                converged = False
                break
        
        current_elos = temp_elos # Apply all changes for the next iteration

        if converged:
            break

    # Normalize the final Elo ratings to a [0, 1] range
    min_elo = min(current_elos)
    max_elo = max(current_elos)

    if max_elo == min_elo:
        return [0.5 for _ in current_elos]

    normalized_elos = [(elo - min_elo) / (max_elo - min_elo) for elo in current_elos]

    return normalized_elos

# Helper function to parse the table, similar to your existing algorithm.py
def parse_elo_table(table):
    """
    Parses a 2D table of h2h records formatted as "X -- Y" into
    (wins, losses) tuples. Handles non-standard entries by returning (0,0).
    """
    parsed = []
    for row in table:
        parsed_row = []
        for cell in row:
            try:
                x, y = map(int, cell.strip().split('--'))
                parsed_row.append((x, y))
            except Exception:
                # If a cell is malformed or empty, treat it as 0 wins and 0 losses
                # This prevents errors but might need more sophisticated handling
                # depending on your specific data input expectations.
                parsed_row.append((0, 0))
        parsed.append(parsed_row)
    return parsed


# Main function to be called from the ranking service
def rank(table, max_iters=100, tolerance=0.001):
    """
    Parses the input table and computes Elo rankings.
    """
    parsed_table = parse_elo_table(table)
    return rank_elo(parsed_table, max_iters, tolerance)

if __name__ == '__main__':
    # Example Usage:
    # Let's say we have 3 players: Player A, Player B, Player C
    # The table represents:
    #                     A vs A, A vs B, A vs C
    #                     B vs A, B vs B, B vs C
    #                     C vs A, C vs B, C vs C

    # Format: "Wins_against_j -- Losses_against_j"
    # Example: A beat B 2 times, lost 1 time (A vs B is "2 -- 1")
    #          B beat A 1 time, lost 2 times (B vs A is "1 -- 2")
    print("--- Elo Ranking Test ---")
    sample_table = [
        ["0 -- 0", "2 -- 1", "3 -- 0"],  # A vs A, A vs B, A vs C
        ["1 -- 2", "0 -- 0", "1 -- 1"],  # B vs A, B vs B, B vs C
        ["0 -- 3", "1 -- 1", "0 -- 0"]   # C vs A, C vs B, C vs C
    ]

    print("Sample Table:")
    for r in sample_table:
        print(r)

    print("\nComputing Elo ranks for the sample table:")
    elo_rankings = rank(sample_table)
    print("Normalized Elo Rankings:", [f"{r:.3f}" for r in elo_rankings])
    # Expected: Player A should be highest, C lowest, B in middle

    print("\n--- Another Example: More Even Match-ups ---")
    sample_table_2 = [
        ["0 -- 0", "5 -- 5", "6 -- 4"],
        ["5 -- 5", "0 -- 0", "4 -- 6"],
        ["4 -- 6", "6 -- 4", "0 -- 0"]
    ]
    print("Sample Table 2:")
    for r in sample_table_2:
        print(r)

    print("\nComputing Elo ranks for sample table 2 (more even):")
    elo_rankings_2 = rank(sample_table_2)
    print("Normalized Elo Rankings:", [f"{r:.3f}" for r in elo_rankings_2])
    # Expected: Ratings should be closer, A might be slightly higher than B, C might be lowest or similar to B

    print("\n--- Edge Case: All zeros ---")
    sample_table_3 = [
        ["0 -- 0", "0 -- 0", "0 -- 0"],
        ["0 -- 0", "0 -- 0", "0 -- 0"],
        ["0 -- 0", "0 -- 0", "0 -- 0"]
    ]
    print("Sample Table 3 (all zeros):")
    for r in sample_table_3:
        print(r)
    print("\nComputing Elo ranks for sample table 3:")
    elo_rankings_3 = rank(sample_table_3)
    print("Normalized Elo Rankings:", [f"{r:.3f}" for r in elo_rankings_3])
    # Expected: All players should have a normalized rank of 0.5