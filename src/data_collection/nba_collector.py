from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import os

class NBACollector:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_historical_games(self, seasons):
        for season in seasons:
            games = leaguegamefinder.LeagueGameFinder(season_nullable=season).get_data_frames()[0]
            file_path = f"{self.data_dir}/games_{season}.csv"
            games.to_csv(file_path, index=False)
            print(f"Saved games for {season} to {file_path}")

if __name__ == "__main__":
    collector = NBACollector("data/raw/nba")
    collector.fetch_historical_games(["2022-23", "2023-24"])