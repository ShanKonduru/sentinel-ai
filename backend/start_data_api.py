#!/usr/bin/env python3
"""
Startup script for the Data Retrieval API
"""
import sys
import os
import uvicorn

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    # Import the app after setting up the path
    from src.api.data_retrieval.app import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )