import subprocess
import time
import os
import sys
from dotenv import load_dotenv
from config.logging import setup_logging
from config.config_manager import get_project_config

# Konfiguracja loggera używając shared_logging
logger = setup_logging("main")

# Initialize project config manager
project_config = get_project_config()

def start_project():
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Wczytaj główny .env jeśli istnieje (dla wstecznej kompatybilności)
        main_env_path = os.path.join(project_dir, ".env")
        if os.path.exists(main_env_path):
            load_dotenv(main_env_path, override=True)

        backend_dir = os.path.join(project_dir, "backend")
        frontend_dir = os.path.join(project_dir, "frontend")
        ai_dir = os.path.join(project_dir, "ai")

        # Pobierz porty z config managera
        ports = project_config.get_all_ports()
        ai_port = str(ports["ai"])
        backend_port = str(ports["backend"])
        frontend_port = str(ports["frontend"])
        
        # Sprawdź czy porty są ustawione
        if not all([ai_port, backend_port, frontend_port]):
            logger.error("Missing required port configuration")
            return False

        logger.info(f"Starting services with ports: AI={ai_port}, Backend={backend_port}, Frontend={frontend_port}")

        # Pobierz opóźnienia z konfiguracji
        ai_delay = project_config.get("services", "ai", "startup_delay", default=3)
        backend_delay = project_config.get("services", "backend", "startup_delay", default=2)
        frontend_delay = project_config.get("services", "frontend", "startup_delay", default=2)

        logger.info("Starting AI service...")
        ai_process = subprocess.Popen(
            ["uv", "run", "python", "app.py", "--port", ai_port],
            cwd=ai_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(ai_delay)

        if ai_process.poll() is not None:
            stderr_output = ai_process.stderr.read() if ai_process.stderr else "No error details"
            logger.error(f"AI service failed to start! Error: {stderr_output}")
            return False
        logger.info(f"✓ AI service started on port {ai_port}")

        logger.info("Starting backend...")
        backend_process = subprocess.Popen(
            ["uv", "run", "python", "app.py", "--port", backend_port], 
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(backend_delay)

        if backend_process.poll() is not None:
            stderr_output = backend_process.stderr.read() if backend_process.stderr else "No error details"
            logger.error(f"Backend failed to start! Error: {stderr_output}")
            ai_process.terminate()
            return False
        logger.info(f"✓ Backend started on port {backend_port}")

        logger.info("Starting frontend...")
        frontend_process = subprocess.Popen(
            ["uv", "run", "streamlit", "run", "app.py", "--server.port", frontend_port],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(frontend_delay)

        if frontend_process.poll() is not None:
            stderr_output = frontend_process.stderr.read() if frontend_process.stderr else "No error details"
            logger.error(f"Frontend failed to start! Error: {stderr_output}")
            backend_process.terminate()
            ai_process.terminate()
            return False
        logger.info("✓ Frontend started")
        logger.info("\n🚀 All services running!")
        logger.info(f"Frontend: {project_config.get_service_url('frontend')}")
        logger.info(f"Backend API: {project_config.get_service_url('backend')}")
        logger.info(f"AI Service: {project_config.get_service_url('ai')}")

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