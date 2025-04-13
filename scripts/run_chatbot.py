# scripts/run_chatbot.py
from src.chatbot.discord_bot import bot
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise ValueError("DISCORD_TOKEN not found in .env")
    bot.run(token)