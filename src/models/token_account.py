"""
Token account model for managing wallet-token relationships in the database.
"""

import logging
from typing import Dict, Any, List, Optional
import psycopg2

from src.db.database import Database

logger = logging.getLogger(__name__)

class TokenAccountManager:
    """
    Manager class for TokenAccount operations in the database.
    """
    
    def __init__(self, db: Database):
        """
        Initialize token account manager.
        
        Args:
            db (Database): Database connection handler
        """
        self.db = db
        self.table_name = "token_accounts"
    
    def create_table_if_not_exists(self) -> bool:
        """
        Create the token_accounts table if it doesn't exist.
        
        Returns:
            bool: True if successful
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            token_id SERIAL PRIMARY KEY,
            wallet_address TEXT NOT NULL,
            token_mint VARCHAR(255) NOT NULL,
            balance NUMERIC(38,0) NOT NULL,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT,
            decimals INTEGER,
            UNIQUE(wallet_address, token_mint)
        );
        """
        
        try:
            self.db.execute_query(query)
            logger.info(f"Ensured {self.table_name} table exists")
            return True
        except Exception as e:
            logger.error(f"Error creating {self.table_name} table: {e}")
            raise
    
    def save_token_account(self, token_account: Dict[str, Any]) -> bool:
        """
        Save token account data to the database.
        
        Args:
            token_account (Dict): Token account data to save
            
        Returns:
            bool: True if successful
        """
        # Ensure required fields are present
        required_fields = ['wallet_address', 'token_mint', 'balance', 'decimals']
        for field in required_fields:
            if field not in token_account:
                logger.error(f"Missing required field '{field}' in token account data")
                return False
        
        try:            
            # Insert or update token account using UPSERT
            query = f"""
            INSERT INTO {self.table_name} 
            (wallet_address, token_mint, balance, symbol, decimals)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (wallet_address, token_mint) 
            DO UPDATE SET 
                balance = EXCLUDED.balance,
                symbol = EXCLUDED.symbol,
                decimals = EXCLUDED.decimals,
                last_updated = CURRENT_TIMESTAMP
            """
            
            params = (
                token_account['wallet_address'],
                token_account['token_mint'],
                token_account['balance'],
                token_account.get('symbol'),
                token_account['decimals']
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Saved token account for wallet {token_account['wallet_address']} and token {token_account['token_mint']}")
            return True
        except Exception as e:
            logger.error(f"Error in save_token_account: {e}")
            return False
    
    def clean_up_removed_tokens(self, wallet_address: str, current_token_mints: List[str]) -> int:
        """
        Remove token accounts for tokens that are no longer in the wallet.
        
        Args:
            wallet_address (str): The wallet address
            current_token_mints (List[str]): List of token mints currently in the wallet
            
        Returns:
            int: Number of records removed
        """
        try:
            # Convert list to tuple for SQL IN clause
            # Handle empty list case - if no tokens, we'd remove all
            if not current_token_mints:
                return 0
                
            # Format the list of token mints for SQL IN clause
            placeholders = ','.join(['%s'] * len(current_token_mints))
            
            # Delete tokens that aren't in the current list
            query = f"""
            DELETE FROM {self.table_name}
            WHERE wallet_address = %s
            AND token_mint NOT IN ({placeholders})
            RETURNING token_id
            """
            
            # Build parameters with wallet_address first, then all token_mints
            params = [wallet_address] + current_token_mints
            
            result = self.db.execute_query(query, tuple(params))
            removed_count = len(result) if result else 0
            
            if removed_count > 0:
                logger.info(f"Removed {removed_count} tokens no longer in wallet {wallet_address}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error in clean_up_removed_tokens: {e}")
            return 0
    
    def get_token_accounts_by_wallet(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Get all token accounts for a specific wallet.
        
        Args:
            wallet_address (str): Wallet address to retrieve token accounts for
            
        Returns:
            List[Dict]: List of token account information dictionaries
        """
        query = f"""
        SELECT ta.token_id, ta.wallet_address, ta.token_mint, ta.balance, ta.last_updated, 
               ta.symbol, ta.decimals, te.name, te.price
        FROM {self.table_name} ta
        LEFT JOIN token_entity te ON ta.token_mint = te.token_id
        WHERE ta.wallet_address = %s
        ORDER BY ta.token_id;
        """
        
        try:
            result = self.db.execute_query(query, (wallet_address,))
            
            # Convert rows to dictionaries
            token_accounts = []
            for row in result:
                token_accounts.append({
                    'token_id': row[0],
                    'wallet_address': row[1],
                    'token_mint': row[2],
                    'balance': row[3],
                    'last_updated': row[4],
                    'symbol': row[5],
                    'decimals': row[6],
                    'token_name': row[7],
                    'token_price': float(row[8]) if row[8] else 0
                })
            
            return token_accounts
        except Exception as e:
            logger.error(f"Error retrieving token accounts: {e}")
            return []
    
    def token_account_exists(self, wallet_address: str, token_mint: str) -> bool:
        """
        Check if a token account exists in the database.
        
        Args:
            wallet_address (str): Wallet address
            token_mint (str): Token mint address
            
        Returns:
            bool: True if the token account exists
        """
        query = f"""
        SELECT COUNT(*) FROM {self.table_name}
        WHERE wallet_address = %s AND token_mint = %s;
        """
        
        try:
            result = self.db.execute_query(query, (wallet_address, token_mint))
            return result[0][0] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking if token account exists: {e}")
            return False 