import subprocess
import time
import os
import sys
from dotenv import load_dotenv
from shared_logging import setup_logging

# Konfiguracja loggera używając shared_logging
logger = setup_logging("main")

def start_project():
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        load_dotenv( ".env", override=True)

        backend_dir = os.path.join(project_dir, "backend")
        frontend_dir = os.path.join(project_dir, "frontend")
        ai_dir = os.path.join(project_dir, "ai")

        # Jawne wskazanie ścieżki do pliku .env
        
        print(os.environ.get('BACKEND_PORT'))
        print(os.environ.get('AI_PORT'))
        print(os.environ.get('FRONTEND_PORT'))

        # Sprawdź czy wymagane zmienne środowiskowe są ustawione
        required_env_vars = ['AI_PORT', 'BACKEND_PORT', 'FRONTEND_PORT']
        for var in required_env_vars:
            if not os.environ.get(var):
                logger.error(f"Missing required environment variable: {var}")
                return False

        logger.info("Starting AI service...")
        ai_process = subprocess.Popen(
            ["uv", "run", "python", "ai/app.py", "--port", os.environ.get('AI_PORT')],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(3)

        if ai_process.poll() is not None:
            stderr_output = ai_process.stderr.read() if ai_process.stderr else "No error details"
            logger.error(f"AI service failed to start! Error: {stderr_output}")
            return False
        logger.info(f"✓ AI service started on port {os.environ.get('AI_PORT')}")

        logger.info("Starting backend...")
        backend_process = subprocess.Popen(
            ["uv", "run", "python", "app.py", "--port", os.environ.get('BACKEND_PORT')], 
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(2)

        if backend_process.poll() is not None:
            stderr_output = backend_process.stderr.read() if backend_process.stderr else "No error details"
            logger.error(f"Backend failed to start! Error: {stderr_output}")
            ai_process.terminate()
            return False
        logger.info(f"✓ Backend started on port {os.environ.get('BACKEND_PORT')}")

        logger.info("Starting frontend...")
        frontend_process = subprocess.Popen(
            ["uv", "run", "streamlit", "run", "app.py", "--server.port", os.environ.get('FRONTEND_PORT')],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(2)

        if frontend_process.poll() is not None:
            stderr_output = frontend_process.stderr.read() if frontend_process.stderr else "No error details"
            logger.error(f"Frontend failed to start! Error: {stderr_output}")
            backend_process.terminate()
            ai_process.terminate()
            return False
        logger.info("✓ Frontend started")
        logger.info("\n🚀 All services running!")
        logger.info(f"Frontend: http://localhost:{os.environ.get('FRONTEND_PORT')}")
        logger.info(f"Backend API: http://localhost:{os.environ.get('BACKEND_PORT')}")
        logger.info(f"AI Service: http://localhost:{os.environ.get('AI_PORT')}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down all services...")
            ai_process.terminate()
            backend_process.terminate()
            frontend_process.terminate()
            logger.info("All services stopped.")
            return True

    except Exception as e:
        logger.error(f"Failed to start project: {str(e)}")
        return False

if __name__ == "__main__":
    success = start_project()
    if not success:
        logger.error("Project failed to start properly")
        sys.exit(1)