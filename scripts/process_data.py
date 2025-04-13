# scripts/process_data.py
from src.data_processing.nba_processor import NBAProcessor

if __name__ == "__main__":
    processor = NBAProcessor("data/raw/nba", "data/processed/nba")
    processor.process_games("2022-23")
    processor.process_games("2023-24")