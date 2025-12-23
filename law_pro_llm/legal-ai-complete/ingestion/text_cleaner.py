# -*- coding: utf-8 -*-
"""
Text Cleaner for Legal AI
โมดูลสำหรับทำความสะอาด text จากเอกสาร

Adapted from open-source RAG architecture
"""

import re
from typing import Optional


class TextCleaner:
    """
    ทำความสะอาด text จากเอกสารกฎหมาย
    
    Features:
    - ลบ whitespace เกิน
    - ลบอักขระพิเศษ
    - แก้ปัญหา OCR (เบื้องต้น)
    - Normalize unicode
    """
    
    def __init__(self):
        # Pattern สำหรับลบ
        self.patterns_to_remove = [
            r'\x00',  # Null character
            r'\x0c',  # Form feed
            r'\r',    # Carriage return
        ]
        
        # Pattern สำหรับแทนที่
        self.patterns_to_replace = [
            (r'[ \t]+', ' '),        # Multiple spaces/tabs → single space
            (r'\n{3,}', '\n\n'),     # Multiple newlines → double newline
            (r'\.{4,}', '...'),      # Multiple dots → ellipsis
            (r'-{3,}', '---'),       # Multiple dashes → hr
        ]
    
    def remove_special_chars(self, text: str) -> str:
        """
        ลบอักขระพิเศษที่ไม่ต้องการ
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            str: ข้อความที่ลบอักขระพิเศษแล้ว
        """
        for pattern in self.patterns_to_remove:
            text = re.sub(pattern, '', text)
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            str: ข้อความที่ normalize แล้ว
        """
        for pattern, replacement in self.patterns_to_replace:
            text = re.sub(pattern, replacement, text)
        
        # Strip leading/trailing whitespace from each line
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        
        return '\n'.join(lines)
    
    def fix_common_ocr_errors(self, text: str) -> str:
        """
        แก้ปัญหา OCR ที่พบบ่อย (เบื้องต้น)
        
        Args:
            text: ข้อความที่อาจมี OCR errors
            
        Returns:
            str: ข้อความที่แก้ไขแล้ว
        """
        # Common OCR mistakes (Thai)
        ocr_fixes = [
            (r'ํา', 'ำ'),      # Fix Thai sara am
            (r'เเ', 'แ'),     # Fix Thai mai ek
        ]
        
        for wrong, correct in ocr_fixes:
            text = re.sub(wrong, correct, text)
        
        return text
    
    def remove_page_numbers(self, text: str) -> str:
        """
        ลบเลขหน้าที่อาจปนมา
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            str: ข้อความที่ลบเลขหน้าแล้ว
        """
        # Pattern: standalone numbers at start/end of lines
        text = re.sub(r'^\d{1,3}\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*หน้า\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*Page\s*\d+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        return text
    
    def remove_headers_footers(self, text: str) -> str:
        """
        ลบ headers/footers ที่ซ้ำ (เบื้องต้น)
        
        Args:
            text: ข้อความต้นฉบับ
            
        Returns:
            str: ข้อความที่ลบ headers/footers แล้ว
        """
        # Remove common footer patterns
        patterns = [
            r'^\s*-\s*\d+\s*-\s*$',  # - 1 -
            r'^\s*\[\s*\d+\s*\]\s*$',  # [ 1 ]
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        
        return text
    
    def clean(self, text: str, 
              remove_page_numbers: bool = True,
              fix_ocr: bool = True) -> str:
        """
        ทำความสะอาด text ครบวงจร (Main function)
        
        Args:
            text: ข้อความต้นฉบับ
            remove_page_numbers: ลบเลขหน้าหรือไม่
            fix_ocr: แก้ปัญหา OCR หรือไม่
            
        Returns:
            str: ข้อความที่ทำความสะอาดแล้ว
        """
        if not text:
            return ""
        
        # 1. Remove special characters
        text = self.remove_special_chars(text)
        
        # 2. Fix OCR errors
        if fix_ocr:
            text = self.fix_common_ocr_errors(text)
        
        # 3. Remove page numbers
        if remove_page_numbers:
            text = self.remove_page_numbers(text)
            text = self.remove_headers_footers(text)
        
        # 4. Normalize whitespace
        text = self.normalize_whitespace(text)
        
        # 5. Final trim
        text = text.strip()
        
        return text
    
    def get_text_stats(self, text: str) -> dict:
        """
        ดึงสถิติของ text
        
        Args:
            text: ข้อความ
            
        Returns:
            dict: สถิติต่างๆ
        """
        if not text:
            return {
                "char_count": 0,
                "word_count": 0,
                "line_count": 0,
                "paragraph_count": 0
            }
        
        return {
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": text.count('\n') + 1,
            "paragraph_count": text.count('\n\n') + 1
        }
