"""Configuration management via environment variables."""

import os

# AI Provider (OpenAI-compatible: DashScope/智谱 etc.)
API_KEY = os.getenv("API_KEY", "")
PROVIDER_BASE_URL = os.getenv("PROVIDER_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# Model settings
SHINOGRAPH_MODEL = os.getenv("SHINOGRAPH_MODEL", "qwen-vl-plus")          # 视觉模型（解析截图）
SHINOGRAPH_TEXT_MODEL = os.getenv("SHINOGRAPH_TEXT_MODEL", "qwen-plus")    # 文本模型（问答/解析文本）

# SQLite database path
SHINOGRAPH_DB = os.getenv("SHINOGRAPH_DB", "shinograph.db")

# ChromaDB persistence directory
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

# Server settings
HOST = os.getenv("SHINOGRAPH_HOST", "0.0.0.0")
PORT = int(os.getenv("SHINOGRAPH_PORT", "8000"))
