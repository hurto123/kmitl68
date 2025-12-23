# -*- coding: utf-8 -*-
"""
Configuration settings for Legal AI System
ไฟล์ตั้งค่าสำหรับระบบ AI วิเคราะห์เอกสารกฎหมาย

Adapted from open-source RAG architecture
"""

import os
from pathlib import Path

# =============================================================================
# Base Paths
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
VECTOR_DB_DIR = STORAGE_DIR / "vector_db"
TEMP_DIR = STORAGE_DIR / "temp"
DATA_DIR = STORAGE_DIR / "data"

# สร้างโฟลเดอร์ที่จำเป็น
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# LLM Settings (Ollama - Local Only)
# =============================================================================
LLM_MODEL_TYPE = "ollama"  # Fixed: Local-only, no cloud
LLM_MODEL_NAME = "llama3.2"  # Default model, can be changed
OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama URL

# Available models (for GUI selection)
AVAILABLE_MODELS = [
    "llama3.2",
    "llama3.2:1b",
    "gemma2:2b",
    "gemma2:9b",
    "qwen2.5:3b",
    "qwen2.5:7b",
]

# =============================================================================
# Embedding Settings
# =============================================================================
EMBEDDING_MODEL = "nomic-embed-text"  # Local embedding via Ollama

# =============================================================================
# RAG Settings
# =============================================================================
CHUNK_SIZE = 1000  # ขนาด chunk สำหรับแบ่งเอกสาร
CHUNK_OVERLAP = 100  # overlap ระหว่าง chunks
NUM_RELEVANT_DOCS = 4  # จำนวน documents ที่ดึงมาตอบคำถาม
RETRIEVAL_THRESHOLD = 0.3  # threshold สำหรับ similarity score

# =============================================================================
# Privacy Settings
# =============================================================================
AUTO_DELETE_TEMP = True  # ลบ temp files เมื่อปิดโปรแกรม
RETENTION_DAYS = 30  # จำนวนวันที่เก็บข้อมูล (0 = ไม่จำกัด)
SAVE_ORIGINAL_FILES = False  # ไม่เก็บไฟล์ต้นฉบับ (privacy-first)

# =============================================================================
# GUI Settings
# =============================================================================
APP_TITLE = "Legal AI - ระบบวิเคราะห์เอกสารกฎหมาย"
APP_DESCRIPTION = "ระบบ AI สำหรับวิเคราะห์และตอบคำถามจากเอกสารกฎหมาย (Local-first)"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7860

# =============================================================================
# Supported File Types
# =============================================================================
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".docx"]

# =============================================================================
# Collection Name for Vector DB
# =============================================================================
COLLECTION_NAME = "legal_documents"

# =============================================================================
# LLM Temperature Settings
# =============================================================================
LLM_TEMPERATURE = 0.3  # Low temp for legal accuracy (0.0 - 1.0)

# =============================================================================
# Logging Settings
# =============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
