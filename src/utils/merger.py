"""Merger für AND-Queries: Kombiniert zwei Ergebnismengen"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime


class ResultMerger:
    """Merged zwei Ergebnismengen mit AND-Logik"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def merge_results(self, 
                     file_a: Path, 
                     file_b: Path,
                     terms_a: List[str],
                     terms_b: List[str],
                     output_dir: Path,
                     database: str) -> Tuple[Path, Path]:
        """
        Merged zwei Ergebnisdateien mit AND-Logik
        
        Args:
            file_a: Ergebnisse von Gruppe A (JSON)
            file_b: Ergebnisse von Gruppe B (JSON)
            terms_a: Begriffe aus Gruppe A (für Validierung)
            terms_b: Begriffe aus Gruppe B (für Validierung)
            output_dir: Output-Verzeichnis
            database: Datenbankname
            
        Returns:
            (csv_path, json_path) tuple
        """
        self.logger.info(f"Merge gestartet: {file_a.name} AND {file_b.name}")
        
        # Load results
        results_a = self._load_json(file_a)
        results_b = self._load_json(file_b)
        
        self.logger.info(f"Geladen: {len(results_a)} Artikel aus A, {len(results_b)} aus B")
        
        # Step 1: Find matching articles (by title + authors)
        matched_articles = self._find_matches(results_a, results_b)
        self.logger.info(f"Schritt 1: {len(matched_articles)} übereinstimmende Artikel gefunden")
        
        # Step 2: Validate content (terms from both groups in title OR abstract)
        validated_articles = self._validate_content(matched_articles, terms_a, terms_b)
        self.logger.info(f"Schritt 2: {len(validated_articles)} Artikel validiert (A AND B in content)")
        
        # Step 3: Deduplicate by (authors, title)
        unique_articles = self._deduplicate(validated_articles)
        duplicates_removed = len(validated_articles) - len(unique_articles)
        self.logger.info(f"Schritt 3: {len(unique_articles)} eindeutige Artikel (entfernte Duplikate: {duplicates_removed})")
        
        # Step 4: Export results
        if unique_articles:
            csv_path, json_path = self._export_results(
                unique_articles, 
                output_dir, 
                database
            )
            return (csv_path, json_path)
        else:
            self.logger.warning("Keine Artikel erfüllen die AND-Bedingungen")
            return (None, None)
    
    def _load_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """Lädt Artikel aus JSON-Datei"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('articles', [])
    
    def _find_matches(self, 
                     results_a: List[Dict],
                     results_b: List[Dict]) -> List[Dict]:
        """
        Findet übereinstimmende Artikel (Title + Authors)
        
        Returns:
            Liste von Artikeln die in BEIDEN Listen vorkommen
        """
        matched = []
        
        for article_a in results_a:
            title_a = (article_a.get('title') or '').lower().strip()
            authors_a = (article_a.get('authors') or '').lower().strip()
            
            for article_b in results_b:
                title_b = (article_b.get('title') or '').lower().strip()
                authors_b = (article_b.get('authors') or '').lower().strip()
                
                # Match by title AND authors
                if title_a == title_b and authors_a == authors_b:
                    matched.append(article_a)
                    break
        
        return matched
    
    def _validate_content(self,
                         articles: List[Dict],
                         terms_a: List[str],
                         terms_b: List[str]) -> List[Dict]:
        """
        Validiert dass Artikel Begriffe aus BEIDEN Gruppen enthalten
        
        Check: (Begriff aus A in [title OR abstract]) AND
               (Begriff aus B in [title OR abstract])
        """
        validated = []
        
        for article in articles:
            # Handle None values properly
            title = (article.get('title') or '').lower()
            abstract = (article.get('abstract') or '').lower()
            content = f"{title} {abstract}"
            
            # Check if at least one term from A is in content
            has_term_a = any(term.lower() in content for term in terms_a)
            
            # Check if at least one term from B is in content
            has_term_b = any(term.lower() in content for term in terms_b)
            
            # Only include if BOTH conditions are met
            if has_term_a and has_term_b:
                validated.append(article)
        
        return validated
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """
        Entfernt Duplikate basierend auf (authors, title)
        
        Args:
            articles: Liste von Artikeln (kann Duplikate enthalten)
            
        Returns:
            Liste ohne Duplikate (behält ersten Treffer)
        """
        seen = set()
        unique_articles = []
        
        for article in articles:
            # Erstelle eindeutigen Key aus authors + title (normalisiert)
            title = (article.get('title') or '').lower().strip()
            authors = (article.get('authors') or '').lower().strip()
            key = (authors, title)
            
            if key not in seen:
                seen.add(key)
                unique_articles.append(article)
        
        return unique_articles
    
    def _export_results(self,
                       articles: List[Dict],
                       output_dir: Path,
                       database: str) -> Tuple[Path, Path]:
        """Exportiert Ergebnisse als CSV und JSON"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV- und JSON-Unterverzeichnisse erstellen
        csv_dir = output_dir / "csv"
        json_dir = output_dir / "json"
        csv_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        csv_file = csv_dir / f"{database}_{timestamp}.csv"
        json_file = json_dir / f"{database}_{timestamp}.json"
        
        # Export CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['authors', 'title', 'year', 'doi', 'url', 'abstract']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                writer.writerow({
                    'authors': article.get('authors', 'N/A'),
                    'title': article.get('title', 'N/A'),
                    'year': article.get('year', 'N/A'),
                    'doi': article.get('doi', 'N/A'),
                    'url': article.get('url', 'N/A'),
                    'abstract': article.get('abstract', 'N/A')
                })
        
        # Export JSON
        data = {
            "metadata": {
                "database": database,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_results": len(articles),
                "query_type": "AND merge",
                "version": "1.0.0"
            },
            "articles": articles
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        csv_size = csv_file.stat().st_size / 1024
        json_size = json_file.stat().st_size / 1024
        
        self.logger.info(f"✓ CSV exportiert: {csv_file} ({csv_size:.1f} KB)")
        self.logger.info(f"✓ JSON exportiert: {json_file} ({json_size:.1f} KB)")
        
        return (csv_file, json_file)
