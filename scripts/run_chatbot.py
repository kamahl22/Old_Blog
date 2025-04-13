# scripts/run_chatbot.py
from src.chatbot.discord_bot import bot
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("DISCORD_TOKEN"))