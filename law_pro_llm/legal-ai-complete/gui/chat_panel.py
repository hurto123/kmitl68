# -*- coding: utf-8 -*-
"""
Chat Panel for Legal AI GUI
แผงแชทสำหรับถาม-ตอบ

Adapted from JARVIS Chatbot concept
"""

import gradio as gr
from typing import List, Tuple
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Note: engine is imported lazily inside create_chat_interface() to avoid initialization issues


def create_chat_interface():
    """
    สร้าง Chat Interface
    
    Returns:
        dict: Gradio components
    """
    # Lazy import to avoid circular dependencies and initialization issues
    from app.engine import get_engine
    engine = get_engine()
    
    # =========================================================================
    # Chat Functions
    # =========================================================================
    
    def process_upload(file):
        """ประมวลผลไฟล์ที่อัปโหลด"""
        if file is None:
            return "⚠️ กรุณาเลือกไฟล์", get_sources_display()
        
        result = engine.ingest_file(file.name)
        
        if result.get("success"):
            status = f"""✅ **อัปโหลดสำเร็จ!**
            
📄 ไฟล์: {result.get('file_name')}
📊 Chunks: {result.get('num_chunks')} ชิ้น
📚 รวมเอกสารทั้งหมด: {result.get('total_documents')} ชิ้น

💡 พร้อมถาม-ตอบแล้ว!"""
        else:
            status = f"❌ {result.get('message', 'เกิดข้อผิดพลาด')}"
        
        return status, get_sources_display()
    
    def get_sources_display():
        """ดึงรายชื่อเอกสารที่โหลดแล้ว"""
        sources = engine.get_sources()
        if not sources:
            return "📄 ยังไม่มีเอกสาร"
        
        display = "📄 **เอกสารที่โหลดแล้ว:**\n"
        for i, source in enumerate(sources, 1):
            display += f"\n{i}. ✅ {source}"
        
        return display
    
    def chat_response(message, history):
        """ตอบคำถามจากเอกสาร"""
        if not message.strip():
            return history, ""
        
        # Get response from RAG engine
        result = engine.chat(message)
        
        answer = result.get("answer", "เกิดข้อผิดพลาด")
        
        # Add source info if available
        sources = result.get("sources", [])
        if sources and result.get("success"):
            source_text = "\n\n📌 **แหล่งอ้างอิง:**\n"
            unique_sources = list(set(s["source"] for s in sources))
            for src in unique_sources:
                source_text += f"• {src}\n"
            answer += source_text
        
        # Add to history using new Gradio message format
        history = history or []
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": answer})
        
        return history, ""
    
    def summarize_docs():
        """สรุปเอกสาร"""
        result = engine.summarize()
        
        if result.get("success"):
            summary = result.get("summary", "")
            sources = result.get("sources", [])
            
            response = f"📝 **สรุปเอกสาร:**\n\n{summary}"
            
            if sources:
                response += "\n\n📌 **เอกสารที่ใช้:**\n"
                for src in sources:
                    response += f"• {src}\n"
            
            return response
        else:
            return result.get("summary", "❌ ไม่สามารถสรุปได้")
    
    def clear_chat():
        """ล้างประวัติแชท"""
        return [], ""
    
    # =========================================================================
    # Gradio Components
    # =========================================================================
    
    with gr.Column():
        # Header
        gr.Markdown("""
        ## 💬 ถาม-ตอบจากเอกสาร
        
        อัปโหลดเอกสาร PDF แล้วถามคำถามได้เลย
        """)
        
        # Upload Section
        with gr.Row():
            with gr.Column(scale=3):
                file_upload = gr.File(
                    label="📤 อัปโหลดเอกสาร",
                    file_types=[".pdf", ".txt", ".docx"],
                    file_count="single"
                )
            with gr.Column(scale=1):
                upload_btn = gr.Button("📥 ประมวลผล", variant="primary")
        
        # Status
        with gr.Row():
            with gr.Column(scale=2):
                upload_status = gr.Markdown("📄 รอการอัปโหลดเอกสาร...")
            with gr.Column(scale=1):
                sources_display = gr.Markdown(get_sources_display())
        
        gr.Markdown("---")
        
        # Chat Area
        chatbot = gr.Chatbot(
            label="💬 ประวัติการสนทนา",
            height=400
        )
        
        # Input Area
        with gr.Row():
            msg_input = gr.Textbox(
                label="❓ พิมพ์คำถามของคุณ",
                placeholder="เช่น: มาตรา 15 พูดถึงอะไร?",
                lines=2,
                scale=4
            )
            send_btn = gr.Button("📝 ถาม", variant="primary", scale=1)
        
        # Action Buttons
        with gr.Row():
            summarize_btn = gr.Button("📜 สรุปเอกสาร", variant="secondary")
            clear_btn = gr.Button("🗑️ ล้างแชท", variant="secondary")
        
        # Summary Output
        summary_output = gr.Markdown(visible=False)
    
    # =========================================================================
    # Event Handlers
    # =========================================================================
    
    # Upload
    upload_btn.click(
        fn=process_upload,
        inputs=[file_upload],
        outputs=[upload_status, sources_display]
    )
    
    # Chat
    send_btn.click(
        fn=chat_response,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    )
    
    msg_input.submit(
        fn=chat_response,
        inputs=[msg_input, chatbot],
        outputs=[chatbot, msg_input]
    )
    
    # Summarize
    def show_summary():
        summary = summarize_docs()
        return gr.update(value=summary, visible=True)
    
    summarize_btn.click(
        fn=show_summary,
        outputs=[summary_output]
    )
    
    # Clear
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, msg_input]
    )
    
    return {
        "file_upload": file_upload,
        "upload_btn": upload_btn,
        "upload_status": upload_status,
        "sources_display": sources_display,
        "chatbot": chatbot,
        "msg_input": msg_input,
        "send_btn": send_btn,
        "summarize_btn": summarize_btn,
        "clear_btn": clear_btn,
        "summary_output": summary_output
    }
