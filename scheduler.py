#!/usr/bin/env python3
"""
Scheduler for the Solana Wallet Token Monitor.
Runs the monitor script and token price updater at regular intervals.
"""

import time
import subprocess
import logging
import os
import sys
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("scheduler")

def run_wallet_monitor():
    """Run the wallet monitor script."""
    try:
        logger.info("Starting wallet monitor execution")
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, "main.py")
        
        # Run the main script
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=True,
            text=True,
            env=os.environ.copy()  # Pass current environment variables including those from .env
        )
        
        if result.returncode == 0:
            logger.info("Wallet monitor executed successfully")
        else:
            logger.error(f"Wallet monitor execution failed with code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
        
        # Log stdout for debugging
        if result.stdout:
            logger.debug(f"Script output: {result.stdout}")
            
    except Exception as e:
        logger.exception(f"Error running wallet monitor: {e}")

def run_token_price_updater():
    """Run the token price updater script."""
    try:
        logger.info("Starting token price updater execution")
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        updater_script = os.path.join(script_dir, "update_token_prices.py")
        
        # Run the updater script
        result = subprocess.run(
            [sys.executable, updater_script],
            capture_output=True,
            text=True,
            env=os.environ.copy()  # Pass current environment variables including those from .env
        )
        
        if result.returncode == 0:
            logger.info("Token price updater executed successfully")
        else:
            logger.error(f"Token price updater execution failed with code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
        
        # Log stdout for debugging
        if result.stdout:
            logger.debug(f"Script output: {result.stdout}")
            
    except Exception as e:
        logger.exception(f"Error running token price updater: {e}")

def main():
    """Main scheduler function."""
    
    parser = argparse.ArgumentParser(description="Schedule wallet monitor and token price updater execution")
    parser.add_argument(
        "--monitor-interval", 
        type=int, 
        default=120, 
        help="Interval in minutes between wallet monitor runs (default: 120 minutes / 2 hours)"
    )
    parser.add_argument(
        "--price-interval", 
        type=int, 
        default=30, 
        help="Interval in minutes between token price updates (default: 30 minutes)"
    )
    parser.add_argument(
        "--run-now", 
        action="store_true",
        help="Run both scripts immediately, then follow schedule"
    )
    args = parser.parse_args()
    
    monitor_interval_seconds = args.monitor_interval * 60
    price_interval_seconds = args.price_interval * 60
    
    logger.info(f"Starting scheduler with wallet monitor interval: {args.monitor_interval} minutes")
    logger.info(f"Token price update interval: {args.price_interval} minutes")
    
    try:
        # Run immediately if requested
        if args.run_now:
            logger.info("Running initial execution of both scripts")
            run_wallet_monitor()
            run_token_price_updater()
        
        # Calculate next run times
        next_monitor_run = datetime.now().timestamp() + monitor_interval_seconds
        next_price_run = datetime.now().timestamp() + price_interval_seconds
        
        while True:
            # Sleep until the next scheduled task (whichever comes first)
            current_time = datetime.now().timestamp()
            next_run = min(next_monitor_run, next_price_run)
            time_to_sleep = max(0, next_run - current_time)
            
            if time_to_sleep > 0:
                next_run_time = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Next execution scheduled at: {next_run_time}")
                time.sleep(time_to_sleep)
            
            # Check which script(s) need to run
            current_time = datetime.now().timestamp()
            
            # Run wallet monitor if it's time
            if current_time >= next_monitor_run:
                run_wallet_monitor()
                next_monitor_run = current_time + monitor_interval_seconds
                next_monitor_time = datetime.fromtimestamp(next_monitor_run).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Next wallet monitor scheduled at: {next_monitor_time}")
            
            # Run token price updater if it's time
            if current_time >= next_price_run:
                run_token_price_updater()
                next_price_run = current_time + price_interval_seconds
                next_price_time = datetime.fromtimestamp(next_price_run).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"Next token price update scheduled at: {next_price_time}")
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.exception(f"Scheduler error: {e}")

if __name__ == "__main__":
    main() 