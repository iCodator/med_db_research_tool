"""Export-Funktionen für CSV und JSON"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class Exporter:
    """Klasse für Export-Operationen"""
    
    @staticmethod
    def export_to_csv(results: List[Dict[str, Any]], output_path: Path, database: str) -> bool:
        """
        Exportiert Ergebnisse als CSV-Datei
        
        Args:
            results: Liste von Artikeln (Dictionaries)
            output_path: Pfad zum Output-Verzeichnis
            database: Name der Datenbank
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not results:
            print("Keine Ergebnisse zum Exportieren.")
            return False
        
        try:
            # Timestamp für Dateiname
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            csv_file = output_path / f"{database}_{timestamp}.csv"
            
            # CSV schreiben
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['authors', 'title', 'year', 'doi', 'url', 'abstract', 'venue']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for article in results:
                    writer.writerow({
                        'authors': article.get('authors', 'N/A'),
                        'title': article.get('title', 'N/A'),
                        'year': article.get('year', 'N/A'),
                        'doi': article.get('doi', 'N/A'),
                        'url': article.get('url', 'N/A'),
                        'abstract': article.get('abstract', 'N/A'),
                        'venue': article.get('venue', 'N/A')
                    })
            
            file_size = csv_file.stat().st_size / 1024
            print(f"✓ CSV exportiert: {csv_file}")
            print(f"  Größe: {file_size:.1f} KB")
            return True
            
        except Exception as e:
            print(f"Fehler beim CSV-Export: {e}")
            return False
    
    @staticmethod
    def export_to_json(results: List[Dict[str, Any]], output_path: Path, 
                      database: str, query: str) -> bool:
        """
        Exportiert Ergebnisse als JSON-Datei
        
        Args:
            results: Liste von Artikeln (Dictionaries)
            output_path: Pfad zum Output-Verzeichnis
            database: Name der Datenbank
            query: Original Query-String
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not results:
            print("Keine Ergebnisse zum Exportieren.")
            return False
        
        try:
            # Timestamp für Dateiname
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
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
            return True
            
        except Exception as e:
            print(f"Fehler beim JSON-Export: {e}")
            return False
