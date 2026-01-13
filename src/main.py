#!/usr/bin/env python3
"""
Medical Database Research Tool - Main Entry Point

Dieses Tool ermöglicht die Abfrage medizinischer Datenbanken mit
vorformatierten Query-Strings aus Textdateien.

Usage:
    python src/main.py
"""

import sys
from pathlib import Path

# Project root setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings
from src.core.query_handler import QueryHandler
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger


def main():
    """Hauptfunktion des Research Tools"""
    
    print("=" * 70)
    print("MEDICAL DATABASE RESEARCH TOOL")
    print("=" * 70)
    print()
    print("Unterstützte Datenbanken:")
    print("  • pubmed.txt    → PubMed")
    print("  • europepmc.txt → Europe PMC")
    print("  • openalex.txt  → OpenAlex")
    print()
    print("-" * 70)
    print()
    
    # Logger initialisieren
    logger = setup_logger()
    
    # Dateinamen vom Benutzer abfragen
    try:
        filename = input("Geben Sie den Dateinamen ein (z.B. pubmed.txt): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramm beendet.")
        return
    
    if not filename:
        print("Fehler: Kein Dateiname angegeben.")
        return
    
    # Query Handler initialisieren
    handler = QueryHandler(logger)
    
    # Query verarbeiten
    success = handler.process_query_file(filename)
    
    if success:
        print("\n" + "=" * 70)
        print("SUCHE ERFOLGREICH ABGESCHLOSSEN")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("SUCHE FEHLGESCHLAGEN")
        print("=" * 70)
        print("Überprüfen Sie die Logs für Details.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFehler: {e}")
        sys.exit(1)
