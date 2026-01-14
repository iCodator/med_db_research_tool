# Research.py - Dokumentation

## Überblick

`research.py` ist das Hauptskript des Medical Database Research Tools. Es ermöglicht die Abfrage von drei medizinischen Datenbanken (PubMed, Europe PMC, OpenAlex) mit vordefinierten Query-Strings aus Textdateien.

## Verwendungszweck

Das Script automatisiert die Literaturrecherche in medizinischen Datenbanken, indem es:
- Query-Dateien aus dem `queries/` Verzeichnis liest
- Die entsprechende Datenbank automatisch erkennt
- Die Suche durchführt
- Ergebnisse als CSV und JSON exportiert
- Bei AND-Queries einen zweistufigen Workflow mit Merge-Logik verwendet (nur OpenAlex)

## Installation

### Voraussetzungen

```bash
# Python 3.8 oder höher
python --version

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Benötigte Bibliotheken

- `requests` - HTTP-Anfragen an APIs
- `pathlib` - Dateipfad-Handling
- Standard Python Libraries (sys, logging, etc.)

## Verwendung

### Basis-Verwendung

```bash
# Script starten
python research.py

# Eingabe bei Prompt
# Geben Sie den Dateinamen ein: pubmed
```

### Workflow

1. **Start des Scripts**
   ```bash
   python research.py
   ```

2. **Dateiname eingeben**
   - Mit oder ohne .txt Extension
   - Beispiele: `pubmed`, `pubmed.txt`, `europepmc`, `openalex`

3. **Automatische Verarbeitung**
   - Query wird aus Datei gelesen
   - Datenbank-Adapter wird initialisiert
   - Suche wird durchgeführt
   - Ergebnisse werden exportiert

### Unterstützte Datenbanken

| Datenbank | Query-Datei | Beschreibung |
|-----------|-------------|--------------|
| PubMed | `queries/pubmed.txt` | US National Library of Medicine |
| Europe PMC | `queries/europepmc.txt` | European PubMed Central |
| OpenAlex | `queries/openalex.txt` | Open Access Datenbank |

## Dateistruktur

### Input

```
queries/
├── pubmed.txt       # PubMed Query
├── europepmc.txt    # Europe PMC Query
└── openalex.txt     # OpenAlex Query
```

### Output

```
output/
├── pubmed/
│   ├── csv/
│   │   └── pubmed_2026-01-14_10-00-00.csv
│   └── json/
│       └── pubmed_2026-01-14_10-00-00.json
├── europepmc/
│   ├── csv/
│   └── json/
└── openalex/
    ├── csv/
    └── json/
