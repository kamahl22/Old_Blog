from sqlite3 import connect
import random
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.conn = connect(db_path)
        self.create_tables()

    def create_tables(self):
        self.conn.execute("""
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
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT,
                name TEXT,
                verified INTEGER,
                win_rate REAL,
                roi REAL,
                bet_count INTEGER
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS community_picks (
                user_id TEXT,
                date TEXT,
                consecutive_days INTEGER,
                last_win INTEGER
            )
        """)
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
            """
            SELECT user_id, SUM(payout) - SUM(stake) AS profit, SUM(stake) AS total, COUNT(*) AS bets
            FROM bets WHERE timestamp > ?
            GROUP BY user_id HAVING bets >= ? AND total > 0
            ORDER BY (SUM(payout) - SUM(stake)) / SUM(stake) DESC
            """,
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