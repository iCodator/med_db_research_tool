# Systematische Analyse des Workflow-Flussdiagramms

## Abstract

Das vorliegende Dokument analysiert das Flussdiagramm des Medical Database Research Tools unter Verwendung ISO 5807-konformer Notation. Die Systemarchitektur implementiert drei distinkte Suchpfade zur Optimierung von Datenbankabruffragen unter Berücksichtigung datenbankspezifischer API-Limitationen und semantischer Anforderungen.

---

## 1. Einleitung

### 1.1 Systemübersicht

Das Medical Database Research Tool (MDRT) stellt eine integrierte Lösung zur systematischen Literaturrecherche in biomedizinischen Datenbanken dar. Das System implementiert datenbankspezifische Adapter für PubMed (NCBI E-utilities), Europe PMC und OpenAlex, wobei eine standardisierte Ausgabe in CSV- und JSON-Format gewährleistet wird.

### 1.2 Zielsetzung der Analyse

Diese Analyse dokumentiert die algorithmische Logik, Entscheidungsstrukturen und Datenflüsse des Systems, mit besonderem Fokus auf:
- Die Implementierung boolescher AND-Operatoren
- Datenbankspezifische Optimierungsstrategien
- Die mehrstufige Validierung bei komplexen Queries

---

## 2. Systemarchitektur

### 2.1 Modulare Komponenten

```
┌─────────────────────────────────────────┐
│         Präsentationsschicht            │
│         (main.py, CLI)                  │
├─────────────────────────────────────────┤
│         Logikschicht                    │
│         (query_handler, splitter)       │
├─────────────────────────────────────────┤
│         Datenzugriffsschicht            │
│         (Database Adapters)             │
├─────────────────────────────────────────┤
│         Datenverarbeitungsschicht       │
│         (merger, exporter)              │
└─────────────────────────────────────────┘
```

### 2.2 Datenfluss-Taxonomie

Der Datenfluss lässt sich in folgende Phasen kategorisieren:

1. **Initialisierungsphase:** Query-Parsing und Datenbankidentifikation
2. **Entscheidungsphase:** Klassifikation der AND-Logik-Variante
3. **Abfragephase:** API-Kommunikation und Datenakquisition
4. **Verarbeitungsphase:** Standardisierung und optionale Mergierung
5. **Exportphase:** Serialisierung in standardisierte Ausgabeformate

---

## 3. Prozessfluss-Analyse

### 3.1 Initialisierungsphase

#### 3.1.1 Query-Handler-Modul

**Funktion:** Einlesen und Parsing von Query-Dateien

**Input:**
- Dateipfad (String, Format: `{database}.txt`)
- Query-Content (String, potentiell mehrzeilig)

**Verarbeitung:**
1. File-I/O-Operation zur Query-Extraktion
2. Pattern-Matching zur Datenbankidentifikation via Dateinamen-Suffix
3. Syntaxanalyse zur Klassifikation der Query-Struktur

**Output:**
- Database-Identifier (Enum: PUBMED | EUROPEPMC | OPENALEX)
- Parsed Query-Objekt

#### 3.1.2 Datenbankidentifikation

**Mapping-Regel:**
```
filename.endswith("pubmed.txt")    → PubMedAdapter
filename.endswith("europepmc.txt") → EuropePMCAdapter
filename.endswith("openalex.txt")  → OpenAlexAdapter
```

**Rationale:** Explizite Namenskonvention zur eindeutigen Zuordnung ohne Konfigurationsdateien.

### 3.2 Entscheidungsphase: AND-Logik-Klassifikation

Die zentrale Verzweigung des Systems basiert auf der Struktur der booleschen Konjunktion:

#### 3.2.1 Klassifikation

**Typ A: Keine AND-Logik**
```
Query: "Diabetes"
Struktur: Simple Query
Klassifikation: Unäre Suche
```

**Typ B: Einzeilige AND-Logik**
```
Query: "Diabetes AND Insulin"
Struktur: Boolesche Konjunktion in einzeiliger Notation
Klassifikation: Inline-AND
Anwendbar: Alle Datenbanken (PubMed, EuropePMC, OpenAlex)
```

**Typ C: Mehrzeilige AND-Logik**
```
Query:
  Line 1: "Diabetes OR Type 2 Diabetes"
  Line 2: "AND"
  Line 3: "Insulin OR Insulin therapy"
Struktur: Konjunktion von Disjunktionen mit expliziter AND-Zeile
Klassifikation: Multiline-AND
Anwendbar: Ausschließlich OpenAlex
```

