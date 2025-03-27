"""
Solana wallet module for retrieving token information.
"""

import os
import logging
import time
from typing import List, Dict, Any
import json
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class SolanaWallet:
    """
    Class for interacting with Solana blockchain to retrieve wallet token data.
    """
    
    # Wrapped SOL token address (used for representing native SOL)
    WRAPPED_SOL_ADDRESS = "So11111111111111111111111111111111111111112"
    
    def __init__(self):
        """Initialize Solana RPC client."""
        self.rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.timeout = int(os.getenv('SOLANA_RPC_TIMEOUT', '30'))
        self.retry_limit = int(os.getenv('SOLANA_RETRY_LIMIT', '3'))
        self.retry_delay = int(os.getenv('SOLANA_RETRY_DELAY', '5'))
        logger.info(f"Initialized Solana RPC client with URL: {self.rpc_url}")
    
    def _make_rpc_request(self, payload):
        """
        Make an RPC request to Solana with retry mechanism.
        
        Args:
            payload (dict): RPC request payload
            
        Returns:
            dict: Response data or empty dict if failed
        """
        attempts = 0
        last_error = None
        
        while attempts < self.retry_limit:
            try:
                attempts += 1
                
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
                    last_error = result['error']
                    # Wait before retry
                    if attempts < self.retry_limit:
                        logger.warning(f"Retrying in {self.retry_delay} seconds (attempt {attempts}/{self.retry_limit})")
                        time.sleep(self.retry_delay)
                        continue
                    return {}
                
                # Success
                return result
                
            except RequestException as e:
                last_error = str(e)
                logger.warning(f"Solana RPC connection error (attempt {attempts}/{self.retry_limit}): {e}")
                if attempts < self.retry_limit:
                    logger.warning(f"Retrying in {self.retry_delay} seconds")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to Solana RPC after {self.retry_limit} attempts")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Unexpected error in RPC request: {e}")
                if attempts < self.retry_limit:
                    logger.warning(f"Retrying in {self.retry_delay} seconds")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed after {self.retry_limit} attempts")
        
        logger.error(f"All retry attempts failed. Last error: {last_error}")
        return {}
    
    def get_sol_balance(self, wallet_address: str) -> float:
        """
        Get the native SOL balance of a wallet.
        
        Args:
            wallet_address (str): Solana wallet address
            
        Returns:
            float: SOL balance in SOL units (not lamports)
        """
        # Build Solana RPC request for getBalance
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [
                wallet_address
            ]
        }
        
        result = self._make_rpc_request(payload)
        
        if not result or 'result' not in result:
            logger.error(f"Failed to get SOL balance for wallet {wallet_address}")
            return 0.0
        
        # Extract balance in lamports
        lamports = result.get('result', {}).get('value', 0)
        
        # Convert lamports to SOL (1 SOL = 10^9 lamports)
        sol_balance = lamports / 1_000_000_000
        
        logger.info(f"SOL balance for wallet {wallet_address}: {sol_balance} SOL")
        return sol_balance
    
    def get_tokens(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get all token accounts for a wallet address.
        
        Args:
            wallet_address (str): Solana wallet address
            
        Returns:
            List[Dict]: List of token information dictionaries
        """
        tokens = []
        
        # Get native SOL balance
        sol_balance = self.get_sol_balance(wallet_address)
        
        # Only add SOL if there's a non-zero balance
        if sol_balance > 0:
            tokens.append({
                'token_id': self.WRAPPED_SOL_ADDRESS,  # Use wrapped SOL address for compatibility
                'amount': sol_balance,
                'decimals': 9,  # SOL has 9 decimals
                'is_native_sol': True  # Flag to indicate this is native SOL
            })
            logger.info(f"Added native SOL token with balance {sol_balance} SOL")
        
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
        
        result = self._make_rpc_request(payload)
        
        if not result or 'result' not in result:
            logger.error(f"Failed to get tokens for wallet {wallet_address}")
            return tokens  # Still return any SOL balance we found
        
        # Extract token accounts from response
        token_accounts = result.get('result', {}).get('value', [])
        logger.info(f"Found {len(token_accounts)} token accounts for wallet {wallet_address}")
        
        # Format token information
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
                
                # Skip wrapped SOL if we already added native SOL
                # This avoids double-counting SOL
                if token_id == self.WRAPPED_SOL_ADDRESS and any(t.get('is_native_sol', False) for t in tokens):
                    logger.info(f"Skipping wrapped SOL token as native SOL is already included")
                    continue
                
                # Get token amount and decimals
                token_amount = token_data.get('tokenAmount', {})
                ui_amount = token_amount.get('uiAmount', 0)
                decimals = token_amount.get('decimals', 0)
                
                tokens.append({
                    'token_id': token_id,
                    'amount': ui_amount,
                    'decimals': decimals
                })
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing token account data: {e}")
                continue
        
        return tokens
    
    def get_token_metadata(self, token_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific token.
        
        Args:
            token_id (str): Token mint address
            
        Returns:
            Dict: Token metadata or empty dict if not found
        """
        # Handle special case for wrapped SOL
        if token_id == self.WRAPPED_SOL_ADDRESS:
            return {
                'token_id': token_id,
                'decimals': 9,
                'name': 'Solana',
                'symbol': 'SOL'
            }
            
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
        
        result = self._make_rpc_request(payload)
        
        if not result or 'result' not in result:
            logger.error(f"Failed to get metadata for token {token_id}")
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