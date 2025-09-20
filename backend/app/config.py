"""Application configuration and environment variables."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class."""
    
    # API Configuration
    API_KEY = os.environ.get("API_KEY")
    SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")
    
    # Database Configuration
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    
    # Application Configuration
    APP_TITLE = "News Advisor AI Fact Checker"
    APP_VERSION = "2.0.0"
    
    # CORS Configuration
    CORS_ORIGINS = ["https://your-project.vercel.app"]
    CORS_ORIGIN_REGEX = r"https://.*\.vercel\.app"
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """Get database configuration as a dictionary."""
        return {
            "DB_NAME": cls.DB_NAME,
            "DB_USER": cls.DB_USER,
            "DB_PASSWORD": cls.DB_PASSWORD,
            "DB_HOST": cls.DB_HOST,
            "DB_PORT": cls.DB_PORT,
        }
    
    @classmethod
    def validate_config(cls) -> None:
        """Validate required configuration variables."""
        required_vars = [
            ("API_KEY", cls.API_KEY),
            ("SEARCH_ENGINE_ID", cls.SEARCH_ENGINE_ID),
            ("DB_NAME", cls.DB_NAME),
            ("DB_USER", cls.DB_USER),
            ("DB_PASSWORD", cls.DB_PASSWORD),
        ]
        
        missing_vars = [name for name, value in required_vars if not value]
        
        if missing_vars:
            print(f"WARNING: Missing required environment variables: {', '.join(missing_vars)}")
            print("Some functionality may not work correctly.")


# Create global config instance
config = Config()