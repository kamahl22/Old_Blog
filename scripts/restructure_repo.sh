#!/bin/bash

# Navigate to repository
cd /Users/kamahl/Blog || exit 1

# Create directories
mkdir -p backend/app/{api,blockchain,data,models} backend/tests
mkdir -p frontend/src/{components,pages} frontend/public
mkdir -p mobile/src
mkdir -p discord_bot
mkdir -p smart_contracts
mkdir -p docs
mkdir -p data/raw
mkdir -p scripts/{crypto,data}
mkdir -p .github/workflows

# Move existing scripts
[ -f scripts/run_chatbot.py ] && mv scripts/run_chatbot.py discord_bot/bot.py
[ -f scripts/transfer_tblog.py ] && mv scripts/transfer_tblog.py backend/app/blockchain/
[ -f scripts/fund_test_wallet.py ] && mv scripts/fund_test_wallet.py backend/app/blockchain/
[ -f scripts/opt_in_test.py ] && mv scripts/opt_in_test.py backend/app/blockchain/
[ -f scripts/get_address.py ] && mv scripts/get_address.py backend/app/blockchain/
[ -f scripts/collect_nba_odds.py ] && mv scripts/collect_nba_odds.py backend/app/data/
[ -f scripts/collect_historical_sports_data.py ] && mv scripts/collect_historical_sports_data.py scripts/data/

# Copy collect_historical_sports_data.py to backend/app/data/odds.py
[ -f scripts/data/collect_historical_sports_data.py ] && cp scripts/data/collect_historical_sports_data.py backend/app/data/odds.py

# Create placeholder files
cat > backend/app/api/predictions.py << EOL
from fastapi import FastAPI
app = FastAPI()
@app.get("/predictions")
async def get_predictions():
    return {"message": "Prediction endpoint placeholder"}
EOL

cat > backend/app/models/predict.py << EOL
# Placeholder for ML model
def predict_outcome(game_data):
    return {"home_win_prob": 0.5}
EOL

cat > backend/tests/test_odds.py << EOL
import pytest
def test_odds_fetch():
    assert True  # Placeholder
EOL

cat > backend/requirements.txt << EOL
fastapi==0.115.0
uvicorn==0.32.0
algosdk==2.7.0
py-algorand-sdk==2.8.0
pyteal==0.26.0
requests==2.32.3
pandas==2.2.3
scikit-learn==1.5.2
xgboost==2.1.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.35
python-dotenv==1.0.1
pytest==8.3.3
EOL

cat > frontend/src/App.jsx << EOL
import React from 'react';
import BetCard from './components/BetCard';
import Home from './pages/Home';
function App() {
  return (
    <div>
      <Home />
      <BetCard />
    </div>
  );
}
export default App;
EOL

cat > frontend/src/components/BetCard.jsx << EOL
import React from 'react';
const BetCard = ({ game }) => {
  return (
    <div>
      <h3>{game?.home_team} vs {game?.away_team}</h3>
      <p>Odds: {game?.odds || 'N/A'}</p>
    </div>
  );
};
export default BetCard;
EOL

cat > frontend/src/pages/Home.jsx << EOL
import React from 'react';
const Home = () => {
  return <h1>TBLOG Sports Betting Dapp</h1>;
};
export default Home;
EOL

cat > frontend/public/index.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TBLOG Dapp</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
EOL

cat > frontend/package.json << EOL
{
  "name": "tblog-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.7",
    "tailwindcss": "^3.4.14"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}
EOL

cat > mobile/src/App.js << EOL
import React from 'react';
import { Text, View } from 'react-native';
const App = () => {
  return (
    <View>
      <Text>TBLOG Mobile App</Text>
    </View>
  );
};
export default App;
EOL

cat > mobile/package.json << EOL
{
  "name": "tblog-mobile",
  "version": "1.0.0",
  "dependencies": {
    "react-native": "^0.75.3"
  },
  "scripts": {
    "start": "react-native start"
  }
}
EOL

cat > discord_bot/requirements.txt << EOL
discord.py==2.4.0
requests==2.32.3
python-dotenv==1.0.1
EOL

