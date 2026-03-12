#!/usr/bin/env python3
"""ShinoGraph — Quick start script."""

import sys
import os

def main():
    # Check for .env file
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    # Check API key
    if not os.getenv("API_KEY"):
        print("ERROR: API_KEY not set.")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your API key")
        print("  Or: export API_KEY=sk-xxx")
        sys.exit(1)

    import uvicorn
    from backend.config import HOST, PORT

    print(f"Starting ShinoGraph on http://{HOST}:{PORT}")
    print(f"  API docs: http://localhost:{PORT}/docs")
    print(f"  Health:   http://localhost:{PORT}/health")
    print(f"  Provider: {os.getenv('PROVIDER_BASE_URL', 'dashscope')}")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)


if __name__ == "__main__":
    main()