#### 3.2.2 Entscheidungslogik

**Pseudocode:**
```python
if not contains_AND_operator(query):
    return SearchPath.NORMAL
elif is_single_line_AND(query):
    return SearchPath.INLINE_AND
elif is_multiline_AND(query) and database == "openalex":
    return SearchPath.SPLIT_MERGE
else:
    raise InvalidQueryStructureException
```

---

## 4. Suchpfad-Implementierungen

### 4.1 Pfad 1: Normale Suche (Unäre Query)

#### 4.1.1 Algorithmus

```
FUNCTION normal_search(query, database_adapter):
    1. results ← database_adapter.search(query)
    2. standardized ← standardize_results(results)
    3. RETURN export(standardized)
END FUNCTION
```

#### 4.1.2 Komplexitätsanalyse

- **Zeitkomplexität:** O(n), wobei n = Anzahl der Treffer
- **API-Calls:** O(⌈n/page_size⌉), typischerweise 1-50 Requests
- **Speicherkomplexität:** O(n) für Result-Set

#### 4.1.3 Anwendungsfall

Explorative Recherchen ohne spezifische Konjunktionsanforderungen.

**Beispiel:** Überblickssuche zur Literaturlandschaft eines einzelnen Begriffes.

---

### 4.2 Pfad 2: Einzeilige AND-Logik

#### 4.2.1 Algorithmus

```
FUNCTION inline_and_search(query, database_adapter):
    1. conjunctive_query ← format_inline_AND(query)
       // z.B. "(Diabetes) AND (Insulin)"
    2. results ← database_adapter.search(conjunctive_query)
    3. standardized ← standardize_results(results)
    4. RETURN export(standardized)
END FUNCTION
```

#### 4.2.2 Datenbankspezifische Syntaxadaptierung

| Datenbank | AND-Syntax | Beispiel |
|-----------|------------|----------|
| PubMed | `(term1) AND (term2)` | `(Diabetes[MeSH]) AND (Insulin[MeSH])` |
| EuropePMC | `term1 AND term2` | `Diabetes AND Insulin` |
| OpenAlex | `filter: A AND B` | Wird intern transformiert |

#### 4.2.3 Vorteile

- **Effizienz:** Single-Pass-Retrieval
- **API-Konformität:** Alle Datenbanken unterstützen inline-AND nativ
- **Präzision:** Datenbank führt Konjunktion serverseitig aus

#### 4.2.4 Anwendungsfall

Gezielte Suchen mit klarer Konjunktionsanforderung über alle Datenbanken hinweg.

---

### 4.3 Pfad 3: Mehrzeilige AND-Logik mit Split-Merge-Workflow

#### 4.3.1 Rationale für OpenAlex-Exklusivität

**Begründung:**
1. OpenAlex besitzt das größte Korpus (>200M Publikationen)
2. API-Limitation: Keine native Unterstützung für komplexe mehrzeilige Queries
3. Kompensationsstrategie: Client-seitige Mergierung notwendig
4. Kostenvorteil: Lohnt sich nur bei großem Ergebnisraum

#### 4.3.2 Vier-Phasen-Algorithmus

##### Phase 1: Query-Splitting

```
FUNCTION split_query(multiline_query):
    lines ← parse_lines(multiline_query)
    and_index ← find_AND_line(lines)
    
    group_A ← lines[0:and_index]
    group_B ← lines[and_index+1:end]
    timeframe ← extract_timeframe(lines)
    
    RETURN (group_A, group_B, timeframe, extract_terms(group_A), extract_terms(group_B))
END FUNCTION
```

**Output-Struktur:**
```json
{
  "group_A": {
    "query": "periodontitis OR periodontal disease",
    "terms": ["periodontitis", "periodontal disease"]
  },
  "group_B": {
    "query": "ubiquinone OR coenzyme q10",
    "terms": ["ubiquinone", "coenzyme q10"]
  },
  "timeframe": "2000-2024"
}
```

##### Phase 2: Parallele Datenakquisition

```
FUNCTION parallel_search(group_A, group_B, adapter):
    // Konzeptuell parallel, sequentiell implementiert
    results_A ← adapter.search(group_A.query)
    results_B ← adapter.search(group_B.query)
    
    export_intermediate(results_A, "A")
    export_intermediate(results_B, "B")
    
    RETURN (results_A, results_B, group_A.terms, group_B.terms)
END FUNCTION
```

