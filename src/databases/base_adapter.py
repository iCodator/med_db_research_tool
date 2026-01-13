"""Basis-Adapter-Klasse für Datenbank-Adapter"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAdapter(ABC):
    """Abstrakte Basisklasse für alle Datenbank-Adapter"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    @abstractmethod
    def search(self, query: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Führt Suche in der Datenbank durch
        
        Args:
            query: Query-String
            limit: Maximale Anzahl Ergebnisse
            
        Returns:
            Liste von Artikel-Dictionaries
        """
        pass
    
    @abstractmethod
    def _parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """
        Parsed API-Response zu standardisiertem Format
        
        Args:
            response: Raw API Response
            
        Returns:
            Liste von standardisierten Artikel-Dictionaries
        """
        pass
    
    def _standardize_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardisiert Artikel-Daten zu einheitlichem Format
        
        Returns:
            Dictionary mit Feldern: authors, year, venue, doi, url, abstract
        """
        return {
            'authors': article_data.get('authors', 'N/A'),
            'year': article_data.get('year', 'N/A'),
            'venue': article_data.get('venue', 'N/A'),
            'doi': article_data.get('doi', 'N/A'),
            'url': article_data.get('url', 'N/A'),
            'abstract': article_data.get('abstract', 'N/A')
        }
