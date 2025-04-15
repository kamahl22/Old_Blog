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
        self.pools[pool_id]["contributions"][user_address] =             self.pools[pool_id]["contributions"].get(user_address, 0) + amount
        return f"Contributed {amount} microALGOs to {pool_id}"

    def close_pool(self, pool_id):
        if pool_id not in self.pools or not self.pools[pool_id]["open"]:
            raise ValueError("Pool not open")
        self.pools[pool_id]["open"] = False
        total = sum(self.pools[pool_id]["contributions"].values())
        fee = total * 0.01
        self.pools[pool_id]["contributions"][self.bot_wallet.address] =             self.pools[pool_id]["contributions"].get(self.bot_wallet.address, 0) + fee
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