# Solana Wallet Token Monitor

A simplified Python-based clone of the Insider-Monitor tool that:

1. Connects to PostgreSQL database
2. Retrieves wallets to monitor from database
3. Retrieves tokens from Solana wallets using the Solana Mainnet Beta RPC
4. Checks if tokens exist in the database
5. Fetches and saves token data from Dexscreener

## Features

- 🔍 Fetch all tokens from Solana wallet addresses stored in database
- 💾 Store token data in PostgreSQL database
- 📊 Retrieve token info from Dexscreener API
- 🔄 Update token data when changes are detected

## Requirements

- Python 3.8+
- PostgreSQL database
- Internet connection to access Solana RPC and Dexscreener API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd wallet-monitoring
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on the `.env.example` file:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your configuration:
```
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wallet_monitor
DB_USER=postgres
DB_PASSWORD=postgres

# Solana Configuration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_RPC_TIMEOUT=30
```

## Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE wallet_monitor;
```

2. Create a table to store wallet addresses:
```sql
CREATE TABLE wallets_to_monitor (
    wallet_address TEXT PRIMARY KEY,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

3. Add wallet addresses to monitor:
```sql
INSERT INTO wallets_to_monitor (wallet_address) VALUES ('YOUR_SOLANA_WALLET_ADDRESS');
```

4. The application will automatically create the token_entity table when run.

## Usage

Run the application to process all wallets in the database:
```bash
python main.py
```

## Database Schema

The application uses three tables:

1. `wallets_to_monitor` - Stores the Solana wallet addresses to monitor:
```sql
CREATE TABLE wallets_to_monitor (
    wallet_address TEXT PRIMARY KEY,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

2. `token_entity` - Stores token metadata:
```sql
CREATE TABLE token_entity (
    token_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    price NUMERIC(30, 10) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

3. `token_accounts` - Links wallets to their tokens and stores balance information:
```sql
CREATE TABLE token_accounts (
    token_id SERIAL PRIMARY KEY,
    wallet_address TEXT NOT NULL,
    token_mint VARCHAR(255) NOT NULL,
    balance BIGINT NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    symbol TEXT,
    decimals INTEGER,
    UNIQUE(wallet_address, token_mint)
);
```

## Project Structure

```
wallet-monitoring/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── README.md            # This file
└── src/                 # Source code
    ├── db/              # Database related modules
    │   ├── __init__.py
    │   └── database.py  # Database connection handler
    ├── dexscreener/     # Dexscreener API integration
    │   ├── __init__.py
    │   └── api.py       # Dexscreener API client
    ├── models/          # Data models
    │   ├── __init__.py
    │   ├── token_entity.py  # Token entity database operations
    │   ├── token_account.py # Token account linking wallets to tokens
    │   └── wallet_manager.py # Wallet manager for retrieving wallets
    └── solana/          # Solana blockchain integration
        ├── __init__.py
        └── wallet.py    # Solana wallet operations
```

## License

MIT 