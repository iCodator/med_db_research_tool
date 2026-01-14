# Dedup.py - Dokumentation

## Überblick

`dedup.py` ist ein Deduplizierungs-Tool für medizinische Literatur-Daten. Es entfernt Duplikate über mehrere Datenbank-Exporte hinweg und erstellt eine konsolidierte Liste eindeutiger Artikel.

## Verwendungszweck

Das Script löst das Problem von Duplikaten, die entstehen, wenn:
- Dieselbe Query in mehreren Datenbanken ausgeführt wird
- Artikel in mehreren Datenbanken indexiert sind
- Verschiedene Zeiträume oder Query-Varianten verwendet werden

## Installation

### Voraussetzungen

```bash
# Python 3.8 oder höher
python --version

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Benötigte Bibliotheken

- `pathlib` - Dateipfad-Handling
- Standard Python Libraries (json, csv, datetime, etc.)

## Verwendung

### Basis-Verwendung

```bash
# Script starten
python dedup.py

# Interaktive Auswahl
# Wählen Sie Datenbanken:
# 1. PubMed
# 2. Europe PMC
# 3. OpenAlex
# 4. Alle Datenbanken
```

### Workflow

1. **Start des Scripts**
   ```bash
   python dedup.py
   ```

2. **Datenbank-Auswahl**
   - Einzelne Datenbank (1-3)
   - Alle Datenbanken (4)
   - Kombinationen möglich

3. **Automatische Verarbeitung**
   - JSON-Files werden gesammelt
   - Artikel werden geladen
   - Duplikate werden erkannt und entfernt
   - Konsolidierte Ergebnisse werden exportiert

## Deduplizierungs-Logik

### Erkennungskriterien

Duplikate werden identifiziert anhand von:

```python
key = (authors, title, year)
```

**Alle drei Felder** müssen übereinstimmen (case-insensitive, normalisiert).

### Beispiel

Artikel 1 (PubMed):
```json
{
  "authors": "Smith J, Doe A",
  "title": "Dental Implants in Periodontal Patients",
  "year": "2024"
}
```

Artikel 2 (OpenAlex):
```json
{
  "authors": "SMITH J, DOE A",
  "title": "dental implants in periodontal patients",
  "year": "2024"
}
```

➡️ **Wird als Duplikat erkannt** (nach Normalisierung identisch)

### Prioritäts-System

Bei Duplikaten wird der Artikel mit **höchster Priorität** behalten:

| Priorität | Datenbank | Begründung |
|-----------|-----------|------------|
| 1 (höchste) | PubMed | Meiste Metadaten, höchste Qualität |
| 2 | Europe PMC | Gute Metadaten-Qualität |
| 3 (niedrigste) | OpenAlex | Open Access, teilweise unvollständig |

## Input/Output

### Input-Struktur

```
output/
├── pubmed/
│   └── json/
│       ├── pubmed_2026-01-14_10-00-00.json
│       └── pubmed_2026-01-14_11-30-00.json
├── europepmc/
│   └── json/
│       └── europepmc_2026-01-14_10-05-00.json
└── openalex/
    └── json/
        └── openalex_2026-01-14_10-10-00.json
```

### Output-Struktur

```
output/
└── deduplicated/
    ├── csv/
    │   └── dedup_all_2026-01-14_12-00-00.csv
    └── json/
        └── dedup_all_2026-01-14_12-00-00.json
