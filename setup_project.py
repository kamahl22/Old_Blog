import os
import shutil

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content.strip())

# Define project structure
dirs = [
    "src",
    "src/blockchain",
    "src/chatbot",
    "src/data_collection",
    "src/prediction_engine",
    "src/utils",
    "data",
    "scripts"
]

files = {
    "src/utils/db.py": """
from sqlite3 import connect
import random
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.conn = connect(db_path)
        self.create_tables()

    def create_tables(self):
        self.conn.execute(\"""
            CREATE TABLE IF NOT EXISTS bets (
                user_id TEXT,
                game_id TEXT,
                team TEXT,
                stake INTEGER,
                odds TEXT,
                won INTEGER,
                payout INTEGER,
                timestamp TEXT
            )
        \""")
        self.conn.execute(\"""
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT,
                name TEXT,
                verified INTEGER,
                win_rate REAL,
                roi REAL,
                bet_count INTEGER
            )
        \""")
        self.conn.execute(\"""
            CREATE TABLE IF NOT EXISTS community_picks (
                user_id TEXT,
                date TEXT,
                consecutive_days INTEGER,
                last_win INTEGER
            )
        \""")
        self.conn.commit()

    def record_bet(self, user_id, game_id, team, stake, odds, won, payout):
        self.conn.execute(
            "INSERT INTO bets VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, game_id, team, stake, odds, won, payout, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def get_user_stats(self, user_id, days=30):
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            "SELECT stake, payout, won FROM bets WHERE user_id = ? AND timestamp > ?",
            (user_id, start)
        ).fetchall()
        total_stake = sum(row[0] for row in rows)
        total_payout = sum(row[1] for row in rows)
        wins = sum(row[2] for row in rows)
        bets = len(rows)
        win_rate = wins / bets if bets > 0 else 0
        roi = (total_payout - total_stake) / total_stake if total_stake > 0 else 0
        return {"win_rate": win_rate, "roi": roi, "bets": bets}

    def get_top_bettors(self, days=7, min_bets=10):
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        rows = self.conn.execute(
            \"""
            SELECT user_id, SUM(payout) - SUM(stake) AS profit, SUM(stake) AS total, COUNT(*) AS bets
            FROM bets WHERE timestamp > ?
            GROUP BY user_id HAVING bets >= ? AND total > 0
            ORDER BY (SUM(payout) - SUM(stake)) / SUM(stake) DESC
            \""",
            (start, min_bets)
        ).fetchall()
        return [(row[0], (row[1] / row[2]) if row[2] > 0 else 0) for row in rows]

    def select_community_bettors(self, limit=5):
        today = datetime.utcnow().date().isoformat()
        picks = self.conn.execute(
            "SELECT user_id, consecutive_days, last_win FROM community_picks WHERE date = ?",
            (today,)
        ).fetchall()
        selected = []
        for user_id, days, last_win in picks:
            if days < 3 and last_win:
                selected.append(user_id)
        needed = limit - len(selected)
        if needed <= 0:
            return selected
        bettors = self.get_top_bettors(days=30, min_bets=10)
        eligible = [(uid, roi) for uid, roi in bettors if uid not in selected and self.get_user_stats(uid)["win_rate"] >= 0.5]
        if not eligible:
            return selected
        weights = []
        for i, (uid, roi) in enumerate(eligible):
            if i < 3:
                weights.append(0.4)
            elif i < 10:
                weights.append(0.2)
            else:
                weights.append(0.05)
        total = sum(weights)
        weights = [w / total for w in weights]
        new_picks = random.choices([uid for uid, _ in eligible], weights=weights, k=needed)
        for uid in new_picks:
            existing = self.conn.execute(
                "SELECT consecutive_days, last_win FROM community_picks WHERE user_id = ? ORDER BY date DESC LIMIT 1",
                (uid,)
            ).fetchone()
            days = (existing[0] + 1) if existing and existing[1] and existing[0] < 3 else 1
            self.conn.execute(
                "INSERT INTO community_picks VALUES (?, ?, ?, ?)",
                (uid, today, days, 1)
            )
        self.conn.commit()
        return selected + new_picks

    def update_community_outcome(self, user_id, date, won):
        self.conn.execute(
            "UPDATE community_picks SET last_win = ? WHERE user_id = ? AND date = ?",
            (won, user_id, date)
        )
        self.conn.commit()

    def update_group_verification(self):
        groups = self.conn.execute("SELECT group_id, name, verified, bet_count FROM groups").fetchall()
        for group_id, name, verified, bet_count in groups:
            stats = self.get_user_stats(group_id)
            new_verified = 1 if (
                stats["win_rate"] >= 0.6 and stats["roi"] >= 0.2 and stats["bets"] >= 50
            ) else 0
            if new_verified != verified:
                self.conn.execute(
                    "UPDATE groups SET verified = ?, win_rate = ?, roi = ?, bet_count = ? WHERE group_id = ?",
                    (new_verified, stats["win_rate"], stats["roi"], stats["bets"], group_id)
                )
        self.conn.commit()
""",

    "src/blockchain/betting_pool.py": """
from algosdk.v2client import algod
from algosdk import transaction
from src.blockchain.wallet import AlgorandWallet
from src.utils.db import Database
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

class BettingPool:
    def __init__(self, algod_client, bot_wallet, db_path="data/blog.db"):
        self.client = algod_client
        self.bot_wallet = bot_wallet
        self.db = Database(db_path)
        self.pools = {}
        self.daily_bets = {}
        self.max_bot_bets = 3

    def check_balance(self):
        return 10000

    def check_daily_limit(self, pool_type, group_id=None):
        today = datetime.utcnow().date().isoformat()
        self.daily_bets.setdefault(today, {"bot": 0, "community": []})
        if pool_type == "bot" and self.daily_bets[today]["bot"] >= self.max_bot_bets:
            raise ValueError(f"Reached daily limit of {self.max_bot_bets} bot bets")
        if pool_type == "community" and len(self.daily_bets[today]["community"]) >= 5:
            raise ValueError("Community pool limit reached")
        if pool_type == "group":
            group_key = f"group_{group_id}"
            self.daily_bets[today].setdefault(group_key, False)
            if self.daily_bets[today][group_key]:
                raise ValueError(f"Group {group_id} pool already opened today")
        return today

    def open_pool(self, pool_type, game_id, team, odds, stake, leader_id=None, group_id=None):
        if pool_type not in ["bot", "community", "group"]:
            raise ValueError("Invalid pool type")
        pool_id = f"{pool_type}_{game_id}_{datetime.utcnow().isoformat()}"
        today = self.check_daily_limit(pool_type, group_id)
        if pool_type != "bot" and stake > self.check_balance() * 0.05:
            raise ValueError("Stake exceeds 5% of balance")
        if self.check_balance() < 500:
            raise ValueError("Balance too low")
        if pool_type == "community":
            bettors = self.db.select_community_bettors()
            if leader_id not in bettors:
                raise ValueError("Not selected for community pool")
        params = self.client.suggested_params()
        note = f"Pool: {pool_type}, {game_id}, {team}, odds {odds}, stake {stake}".encode()
        txn = transaction.PaymentTxn(
            sender=self.bot_wallet.address,
            sp=params,
            receiver=self.bot_wallet.address,
            amt=0,
            note=note
        )
        signed_txn = txn.sign(self.bot_wallet.private_key)
        txid = self.client.send_transaction(signed_txn)
        self.pools[pool_id] = {
            "type": pool_type,
            "contributions": {leader_id or self.bot_wallet.address: stake},
            "open": True,
            "game_id": game_id,
            "team": team,
            "odds": odds
        }
        if pool_type == "bot":
            self.daily_bets[today]["bot"] += 1
        elif pool_type == "community":
            self.daily_bets[today]["community"].append(leader_id)
        elif pool_type == "group":
            self.daily_bets[today][f"group_{group_id}"] = True
        return pool_id, txid

    def contribute(self, pool_id, user_address, amount):
        if pool_id not in self.pools or not self.pools[pool_id]["open"]:
            raise ValueError("Pool not open")
        self.pools[pool_id]["contributions"][user_address] = \
            self.pools[pool_id]["contributions"].get(user_address, 0) + amount
        return f"Contributed {amount} microALGOs to {pool_id}"

    def close_pool(self, pool_id):
        if pool_id not in self.pools or not self.pools[pool_id]["open"]:
            raise ValueError("Pool not open")
        self.pools[pool_id]["open"] = False
        total = sum(self.pools[pool_id]["contributions"].values())
        fee = total * 0.01
        self.pools[pool_id]["contributions"][self.bot_wallet.address] = \
            self.pools[pool_id]["contributions"].get(self.bot_wallet.address, 0) + fee
        return total - fee

    def distribute_winnings(self, pool_id, total_winnings):
        if pool_id not in self.pools or self.pools[pool_id]["open"]:
            raise ValueError("Pool still open")
        total_stake = sum(self.pools[pool_id]["contributions"].values())
        payouts = {}
        for addr, stake in self.pools[pool_id]["contributions"].items():
            share = (stake / total_stake) * total_winnings
            payouts[addr] = share
        leader_id = next((k for k in self.pools[pool_id]["contributions"] if k != self.bot_wallet.address), None)
        if leader_id and self.pools[pool_id]["type"] in ["community", "group"]:
            self.db.record_bet(
                user_id=leader_id,
                game_id=self.pools[pool_id]["game_id"],
                team=self.pools[pool_id]["team"],
                stake=self.pools[pool_id]["contributions"].get(leader_id, 0),
                odds=self.pools[pool_id]["odds"],
                won=total_winnings > 0,
                payout=payouts.get(leader_id, 0)
            )
            if self.pools[pool_id]["type"] == "community":
                self.db.update_community_outcome(leader_id, datetime.utcnow().date().isoformat(), total_winnings > 0)
        self.db.update_group_verification()
        return payouts

if __name__ == "__main__":
    client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
    wallet = AlgorandWallet(os.getenv("BOT_MNEMONIC"))
    pool = BettingPool(client, wallet)
    pool_id, txid = pool.open_pool("bot", "game_123", "Phoenix Suns", "+100", 500)
    print(f"Bot pool opened: {pool_id}, TxID: {txid}")
    print(pool.contribute(pool_id, "TEST_USER_ADDRESS", 200))
    total = pool.close_pool(pool_id)
    print(f"Total pool after fee: {total} microALGOs")
    print(pool.distribute_winnings(pool_id, total * 2))
    pool_id, txid = pool.open_pool("community", "game_456", "Celtics", "+110", 300, "LEADER_ADDRESS")
    print(f"Community pool opened: {pool_id}, TxID: {txid}")
""",

    "src/chatbot/discord_bot.py": """
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
    response = "Bot's Top 3 Bets:\\n"
    for i, bet in enumerate(top_bets, 1):
        response += f"{i}. {bet['team1']} vs {bet['team2']}: {bet['winner']} ({bet['confidence']*100:.1f}%, odds {bet['odds']})\\n"
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
    response = "Top 5 Bettors (Weekly ROI):\\n" + "\\n".join(f"{i+1}. <@{uid}>" for i, uid in enumerate([uid for uid, _ in bettors]))
    await ctx.send(response)

@bot.command()
async def community_bettors(ctx):
    bettors = pool_manager.db.select_community_bettors()
    response = "Today's Community Bettors:\\n" + "\\n".join(f"- <@{uid}>" for uid in bettors)
    await ctx.send(response)

token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("DISCORD_TOKEN not found in .env")
bot.run(token)
""",

    "src/blockchain/wallet.py": """
from algosdk import account, mnemonic
import os

class AlgorandWallet:
    def __init__(self, mnemonic_phrase=None):
        if mnemonic_phrase:
            self.private_key = mnemonic.to_private_key(mnemonic_phrase)
            self.address = account.address_from_private_key(self.private_key)
        else:
            self.private_key, self.address = account.generate_account()

    def get_details(self):
        return {
            "address": self.address,
            "mnemonic": mnemonic.from_private_key(self.private_key)
        }
""",

    "src/prediction_engine/engine.py": """
class PredictionEngine:
    def __init__(self):
        self.model = None  # Placeholder for XGBoost

    def predict_game(self, team1, team2):
        # Mock prediction
        return {"winner": team1, "confidence": 0.6}

    def get_top_bets(self, games, limit=3):
        predictions = []
        for game in games:
            pred = self.predict_game(game[0], game[1])
            predictions.append({
                "team1": game[0],
                "team2": game[1],
                "winner": pred["winner"],
                "confidence": pred["confidence"],
                "odds": "+100"
            })
        return sorted(predictions, key=lambda x: x["confidence"], reverse=True)[:limit]
""",

    "src/data_collection/nba_collector.py": """
class NBACollector:
    def __init__(self):
        pass

    def fetch_games(self, season):
        # Placeholder: Use nba_api later
        return [{"game_id": "123", "team1": "Suns", "team2": "Lakers"}]
""",

    "src/data_collection/nba_processor.py": """
class NBAProcessor:
    def __init__(self):
        pass

    def process_games(self, season):
        # Placeholder
        pass
""",

    "src/prediction_engine/game_outcome.py": """
class GameOutcomeModel:
    def __init__(self):
        pass

    def train(self, data):
        # Placeholder
        pass
""",

    ".env": """
DISCORD_TOKEN=your_discord_bot_token
BOT_MNEMONIC=your_25_word_mnemonic
""",

    "requirements.txt": """
discord.py
algosdk
python-dotenv
sqlite3
""",

    "scripts/run_chatbot.py": """
from src.chatbot.discord_bot import bot

if __name__ == "__main__":
    bot.run()
""",

    "README.md": """
# BLOG: AI-Driven Sports Betting Platform

## Overview
BLOG is a decentralized sports betting platform using Algorand, featuring an AI bot, community pools, and verified group pools. Users bet with ALGO (BLOG tokens soon), join pools, and compete for leaderboard spots.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create `.env`:
   - Add `DISCORD_TOKEN` (from Discord Developer Portal).
   - Add `BOT_MNEMONIC` (generate via Algorand wallet or testnet).
3. Fund wallet: https://dispenser.testnet-algorand.network/
4. Run bot:
   ```bash
   python -m scripts.run_chatbot
   ```

## Commands
- `!predict team1 team2`: Get AI prediction.
- `!top_bets`: See bot's top 3 bets.
- `!bot_bet team odds stake`: Open bot pool.
- `!community_pool team odds stake`: Open community pool (if selected).
- `!group_pool group_name team odds stake`: Open group pool (if verified).
- `!back_bet pool_id amount`: Join a pool.
- `!top_bettors`: View leaderboard.
- `!community_bettors`: See today's community bettors.

## Features
- Bot: 3 daily bets with pools.
- Community Pools: 5 bettors/day, tiered selection, max 3 days if winning.
- Group Pools: Verified groups (≥60% win rate), revocable if <50%.
- Algorand: Transparent pools, low fees.

## Next Steps
- Add BLOG token (100M supply).
- Integrate live NBA data.
- Expand to mobile app.
"""
}

# Create directories
for d in dirs:
    create_directory(d)

# Create files
for path, content in files.items():
    write_file(path, content)

print("Project structure created successfully!")
print("Next steps:")
print("1. Edit .env with DISCORD_TOKEN and BOT_MNEMONIC")
print("2. Install dependencies: pip install -r requirements.txt")
print("3. Fund wallet: https://dispenser.testnet-algorand.network/")
print("4. Run: python -m scripts.run_chatbot")