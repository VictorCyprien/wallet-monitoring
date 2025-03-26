"""
Dexscreener API module for retrieving token information.
"""

import logging
import time
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class DexscreenerAPI:
    """
    Class for interacting with the Dexscreener API to get token data.
    """
    
    def __init__(self):
        """Initialize Dexscreener API client."""
        self.base_url = "https://api.dexscreener.com/latest/dex"
        self.timeout = 30
        self.retry_limit = 3
        self.retry_delay = 2  # seconds
        
        logger.info("Initialized Dexscreener API client")
    
    def get_token_data(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get token data from Dexscreener.
        
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
                url = f"{self.base_url}/search?q={token_id}"
                
                # Make request to Dexscreener API
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Extract token information from the response
                pairs = data.get('pairs', [])
                if not pairs:
                    logger.warning(f"No token data found for {token_id}")
                    return None
                
                # Use the first pair that matches our token
                for pair in pairs:
                    if pair.get('chainId') == 'solana' and (
                        pair.get('baseToken', {}).get('address') == token_id or 
                        pair.get('quoteToken', {}).get('address') == token_id
                    ):
                        # Determine which token in the pair is our target
                        if pair.get('baseToken', {}).get('address') == token_id:
                            token_info = pair.get('baseToken', {})
                        else:
                            token_info = pair.get('quoteToken', {})
                        
                        # Format token data for storage
                        token_data = {
                            'token_id': token_id,
                            'name': token_info.get('name', 'Unknown'),
                            'symbol': token_info.get('symbol', 'UNKNOWN'),
                            'price': float(token_info.get('price', 0))
                        }
                        
                        logger.info(f"Retrieved data for token {token_data['name']} ({token_data['symbol']})")
                        return token_data
                
                # If we reach here, no matching token was found
                logger.warning(f"Token {token_id} found on Dexscreener but no matching Solana token")
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