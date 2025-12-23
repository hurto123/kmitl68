# -*- coding: utf-8 -*-
"""
Settings Panel for Legal AI GUI
แผงตั้งค่าและ Privacy Controls

🏆 CONTRIBUTION: Privacy UI
"""

import gradio as gr
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Note: imports are done lazily inside create_settings_panel() to avoid initialization issues
from app.config import AVAILABLE_MODELS, LLM_MODEL_NAME


def create_settings_panel():
    """
    สร้าง Settings Panel
    
    Returns:
        dict: Gradio components
    """
    # Lazy imports to avoid circular dependencies and initialization issues
    from llm.ollama_client import get_ollama_client
    from privacy.retention_manager import get_retention_manager
    from app.engine import get_engine
    
    retention_manager = get_retention_manager()
    ollama_client = get_ollama_client()
    engine = get_engine()
    
    # =========================================================================
    # Settings Functions
    # =========================================================================
    
    def get_model_list():
        """ดึงรายชื่อ models"""
        try:
            models = ollama_client.get_available_models()
            if models:
                return models
        except Exception:
            pass
        return AVAILABLE_MODELS
    
    def change_model(model_name):
        """เปลี่ยน model"""
        try:
            ollama_client.set_model(model_name)
            return f"✅ เปลี่ยนเป็น {model_name} แล้ว"
        except Exception as e:
            return f"❌ ไม่สามารถเปลี่ยน model: {str(e)}"
    
    def get_storage_info():
        """ดึงข้อมูล storage"""
        return retention_manager.get_storage_summary()
    
    def get_system_status():
        """ดึงสถานะระบบ"""
        status = engine.get_status()
        
        ollama_status = "🟢 เชื่อมต่อแล้ว" if status["ollama"]["connected"] else "🔴 ไม่ได้เชื่อมต่อ"
        model_status = status["ollama"]["current_model"]
        doc_count = status["vector_db"]["document_count"]
        sources = status["sources"]
        
        return f"""**🔧 สถานะระบบ**

• Ollama: {ollama_status}
• Model: {model_status}
• Documents: {doc_count} chunks
• Sources: {len(sources)} ไฟล์"""
    
    def clear_temp():
        """ลบ temp files"""
        result = retention_manager.clear_temp_files()
        return result.get("message", "เสร็จสิ้น"), get_storage_info()
    
    def clear_uploads():
        """ลบไฟล์ที่อัปโหลด"""
        result = retention_manager.clear_uploaded_files()
        return result.get("message", "เสร็จสิ้น"), get_storage_info()
    
    def clear_all():
        """ลบข้อมูลทั้งหมด"""
        result = engine.clear_all_data()
        retention_result = retention_manager.clear_all_data()
        
        if result.get("success") and retention_result.get("success"):
            return "✅ ลบข้อมูลทั้งหมดสำเร็จ", get_storage_info()
        else:
            return "⚠️ ลบข้อมูลบางส่วนไม่สำเร็จ", get_storage_info()
    
    def check_ollama():
        """ตรวจสอบการเชื่อมต่อ Ollama"""
        if ollama_client.check_connection():
            models = ollama_client.get_available_models()
            return f"✅ เชื่อมต่อ Ollama สำเร็จ!\n\nModels ที่พร้อมใช้: {', '.join(models[:5])}"
        else:
            return "❌ ไม่สามารถเชื่อมต่อ Ollama\n\nกรุณาตรวจสอบว่า Ollama กำลังทำงาน (ollama serve)"
    
    # =========================================================================
    # Gradio Components
    # =========================================================================
    
    with gr.Column():
        # Model Settings
        gr.Markdown("## ⚙️ ตั้งค่า")
        
        with gr.Accordion("🤖 Model Settings", open=True):
            model_dropdown = gr.Dropdown(
                choices=get_model_list(),
                value=LLM_MODEL_NAME,
                label="เลือก Model",
                interactive=True,
                allow_custom_value=True
            )
            model_status = gr.Markdown("")
            check_btn = gr.Button("🔍 ตรวจสอบ Ollama", size="sm")
        
        gr.Markdown("---")
        
        # System Status
        with gr.Accordion("📊 สถานะระบบ", open=True):
            system_status = gr.Markdown(get_system_status())
            refresh_btn = gr.Button("🔄 รีเฟรช", size="sm")
        
        gr.Markdown("---")
        
        # Storage Info
        with gr.Accordion("📦 Storage", open=True):
            storage_info = gr.Markdown(get_storage_info())
        
        gr.Markdown("---")
        
        # Privacy Controls
        with gr.Accordion("🔒 Privacy Controls", open=True):
            gr.Markdown("""
            **ควบคุมข้อมูลของคุณ:**
            - ลบ temp files ที่ไม่จำเป็น
            - ลบไฟล์ที่อัปโหลด
            - ล้างข้อมูลทั้งหมด
            """)
            
            privacy_status = gr.Markdown("")
            
            with gr.Row():
                clear_temp_btn = gr.Button("🧹 ล้าง Temp", size="sm")
                clear_uploads_btn = gr.Button("📁 ลบไฟล์", size="sm")
            
            clear_all_btn = gr.Button(
                "🗑️ ลบข้อมูลทั้งหมด", 
                variant="stop",
                size="sm"
            )
    
    # =========================================================================
    # Event Handlers
    # =========================================================================
    
    # Model change
    model_dropdown.change(
        fn=change_model,
        inputs=[model_dropdown],
        outputs=[model_status]
    )
    
    # Check Ollama
    check_btn.click(
        fn=check_ollama,
        outputs=[model_status]
    )
    
    # Refresh status
    def refresh_all():
        return get_system_status(), get_storage_info()
    
    refresh_btn.click(
        fn=refresh_all,
        outputs=[system_status, storage_info]
    )
    
    # Privacy controls
    clear_temp_btn.click(
        fn=clear_temp,
        outputs=[privacy_status, storage_info]
    )
    
    clear_uploads_btn.click(
        fn=clear_uploads,
        outputs=[privacy_status, storage_info]
    )
    
    clear_all_btn.click(
        fn=clear_all,
        outputs=[privacy_status, storage_info]
    )
    
    return {
        "model_dropdown": model_dropdown,
        "model_status": model_status,
        "check_btn": check_btn,
        "system_status": system_status,
        "refresh_btn": refresh_btn,
        "storage_info": storage_info,
        "privacy_status": privacy_status,
        "clear_temp_btn": clear_temp_btn,
        "clear_uploads_btn": clear_uploads_btn,
        "clear_all_btn": clear_all_btn
    }
