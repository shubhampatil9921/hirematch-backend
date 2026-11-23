
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.matching import router as matching_router
from app.core.resources import create_resources
from app.api.routes.resume import router as resume_router

def create_app(resource_factory=create_resources):

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Initialize shared ML resources once at application startup.
        resources = resource_factory()

        app.state.resources = resources
        app.state.matching_service = resources.matching_service

        yield

        # Release application references during shutdown.
        app.state.matching_service = None
        app.state.resources = None

    app = FastAPI(
        title="HireMatch API",
        description="AI-Powered Resume Analyzer and Job Matcher",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def home():
        return {
            "message": "Welcome to HireMatch API",
            "status": "running",
            "version": "1.0.0"
        }

    @app.get("/api/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "HireMatch Backend"
        }

    app.include_router(matching_router)
    app.include_router(resume_router)
    return app


app = create_app()