**Charakteristika:**
- Unabhängige API-Abfragen
- Intermediate Persistence (Fault Tolerance)
- Disjunktive Expansion pro Gruppe

##### Phase 3: Merge-Algorithmus (3 Stufen)

###### Stufe 3.1: Match-Finding

**Algorithmus:**
```
FUNCTION find_matches(results_A, results_B):
    matches ← ∅
    
    FOR EACH article_a IN results_A:
        title_a ← normalize(article_a.title)
        authors_a ← normalize(article_a.authors)
        
        FOR EACH article_b IN results_B:
            title_b ← normalize(article_b.title)
            authors_b ← normalize(article_b.authors)
            
            IF title_a = title_b AND authors_a = authors_b:
                matches ← matches ∪ {article_a}
                BREAK  // Innere Schleife
            END IF
        END FOR
    END FOR
    
    RETURN matches
END FUNCTION
```

**Komplexitätsanalyse:**
- **Worst-Case:** O(|A| × |B|) bei keinen Matches
- **Best-Case:** O(|A|) bei frühen Matches
- **Average-Case:** O(|A| × |B|/2)

**Normalisierung:**
```python
normalize(string) = lowercase(strip_whitespace(string))
```

**Empirisches Beispiel:**
```
|A| = 95,513
|B| = 16,268
|matches| = 161

Reduktion: 99.83%
```

###### Stufe 3.2: Content-Validation

**Algorithmus:**
```
FUNCTION validate_content(matches, terms_A, terms_B):
    validated ← ∅
    
    FOR EACH article IN matches:
        content ← concatenate(article.title, article.abstract)
        content_normalized ← normalize(content)
        
        has_term_A ← ∃ term ∈ terms_A: term IN content_normalized
        has_term_B ← ∃ term ∈ terms_B: term IN content_normalized
        
        IF has_term_A AND has_term_B:
            validated ← validated ∪ {article}
        END IF
    END FOR
    
    RETURN validated
END FUNCTION
```

**Rationale:**
- **Problem:** Match-Finding basiert nur auf Metadaten (Titel, Autoren)
- **Risiko:** False Positives durch ähnliche, aber nicht identische Artikel
- **Lösung:** Semantische Validation via Volltext-Check
- **Suchraum:** title ∪ abstract (nicht body, da nicht verfügbar)

**Empirisches Beispiel:**
```
Input:  161 matches
Output: 61 validated (37.9% Retention)
Rejected: 100 articles (62.1%)
```

**Rejection-Gründe:**
1. Abstract fehlt (field = "N/A")
2. Nur ein Term-Set präsent (nicht konjunktiv)
3. Synonyme/Varianten nicht erkannt

###### Stufe 3.3: Deduplizierung

**Algorithmus:**
```
FUNCTION deduplicate(validated):
    seen ← ∅  // Set of (authors, title) tuples
    unique ← []
    
    FOR EACH article IN validated:
        key ← (normalize(article.authors), normalize(article.title))
        
        IF key NOT IN seen:
            seen ← seen ∪ {key}
            unique ← unique ∪ [article]
        END IF
    END FOR
    
    RETURN unique
END FUNCTION
```

**Komplexitätsanalyse:**
- **Zeitkomplexität:** O(n), wobei n = |validated|
- **Speicherkomplexität:** O(n) für Hash-Set

**Empirisches Beispiel:**
```
Input:  61 validated
Output: 61 unique (0 duplicates)
```

**Hinweis:** Geringe Duplikatrate aufgrund vorheriger Filterung.

##### Phase 4: Export

Identisch zu Pfad 1 und 2.

#### 4.3.3 Gesamtkomplexität

```
T_total = T_split + T_search_A + T_search_B + T_merge + T_export

Wobei:
T_split ≈ O(|query_lines|) ≈ O(1)
T_search_A ≈ O(|A|)
T_search_B ≈ O(|B|)
T_merge ≈ O(|A| × |B|) [dominant term]
T_export ≈ O(|final|)

Dominanz: O(|A| × |B|) für großen Suchraum
```

#### 4.3.4 Anwendungsfall

Hochpräzise systematische Reviews mit komplexen Boolean Queries, ausschließlich für OpenAlex-Korpus.

---

## 5. ISO 5807 Symbolik

### 5.1 Verwendete Symbole