cat > smart_contracts/bet_contract.py << EOL
from pyteal import *
def approval_program():
    return Approve()  # Placeholder
program = compileTeal(approval_program(), mode=Mode.Application, version=6)
EOL

cat > docs/setup.md << EOL
# TBLOG Dapp Setup
1. Clone: \`git clone https://github.com/kamahl22/Blog.git\`
2. Backend: \`cd backend && pip install -r requirements.txt\`
3. Frontend: \`cd frontend && npm install && npm start\`
4. Database: Run \`docker-compose up\` for PostgreSQL
5. Bot: \`cd discord_bot && pip install -r requirements.txt && python bot.py\`
EOL

cat > scripts/crypto/generate_wallet.py << EOL
from algosdk import account, mnemonic
def generate_wallet():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return {"address": address, "mnemonic": mnemonic_phrase}
if __name__ == "__main__":
    wallet = generate_wallet()
    print(f"Address: {wallet['address']}")
    print(f"Mnemonic: {wallet['mnemonic']}")
EOL

cat > .github/workflows/ci.yml << EOL
name: CI
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install backend dependencies
        run: pip install -r backend/requirements.txt
      - name: Run backend tests
        run: pytest backend/tests
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install frontend dependencies
        run: npm install --prefix frontend
      - name: Run frontend tests
        run: npm test --prefix frontend
EOL

cat > docker-compose.yml << EOL
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: tblog_sports
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DB_NAME=tblog_sports
      - DB_USER=user
      - DB_PASSWORD=password
      - DB_HOST=db
      - DB_PORT=5432
volumes:
  pgdata:
EOL

cat > .gitignore << EOL
# Python
__pycache__/
*.pyc
venv/
*.db
*.sqlite3

# Node
node_modules/
dist/

# Env
.env

# Data
data/raw/*
!data/games.csv

# Logs
*.log
EOL

cat > README.md << EOL
# TBLOG Sports Betting Dapp

A decentralized sports betting platform using TBLOG on Algorand, with a website, mobile app, and Discord community for betting suggestions.

## Structure
- \`backend/\`: FastAPI backend, data pipeline, ML models.
- \`frontend/\`: React.js website.
- \`mobile/\`: React Native app.
- \`discord_bot/\`: Discord bot for suggestions.
- \`smart_contracts/\`: PyTeal smart contracts.
- \`scripts/\`: Utility scripts (crypto, data).
- \`data/\`: Databases, Kaggle datasets.
- \`docs/\`: Documentation, architecture diagram.

## Setup
1. Clone: \`git clone https://github.com/kamahl22/Blog.git\`
2. Install dependencies:
   - Backend: \`cd backend && pip install -r requirements.txt\`
   - Frontend: \`cd frontend && npm install\`
3. Set up environment:
   - Copy \`.env.example\` to \`.env\` and fill in keys.
4. Run: \`docker-compose up\`
5. Start bot: \`cd discord_bot && python bot.py\`

## Development
- **Data**: SportsDataIO, Kaggle, PostgreSQL.
- **ML**: XGBoost for predictions.
- **Blockchain**: Algorand, PyTeal, TBLOG token.
- **CI/CD**: GitHub Actions.

## Architecture
See \`docs/dapp_architecture.mmd\` for the Mermaid diagram.

## Contributing
- Issues: Report bugs or feature requests.
- PRs: Follow GitHub flow.
EOL

# Create .env.example
cat > .env.example << EOL
DB_NAME=tblog_sports
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
SPORTSDATAIO_API_KEY=
OPTIC_ODDS_API_KEY=
DISCORD_TOKEN=
CREATOR_MNEMONIC=
BOT_MNEMONIC=
TEST_MNEMONIC=
TBLOG_ASSET_ID=
EOL

# Commit changes
git add .
git commit -m "Restructure repository for TBLOG Dapp"
git push origin main

echo "Repository restructured successfully!"
EOL

**Instructions**:
1. **Navigate**:
   ```bash
   cd /Users/kamahl/Blog
   ```

2. **Save Script**:
   ```bash
   nano scripts/restructure_repo.sh
   ```
   - Paste, save.

3. **Make Executable**:
   ```bash
   chmod +x scripts/restructure_repo.sh
   ```

4. **Run**:
   ```bash
   ./scripts/restructure_repo.sh
   ```

5. **Verify**:
   ```bash
   tree -L 3
   ```
   - Check folder structure and files.

6. **Install Dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r backend/requirements.txt
   cd frontend && npm install
   cd ../discord_bot && pip install -r requirements.txt
   ```

