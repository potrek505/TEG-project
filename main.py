import subprocess
import time
import os
import sys
import threading
from dotenv import load_dotenv
from config.logging import init_logging, get_logger
from config.config_manager import get_project_config

# Inicjalizacja systemu logowania
init_logging()
logger = get_logger(__name__)

# Initialize project config manager
project_config = get_project_config()

def log_subprocess_output(pipe, logger_func, prefix):
    """Czytaj output z subprocess i przekaż do loggera."""
    try:
        for line in iter(pipe.readline, ''):
            if line.strip():
                logger_func(f"{prefix}: {line.strip()}")
        pipe.close()
    except Exception as e:
        logger.error(f"Error reading {prefix} output: {e}")

def start_project():
    try:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Wczytaj .env z katalogu config
        config_env_path = os.path.join(project_dir, "config", ".env")
        if os.path.exists(config_env_path):
            load_dotenv(config_env_path, override=True)

        backend_dir = os.path.join(project_dir, "backend")
        frontend_dir = os.path.join(project_dir, "frontend")
        ai_dir = os.path.join(project_dir, "ai")

        # Pobierz porty z config managera
        ports = project_config.get_all_ports()
        ai_port = os.environ.get("AI_PORT", str(ports["ai"]))
        backend_port = os.environ.get("BACKEND_PORT", str(ports["backend"]))
        frontend_port = os.environ.get("FRONTEND_PORT", str(ports["frontend"]))

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
        
        # Ustaw zmienne środowiskowe dla AI service
        ai_env = os.environ.copy()
        # Ustaw PYTHONPATH z priorytetem dla lokalnego katalogu AI
        current_pythonpath = ai_env.get("PYTHONPATH", "")
        ai_pythonpath = f"{ai_dir}:{project_dir}:{current_pythonpath}" if current_pythonpath else f"{ai_dir}:{project_dir}"
        ai_env["PYTHONPATH"] = ai_pythonpath
        ai_env["AI_PORT"] = ai_port
        ai_env["LAUNCHED_BY_MAIN"] = "true"
        ai_env["SERVICE_NAME"] = "ai"
        
        # Przekaż zmienne bazy danych z głównego .env
        if os.environ.get("transactions_db"):
            ai_env["transactions_db"] = os.environ.get("transactions_db")
        if os.environ.get("transactions_db_uri"):
            ai_env["transactions_db_uri"] = os.environ.get("transactions_db_uri")
        if os.environ.get("transactions_db_path"):
            ai_env["transactions_db_path"] = os.environ.get("transactions_db_path")
            
        # Jeśli nie ma transactions_db_path, użyj transactions_db
        if not ai_env.get("transactions_db_path") and ai_env.get("transactions_db"):
            ai_env["transactions_db_path"] = ai_env.get("transactions_db")
        
        ai_process = subprocess.Popen(
            ["uv", "run", "python", "app.py", "--port", ai_port],
            cwd=ai_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=ai_env
        )

        # Uruchom wątki do przechwytywania logów
        ai_stdout_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(ai_process.stdout, logger.info, "AI"),
            daemon=True
        )
        ai_stderr_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(ai_process.stderr, logger.error, "AI"),
            daemon=True
        )
        ai_stdout_thread.start()
        ai_stderr_thread.start()

        time.sleep(ai_delay)

        if ai_process.poll() is not None:
            logger.error(f"AI service failed to start!")
            return False
        logger.info(f"✓ AI service started on port {ai_port}")

        logger.info("Starting backend...")
        
        # Ustaw zmienne środowiskowe dla Backend service
        backend_env = os.environ.copy()
        # Ustaw PYTHONPATH z priorytetem dla lokalnego katalogu backend
        current_pythonpath = backend_env.get("PYTHONPATH", "")
        backend_pythonpath = f"{backend_dir}:{project_dir}:{current_pythonpath}" if current_pythonpath else f"{backend_dir}:{project_dir}"
        backend_env["PYTHONPATH"] = backend_pythonpath
        backend_env["BACKEND_PORT"] = backend_port
        backend_env["AI_SERVICE_URL"] = f"http://localhost:{ai_port}"
        backend_env["LAUNCHED_BY_MAIN"] = "true"
        backend_env["SERVICE_NAME"] = "backend"
        
        # Przekaż zmienne bazy danych z głównego .env
        if os.environ.get("transactions_db"):
            backend_env["transactions_db"] = os.environ.get("transactions_db")
        if os.environ.get("transactions_db_uri"):
            backend_env["transactions_db_uri"] = os.environ.get("transactions_db_uri")
        
        backend_process = subprocess.Popen(
            ["uv", "run", "python", "app.py", "--port", backend_port], 
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=backend_env
        )

        # Uruchom wątki do przechwytywania logów
        backend_stdout_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(backend_process.stdout, logger.info, "Backend"),
            daemon=True
        )
        backend_stderr_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(backend_process.stderr, logger.error, "Backend"),
            daemon=True
        )
        backend_stdout_thread.start()
        backend_stderr_thread.start()

        time.sleep(backend_delay)

        if backend_process.poll() is not None:
            logger.error(f"Backend failed to start!")
            ai_process.terminate()
            return False
        logger.info(f"✓ Backend started on port {backend_port}")

        logger.info("Starting frontend...")
        
        # Ustaw zmienne środowiskowe dla Frontend service  
        frontend_env = os.environ.copy()
        # Ustaw PYTHONPATH z priorytetem dla lokalnego katalogu frontend
        current_pythonpath = frontend_env.get("PYTHONPATH", "")
        frontend_pythonpath = f"{frontend_dir}:{project_dir}:{current_pythonpath}" if current_pythonpath else f"{frontend_dir}:{project_dir}"
        frontend_env["PYTHONPATH"] = frontend_pythonpath
        frontend_env["FRONTEND_PORT"] = frontend_port
        frontend_env["BACKEND_SERVICE_URL"] = f"http://localhost:{backend_port}"
        frontend_env["LAUNCHED_BY_MAIN"] = "true"
        frontend_env["SERVICE_NAME"] = "frontend"
        
        frontend_process = subprocess.Popen(
            ["uv", "run", "streamlit", "run", "app.py", "--server.port", frontend_port],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=frontend_env
        )

        # Uruchom wątki do przechwytywania logów
        frontend_stdout_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(frontend_process.stdout, logger.info, "Frontend"),
            daemon=True
        )
        frontend_stderr_thread = threading.Thread(
            target=log_subprocess_output, 
            args=(frontend_process.stderr, logger.error, "Frontend"),
            daemon=True
        )
        frontend_stdout_thread.start()
        frontend_stderr_thread.start()

        time.sleep(frontend_delay)

        if frontend_process.poll() is not None:
            logger.error(f"Frontend failed to start!")
            backend_process.terminate()
            ai_process.terminate()
            return False
        logger.info("✓ Frontend started")
        logger.info("\n🚀 All services running!")
        logger.info(f"Frontend: {project_config.get_service_url('frontend')}")
        logger.info(f"Backend API: {project_config.get_service_url('backend')}")
        logger.info(f"AI Service: {project_config.get_service_url('ai')}")

        try:
            # Sprawdź czy wszystkie procesy nadal działają co 5 sekund
            while True:
                time.sleep(5)
                
                # Sprawdź status wszystkich procesów
                if ai_process.poll() is not None:
                    logger.error("AI service has stopped unexpectedly!")
                    break
                    
                if backend_process.poll() is not None:
                    logger.error("Backend service has stopped unexpectedly!")
                    break
                    
                if frontend_process.poll() is not None:
                    logger.error("Frontend service has stopped unexpectedly!")
                    break
                    
        except KeyboardInterrupt:
            logger.info("\nShutting down all services...")
            
            # Graceful shutdown
            logger.info("Stopping AI service...")
            ai_process.terminate()
            try:
                ai_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ai_process.kill()
                
            logger.info("Stopping Backend service...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                
            logger.info("Stopping Frontend service...")
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
                
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