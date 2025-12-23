# -*- coding: utf-8 -*-
"""
Main Window for Legal AI GUI
หน้าหลัก Gradio Interface

Concept adapted from: JARVIS-Chatbot
Modified for: Legal Document Analysis
"""

import gradio as gr
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import APP_TITLE, APP_DESCRIPTION, SERVER_HOST, SERVER_PORT

# Note: GUI panel imports are done lazily inside create_main_window() to avoid initialization issues


# Custom CSS for Legal theme
CUSTOM_CSS = """
.legal-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    text-align: center;
}
.legal-title {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
}
.legal-subtitle {
    font-size: 14px;
    opacity: 0.9;
}
.privacy-badge {
    display: inline-block;
    background-color: #28a745;
    color: white;
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 12px;
    margin: 5px;
}
.badge-blue {
    background-color: #17a2b8;
}
.badge-purple {
    background-color: #6f42c1;
}
.footer-text {
    text-align: center;
    padding: 20px;
    color: #666;
    font-size: 12px;
    border-top: 1px solid #eee;
    margin-top: 20px;
}
.disclaimer {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 10px 15px;
    margin: 10px 0;
    color: #856404;
}
"""


def create_main_window():
    """
    สร้างหน้าต่างหลักของ Legal AI
    
    Returns:
        gr.Blocks: Gradio application
    """
    # Lazy imports to avoid initialization issues
    from gui.chat_panel import create_chat_interface
    from gui.settings_panel import create_settings_panel
    
    with gr.Blocks(
        title=APP_TITLE,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green"
        )
    ) as app:
        
        # =====================================================================
        # Header
        # =====================================================================
        gr.HTML(f"""
        <div class="legal-header">
            <div class="legal-title">⚖️ {APP_TITLE}</div>
            <div class="legal-subtitle">{APP_DESCRIPTION}</div>
            <div style="margin-top: 15px;">
                <span class="privacy-badge">🔒 Local-only</span>
                <span class="privacy-badge badge-blue">📄 Privacy-first</span>
                <span class="privacy-badge badge-purple">🤖 Ollama</span>
            </div>
            <div class="legal-subtitle" style="margin-top: 10px; font-size: 11px;">
                💡 อัปโหลดเอกสารของคุณ → ถามคำถาม → AI ตอบจากเอกสารเท่านั้น
            </div>
        </div>
        """)
        
        # =====================================================================
        # Main Content
        # =====================================================================
        with gr.Row():
            # Left Sidebar - Settings (25%)
            with gr.Column(scale=1, min_width=280):
                settings_components = create_settings_panel()
            
            # Main Content - Chat (75%)
            with gr.Column(scale=3):
                chat_components = create_chat_interface()
        
        # =====================================================================
        # Footer
        # =====================================================================
        gr.HTML("""
        <div class="footer-text">
            <p class="disclaimer">
                ⚠️ <strong>คำเตือน:</strong> คำตอบเป็นเพียงข้อมูลเพื่อการศึกษา ไม่ถือเป็นคำปรึกษาทางกฎหมาย
                กรุณาปรึกษาทนายความหรือผู้เชี่ยวชาญสำหรับกรณีจริง
            </p>
            <p>
                💻 ข้อมูลทั้งหมดประมวลผลในเครื่องของคุณ | ไม่ส่งข้อมูลออกนอกเครื่อง
            </p>
            <p style="color: #999; font-size: 11px;">
                Legal AI Complete | Powered by Ollama & LangChain
            </p>
        </div>
        """)
    
    return app


def launch_app(share: bool = False):
    """
    เปิดใช้งาน Legal AI Application
    
    Args:
        share: แชร์ออก public หรือไม่ (default: False เพื่อ privacy)
    """
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║             ⚖️  Legal AI Complete - เริ่มต้นระบบ             ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🌐 URL: http://{SERVER_HOST}:{SERVER_PORT}                          ║
    ║  🔒 Mode: Local-only (ไม่ส่งข้อมูลออกนอกเครื่อง)              ║
    ║  📄 Privacy: Auto-cleanup enabled                            ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📋 วิธีใช้:                                                  ║
    ║  1. อัปโหลดเอกสาร PDF                                        ║
    ║  2. รอประมวลผล                                               ║
    ║  3. ถามคำถามเกี่ยวกับเอกสาร                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    app = create_main_window()
    app.launch(
        server_name=SERVER_HOST,
        server_port=SERVER_PORT,
        share=share,  # False for privacy
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    launch_app()
