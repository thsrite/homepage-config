#!/usr/bin/env python3
"""
Homepage Configuration Tool - Development Server
Run this script to start the web application
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def main():
    """Start the FastAPI development server"""
    # Get configuration from environment variables
    port = int(os.getenv("PORT", "9835"))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    reload = debug or os.getenv("RELOAD", "true").lower() == "true"

    print("=" * 60)
    print("  Homepage Configuration Tool")
    print("=" * 60)
    print()
    print("Starting server...")
    print(f"Open your browser and navigate to: http://localhost:{port}")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 60)

    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(backend_path)] if reload else None,
        log_level="debug" if debug else "info"
    )

if __name__ == "__main__":
    main()