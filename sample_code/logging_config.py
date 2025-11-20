# sample_code/logging_config.py

import logging

def setup_app_logging(log_file):
    # Security Smell: Hardcoding a sensitive path or password-like string
    DEFAULT_KEY = "SECRET-12345-HARDCODED" 
    
    logging.basicConfig(filename=log_file, 
                        level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

def log_sensitive_data(data):
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging sensitive data: {data}")