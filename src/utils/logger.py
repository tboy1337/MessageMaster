"""
Logging utilities for SMS application
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

def setup_logger(name="sms_sender", log_level=logging.INFO):
    """
    Set up a logger with console and file handlers
    
    Args:
        name: Logger name (default: "sms_sender")
        log_level: Logging level (default: logging.INFO)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    
    # Create file handler
    log_dir = Path.home() / '.sms_sender' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = log_dir / f"sms_sender_{today}.log"
    
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name="sms_sender"):
    """
    Get an existing logger or create a new one
    
    Args:
        name: Logger name (default: "sms_sender")
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If the logger doesn't exist or has no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name)
        
    return logger 