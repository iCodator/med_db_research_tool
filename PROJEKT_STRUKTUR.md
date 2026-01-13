# Projektstruktur - Medical Database Research Tool

## 📁 Vollständige Verzeichnisstruktur

```
med_db_research_tool/
│
├── .env                           # Umgebungsvariablen (API-Keys)
├── .gitignore                     # Git-Ausschlüsse
├── requirements.txt               # Python-Abhängigkeiten
├── README.md                      # Projekt-Readme (leer, für Ihre Inhalte)
├── PROJEKT_STRUKTUR.md           # Diese Datei
│
├── src/                           # Quellcode
│   ├── __init__.py               # Package-Initialisierung
│   ├── main.py                   # Haupteinstiegspunkt
│   │
│   ├── config/                   # Konfiguration
│   │   ├── __init__.py
│   │   └── settings.py           # Zentrale Einstellungen
│   │
│   ├── core/                     # Kernlogik
│   │   ├── __init__.py
│   │   ├── query_handler.py      # Query-Workflow-Orchestrierung
│   │   └── parsers/              # Query-Parser (TODO)
│   │       └── __init__.py
│   │
│   ├── databases/                # Datenbank-Adapter
│   │   ├── __init__.py
│   │   ├── base_adapter.py       # Basis-Adapter-Klasse
│   │   ├── pubmed.py            # ✓ PubMed (funktionsfähig)
│   │   ├── europepmc.py         # ⚠ Europe PMC (Stub)
│   │   └── openalex.py          # ⚠ OpenAlex (Stub)
│   │
│   └── utils/                    # Hilfsfunktionen
│       ├── __init__.py
│       ├── logger.py             # Logging-Setup
│       ├── file_handler.py       # Datei-I/O
│       └── exporter.py           # CSV/JSON-Export
│
├── queries/                       # 📥 INPUT: Query-Dateien
│   ├── pubmed.txt                # Beispiel: Diabetes-Query
│   ├── europepmc.txt             # Beispiel: Cancer-Query
│   └── openalex.txt              # Beispiel: ML-Healthcare-Query
│
├── output/                        # 📤 OUTPUT: Ergebnisse
│   ├── pubmed/                   # PubMed-Ergebnisse (CSV + JSON)
│   ├── europepmc/                # Europe PMC-Ergebnisse
│   └── openalex/                 # OpenAlex-Ergebnisse
│
├── logs/                          # 📋 Log-Dateien
│   └── research_YYYYMMDD_HHMMSS.log
│
└── tests/                         # Unit-Tests (TODO)
    ├── __init__.py
    └── fixtures/
```

---

## 🔄 Workflow-Ablauf

```
┌─────────────────────────────────────────────────────────────┐
│  1. Benutzer startet: python src/main.py                    │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Eingabe: Dateiname (z.B. "pubmed.txt")                  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. FileHandler liest: queries/pubmed.txt                   │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Settings erkennt Datenbank: "pubmed" → PubMed           │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. QueryHandler initialisiert: PubMedAdapter               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Adapter führt API-Abfrage aus                           │
│     - esearch: IDs holen                                     │
│     - efetch: Details abrufen                                │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  7. Exporter schreibt Ergebnisse:                           │
│     - output/pubmed/pubmed_20260113-110700.csv              │
│     - output/pubmed/pubmed_20260113-110700.json             │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  8. Logger schreibt: logs/research_20260113_110700.log      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Datenmodell

### Artikel-Dictionary (Standardformat)

Alle Adapter geben Artikel in diesem Format zurück:

```python
{
    'authors': 'Smith J, Doe M, ...',     # Autorenliste (kommagetrennt)
    'title': 'Study on diabetes...',      # Artikeltitel
    'year': '2023',                       # Publikationsjahr
    'doi': '10.1234/example',             # Digital Object Identifier
    'url': 'https://pubmed...',           # Direktlink zum Artikel
    'abstract': 'Abstract text...',       # Zusammenfassung
    'venue': 'Journal of Medicine'        # Journal/Zeitschrift
}
```

### CSV-Ausgabe

```csv
authors,title,year,doi,url,abstract,venue
"Smith J, Doe M","Study on diabetes",2023,10.1234/example,https://...,Abstract text,Journal of Medicine
```

### JSON-Ausgabe

```json
{
  "metadata": {
    "database": "pubmed",
    "query": "\"diabetes\"[MeSH] AND ...",
    "timestamp": "2026-01-13 11:07:00",
    "total_results": 150,
    "version": "1.0.0"
  },
  "articles": [
    {
      "authors": "Smith J, Doe M",
      "title": "Study on diabetes",
      "year": "2023",
      "doi": "10.1234/example",
      "url": "https://...",
      "abstract": "Abstract text",
      "venue": "Journal of Medicine"
    }
  ]
}
```

---

## 🗄️ Datenbank-Mapping

| Datei | Datenbank | Adapter | Status |
|-------|-----------|---------|--------|
| `pubmed.txt` | PubMed (NCBI) | `PubMedAdapter` | ✅ Funktionsfähig |
| `europepmc.txt` | Europe PMC | `EuropePMCAdapter` | ⚠️ Stub (TODO) |
| `openalex.txt` | OpenAlex | `OpenAlexAdapter` | ⚠️ Stub (TODO) |

---

## 🔧 Technische Details

### Adapter-Pattern

Alle Datenbank-Adapter erben von `BaseAdapter`:

```python
class BaseAdapter(ABC):
    @abstractmethod
    def search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Führt Datenbanksuche durch"""
        pass
    
    @abstractmethod
    def _parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parsed API-Response"""
        pass
    
    def _standardize_article(self, article_data: Dict) -> Dict:
        """Standardisiert zu einheitlichem Format"""
        pass
