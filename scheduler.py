#!/usr/bin/env python3
"""
Scheduler for the Solana Wallet Token Monitor.
Runs the monitor script at regular intervals.
"""

import time
import subprocess
import logging
import os
import sys
from datetime import datetime
import argparse

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
            text=True
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

def main():
    """Main scheduler function."""
    
    parser = argparse.ArgumentParser(description="Schedule wallet monitor execution")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=120, 
        help="Interval in minutes between runs (default: 120 minutes / 2 hours)"
    )
    parser.add_argument(
        "--run-now", 
        action="store_true",
        help="Run immediately, then follow schedule"
    )
    args = parser.parse_args()
    
    interval_seconds = args.interval * 60
    
    logger.info(f"Starting scheduler with {args.interval} minute interval")
    
    try:
        # Run immediately if requested
        if args.run_now:
            logger.info("Running initial execution")
            run_wallet_monitor()
        
        while True:
            # Calculate next run time
            next_run = datetime.now().timestamp() + interval_seconds
            next_run_time = datetime.fromtimestamp(next_run).strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Next execution scheduled at: {next_run_time}")
            
            # Sleep until next run
            time.sleep(interval_seconds)
            
            # Run the wallet monitor
            run_wallet_monitor()
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.exception(f"Scheduler error: {e}")

if __name__ == "__main__":
    main() 