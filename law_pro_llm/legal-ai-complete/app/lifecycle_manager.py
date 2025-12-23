# -*- coding: utf-8 -*-
"""
Lifecycle Manager for Legal AI
จัดการการเริ่มต้นและปิดโปรแกรม

Features:
- Startup initialization
- Shutdown cleanup
- Singleton management
"""

import atexit
from pathlib import Path
from typing import Optional

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import AUTO_DELETE_TEMP
from privacy.retention_manager import get_retention_manager


class LifecycleManager:
    """
    จัดการ lifecycle ของแอปพลิเคชัน
    
    - startup: เริ่มต้นระบบ
    - shutdown: ปิดระบบ (cleanup)
    """
    
    _instance: Optional['LifecycleManager'] = None
    _started: bool = False
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.retention_manager = get_retention_manager()
    
    def startup(self) -> dict:
        """
        เริ่มต้นระบบ
        
        Returns:
            dict: ข้อมูลการเริ่มต้น
        """
        if self._started:
            return {"status": "already_started"}
        
        print("🚀 Starting Legal AI...")
        
        # 1. Apply retention policy (cleanup old files)
        retention_result = self.retention_manager.apply_retention_policy()
        
        # 2. Register shutdown handler
        atexit.register(self.shutdown)
        
        self._started = True
        
        print("✅ Legal AI started successfully!")
        
        return {
            "status": "started",
            "retention_applied": retention_result.get("total_deleted", 0)
        }
    
    def shutdown(self) -> dict:
        """
        ปิดระบบและ cleanup
        
        Returns:
            dict: ข้อมูลการปิด
        """
        if not self._started:
            return {"status": "not_started"}
        
        print("🔒 Shutting down Legal AI...")
        
        # 1. Clear temp files if configured
        temp_cleared = 0
        if AUTO_DELETE_TEMP:
            result = self.retention_manager.clear_temp_files()
            temp_cleared = result.get("deleted_count", 0)
            print(f"   ✅ Cleared {temp_cleared} temp files")
        
        self._started = False
        
        print("👋 Legal AI shutdown complete!")
        
        return {
            "status": "shutdown",
            "temp_cleared": temp_cleared
        }
    
    def is_running(self) -> bool:
        """
        ตรวจสอบว่าระบบกำลังทำงานอยู่หรือไม่
        
        Returns:
            bool: True ถ้ากำลังทำงาน
        """
        return self._started
    
    def get_status(self) -> dict:
        """
        ดึงสถานะของ lifecycle
        
        Returns:
            dict: สถานะ
        """
        return {
            "running": self._started,
            "auto_delete_temp": AUTO_DELETE_TEMP
        }


# Singleton instance
_lifecycle_manager: Optional[LifecycleManager] = None


def get_lifecycle_manager() -> LifecycleManager:
    """
    Get singleton instance of LifecycleManager
    
    Returns:
        LifecycleManager: Singleton instance
    """
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager


def startup() -> dict:
    """
    Convenience function: เริ่มต้นระบบ
    
    Returns:
        dict: ข้อมูลการเริ่มต้น
    """
    return get_lifecycle_manager().startup()


def shutdown() -> dict:
    """
    Convenience function: ปิดระบบ
    
    Returns:
        dict: ข้อมูลการปิด
    """
    return get_lifecycle_manager().shutdown()
