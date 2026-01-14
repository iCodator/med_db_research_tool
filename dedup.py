#!/usr/bin/env python3
"""
Cross-Database Deduplication Tool

Entfernt Duplikate über mehrere Datenbanken hinweg basierend auf
(authors, title, year).

Usage:
    python dedup.py [OPTIONS]
    
Options:
    --help              Zeigt diese Hilfe an
    --log-mode MODE     Logging-Modus: none, simple, detailed (Standard: simple)
"""

import sys
import argparse
from pathlib import Path

# Project root setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings
from src.utils.deduplicator import Deduplicator
from src.utils.logger import setup_logger
from src.utils.ui_helpers import (
    print_banner,
    print_separator,
    print_section_header,
    print_success_banner,
    print_warning,
    get_user_input
)


# Verfügbare Datenbanken
AVAILABLE_DATABASES = ['pubmed', 'europepmc', 'openalex']


def show_help():
    """Zeigt ausführliche Hilfe an"""
    help_text = """
╔═══════════════════════════════════════════════════════════════════════════╗
║           CROSS-DATABASE DEDUPLICATION TOOL - HILFE                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

BESCHREIBUNG:
    Entfernt Duplikate über mehrere Datenbanken hinweg basierend auf der
    Kombination von (Autoren, Titel, Jahr).
    
    Bei Duplikaten wird der Artikel mit der höchsten Priorität behalten:
      1. PubMed (höchste Priorität)
      2. Europe PMC
      3. OpenAlex (niedrigste Priorität)

VERWENDUNG:
    python dedup.py [OPTIONS]

OPTIONEN:
    --help
        Zeigt diese ausführliche Hilfe an.
    
    --log-mode MODE
        Bestimmt den Logging-Modus. Mögliche Werte:
        
        none      - Kein Logging (nur Konsolen-Ausgabe)
        simple    - Einfaches Logging (Standard)
                    Zeigt pro Datenbank: Anzahl Quellen, Duplikate, 
                    verbleibende eindeutige Artikel
        detailed  - Detailliertes Logging
                    Wie 'simple' + vollständige Liste aller Duplikate
                    mit (Autor, Titel (40 Zeichen), Jahr)
        
        Standard: simple

BEISPIELE:
    # Interaktive Verwendung mit einfachem Logging (Standard)
    python dedup.py
    
    # Ohne Logging
    python dedup.py --log-mode none
    
    # Mit detailliertem Logging (inkl. Duplikate-Liste)
    python dedup.py --log-mode detailed

ARBEITSWEISE:
    1. Auswahl der zu durchsuchenden Datenbanken (interaktiv)
    2. Sammeln aller JSON-Files aus den output/<database>/ Verzeichnissen
    3. Laden aller Artikel aus den JSON-Files
    4. Deduplizierung basierend auf (authors, title, year)
    5. Export der eindeutigen Artikel als CSV und JSON
    6. Optional: Logging der Statistiken in logs/

OUTPUT:
    Die dedulizierten Ergebnisse werden gespeichert in:
      - output/deduplicated/csv/dedup_<databases>_<timestamp>.csv
      - output/deduplicated/json/dedup_<databases>_<timestamp>.json
    
    Log-Dateien (falls aktiviert):
      - logs/dedup_<timestamp>.log

HINWEISE:
    - Stellen Sie sicher, dass Sie zuerst eine Suche mit research.py 
      durchgeführt haben
    - Die Deduplizierung basiert auf exakter Übereinstimmung (case-insensitive)
      von Autoren, Titel und Jahr
    - Bei mehreren identischen Artikeln wird immer der mit der höchsten
      Datenbank-Priorität behalten

╚═══════════════════════════════════════════════════════════════════════════╝
"""
    print(help_text)
    sys.exit(0)


def get_database_selection() -> list:
    """
    Fragt User nach Datenbank-Auswahl
    
    Returns:
        Liste der ausgewählten Datenbanken
    """
    print_banner("CROSS-DATABASE DEDUPLICATION TOOL")
    print_section_header("Welche Datenbanken sollen auf Duplikate überprüft werden?")
    
    print("  A) 'alle' - Durchsucht alle Datenbanken (pubmed, europepmc, openalex)")
    print("  B) Einzeln eingeben (z.B. pubmed, dann europepmc)")
    print()
    
    choice = get_user_input("Ihre Wahl (alle/einzeln): ")
    
    if choice and choice.lower() in ['alle', 'all', 'a']:
        return AVAILABLE_DATABASES.copy()
    
    # Einzelne Datenbanken abfragen
    return _get_individual_databases()


def _get_individual_databases() -> list:
    """
    Fragt User nach einzelnen Datenbanken
    
    Returns:
        Liste der ausgewählten Datenbanken
    """
    databases = []
    
    print()
    print(f"Verfügbare Datenbanken: {', '.join(AVAILABLE_DATABASES)}")
    print("(Drücken Sie Enter ohne Eingabe zum Beenden)")
    print()
    
    while True:
        if databases:
            prompt = f"Weitere Datenbank hinzufügen? (bereits: {', '.join(databases)}): "
        else:
            prompt = "Erste Datenbank: "
        
        db = get_user_input(prompt, allow_empty=True)
        
        if not db:
            # Leere Eingabe = fertig
            break
        
        db = db.lower()
        
        if db not in AVAILABLE_DATABASES:
            print_warning(f"Ungültige Datenbank: {db}")
            print(f"   Verfügbare Optionen: {', '.join(AVAILABLE_DATABASES)}")
            continue
        
        if db in databases:
            print_warning(f"{db} wurde bereits hinzugefügt")
            continue
        
        databases.append(db)
    
    if not databases:
        print()
        print_warning("Keine Datenbank ausgewählt. Programm wird beendet.")
        sys.exit(0)
    
    return databases


