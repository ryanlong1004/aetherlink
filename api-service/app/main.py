"""
Main FastAPI application for AetherLink Network Monitor
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import network

# Create FastAPI app
app = FastAPI(
    title="AetherLink API",
    description="Network monitoring API service for AetherLink dashboard",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - adjust origins as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(network.router)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "name": "AetherLink API",
        "version": "0.1.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
