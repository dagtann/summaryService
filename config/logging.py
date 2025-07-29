import logging
import logging.config
import os
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration for the application"""
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": os.getenv("LOG_FILE", "logs/summary_service.log"),
                "mode": "a"
            }
        },
        "loggers": {
            "src": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"]
        }
    }
    
    # Create logs directory if it doesn't exist
    log_file = config["handlers"]["file"]["filename"]
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    logging.config.dictConfig(config)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)