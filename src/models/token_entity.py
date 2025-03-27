"""
Token entity model for managing token data in the database.
"""

import logging
from typing import Dict, Any, List, Optional
import psycopg2

from src.db.database import Database

logger = logging.getLogger(__name__)

class TokenEntityManager:
    """
    Manager class for TokenEntity operations in the database.
    """
    
    def __init__(self, db: Database):
        """
        Initialize token entity manager.
        
        Args:
            db (Database): Database connection handler
        """
        self.db = db
        self.table_name = "token_entity"
    
    def create_table_if_not_exists(self) -> bool:
        """
        Create the token_entity table if it doesn't exist.
        
        Returns:
            bool: True if successful
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            token_id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            symbol VARCHAR(50) NOT NULL,
            price NUMERIC(30, 10) NOT NULL,
            price_24h_change NUMERIC(30, 10),
            image_url VARCHAR(255),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.db.execute_query(query)
            logger.info(f"Ensured {self.table_name} table exists")
            return True
        except Exception as e:
            logger.error(f"Error creating {self.table_name} table: {e}")
            raise
    
    def token_exists(self, token_id: str) -> bool:
        """
        Check if a token exists in the database.
        
        Args:
            token_id (str): Token ID to check
            
        Returns:
            bool: True if the token exists
        """
        query = f"""
        SELECT COUNT(*) FROM {self.table_name}
        WHERE token_id = %s;
        """
        
        try:
            result = self.db.execute_query(query, (token_id,))
            return result[0][0] > 0 if result else False
        except Exception as e:
            logger.error(f"Error checking if token exists: {e}")
            return False
    
    def save_token(self, token_data: Dict[str, Any]) -> bool:
        """
        Save token data to the database.
        
        Args:
            token_data (Dict): Token data to save
            
        Returns:
            bool: True if successful
        """
        # Ensure required fields are present
        required_fields = ['token_id', 'name', 'symbol', 'price']
        for field in required_fields:
            if field not in token_data:
                logger.error(f"Missing required field '{field}' in token data")
                return False
        
        # Insert or update token
        query = f"""
        INSERT INTO {self.table_name} (token_id, name, symbol, price, price_24h_change, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (token_id) 
        DO UPDATE SET 
            name = EXCLUDED.name,
            symbol = EXCLUDED.symbol,
            price = EXCLUDED.price,
            price_24h_change = EXCLUDED.price_24h_change,
            image_url = EXCLUDED.image_url,
            updated_at = CURRENT_TIMESTAMP;
        """
        
        try:
            params = (
                token_data['token_id'],
                token_data['name'],
                token_data['symbol'],
                token_data['price'],
                token_data['price_24h_change'],
                token_data['image_url']
            )
            
            self.db.execute_query(query, params)
            logger.info(f"Saved token {token_data['token_id']} to database")
            return True
        except Exception as e:
            logger.error(f"Error saving token data: {e}")
            return False
    
    def get_token(self, token_id: str) -> Optional[Dict[str, Any]]:
        """
        Get token data from the database.
        
        Args:
            token_id (str): Token ID to retrieve
            
        Returns:
            Optional[Dict]: Token data or None if not found
        """
        query = f"""
        SELECT token_id, name, symbol, price, price_24h_change, image_url, updated_at
        FROM {self.table_name}
        WHERE token_id = %s;
        """
        
        try:
            result = self.db.execute_query(query, (token_id,))
            if not result:
                return None
            
            # Convert row tuple to dictionary
            row = result[0]
            return {
                'token_id': row[0],
                'name': row[1],
                'symbol': row[2],
                'price': float(row[3]),
                'price_24h_change': float(row[4]),
                'image_url': row[5],
                'updated_at': row[6]
            }
        except Exception as e:
            logger.error(f"Error retrieving token data: {e}")
            return None
    
    def get_all_tokens(self) -> List[Dict[str, Any]]:
        """
        Get all tokens from the database.
        
        Returns:
            List[Dict]: List of token data dictionaries
        """
        query = f"""
        SELECT token_id, name, symbol, price, price_24h_change, image_url, updated_at
        FROM {self.table_name}
        ORDER BY name;
        """
        
        try:
            result = self.db.execute_query(query)
            
            # Convert rows to dictionaries
            tokens = []
            for row in result:
                tokens.append({
                    'token_id': row[0],
                    'name': row[1],
                    'symbol': row[2],
                    'price': float(row[3]),
                    'price_24h_change': float(row[4]),
                    'image_url': row[5],
                    'updated_at': row[6]
                })
            
            return tokens
        except Exception as e:
            logger.error(f"Error retrieving all tokens: {e}")
            return [] 