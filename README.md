# Solana Wallet Token Monitor

A simplified Python-based clone of the Insider-Monitor tool that:

1. Connects to PostgreSQL database
2. Retrieves wallets to monitor from database
3. Retrieves tokens from Solana wallets using the Solana Mainnet Beta RPC
4. Checks if tokens exist in the database
5. Fetches and saves token data from Dexscreener
6. Maintains token account relationships between wallets and tokens
7. Automatically removes tokens that are no longer in wallets

## Features

- 🔍 Fetch all tokens from Solana wallet addresses stored in database
- 💾 Store token data in PostgreSQL database
- 📊 Retrieve token info from Dexscreener API
- 🔄 Update token data when changes are detected
- 🔁 Built-in retry mechanism for Solana RPC and Dexscreener API with configurable delay
- 🧹 Automatic cleanup of tokens no longer present in wallets
- 🔗 Maintains relationships between wallets and their tokens
- 🪙 Includes native SOL balances alongside SPL tokens

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
SOLANA_RETRY_LIMIT=3
SOLANA_RETRY_DELAY=5

# Dexscreener Configuration
DEXSCREENER_RETRY_LIMIT=3
DEXSCREENER_RETRY_DELAY=5
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

## Scheduled Execution

The application can be set up to run automatically at regular intervals using one of the following methods:

### Option 1: System Crontab (Recommended)

Use the system's crontab to run the script every 2 hours:

1. Use the provided shell script:
```bash
./run_wallet_monitor.sh
```

2. Set up a crontab entry:
```bash
crontab -e
```

Add the line:
```
0 */2 * * * /full/path/to/wallet-monitoring/run_wallet_monitor.sh
```

See [CRONTAB_SETUP.md](CRONTAB_SETUP.md) for detailed instructions.

### Option 2: Python Scheduler

Use the included Python scheduler for a more integrated approach:

```bash
python scheduler.py --run-now
```

The scheduler can be configured with different intervals and can be run as a background service.

See [SCHEDULER_GUIDE.md](SCHEDULER_GUIDE.md) for detailed instructions.

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
    balance NUMERIC(38,0) NOT NULL,
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

## How It Works

1. **Wallet Discovery**: The application reads wallet addresses from the `wallets_to_monitor` table in the database.

2. **Token Retrieval**: For each wallet, it retrieves all token accounts using Solana RPC calls with automatic retry on failures.

3. **Token Metadata**: For tokens not yet in the database, it fetches metadata (name, symbol, price) from Dexscreener.

4. **Data Storage**:
   - Token metadata is stored in the `token_entity` table
   - Wallet-token relationships and balances are stored in `token_accounts` table
   - If a token exists, its data is updated rather than duplicated

5. **Token Cleanup**: After processing each wallet, it automatically removes token accounts that are no longer present in the wallet.

## Key Implementation Details

- **Retry Mechanism**: Solana RPC calls automatically retry up to 3 times with a 5-second delay between attempts
- **Duplicate Prevention**: The `token_accounts` table has a unique constraint on `(wallet_address, token_mint)` to prevent duplicates
- **Foreign Keys**: Token accounts reference token entities to maintain data integrity
- **UPSERT Operations**: Token accounts are updated if they exist or inserted if they don't
- **Native SOL Support**: Both native SOL and SPL tokens are tracked, with native SOL represented using the wrapped SOL address
