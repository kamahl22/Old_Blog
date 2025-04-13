# src/models/nba_models/game_outcome.py
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pandas as pd
import pickle
import os

class GameOutcomeModel:
    def __init__(self, model_path):
        self.model_path = model_path
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

    def train(self, data_path):
        df = pd.read_csv(data_path)
        raw_df = pd.read_csv("data/raw/nba/games_2022-23.csv")
        df = raw_df.merge(df, on="TEAM_NAME")
        X = df[["win_pct"]]
        y = (df["WL"] == "W").astype(int)
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        model = XGBClassifier()
        model.fit(X_train, y_train)
        with open(self.model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"Model saved to {self.model_path}")

    def predict(self, features):
        with open(self.model_path, "rb") as f:
            model = pickle.load(f)
        confidence = model.predict_proba(features)[0][1]
        return float(confidence)  # Convert np.float32 to Python float

if __name__ == "__main__":
    model = GameOutcomeModel("models/nba/game_outcome.pkl")
    model.train("data/processed/nba/team_stats_2022-23.csv")