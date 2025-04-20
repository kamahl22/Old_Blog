import discord
import os
import sqlite3
from discord.ext import commands
from algosdk.v2client import algod
from algosdk import transaction, mnemonic, account
from dotenv import load_dotenv

load_dotenv()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# SQLite database setup
def init_db():
    conn = sqlite3.connect("data/blog.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT,
            team TEXT,
            odds TEXT,
            amount INTEGER,
            txid TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            algo_address TEXT
        )
    """)
    conn.commit()
    conn.close()

# Check if transaction exists
def check_transaction(txid):
    conn = sqlite3.connect("data/blog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT txid FROM bets WHERE txid = ?", (txid,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Algorand TBLOG transaction
async def send_tblog(sender_mnemonic, receiver_address, amount, asset_id):
    client = algod.AlgodClient("", "https://testnet-api.4160.nodely.dev")
    private_key = mnemonic.to_private_key(sender_mnemonic)
    sender_address = account.address_from_private_key(private_key)
    
    # Check sender balance
    try:
        account_info = client.account_info(sender_address)
    except Exception as e:
        raise ValueError(f"Failed to fetch account info: {e}")
    
    algo_balance = account_info.get('amount', 0)
    if algo_balance < 200_000:  # 0.2 ALGO for fees
        raise ValueError(f"Insufficient ALGO in bot wallet: {algo_balance/1_000_000} ALGO")
    
    for asset in account_info.get('assets', []):
        if asset['asset-id'] == int(asset_id):
            if asset['amount'] < amount * 1_000_000:
                raise ValueError(f"Insufficient TBLOG: {asset['amount']/1_000_000} TBLOG")
            break
    else:
        raise ValueError("Bot wallet not opted into TBLOG")

    params = client.suggested_params()
    txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount * 1_000_000,  # Convert to microTBLOG
        index=int(asset_id)
    )
    signed_txn = txn.sign(private_key)
    try:
        txid = client.send_transaction(signed_txn)
        transaction.wait_for_confirmation(client, txid, 4)
    except Exception as e:
        raise ValueError(f"Transaction failed: {e}")
    
    # Verify transaction in ledger
    try:
        client.status_after_block(client.status().get('last-round'))
        tx_info = client.pending_transaction_info(txid)
        if 'confirmed-round' not in tx_info:
            raise ValueError(f"Transaction {txid} not confirmed")
    except Exception as e:
        raise ValueError(f"Failed to verify transaction {txid}: {e}")
    
    # Check for duplicates
    if check_transaction(txid):
        raise ValueError(f"Transaction {txid} already in ledger")
    
    return txid

# Get user’s Algorand address
def get_user_address(discord_id):
    conn = sqlite3.connect("data/blog.db")
    cursor = conn.cursor()
    cursor.execute("SELECT algo_address FROM users WHERE discord_id = ?", (discord_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    init_db()

@client.command()
async def register_address(ctx, algo_address: str):
    discord_id = str(ctx.author.id)
    conn = sqlite3.connect("data/blog.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (discord_id, algo_address) VALUES (?, ?)", 
                  (discord_id, algo_address))
    conn.commit()
    conn.close()
    await ctx.send(f"Registered Algorand address: {algo_address}")

@client.command()
async def bot_bet(ctx, team: str, odds: str, amount: int):
    discord_id = str(ctx.author.id)
    user_address = get_user_address(discord_id)
    if not user_address:
        await ctx.send("Please register your Algorand address with !register_address <address>")
        return
    
    bot_mnemonic = os.getenv("BOT_MNEMONIC")
    asset_id = os.getenv("TBLOG_ASSET_ID")
    try:
        txid = await send_tblog(bot_mnemonic, user_address, amount, asset_id)
        conn = sqlite3.connect("data/blog.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bets (discord_id, team, odds, amount, txid) VALUES (?, ?, ?, ?, ?)",
                      (discord_id, team, odds, amount, txid))
        conn.commit()
        conn.close()
        await ctx.send(f"Bet {amount} TBLOG on {team} at {odds}. TxID: {txid}")
    except Exception as e:
        await ctx.send(f"Error placing bet: {e}")

@client.command()
async def community_pool(ctx, team: str, odds: str, amount: int):
    await ctx.send(f"Added {amount} TBLOG to community pool for {team} at {odds} (placeholder)")

# Run bot
client.run(os.getenv("DISCORD_TOKEN"))