```

### Logger-Konfiguration

- **File Handler:** Alle Logs in `logs/research_TIMESTAMP.log`
- **Console Handler:** Nur INFO und höher auf Console
- **Format:** `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

### Export-Format

- **Dateinamen:** `{database}_{YYYYMMDD-HHMMSS}.{ext}`
- **Encoding:** UTF-8
- **CSV:** DictWriter mit festen Feldnamen
- **JSON:** Mit Metadata-Block

---

## ⚙️ Konfiguration

### .env Datei

```bash
# PubMed API Key (optional, erhöht Rate-Limit)
PUBMED_API_KEY=your_key_here

# OpenAlex (benötigt Email für Polite Pool)
OPENALEX_EMAIL=your_email@example.com
```

### Settings (src/config/settings.py)

```python
BATCH_SIZE = 500        # Ergebnisse pro Batch
MAX_RESULTS = 10000     # Maximum Gesamtergebnisse
```

---

## 🚀 Verwendung

### Installation

```bash
pip install -r requirements.txt
```

### Ausführung

```bash
python src/main.py
```

### Beispiel-Session

```
======================================================================
MEDICAL DATABASE RESEARCH TOOL
======================================================================

Unterstützte Datenbanken:
  • pubmed.txt    → PubMed
  • europepmc.txt → Europe PMC
  • openalex.txt  → OpenAlex

----------------------------------------------------------------------

Geben Sie den Dateinamen ein (z.B. pubmed.txt): pubmed.txt

Datenbank: PubMed
Query: "diabetes"[MeSH] AND "treatment"[Title/Abstract] AND 2020:2024[pdat]

Starte Suche...

✓ 150 Artikel gefunden

Exportiere Ergebnisse...
✓ CSV exportiert: output/pubmed/pubmed_20260113-110700.csv
  Größe: 125.3 KB
✓ JSON exportiert: output/pubmed/pubmed_20260113-110700.json
  Größe: 245.8 KB

======================================================================
SUCHE ERFOLGREICH ABGESCHLOSSEN
======================================================================
```

---

## ✅ Status

### Fertiggestellt

- ✅ Projektstruktur
- ✅ Basis-Konfiguration (Settings, Logger, FileHandler)
- ✅ Export-Funktionen (CSV, JSON)
- ✅ QueryHandler (Workflow-Orchestrierung)
- ✅ BaseAdapter (Abstrakte Basisklasse)
- ✅ PubMedAdapter (vollständig implementiert)
- ✅ Beispiel-Query-Dateien

### TODO (Erweiterungen)

- ⚠️ EuropePMCAdapter (API-Anbindung)
- ⚠️ OpenAlexAdapter (API-Anbindung)
- ⚠️ Query-Parser (Syntax-Validierung)
- ⚠️ Batch-Processing (für große Ergebnismengen)
- ⚠️ Unit-Tests
- ⚠️ Abstract-Fetching für PubMed (benötigt extra efetch-Call)

---

## 📝 Hinweise

1. **PubMed API Key:** Ohne Key sind Sie auf 3 Requests/Sekunde limitiert. Mit Key: 10 Requests/Sekunde.

2. **Europe PMC:** API ist offen zugänglich, keine Authentifizierung nötig.

3. **OpenAlex:** Benötigt Email-Adresse im User-Agent für "Polite Pool" (schnellere Antworten).

4. **Feldordnung:** Die Reihenfolge der Felder ist festgelegt:
   `authors, title, year, doi, url, abstract, venue`

5. **Erweiterung:** Um eine neue Datenbank hinzuzufügen:
   - Adapter in `src/databases/` erstellen (von `BaseAdapter` erben)
   - In `settings.py` unter `SUPPORTED_DATABASES` eintragen
   - In `query_handler.py` unter `_get_adapter()` hinzufügen

---

**Version:** 1.0.0  
**Erstellt:** 13.01.2026  
**Status:** ✅ Grundstruktur fertig, PubMed funktionsfähig
