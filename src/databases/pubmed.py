"""PubMed Datenbank-Adapter"""

import requests
import logging
import time
import xml.etree.ElementTree as ET
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
        """
        Sucht PubMed IDs via esearch with pagination support
        
        Args:
            query: Search query
            limit: Maximum number of results (None = all available)
        """
        url = f"{self.BASE_URL}esearch.fcgi"
        headers = {'User-Agent': self.user_agent}
        
        all_ids = []
        batch_size = 10000  # esearch max retmax
        retstart = 0
        
        # First request to get total count
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': 0,  # Just get count first
            'retmode': 'json',
            'tool': 'MedicalDatabaseResearchTool',
            'email': self.email
        }
        
        if self.api_key:
            params['api_key'] = self.api_key
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        esearch_result = data.get('esearchresult', {})
        total_count = int(esearch_result.get('count', '0'))
        
        limit_msg = "alle" if limit is None else str(limit)
        self.logger.info(f"PubMed Datenbank: {total_count} Treffer insgesamt (Limit: {limit_msg})")
        
        # Determine how many IDs to fetch
        target_count = total_count if limit is None else min(limit, total_count)
        
        # Fetch IDs in batches
        while retstart < target_count:
            current_batch = min(batch_size, target_count - retstart)
            
            params['retmax'] = current_batch
            params['retstart'] = retstart
            
            self.logger.debug(f"Fetching IDs: retstart={retstart}, retmax={current_batch}")
            
            if retstart > 0:
                time.sleep(self.rate_limit_delay)
            
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            esearch_result = data.get('esearchresult', {})
            batch_ids = esearch_result.get('idlist', [])
            
            if not batch_ids:
                break
            
            all_ids.extend(batch_ids)
            retstart += len(batch_ids)
            
            self.logger.debug(f"Retrieved {len(batch_ids)} IDs, total: {len(all_ids)}")
        
        return all_ids
    
    def _fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Holt Artikel-Details via efetch (XML) in Batches mit Rate Limiting
        Verwendet XML für vollständige Metadaten inkl. Abstract
        """
        if not pmids:
            return []
        
        all_articles = []
        batch_size = 200  # Max 200 IDs pro Request
        
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
            
            # Use efetch with XML for complete metadata including abstract
            url = f"{self.BASE_URL}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(batch_pmids),
                'retmode': 'xml',
                'rettype': 'abstract',  # Get abstract data
                'tool': 'MedicalDatabaseResearchTool',
                'email': self.email
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            
            # Parse XML response
            articles = self._parse_xml_response(response.text)
            all_articles.extend(articles)
        
        return all_articles
    
    def _parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """Not used - PubMed uses XML parsing directly"""
        return []
    
    def _parse_xml_response(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parsed PubMed efetch XML Response"""
        articles = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # Iterate over all PubmedArticle elements
            for article_elem in root.findall('.//PubmedArticle'):
                try:
                    # Extract PMID
                    pmid_elem = article_elem.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else 'N/A'
                    
                    # Extract title
                    title_elem = article_elem.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else 'N/A'
                    
                    # Extract authors
                    authors_list = []
                    for author in article_elem.findall('.//Author'):
                        lastname = author.find('LastName')
                        forename = author.find('ForeName')
                        if lastname is not None:
                            name = lastname.text
                            if forename is not None:
                                name = f"{forename.text} {name}"
                            authors_list.append(name)
                    authors = ', '.join(authors_list) if authors_list else 'N/A'
                    
                    # Extract year
                    year = 'N/A'
                    pub_date = article_elem.find('.//PubDate/Year')
                    if pub_date is not None:
                        year = pub_date.text
                    else:
                        # Try MedlineDate format (e.g., "2024 Jan-Feb")
                        medline_date = article_elem.find('.//PubDate/MedlineDate')
                        if medline_date is not None and medline_date.text:
                            year = medline_date.text.split()[0]
                    
                    # Extract DOI
                    doi = 'N/A'
                    for article_id in article_elem.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'doi':
                            doi = article_id.text
                            break
                    
                    # Extract abstract
                    abstract_parts = []
                    for abstract_text in article_elem.findall('.//Abstract/AbstractText'):
                        # Handle labeled abstracts (Background, Methods, etc.)
                        label = abstract_text.get('Label')
                        text = abstract_text.text or ''
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                    abstract = ' '.join(abstract_parts) if abstract_parts else 'N/A'
                    
                    # Extract journal
                    journal_elem = article_elem.find('.//Journal/Title')
                    venue = journal_elem.text if journal_elem is not None else 'N/A'
                    
                    # Standardize article
                    article = self._standardize_article({
                        'authors': authors,
                        'title': title,
                        'year': year,
                        'doi': doi,
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        'abstract': abstract,
                        'venue': venue
                    })
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse article: {e}")
                    continue
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
        
        return articles