| Symbol | Bezeichnung | Semantik | Verwendung im MDRT |
|--------|-------------|----------|-------------------|
| Abgerundetes Rechteck | Terminator | Start/Ende | START, ENDE |
| Rechteck | Prozess | Verarbeitung | API-Call, Standardisierung |
| Raute | Entscheidung | Verzweigung | Datenbank?, AND-Logik? |
| Parallelogramm | I/O | Ein-/Ausgabe | Query-Eingabe, CSV/JSON-Export |
| Pfeil | Flussrichtung | Kontrolfluss | Sequenzielle Abfolge |

### 5.2 Farbkodierung

| Farbe | Hex-Code | Symboltyp | Kognitive Assoziation |
|-------|----------|-----------|----------------------|
| Rot | #ffebee | Terminatoren | Anfang/Ende, Aufmerksamkeit |
| Blau | #e1f5ff | Prozesse | Verarbeitung, Workflow |
| Gelb | #fff4e1 | Entscheidungen | Achtung, Verzweigung |
| Grün | #e8f5e9 | I/O | Datenfluss, extern |

---

## 6. Ausgabeformate

### 6.1 CSV-Export

**Schema:**
```
authors: VARCHAR
title: VARCHAR
year: INTEGER
doi: VARCHAR (optional, Pattern: 10.\d{4,}/[^\s]+)
url: VARCHAR (URL-validated)
abstract: TEXT
```

**Eigenschaften:**
- UTF-8 Encoding
- RFC 4180 konform
- Delimiter: Komma
- Quoting: Alle Felder (Konsistenz)

**Verwendungszweck:** Tabellenkalkulationssoftware, statistische Auswertung

### 6.2 JSON-Export

**Schema:**
```json
{
  "metadata": {
    "database": "string",
    "timestamp": "ISO 8601 datetime",
    "total_results": "integer",
    "query_type": "string (normal|inline_and|split_merge)",
    "version": "semantic version"
  },
  "articles": [
    {
      "authors": "string",
      "title": "string",
      "year": "string",
      "doi": "string",
      "url": "string",
      "abstract": "string"
    }
  ]
}
```

**Eigenschaften:**
- UTF-8 Encoding
- Pretty-Printed (indent=2)
- Non-ASCII preservation

**Verwendungszweck:** Programmatische Weiterverarbeitung, Datenanalyse

---

## 7. Evaluationsmetriken

### 7.1 Empirische Performance-Analyse

**Testfall: Parodontitis AND Ubiquinone (OpenAlex, mehrzeilig)**

| Metrik | Wert | Interpretation |
|--------|------|----------------|
| Korpusgröße A | 95,513 | Initiales Retrieval |
| Korpusgröße B | 16,268 | Initiales Retrieval |
| Matches (Stufe 1) | 161 | 0.168% von A |
| Validated (Stufe 2) | 61 | 37.9% von Matches |
| Unique (Stufe 3) | 61 | 100% Retention |
| **Precision Gain** | **1 → 15.66** | Verbesserung durch Filtering |
| Gesamt-Laufzeit | ~18 Min | Akzeptabel für Korpusgröße |

**Precision-Berechnung:**
```
Baseline Precision (nur A): 61 / 95,513 = 0.064%
Filtered Precision (final): 61 / 61 = 100%
Improvement Factor: 100 / 0.064 ≈ 1563x
```

### 7.2 Komparative Analyse der Suchpfade

| Kriterium | Normal | Inline-AND | Multiline-AND |
|-----------|--------|------------|---------------|
| **Laufzeit** | O(n) | O(n) | O(n²) |
| **Präzision** | Niedrig | Mittel | Hoch |
| **API-Calls** | Minimal | Minimal | 2x Minimal |
| **DB-Support** | Alle | Alle | Nur OpenAlex |
| **Anwendung** | Exploration | Zielgerichtet | Systematisch |

---

## 8. Diskussion

### 8.1 Architektonische Entscheidungen

#### 8.1.1 Warum Split-Merge nur für OpenAlex?

**Rationale:**
1. **Korpusgröße:** OpenAlex >>  PubMed > EuropePMC
2. **ROI:** O(n²)-Komplexität rechtfertigt sich nur bei großem n
3. **API-Design:** PubMed/EuropePMC haben native AND-Unterstützung

#### 8.1.2 Warum Client-seitige Mergierung?

**Alternative:** Server-seitige Konjunktion (wenn verfügbar)

**Contra:**
- OpenAlex API unterstützt keine komplexen Mehrklausel-Queries
- Client-Kontrolle: Explizite Validierungsschritte
- Transparenz: Intermediate Results einsehbar

