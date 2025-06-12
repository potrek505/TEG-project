import subprocess
import time
import os

def start_project():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")
    frontend_dir = os.path.join(project_dir, "frontend")
    ai_dir = os.path.join(project_dir, "ai")
    
    # Start AI service first
    print("Starting AI service...")
    ai_process = subprocess.Popen(
        ["python", "app.py"],
        cwd=ai_dir,
        stdout=None,
        stderr=None,
        text=True
    )
    
    time.sleep(3)  # AI needs time to load models
    
    if ai_process.poll() is not None:
        print("ERROR: AI service failed to start!")
        return
    print("✓ AI service started on port 5001")
    
    # Start backend
    print("Starting backend...")
    backend_process = subprocess.Popen(
        ["python", "app.py"], 
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
    print("✓ Backend started on port 5000")
    
    # Start frontend
    print("Starting frontend...")
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "app.py"], 
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
    print("Frontend: http://localhost:8501")
    print("Backend API: http://localhost:5000") 
    print("AI Service: http://localhost:5001")
    
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