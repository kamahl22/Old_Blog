import discord
from discord.ext import commands
from src.prediction_engine.engine import PredictionEngine
from src.blockchain.betting_pool import BettingPool
from src.blockchain.wallet import AlgorandWallet
from src.utils.db import Database
from algosdk.v2client import algod
from dotenv import load_dotenv
import os

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
bot_wallet = AlgorandWallet(os.getenv("BOT_MNEMONIC"))
db = Database("data/blog.db")
pool_manager = BettingPool(client, bot_wallet)

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

@bot.command()
async def top_bets(ctx):
    engine = PredictionEngine()
    games = [("Phoenix Suns", "Lakers"), ("Celtics", "Nets"), ("Warriors", "Clippers"), ("Bulls", "Heat")]
    top_bets = engine.get_top_bets(games)
    response = "Bot's Top 3 Bets:\n"
    for i, bet in enumerate(top_bets, 1):
        response += f"{i}. {bet['team1']} vs {bet['team2']}: {bet['winner']} ({bet['confidence']*100:.1f}%, odds {bet['odds']})\n"
    await ctx.send(response)

@bot.command()
async def bot_bet(ctx, team: str, odds: str, stake: int):
    try:
        pool_id, txid = pool_manager.open_pool("bot", f"game_{ctx.message.id}", team, odds, stake)
        await ctx.send(f"Bot bet {stake} microALGOs on {team} at {odds}. Pool {pool_id} opened: {txid}")
    except ValueError as e:
        await ctx.send(str(e))

@bot.command()
async def community_pool(ctx, team: str, odds: str, stake: int):
    try:
        pool_id, txid = pool_manager.open_pool("community", f"game_{ctx.message.id}", team, odds, stake, str(ctx.author.id))
        await ctx.send(f"Community pool by {ctx.author.name} for {team} at {odds} ({stake} microALGOs): {pool_id}, TxID: {txid}")
    except ValueError as e:
        await ctx.send(str(e))

@bot.command()
async def group_pool(ctx, group_name: str, team: str, odds: str, stake: int):
    group = db.conn.execute("SELECT verified FROM groups WHERE name = ?", (group_name,)).fetchone()
    if not group or not group[0]:
        await ctx.send(f"{group_name} is not a verified group!")
        return
    try:
        pool_id, txid = pool_manager.open_pool("group", f"game_{ctx.message.id}", team, odds, stake, group_id=group_name)
        await ctx.send(f"{group_name} pool for {team} at {odds} ({stake} microALGOs): {pool_id}, TxID: {txid}")
    except ValueError as e:
        await ctx.send(str(e))

@bot.command()
async def back_bet(ctx, pool_id: str, amount: int):
    try:
        result = pool_manager.contribute(pool_id, f"USER_{ctx.author.id}", amount)
        await ctx.send(result)
    except ValueError as e:
        await ctx.send(str(e))

@bot.command()
async def top_bettors(ctx):
    bettors = db.get_top_bettors()
    response = "Top 5 Bettors (Weekly ROI):\n" + "\n".join(f"{i+1}. <@{uid}>" for i, uid in enumerate([uid for uid, _ in bettors]))
    await ctx.send(response)

@bot.command()
async def community_bettors(ctx):
    bettors = pool_manager.db.select_community_bettors()
    response = "Today's Community Bettors:\n" + "\n".join(f"- <@{uid}>" for uid in bettors)
    await ctx.send(response)

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN not found in .env")
bot.run(token)