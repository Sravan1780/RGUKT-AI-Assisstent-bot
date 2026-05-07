#!/usr/bin/env python3
"""
Start script for RGUKT ChatBot API
Run from the backend/ directory: python run.py
"""

import uvicorn
import os
import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    print("🚀 Starting RGUKT ChatBot API on http://localhost:8000")

    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found! Please create backend/.env with:")
        print("    GROQ_API_KEY=your_groq_api_key_here")
        sys.exit(1)

    # Check key is set
    from dotenv import load_dotenv
    load_dotenv(env_file)
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        print("❌ GROQ_API_KEY is not set in backend/.env")
        sys.exit(1)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
