# -*- coding: utf-8 -*-
"""
Ollama Client for Legal AI
โมดูลสำหรับเชื่อมต่อ Ollama LLM (Local-only)

Adapted from open-source RAG architecture
"""

import requests
from typing import Optional, List
from langchain_ollama import ChatOllama

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import (
    LLM_MODEL_NAME, 
    OLLAMA_BASE_URL, 
    LLM_TEMPERATURE,
    AVAILABLE_MODELS
)


class OllamaClient:
    """
    Client สำหรับเชื่อมต่อ Ollama LLM
    
    Features:
    - เชื่อมต่อ Ollama local
    - เปลี่ยน model ได้
    - ตรวจสอบ connection
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize Ollama Client
        
        Args:
            model_name: ชื่อ model ที่ต้องการใช้ (default จาก config)
        """
        self.model_name = model_name or LLM_MODEL_NAME
        self.base_url = OLLAMA_BASE_URL
        self.temperature = LLM_TEMPERATURE
        self._llm = None
    
    def get_llm(self) -> ChatOllama:
        """
        Get the LangChain ChatOllama instance
        
        Returns:
            ChatOllama: LangChain Ollama instance
        """
        if self._llm is None:
            self._llm = ChatOllama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                num_ctx=4096,  # Context window size
                timeout=120    # 2 minute timeout for slow models
            )
        return self._llm
    
    def set_model(self, model_name: str):
        """
        เปลี่ยน model ที่ใช้งาน
        
        Args:
            model_name: ชื่อ model ใหม่
        """
        self.model_name = model_name
        self._llm = None  # Reset to create new instance
    
    def set_temperature(self, temperature: float):
        """
        เปลี่ยน temperature
        
        Args:
            temperature: ค่า temperature (0.0 - 1.0)
        """
        self.temperature = max(0.0, min(1.0, temperature))
        self._llm = None  # Reset to create new instance
    
    def check_connection(self) -> bool:
        """
        ตรวจสอบว่า Ollama ทำงานอยู่หรือไม่
        
        Returns:
            bool: True ถ้าเชื่อมต่อได้
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """
        ดึงรายชื่อ models ที่มีใน Ollama
        
        Returns:
            List[str]: รายชื่อ models
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return AVAILABLE_MODELS
        except Exception:
            return AVAILABLE_MODELS
    
    def check_model_exists(self, model_name: str) -> bool:
        """
        ตรวจสอบว่า model มีอยู่ใน Ollama หรือไม่
        
        Args:
            model_name: ชื่อ model
            
        Returns:
            bool: True ถ้า model มีอยู่
        """
        available = self.get_available_models()
        return any(model_name in m for m in available)
    
    def get_status(self) -> dict:
        """
        ดึงสถานะของ Ollama
        
        Returns:
            dict: สถานะ connection และ model
        """
        connected = self.check_connection()
        models = self.get_available_models() if connected else []
        
        return {
            "connected": connected,
            "base_url": self.base_url,
            "current_model": self.model_name,
            "available_models": models,
            "model_exists": self.model_name in str(models)
        }


# Singleton instance for global access
_client_instance: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create singleton Ollama client
    
    Returns:
        OllamaClient: Singleton instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = OllamaClient()
    return _client_instance
