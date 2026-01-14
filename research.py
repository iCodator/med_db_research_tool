#!/usr/bin/env python3
"""
Medical Database Research Tool - Main Entry Point

Dieses Tool ermöglicht die Abfrage medizinischer Datenbanken mit
vorformatierten Query-Strings aus Textdateien.

Usage:
    python research.py
"""

import sys
from pathlib import Path

# Project root setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings
from src.core.query_handler import QueryHandler
from src.utils.logger import setup_logger
from src.utils.ui_helpers import (
    print_banner,
    print_separator,
    print_section_header,
    print_list_items,
    print_success_banner,
    print_error_banner,
    get_user_input
)


def main():
    """Hauptfunktion des Research Tools"""
    
    # Header
    print_banner("MEDICAL DATABASE RESEARCH TOOL")
    print_section_header("Unterstützte Datenbanken:")
    
    databases = [
        ("pubmed", "PubMed"),
        ("europepmc", "Europe PMC"),
        ("openalex", "OpenAlex")
    ]
    print_list_items(databases)
    
    print()
    print_separator()
    print()
    
    # Logger initialisieren
    logger = setup_logger()
    
    # Dateinamen vom Benutzer abfragen
    filename = get_user_input("Geben Sie den Dateinamen ein (z.B. pubmed oder pubmed.txt): ")
    
    if not filename:
        print("Fehler: Kein Dateiname angegeben.")
        sys.exit(1)
    
    # Query Handler initialisieren
    handler = QueryHandler(logger)
    
    # Query verarbeiten
    success = handler.process_query_file(filename)
    
    if success:
        print_success_banner("SUCHE ERFOLGREICH ABGESCHLOSSEN")
    else:
        print_error_banner("SUCHE FEHLGESCHLAGEN")
        print("Überprüfen Sie die Logs für Details.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFehler: {e}")
        sys.exit(1)
