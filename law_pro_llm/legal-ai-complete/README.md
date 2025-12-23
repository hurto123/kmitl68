# ⚖️ Legal AI Complete

> ระบบ AI วิเคราะห์เอกสารกฎหมายแบบ **Local-first** ไม่ส่งข้อมูลออกนอกเครื่อง

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-brightgreen.svg)

---

## 📖 สารบัญ

- [Features](#-features)
- [สถาปัตยกรรมระบบ](#-สถาปัตยกรรมระบบ-system-architecture)
- [การติดตั้ง](#-การติดตั้ง-installation)
- [วิธีใช้งาน](#-วิธีใช้งาน-usage)
- [โครงสร้างโปรเจกต์](#-โครงสร้างโปรเจกต์)
- [แนวคิดการออกแบบ](#-แนวคิดการออกแบบ-design-philosophy)
- [เทคโนโลยีที่ใช้](#-เทคโนโลยีที่ใช้-tech-stack)
- [Privacy & Security](#-privacy--security)

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 📄 **Upload เอกสาร** | รองรับ PDF, TXT, DOCX |
| 💬 **RAG Chat** | ถาม-ตอบจากเอกสาร (ไม่เดา) |
| 📜 **สรุปเอกสาร** | สรุปอัตโนมัติ |
| 🔒 **Privacy-first** | ประมวลผลในเครื่อง 100% |
| 🗑️ **User Control** | ลบข้อมูลได้ทุกเมื่อ |
| 🤖 **Ollama LLM** | ใช้ LLM local (llama3.2, gemma2, etc.) |

---

## 🏗️ สถาปัตยกรรมระบบ (System Architecture)

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        🖥️ Legal AI Complete                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   📄 GUI     │    │  🔧 App      │    │  🧠 LLM      │          │
│  │   (Gradio)   │◄──►│  Engine      │◄──►│  (Ollama)    │          │
│  └──────────────┘    └──────────────┘    └──────────────┘          │
│         │                   │                                       │
│         ▼                   ▼                                       │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │ 📥 Ingestion │    │ 🗄️ Vector   │                              │
│  │ (PDF/DOCX)   │───►│   Store      │                              │
│  └──────────────┘    │ (ChromaDB)   │                              │
│                      └──────────────┘                              │
│                             │                                       │
│                      ┌──────────────┐                              │
│                      │ 🔒 Privacy   │                              │
│                      │   Manager    │                              │
│                      └──────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### RAG Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      📊 RAG Pipeline                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1️⃣ INGESTION PHASE                                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │ Upload   │───►│ Extract  │───►│ Clean &  │───►│ Create   │     │
│  │ Document │    │ Text     │    │ Chunk    │    │ Vectors  │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │                                               │            │
│       ▼                                               ▼            │
│  PDF/TXT/DOCX                                   ChromaDB           │
│                                                                     │
│  2️⃣ QUERY PHASE                                                    │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │ User     │───►│ Search   │───►│ Retrieve │───►│ Generate │     │
│  │ Question │    │ Vectors  │    │ Context  │    │ Answer   │     │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘     │
│       │                               │               │            │
│       ▼                               ▼               ▼            │
│   "มาตรา 112?"              Top-K Documents    LLM Response        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📥 การติดตั้ง (Installation)

### ความต้องการของระบบ (System Requirements)

| Component | Requirement |
|-----------|-------------|
| **OS** | Windows 10/11, macOS, Linux |
| **Python** | 3.10 หรือสูงกว่า |
| **RAM** | 8GB+ (แนะนำ 16GB สำหรับ LLM ใหญ่) |
| **Storage** | 10GB+ สำหรับ models |
| **GPU** | ไม่จำเป็น (แต่ช่วยให้เร็วขึ้น) |

### ขั้นตอนที่ 1: ติดตั้ง Ollama

Ollama เป็น runtime สำหรับรัน LLM บนเครื่อง local

**Windows/macOS:**

1. ดาวน์โหลดจาก: <https://ollama.com/download>
2. ติดตั้งตามปกติ
3. เปิด Terminal และรัน:

```bash
# ดาวน์โหลด LLM model (เลือกอย่างใดอย่างหนึ่ง)
ollama pull llama3.2          # แนะนำ - สมดุลระหว่างความเร็วและคุณภาพ
# หรือ
ollama pull gemma2            # ตัวเลือกอื่น

# ดาวน์โหลด Embedding model (จำเป็น)
ollama pull nomic-embed-text
```

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
ollama pull nomic-embed-text
```

### ขั้นตอนที่ 2: Clone โปรเจกต์

```bash
git clone https://github.com/YOUR_USERNAME/legal-ai-complete.git
cd legal-ai-complete
```

### ขั้นตอนที่ 3: สร้าง Virtual Environment (แนะนำ)

```bash
# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน (Windows)
venv\Scripts\activate

# เปิดใช้งาน (macOS/Linux)
source venv/bin/activate
```

### ขั้นตอนที่ 4: ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### ขั้นตอนที่ 5: รันโปรแกรม

```bash
python app/main_app.py
```

### ขั้นตอนที่ 6: เปิดใช้งาน

เปิด Browser ไปที่: **<http://127.0.0.1:7860>**

---

## 🎯 วิธีใช้งาน (Usage)

### 1. อัปโหลดเอกสาร

- คลิก "Upload" หรือลากไฟล์มาวาง
- รองรับ: `.pdf`, `.txt`, `.docx`
- ระบบจะประมวลผลและสร้าง vector index อัตโนมัติ

### 2. ถามคำถาม

- พิมพ์คำถามในช่อง Chat
- ระบบจะค้นหาข้อมูลจากเอกสารและตอบพร้อมแหล่งอ้างอิง

### 3. ตัวอย่างคำถาม

```
📌 "สรุปเนื้อหาหลักของเอกสารนี้"
📌 "มาตรา 112 ระบุว่าอย่างไร?"
📌 "ค่าปรับสูงสุดตามกฎหมายนี้คือเท่าไหร่?"
📌 "เปรียบเทียบข้อกำหนดในมาตรา 5 กับ มาตรา 10"
```

### 4. จัดการข้อมูล

- ไปที่ **Settings** เพื่อลบเอกสารหรือ vector data
- ข้อมูลทั้งหมดอยู่ในเครื่องของคุณเท่านั้น

---

## 📁 โครงสร้างโปรเจกต์

```
legal-ai-complete/
│
├── 📂 app/                     # Core Application
│   ├── __init__.py
│   ├── config.py               # ⚙️ Configuration settings
│   ├── main_app.py             # 🚀 Entry point
│   ├── lifecycle_manager.py    # 🔄 Startup/Shutdown management
│   └── engine.py               # ⭐ RAG Engine (หัวใจหลัก)
│
├── 📂 llm/                     # LLM Integration
│   ├── __init__.py
│   ├── ollama_client.py        # 🤖 Ollama API client
│   └── prompt_templates.py     # 📝 Legal-specific prompts
│
├── 📂 ingestion/               # Document Processing
│   ├── __init__.py
│   ├── file_loader.py          # 📄 Load PDF/TXT/DOCX
│   └── text_cleaner.py         # 🧹 Text preprocessing
│
├── 📂 vector_store/            # Vector Database
│   ├── __init__.py
│   ├── embedding_manager.py    # 🔢 Create embeddings
│   ├── vector_db_manager.py    # 🗄️ ChromaDB operations
│   └── retriever.py            # 🔍 Semantic search
│
├── 📂 privacy/                 # Privacy Controls
│   ├── __init__.py
│   └── retention_manager.py    # 🔒 Data retention & deletion
│
├── 📂 gui/                     # User Interface
│   ├── __init__.py
│   ├── main_window.py          # 🖥️ Main layout
│   ├── chat_panel.py           # 💬 Chat interface
│   └── settings_panel.py       # ⚙️ Settings & Privacy UI
│
├── 📂 storage/                 # Data Storage (git-ignored)
│   ├── data/                   # 📁 User uploaded files
│   ├── vector_db/              # 🗃️ ChromaDB data
│   └── temp/                   # 🗑️ Temporary files
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 แนวคิดการออกแบบ (Design Philosophy)

### 1. Privacy-First Architecture

```
┌─────────────────────────────────────────────┐
│           ❌ ไม่มี Cloud Connection          │
├─────────────────────────────────────────────┤
│  🔒 ทุกอย่างประมวลผลใน Local Machine        │
│  🔒 ไม่มี API calls ออกไปข้างนอก            │
│  🔒 ผู้ใช้ควบคุมข้อมูลได้ 100%               │
│  🔒 ลบข้อมูลได้ทันทีเมื่อต้องการ             │
└─────────────────────────────────────────────┘
```

### 2. Modular Design

แยก components ชัดเจน ง่ายต่อการ maintain และ extend:

| Module | Responsibility |
|--------|----------------|
| `app/` | Application logic & coordination |
| `llm/` | LLM communication |
| `ingestion/` | Document parsing |
| `vector_store/` | Embedding & retrieval |
| `privacy/` | Data lifecycle management |
| `gui/` | User interface |

### 3. RAG (Retrieval-Augmented Generation)

ใช้ RAG pattern เพื่อให้ LLM ตอบจากเอกสารจริง ไม่ใช่ความรู้ทั่วไป:

```python
# Simplified RAG Flow
1. User uploads document → Split into chunks
2. Each chunk → Convert to vector embedding
3. Store vectors in ChromaDB

4. User asks question → Convert to vector
5. Find similar chunks (semantic search)
6. Send [question + relevant chunks] to LLM
7. LLM answers based on provided context only
```

### 4. Legal-Specific Prompting

Prompt templates ออกแบบมาเฉพาะสำหรับงานกฎหมาย:

- ✅ ตอบเฉพาะจากเอกสารที่ให้ (ไม่เดา)
- ✅ อ้างอิงมาตรา/หมวด/ข้อที่เกี่ยวข้อง
- ✅ ใช้ภาษากฎหมายที่เหมาะสม
- ✅ แจ้งเตือนเมื่อไม่พบข้อมูล

---

## 🛠️ เทคโนโลยีที่ใช้ (Tech Stack)

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM Runtime** | Ollama | รัน LLM บน local |
| **LLM Models** | Llama 3.2, Gemma 2 | ประมวลผลภาษา |
| **Embedding** | nomic-embed-text | สร้าง vector embeddings |
| **Vector DB** | ChromaDB | เก็บและค้นหา vectors |
| **RAG Framework** | LangChain | จัดการ RAG pipeline |
| **UI Framework** | Gradio | Web interface |
| **PDF Processing** | pdfplumber | อ่านไฟล์ PDF |
| **DOCX Processing** | python-docx | อ่านไฟล์ Word |

---

## 🔒 Privacy & Security

### ✅ สิ่งที่ระบบทำ

- ประมวลผลในเครื่อง 100%
- ไม่ส่งข้อมูลไปยัง server ภายนอก
- ผู้ใช้ลบข้อมูลได้ทุกเมื่อ
- ลบ temp files อัตโนมัติเมื่อปิดโปรแกรม

### ❌ สิ่งที่ระบบไม่ทำ

- ไม่ใช้ Cloud API
- ไม่เก็บข้อมูลโดยไม่ได้รับอนุญาต
- ไม่ฝังเอกสารมีลิขสิทธิ์มากับระบบ

### 📋 Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    🔒 All Data Stays Local                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   User's Computer                                            │
│   ┌────────────────────────────────────────────────────┐    │
│   │                                                    │    │
│   │  📄 Documents ──► 🔢 Vectors ──► 🗄️ ChromaDB      │    │
│   │       │                              │             │    │
│   │       ▼                              ▼             │    │
│   │  storage/data/              storage/vector_db/     │    │
│   │                                                    │    │
│   │  🤖 Ollama (LLM) ◄── Runs locally on your machine │    │
│   │                                                    │    │
│   └────────────────────────────────────────────────────┘    │
│                                                              │
│   ❌ NO data sent to external servers                        │
│   ❌ NO cloud APIs used                                      │
│   ❌ NO telemetry or tracking                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Disclaimer

> คำตอบจากระบบนี้เป็นเพียงข้อมูลเพื่อการศึกษาเท่านั้น
> ไม่ถือเป็นคำปรึกษาทางกฎหมาย
> กรุณาปรึกษาทนายความหรือผู้เชี่ยวชาญสำหรับกรณีจริง

---

## 📝 License

MIT License - ใช้งานได้อย่างอิสระ

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com) - Local LLM runtime
- [LangChain](https://langchain.com) - RAG framework
- [ChromaDB](https://trychroma.com) - Vector database
- [Gradio](https://gradio.app) - UI framework
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF extraction

---

## 👨‍💻 Author

สร้างโดย Team สำหรับโปรเจกต์ AI กฎหมาย

---

<p align="center">
  <b>⚖️ Legal AI Complete - ปลอดภัย ส่วนตัว ใช้งานง่าย</b>
</p>
