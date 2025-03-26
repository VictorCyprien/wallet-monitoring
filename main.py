#!/usr/bin/env python3
"""
Solana Wallet Token Monitor

A simplified version of the Insider-Monitor tool that:
1. Connects to PostgreSQL
2. Retrieves tokens from a Solana wallet
3. Checks if tokens exist in the database
4. Fetches and saves token data from Dexscreener
"""

import argparse
import os
import logging
from dotenv import load_dotenv

from src.db.database import Database
from src.solana.wallet import SolanaWallet
from src.dexscreener.api import DexscreenerAPI
from src.models.token_entity import TokenEntityManager
from src.logger.logger import Logger

# Initialize logger
logger = Logger()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Solana Wallet Token Monitor')
    parser.add_argument('--wallet', type=str, help='Solana wallet address to monitor')
    parser.add_argument('--db-config', type=str, default='.env', help='Path to database configuration file')
    return parser.parse_args()

def main():
    """Main entry point of the application."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_args()
    wallet_address = args.wallet or os.getenv('SOLANA_WALLET_ADDRESS')
    
    if not wallet_address:
        logger.error("No wallet address provided. Use --wallet argument or set SOLANA_WALLET_ADDRESS environment variable.")
        return
    
    try:
        # Initialize components
        db = Database()
        token_manager = TokenEntityManager(db)
        solana_wallet = SolanaWallet()
        dexscreener = DexscreenerAPI()
        
        # Ensure database tables exist
        token_manager.create_table_if_not_exists()
        
        # Get all tokens from the wallet
        logger.info(f"Retrieving tokens for wallet: {wallet_address}")
        tokens = solana_wallet.get_tokens(wallet_address)
        logger.info(f"Found {len(tokens)} tokens in wallet")
        
        # Process each token
        for token in tokens:
            token_id = token['token_id']
            
            # Check if token exists in database
            if not token_manager.token_exists(token_id):
                logger.info(f"Token {token_id} not found in database, fetching from Dexscreener")
                
                # Fetch token data from Dexscreener
                token_data = dexscreener.get_token_data(token_id)
                
                if token_data:
                    # Save token data to database
                    token_manager.save_token(token_data)
                    logger.info(f"Saved token {token_data['name']} ({token_data['symbol']}) to database")
                else:
                    logger.warning(f"Could not fetch data for token {token_id}")
            else:
                logger.info(f"Token {token_id} already exists in database")
        
        logger.info("Token processing completed successfully")
        
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
    finally:
        # Close database connection
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main() 