# -*- coding: utf-8 -*-
"""
Legal AI Complete - Main Application Entry Point
จุดเริ่มต้นของแอปพลิเคชัน Legal AI

Usage:
    python app/main_app.py

หรือ:
    cd legal-ai-complete
    python -m app.main_app
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.lifecycle_manager import startup, shutdown
from gui.main_window import launch_app


def main():
    """
    Main function - Entry point
    """
    try:
        # 1. Startup (initialize, cleanup old files)
        startup_info = startup()
        
        # 2. Launch GUI
        launch_app(share=False)  # share=False for privacy
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        # 3. Shutdown (cleanup)
        shutdown()


if __name__ == "__main__":
    main()
