"""Datei-Handling für Query-Dateien"""

from pathlib import Path
from typing import Optional
from src.config.settings import Settings


class FileHandler:
    """Klasse für Datei-I/O Operationen"""
    
    @staticmethod
    def read_query_file(filename: str) -> Optional[str]:
        """
        Liest Query-String aus Textdatei
        
        Args:
            filename: Name der Query-Datei (z.B. "pubmed.txt")
            
        Returns:
            Query-String oder None bei Fehler
        """
        query_path = Settings.QUERIES_DIR / filename
        
        if not query_path.exists():
            print(f"Fehler: Datei nicht gefunden: {query_path}")
            return None
        
        try:
            with open(query_path, 'r', encoding='utf-8') as f:
                query = f.read().strip()
            
            if not query:
                print(f"Fehler: Query-Datei ist leer: {query_path}")
                return None
            
            return query
            
        except Exception as e:
            print(f"Fehler beim Lesen der Datei: {e}")
            return None
    
    @staticmethod
    def ensure_output_directory(database: str) -> Path:
        """
        Stellt sicher, dass Output-Verzeichnis für Datenbank existiert
        
        Args:
            database: Name der Datenbank
            
        Returns:
            Path zum Output-Verzeichnis
        """
        output_path = Settings.OUTPUT_DIR / database
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
