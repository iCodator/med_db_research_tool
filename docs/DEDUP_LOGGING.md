# Dedup.py Logging-Dokumentation

## Übersicht

Die Logging-Funktionalität in `dedup.py` bietet zwei Modi zur Protokollierung der Deduplizierungs-Ergebnisse:

1. **Einfaches Logging**: Statistische Zusammenfassung pro Datenbank
2. **Detailliertes Logging**: Wie einfaches Logging + vollständige Liste aller entfernten Duplikate

## Verwendung

### Command-Line Interface

```bash
# Hilfe anzeigen
python dedup.py --help

# Ohne Logging
python dedup.py --log-mode none

# Mit einfachem Logging (Standard)
python dedup.py --log-mode simple

# Mit detailliertem Logging
python dedup.py --log-mode detailed

# Interaktive Auswahl (Standard: simple)
python dedup.py
```

### Interaktive Auswahl

Wenn kein `--log-mode` Parameter angegeben wird, erscheint eine interaktive Auswahl:

```
Logging-Modus auswählen:
  1) Kein Logging (nur Konsolen-Ausgabe)
  2) Einfaches Logging (Statistiken pro Datenbank)
  3) Detailliertes Logging (+ Liste aller Duplikate)

Ihre Wahl (1/2/3, Standard: 2):
```

## Logging-Modi

### 1. Kein Logging (`none`)

Nur Konsolen-Ausgabe, keine Log-Dateien werden erstellt.

### 2. Einfaches Logging (`simple`)

**Log-Ausgabe:**
```
======================================================================
DEDUPLIZIERUNGS-STATISTIKEN
======================================================================

GESAMT:
  - Geladene Artikel (total):     150
  - Gefundene Duplikate:          25
  - Eindeutige Artikel:           125

PRO DATENBANK:
----------------------------------------------------------------------

Datenbank: EUROPEPMC
  - Anzahl Quellen (geladen):     50
  - Anzahl Duplikate:             8
  - Verbleibende eindeutige:      42

Datenbank: OPENALEX
  - Anzahl Quellen (geladen):     50
  - Anzahl Duplikate:             10
  - Verbleibende eindeutige:      40

Datenbank: PUBMED
  - Anzahl Quellen (geladen):     50
  - Anzahl Duplikate:             7
  - Verbleibende eindeutige:      43
```

### 3. Detailliertes Logging (`detailed`)

Wie einfaches Logging, aber zusätzlich mit vollständiger Liste aller entfernten Duplikate:

**Zusätzliche Log-Ausgabe:**
```
======================================================================
DETAILLIERTE DUPLIKATE-LISTE
======================================================================

Datenbank: EUROPEPMC (8 Duplikate)
----------------------------------------------------------------------
  [1] Autor(en): Smith J, Doe J
      Titel:      Machine Learning in Medical Imaging...
      Jahr:       2023
      (Behalten von: pubmed)

  [2] Autor(en): Johnson A, Williams B
      Titel:      Deep Learning for Cancer Detection a...
      Jahr:       2022
      (Behalten von: pubmed)
  ...
```

**Hinweis:** Titel werden auf 40 Zeichen gekürzt (mit "..." suffix wenn länger).

## Log-Dateien

Log-Dateien werden im `logs/` Verzeichnis gespeichert:

- **Dateiname**: `dedup_YYYY-MM-DD_HH-MM-SS.log`
- **Format**: UTF-8 Text
- **Encoding**: UTF-8 (unterstützt Umlaute und Sonderzeichen)

### Beispiel Log-Datei-Name

```
logs/dedup_2026-01-14_17-05-30.log
```

## Technische Details

### Datenbank-Priorität

Bei Duplikaten wird der Artikel mit der höchsten Priorität behalten:

1. **PubMed** (höchste Priorität)
2. **Europe PMC**
3. **OpenAlex** (niedrigste Priorität)

### Duplikate-Erkennung

Duplikate werden identifiziert durch exakte Übereinstimmung (case-insensitive) von:
- Autoren
- Titel
- Jahr

### Pro-Datenbank-Statistiken

Für jede Datenbank werden erfasst:
- **Anzahl Quellen**: Geladene Artikel aus dieser Datenbank
- **Anzahl Duplikate**: Artikel aus dieser Datenbank, die als Duplikate entfernt wurden
- **Verbleibende eindeutige**: Artikel aus dieser Datenbank, die im finalen Ergebnis enthalten sind

## Beispiel-Workflow

```bash
# 1. Suche durchführen (falls noch nicht geschehen)
python research.py

# 2. Deduplizierung mit detailliertem Logging
python dedup.py --log-mode detailed

# 3. Log-Datei prüfen
ls -lt logs/ | head -5

# 4. Log-Datei anzeigen
cat logs/dedup_2026-01-14_17-05-30.log
```

## Implementierung

### Geänderte Dateien

1. **dedup.py**
   - Command-Line Arguments (argparse)
   - Help-Funktion
   - Logger-Initialisierung
   - Interaktive Logging-Modus-Auswahl

2. **src/utils/deduplicator.py**
   - Logger-Parameter im Konstruktor
   - Pro-Datenbank-Statistiken (`per_database_stats`)
   - Duplikate-Details (`duplicates_details`)
   - Neue Methode: `log_statistics(mode)`

### Neue Features

- ✅ `--help` für ausführliche Hilfe
- ✅ `--log-mode` für CLI-basierte Auswahl
- ✅ Interaktive Abfrage wenn keine CLI-Args
- ✅ Einfaches Logging (pro-Datenbank-Statistiken)
- ✅ Detailliertes Logging (mit Duplikate-Liste)
- ✅ UTF-8 Log-Dateien mit Timestamp

## Siehe auch

- [DEDUP_DOC.md](DEDUP_DOC.md) - Allgemeine Dedup-Dokumentation
- [RESEARCH_DOC.md](RESEARCH_DOC.md) - Research-Tool-Dokumentation
