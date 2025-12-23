# -*- coding: utf-8 -*-
"""
Vector Database Manager for Legal AI
โมดูลสำหรับจัดการ ChromaDB (Local Vector Store)

Adapted from open-source RAG architecture
"""

import shutil
from typing import List, Optional, Tuple
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import VECTOR_DB_DIR, COLLECTION_NAME, NUM_RELEVANT_DOCS
from vector_store.embedding_manager import EmbeddingManager


class VectorDBManager:
    """
    จัดการ Vector Database (ChromaDB)
    
    Features:
    - เก็บ documents เป็น vectors
    - ค้นหา similarity
    - ลบข้อมูลได้
    """
    
    _instance: Optional['VectorDBManager'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.persist_directory = str(VECTOR_DB_DIR)
        self.collection_name = COLLECTION_NAME
        self.embedding_function = EmbeddingManager.get_embedding_model()
        self.db = None
        self._load_db()
        self._initialized = True
    
    def _load_db(self):
        """Initialize or load ChromaDB"""
        try:
            self.db = Chroma(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            print(f"⚠️ Error loading ChromaDB: {e}")
            # Try to create new
            self.db = Chroma(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function
            )
    
    def add_documents(self, documents: List[Document]) -> int:
        """
        เพิ่ม documents เข้า database
        
        Args:
            documents: รายการ documents
            
        Returns:
            int: จำนวน documents ที่เพิ่ม
        """
        if not documents:
            print("⚠️ No documents to add!")
            return 0
        
        print(f"📥 Adding {len(documents)} documents to vector store...")
        
        # Debug: Show sample content
        for i, doc in enumerate(documents[:2]):
            content_preview = doc.page_content[:150].replace('\n', ' ')
            print(f"   Chunk {i+1}: {len(doc.page_content)} chars - '{content_preview}...'")
        
        try:
            self.db.add_documents(documents)
            print(f"✅ Successfully added {len(documents)} documents!")
            print(f"   Total documents in DB: {self.get_document_count()}")
            return len(documents)
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return 0
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        ค้นหา documents ที่คล้ายกับ query
        
        Args:
            query: คำค้นหา
            k: จำนวน documents ที่ต้องการ
            
        Returns:
            List[Document]: รายการ documents ที่เกี่ยวข้อง
        """
        k = k or NUM_RELEVANT_DOCS
        
        print(f"🔍 Searching for: '{query[:50]}...' (k={k})")
        print(f"   Documents in DB: {self.get_document_count()}")
        
        try:
            results = self.db.similarity_search(query, k=k)
            print(f"   Found {len(results)} relevant documents")
            for i, doc in enumerate(results[:2]):
                content_preview = doc.page_content[:100].replace('\n', ' ')
                print(f"   Result {i+1}: '{content_preview}...'")
            return results
        except Exception as e:
            print(f"❌ Error searching: {e}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """
        ค้นหา documents พร้อม relevance score
        
        Args:
            query: คำค้นหา
            k: จำนวน documents ที่ต้องการ
            
        Returns:
            List[Tuple[Document, float]]: รายการ (document, score)
        """
        k = k or NUM_RELEVANT_DOCS
        
        try:
            results = self.db.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"❌ Error searching with score: {e}")
            return []
    
    def get_retriever(self, k: int = None):
        """
        สร้าง retriever object สำหรับใช้กับ LangChain
        
        Args:
            k: จำนวน documents ที่ต้องการ
            
        Returns:
            Retriever: LangChain retriever
        """
        k = k or NUM_RELEVANT_DOCS
        return self.db.as_retriever(search_kwargs={"k": k})
    
    def get_document_count(self) -> int:
        """
        นับจำนวน documents ใน database
        
        Returns:
            int: จำนวน documents
        """
        try:
            collection = self.db._collection
            return collection.count()
        except Exception:
            return 0
    
    def get_all_sources(self) -> List[str]:
        """
        ดึงรายชื่อ sources ทั้งหมดที่มีใน database
        
        Returns:
            List[str]: รายชื่อ sources
        """
        try:
            collection = self.db._collection
            results = collection.get(include=["metadatas"])
            
            sources = set()
            for metadata in results.get("metadatas", []):
                if metadata and "source" in metadata:
                    sources.add(metadata["source"])
            
            return list(sources)
        except Exception:
            return []
    
    def delete_by_source(self, source_name: str) -> bool:
        """
        ลบ documents ตาม source name
        
        Args:
            source_name: ชื่อ source ที่ต้องการลบ
            
        Returns:
            bool: สำเร็จหรือไม่
        """
        try:
            collection = self.db._collection
            
            # Get IDs with matching source
            results = collection.get(
                where={"source": source_name},
                include=["metadatas"]
            )
            
            ids_to_delete = results.get("ids", [])
            
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                return True
            
            return False
        except Exception as e:
            print(f"❌ Error deleting by source: {e}")
            return False
    
    def clear_database(self) -> bool:
        """
        ล้างข้อมูลทั้งหมดใน database
        
        Returns:
            bool: สำเร็จหรือไม่
        """
        try:
            # Delete the persist directory
            db_path = Path(self.persist_directory)
            if db_path.exists():
                shutil.rmtree(db_path)
            
            # Recreate directory
            db_path.mkdir(parents=True, exist_ok=True)
            
            # Reinitialize
            self._initialized = False
            self.__init__()
            
            return True
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        ดึงสถิติของ database
        
        Returns:
            dict: สถิติต่างๆ
        """
        return {
            "document_count": self.get_document_count(),
            "sources": self.get_all_sources(),
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name
        }


def get_vector_db() -> VectorDBManager:
    """
    Get singleton instance of VectorDBManager
    
    Returns:
        VectorDBManager: Singleton instance
    """
    return VectorDBManager()
