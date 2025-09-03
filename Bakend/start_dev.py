#!/usr/bin/env python3
"""
Development server startup script for the Trading Backend API
"""

import uvicorn
import os
from app.core.config import settings

if __name__ == "__main__":
    # Set development environment
    os.environ.setdefault("ENVIRONMENT", "development")
    
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"API Documentation will be available at: http://localhost:8000/docs")
    print(f"API Base URL: http://localhost:8000{settings.API_V1_STR}")
    print("Press CTRL+C to stop the server")
    
    # Start the development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )