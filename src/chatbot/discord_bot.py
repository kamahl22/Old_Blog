# src/chatbot/discord_bot.py
import discord
from discord.ext import commands
from src.prediction_engine.engine import PredictionEngine
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def predict(ctx, team1: str, team2: str):
    engine = PredictionEngine()
    result = engine.predict_game(team1, team2)
    if "error" in result:
        await ctx.send(result["error"])
    else:
        await ctx.send(f"{team1} vs {team2}: {result['winner']} ({result['confidence']*100:.1f}%)")

# Validate token
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN not found in .env")
bot.run(token)