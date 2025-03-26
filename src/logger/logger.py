from typing import Dict
import logging
from colorama import Fore, Style, init


init(autoreset=True)

class Logger:
    LOG_COLORS = {
        logging.DEBUG: Fore.GREEN,
        logging.INFO: Fore.BLUE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

    def __init__(self, name: str = 'Logger', level: int = logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self.ColorFormatter())
            self.logger.addHandler(handler)

    class ColorFormatter(logging.Formatter):
        def __init__(self):
            super().__init__('%(asctime)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
        
        def format(self, record):
            log_color = Logger.LOG_COLORS.get(record.levelno, Fore.WHITE)
            if isinstance(record.msg, Dict):
                record.msg = str(record.msg)
            record.msg = log_color + record.msg + Style.RESET_ALL
            return super().format(record)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

