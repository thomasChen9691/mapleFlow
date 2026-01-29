#!/usr/bin/env python
"""Simple script to run the FastAPI backend server."""
import uvicorn
import sys

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout/stderr
    if sys.platform != "win32":
        import locale
        locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
