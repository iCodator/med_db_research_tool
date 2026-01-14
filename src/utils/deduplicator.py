"""Deduplicator - Entfernt Duplikate über mehrere Datenbanken hinweg"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
from datetime import datetime
from collections import defaultdict


class Deduplicator:
    """Klasse für Cross-Database Deduplication"""
    
    # Priorität der Datenbanken (bei Duplikaten wird höchste Priorität behalten)
    DATABASE_PRIORITY = {
        'pubmed': 1,
        'europepmc': 2,
        'openalex': 3
    }
    
    def __init__(self, output_base_dir: Path):
        """
        Args:
            output_base_dir: Basis-Output-Verzeichnis (z.B. 'output/')
        """
        self.output_base_dir = output_base_dir
        self.stats = {
            'files_found': 0,
            'articles_loaded': 0,
            'duplicates_removed': 0,
            'unique_articles': 0
        }
    
    def collect_json_files(self, databases: List[str]) -> Dict[str, List[Path]]:
        """
        Sammelt alle JSON-Files aus den angegebenen Datenbank-Verzeichnissen
        
        Args:
            databases: Liste von Datenbanknamen (z.B. ['pubmed', 'europepmc'])
            
        Returns:
            Dict mit Datenbank -> Liste von JSON-File-Pfaden
        """
        json_files = {}
        
        for db in databases:
            db_dir = self.output_base_dir / db
            if not db_dir.exists():
                print(f"⚠ Verzeichnis nicht gefunden: {db_dir}")
                json_files[db] = []
                continue
            
            # Rekursiv alle JSON-Files finden (auch in Subfoldern)
            files = list(db_dir.rglob('*.json'))
            json_files[db] = files
            self.stats['files_found'] += len(files)
            
            print(f"├─ {db}: {len(files)} JSON-File{'s' if len(files) != 1 else ''} gefunden")
        
        return json_files
    
    def load_articles(self, json_files: Dict[str, List[Path]]) -> List[Dict[str, Any]]:
        """
        Lädt alle Artikel aus den JSON-Files
        
        Args:
            json_files: Dict mit Datenbank -> Liste von JSON-Files
            
        Returns:
            Liste aller Artikel mit 'source_database' Feld
        """
        all_articles = []
        
        for database, files in json_files.items():
            for json_file in files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        articles = data.get('articles', [])
                        
                        # Füge Quelldatenbank zu jedem Artikel hinzu
                        for article in articles:
                            article['source_database'] = database
                            all_articles.append(article)
                        
                        self.stats['articles_loaded'] += len(articles)
                
                except Exception as e:
                    print(f"⚠ Fehler beim Laden von {json_file}: {e}")
        
        return all_articles
    
    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Entfernt Duplikate basierend auf (authors, title, year)
        Bei Duplikaten: Behalte Artikel mit höchster Priorität
        
        Args:
            articles: Liste aller Artikel (mit 'source_database' Feld)
            
        Returns:
            Liste eindeutiger Artikel
        """
        # Gruppiere Artikel nach (authors, title, year)
        groups = defaultdict(list)
        
        for article in articles:
            # Normalisiere Schlüssel-Felder
            authors = (article.get('authors') or '').lower().strip()
            title = (article.get('title') or '').lower().strip()
            year = (article.get('year') or '').strip()
            
            key = (authors, title, year)
            groups[key].append(article)
        
        # Für jede Gruppe: Behalte Artikel mit höchster Priorität
        unique_articles = []
        duplicates_count = 0
        
        for key, group_articles in groups.items():
            if len(group_articles) == 1:
                # Kein Duplikat
                unique_articles.append(group_articles[0])
            else:
                # Duplikat gefunden - wähle nach Priorität
                duplicates_count += len(group_articles) - 1
                
                # Sortiere nach Datenbank-Priorität
                sorted_articles = sorted(
                    group_articles,
                    key=lambda a: self.DATABASE_PRIORITY.get(
                        a.get('source_database', ''), 
                        999
                    )
                )
                
                # Behalte den mit höchster Priorität (niedrigste Nummer)
                unique_articles.append(sorted_articles[0])
        
        self.stats['duplicates_removed'] = duplicates_count
        self.stats['unique_articles'] = len(unique_articles)
        
        return unique_articles
    
    def export_results(self, 
                      articles: List[Dict[str, Any]], 
                      databases: List[str],
                      output_dir: Path) -> Tuple[Path, Path]:
        """
        Exportiert deduplizierte Ergebnisse als CSV und JSON
        
        Args:
            articles: Liste eindeutiger Artikel
            databases: Liste der durchsuchten Datenbanken
            output_dir: Output-Verzeichnis
            
        Returns:
            (csv_path, json_path) Tuple
        """
        # Timestamp für Dateinamen
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Datenbankname für Filename
        if len(databases) == 3:  # Alle Datenbanken
            db_name = "all"
        else:
            db_name = "-".join(sorted(databases))
        
        # Stelle sicher dass Output-Verzeichnis existiert
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV- und JSON-Unterverzeichnisse erstellen
        csv_dir = output_dir / "csv"
        json_dir = output_dir / "json"
        csv_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)
        
        # Dateinamen
        csv_file = csv_dir / f"dedup_{db_name}_{timestamp}.csv"
        json_file = json_dir / f"dedup_{db_name}_{timestamp}.json"
        
        # Export CSV mit selektivem Quoting
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # Header schreiben
            f.write('authors,title,year,doi,url,abstract,source_database\n')
            
            # Daten schreiben
            for article in articles:
                authors = article.get('authors', 'N/A')
                title = article.get('title', 'N/A')
                year = article.get('year', 'N/A')
                doi = article.get('doi', 'N/A')
                url = article.get('url', 'N/A')
                abstract = article.get('abstract', 'N/A')
                source_db = article.get('source_database', 'N/A')
                
                # Quote title and abstract (escape internal quotes)
                title_quoted = '"' + str(title).replace('"', '""') + '"'
                abstract_quoted = '"' + str(abstract).replace('"', '""') + '"'
                
                # Quote authors if contains comma
                if ',' in str(authors) or '"' in str(authors) or '\n' in str(authors):
                    authors_quoted = '"' + str(authors).replace('"', '""') + '"'
                else:
                    authors_quoted = str(authors)
                
                # Zeile zusammenbauen
                line = f'{authors_quoted},{title_quoted},{year},{doi},{url},{abstract_quoted},{source_db}\n'
                f.write(line)
        
        # Export JSON
        data = {
            "metadata": {
                "databases": databases,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_results": len(articles),
                "query_type": "cross-database deduplication",
                "version": "1.0.0",
                "statistics": {
                    "files_processed": self.stats['files_found'],
                    "articles_loaded": self.stats['articles_loaded'],
                    "duplicates_removed": self.stats['duplicates_removed'],
                    "unique_articles": self.stats['unique_articles']
                }
            },
            "articles": articles
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Dateigrößen
        csv_size = csv_file.stat().st_size / 1024
        json_size = json_file.stat().st_size / 1024
        
        print(f"\n✓ CSV exportiert: {csv_file.name}")
        print(f"  Größe: {csv_size:.1f} KB")
        print(f"✓ JSON exportiert: {json_file.name}")
        print(f"  Größe: {json_size:.1f} KB")
        
        return (csv_file, json_file)
    
    def get_stats(self) -> Dict[str, int]:
        """Gibt Statistiken zurück"""
        return self.stats.copy()
