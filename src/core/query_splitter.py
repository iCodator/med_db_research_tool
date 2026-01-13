"""Query Splitter für AND-Logik zwischen Begriffsgruppen"""

from typing import Tuple, Optional


class QuerySplitter:
    """Splittet Queries mit AND-Logik in separate Teile"""
    
    @staticmethod
    def has_and_logic(query: str) -> bool:
        """
        Prüft ob Query AND-Logik enthält
        
        Format: "Begriff1\nAND\nBegriff2" oder "Begriff1 AND Begriff2"
        """
        lines = query.strip().split('\n')
        
        # Check für AND auf eigener Zeile
        if any(line.strip().upper() == 'AND' for line in lines):
            return True
        
        # Check für einfaches "A AND B" (ein Begriff pro Seite)
        if ' AND ' in query and '\n' not in query:
            parts = query.split(' AND ')
            if len(parts) == 2:
                return True
        
        return False
    
    @staticmethod
    def split_query(query: str) -> Tuple[str, str]:
        """
        Splittet Query in Gruppe A und Gruppe B
        
        Returns:
            (group_a, group_b) tuple
        """
        lines = query.strip().split('\n')
        
        # Find AND line
        and_index = None
        for i, line in enumerate(lines):
            if line.strip().upper() == 'AND':
                and_index = i
                break
        
        if and_index is not None:
            # Multi-line format
            group_a = '\n'.join(lines[:and_index]).strip()
            group_b = '\n'.join(lines[and_index+1:]).strip()
            return (group_a, group_b)
        
        # Simple "A AND B" format
        if ' AND ' in query:
            parts = query.split(' AND ', 1)
            if len(parts) == 2:
                return (parts[0].strip(), parts[1].strip())
        
        raise ValueError("Query does not contain valid AND logic")
    
    @staticmethod
    def extract_first_term(query_part: str) -> str:
        """
        Extrahiert ersten Begriff aus Query-Teil für Dateinamen
        
        Entfernt OR, Anführungszeichen, etc.
        """
        # Split by OR
        terms = query_part.replace('\n', ' ').split(' OR ')
        first_term = terms[0].strip()
        
        # Remove quotes
        first_term = first_term.strip('"').strip("'")
        
        # Remove special characters, keep only alphanumeric and space
        first_term = ''.join(c if c.isalnum() or c.isspace() else '_' for c in first_term)
        
        # Replace spaces with underscore, lowercase
        first_term = '_'.join(first_term.split()).lower()
        
        # Limit length
        if len(first_term) > 20:
            first_term = first_term[:20]
        
        return first_term
    
    @staticmethod
    def extract_terms_for_validation(query_part: str) -> list:
        """
        Extrahiert alle Begriffe aus Query-Teil für Validierung
        
        Returns:
            Liste von Begriffen (lowercase, ohne Anführungszeichen)
        """
        terms = []
        
        # Split by OR (and newlines)
        parts = query_part.replace('\n', ' OR ').split(' OR ')
        
        for part in parts:
            term = part.strip().strip('"').strip("'").strip().lower()
            if term:
                terms.append(term)
        
        return terms
