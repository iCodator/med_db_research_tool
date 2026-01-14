"""Deduplicator - Entfernt Duplikate über mehrere Datenbanken hinweg"""

import json
import html
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set, Optional
from datetime import datetime
from collections import defaultdict
import logging


class Deduplicator:
    """Klasse für Cross-Database Deduplication"""
    
    # Priorität der Datenbanken (bei Duplikaten wird höchste Priorität behalten)
    DATABASE_PRIORITY = {
        'pubmed': 1,
        'europepmc': 2,
        'openalex': 3
    }
    
    def __init__(self, output_base_dir: Path, logger: Optional[logging.Logger] = None):
        """
        Args:
            output_base_dir: Basis-Output-Verzeichnis (z.B. 'output/')
            logger: Optional Logger-Instanz für Logging
        """
        self.output_base_dir = output_base_dir
        self.logger = logger
        self.stats = {
            'files_found': 0,
            'articles_loaded': 0,
            'duplicates_removed': 0,
            'unique_articles': 0
        }
        # Pro-Datenbank-Statistiken
        self.per_database_stats = defaultdict(lambda: {
            'files_found': 0,
            'articles_loaded': 0,
            'duplicates_found': 0,
            'unique_articles': 0
        })
        # Duplikate-Details (für detailliertes Logging)
        self.duplicates_details = []
    
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
            all_json_files = list(db_dir.rglob('*.json'))
            
            # Spezielle Behandlung für OpenAlex: Nur finale Dateien (openalex_*.json)
            # Ignoriere Query-Zwischendateien
            if db == 'openalex':
                files = [f for f in all_json_files if f.name.startswith('openalex_')]
            else:
                files = all_json_files
            
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
            db_articles_count = 0
            self.per_database_stats[database]['files_found'] = len(files)
            
            for json_file in files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        articles = data.get('articles', [])
                        
                        # Füge Quelldatenbank zu jedem Artikel hinzu
                        for article in articles:
                            article['source_database'] = database
                            all_articles.append(article)
                        
                        db_articles_count += len(articles)
                        self.stats['articles_loaded'] += len(articles)
                
                except Exception as e:
                    print(f"⚠ Fehler beim Laden von {json_file}: {e}")
            
            self.per_database_stats[database]['articles_loaded'] = db_articles_count
            if self.logger:
                self.logger.info(f"{database}: {db_articles_count} Artikel geladen")
        
        return all_articles
    
    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normalisiert Titel für besseren Duplikats-Vergleich
        
        Args:
            title: Artikel-Titel
            
        Returns:
            Normalisierter Titel
        """
        if not title:
            return ''
        
        # HTML-Entities dekodieren (&amp; → &, &trade; → ™, etc.)
        title = html.unescape(title)
        
        # Satzzeichen am Ende entfernen
        title = title.rstrip('.!?;:,')
        
        # Mehrfache Leerzeichen normalisieren
        title = ' '.join(title.split())
        
        # Lowercase & trim
        return title.lower().strip()
    
    @staticmethod
    def normalize_abstract(abstract: str, max_length: int = 200) -> str:
        """
        Normalisiert Abstract für Ähnlichkeits-Vergleich
        
        Args:
            abstract: Artikel-Abstract
            max_length: Maximale Länge für Vergleich
            
        Returns:
            Normalisierter Abstract (gekürzt)
        """
        if not abstract or abstract == 'N/A':
            return ''
        
        # HTML-Entities dekodieren
        abstract = html.unescape(abstract)
        
        # Whitespace normalisieren
        abstract = ' '.join(abstract.split())
        
        # Lowercase, trim, kürzen
        return abstract.lower().strip()[:max_length]
    
    @staticmethod
    def text_similarity(text1: str, text2: str) -> float:
        """
        Berechnet Ähnlichkeit zwischen zwei Texten (Jaccard-Ähnlichkeit)
        
        Args:
            text1: Erster Text
            text2: Zweiter Text
            
        Returns:
            Ähnlichkeits-Score (0.0 - 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Wortbasierter Vergleich
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def deduplicate(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Entfernt Duplikate basierend auf (authors, normalized_title)
        Mit intelligenter Jahr-Prüfung über DOI/URL/Abstract
        Bei Duplikaten: Behalte Artikel mit höchster Priorität
        
        Args:
            articles: Liste aller Artikel (mit 'source_database' Feld)
            
        Returns:
            Liste eindeutiger Artikel
        """
        # STUFE 1: Gruppiere Artikel nach (authors, normalized_title) - OHNE Jahr
        groups = defaultdict(list)
        
        for article in articles:
            # Normalisiere Schlüssel-Felder
            authors = (article.get('authors') or '').lower().strip()
            title_norm = self.normalize_title(article.get('title') or '')
            
            key = (authors, title_norm)
            groups[key].append(article)
        
        # STUFE 2: Für jede Gruppe - intelligente Duplikats-Prüfung
        unique_articles = []
        duplicates_count = 0
        db_duplicates = defaultdict(int)
        
        for key, group_articles in groups.items():
            if len(group_articles) == 1:
                # Kein Duplikat
                unique_articles.append(group_articles[0])
            else:
                # Mehrere Artikel mit gleichen Autoren und Titel
                # Gruppiere nach Jahr
                year_groups = defaultdict(list)
                for article in group_articles:
                    year = (article.get('year') or '').strip()
                    year_groups[year].append(article)
                
                # Prüfe jede Jahr-Gruppe
                if len(year_groups) == 1:
                    # Fall A: Alle haben dasselbe Jahr → DUPLIKATE
                    sorted_articles = sorted(
                        group_articles,
                        key=lambda a: self.DATABASE_PRIORITY.get(
                            a.get('source_database', ''), 999
                        )
                    )
                    kept_article = sorted_articles[0]
                    unique_articles.append(kept_article)
                    duplicates_count += len(sorted_articles) - 1
                    
                    # Logging für Duplikate
                    for article in sorted_articles[1:]:
                        self._log_duplicate(article, kept_article, db_duplicates)
                
                else:
                    # Fall B: Unterschiedliche Jahre → intelligente Prüfung
                    potential_duplicates = []
                    
                    # Gruppiere Artikel die potenziell Duplikate sind
                    processed_indices = set()
                    
                    for i, article1 in enumerate(group_articles):
                        if i in processed_indices:
                            continue
                        
                        duplicate_group = [article1]
                        
                        for j, article2 in enumerate(group_articles[i+1:], start=i+1):
                            if j in processed_indices:
                                continue
                            
                            # Prüfe ob Duplikat trotz unterschiedlicher Jahre
                            if self._are_duplicates_despite_year_difference(article1, article2):
                                duplicate_group.append(article2)
                                processed_indices.add(j)
                        
                        # Behalte bestes Artikel aus Duplikat-Gruppe
                        if len(duplicate_group) > 1:
                            sorted_group = sorted(
                                duplicate_group,
                                key=lambda a: self.DATABASE_PRIORITY.get(
                                    a.get('source_database', ''), 999
                                )
                            )
                            kept_article = sorted_group[0]
                            unique_articles.append(kept_article)
                            duplicates_count += len(sorted_group) - 1
                            
                            # Logging
                            for article in sorted_group[1:]:
                                self._log_duplicate(article, kept_article, db_duplicates,
                                                   reason="Jahr-Konflikt (DOI/URL/Abstract)")
                        else:
                            unique_articles.append(article1)
                        
                        processed_indices.add(i)
        
        # Update Statistiken
        for db in self.per_database_stats.keys():
            self.per_database_stats[db]['duplicates_found'] = db_duplicates.get(db, 0)
            unique_from_db = sum(1 for a in unique_articles if a.get('source_database') == db)
            self.per_database_stats[db]['unique_articles'] = unique_from_db
        
        self.stats['duplicates_removed'] = duplicates_count
        self.stats['unique_articles'] = len(unique_articles)
        
        if self.logger:
            self.logger.info(f"Deduplizierung abgeschlossen: {duplicates_count} Duplikate entfernt")
        
        return unique_articles
    
    def _are_duplicates_despite_year_difference(self, article1: Dict[str, Any], 
                                                article2: Dict[str, Any]) -> bool:
        """
        Prüft ob zwei Artikel Duplikate sind, trotz unterschiedlicher Jahre
        
        Prüfungs-Reihenfolge:
        1. DOI identisch (und beide vorhanden)
        2. URL identisch (und beide vorhanden)
        3. Abstract-Ähnlichkeit > 80%
        
        Args:
            article1: Erster Artikel
            article2: Zweiter Artikel
            
        Returns:
            True wenn Duplikat, False sonst
        """
        # Prüfe DOI
        doi1 = (article1.get('doi') or '').strip()
        doi2 = (article2.get('doi') or '').strip()
        
        if doi1 and doi2 and doi1 != 'N/A' and doi2 != 'N/A':
            if doi1.lower() == doi2.lower():
                return True
            else:
                # Unterschiedliche DOIs → definitiv keine Duplikate
                return False
        
        # Prüfe URL
        url1 = (article1.get('url') or '').strip()
        url2 = (article2.get('url') or '').strip()
        
        if url1 and url2 and url1 != 'N/A' and url2 != 'N/A':
            if url1.lower() == url2.lower():
                return True
            else:
                # Unterschiedliche URLs → definitiv keine Duplikate
                return False
        
        # Prüfe Abstract-Ähnlichkeit (Fallback)
        abstract1 = self.normalize_abstract(article1.get('abstract') or '')
        abstract2 = self.normalize_abstract(article2.get('abstract') or '')
        
        if abstract1 and abstract2:
            similarity = self.text_similarity(abstract1, abstract2)
            return similarity > 0.80
        
        # Keine ausreichenden Informationen → als nicht-Duplikat behandeln
        return False
    
    def _log_duplicate(self, article: Dict[str, Any], kept_article: Dict[str, Any],
                      db_duplicates: Dict[str, int], reason: str = ""):
        """
        Loggt ein Duplikat
        
        Args:
            article: Duplikats-Artikel (wird entfernt)
            kept_article: Behaltener Artikel
            db_duplicates: Duplikats-Zähler pro Datenbank
            reason: Zusätzlicher Grund (optional)
        """
        db = article.get('source_database', 'unknown')
        db_duplicates[db] += 1
        
        authors_orig = article.get('authors') or 'N/A'
        title_orig = article.get('title') or 'N/A'
        year_orig = article.get('year') or 'N/A'
        
        # Kürze Titel auf 40 Zeichen
        title_str = str(title_orig) if title_orig else 'N/A'
        title_short = title_str[:40] + '...' if len(title_str) > 40 else title_str
        
        detail = {
            'database': db,
            'authors': authors_orig,
            'title': title_short,
            'year': year_orig,
            'kept_from': kept_article.get('source_database', 'unknown')
        }
        
        if reason:
            detail['reason'] = reason
        
        self.duplicates_details.append(detail)
    
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
    
    def log_statistics(self, mode: str):
        """
        Loggt Deduplizierungs-Statistiken
        
        Args:
            mode: 'simple' oder 'detailed'
        """
        if not self.logger:
            return
        
        self.logger.info("")
        self.logger.info("="*70)
        self.logger.info("DEDUPLIZIERUNGS-STATISTIKEN")
        self.logger.info("="*70)
        self.logger.info("")
        
        # Globale Statistiken
        self.logger.info("GESAMT:")
        self.logger.info(f"  - Geladene Artikel (total):     {self.stats['articles_loaded']}")
        self.logger.info(f"  - Gefundene Duplikate:          {self.stats['duplicates_removed']}")
        self.logger.info(f"  - Eindeutige Artikel:           {self.stats['unique_articles']}")
        self.logger.info("")
        
        # Pro-Datenbank-Statistiken
        self.logger.info("PRO DATENBANK:")
        self.logger.info("-" * 70)
        
        for db in sorted(self.per_database_stats.keys()):
            stats = self.per_database_stats[db]
            self.logger.info("")
            self.logger.info(f"Datenbank: {db.upper()}")
            self.logger.info(f"  - Anzahl Quellen (geladen):     {stats['articles_loaded']}")
            self.logger.info(f"  - Anzahl Duplikate:             {stats['duplicates_found']}")
            self.logger.info(f"  - Verbleibende eindeutige:      {stats['unique_articles']}")
        
        # Detailliertes Logging: Liste aller Duplikate
        if mode == 'detailed' and self.duplicates_details:
            self.logger.info("")
            self.logger.info("="*70)
            self.logger.info("DETAILLIERTE DUPLIKATE-LISTE")
            self.logger.info("="*70)
            self.logger.info("")
            
            # Gruppiere Duplikate nach Datenbank
            db_dups = defaultdict(list)
            for dup in self.duplicates_details:
                db_dups[dup['database']].append(dup)
            
            for db in sorted(db_dups.keys()):
                dups = db_dups[db]
                self.logger.info(f"Datenbank: {db.upper()} ({len(dups)} Duplikate)")
                self.logger.info("-" * 70)
                
                for i, dup in enumerate(dups, 1):
                    authors = dup['authors']
                    title = dup['title']
                    year = dup['year']
                    kept_from = dup['kept_from']
                    
                    self.logger.info(f"  [{i}] Autor(en): {authors}")
                    self.logger.info(f"      Titel:      {title}")
                    self.logger.info(f"      Jahr:       {year}")
                    self.logger.info(f"      (Behalten von: {kept_from})")
                    
                    if i < len(dups):
                        self.logger.info("")
                
                self.logger.info("")
    
    def get_stats(self) -> Dict[str, int]:
        """Gibt Statistiken zurück"""
        return self.stats.copy()
