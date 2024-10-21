from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Initialize Database and drop the table on restart
def init_db():
    conn = sqlite3.connect('elo.db')
    c = conn.cursor()
    # Drop the previous players table if it exists
    c.execute('DROP TABLE IF EXISTS players')

    # Create Absents Table
    c.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER DEFAULT 1000
        )
    ''')
    conn.commit()
    conn.close()

# Add a Absent
def add_player(name):
    conn = sqlite3.connect('elo.db')
    c = conn.cursor()
    c.execute('INSERT INTO players (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

# Elo Calculation with rounding to 6 decimal places
def calculate_elo(winner_rating, loser_rating, k=32, tie=False):
    if tie:
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))

        new_winner_rating = winner_rating + k * (0.5 - expected_winner)
        new_loser_rating = loser_rating + k * (0.5 - expected_loser)
    else:
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))

        new_winner_rating = winner_rating + k * (1 - expected_winner)
        new_loser_rating = loser_rating + k * (0 - expected_loser)

    # Round the ratings to 6 decimal places
    new_winner_rating = round(new_winner_rating, 6)
    new_loser_rating = round(new_loser_rating, 6)

    return new_winner_rating, new_loser_rating

# Get all players and their ratings, sorted by rating
def get_all_players():
    conn = sqlite3.connect('elo.db')
    c = conn.cursor()
    # Fetch players sorted by rating in descending order
    c.execute('SELECT id, name, rating FROM players ORDER BY rating DESC')
    players = c.fetchall()
    conn.close()
    return players

# Home Route
@app.route('/')
def home():
    return "Elo Rating System"

# Get Absent Rating by ID
@app.route('/player/<int:id>', methods=['GET'])
def get_player_rating(id):
    conn = sqlite3.connect('elo.db')
    c = conn.cursor()
    c.execute('SELECT name, rating FROM players WHERE id=?', (id,))
    player = c.fetchone()
    conn.close()

    if player:
        return jsonify({"name": player[0], "rating": player[1]})
    else:
        return jsonify({"error": "Absent not found"}), 404

# Add a New Absent
@app.route('/player', methods=['POST'])
def add_new_player():
    data = request.get_json()
    name = data.get('name')

    add_player(name)
    return jsonify({"message": f"Absent {name} added."}), 201

# Record Match and Update Elo Ratings
@app.route('/match', methods=['POST'])
def record_match():
    data = request.get_json()
    winner_id = data.get('winner_id')
    loser_id = data.get('loser_id')

    # Check for a tie condition
    if winner_id == loser_id:
        conn = sqlite3.connect('elo.db')
        c = conn.cursor()

        # Get current ratings for the tied player
        c.execute('SELECT rating FROM players WHERE id=?', (winner_id,))
        result = c.fetchone()

        if result is None:
            return jsonify({"error": "Winner ID does not exist."}), 404

        current_rating = result[0]

        # Update both players' ratings based on a tie
        new_rating, _ = calculate_elo(current_rating, current_rating, tie=True)

        # Update the player's rating (same player for a tie)
        c.execute('UPDATE players SET rating=? WHERE id=?', (new_rating, winner_id))

        conn.commit()
        conn.close()

        return jsonify({"message": "Match ended in a tie. Ratings updated."})

    conn = sqlite3.connect('elo.db')
    c = conn.cursor()

    # Get current ratings for the winner
    c.execute('SELECT rating FROM players WHERE id=?', (winner_id,))
    winner_result = c.fetchone()

    if winner_result is None:
        return jsonify({"error": "Winner ID does not exist."}), 404

    winner_rating = winner_result[0]

    # Get current ratings for the loser
    c.execute('SELECT rating FROM players WHERE id=?', (loser_id,))
    loser_result = c.fetchone()

    if loser_result is None:
        return jsonify({"error": "Loser ID does not exist."}), 404

    loser_rating = loser_result[0]

    # Calculate new Elo ratings
    new_winner_rating, new_loser_rating = calculate_elo(winner_rating, loser_rating)

    # Update database with new ratings
    c.execute('UPDATE players SET rating=? WHERE id=?', (new_winner_rating, winner_id))
    c.execute('UPDATE players SET rating=? WHERE id=?', (new_loser_rating, loser_id))

    conn.commit()
    conn.close()

    return jsonify({
        "winner_new_rating": new_winner_rating,
        "loser_new_rating": new_loser_rating
    })

# Scoreboard Route to Display All Absent Ratings
@app.route('/scoreboard')
def scoreboard():
    players = get_all_players()  # Fetch all players from the database, sorted by rating
    return render_template('scoreboard.html', players=players)

# Initialize the database when starting the app
if __name__ == '__main__':
    init_db()  # This will drop the previous table and create a new one
    app.run(host='0.0.0.0', port=5000, debug=True)
