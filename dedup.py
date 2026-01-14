#!/usr/bin/env python3
"""
Cross-Database Deduplication Tool

Entfernt Duplikate über mehrere Datenbanken hinweg basierend auf
(authors, title, year).

Usage:
    python dedup.py
"""

import sys
from pathlib import Path

# Project root setup
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings
from src.utils.deduplicator import Deduplicator
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


def main():
    """Hauptfunktion des Deduplication Tools"""
    
    # Datenbank-Auswahl
    databases = get_database_selection()
    
    print()
    print_separator()
    print()
    print(f"Durchsuche Datenbanken: {', '.join(databases)}")
    print()
    
    # Deduplicator initialisieren
    output_base = Settings.OUTPUT_DIR
    deduplicator = Deduplicator(output_base)
    
    # Schritt 1: JSON-Files sammeln
    json_files = deduplicator.collect_json_files(databases)
    
    # Prüfe ob Files gefunden wurden
    total_files = sum(len(files) for files in json_files.values())
    if total_files == 0:
        print()
        print("⚠ Keine JSON-Files gefunden in den ausgewählten Datenbanken.")
        print("  Führen Sie zuerst eine Suche durch (python research.py)")
        sys.exit(1)
    
    print()
    
    # Schritt 2: Artikel laden
    print("Lade Artikel...")
    all_articles = deduplicator.load_articles(json_files)
    
    if not all_articles:
        print()
        print("⚠ Keine Artikel geladen.")
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
        sys.exit(1)
    
    # Schritt 4: Export
    output_dir = Settings.OUTPUT_DIR / "deduplicated"
    csv_path, json_path = deduplicator.export_results(
        unique_articles,
        databases,
        output_dir
    )
    
    # Abschluss
    print_success_banner("DEDUPLIZIERUNG ERFOLGREICH ABGESCHLOSSEN")
    print(f"Dateien gespeichert in: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
