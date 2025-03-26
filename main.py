#!/usr/bin/env python3
"""
Solana Wallet Token Monitor

A simplified version of the Insider-Monitor tool that:
1. Connects to PostgreSQL
2. Retrieves tokens from wallets stored in database
3. Checks if tokens exist in the database
4. Fetches and saves token data from Dexscreener
"""

import os
import logging
from dotenv import load_dotenv

from src.db.database import Database
from src.solana.wallet import SolanaWallet
from src.dexscreener.api import DexscreenerAPI
from src.models.token_entity import TokenEntityManager
from src.models.wallet_manager import WalletManager
from src.logger.logger import Logger

# Initialize logger
logger = Logger()

def main():
    """Main entry point of the application."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize components
        db = Database()
        token_manager = TokenEntityManager(db)
        wallet_manager = WalletManager(db)
        solana_wallet = SolanaWallet()
        dexscreener = DexscreenerAPI()
        
        # Ensure token table exists
        token_manager.create_table_if_not_exists()
        
        # Get all wallets from database
        wallet_addresses = wallet_manager.get_wallets()
        
        if not wallet_addresses:
            logger.warning("No wallet addresses found in database")
            return
        
        logger.info(f"Found {len(wallet_addresses)} wallets to process")
        
        # Process each wallet
        for wallet_address in wallet_addresses:
            logger.info(f"Processing wallet: {wallet_address}")
            
            # Get all tokens from the wallet
            tokens = solana_wallet.get_tokens(wallet_address)
            logger.info(f"Found {len(tokens)} tokens in wallet {wallet_address}")
            
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