#!/usr/bin/env python3
"""
Solana Wallet Token Monitor

A simplified version of the Insider-Monitor tool that:
1. Connects to PostgreSQL
2. Retrieves tokens from wallets stored in database
3. Checks if tokens exist in the database
4. Fetches and saves token data from Dexscreener
5. Links tokens to wallets in token_accounts table
"""

import time
from dotenv import load_dotenv

from src.db.database import Database
from src.solana.wallet import SolanaWallet
from src.dexscreener.api import DexscreenerAPI
from src.models.token_entity import TokenEntityManager
from src.models.token_account import TokenAccountManager
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
        token_account_manager = TokenAccountManager(db)
        solana_wallet = SolanaWallet()
        dexscreener = DexscreenerAPI()
        
        # Ensure tables exist
        token_manager.create_table_if_not_exists()
        token_account_manager.create_table_if_not_exists()
        
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
            
            # Keep track of current token mints for cleanup later
            current_token_mints = []
            
            # Process each token
            for token in tokens:
                token_mint = token['token_id']
                token_balance = token['amount']
                token_decimals = token.get('decimals', 0)
                
                # Add to current tokens list
                current_token_mints.append(token_mint)
                
                # Calculate raw balance (convert from UI amount to raw amount)
                raw_balance = int(token_balance * (10 ** token_decimals))
                
                # Check if token exists in database
                if not token_manager.token_exists(token_mint):
                    logger.info(f"Token {token_mint} not found in database, fetching from Dexscreener")
                    
                    # Fetch token data from Dexscreener
                    token_data = dexscreener.get_token_data(token_mint)
                    
                    if token_data:
                        # Save token data to database
                        token_manager.save_token(token_data)
                        logger.info(f"Saved token {token_data['name']} ({token_data['symbol']}) to database")
                        
                        # Get the symbol from Dexscreener data
                        token_symbol = token_data['symbol']
                        
                        # Create token account record
                        token_account = {
                            'wallet_address': wallet_address,
                            'token_mint': token_mint,
                            'balance': raw_balance,
                            'symbol': token_symbol,
                            'decimals': token_decimals
                        }
                        
                        # Save token account to database
                        result = token_account_manager.save_token_account(token_account)
                        if result:
                            logger.info(f"Saved token account for {token_symbol} in wallet {wallet_address}")
                        else:
                            logger.warning(f"Failed to save token account for {token_symbol} in wallet {wallet_address}")
                    else:
                        logger.warning(f"Could not fetch data for token {token_mint} from Dexscreener, skipping token account creation")
                else:
                    # Get the token info from our database
                    token_info = token_manager.get_token(token_mint)
                    if token_info:
                        token_symbol = token_info['symbol']
                        logger.info(f"Token {token_mint} already exists in database")
                        
                        # Create token account record
                        token_account = {
                            'wallet_address': wallet_address,
                            'token_mint': token_mint,
                            'balance': raw_balance,
                            'symbol': token_symbol,
                            'decimals': token_decimals
                        }
                        
                        # Save token account to database
                        result = token_account_manager.save_token_account(token_account)
                        if result:
                            logger.info(f"Saved token account for {token_symbol} in wallet {wallet_address}")
                        else:
                            logger.warning(f"Failed to save token account for {token_symbol} in wallet {wallet_address}")
                    else:
                        logger.warning(f"Token {token_mint} exists in database but could not be retrieved, skipping token account creation")
            
            # Clean up tokens no longer in the wallet
            removed_count = token_account_manager.clean_up_removed_tokens(wallet_address, current_token_mints)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} tokens that are no longer in wallet {wallet_address}")
            
            # Sleep for 1 second
            time.sleep(1)
        logger.info("Token processing completed successfully")
        
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
    finally:
        # Close database connection
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main() 