"""Query-Handler - Orchestriert den gesamten Workflow"""

import logging
from typing import Optional
from pathlib import Path
from src.config.settings import Settings
from src.utils.file_handler import FileHandler
from src.utils.exporter import Exporter
from src.core.query_splitter import QuerySplitter
from src.utils.merger import ResultMerger


class QueryHandler:
    """Hauptklasse für Query-Verarbeitung"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.file_handler = FileHandler()
        self.exporter = Exporter()
    
    def process_query_file(self, filename: str) -> bool:
        """
        Verarbeitet Query-Datei komplett: Lesen → Validieren → Suchen → Exportieren
        
        Args:
            filename: Name der Query-Datei (z.B. "pubmed.txt")
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        self.logger.info(f"Starte Verarbeitung von: {filename}")
        
        # 1. Datenbankname aus Filename extrahieren
        db_name = Settings.get_database_name(filename)
        if not db_name:
            self.logger.error(f"Ungültiger Dateiname: {filename}")
            print(f"Fehler: Datei muss auf .txt enden")
            return False
        
        if not Settings.is_valid_database(db_name):
            self.logger.error(f"Unbekannte Datenbank: {db_name}")
            print(f"Fehler: Datenbank '{db_name}' wird nicht unterstützt")
            print(f"Unterstützte Datenbanken: {', '.join(Settings.SUPPORTED_DATABASES.keys())}")
            return False
        
        self.logger.info(f"Datenbank erkannt: {db_name}")
        print(f"\nDatenbank: {Settings.SUPPORTED_DATABASES[db_name]['name']}")
        
        # 2. Query aus Datei lesen
        query = self.file_handler.read_query_file(filename)
        if not query:
            self.logger.error("Query konnte nicht gelesen werden")
            return False
        
        self.logger.info(f"Query gelesen: {query[:100]}...")
        print(f"Query: {query[:80]}{'...' if len(query) > 80 else ''}")
        
        # 3. Check for AND-logic (only for OpenAlex)
        if QuerySplitter.has_and_logic(query) and db_name == 'openalex':
            self.logger.info("AND-Logik erkannt - verwende zweistufigen Workflow (OpenAlex)")
            print("\n⚡ AND-Logik erkannt - zweistufiger Workflow (OpenAlex)")
            return self._process_and_query(filename, db_name, query)
        
        # 4. Normale Query-Verarbeitung
        # Datenbank-Adapter initialisieren und Suche durchführen
        adapter = self._get_adapter(db_name)
        if not adapter:
            self.logger.error(f"Adapter für {db_name} konnte nicht initialisiert werden")
            return False
        
        print("\nStarte Suche...")
        results = adapter.search(query, limit=None)
        
        if not results:
            self.logger.warning("Keine Ergebnisse gefunden")
            print("Keine Ergebnisse gefunden.")
            return False
        
        self.logger.info(f"{len(results)} Ergebnisse gefunden")
        print(f"\n✓ {len(results)} Artikel gefunden")
        
        # 5. Ergebnisse exportieren
        output_path = self.file_handler.ensure_output_directory(db_name)
        
        print("\nExportiere Ergebnisse...")
        csv_file = self.exporter.export_to_csv(results, output_path, db_name)
        json_file = self.exporter.export_to_json(results, output_path, db_name, query)
        
        if csv_file and json_file:
            self.logger.info("Export erfolgreich abgeschlossen")
            return True
        else:
            self.logger.error("Export fehlgeschlagen")
            return False
    
    def _process_and_query(self, filename: str, db_name: str, query: str) -> bool:
        """
        Verarbeitet Query mit AND-Logik (zweistufiger Workflow)
        
        Args:
            filename: Query-Dateiname
            db_name: Datenbankname
            query: Vollständiger Query-String
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        # Split query in Gruppe A, B und Zeitraum
        try:
            group_a, group_b, time_range = QuerySplitter.split_query(query)
            terms_a = QuerySplitter.extract_terms_for_validation(group_a)
            terms_b = QuerySplitter.extract_terms_for_validation(group_b)
            
            term_a_name = QuerySplitter.extract_first_term(group_a)
            term_b_name = QuerySplitter.extract_first_term(group_b)
            
            # Add time range to queries if present (for OpenAlex)
            if time_range and db_name == 'openalex':
                group_a = f"{group_a},publication_year:{time_range}"
                group_b = f"{group_b},publication_year:{time_range}"
                self.logger.info(f"Zeitraum: {time_range}")
                print(f"├─ Gruppe A: {term_a_name}")
                print(f"├─ Gruppe B: {term_b_name}")
                print(f"└─ Zeitraum: {time_range}")
            else:
                self.logger.info(f"Gruppe A: {term_a_name} ({len(terms_a)} Begriffe)")
                self.logger.info(f"Gruppe B: {term_b_name} ({len(terms_b)} Begriffe)")
                print(f"├─ Gruppe A: {term_a_name}")
                print(f"└─ Gruppe B: {term_b_name}")
            
        except ValueError as e:
            self.logger.error(f"Query-Split fehlgeschlagen: {e}")
            print(f"Fehler beim Parsen der AND-Query: {e}")
            return False
        
        # Get adapter
        adapter = self._get_adapter(db_name)
        if not adapter:
            return False
        
        output_base = self.file_handler.ensure_output_directory(db_name)
        
        # Step 1: Query A (unbegrenzt)
        print(f"\n[1/3] Suche Gruppe A ({term_a_name})...")
        results_a = adapter.search(group_a, limit=None)
        if not results_a:
            self.logger.warning("Keine Ergebnisse für Gruppe A")
            print("❌ Keine Ergebnisse für Gruppe A gefunden")
            return False
        
        print(f"✓ {len(results_a)} Artikel gefunden")
        file_a_csv = self.exporter.export_to_csv(results_a, output_base, term_a_name + "_A")
        file_a_json = self.exporter.export_to_json(results_a, output_base, term_a_name + "_A", group_a)
        
        # Step 2: Query B (unbegrenzt)
        print(f"\n[2/3] Suche Gruppe B ({term_b_name})...")
        results_b = adapter.search(group_b, limit=None)
        if not results_b:
            self.logger.warning("Keine Ergebnisse für Gruppe B")
            print("❌ Keine Ergebnisse für Gruppe B gefunden")
            return False
        
        print(f"✓ {len(results_b)} Artikel gefunden")
        file_b_csv = self.exporter.export_to_csv(results_b, output_base, term_b_name + "_B")
        file_b_json = self.exporter.export_to_json(results_b, output_base, term_b_name + "_B", group_b)
        
        # Step 3: Merge results
        print(f"\n[3/3] Merge mit AND-Logik...")
        merger = ResultMerger(self.logger)
        
        try:
            csv_path, json_path = merger.merge_results(
                file_a_json,
                file_b_json,
                terms_a,
                terms_b,
                output_base,
                db_name
            )
            
            if csv_path and json_path:
                print(f"\n✓ Merge erfolgreich!")
                print(f"  → {csv_path.name}")
                print(f"  → {json_path.name}")
                return True
            else:
                print("\n❌ Keine Artikel erfüllen AND-Bedingung")
                return False
                
        except Exception as e:
            self.logger.error(f"Merge fehlgeschlagen: {e}")
            print(f"\n❌ Merge-Fehler: {e}")
            return False
    
    def _get_adapter(self, db_name: str):
        """
        Initialisiert passenden Datenbank-Adapter
        
        Args:
            db_name: Name der Datenbank
            
        Returns:
            Adapter-Instanz oder None
        """
        try:
            if db_name == "pubmed":
                from src.databases.pubmed import PubMedAdapter
                return PubMedAdapter(self.logger)
            elif db_name == "europepmc":
                from src.databases.europepmc import EuropePMCAdapter
                return EuropePMCAdapter(self.logger)
            elif db_name == "openalex":
                from src.databases.openalex import OpenAlexAdapter
                return OpenAlexAdapter(self.logger)
            else:
                return None
        except ImportError as e:
            self.logger.error(f"Adapter konnte nicht importiert werden: {e}")
            return None
