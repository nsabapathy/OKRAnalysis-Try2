"""
Configuration Management
Centralized configuration loading from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    """Application configuration"""
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "125"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")
    
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "./data/okr_results.db")
    
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "8000"))
    
    OKR_DATA_PATH: str = os.getenv("OKR_DATA_PATH", "./data/okr_samples_500.txt")
    PROCESSED_DATA_PATH: str = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY not set in .env file")
            return False
        
        if not Path(cls.OKR_DATA_PATH).exists():
            print(f"❌ OKR data file not found: {cls.OKR_DATA_PATH}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("Configuration:")
        print(f"  Model: {cls.GEMINI_MODEL}")
        print(f"  Chunks: {cls.CHUNK_SIZE} OKRs per chunk")
        print(f"  Workers: {cls.MAX_WORKERS} parallel workers")
        print(f"  Embedding: {cls.EMBEDDING_MODEL}")
        print(f"  Temperature: {cls.TEMPERATURE}")
        print(f"  Data: {cls.OKR_DATA_PATH}")
