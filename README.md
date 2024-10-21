# elo-rating-scoreboard
Elo Rating Scoreboard for college hackathon

## Requirements
- flask

## How to run:
1. Start the flask server with `python3 app.py`
2. Run `players_create.sh` to create players with a base rating of 1000
3. Run `players_activity_populate.sh` to give them some activity

## Possible activities with curl
```
curl -X POST -H "Content-Type: application/json" -d '{"winner_id": 1, "loser_id": 2}' http://localhost:5000/match
curl -X POST -H "Content-Type: application/json" -d '{"winner_id": 2, "loser_id": 1}' http://localhost:5000/match
curl -X POST -H "Content-Type: application/json" -d '{"winner_id": 1, "loser_id": 1}' http://localhost:5000/match
curl -X POST -H "Content-Type: application/json" -d '{"winner_id": 2, "loser_id": 2}' http://localhost:5000/match
```
