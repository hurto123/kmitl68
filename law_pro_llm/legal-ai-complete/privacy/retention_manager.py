# -*- coding: utf-8 -*-
"""
Retention Manager for Legal AI
โมดูลจัดการการเก็บและลบข้อมูล

🏆 CONTRIBUTION: Privacy feature - User data control
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import (
    STORAGE_DIR, VECTOR_DB_DIR, TEMP_DIR, DATA_DIR,
    RETENTION_DAYS, AUTO_DELETE_TEMP
)


class RetentionManager:
    """
    จัดการ Data Retention Policy สำหรับ Privacy-first design
    
    Features:
    - ลบข้อมูลตามระยะเวลา
    - ลบข้อมูลตามคำขอผู้ใช้
    - ลบ temp files
    - ล้าง vector database
    """
    
    _instance: Optional['RetentionManager'] = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.temp_dir = TEMP_DIR
        self.data_dir = DATA_DIR
        self.vector_db_dir = VECTOR_DB_DIR
        self.retention_days = RETENTION_DAYS
    
    def clear_temp_files(self) -> dict:
        """
        ลบไฟล์ temp ทั้งหมด
        
        Returns:
            dict: ผลการลบ
        """
        count = 0
        errors = []
        
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.iterdir():
                    try:
                        if file.is_file():
                            file.unlink()
                            count += 1
                        elif file.is_dir():
                            shutil.rmtree(file)
                            count += 1
                    except PermissionError:
                        errors.append(f"ไฟล์ถูกล็อค: {file.name}")
                    except Exception as e:
                        errors.append(f"{file.name}: {str(e)}")
            
            return {
                "success": True,
                "deleted_count": count,
                "errors": errors,
                "message": f"✅ ลบ temp files {count} รายการ"
            }
        except Exception as e:
            return {
                "success": False,
                "deleted_count": count,
                "errors": [str(e)],
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def clear_uploaded_files(self) -> dict:
        """
        ลบไฟล์ที่อัปโหลดทั้งหมด
        
        Returns:
            dict: ผลการลบ
        """
        count = 0
        errors = []
        
        try:
            if self.data_dir.exists():
                for file in self.data_dir.iterdir():
                    try:
                        if file.is_file():
                            file.unlink()
                            count += 1
                    except Exception as e:
                        errors.append(f"{file.name}: {str(e)}")
            
            return {
                "success": True,
                "deleted_count": count,
                "errors": errors,
                "message": f"✅ ลบไฟล์ที่อัปโหลด {count} รายการ"
            }
        except Exception as e:
            return {
                "success": False,
                "deleted_count": count,
                "errors": [str(e)],
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def clear_vector_database(self) -> dict:
        """
        ล้าง vector database ทั้งหมด
        
        Returns:
            dict: ผลการลบ
        """
        try:
            if self.vector_db_dir.exists():
                shutil.rmtree(self.vector_db_dir)
            
            self.vector_db_dir.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "message": "✅ ล้าง vector database สำเร็จ"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def clear_all_data(self) -> dict:
        """
        ลบข้อมูลทั้งหมด (Full Privacy Clear)
        
        Returns:
            dict: ผลการลบ
        """
        results = {
            "temp": self.clear_temp_files(),
            "uploads": self.clear_uploaded_files(),
            "vector_db": self.clear_vector_database()
        }
        
        all_success = all(r.get("success", False) for r in results.values())
        
        return {
            "success": all_success,
            "results": results,
            "message": "✅ ลบข้อมูลทั้งหมดสำเร็จ" if all_success else "⚠️ ลบข้อมูลบางส่วนไม่สำเร็จ"
        }
    
    def delete_old_files(self, directory: Path, days: int = None) -> dict:
        """
        ลบไฟล์ที่เก่ากว่าจำนวนวันที่กำหนด
        
        Args:
            directory: โฟลเดอร์ที่ต้องการตรวจสอบ
            days: จำนวนวัน (default จาก config)
            
        Returns:
            dict: ผลการลบ
        """
        days = days or self.retention_days
        
        if days <= 0:  # 0 = ไม่จำกัด
            return {
                "success": True,
                "deleted_count": 0,
                "message": "ไม่มีการลบ (retention = unlimited)"
            }
        
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        try:
            if not directory.exists():
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "ไม่พบโฟลเดอร์"
                }
            
            for file in directory.iterdir():
                if file.is_file():
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime < cutoff:
                        file.unlink()
                        count += 1
            
            return {
                "success": True,
                "deleted_count": count,
                "message": f"✅ ลบไฟล์เก่า {count} รายการ (>{days} วัน)"
            }
        except Exception as e:
            return {
                "success": False,
                "deleted_count": count,
                "message": f"❌ เกิดข้อผิดพลาด: {str(e)}"
            }
    
    def apply_retention_policy(self) -> dict:
        """
        ใช้ retention policy กับทุกโฟลเดอร์
        
        Returns:
            dict: ผลการใช้ policy
        """
        results = {
            "temp": self.delete_old_files(self.temp_dir, days=1),  # temp = 1 วัน
            "data": self.delete_old_files(self.data_dir, days=self.retention_days)
        }
        
        total_deleted = sum(r.get("deleted_count", 0) for r in results.values())
        
        return {
            "success": True,
            "results": results,
            "total_deleted": total_deleted,
            "message": f"✅ ใช้ retention policy สำเร็จ (ลบ {total_deleted} รายการ)"
        }
    
    def get_storage_info(self) -> dict:
        """
        ดึงข้อมูลการใช้งาน storage
        
        Returns:
            dict: ข้อมูล storage
        """
        def get_dir_size(path: Path) -> int:
            total = 0
            if path.exists():
                for file in path.rglob('*'):
                    if file.is_file():
                        try:
                            total += file.stat().st_size
                        except Exception:
                            pass
            return total
        
        def count_files(path: Path) -> int:
            if path.exists():
                return len([f for f in path.rglob('*') if f.is_file()])
            return 0
        
        def format_size(size_bytes: int) -> str:
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"
        
        temp_size = get_dir_size(self.temp_dir)
        data_size = get_dir_size(self.data_dir)
        vector_size = get_dir_size(self.vector_db_dir)
        total_size = temp_size + data_size + vector_size
        
        return {
            "temp": {
                "path": str(self.temp_dir),
                "size_bytes": temp_size,
                "size_display": format_size(temp_size),
                "file_count": count_files(self.temp_dir)
            },
            "data": {
                "path": str(self.data_dir),
                "size_bytes": data_size,
                "size_display": format_size(data_size),
                "file_count": count_files(self.data_dir)
            },
            "vector_db": {
                "path": str(self.vector_db_dir),
                "size_bytes": vector_size,
                "size_display": format_size(vector_size),
                "file_count": count_files(self.vector_db_dir)
            },
            "total": {
                "size_bytes": total_size,
                "size_display": format_size(total_size)
            },
            "retention_days": self.retention_days,
            "auto_delete_temp": AUTO_DELETE_TEMP
        }
    
    def get_storage_summary(self) -> str:
        """
        ดึงสรุป storage แบบ text
        
        Returns:
            str: สรุป storage
        """
        info = self.get_storage_info()
        
        return f"""📦 Storage Summary:
• Temp: {info['temp']['size_display']} ({info['temp']['file_count']} files)
• Data: {info['data']['size_display']} ({info['data']['file_count']} files)
• Vector DB: {info['vector_db']['size_display']}
• Total: {info['total']['size_display']}"""


def get_retention_manager() -> RetentionManager:
    """
    Get singleton instance of RetentionManager
    
    Returns:
        RetentionManager: Singleton instance
    """
    return RetentionManager()
