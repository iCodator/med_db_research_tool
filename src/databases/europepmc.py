"""Europe PMC Datenbank-Adapter"""

import requests
import logging
import time
from typing import List, Dict, Any
from src.databases.base_adapter import BaseAdapter


class EuropePMCAdapter(BaseAdapter):
    """Adapter für Europe PMC Datenbank"""
    
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        # Europe PMC has no strict rate limiting, but we'll be polite
        self.rate_limit_delay = 0.2  # 5 requests/second (polite usage)
        self.logger.info("Europe PMC Adapter initialized")
    
    def search(self, query: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Führt Europe PMC-Suche durch
        
        Args:
            query: Europe PMC Query-String
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von Artikel-Dictionaries
        """
        self.logger.info(f"Starte Europe PMC-Suche mit Query: {query[:100]}...")
        
        try:
            all_articles = []
            page_size = 100  # Europe PMC empfiehlt max 1000, wir nutzen 100
            cursor_mark = "*"  # Start cursor
            
            while len(all_articles) < limit:
                # Prepare request
                params = {
                    'query': query,
                    'format': 'json',
                    'pageSize': min(page_size, limit - len(all_articles)),
                    'cursorMark': cursor_mark
                }
                
                self.logger.debug(f"Fetching page: cursorMark={cursor_mark}, pageSize={params['pageSize']}")
                
                # Make request
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse results
                articles = self._parse_response(data)
                
                if not articles:
                    self.logger.info("Keine weiteren Ergebnisse")
                    break
                
                all_articles.extend(articles)
                self.logger.debug(f"Abgerufen: {len(articles)} Artikel, Gesamt: {len(all_articles)}")
                
                # Check if we have more pages
                next_cursor = data.get('nextCursorMark')
                if not next_cursor or next_cursor == cursor_mark:
                    self.logger.info("Letzte Seite erreicht")
                    break
                
                cursor_mark = next_cursor
                
                # Rate limiting (polite usage)
                if len(all_articles) < limit:
                    time.sleep(self.rate_limit_delay)
            
            self.logger.info(f"{len(all_articles)} Artikel von Europe PMC abgerufen")
            return all_articles[:limit]  # Ensure we don't exceed limit
            
        except Exception as e:
            self.logger.error(f"Europe PMC-Suche fehlgeschlagen: {e}")
            return []
    
    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parsed Europe PMC API Response"""
        articles = []
        
        result_list = response.get('resultList', {})
        results = result_list.get('result', [])
        
        for result in results:
            # Extract and standardize article data
            article = self._standardize_article({
                'authors': result.get('authorString', 'N/A'),
                'title': result.get('title', 'N/A'),
                'year': str(result.get('pubYear', 'N/A')),
                'doi': result.get('doi', 'N/A'),
                'url': self._build_url(result),
                'abstract': result.get('abstractText', 'N/A'),
                'venue': result.get('journalTitle', 'N/A')
            })
            
            articles.append(article)
        
        return articles
    
    def _build_url(self, result: Dict[str, Any]) -> str:
        """Builds the Europe PMC URL for an article"""
        # Prefer PMID for PubMed articles
        pmid = result.get('pmid')
        if pmid:
            return f"https://europepmc.org/article/MED/{pmid}"
        
        # Otherwise use PMC ID
        pmcid = result.get('pmcid')
        if pmcid:
            return f"https://europepmc.org/article/PMC/{pmcid}"
        
        # Fallback to Europe PMC ID
        source = result.get('source', 'MED')
        ext_id = result.get('id', 'N/A')
        return f"https://europepmc.org/article/{source}/{ext_id}"
