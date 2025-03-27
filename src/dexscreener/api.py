"""
Dexscreener API module for retrieving token information.
"""

import os
import time
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException

from src.logger.logger import Logger
from src.solana.wallet import SolanaWallet

logger = Logger()

class DexscreenerAPI:
    """
    Class for interacting with the Dexscreener API to get token data.
    """
    
    def __init__(self):
        """Initialize Dexscreener API client."""
        self.base_url = "https://api.dexscreener.com"
        self.timeout = 30
        self.retry_limit = int(os.getenv('DEXSCREENER_RETRY_LIMIT', 3))
        self.retry_delay = int(os.getenv('DEXSCREENER_RETRY_DELAY', 5))  # seconds
        
        logger.info("Initialized Dexscreener API client")
    
    def get_token_data(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get token data from Dexscreener.
        
        Args:
            token_id (str): Token contract address
            
        Returns:
            Optional[Dict]: Token data dictionary or None if not found
        """
        # Special case for SOL token
        if token_id == SolanaWallet.WRAPPED_SOL_ADDRESS:
            # For SOL, we can get the price from a reliable source or hardcode it
            # Here we'll still try to get it from Dexscreener but return a fallback if not available
            logger.info("Getting data for native SOL token")
            
            # Try to get SOL price from Dexscreener
            sol_data = self._get_dexscreener_data(token_id)
            if sol_data:
                return sol_data
            
            # If Dexscreener data is not available, use a fallback
            logger.info("Using fallback data for SOL token")
            return {
                'token_id': token_id,
                'name': 'Solana',
                'symbol': 'SOL',
                'price': 0.0  # We don't have a price without Dexscreener
            }
            
        # For all other tokens, use the standard Dexscreener API
        return self._get_dexscreener_data(token_id)
    
    def _get_dexscreener_data(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get token data from Dexscreener API.
        
        Args:
            token_id (str): Token contract address
            
        Returns:
            Optional[Dict]: Token data dictionary or None if not found
        """
        tries = 0
        while tries < self.retry_limit:
            tries += 1
            try:
                # Build URL for token search
                url = f"{self.base_url}/tokens/v1/solana/{token_id}"
                
                # Make request to Dexscreener API
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # The response is an array of pairs
                pairs = data
                if not pairs or len(pairs) == 0:
                    logger.warning(f"No token data found for {token_id}")
                    return None
                
                # Find the token in either baseToken or quoteToken
                for pair in pairs:
                    base_token = pair.get('baseToken', {})
                    quote_token = pair.get('quoteToken', {})
                    
                    # Check if our token is the base token
                    if base_token.get('address') == token_id:
                        # Format token data for storage
                        price_usd = pair.get('priceUsd', 0)
                        price_usd_24h_change = pair.get('priceChange', {}).get('h24', 0)
                        token_image = pair.get('info', {}).get('imageUrl', None)
                        token_data = {
                            'token_id': token_id,
                            'name': base_token.get('name', 'Unknown'),
                            'symbol': base_token.get('symbol', 'UNKNOWN'),
                            'price': float(price_usd) if price_usd else 0,
                            'price_24h_change': float(price_usd_24h_change) if price_usd_24h_change else 0,
                            'image_url': token_image
                        }
                        
                        logger.info(f"Retrieved data for token {token_data['name']} ({token_data['symbol']})")
                        return token_data
                    
                    # Check if our token is the quote token
                    elif quote_token.get('address') == token_id:
                        # For quote tokens, we may need to calculate the price differently
                        # or use the priceUsd directly if available
                        price_usd = pair.get('priceUsd', 0)
                        token_data = {
                            'token_id': token_id,
                            'name': quote_token.get('name', 'Unknown'),
                            'symbol': quote_token.get('symbol', 'UNKNOWN'),
                            'price': float(price_usd) if price_usd else 0
                        }
                        
                        logger.info(f"Retrieved data for token {token_data['name']} ({token_data['symbol']})")
                        return token_data
                
                # If we reach here, the token was found in the API but :
                # Either the token is not listed on Dexscreener
                # Or the token is "inactive"
                logger.warning(f"Token {token_id} found on Dexscreener but in an unrecognized format")
                return None
                
            except RequestException as e:
                logger.warning(f"Error connecting to Dexscreener (attempt {tries}/{self.retry_limit}): {e}")
                if tries < self.retry_limit:
                    time.sleep(self.retry_delay)
                    continue
                return None
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing Dexscreener data: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error in get_token_data: {e}")
                return None
        
        return None 