def get_logging_mode(cli_mode=None) -> str:
    """
    Bestimmt den Logging-Modus
    
    Args:
        cli_mode: Über CLI angegebener Modus (oder None)
        
    Returns:
        Logging-Modus: 'none', 'simple', oder 'detailed'
    """
    if cli_mode:
        return cli_mode
    
    # Interaktive Abfrage
    print()
    print_section_header("Logging-Modus auswählen")
    print("  1) Kein Logging (nur Konsolen-Ausgabe)")
    print("  2) Einfaches Logging (Statistiken pro Datenbank)")
    print("  3) Detailliertes Logging (+ Liste aller Duplikate)")
    print()
    
    choice = get_user_input("Ihre Wahl (1/2/3, Standard: 2): ", allow_empty=True)
    
    if not choice or choice == '2':
        return 'simple'
    elif choice == '1':
        return 'none'
    elif choice == '3':
        return 'detailed'
    else:
        print_warning(f"Ungültige Wahl: {choice}. Verwende Standard (einfach).")
        return 'simple'


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Cross-Database Deduplication Tool',
        add_help=False  # Wir verwenden eigene --help Funktion
    )
    
    parser.add_argument(
        '--help',
        action='store_true',
        help='Zeigt ausführliche Hilfe an'
    )
    
    parser.add_argument(
        '--log-mode',
        choices=['none', 'simple', 'detailed'],
        default=None,
        help='Logging-Modus (none/simple/detailed, Standard: simple)'
    )
    
    return parser.parse_args()


def main():
    """Hauptfunktion des Deduplication Tools"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Zeige Hilfe wenn angefordert
    if args.help:
        show_help()
    
    # Datenbank-Auswahl
    databases = get_database_selection()
    
    # Logging-Modus bestimmen
    log_mode = get_logging_mode(args.log_mode)
    
    # Logger initialisieren (wenn nicht 'none')
    logger = None
    if log_mode != 'none':
        logger = setup_logger("dedup_tool")
        logger.info("="*70)
        logger.info("CROSS-DATABASE DEDUPLICATION TOOL - START")
        logger.info("="*70)
        logger.info(f"Ausgewählte Datenbanken: {', '.join(databases)}")
        logger.info(f"Logging-Modus: {log_mode}")

    
    print()
    print_separator()
    print()
    print(f"Durchsuche Datenbanken: {', '.join(databases)}")
    print()
    
    # Deduplicator initialisieren (mit Logger)
    output_base = Settings.OUTPUT_DIR
    deduplicator = Deduplicator(output_base, logger=logger)
    
    # Schritt 1: JSON-Files sammeln
    json_files = deduplicator.collect_json_files(databases)
    
    # Prüfe ob Files gefunden wurden
    total_files = sum(len(files) for files in json_files.values())
    if total_files == 0:
        print()
        print("⚠ Keine JSON-Files gefunden in den ausgewählten Datenbanken.")
        print("  Führen Sie zuerst eine Suche durch (python research.py)")
        if logger:
            logger.warning("Keine JSON-Files gefunden")
        sys.exit(1)
    
    print()
    
    # Schritt 2: Artikel laden
    print("Lade Artikel...")
    all_articles = deduplicator.load_articles(json_files)
    
    if not all_articles:
        print()
        print("⚠ Keine Artikel geladen.")
        if logger:
            logger.warning("Keine Artikel geladen")
        sys.exit(1)
    
    stats = deduplicator.get_stats()
    print(f"Total geladen: {stats['articles_loaded']} Artikel")
    print()
    
    # Schritt 3: Deduplizierung
    print("Deduplizierung läuft...")
    unique_articles = deduplicator.deduplicate(all_articles)
    
    stats = deduplicator.get_stats()
    print(f"Duplikate entfernt: {stats['duplicates_removed']}")
    print(f"Eindeutige Artikel: {stats['unique_articles']}")
    
    if not unique_articles:
        print()
        print("⚠ Keine Artikel nach Deduplizierung.")
        if logger:
            logger.warning("Keine Artikel nach Deduplizierung")
        sys.exit(1)
    
    # Schritt 4: Export
    output_dir = Settings.OUTPUT_DIR / "deduplicated"
    csv_path, json_path = deduplicator.export_results(
        unique_articles,
        databases,
        output_dir
    )
    
    # Schritt 5: Logging (falls aktiviert)
    if logger and log_mode in ['simple', 'detailed']:
        print()
        print_separator()
        print("Schreibe Logs...")
        deduplicator.log_statistics(log_mode)
        logger.info("="*70)
        logger.info("DEDUPLIZIERUNG ERFOLGREICH ABGESCHLOSSEN")
        logger.info("="*70)
    
    # Abschluss
    print_success_banner("DEDUPLIZIERUNG ERFOLGREICH ABGESCHLOSSEN")
    print(f"Dateien gespeichert in: {output_dir}")
    if logger:
        print(f"Log-Datei: logs/ (siehe neueste Datei)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
