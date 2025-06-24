import subprocess
import time
import os
from dotenv import load_dotenv

def start_project():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")
    frontend_dir = os.path.join(project_dir, "frontend")
    ai_dir = os.path.join(project_dir, "ai")
    
    load_dotenv()
    
    print("Starting AI service...")
    ai_process = subprocess.Popen(
        ["uv", "run", "python", "ai/app.py"],
        cwd=project_dir,  # <-- changed from ai_dir
        stdout=None,
        stderr=None,
        text=True
    )
    
    time.sleep(3)
    
    if ai_process.poll() is not None:
        print("ERROR: AI service failed to start!")
        return
    print(f"✓ AI service started on port {os.environ.get('AI_PORT')}")
    
    print("Starting backend...")
    backend_process = subprocess.Popen(
        ["uv", "run", "python", "app.py"], 
        cwd=backend_dir,
        stdout=None,  
        stderr=None,
        text=True
    )
    
    time.sleep(2)
    
    if backend_process.poll() is not None:
        print("ERROR: Backend failed to start!")
        ai_process.terminate()
        return
    print(f"✓ Backend started on port {os.environ.get('BACKEND_PORT')}")
    
    print("Starting frontend...")
    frontend_process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "app.py", "--server.port", os.environ.get('FRONTEND_PORT')], 
        cwd=frontend_dir,
        stdout=None,
        stderr=None,
        text=True
    )
    
    time.sleep(2)
    
    if frontend_process.poll() is not None:
        print("ERROR: Frontend failed to start!")
        backend_process.terminate()
        ai_process.terminate()
        return
    print("✓ Frontend started")
    print("\n🚀 All services running!")
    print(f"Frontend: http://localhost:{os.environ.get('FRONTEND_PORT')}")
    print(f"Backend API: http://localhost:{os.environ.get('BACKEND_PORT')}")
    print(f"AI Service: http://localhost:{os.environ.get('AI_PORT')}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        ai_process.terminate()
        backend_process.terminate()
        frontend_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    start_project()