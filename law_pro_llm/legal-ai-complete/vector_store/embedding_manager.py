# -*- coding: utf-8 -*-
"""
Embedding Manager for Legal AI
โมดูลสำหรับสร้าง embeddings ผ่าน Ollama

Adapted from open-source RAG architecture
"""

from typing import List, Optional
from langchain_ollama import OllamaEmbeddings

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import EMBEDDING_MODEL, OLLAMA_BASE_URL


class EmbeddingManager:
    """
    จัดการ Embeddings ผ่าน Ollama (Local-only)
    
    ใช้ model: nomic-embed-text
    """
    
    _instance: Optional['EmbeddingManager'] = None
    _embedding_model = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._embedding_model is None:
            self._embedding_model = OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url=OLLAMA_BASE_URL
            )
    
    @classmethod
    def get_embedding_model(cls) -> OllamaEmbeddings:
        """
        Get embedding model instance (Singleton)
        
        Returns:
            OllamaEmbeddings: Embedding model
        """
        if cls._embedding_model is None:
            cls._embedding_model = OllamaEmbeddings(
                model=EMBEDDING_MODEL,
                base_url=OLLAMA_BASE_URL
            )
        return cls._embedding_model
    
    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        """
        สร้าง embeddings สำหรับหลาย documents (with retry)
        
        Args:
            texts: รายการ text ที่ต้องการ embed
            
        Returns:
            List[List[float]]: รายการ embeddings
        """
        import time
        
        model = cls.get_embedding_model()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return model.embed_documents(texts)
            except Exception as e:
                print(f"⚠️ Embedding attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    raise
    
    @classmethod
    def embed_query(cls, text: str) -> List[float]:
        """
        สร้าง embedding สำหรับ query (with retry)
        
        Args:
            text: query text
            
        Returns:
            List[float]: embedding vector
        """
        import time
        
        model = cls.get_embedding_model()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return model.embed_query(text)
            except Exception as e:
                print(f"⚠️ Query embedding attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                else:
                    raise
    
    @classmethod
    def check_connection(cls) -> bool:
        """
        ตรวจสอบว่า embedding model ทำงานได้
        
        Returns:
            bool: True ถ้าทำงานได้
        """
        try:
            model = cls.get_embedding_model()
            # Test with a simple query
            result = model.embed_query("test")
            return len(result) > 0
        except Exception:
            return False
    
    @classmethod
    def get_embedding_dimension(cls) -> int:
        """
        ดึงขนาด dimension ของ embedding
        
        Returns:
            int: จำนวน dimensions
        """
        try:
            result = cls.embed_query("test")
            return len(result)
        except Exception:
            return 768  # Default dimension for nomic-embed-text
