"""
Simple wallet manager to get wallets from database.
"""

import logging
from typing import List, Dict, Any
from src.db.database import Database

logger = logging.getLogger(__name__)

class WalletManager:
    """
    Manager to get wallet addresses from the database.
    """
    
    def __init__(self, db: Database):
        """
        Initialize wallet manager.
        
        Args:
            db (Database): Database connection handler
        """
        self.db = db
        self.table_name = "wallets_to_monitor"
    
    def get_wallets(self) -> List[str]:
        """
        Get all wallet addresses from the database.
        
        Returns:
            List[str]: List of wallet addresses
        """
        query = f"""
        SELECT wallet_address FROM {self.table_name}
        """
        
        try:
            result = self.db.execute_query(query)
            
            # Extract wallet addresses from result
            wallet_addresses = [row[0] for row in result]
            
            logger.info(f"Retrieved {len(wallet_addresses)} wallet addresses from database")
            return wallet_addresses
        except Exception as e:
            logger.error(f"Error retrieving wallet addresses: {e}")
            return [] 