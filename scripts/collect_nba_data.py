from src.data_collection.nba_collector import NBACollector

if __name__ == "__main__":
    collector = NBACollector("data/raw/nba")
    collector.fetch_historical_games(["2022-23", "2023-24"])