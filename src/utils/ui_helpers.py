"""
UI Helper Functions für CLI-Scripts

Gemeinsame Funktionen für Benutzerinteraktion und formatierte Ausgaben.
"""

import sys
from typing import Optional


# Konstanten
BANNER_WIDTH = 70


def print_banner(title: str, char: str = "=") -> None:
    """
    Druckt einen formatierten Banner mit Titel
    
    Args:
        title: Titel-Text
        char: Zeichen für Banner (Standard: =)
    
    Example:
        >>> print_banner("MY TITLE")
        ======================================================================
        MY TITLE
        ======================================================================
    """
    print(char * BANNER_WIDTH)
    print(title)
    print(char * BANNER_WIDTH)


def print_separator(char: str = "-") -> None:
    """
    Druckt eine Trennlinie
    
    Args:
        char: Zeichen für Linie (Standard: -)
    """
    print(char * BANNER_WIDTH)


def get_user_input(prompt: str, allow_empty: bool = False) -> Optional[str]:
    """
    Sichere Input-Funktion mit Keyboard Interrupt Handling
    
    Args:
        prompt: Eingabeaufforderung
        allow_empty: Ob leere Eingabe erlaubt ist
        
    Returns:
        Eingabe-String (stripped) oder None bei Abbruch
        
    Raises:
        SystemExit: Bei Keyboard Interrupt (exit code 0)
    """
    try:
        user_input = input(prompt).strip()
        
        if not user_input and not allow_empty:
            return None
            
        return user_input
        
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramm beendet.")
        sys.exit(0)


def print_success_banner(message: str) -> None:
    """
    Success-Nachricht mit Banner
    
    Args:
        message: Success-Nachricht
    """
    print()
    print_banner(message)


def print_error_banner(message: str) -> None:
    """
    Error-Nachricht mit Banner
    
    Args:
        message: Error-Nachricht
    """
    print()
    print_banner(message)


def print_info(message: str, prefix: str = "ℹ") -> None:
    """
    Formatierte Info-Nachricht
    
    Args:
        message: Info-Text
        prefix: Präfix-Symbol
    """
    print(f"{prefix} {message}")


def print_warning(message: str) -> None:
    """
    Formatierte Warning-Nachricht
    
    Args:
        message: Warning-Text
    """
    print(f"⚠ {message}")


def print_error(message: str) -> None:
    """
    Formatierte Error-Nachricht
    
    Args:
        message: Error-Text
    """
    print(f"❌ {message}")


def print_section_header(title: str) -> None:
    """
    Druckt einen Section-Header mit Leerzeilen
    
    Args:
        title: Section-Titel
    """
    print()
    print(title)
    print()


def print_list_items(items: list[tuple[str, str]], bullet: str = "•") -> None:
    """
    Druckt eine Liste von Items mit Beschreibungen
    
    Args:
        items: Liste von (key, description) Tupeln
        bullet: Bullet-Zeichen
        
    Example:
        >>> items = [("pubmed", "PubMed Database"), ("openalex", "OpenAlex")]
        >>> print_list_items(items)
        • pubmed     → PubMed Database
        • openalex   → OpenAlex
    """
    for key, description in items:
        print(f"  {bullet} {key:<10} → {description}")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Fragt User um Bestätigung (y/n)
    
    Args:
        prompt: Frage-Text
        default: Default-Wert bei Enter
        
    Returns:
        True wenn bestätigt, False sonst
    """
    suffix = " (Y/n): " if default else " (y/N): "
    response = get_user_input(prompt + suffix, allow_empty=True)
    
    if response is None or response == "":
        return default
        
    return response.lower() in ['y', 'yes', 'ja', 'j']
