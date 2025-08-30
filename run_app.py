#!/usr/bin/env python3
"""
Convenience script to run both frontend and backend
Usage: uv run python run_app.py
"""

import subprocess
import sys
import time
import signal
import os

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.api.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", 
        "run", "app/ui/streamlit_app.py",
        "--server.port", "8501"
    ])

def main():
    print("🌟 Starting Local Orchestrator...")
    print("📱 Backend will be available at: http://localhost:8000")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop both services")
    print()
    
    # Clear cache at startup to ensure fresh responses
    try:
        from app.utils.cache import clear_cache
        clear_cache()
        print("🗑️ Cache cleared for fresh start")
    except Exception as e:
        print(f"⚠️ Could not clear cache: {e}")
    
    try:
        # Start backend
        backend = run_backend()
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend = run_frontend()
        time.sleep(2)  # Give frontend time to start
        
        print("✅ Both services are running!")
        print("🔗 Open http://localhost:8501 in your browser")
        
        # Wait for user to stop
        try:
            backend.wait()
            frontend.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Clean up processes
        try:
            backend.terminate()
            frontend.terminate()
            print("✅ Services stopped")
        except:
            pass

if __name__ == "__main__":
    main()
