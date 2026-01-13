"""PubMed Datenbank-Adapter"""

import requests
import logging
import time
from typing import List, Dict, Any
from src.databases.base_adapter import BaseAdapter
from src.config.settings import Settings


class PubMedAdapter(BaseAdapter):
    """Adapter für PubMed Datenbank (NCBI E-utilities)"""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    def __init__(self, logger: logging.Logger):
        super().__init__(logger)
        # Use NCBI_API_KEY, fallback to PUBMED_API_KEY for legacy support
        self.api_key = Settings.NCBI_API_KEY or Settings.PUBMED_API_KEY
        self.email = Settings.NCBI_EMAIL
        
        # Rate limiting: 3 req/sec without key, 10 req/sec with key
        self.rate_limit_delay = 0.11 if self.api_key else 0.34
        
        # User-Agent as per NCBI guidelines
        self.user_agent = f"MedicalDatabaseResearchTool/1.0 ({self.email})"
        
        self.logger.info(f"PubMed Adapter initialized with API key: {'Yes' if self.api_key else 'No'}")
        self.logger.info(f"Rate limit: {1/self.rate_limit_delay:.1f} requests/second")
    
    def search(self, query: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Führt PubMed-Suche durch
        
        Args:
            query: PubMed Query-String
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von Artikel-Dictionaries
        """
        self.logger.info(f"Starte PubMed-Suche mit Query: {query[:100]}...")
        
        try:
            # Schritt 1: esearch - IDs holen
            pmids = self._search_ids(query, limit)
            
            if not pmids:
                self.logger.warning("Keine PubMed IDs gefunden")
                return []
            
            self.logger.info(f"{len(pmids)} PubMed IDs gefunden")
            
            # Schritt 2: efetch - Artikel-Details holen
            articles = self._fetch_details(pmids)
            
            self.logger.info(f"{len(articles)} Artikel abgerufen")
            return articles
            
        except Exception as e:
            self.logger.error(f"PubMed-Suche fehlgeschlagen: {e}")
            return []
    
    def _search_ids(self, query: str, limit: int) -> List[str]:
        """Sucht PubMed IDs via esearch"""
        url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': limit,
            'retmode': 'json',
            'tool': 'MedicalDatabaseResearchTool',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        headers = {'User-Agent': self.user_agent}
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get('esearchresult', {}).get('idlist', [])
    
    def _fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Holt Artikel-Details via efetch in Batches mit Rate Limiting"""
        if not pmids:
            return []
        
        all_articles = []
        batch_size = 200  # Max 200 IDs pro Request (URL-Längen-Limit)
        
        headers = {'User-Agent': self.user_agent}
        
        # IDs in Batches aufteilen
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            batch_num = i//batch_size + 1
            self.logger.debug(f"Fetching batch {batch_num}: {len(batch_pmids)} IDs")
            
            # Rate limiting: Sleep between requests (except first)
            if i > 0:
                time.sleep(self.rate_limit_delay)
                self.logger.debug(f"Rate limit delay: {self.rate_limit_delay}s")
            
            url = f"{self.BASE_URL}esummary.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'retmode': 'json',
                'tool': 'MedicalDatabaseResearchTool',
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            articles = self._parse_response(data)
            all_articles.extend(articles)
        
        return all_articles
    
    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parsed PubMed API Response"""
        articles = []
        result = response.get('result', {})
        
        for pmid in result.get('uids', []):
            if pmid in result:
                article_data = result[pmid]
                
                # Autoren zusammensetzen
                authors = ', '.join([
                    author.get('name', '') 
                    for author in article_data.get('authors', [])
                ])
                
                # Artikel standardisieren
                article = self._standardize_article({
                    'authors': authors if authors else 'N/A',
                    'title': article_data.get('title', 'N/A'),
                    'year': article_data.get('pubdate', 'N/A').split()[0] if article_data.get('pubdate') else 'N/A',
                    'doi': article_data.get('elocationid', 'N/A').replace('doi: ', ''),
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'abstract': 'N/A',  # Abstract benötigt separaten efetch-Call
                    'venue': article_data.get('fulljournalname', 'N/A')
                })
                
                articles.append(article)
        
        return articles