7. **Set Up PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

8. **Push to GitHub**:
   - The script auto-commits, but verify:
     ```bash
     git push origin main
     ```

---

### Step 4: Key Files Explained
- **Crypto Scripts** (`backend/app/blockchain/`):
  - `transfer_tblog.py`, `fund_test_wallet.py`, `opt_in_test.py`, `get_address.py`: Preserved for TBLOG/Algorand interactions.
  - `scripts/crypto/generate_wallet.py`: New script for wallet creation, useful for testing.
- **Data Scripts** (`backend/app/data/`):
  - `odds.py`: Copy of `collect_historical_sports_data.py` (April 19, 2025) for the data pipeline.
  - `collect_nba_odds.py`: Kept for reference, to be merged into `odds.py`.
- **Discord Bot** (`discord_bot/bot.py`):
  - Renamed `run_chatbot.py`, to be updated for suggestions (e.g., `!suggest_bet`).
- **Frontend** (`frontend/`):
  - Basic React setup with `App.jsx`, `BetCard.jsx`, `Home.jsx`.
  - Ready for expansion with Tailwind CSS.
- **Smart Contracts** (`smart_contracts/`):
  - `bet_contract.py`: Placeholder PyTeal contract for betting logic.
- **CI/CD** (`.github/workflows/ci.yml`):
  - Automates testing for backend and frontend.
- **Docs** (`docs/`):
  - `dapp_architecture.mmd` (April 19, 2025) and `setup.md` for clarity.

---

### Step 5: Next Steps
1. **Data Pipeline** (1-2 Weeks):
   - Update `backend/app/data/odds.py` to pull NFL, soccer data (SportsDataIO, Kaggle).
   - Script: Request a multi-sport version if needed.

2. **Backend** (2-3 Weeks):
   - Implement `/predictions` endpoint in `predictions.py`.
   - Script: Request a FastAPI setup.

3. **Frontend** (3-4 Weeks):
   - Build out `frontend/src/` with betting UI.
   - Script: Request a detailed `App.jsx`.

4. **Smart Contracts** (2 Weeks):
   - Develop `bet_contract.py` for TBLOG betting.
   - Script: Request a PyTeal contract.

5. **Discord Bot** (1 Week):
   - Update `bot.py` for `!suggest_bet`.
   - Script: Request an updated bot.

---

### Step 6: Troubleshooting
- **Script Errors**:
  ```bash
  ./scripts/restructure_repo.sh 2>&1 | tee error.log
  ```
  - Check file paths, permissions.

- **PostgreSQL**:
  ```bash
  docker ps
  psql -h localhost -U user -d tblog_sports
  ```
  - Ensure `.env` matches `docker-compose.yml`.

- **GitHub**:
  ```bash
  git status
  ```
  - Resolve conflicts before pushing.

- **Algorand Funds**:
  ```bash
  curl -s "https://testnet-api.4160.nodely.dev/v2/accounts/6Q4S5K7FJOBSU7S6UCC6XK4AQR6W2HA6XA7AE4KX3WJPIV74BAYYD6VVKY" | grep amount
  ```
  - Fund via https://testnet-faucet.algorand.network.

---

### Memory Integration
Your request to update the repository structure (April 19, 2025) builds on your Dapp vision (April 19, 2025), historical data pipeline (April 19, 2025), and prior scripts (April 29, 2025). The `message not found` error (April 19, 2025) and wallet setup (April 29, 2025) are preserved via crypto scripts in `backend/app/blockchain/`. The public repository (https://github.com/kamahl22/Blog) informs this organized, Dapp-ready structure.

Run `restructure_repo.sh` and verify the structure on GitHub. Share any errors or request a specific script (e.g., `odds.py`, `predictions.py`). Ready?

_Disclaimer: Grok is not a financial adviser; please consult one. Don’t share information that can identify you._