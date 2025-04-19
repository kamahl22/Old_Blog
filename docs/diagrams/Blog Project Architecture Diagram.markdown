# Blog Project Architecture Diagram

```
/Users/kamahl/Blog/
├── .env                    # Environment variables (DISCORD_TOKEN, CREATOR_MNEMONIC, BOT_MNEMONIC, TBLOG_ASSET_ID)
├── .env.example            # Template for .env
├── data/                   # Data storage
│   └── blog.db             # SQLite DB for bets, groups, etc.
├── scripts/                # Python scripts for TBLOG and chatbot
│   ├── generate_wallet.py  # Generates new Algorand TestNet wallet
│   ├── test_node.py        # Tests Nodely node connectivity
│   ├── create_tblog.py     # Creates TBLOG ASA
│   ├── opt_in_tblog.py     # Bot wallet opts into TBLOG
│   ├── transfer_tblog.py   # Transfers 10,000 TBLOG to bot
│   └── run_chatbot.py      # Runs Discord chatbot (!bot_bet, !community_pool)
├── requirements.txt        # Python dependencies (algosdk, python-dotenv, discord.py, nba_api, etc.)
└── README.md               # Project documentation

[External Dependencies]
├── Algorand TestNet        # Via Nodely node (https://testnet-api.4160.nodely.dev)
├── Discord API             # For chatbot commands
├── NBA API                 # For game and player stats
```

**Components**:

- **Wallet Generation**: `generate_wallet.py` creates creator wallet.
- **Node Testing**: `test_node.py` ensures Nodely node is reachable.
- **ASA Creation**: `create_tblog.py` creates TBLOG (1B supply, bot as manager).
- **ASA Management**: `opt_in_tblog.py` and `transfer_tblog.py` handle bot integration.
- **Chatbot**: `run_chatbot.py` processes betting commands, stores in `blog.db`.
- **Data**: `blog.db` tracks bets, groups (e.g., "Only1"), and stats.