```

## Ausgabeformate

### CSV-Datei

```csv
authors,title,year,doi,url,abstract,source_database
"Smith J, Doe A","Example Title",2024,10.1234/example,https://..,"Abstract...",pubmed
```

**Zusätzliches Feld:**
- `source_database` - Zeigt, aus welcher Datenbank der Artikel stammt

### JSON-Datei

```json
{
  "metadata": {
    "databases": ["pubmed", "europepmc", "openalex"],
    "timestamp": "2026-01-14 12:00:00",
    "total_results": 89,
    "query_type": "cross-database deduplication",
    "version": "1.0.0",
    "statistics": {
      "files_processed": 4,
      "articles_loaded": 125,
      "duplicates_removed": 36,
      "unique_articles": 89
    }
  },
  "articles": [
    {
      "authors": "Smith J, Doe A",
      "title": "Example Title",
      "year": "2024",
      "doi": "10.1234/example",
      "url": "https://...",
      "abstract": "Abstract text...",
      "source_database": "pubmed"
    }
  ]
}
```

## Funktionsweise

### Prozess-Flow

```
┌─────────────────────┐
│ User wählt          │
│ Datenbanken         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Sammle alle         │
│ JSON-Files aus      │
│ output/{db}/json/   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Lade alle Artikel   │
│ + füge source_db    │
│ Feld hinzu          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Gruppiere nach      │
│ (authors, title,    │
│ year)               │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Für jede Gruppe:    │
│ - Duplikat?         │
│ - Wähle höchste     │
│   Priorität         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Export deduplizierte│
│ Ergebnisse          │
│ (CSV + JSON)        │
└─────────────────────┘
```

### Algorithmus-Details

```python
# Schritt 1: Gruppierung
groups = defaultdict(list)
for article in all_articles:
    key = (normalize(authors), normalize(title), year)
    groups[key].append(article)

# Schritt 2: Deduplizierung
unique = []
for key, articles in groups.items():
    if len(articles) == 1:
        unique.append(articles[0])  # Kein Duplikat
    else:
        # Sortiere nach Priorität
        sorted_articles = sorted(
            articles,
            key=lambda a: DATABASE_PRIORITY[a['source_database']]
        )
        unique.append(sorted_articles[0])  # Höchste Priorität

# Schritt 3: Statistiken
duplicates_removed = sum(len(g) - 1 for g in groups.values() if len(g) > 1)
```

## Verwendungsszenarien

### Szenario 1: Alle Datenbanken

**Use Case:** Vollständige Literatur-Recherche über alle verfügbaren Datenbanken

```bash
python dedup.py
# Wähle: 4 (alle)
```

**Ergebnis:**
- Konsolidierte Liste aller eindeutigen Artikel
- Maximale Abdeckung
- Beste Metadaten-Qualität (PubMed bevorzugt)

### Szenario 2: Zwei Datenbanken

**Use Case:** Vergleich zwischen PubMed und Europe PMC

```bash
python dedup.py
# Wähle: 1,2 (pubmed,europepmc)
```

**Ergebnis:**
- Artikel aus beiden Datenbanken
- PubMed-Versionen werden bei Duplikaten bevorzugt

### Szenario 3: Einzelne Datenbank

**Use Case:** Mehrere Exports derselben Datenbank deduplizieren

```bash
python dedup.py
# Wähle: 1 (pubmed)
```

**Ergebnis:**
- Konsolidiert mehrere PubMed-Exports
- Nützlich bei verschiedenen Zeiträumen/Queries

## Statistiken

### Console-Output

```
======================================================================
CROSS-DATABASE DEDUPLIZIERUNG
======================================================================

Verfügbare Datenbanken:
  1. pubmed
  2. europepmc
  3. openalex
  4. alle

Wählen Sie Datenbanken (Komma-getrennt oder 'alle'): alle

Sammle JSON-Files...
├─ pubmed: 2 JSON-Files gefunden
├─ europepmc: 1 JSON-File gefunden
└─ openalex: 1 JSON-File gefunden

Lade Artikel...
✓ 125 Artikel aus 4 Files geladen

Deduplizierung läuft...
Duplikate entfernt: 36
Eindeutige Artikel: 89

✓ CSV exportiert: dedup_all_2026-01-14_12-00-00.csv
  Größe: 125.4 KB
✓ JSON exportiert: dedup_all_2026-01-14_12-00-00.json
  Größe: 156.8 KB

