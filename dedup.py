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


def get_database_selection() -> list:
    """
    Fragt User nach Datenbank-Auswahl
    
    Returns:
        Liste der ausgewählten Datenbanken
    """
    print("=" * 70)
    print("CROSS-DATABASE DEDUPLICATION TOOL")
    print("=" * 70)
    print()
    print("Welche Datenbanken sollen auf Duplikate überprüft werden?")
    print()
    print("  A) 'alle' - Durchsucht alle Datenbanken (pubmed, europepmc, openalex)")
    print("  B) Einzeln eingeben (z.B. pubmed, dann europepmc)")
    print()
    
    try:
        choice = input("Ihre Wahl (alle/einzeln): ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramm beendet.")
        sys.exit(0)
    
    if choice in ['alle', 'all', 'a']:
        return ['pubmed', 'europepmc', 'openalex']
    
    # Einzelne Datenbanken abfragen
    databases = []
    available_dbs = ['pubmed', 'europepmc', 'openalex']
    
    print()
    print("Verfügbare Datenbanken: pubmed, europepmc, openalex")
    print("(Drücken Sie Enter ohne Eingabe zum Beenden)")
    print()
    
    while True:
        try:
            if databases:
                prompt = f"Weitere Datenbank hinzufügen? (bereits: {', '.join(databases)}): "
            else:
                prompt = "Erste Datenbank: "
            
            db = input(prompt).strip().lower()
            
            if not db:
                # Leere Eingabe = fertig
                break
            
            if db not in available_dbs:
                print(f"⚠ Ungültige Datenbank: {db}")
                print(f"   Verfügbare Optionen: {', '.join(available_dbs)}")
                continue
            
            if db in databases:
                print(f"⚠ {db} wurde bereits hinzugefügt")
                continue
            
            databases.append(db)
            
        except (KeyboardInterrupt, EOFError):
            print("\n\nProgramm beendet.")
            sys.exit(0)
    
    if not databases:
        print("\n⚠ Keine Datenbank ausgewählt. Programm wird beendet.")
        sys.exit(0)
    
    return databases


def main():
    """Hauptfunktion des Deduplication Tools"""
    
    # Datenbank-Auswahl
    databases = get_database_selection()
    
    print()
    print("-" * 70)
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
    print()
    print("=" * 70)
    print("DEDUPLIZIERUNG ERFOLGREICH ABGESCHLOSSEN")
    print("=" * 70)
    print()
    print(f"Dateien gespeichert in: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
