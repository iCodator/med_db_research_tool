"""Export-Funktionen für CSV und JSON"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class Exporter:
    """Klasse für Export-Operationen"""
    
    @staticmethod
    def export_to_csv(results: List[Dict[str, Any]], output_path: Path, database: str) -> Path:
        """
        Exportiert Ergebnisse als CSV-Datei
        
        Args:
            results: Liste von Artikeln (Dictionaries)
            output_path: Pfad zum Output-Verzeichnis
            database: Name der Datenbank
            
        Returns:
            Path zur CSV-Datei oder None bei Fehler
        """
        if not results:
            print("Keine Ergebnisse zum Exportieren.")
            return None
        
        try:
            # Timestamp für Dateiname (ISO-Format für bessere Lesbarkeit)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_file = output_path / f"{database}_{timestamp}.csv"
            
            # CSV schreiben mit selektivem Quoting (title und abstract immer mit "", rest ohne)
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                # Header schreiben
                f.write('authors,title,year,doi,url,abstract\n')
                
                # Daten schreiben mit selektivem Quoting
                for article in results:
                    authors = article.get('authors', 'N/A')
                    title = article.get('title', 'N/A')
                    year = article.get('year', 'N/A')
                    doi = article.get('doi', 'N/A')
                    url = article.get('url', 'N/A')
                    abstract = article.get('abstract', 'N/A')
                    
                    # Escape quotes in title and abstract (double them)
                    title_quoted = '"' + str(title).replace('"', '""') + '"'
                    abstract_quoted = '"' + str(abstract).replace('"', '""') + '"'
                    
                    # Authors mit Quoting wenn nötig (enthält oft Kommas)
                    if ',' in str(authors) or '"' in str(authors) or '\n' in str(authors):
                        authors_quoted = '"' + str(authors).replace('"', '""') + '"'
                    else:
                        authors_quoted = str(authors)
                    
                    # Zeile zusammenbauen
                    line = f'{authors_quoted},{title_quoted},{year},{doi},{url},{abstract_quoted}\n'
                    f.write(line)
            
            file_size = csv_file.stat().st_size / 1024
            print(f"✓ CSV exportiert: {csv_file}")
            print(f"  Größe: {file_size:.1f} KB")
            return csv_file
            
        except Exception as e:
            print(f"Fehler beim CSV-Export: {e}")
            return None
    
    @staticmethod
    def export_to_json(results: List[Dict[str, Any]], output_path: Path, 
                      database: str, query: str) -> Path:
        """
        Exportiert Ergebnisse als JSON-Datei
        
        Args:
            results: Liste von Artikeln (Dictionaries)
            output_path: Pfad zum Output-Verzeichnis
            database: Name der Datenbank
            query: Original Query-String
            
        Returns:
            Path zur JSON-Datei oder None bei Fehler
        """
        if not results:
            print("Keine Ergebnisse zum Exportieren.")
            return None
        
        try:
            # Timestamp für Dateiname (ISO-Format für bessere Lesbarkeit)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            json_file = output_path / f"{database}_{timestamp}.json"
            
            # JSON-Struktur erstellen
            data = {
                "metadata": {
                    "database": database,
                    "query": query,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_results": len(results),
                    "version": "1.0.0"
                },
                "articles": results
            }
            
            # JSON schreiben
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            file_size = json_file.stat().st_size / 1024
            print(f"✓ JSON exportiert: {json_file}")
            print(f"  Größe: {file_size:.1f} KB")
            return json_file
            
        except Exception as e:
            print(f"Fehler beim JSON-Export: {e}")
            return None
