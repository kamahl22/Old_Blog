# src/prediction_engine/engine.py
from src.models.nba_models.game_outcome import GameOutcomeModel
import pandas as pd

class PredictionEngine:
    def __init__(self, model_path="models/nba/game_outcome.pkl"):
        self.model = GameOutcomeModel(model_path)

    def predict_game(self, team1, team2):
        stats = pd.read_csv("data/processed/nba/team_stats_2022-23.csv")
        try:
            team1_pct = stats[stats["TEAM_NAME"] == team1]["win_pct"].values[0]
            features = pd.DataFrame({"win_pct": [team1_pct]})
            confidence = self.model.predict(features)
            winner = team1 if confidence > 0.5 else team2
            return {"winner": winner, "confidence": round(confidence, 2)}  # Round to 2 decimals
        except IndexError:
            return {"error": "Team not found"}

if __name__ == "__main__":
    engine = PredictionEngine()
    result = engine.predict_game("Phoenix Suns", "Los Angeles Lakers")
    print(result)