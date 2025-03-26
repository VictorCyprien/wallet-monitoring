# Solana Wallet Token Monitor

A simplified Python-based clone of the Insider-Monitor tool that:

1. Connects to PostgreSQL database
2. Retrieves tokens from a Solana wallet using the Solana Mainnet Beta RPC
3. Checks if tokens exist in the database
4. Fetches and saves token data from Dexscreener

## Features

- 🔍 Fetch all tokens from a Solana wallet address
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

# Default wallet to monitor (optional)
SOLANA_WALLET_ADDRESS=your_wallet_address_here
```

## Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE wallet_monitor;
```

2. The application will automatically create the necessary tables when run

## Usage

Run the application with a specific wallet address:
```bash
python main.py --wallet YOUR_SOLANA_WALLET_ADDRESS
```

Or, if you've set the default wallet in the `.env` file:
```bash
python main.py
```

## Database Schema

The application creates a single table called `token_entity` with the following schema:

```sql
CREATE TABLE token_entity (
    token_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    price NUMERIC(30, 10) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    │   └── token_entity.py  # Token entity database operations
    └── solana/          # Solana blockchain integration
        ├── __init__.py
        └── wallet.py    # Solana wallet operations
```

## License

MIT 