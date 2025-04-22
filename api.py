#!/usr/bin/env python3
"""
Solana Wallet Token Monitor API

Provides API endpoints to:
- Get tokens for a specific wallet
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from src.db.database import Database
from src.solana.wallet import SolanaWallet
from src.dexscreener.api import DexscreenerAPI
from src.models.token_entity import TokenEntityManager
from src.models.token_account import TokenAccountManager
from src.logger.logger import Logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = Logger()

# Initialize FastAPI app
app = FastAPI(
    title="Solana Wallet Token Monitor API",
    description="API to monitor and retrieve token information for Solana wallets",
    version="1.0.0"
)

class AddWalletResponse(BaseModel):
    """Response model for adding a wallet"""
    status: str
    message: str

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"status": "ok", "message": "Solana Wallet Token Monitor API is running"}

@app.get("/wallet/{wallet_address}/tokens", response_model=AddWalletResponse)
def get_wallet_tokens(wallet_address: str):
    """
    Get all tokens for a specific wallet
    
    Args:
        wallet_address: The Solana wallet address to query
        
    Returns:
        List of tokens with their details
    """
    try:
        # Initialize components
        db = Database()
        token_manager = TokenEntityManager(db)
        token_account_manager = TokenAccountManager(db)
        solana_wallet = SolanaWallet()
        dexscreener = DexscreenerAPI()
        
        # Ensure tables exist
        token_manager.create_table_if_not_exists()
        token_account_manager.create_table_if_not_exists()
        
        # Get all tokens from the wallet
        tokens = solana_wallet.get_tokens(wallet_address)
        logger.info(f"Found {len(tokens)} tokens in wallet {wallet_address}")
        
        # Keep track of current token mints for cleanup later
        current_token_mints = []
        
        for token in tokens:
            token_mint = token['token_id']
            token_balance = token['amount']
            token_decimals = token.get('decimals', 0)
            
            # Add to current tokens list
            current_token_mints.append(token_mint)
            
            # Token information to be returned
            token_info = {
                'token_mint': token_mint,
                'balance': token_balance,
                'decimals': token_decimals,
                'symbol': 'UNKNOWN',
                'name': None,
                'price_usd': None
            }
            
            # Check if token exists in database
            if not token_manager.token_exists(token_mint):
                logger.info(f"Token {token_mint} not found in database, fetching from Dexscreener")
                
                # Fetch token data from Dexscreener
                token_data = dexscreener.get_token_data(token_mint)
                
                if token_data:
                    # Save token data to database
                    token_manager.save_token(token_data)
                    logger.info(f"Saved token {token_data['name']} ({token_data['symbol']}) to database")
                    
                    # Update token info for response
                    token_info['symbol'] = token_data['symbol']
                    token_info['name'] = token_data.get('name')
                    token_info['price_usd'] = token_data.get('priceUsd')
                    
                    # Create token account record
                    token_account = {
                        'wallet_address': wallet_address,
                        'token_mint': token_mint,
                        'balance': token_balance,
                        'symbol': token_data['symbol'],
                        'decimals': token_decimals
                    }
                    
                    # Save token account to database
                    token_account_manager.save_token_account(token_account)
                else:
                    logger.warning(f"Could not fetch data for token {token_mint} from Dexscreener")
            else:
                # Get the token info from our database
                db_token_info = token_manager.get_token(token_mint)
                if db_token_info:
                    # Update token info for response
                    token_info['symbol'] = db_token_info['symbol']
                    token_info['name'] = db_token_info.get('name')
                    token_info['price_usd'] = db_token_info.get('priceUsd')
                    
                    # Create token account record
                    token_account = {
                        'wallet_address': wallet_address,
                        'token_mint': token_mint,
                        'balance': token_balance,
                        'symbol': db_token_info['symbol'],
                        'decimals': token_decimals
                    }
                    
                    # Save token account to database
                    token_account_manager.save_token_account(token_account)
        
        # Clean up tokens no longer in the wallet
        token_account_manager.clean_up_removed_tokens(wallet_address, current_token_mints)
        
        # Close database connection
        db.close()
        
        return {
            "status": "success",
            "message": f"Tokens fetched successfully for wallet {wallet_address}"
        }
        
    except Exception as e:
        logger.exception(f"Error processing wallet {wallet_address}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing wallet: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True) 