======================================================================
DEDUPLIZIERUNG ERFOLGREICH ABGESCHLOSSEN
======================================================================
```

### Statistik-Interpretation

| Metrik | Bedeutung |
|--------|-----------|
| Files processed | Anzahl verarbeiteter JSON-Files |
| Articles loaded | Gesamtzahl geladener Artikel (mit Duplikaten) |
| Duplicates removed | Anzahl entfernter Duplikate |
| Unique articles | Finale Anzahl eindeutiger Artikel |

**Duplikations-Rate berechnen:**
```
Rate = (Duplicates removed / Articles loaded) × 100%
Beispiel: (36 / 125) × 100% = 28.8%
```

## Fehlerbehandlung

### Häufige Fehler und Lösungen

#### 1. Keine JSON-Files gefunden

**Fehler:**
```
⚠ Keine JSON-Files in den ausgewählten Datenbanken gefunden
```

**Lösung:**
- Führen Sie zuerst `research.py` aus
- Überprüfen Sie `output/{database}/json/` Verzeichnisse
- Stellen Sie sicher, dass Exports erfolgreich waren

#### 2. Leere JSON-Files

**Fehler:**
```
⚠ Fehler beim Laden von {file}: No 'articles' key found
```

**Lösung:**
- Überprüfen Sie JSON-Struktur
- Re-exportieren Sie mit `research.py`
- Löschen Sie korrupte Files

#### 3. Speicherprobleme

**Symptom:**
```
MemoryError: Unable to allocate array
```

**Lösung:**
- Verarbeiten Sie Datenbanken einzeln
- Löschen Sie alte Exports
- Erhöhen Sie verfügbaren RAM

## Best Practices

### 1. Regelmäßige Deduplizierung

```bash
# Nach jedem research.py Durchlauf
python research.py  # Query in allen DBs
python dedup.py     # Deduplizieren
```

### 2. Archivierung

```bash
# Archivieren Sie deduplizierte Ergebnisse
mkdir -p archive/2024-01/
mv output/deduplicated/*.csv archive/2024-01/
mv output/deduplicated/*.json archive/2024-01/
```

### 3. Qualitätskontrolle

```python
# Überprüfen Sie Duplikations-Rate
# Normal: 20-40% bei 3 Datenbanken
# Hoch: >50% (evtl. identische Queries?)
# Niedrig: <10% (evtl. sehr spezifische Queries?)
```

## Performance

### Typische Durchlaufzeiten

| Artikel (geladen) | Datenbanken | Zeit |
|-------------------|-------------|------|
| 100 | 1 | <1s |
| 500 | 3 | 1-2s |
| 1.000 | 3 | 2-4s |
| 5.000 | 3 | 10-15s |

### Speicherverbrauch

```
RAM ≈ Artikel × 5 KB

Beispiele:
- 1.000 Artikel ≈ 5 MB
- 10.000 Artikel ≈ 50 MB
- 100.000 Artikel ≈ 500 MB
```

## Abhängigkeiten

### Interne Module

```python
from pathlib import Path
from src.utils.deduplicator import Deduplicator
```

### Modul-Hierarchie

```
dedup.py
└── Deduplicator
    ├── collect_json_files()
    ├── load_articles()
    ├── deduplicate()
    └── export_results()
```

## Erweiterte Funktionen

### Custom Priorität

Sie können die Priorität in `src/utils/deduplicator.py` anpassen:

```python
DATABASE_PRIORITY = {
    'pubmed': 1,      # Höchste Priorität
    'europepmc': 2,
    'openalex': 3     # Niedrigste Priorität
}
```

### Zusätzliche Deduplizierungs-Kriterien

Erweitern Sie die Matching-Logik:

```python
# In deduplicate() Methode
key = (
    normalize(authors),
    normalize(title),
    year,
    doi  # Zusätzliches Kriterium
)
```

## Integration mit anderen Tools

### Research.py Workflow

```bash
# 1. Recherche in allen Datenbanken
python research.py  # Input: pubmed
python research.py  # Input: europepmc
python research.py  # Input: openalex

# 2. Deduplizieren
python dedup.py     # Input: alle

# 3. Weiterverarbeitung
# CSV in Excel/R/Python importieren
```

### Automatisiertes Scripting

```bash
#!/bin/bash
# batch_research.sh

# Führe Recherche aus
for db in pubmed europepmc openalex; do
    echo "$db" | python research.py
done

# Dedupliziere
echo "alle" | python dedup.py

echo "Fertig! Siehe output/deduplicated/"
```

## Troubleshooting

### Debug-Informationen

Fügen Sie Debug-Ausgaben hinzu:

```python
# In src/utils/deduplicator.py
print(f"DEBUG: Processing group with {len(articles)} articles")
print(f"DEBUG: Selected article from: {selected['source_database']}")
```

### Manuelle Überprüfung

```python
# Prüfen Sie Duplikate manuell
import json

with open('output/deduplicated/json/dedup_all_*.json') as f:
    data = json.load(f)
    
# Duplikate nach Title suchen
titles = {}
for article in data['articles']:
    title = article['title'].lower()
    if title in titles:
        print(f"Possible duplicate: {title}")
    titles[title] = article
```

## Ausgabe-Analyse

### CSV-Analyse mit Python

```python
import pandas as pd

# Lade deduplizierte Daten
df = pd.read_csv('output/deduplicated/csv/dedup_all_*.csv')

# Statistiken
print(f"Total articles: {len(df)}")
print(f"\nBy database:")
print(df['source_database'].value_counts())
print(f"\nBy year:")
print(df['year'].value_counts().sort_index())
```

### JSON-Analyse

```python
import json
from collections import Counter

with open('output/deduplicated/json/dedup_all_*.json') as f:
    data = json.load(f)

# Database distribution
sources = [a['source_database'] for a in data['articles']]
print(Counter(sources))

# Metadata
print(f"Duplicates removed: {data['metadata']['statistics']['duplicates_removed']}")
print(f"Duplication rate: {data['metadata']['statistics']['duplicates_removed'] / data['metadata']['statistics']['articles_loaded'] * 100:.1f}%")
```

## Limitierungen

### Bekannte Einschränkungen

1. **Name-Varianten**
   - "Smith J" vs "Smith John" werden NICHT als Duplikate erkannt
   - Lösung: Manuelle Nachbearbeitung nötig

2. **Tippfehler**
   - Kleine Unterschiede in Titeln führen zu verschiedenen Artikeln
   - Lösung: Fuzzy-Matching (zukünftige Version)

3. **Fehlende Felder**
   - Artikel ohne Jahr werden als einzigartig behandelt
   - Artikel ohne Autoren ähnlich

4. **Speicher**
   - Sehr große Datasets (>100.000 Artikel) können problematisch sein
   - Lösung: Batch-Processing implementieren

## Weiterentwicklung

### Geplante Features

- [ ] Fuzzy-Matching für ähnliche Titel
- [ ] DOI-basierte Deduplizierung als Option
- [ ] Batch-Processing für große Datasets
- [ ] GUI für Duplikat-Review
- [ ] Configurable Prioritäten
- [ ] Export in weitere Formate (BibTeX, RIS)

### Beitragen

Vorschläge für Verbesserungen:
1. Fork das Repository
2. Erstelle Feature Branch
3. Implementiere Änderungen
4. Submit Pull Request

## Support

- **GitHub**: https://github.com/iCodator/med_db_research_tool
- **Issues**: Melden Sie Bugs via GitHub Issues
- **Dokumentation**: Weitere Docs im `docs/` Verzeichnis

## Lizenz

Siehe LICENSE Datei im Projekt-Root.

## Version

**Aktuelle Version**: 1.0.0

**Changelog**:
- 1.0.0: Initial Release
  - Cross-database Deduplizierung
  - Prioritäts-basierte Auswahl
  - CSV und JSON Export
  - Statistik-Tracking