```

## Query-Format

### Einfache Query (PubMed/Europe PMC)

```
("Periodontal Diseases"[MeSH Terms] OR "Periodontics"[MeSH Terms])
AND "Dental Implants"[MeSH Terms]
AND ("2020"[PDAT] : "2024"[PDAT])
```

### AND-Query (OpenAlex)

```
(Periodontology OR periodontal disease OR periodontitis)
AND
(dental implants OR implant dentistry)
AND
publication_year:2020-2024
```

**Wichtig**: AND-Queries werden nur von OpenAlex unterstützt und triggern einen speziellen zweistufigen Workflow.

## Funktionsweise

### 1. Normale Query-Verarbeitung

```
┌─────────────────┐
│ User Input      │
│ (Dateiname)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query lesen     │
│ aus Datei       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Datenbank-      │
│ Adapter init.   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Suche durch-    │
│ führen          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ergebnisse      │
│ exportieren     │
│ (CSV + JSON)    │
└─────────────────┘
```

### 2. AND-Query Workflow (nur OpenAlex)

```
┌─────────────────┐
│ AND-Query       │
│ erkannt         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query splitten  │
│ in A, B & Zeit  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Suche Gruppe A  │
│ (alle Treffer)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Suche Gruppe B  │
│ (alle Treffer)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Merge A AND B   │
│ - Title Match   │
│ - Author Match  │
│ - Content Valid.│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deduplizierung  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Export Merged   │
│ Results         │
└─────────────────┘
```

## Ausgabeformate

### CSV-Datei

```csv
authors,title,year,doi,url,abstract
"Smith J, Doe A","Example Title",2024,10.1234/example,https://..,"Abstract text..."
```

**Features:**
- Title und Abstract immer in Anführungszeichen
- Authors mit Quoting bei Kommas
- UTF-8 Encoding

### JSON-Datei

```json
{
  "metadata": {
    "database": "pubmed",
    "query": "Original Query String",
    "timestamp": "2026-01-14 10:00:00",
    "total_results": 36,
    "version": "1.0.0"
  },
  "articles": [
    {
      "authors": "Smith J, Doe A",
      "title": "Example Title",
      "year": "2024",
      "doi": "10.1234/example",
      "url": "https://...",
      "abstract": "Abstract text..."
    }
  ]
}
```

## Logging

### Log-Dateien

```
logs/
└── app.log
```

### Log-Level

- **INFO**: Normale Operationen
- **WARNING**: Keine Ergebnisse gefunden
- **ERROR**: Fehler bei Datenzugriff oder Export

### Beispiel-Log

```
2026-01-14 10:00:00,123 - INFO - Starte Verarbeitung von: pubmed.txt
2026-01-14 10:00:00,456 - INFO - Datenbank erkannt: pubmed
2026-01-14 10:00:01,789 - INFO - Query gelesen: ("Periodontal Diseases"...
2026-01-14 10:00:15,234 - INFO - 36 Artikel abgerufen
2026-01-14 10:00:15,567 - INFO - 36 Ergebnisse gefunden
2026-01-14 10:00:16,890 - INFO - Export erfolgreich abgeschlossen
```

## Fehlerbehandlung

### Häufige Fehler und Lösungen

#### 1. Datei nicht gefunden

**Fehler:**
```
Fehler: Query-Datei nicht gefunden
```

**Lösung:**
- Überprüfen Sie, ob die Datei in `queries/` existiert
- Dateiname korrekt eingeben (mit oder ohne .txt)

#### 2. Ungültige Datenbank

**Fehler:**
```
Fehler: Datenbank 'xyz' wird nicht unterstützt
Unterstützte Datenbanken: pubmed, europepmc, openalex
```

**Lösung:**
- Verwenden Sie einen gültigen Datenbanknamen
- Dateiname muss einer der drei Datenbanken entsprechen

#### 3. Keine Ergebnisse

**Ausgabe:**
```
Keine Ergebnisse gefunden.
```

**Mögliche Ursachen:**
- Query zu spezifisch
- Zeitraum zu eng
- API-Probleme

#### 4. Netzwerkfehler

**Fehler:**
```
ConnectionError: Failed to establish connection
```

**Lösung:**
- Internet-Verbindung prüfen
- API-Verfügbarkeit prüfen
- Proxy-Einstellungen überprüfen

## Erweiterte Funktionen

### AND-Query Merge-Logik (OpenAlex)

Der zweistufige Workflow bei AND-Queries:

1. **Suche Gruppe A**
   - Alle Artikel die Begriffe aus Gruppe A enthalten
   - Unbegrenzte Anzahl

2. **Suche Gruppe B**
   - Alle Artikel die Begriffe aus Gruppe B enthalten
   - Unbegrenzte Anzahl

3. **Merge mit AND-Logik**
   - Match nach: (Title + Authors)
   - Content-Validierung: Begriffe aus A **UND** B müssen in (Title ODER Abstract) vorkommen
   - Deduplizierung nach (Authors, Title)

### Ergebnis-Priorität

Bei Duplikaten über mehrere Datenbanken (via dedup.py):

1. PubMed (höchste Priorität)
2. Europe PMC
3. OpenAlex (niedrigste Priorität)

## Performance

### Typische Durchlaufzeiten

| Datenbank | Ergebnisse | Zeit |
|-----------|------------|------|
| PubMed | 10-50 | 5-15s |
| Europe PMC | 10-50 | 10-20s |
| OpenAlex | 10-50 | 5-10s |
| OpenAlex (AND) | 10-50 | 20-40s |

### Limitierungen

- **PubMed**: Max. 10.000 Ergebnisse pro Query
- **Europe PMC**: Max. 1.000 Ergebnisse pro Request
- **OpenAlex**: Keine Limitierung (verwendet Pagination)

## Abhängigkeiten

### Interne Module

```python
from src.config.settings import Settings
from src.core.query_handler import QueryHandler
from src.utils.file_handler import FileHandler
from src.utils.logger import setup_logger
```

### Modul-Hierarchie

```
research.py
├── QueryHandler
│   ├── Settings
│   ├── FileHandler
│   ├── Exporter
│   ├── QuerySplitter
│   ├── ResultMerger
│   └── Database Adapters
│       ├── PubMedAdapter
│       ├── EuropePMCAdapter
│       └── OpenAlexAdapter
├── FileHandler
└── Logger
```

## Best Practices

### 1. Query-Optimierung

- Verwenden Sie spezifische MeSH Terms (PubMed)
- Limitieren Sie den Zeitraum auf relevante Jahre
- Testen Sie Queries zuerst mit kleinem Zeitraum

### 2. Ergebnis-Management

- Verwenden Sie `dedup.py` bei Queries über mehrere Datenbanken
- Archivieren Sie alte Exports regelmäßig
- Behalten Sie Query-Dateien für Reproduzierbarkeit

### 3. Fehlerbehandlung

- Überprüfen Sie Logs bei Problemen
- Testen Sie API-Verfügbarkeit bei Netzwerkfehlern
- Verwenden Sie einfache Queries zum Testen

## Troubleshooting

### Debug-Modus aktivieren

Editieren Sie `src/utils/logger.py` und setzen Sie:
```python
level=logging.DEBUG  # statt INFO
```

### API-Verbindung testen

```bash
# PubMed
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test&retmode=json"

# Europe PMC
curl "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=test&format=json"

# OpenAlex
curl "https://api.openalex.org/works?filter=title.search:test"
```

## Weiterentwicklung

### Geplante Features

- [ ] Weitere Datenbanken (Scopus, Web of Science)
- [ ] GUI-Interface
- [ ] Batch-Processing mehrerer Queries
- [ ] Export in weitere Formate (BibTeX, RIS)

### Erweiterung um neue Datenbanken

1. Erstellen Sie einen neuen Adapter in `src/databases/`
2. Erben Sie von `BaseAdapter`
3. Implementieren Sie `search()` Methode
4. Fügen Sie Datenbank zu `Settings.SUPPORTED_DATABASES` hinzu
5. Erstellen Sie Query-Datei in `queries/`

## Support und Kontakt

- **GitHub**: https://github.com/iCodator/med_db_research_tool
- **Issues**: Verwenden Sie GitHub Issues für Bug Reports
- **Dokumentation**: Weitere Docs im `docs/` Verzeichnis

## Lizenz

Siehe LICENSE Datei im Projekt-Root.

## Version

**Aktuelle Version**: 1.0.0

**Änderungshistorie**: Siehe Git Commits
