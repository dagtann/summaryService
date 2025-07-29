import os
import uvicorn
from config.logging import setup_logging
from src.web import create_app


def main():
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    # Get Anthropic API key
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Create FastAPI app
    app = create_app(anthropic_api_key=anthropic_api_key)
    
    # Run the server
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()