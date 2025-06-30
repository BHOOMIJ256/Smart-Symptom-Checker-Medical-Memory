#!/usr/bin/env python3
"""
Startup script for Smart Health AI Backend
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    """Start the FastAPI server"""
    try:
        import uvicorn
        from backend.main import app
        
        print("🚀 Starting Smart Health AI Backend...")
        print("📖 API Documentation will be available at: http://localhost:8000/docs")
        print("🔍 Health check: http://localhost:8000/")
        
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 