# src/data_processing/nba_processor.py
import pandas as pd
import os

class NBAProcessor:
    def __init__(self, raw_dir, processed_dir):
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(processed_dir, exist_ok=True)

    def process_games(self, season):
        df = pd.read_csv(f"{self.raw_dir}/games_{season}.csv")
        # Basic feature: team win percentage
        team_stats = df.groupby("TEAM_NAME").agg({"WL": lambda x: (x == "W").mean()}).rename(columns={"WL": "win_pct"})
        team_stats.to_csv(f"{self.processed_dir}/team_stats_{season}.csv")
        print(f"Processed team stats for {season}")

if __name__ == "__main__":
    processor = NBAProcessor("data/raw/nba", "data/processed/nba")
    processor.process_games("2022-23")
    processor.process_games("2023-24")