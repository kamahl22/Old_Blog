# TBLOG Sports Betting Dapp

A decentralized sports betting platform using TBLOG on Algorand, with a website, mobile app, and Discord community for betting suggestions.

## Structure
- `backend/`: FastAPI backend, data pipeline, ML models.
- `frontend/`: React.js website.
- `mobile/`: React Native app.
- `discord_bot/`: Discord bot for suggestions.
- `smart_contracts/`: PyTeal smart contracts.
- `scripts/`: Utility scripts (crypto, data).
- `data/`: Databases, Kaggle datasets.
- `docs/`: Documentation, architecture diagram.

## Setup
1. Clone: `git clone https://github.com/kamahl22/Blog.git`
2. Install dependencies:
   - Backend: `cd backend && pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`
3. Set up environment:
   - Copy `.env.example` to `.env` and fill in keys.
4. Run: `docker-compose up`
5. Start bot: `cd discord_bot && python bot.py`

## Development
- **Data**: SportsDataIO, Kaggle, PostgreSQL.
- **ML**: XGBoost for predictions.
- **Blockchain**: Algorand, PyTeal, TBLOG token.
- **CI/CD**: GitHub Actions.

## Architecture
See `docs/dapp_architecture.mmd` for the Mermaid diagram.

## Contributing
- Issues: Report bugs or feature requests.
- PRs: Follow GitHub flow.
