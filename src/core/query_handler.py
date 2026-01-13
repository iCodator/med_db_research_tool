"""Query-Handler - Orchestriert den gesamten Workflow"""

import logging
from typing import Optional
from src.config.settings import Settings
from src.utils.file_handler import FileHandler
from src.utils.exporter import Exporter


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
        
        # 3. Query validieren (optional - für jetzt überspringen)
        # TODO: Parser-Validierung implementieren
        
        # 4. Datenbank-Adapter initialisieren und Suche durchführen
        adapter = self._get_adapter(db_name)
        if not adapter:
            self.logger.error(f"Adapter für {db_name} konnte nicht initialisiert werden")
            return False
        
        print("\nStarte Suche...")
        results = adapter.search(query)
        
        if not results:
            self.logger.warning("Keine Ergebnisse gefunden")
            print("Keine Ergebnisse gefunden.")
            return False
        
        self.logger.info(f"{len(results)} Ergebnisse gefunden")
        print(f"\n✓ {len(results)} Artikel gefunden")
        
        # 5. Ergebnisse exportieren
        output_path = self.file_handler.ensure_output_directory(db_name)
        
        print("\nExportiere Ergebnisse...")
        csv_success = self.exporter.export_to_csv(results, output_path, db_name)
        json_success = self.exporter.export_to_json(results, output_path, db_name, query)
        
        if csv_success and json_success:
            self.logger.info("Export erfolgreich abgeschlossen")
            return True
        else:
            self.logger.error("Export fehlgeschlagen")
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
