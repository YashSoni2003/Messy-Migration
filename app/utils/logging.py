import logging
import sys
from datetime import datetime

def setup_logging():
    """Configure application logging."""
    
    logger = logging.getLogger('user_management')
    logger.setLevel(logging.INFO)
    

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def log_api_request(endpoint, method, user_id=None, success=True, error=None):
    """Log API requests for monitoring."""
    logger = logging.getLogger('user_management')
    
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'endpoint': endpoint,
        'method': method,
        'user_id': user_id,
        'success': success
    }
    
    if success:
        logger.info(f"API Request: {method} {endpoint} - Success")
    else:
        logger.error(f"API Request: {method} {endpoint} - Error: {error}")

app_logger = setup_logging()
