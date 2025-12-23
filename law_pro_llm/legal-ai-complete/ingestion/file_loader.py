# -*- coding: utf-8 -*-
"""
File Loader for Legal AI
โมดูลสำหรับโหลดและประมวลผลเอกสาร (PDF, TXT, DOCX)

Adapted from open-source RAG architecture
"""

import shutil
from pathlib import Path
from typing import List, Optional

from langchain_community.document_loaders import (
    PDFPlumberLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import (
    DATA_DIR,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    SUPPORTED_EXTENSIONS
)
from ingestion.text_cleaner import TextCleaner


class FileLoader:
    """
    โหลดและประมวลผลเอกสารกฎหมาย
    
    รองรับ:
    - PDF (ใช้ PDFPlumber)
    - TXT
    - DOCX
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.text_cleaner = TextCleaner()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            add_start_index=True,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """
        ตรวจสอบว่าไฟล์รองรับหรือไม่
        
        Args:
            file_path: path ของไฟล์
            
        Returns:
            bool: True ถ้ารองรับ
        """
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS
    
    def save_upload(self, file_path: str) -> Path:
        """
        Copy ไฟล์ที่อัปโหลดไปยัง storage
        
        Args:
            file_path: path ของไฟล์ต้นฉบับ
            
        Returns:
            Path: path ของไฟล์ที่ copy ไว้
        """
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"ไม่พบไฟล์: {file_path}")
        
        target = self.data_dir / source.name
        shutil.copy2(source, target)
        
        return target
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        โหลดเอกสารตามประเภทไฟล์
        
        Args:
            file_path: path ของไฟล์
            
        Returns:
            List[Document]: รายการ documents
        """
        file_path = str(file_path)
        ext = Path(file_path).suffix.lower()
        
        print(f"📖 Loading document: {file_path}")
        print(f"   Extension: {ext}")
        
        if ext == ".pdf":
            loader = PDFPlumberLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"ไม่รองรับไฟล์ประเภท: {ext}")
        
        documents = loader.load()
        
        # Debug: Show what was loaded
        print(f"   📄 Loaded {len(documents)} pages/documents")
        for i, doc in enumerate(documents[:3]):  # Show first 3
            content_preview = doc.page_content[:200].replace('\n', ' ')
            print(f"   Page {i+1}: {len(doc.page_content)} chars - '{content_preview}...'")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        แบ่ง documents เป็น chunks
        
        Args:
            documents: รายการ documents
            
        Returns:
            List[Document]: รายการ chunks
        """
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def add_metadata(self, chunks: List[Document], source_name: str) -> List[Document]:
        """
        เพิ่ม metadata ให้แต่ละ chunk
        
        Args:
            chunks: รายการ chunks
            source_name: ชื่อไฟล์ต้นทาง
            
        Returns:
            List[Document]: chunks พร้อม metadata
        """
        for i, chunk in enumerate(chunks):
            chunk.metadata["source"] = source_name
            chunk.metadata["chunk_index"] = i
            
            # เพิ่ม page number ถ้ามี
            if "page" not in chunk.metadata:
                chunk.metadata["page"] = 1
        
        return chunks
    
    def clean_chunks(self, chunks: List[Document]) -> List[Document]:
        """
        ทำความสะอาด text ในแต่ละ chunk
        
        Args:
            chunks: รายการ chunks
            
        Returns:
            List[Document]: chunks ที่ทำความสะอาดแล้ว
        """
        cleaned_chunks = []
        for chunk in chunks:
            cleaned_content = self.text_cleaner.clean(chunk.page_content)
            if cleaned_content.strip():  # ข้าม chunks ที่ว่าง
                chunk.page_content = cleaned_content
                cleaned_chunks.append(chunk)
        
        return cleaned_chunks
    
    def load_and_split(self, file_path: str, clean: bool = True) -> List[Document]:
        """
        โหลดและแบ่งเอกสารเป็น chunks (Main function)
        
        Args:
            file_path: path ของไฟล์
            clean: ทำความสะอาด text หรือไม่
            
        Returns:
            List[Document]: รายการ chunks พร้อม metadata
        """
        # 1. Load document
        documents = self.load_document(file_path)
        
        # 2. Split into chunks
        chunks = self.split_documents(documents)
        
        # 3. Add metadata
        source_name = Path(file_path).name
        chunks = self.add_metadata(chunks, source_name)
        
        # 4. Clean text (optional)
        if clean:
            chunks = self.clean_chunks(chunks)
        
        return chunks
    
    def process_file(self, file_path: str) -> dict:
        """
        ประมวลผลไฟล์ครบวงจร: Copy → Load → Split → Clean
        
        Args:
            file_path: path ของไฟล์ต้นฉบับ
            
        Returns:
            dict: ผลการประมวลผล
        """
        try:
            # 1. Validate
            if not self.is_supported(file_path):
                return {
                    "success": False,
                    "error": f"ไม่รองรับไฟล์ประเภทนี้",
                    "chunks": []
                }
            
            # 2. Copy to storage
            saved_path = self.save_upload(file_path)
            
            # 3. Load and split
            chunks = self.load_and_split(str(saved_path))
            
            return {
                "success": True,
                "file_name": saved_path.name,
                "saved_path": str(saved_path),
                "num_chunks": len(chunks),
                "chunks": chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "chunks": []
            }
    
    def get_uploaded_files(self) -> List[dict]:
        """
        ดึงรายการไฟล์ที่อัปโหลดแล้ว
        
        Returns:
            List[dict]: รายการไฟล์
        """
        files = []
        for file_path in self.data_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "extension": file_path.suffix.lower()
                })
        
        return files
