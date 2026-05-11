# #!/usr/bin/env python3
# """
# Start script for RGUKT ChatBot API
# Run from the backend/ directory: python run.py
# """

# import uvicorn
# import os
# import sys
# from pathlib import Path

# # Ensure backend/ is on sys.path
# sys.path.insert(0, str(Path(__file__).parent))


# def main():
#     print("🚀 Starting RGUKT ChatBot API on http://localhost:8000")

#     env_file = Path(__file__).parent / ".env"
#     if not env_file.exists():
#         print("⚠️  .env file not found! Please create backend/.env with:")
#         print("    GROQ_API_KEY=your_groq_api_key_here")
#         sys.exit(1)

#     # Check key is set
#     from dotenv import load_dotenv
#     load_dotenv(env_file)
#     if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
#         print("❌ GROQ_API_KEY is not set in backend/.env")
#         sys.exit(1)

#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info",
#     )


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
"""
Start script for RGUKT ChatBot API
"""

import uvicorn
import os
import sys
from pathlib import Path

# Ensure backend/ is on sys.path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    # For Railway, use environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting RGUKT ChatBot API on 0.0.0.0:{port}")

    # Load .env if it exists (local development)
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    # For Railway: GROQ_API_KEY is set as env variable
    # For local: read from .env file
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print("⚠️  GROQ_API_KEY not set! Please set it as an environment variable.")
        if env_file.exists():
            sys.exit(1)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Don't reload in production
        log_level="info",
    )


if __name__ == "__main__":
    main()