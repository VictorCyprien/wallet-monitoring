#!/usr/bin/env python3
"""
Script to update token prices from DexScreener API.

This script:
1. Retrieves all tokens from the database
2. Fetches latest price data from DexScreener API
3. Updates token prices in the database
"""

import logging
import sys
import os
import time
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("token-price-updater")

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.database import Database
from src.models.token_entity import TokenEntityManager
from src.dexscreener.api import DexscreenerAPI

# Retry configuration
MAX_RETRIES = int(os.getenv('DEXSCREENER_RETRY_LIMIT', 3))
RETRY_DELAY = int(os.getenv('DEXSCREENER_RETRY_DELAY', 5))  # seconds

def get_token_data_with_retry(dexscreener, token_id, symbol, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    """
    Get token data with retry mechanism.
    
    Args:
        dexscreener: DexscreenerAPI instance
        token_id: Token contract address
        symbol: Token symbol (for logging)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        Dict or None: Token data or None if all retries failed
    """
    for attempt in range(1, max_retries + 1):
        try:
            token_data = dexscreener.get_token_data(token_id)
            if token_data:
                if attempt > 1:
                    logger.info(f"Successfully retrieved data for {symbol} on attempt {attempt}")
                return token_data
            
            if attempt < max_retries:
                logger.warning(f"No data found for {symbol}, retrying ({attempt}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                logger.warning(f"No data found for {symbol} after {max_retries} attempts")
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"Error retrieving data for {symbol}: {e}, retrying ({attempt}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to retrieve data for {symbol} after {max_retries} attempts: {e}")
                raise
    
    return None

def update_token_prices():
    """Update all token prices from DexScreener API."""
    logger.info("Starting token price update process")
    
    # Initialize database connection
    db = Database()
    token_manager = TokenEntityManager(db)
    dexscreener = DexscreenerAPI()
    
    try:
        # Retrieve all tokens from the database
        all_tokens = token_manager.get_all_tokens()
        logger.info(f"Retrieved {len(all_tokens)} tokens from database")
        
        if not all_tokens:
            logger.warning("No tokens found in database")
            return
        
        success_count = 0
        error_count = 0
        
        # Process each token
        for token in all_tokens:
            token_id = token['token_id']
            symbol = token['symbol']
            
            logger.info(f"Updating price for {symbol} ({token_id})")
            
            try:
                # Fetch latest price data from DexScreener with retry
                token_data = get_token_data_with_retry(dexscreener, token_id, symbol)
                
                if not token_data:
                    logger.warning(f"No data found for {symbol} ({token_id})")
                    error_count += 1
                    continue
                
                # Prepare update data
                # Only update price and price_24h_change, keep other fields unchanged
                update_data = {
                    'token_id': token_id,
                    'name': token['name'],  # Keep existing name
                    'symbol': token['symbol'],  # Keep existing symbol
                    'price': token_data.get('price', 0.0),
                    'price_24h_change': token_data.get('price_24h_change', 0.0),
                    'image_url': token['image_url']  # Keep existing image URL
                }
                
                # Update token in database
                if token_manager.save_token(update_data):
                    logger.info(f"Updated price for {symbol}: ${update_data['price']}")
                    success_count += 1
                else:
                    logger.error(f"Failed to update price for {symbol}")
                    error_count += 1
                
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")
                error_count += 1
        
        logger.info(f"Token price update completed. Success: {success_count}, Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Error during token price update process: {e}")
    finally:
        # Close database connection
        db.close()
        logger.info("Token price update process finished")

if __name__ == "__main__":
    update_token_prices() 