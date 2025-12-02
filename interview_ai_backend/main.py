"""FastAPI application for the Interview AI MVP."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import interview


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="Interview AI Backend",
        description="Backend APIs for the interview coaching MVP",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update with explicit origins before production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(interview.router, prefix="/api")

    @app.get("/")
    async def root() -> dict:
        return {"status": "ok", "message": "Interview AI backend is running"}

    return app


app = create_app()
