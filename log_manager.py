#!/usr/bin/env python3
"""
Narzędzie zarządzania logami dla projektu TEG
"""
import os
import argparse
import glob
from pathlib import Path

def clear_logs():
    """Wyczyść wszystkie pliki logów"""
    log_dir = Path(__file__).parent / "logs"
    log_files = glob.glob(str(log_dir / "*.log"))
    
    for log_file in log_files:
        try:
            os.remove(log_file)
            print(f"Usunięto: {log_file}")
        except OSError as e:
            print(f"Błąd usuwania {log_file}: {e}")
    
    print(f"Wyczyszczono {len(log_files)} plików logów")

def show_logs(service=None, errors_only=False, lines=50):
    """Pokaż ostatnie wpisy logów"""
    log_dir = Path(__file__).parent / "logs"
    
    if errors_only:
        log_file = log_dir / "errors.log"
    elif service:
        log_file = log_dir / f"{service}.log"
    else:
        log_file = log_dir / "combined.log"
    
    if not log_file.exists():
        print(f"Plik logów {log_file} nie istnieje")
        return
    
    print(f"=== Ostatnie {lines} linii z {log_file.name} ===")
    os.system(f"tail -n {lines} '{log_file}'")

def follow_logs(service=None, errors_only=False):
    """Śledź pliki logów w czasie rzeczywistym"""
    log_dir = Path(__file__).parent / "logs"
    
    if errors_only:
        log_file = log_dir / "errors.log"
    elif service:
        log_file = log_dir / f"{service}.log"
    else:
        log_file = log_dir / "combined.log"
    
    if not log_file.exists():
        print(f"Plik logów {log_file} nie istnieje")
        return
    
    print(f"=== Śledzenie {log_file.name} (Ctrl+C aby zatrzymać) ===")
    os.system(f"tail -f '{log_file}'")

def list_logs():
    """Wylistuj wszystkie dostępne pliki logów"""
    log_dir = Path(__file__).parent / "logs"
    log_files = glob.glob(str(log_dir / "*.log"))
    
    if not log_files:
        print("Nie znaleziono plików logów")
        return
    
    print("Dostępne pliki logów:")
    for log_file in sorted(log_files):
        file_path = Path(log_file)
        size = file_path.stat().st_size
        size_str = f"{size:,} bajtów"
        if size > 1024:
            size_str = f"{size/1024:.1f} KB"
        if size > 1024*1024:
            size_str = f"{size/(1024*1024):.1f} MB"
        
        print(f"  {file_path.name:<20} ({size_str})")

def main():
    parser = argparse.ArgumentParser(description="Zarządzanie Logami Projektu TEG")
    subparsers = parser.add_subparsers(dest="command", help="Dostępne polecenia")
    
    # Polecenie clear
    subparsers.add_parser("clear", help="Wyczyść wszystkie pliki logów")
    
    # Polecenie list
    subparsers.add_parser("list", help="Wylistuj wszystkie pliki logów")
    
    # Polecenie show
    show_parser = subparsers.add_parser("show", help="Pokaż ostatnie wpisy logów")
    show_parser.add_argument("--service", choices=["main", "ai", "backend", "frontend"], 
                           help="Pokaż logi dla konkretnego serwisu")
    show_parser.add_argument("--errors", action="store_true", help="Pokaż tylko błędy")
    show_parser.add_argument("--lines", type=int, default=50, help="Liczba linii do pokazania")
    
    # Polecenie follow
    follow_parser = subparsers.add_parser("follow", help="Śledź logi w czasie rzeczywistym")
    follow_parser.add_argument("--service", choices=["main", "ai", "backend", "frontend"],
                              help="Śledź logi dla konkretnego serwisu")
    follow_parser.add_argument("--errors", action="store_true", help="Śledź tylko błędy")
    
    args = parser.parse_args()
    
    if args.command == "clear":
        clear_logs()
    elif args.command == "list":
        list_logs()
    elif args.command == "show":
        show_logs(args.service, args.errors, args.lines)
    elif args.command == "follow":
        follow_logs(args.service, args.errors)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
