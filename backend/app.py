"""
Refactored News Advisor AI Fact Checker using modular FastAPI application.
This file now serves as the main entry point that imports the modular application.

The application has been refactored into the following modular structure:
- app/config.py: Configuration and environment variables
- app/models/schemas.py: Pydantic data models
- app/database/: Database operations and connection management
- app/services/: Business logic services (fact-checking, search, analysis)
- app/utils/: Utility functions and helpers
- app/routes/: API route handlers
- app/main.py: Application factory and FastAPI setup
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI on http://0.0.0.0:5000 ...")
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)