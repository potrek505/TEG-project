import subprocess
import time
import os

def start_project():
    """Start the entire project - both backend and frontend"""
    
    print("Starting TEG Project...")
    
    # Get absolute paths
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")
    frontend_dir = os.path.join(project_dir, "frontend")
    
    # Start backend server
    print("Starting backend server...")
    backend_process = subprocess.Popen(
        ["python", "app.py"], 
        cwd=backend_dir,
        stdout=None,  # Logi będą wyświetlane w konsoli
        stderr=None,  # Logi błędów również będą wyświetlane w konsoli
        text=True
    )
    
    # Wait for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(2)
    
    # Check if backend started successfully
    if backend_process.poll() is not None:
        print("ERROR: Backend failed to start!")
        return
    
    print("Backend running successfully!")
    
    # Start frontend
    print("Starting frontend Streamlit app...")
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "app.py"], 
        cwd=frontend_dir,
        stdout=None,  # Logi będą wyświetlane w konsoli
        stderr=None,  # Logi błędów również będą wyświetlane w konsoli
        text=True
    )
    
    # Wait for frontend to start
    time.sleep(2)
    
    if frontend_process.poll() is not None:
        print("ERROR: Frontend failed to start!")
        backend_process.terminate()
        return
    
    print("Frontend running successfully!")
    print("All services started. Press Ctrl+C to stop all services.")
    
    try:
        # Keep the main process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("All services stopped.")

if __name__ == "__main__":
    start_project()