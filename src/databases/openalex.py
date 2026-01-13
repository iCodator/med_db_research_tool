"""OpenAlex Datenbank-Adapter"""

import requests
import logging
import time
from typing import List, Dict, Any
from src.databases.base_adapter import BaseAdapter
from src.config.settings import Settings


class OpenAlexAdapter(BaseAdapter):
    """Adapter für OpenAlex Datenbank"""
    
    BASE_URL = "https://api.openalex.org/works"
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        self.email = Settings.OPENALEX_EMAIL
        # OpenAlex: polite pool (with mailto) = 10 req/sec, no mailto = 5 req/sec
        self.rate_limit_delay = 0.11 if self.email else 0.21
        self.logger.info(f"OpenAlex Adapter initialized with email: {'Yes' if self.email else 'No (slower rate)'}")
        self.logger.info(f"Rate limit: {1/self.rate_limit_delay:.1f} requests/second")
    
    def search(self, query: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Führt OpenAlex-Suche durch
        
        Args:
            query: OpenAlex Query-String (filter format or simple terms)
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von Artikel-Dictionaries
        """
        # Auto-convert simple queries to filter format
        if not query.startswith('default.search:') and not ',' in query:
            # Simple query like "periodontitis OR disease" → default.search:periodontitis disease
            query = f"default.search:{query}"
            self.logger.debug(f"Auto-converted to filter format: {query[:100]}...")
        
        self.logger.info(f"Starte OpenAlex-Suche mit Query: {query[:100]}...")
        
        try:
            all_articles = []
            per_page = 200  # OpenAlex max per page
            page = 1
            
            while len(all_articles) < limit:
                # Prepare request
                params = {
                    'filter': query,
                    'per-page': min(per_page, limit - len(all_articles)),
                    'page': page
                }
                
                # Add mailto for polite pool (faster rate limits)
                if self.email:
                    params['mailto'] = self.email
                
                self.logger.debug(f"Fetching page {page}: per-page={params['per-page']}")
                
                # Make request
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Log total hit count on first request
                if page == 1:
                    total_count = data.get('meta', {}).get('count', 0)
                    self.logger.info(f"OpenAlex Datenbank: {total_count} Treffer insgesamt (Limit: {limit})")
                
                # Parse results
                articles = self._parse_response(data)
                
                if not articles:
                    self.logger.info("Keine weiteren Ergebnisse")
                    break
                
                all_articles.extend(articles)
                self.logger.debug(f"Abgerufen: {len(articles)} Artikel, Gesamt: {len(all_articles)}")
                
                # Check if we have more pages
                meta = data.get('meta', {})
                if page >= meta.get('per_page', 1):
                    # Check if there are more results
                    if len(all_articles) >= meta.get('count', 0):
                        self.logger.info("Alle verfügbaren Ergebnisse abgerufen")
                        break
                
                page += 1
                
                # Rate limiting
                if len(all_articles) < limit:
                    time.sleep(self.rate_limit_delay)
            
            self.logger.info(f"{len(all_articles)} Artikel von OpenAlex abgerufen")
            return all_articles[:limit]  # Ensure we don't exceed limit
            
        except Exception as e:
            self.logger.error(f"OpenAlex-Suche fehlgeschlagen: {e}")
            return []
    
    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parsed OpenAlex API Response"""
        articles = []
        
        results = response.get('results', [])
        
        for result in results:
            # Extract authors
            authors = self._extract_authors(result.get('authorships', []))
            
            # Extract venue/journal
            primary_location = result.get('primary_location', {})
            venue = 'N/A'
            if primary_location and primary_location.get('source'):
                venue = primary_location['source'].get('display_name', 'N/A')
            
            # Extract DOI
            doi = result.get('doi', 'N/A')
            if doi and doi.startswith('https://doi.org/'):
                doi = doi.replace('https://doi.org/', '')
            
            # Build URL (prefer DOI, fallback to OpenAlex URL)
            url = result.get('doi', result.get('id', 'N/A'))
            
            # Extract abstract (simplified - OpenAlex uses inverted index)
            abstract = self._extract_abstract(result.get('abstract_inverted_index'))
            
            # Standardize article
            article = self._standardize_article({
                'authors': authors,
                'title': result.get('display_name', result.get('title', 'N/A')),
                'year': str(result.get('publication_year', 'N/A')),
                'doi': doi,
                'url': url,
                'abstract': abstract,
                'venue': venue
            })
            
            articles.append(article)
        
        return articles
    
    def _extract_authors(self, authorships: List[Dict[str, Any]]) -> str:
        """Extrahiert und formatiert Autorenliste"""
        if not authorships:
            return 'N/A'
        
        authors = []
        for authorship in authorships:
            author = authorship.get('author', {})
            display_name = author.get('display_name', '')
            if display_name:
                authors.append(display_name)
        
        return ', '.join(authors) if authors else 'N/A'
    
    def _extract_abstract(self, inverted_index: Dict[str, List[int]]) -> str:
        """
        Extrahiert Abstract aus OpenAlex inverted index format
        
        OpenAlex stores abstracts as inverted index for efficiency.
        We reconstruct the text (simplified version).
        """
        if not inverted_index:
            return 'N/A'
        
        try:
            # Reconstruct text from inverted index
            words = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    words.append((pos, word))
            
            # Sort by position and join
            words.sort(key=lambda x: x[0])
            abstract = ' '.join([word for _, word in words])
            
            return abstract if abstract else 'N/A'
        except Exception as e:
            self.logger.debug(f"Failed to extract abstract: {e}")
            return 'N/A'
