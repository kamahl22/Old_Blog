class PredictionEngine:
    def __init__(self):
        self.model = None  # Placeholder for XGBoost

    def predict_game(self, team1, team2):
        # Mock prediction
        return {"winner": team1, "confidence": 0.6}

    def get_top_bets(self, games, limit=3):
        predictions = []
        for game in games:
            pred = self.predict_game(game[0], game[1])
            predictions.append({
                "team1": game[0],
                "team2": game[1],
                "winner": pred["winner"],
                "confidence": pred["confidence"],
                "odds": "+100"
            })
        return sorted(predictions, key=lambda x: x["confidence"], reverse=True)[:limit]