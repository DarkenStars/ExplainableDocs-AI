"""Application factory for the News Advisor AI Fact Checker."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import config
from .database.connection import db_pool
from .database.db_manager import get_conn, put_conn, setup_database
from .routes.api import router as api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Validate configuration
    config.validate_config()

    # Create FastAPI app
    app = FastAPI(
        title=config.APP_TITLE,
        version=config.APP_VERSION
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_origin_regex=config.CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(api_router)

    # Lifespan events
    @app.on_event("startup")
    async def startup_event():
        """Initialize database connection and setup on startup."""
        # Initialize database pool
        db_pool.initialize(config.get_db_config())

        # Setup database tables
        conn = get_conn()
        if conn:
            try:
                setup_database(conn)
                print("Database ready.")
            except Exception as e:
                print(f"Database setup error: {e}")
            finally:
                put_conn(conn)

        print("FastAPI started.")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up database connections on shutdown."""
        db_pool.close_all()
        print("Application shutdown complete.")

    return app


# Create app instance
app = create_app()