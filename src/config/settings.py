"""Konfigurationseinstellungen für das Research Tool"""

import os
from pathlib import Path
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()


class Settings:
    """Zentrale Konfigurationsklasse"""
    
    # Projekt-Verzeichnisse
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    QUERIES_DIR = PROJECT_ROOT / "queries"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    LOGS_DIR = PROJECT_ROOT / "logs"
    
    # API-Konfiguration
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "")
    PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")  # Legacy, fallback to NCBI_API_KEY
    OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")
    
    # Batch-Processing
    BATCH_SIZE = 500
    MAX_RESULTS = 10000
    
    # Unterstützte Datenbanken
    SUPPORTED_DATABASES = {
        "pubmed": {
            "name": "PubMed",
            "adapter": "PubMedAdapter",
            "parser": "pubmed"
        },
        "europepmc": {
            "name": "Europe PMC",
            "adapter": "EuropePMCAdapter",
            "parser": "europepmc"
        },
        "openalex": {
            "name": "OpenAlex",
            "adapter": "OpenAlexAdapter",
            "parser": "openalex"
        }
    }
    
    @classmethod
    def get_database_name(cls, filename: str) -> str:
        """Extrahiert Datenbanknamen aus Dateinamen"""
        if not filename.endswith('.txt'):
            return None
        return filename[:-4].lower()
    
    @classmethod
    def is_valid_database(cls, db_name: str) -> bool:
        """Prüft, ob Datenbank unterstützt wird"""
        return db_name in cls.SUPPORTED_DATABASES
