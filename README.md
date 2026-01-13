# Medical Database Research Tool

Ein Python-Tool zur Abfrage medizinischer Datenbanken mit vorformatierten Query-Strings aus Textdateien.

## Features

- 🔍 Abfrage mehrerer medizinischer Datenbanken (PubMed, Europe PMC, OpenAlex)
- 📁 Query-Strings aus Textdateien
- 🎯 Automatische Datenbankwahl über Dateinamen
- 💾 Export in CSV und JSON
- 📊 Standardisiertes Ausgabeformat
- 📝 Detaillierte Logging-Funktionen

## Unterstützte Datenbanken

| Datenbank | Datei | Status |
|-----------|-------|--------|
| PubMed (NCBI) | `pubmed.txt` | ✅ Funktionsfähig |
| Europe PMC | `europepmc.txt` | ⚠️ In Entwicklung |
| OpenAlex | `openalex.txt` | ⚠️ In Entwicklung |

## Installation

```bash
pip install -r requirements.txt
```

## Konfiguration

Erstellen Sie eine `.env` Datei mit Ihren API-Keys:

```bash
PUBMED_API_KEY=your_key_here
OPENALEX_EMAIL=your_email@example.com
```

## Verwendung

1. **Query-Datei erstellen:**
   
   Erstellen Sie eine Datei in `queries/`, z.B. `queries/pubmed.txt`:
   ```
   "diabetes"[MeSH] AND "treatment"[Title/Abstract] AND 2020:2024[pdat]
   ```

2. **Tool ausführen:**
   ```bash
   python src/main.py
   ```

3. **Dateiname eingeben:**
   ```
   Geben Sie den Dateinamen ein (z.B. pubmed.txt): pubmed.txt
   ```

4. **Ergebnisse finden:**
   - CSV: `output/pubmed/pubmed_20260113-110700.csv`
   - JSON: `output/pubmed/pubmed_20260113-110700.json`

## Ausgabeformat

Alle Ergebnisse haben folgende Felder:

```csv
authors,title,year,doi,url,abstract,venue
```

## Projektstruktur

Siehe [PROJEKT_STRUKTUR.md](PROJEKT_STRUKTUR.md) für Details.

## Lizenz

MIT License

## Version

1.0.0 - Initial Release
