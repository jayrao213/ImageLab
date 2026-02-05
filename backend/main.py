"""
PhotoApp FastAPI Backend
Main application entry point

Migrated from photoapp.py by Jay Rao
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from routes import users, images, labels, ping, edit, auth

# Configure logging (same as original photoapp.py)
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

# Create FastAPI app
app = FastAPI(
    title="PhotoApp API",
    description="Photo management API with S3 storage and Rekognition AI labeling",
    version="2.0.0"
)

# Configure CORS for frontend access
# ALLOWED_ORIGINS can be comma-separated list: "http://localhost:3000,https://imagelab.vercel.app"
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ping.router, tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(images.router, prefix="/images", tags=["Images"])
app.include_router(labels.router, prefix="/labels", tags=["Labels"])
app.include_router(edit.router, prefix="/edit", tags=["Edit"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PhotoApp API",
        "version": "2.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
