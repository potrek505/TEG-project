import subprocess
import time
import os

def start_project():
    
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")
    frontend_dir = os.path.join(project_dir, "frontend")
    
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
        return
    
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
        return
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    start_project()