"""
Solana wallet module for retrieving token information.
"""

import os
import logging
from typing import List, Dict, Any
import json
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class SolanaWallet:
    """
    Class for interacting with Solana blockchain to retrieve wallet token data.
    """
    
    def __init__(self):
        """Initialize Solana RPC client."""
        self.rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.timeout = int(os.getenv('SOLANA_RPC_TIMEOUT', '30'))
        logger.info(f"Initialized Solana RPC client with URL: {self.rpc_url}")
    
    def get_tokens(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get all token accounts for a wallet address.
        
        Args:
            wallet_address (str): Solana wallet address
            
        Returns:
            List[Dict]: List of token information dictionaries
        """
        try:
            # Build Solana RPC request for getTokenAccountsByOwner
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {
                        "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Solana Token Program ID
                    },
                    {
                        "encoding": "jsonParsed"
                    }
                ]
            }
            
            # Make request to Solana RPC
            response = requests.post(
                self.rpc_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            if 'error' in result:
                logger.error(f"Solana RPC error: {result['error']}")
                return []
            
            # Extract token accounts from response
            token_accounts = result.get('result', {}).get('value', [])
            logger.info(f"Found {len(token_accounts)} token accounts for wallet {wallet_address}")
            
            # Format token information
            tokens = []
            for account in token_accounts:
                try:
                    token_data = account.get('account', {}).get('data', {}).get('parsed', {}).get('info', {})
                    
                    # Skip accounts with zero balance
                    if float(token_data.get('tokenAmount', {}).get('uiAmount', 0)) <= 0:
                        continue
                    
                    # Extract token mint address (contract address)
                    token_id = token_data.get('mint')
                    if not token_id:
                        continue
                    
                    tokens.append({
                        'token_id': token_id,
                        'amount': token_data.get('tokenAmount', {}).get('uiAmount', 0)
                    })
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error parsing token account data: {e}")
                    continue
            
            return tokens
            
        except RequestException as e:
            logger.error(f"Error connecting to Solana RPC: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_tokens: {e}")
            return []
    
    def get_token_metadata(self, token_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific token.
        
        Args:
            token_id (str): Token mint address
            
        Returns:
            Dict: Token metadata or empty dict if not found
        """
        try:
            # Build Solana RPC request for getAccountInfo
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getAccountInfo",
                "params": [
                    token_id,
                    {
                        "encoding": "jsonParsed"
                    }
                ]
            }
            
            # Make request to Solana RPC
            response = requests.post(
                self.rpc_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            if 'error' in result:
                logger.error(f"Solana RPC error retrieving token metadata: {result['error']}")
                return {}
            
            # Extract token info
            account_info = result.get('result', {}).get('value', {})
            if not account_info:
                return {}
            
            # Basic token metadata (minimal information)
            return {
                'token_id': token_id,
                'decimals': account_info.get('data', {}).get('parsed', {}).get('info', {}).get('decimals', 0)
            }
            
        except RequestException as e:
            logger.error(f"Error connecting to Solana RPC for token metadata: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in get_token_metadata: {e}")
            return {} 