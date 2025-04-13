# scripts/train_models.py
from src.models.nba_models.game_outcome import GameOutcomeModel

if __name__ == "__main__":
    model = GameOutcomeModel("models/nba/game_outcome.pkl")
    model.train("data/processed/nba/team_stats_2022-23.csv")