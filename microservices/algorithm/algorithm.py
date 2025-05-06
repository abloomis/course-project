# used to parse a 2D table of h2h records formatted as "X -- Y"
def parse(table):

    # parse the matrix into a list of tuples (wins, losses)
    parsed = []
    for row in table:
        parsed_row = []
        for cell in row:
            try:
                x, y = cell.strip().split('--')
                parsed_row.append((int(x.strip()), int(y.strip())))

            # Default for invalid/missing cells
            except Exception:
                parsed_row.append((0, 0))

        parsed.append(parsed_row)
    return parsed

# create an initial ranking based purely on win-rate
def init_ranking(table):
    
    win_rates = []
    for i, row in enumerate(table):
        # count wins in all cells of the row, excluding the cell along the main diagonal
        # (players do not play against themselves)
        wins = sum(cell[0] for j, cell in enumerate(row) if i != j)
        total = wins + sum(cell[1] for j, cell in enumerate(row) if i != j)
        win_rate = wins / total if total > 0 else 0.0
        win_rates.append(win_rate)
    return win_rates

# normalizes a list of floats to the range [0, 1]
def normalize(ranks):
    
    min_rank = min(ranks)
    max_rank = max(ranks)
    if max_rank == min_rank:
        return [0.5 for _ in ranks]
    return [(r - min_rank) / (max_rank - min_rank) for r in ranks]

# updates the ranking list by weighting wins according to opponent ranks
def update(table, prev_ranks, scaling_factor=1.0):
    
    new_ranks = []
    for i, row in enumerate(parsed_matrix):
        weighted_wins = 0
        weight_total = 0
        for j, (wins, losses) in enumerate(row):
            if i == j:
                continue
            weight = prev_ranks[j] ** scaling_factor
            weighted_wins += wins * weight
            weight_total += (wins + losses) * weight
        new_ranks.append(weighted_wins / weight_total if weight_total > 0 else 0.0)
    return normalize_ranks(new_ranks)

# main loop: updates the ranking iteratively until it stabilizes
# ------------------------------- NOTE -------------------------------
# - max_iters, scaling_factor, and tolerance should all be adjusted
# - to meet the ranker's needs
# -
# - max_iters controls how many iterations can run at most
# - scaling_factor controls how wins on player rank 1 are weighed
# -     relative to rank 2, etc
# - tolerance controls how close two rankings must be to be
# -     considered equal, thus ending the service before max_iters
# -     are ran
# --------------------------------------------------------------------
def rank(table, max_iters = 100, scaling_factor = 1.0, tolerance = 0.001):
    
    parsed = parse(table)
    prev_ranks = normalize(init_ranking(parsed))

    # loop until max_iters is reached
    for _ in range(max_iters):
        new_ranks = update(parsed, prev_ranks, scaling_factor)
        # check how much the ranking scores updated between the previous
        # iterations, breaking the for loop for insufficient change
        if all(abs(a - b) < tolerance for a, b in zip(prev_ranks, new_ranks)):
            break
        prev_ranks = new_ranks
    return new_ranks