import logging
import sys
from typing import Dict, Any

def setup_logging(
    level: str = "INFO",
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, level),
        format=format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)