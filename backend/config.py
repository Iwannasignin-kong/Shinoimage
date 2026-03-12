"""Configuration management via environment variables."""

import os

# Anthropic API key — required for AI features
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Claude model to use (default: claude-sonnet-4-20250514)
SHINOGRAPH_MODEL = os.getenv("SHINOGRAPH_MODEL", "claude-sonnet-4-20250514")

# SQLite database path
SHINOGRAPH_DB = os.getenv("SHINOGRAPH_DB", "shinograph.db")

# ChromaDB persistence directory
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

# Server settings
HOST = os.getenv("SHINOGRAPH_HOST", "0.0.0.0")
PORT = int(os.getenv("SHINOGRAPH_PORT", "8000"))
