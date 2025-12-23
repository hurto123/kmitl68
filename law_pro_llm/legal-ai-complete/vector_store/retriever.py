# -*- coding: utf-8 -*-
"""
Legal Retriever for RAG
โมดูลสำหรับค้นหาเอกสารที่เกี่ยวข้องกับคำถาม

🏆 CONTRIBUTION: RAG Retrieval with relevance checking
"""

from typing import List, Tuple, Optional
from langchain_core.documents import Document

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import NUM_RELEVANT_DOCS, RETRIEVAL_THRESHOLD
from vector_store.vector_db_manager import VectorDBManager


class LegalRetriever:
    """
    Retriever สำหรับระบบ RAG
    
    Features:
    - ค้นหา documents ที่เกี่ยวข้อง
    - ตรวจสอบ relevance score
    - จัดรูปแบบ context สำหรับ LLM
    """
    
    def __init__(self, vector_db: VectorDBManager = None):
        """
        Initialize Retriever
        
        Args:
            vector_db: VectorDBManager instance (optional)
        """
        self.vector_db = vector_db or VectorDBManager()
        self.default_k = NUM_RELEVANT_DOCS
        self.threshold = RETRIEVAL_THRESHOLD
    
    def retrieve(self, query: str, k: int = None) -> List[Document]:
        """
        ค้นหา k documents ที่เกี่ยวข้องกับ query
        
        Args:
            query: คำถาม/คำค้นหา
            k: จำนวน documents ที่ต้องการ
            
        Returns:
            List[Document]: รายการ documents ที่เกี่ยวข้อง
        """
        k = k or self.default_k
        return self.vector_db.similarity_search(query, k=k)
    
    def retrieve_with_scores(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """
        ค้นหา documents พร้อม relevance score
        
        Args:
            query: คำถาม/คำค้นหา
            k: จำนวน documents ที่ต้องการ
            
        Returns:
            List[Tuple[Document, float]]: รายการ (document, score)
        """
        k = k or self.default_k
        return self.vector_db.similarity_search_with_score(query, k=k)
    
    def retrieve_relevant(self, query: str, k: int = None, 
                          threshold: float = None) -> List[Document]:
        """
        ค้นหา documents ที่มี score สูงกว่า threshold
        
        Args:
            query: คำถาม/คำค้นหา
            k: จำนวน documents สูงสุด
            threshold: score ขั้นต่ำ
            
        Returns:
            List[Document]: รายการ documents ที่เกี่ยวข้อง
        """
        k = k or self.default_k
        threshold = threshold or self.threshold
        
        results_with_scores = self.retrieve_with_scores(query, k=k)
        
        # Filter by threshold (lower score = more similar for some embeddings)
        # ChromaDB returns distance, so lower is better
        relevant_docs = []
        for doc, score in results_with_scores:
            # For cosine distance: 0 = identical, 2 = opposite
            # So we want score < threshold (e.g., < 1.0)
            if score < (2 - threshold):  # Convert similarity threshold to distance
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def format_context(self, docs: List[Document]) -> str:
        """
        จัดรูปแบบ documents เป็น context string สำหรับ LLM
        
        Args:
            docs: รายการ documents
            
        Returns:
            str: Formatted context
        """
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "?")
            
            context_parts.append(
                f"[เอกสาร {i}: {source} | หน้า {page}]\n{doc.page_content}"
            )
        
        return "\n\n" + "─" * 50 + "\n\n".join(context_parts)
    
    def format_context_with_numbers(self, docs: List[Document]) -> Tuple[str, List[dict]]:
        """
        จัดรูปแบบ context พร้อม source references
        
        Args:
            docs: รายการ documents
            
        Returns:
            Tuple[str, List[dict]]: (context, sources)
        """
        if not docs:
            return "", []
        
        context_parts = []
        sources = []
        
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "?")
            
            context_parts.append(
                f"[{i}] {doc.page_content}"
            )
            
            sources.append({
                "index": i,
                "source": source,
                "page": page
            })
        
        context = "\n\n".join(context_parts)
        
        return context, sources
    
    def get_context_for_llm(self, query: str, k: int = None) -> Tuple[str, bool]:
        """
        ดึง context สำหรับส่งให้ LLM (Main function)
        
        Args:
            query: คำถาม
            k: จำนวน documents
            
        Returns:
            Tuple[str, bool]: (context, has_relevant_docs)
        """
        k = k or self.default_k
        
        # Get documents
        docs = self.retrieve(query, k=k)
        
        if not docs:
            return "", False
        
        # Format context
        context = self.format_context(docs)
        
        return context, True
    
    def has_documents(self) -> bool:
        """
        ตรวจสอบว่ามี documents ใน database หรือไม่
        
        Returns:
            bool: True ถ้ามี documents
        """
        return self.vector_db.get_document_count() > 0
    
    def get_sources(self) -> List[str]:
        """
        ดึงรายชื่อ sources ทั้งหมด
        
        Returns:
            List[str]: รายชื่อ sources
        """
        return self.vector_db.get_all_sources()


def get_retriever(vector_db: VectorDBManager = None) -> LegalRetriever:
    """
    Get LegalRetriever instance
    
    Args:
        vector_db: VectorDBManager instance (optional)
        
    Returns:
        LegalRetriever: Retriever instance
    """
    return LegalRetriever(vector_db)
