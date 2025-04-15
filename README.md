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