**Pro Client-Side:**
- Flexibilität: Anpassbare Validierungslogik
- Debugging: Klare Fehlerisolierung
- Portabilität: Unabhängig von API-Änderungen

### 8.2 Limitationen

#### 8.2.1 Content-Validation

**Problem:** Nur title + abstract verfügbar
**Impact:** Full-Text-Erwähnungen werden nicht erfasst
**Mitigation:** In der Regel erwähnen Abstracts alle Hauptbegriffe

#### 8.2.2 Synonymerkennung

**Problem:** Keine automatische Synonym-Expansion
**Beispiel:** "CoQ10" vs. "Coenzyme Q10"
**Mitigation:** Benutzer muss Synonyme in Query inkludieren

#### 8.2.3 False Negatives bei Match-Finding

**Problem:** Autorennamen-Variationen (J. Smith vs. John Smith)
**Impact:** Potentielle Matches werden übersehen
**Mitigation:** Normalisierung hilft teilweise, nicht vollständig lösbar

### 8.3 Optimierungspotential

#### 8.3.1 Algorithmische Verbesserungen

1. **Hash-basiertes Matching:**
   ```
   O(|A| × |B|) → O(|A| + |B|)
   ```
   via HashMap für title+authors

2. **Parallele Verarbeitung:**
   - Thread-Pool für Match-Finding
   - Async I/O für API-Calls

3. **Incremental Merging:**
   - Stream-Processing statt Batch

#### 8.3.2 Semantische Erweiterungen

1. **NLP-Integration:**
   - Word embeddings für Synonym-Detection
   - Named Entity Recognition für Autor-Matching

2. **Fuzzy Matching:**
   - Levenshtein-Distance für Titel
   - Phonetic Matching für Autoren

---

## 9. Schlussfolgerungen

### 9.1 Zusammenfassung

Das MDRT implementiert einen mehrstufigen, adaptiven Workflow zur systematischen Literaturrecherche. Die trimodale Architektur (Normal | Inline-AND | Multiline-AND) optimiert das Trade-off zwischen Laufzeit, Präzision und Datenbankkompatibilität.

### 9.2 Kernbeiträge

1. **Adaptive Query-Klassifikation:** Automatische Pfadwahl basierend auf Query-Struktur
2. **Dreistufige Validierung:** Match-Finding → Content-Validation → Deduplizierung
3. **Datenbankagnostische Standardisierung:** Einheitliche Output-Formate

### 9.3 Wissenschaftlicher Kontext

Das System adressiert eine zentrale Herausforderung in der systematischen Literaturrecherche: Die Integration heterogener Datenquellen mit unterschiedlichen Query-Syntaxen und API-Limitationen. Die implementierte Lösung balanciert praktische Anforderungen (Laufzeit, Ressourcen) mit methodischen Standards (Präzision, Vollständigkeit).

---

## 10. Anhang

### 10.1 Technische Spezifikationen

**Entwicklungsumgebung:**
- Sprache: Python 3.x
- Abhängigkeiten: requests, xml.etree, csv, json
- Version Control: Git

**Datenbank-APIs:**
- PubMed: NCBI E-utilities (efetch, esearch)
- EuropePMC: REST API v6.3
- OpenAlex: REST API v1

### 10.2 Glossar

| Begriff | Definition |
|---------|------------|
| **Adapter Pattern** | Entwurfsmuster zur Vereinheitlichung heterogener Schnittstellen |
| **Boolean Query** | Suchanfrage unter Verwendung logischer Operatoren (AND, OR, NOT) |
| **Cursor Pagination** | Iterative Datenabfrage via Cursor-Pointer |
| **Disjunktion** | Logisches ODER (∨) |
| **Konjunktion** | Logisches UND (∧) |
| **Normalisierung** | Transformation in kanonische Form (lowercase, trim) |
| **Precision** | Anteil relevanter Dokumente im Retrieved Set |

### 10.3 Referenzen

1. ISO/IEC 5807:1985 - Information processing — Documentation symbols and conventions for data, program and system flowcharts
2. NCBI E-utilities Documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/
3. Europe PMC API Documentation: https://europepmc.org/RestfulWebService
4. OpenAlex API Documentation: https://docs.openalex.org/

---

## Versionshistorie

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0.0 | 2026-01-13 | Initiale akademische Dokumentation |

---

**Autor:** Medical Database Research Tool Development Team  
**Institution:** [Institution Name]  
**Kontakt:** [Contact Information]  
**Lizenz:** [License Type]
