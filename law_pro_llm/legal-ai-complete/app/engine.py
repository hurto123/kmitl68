# -*- coding: utf-8 -*-
"""
Legal AI RAG Engine
โมดูลหลักสำหรับระบบ RAG (Retrieval-Augmented Generation)

🏆 CONTRIBUTION: Main RAG Engine that forces LLM to use document context
"""

from typing import List, Tuple, Optional
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import NUM_RELEVANT_DOCS
from llm.ollama_client import OllamaClient, get_ollama_client
from llm.prompt_templates import (
    BASIC_QA_PROMPT,
    LEGAL_SUMMARY_PROMPT,
    THAI_LEGAL_PROMPT,
    NO_CONTEXT_PROMPT,
    LOW_RELEVANCE_PROMPT,
    SYSTEM_PROMPT_DISCLAIMER,
    get_prompt_template,
    format_response_with_disclaimer
)
from ingestion.file_loader import FileLoader
from vector_store.vector_db_manager import VectorDBManager, get_vector_db
from vector_store.retriever import LegalRetriever, get_retriever


class LegalAIEngine:
    """
    RAG Engine สำหรับวิเคราะห์เอกสารกฎหมาย
    
    🎯 หัวใจของระบบ:
    - รับเอกสาร → แปลงเป็น vectors → เก็บใน ChromaDB
    - รับคำถาม → ค้นหา context → ส่งให้ LLM พร้อม context
    - LLM ตอบจาก context เท่านั้น (ไม่เดา)
    
    Features:
    - Document ingestion pipeline
    - RAG chat function
    - Document summarization
    - Source tracking
    """
    
    _instance: Optional['LegalAIEngine'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize components
        self.file_loader = FileLoader()
        self.vector_db = get_vector_db()
        self.retriever = get_retriever(self.vector_db)
        self.llm_client = get_ollama_client()
        self.llm = self.llm_client.get_llm()
        
        self._initialized = True
    
    # =========================================================================
    # Document Ingestion
    # =========================================================================
    
    def ingest_file(self, file_path: str) -> dict:
        """
        ประมวลผลไฟล์: Upload → Load → Split → Embed → Store
        
        Args:
            file_path: path ของไฟล์
            
        Returns:
            dict: ผลการประมวลผล
        """
        try:
            # 1. Process file (load, split, clean)
            result = self.file_loader.process_file(file_path)
            
            if not result["success"]:
                return result
            
            # 2. Add to vector database
            chunks = result["chunks"]
            num_added = self.vector_db.add_documents(chunks)
            
            return {
                "success": True,
                "message": f"✅ ประมวลผลสำเร็จ: {result['file_name']}",
                "file_name": result["file_name"],
                "num_chunks": num_added,
                "total_documents": self.vector_db.get_document_count()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}",
                "error": str(e)
            }
    
    def ingest_multiple_files(self, file_paths: List[str]) -> dict:
        """
        ประมวลผลหลายไฟล์
        
        Args:
            file_paths: รายการ paths
            
        Returns:
            dict: ผลการประมวลผล
        """
        results = []
        total_chunks = 0
        
        for file_path in file_paths:
            result = self.ingest_file(file_path)
            results.append(result)
            if result.get("success"):
                total_chunks += result.get("num_chunks", 0)
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "success": success_count > 0,
            "message": f"✅ ประมวลผลสำเร็จ {success_count}/{len(file_paths)} ไฟล์",
            "total_chunks": total_chunks,
            "results": results
        }
    
    # =========================================================================
    # RAG Chat (หัวใจของระบบ)
    # =========================================================================
    
    def chat(self, question: str, prompt_type: str = "qa") -> dict:
        """
        RAG Chat: ถาม-ตอบจากเอกสาร
        
        🎯 Flow:
        1. ตรวจสอบว่ามีเอกสารหรือไม่
        2. ค้นหาเอกสารที่เกี่ยวข้อง (Retrieval)
        3. สร้าง Prompt ที่มี context
        4. ส่งให้ LLM (LLM เห็นทั้ง context และคำถาม)
        5. LLM ตอบจาก context
        
        Args:
            question: คำถาม
            prompt_type: ประเภท prompt (qa, summary, term, analysis, thai)
            
        Returns:
            dict: คำตอบและข้อมูลเพิ่มเติม
        """
        try:
            # 1. Check if we have documents
            print(f"\n💬 Chat query: '{question[:50]}...'")
            
            if not self.retriever.has_documents():
                print("⚠️ No documents in database!")
                return {
                    "success": False,
                    "answer": NO_CONTEXT_PROMPT,
                    "sources": [],
                    "has_context": False
                }
            
            # 2. Retrieve relevant documents
            print(f"🔍 Retrieving {NUM_RELEVANT_DOCS} relevant documents...")
            docs = self.retriever.retrieve(question, k=NUM_RELEVANT_DOCS)
            
            if not docs:
                print("⚠️ No relevant documents found!")
                return {
                    "success": False,
                    "answer": LOW_RELEVANCE_PROMPT.format(question=question),
                    "sources": [],
                    "has_context": False
                }
            
            print(f"✅ Found {len(docs)} relevant documents")
            
            # 3. Format context
            context = self.retriever.format_context(docs)
            
            # Debug: Show context preview
            print(f"📋 Context length: {len(context)} chars")
            print(f"   Context preview: '{context[:300].replace(chr(10), ' ')}...'")
            
            # Extract sources for reference
            sources = []
            for doc in docs:
                sources.append({
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page", "?")
                })
            
            # 4. Get prompt template
            prompt_template = get_prompt_template(prompt_type)
            prompt = ChatPromptTemplate.from_template(prompt_template)
            
            # 5. Create chain and invoke LLM with retry
            import time
            
            print("🤖 Sending to LLM...")
            chain = prompt | self.llm | StrOutputParser()
            
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = chain.invoke({
                        "context": context,
                        "question": question
                    })
                    break  # Success, exit loop
                except Exception as e:
                    print(f"⚠️ LLM attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(3)  # Wait before retry
                    else:
                        raise
            
            print(f"✅ Got response: {len(response)} chars")
            
            # 6. Add disclaimer
            final_response = format_response_with_disclaimer(response)
            
            return {
                "success": True,
                "answer": final_response,
                "sources": sources,
                "has_context": True,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"❌ เกิดข้อผิดพลาด: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def chat_simple(self, question: str) -> str:
        """
        RAG Chat แบบง่าย - ส่งคืนแค่คำตอบ
        
        Args:
            question: คำถาม
            
        Returns:
            str: คำตอบ
        """
        result = self.chat(question)
        return result.get("answer", "เกิดข้อผิดพลาด")
    
    # =========================================================================
    # Document Summarization
    # =========================================================================
    
    def summarize(self, source_name: str = None) -> dict:
        """
        สรุปเอกสาร
        
        Args:
            source_name: ชื่อ source ที่ต้องการสรุป (None = ทั้งหมด)
            
        Returns:
            dict: ผลการสรุป
        """
        try:
            # Get all relevant chunks
            if source_name:
                query = f"สรุปเนื้อหาทั้งหมดของ {source_name}"
            else:
                query = "สรุปเนื้อหาทั้งหมดของเอกสาร"
            
            # Retrieve more docs for summarization
            docs = self.retriever.retrieve(query, k=10)
            
            if not docs:
                return {
                    "success": False,
                    "summary": "⚠️ ไม่พบเอกสารที่จะสรุป",
                    "sources": []
                }
            
            # Format context
            context = self.retriever.format_context(docs)
            
            # Use summary prompt
            prompt = ChatPromptTemplate.from_template(LEGAL_SUMMARY_PROMPT)
            chain = prompt | self.llm | StrOutputParser()
            
            summary = chain.invoke({"context": context})
            
            # Get sources
            sources = list(set(
                doc.metadata.get("source", "unknown") for doc in docs
            ))
            
            return {
                "success": True,
                "summary": summary,
                "sources": sources,
                "num_chunks_used": len(docs)
            }
            
        except Exception as e:
            return {
                "success": False,
                "summary": f"❌ เกิดข้อผิดพลาด: {str(e)}",
                "error": str(e)
            }
    
    # =========================================================================
    # System Status
    # =========================================================================
    
    def get_status(self) -> dict:
        """
        ดึงสถานะของระบบ
        
        Returns:
            dict: สถานะระบบ
        """
        ollama_status = self.llm_client.get_status()
        db_stats = self.vector_db.get_stats()
        
        return {
            "ollama": ollama_status,
            "vector_db": db_stats,
            "has_documents": self.retriever.has_documents(),
            "sources": self.retriever.get_sources()
        }
    
    def get_sources(self) -> List[str]:
        """
        ดึงรายชื่อ sources ทั้งหมด
        
        Returns:
            List[str]: รายชื่อ sources
        """
        return self.retriever.get_sources()
    
    def get_document_count(self) -> int:
        """
        นับจำนวน documents
        
        Returns:
            int: จำนวน documents
        """
        return self.vector_db.get_document_count()
    
    # =========================================================================
    # Data Management
    # =========================================================================
    
    def clear_all_data(self) -> dict:
        """
        ลบข้อมูลทั้งหมด
        
        Returns:
            dict: ผลการลบ
        """
        try:
            success = self.vector_db.clear_database()
            return {
                "success": success,
                "message": "✅ ลบข้อมูลทั้งหมดสำเร็จ" if success else "❌ ลบข้อมูลไม่สำเร็จ"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def delete_source(self, source_name: str) -> dict:
        """
        ลบข้อมูลตาม source
        
        Args:
            source_name: ชื่อ source ที่ต้องการลบ
            
        Returns:
            dict: ผลการลบ
        """
        try:
            success = self.vector_db.delete_by_source(source_name)
            return {
                "success": success,
                "message": f"✅ ลบ {source_name} สำเร็จ" if success else f"⚠️ ไม่พบ {source_name}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }


# Factory function
def get_engine() -> LegalAIEngine:
    """
    Get singleton instance of LegalAIEngine
    
    Returns:
        LegalAIEngine: Singleton instance
    """
    return LegalAIEngine()
