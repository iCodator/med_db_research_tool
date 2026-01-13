# 📊 Flussdiagramm-Erklärung für Laien

## Was zeigt das Diagramm?

Dieses Flussdiagramm erklärt **Schritt für Schritt**, wie das Medical Database Research Tool funktioniert - von der Eingabe einer Suchanfrage bis zum fertigen Ergebnis mit wissenschaftlichen Artikeln.

---

## 🎯 Das Gesamtbild

Stellen Sie sich vor, Sie möchten wissenschaftliche Artikel finden, die über **Parodontitis UND Coenzym Q10** berichten. Das Tool hilft Ihnen dabei, in drei verschiedenen medizinischen Datenbanken zu suchen und die Ergebnisse übersichtlich zu speichern.

---

## 📖 Der Ablauf Schritt für Schritt

### **1. START: Das Tool wird gestartet**

```
( START )
```

Sie starten das Programm mit `python src/main.py`.

---

### **2. Eingabe: Sie geben eine Datei an**

```
┌─────────────────────┐
│  Benutzer gibt      │
│  Query-Datei ein    │
└─────────────────────┘
```

**Was passiert hier?**
- Sie werden gefragt: "Welche Query-Datei möchten Sie verwenden?"
- Sie geben z.B. `openalex.txt` ein

**Warum eine Datei?**
- Ihre Suchanfragen können komplex sein
- In einer Datei können Sie die Suche in Ruhe vorbereiten
- Sie können die Datei wiederverwenden

---

### **3. Datei einlesen: Das Tool liest Ihre Suchanfrage**

```
┌─────────────────────┐
│  Query Handler:     │
│  Datei einlesen     │
└─────────────────────┘
```

**Was passiert hier?**
- Das Tool öffnet Ihre Datei
- Liest den Inhalt (Ihre Suchbegriffe)
- Bereitet die Suche vor

---

### **4. Datenbank erkennen: Welche Datenbank wollen Sie durchsuchen?**

```
      / \
     /   \
    /Daten\
    \bank?/
     \   /
      \ /
```

**Entscheidung basierend auf Dateiname:**

| Dateiname | Datenbank | Was wird durchsucht? |
|-----------|-----------|---------------------|
| `pubmed.txt` | **PubMed** | Medizinische Datenbank der USA |
| `europepmc.txt` | **Europe PMC** | Europäische medizinische Datenbank |
| `openalex.txt` | **OpenAlex** | Weltweite wissenschaftliche Datenbank |

**Warum ist das wichtig?**
- Jede Datenbank hat eigene Regeln
- Das Tool muss wissen, wie es mit jeder sprechen soll

---

### **5. AND-Logik erkennen: Wie ist Ihre Suche aufgebaut?**

```
      / \
     /AND\
     \   /
      \ /
```

**Das Tool prüft:**

#### **A) Keine AND-Logik**
**Beispiel:** `"Parodontitis"`
- Sie suchen nur nach einem Begriff
- **→ Pfad:** Normale Suche

#### **B) Einzeilig AND** (für ALLE Datenbanken)
**Beispiel:** `"Parodontitis AND Coenzym Q10"`
- Sie suchen nach Artikeln, die BEIDE Begriffe enthalten
- Die Begriffe stehen in **einer Zeile** mit dem Wort "AND" dazwischen
- **→ Pfad:** Normale Suche mit AND-Operator

#### **C) Mehrzeilig AND** (nur OpenAlex)
**Beispiel:**
```
Parodontitis OR Parodontalerkrankung
AND
Ubiquinon OR Coenzym Q10
```
- Komplexe Suche mit mehreren Zeilen
- Erste Zeile: Gruppe A (Parodontitis-Begriffe)
- "AND" in separater Zeile
- Zweite Zeile: Gruppe B (Q10-Begriffe)
- **→ Pfad:** Split & Merge (aufwändiger, aber präziser)

**Warum ist das wichtig?**
- Bestimmt, **wie** das Tool sucht
- Einfache Suchen sind schneller
- Komplexe Suchen sind präziser (aber langsamer)

---

## 🛤️ Die drei verschiedenen Such-Pfade

### **Pfad 1: Normale Suche (ohne AND)**

```
┌────────────────┐
│ Normale Suche  │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  API-Aufruf    │
└───────┬────────┘
        │
        ▼
┌────────────────┐
│ Artikel        │
│standardisieren │
└───────┬────────┘
        │
        ▼
   Zum Export
```

**Was passiert?**
1. **API-Aufruf:** Das Tool fragt die Datenbank nach Ihren Begriffen
2. **Standardisieren:** Die Artikel werden in ein einheitliches Format gebracht
3. **Export:** Fertig!

**Beispiel:**
- Suche: `"Diabetes"`
- Ergebnis: Alle Artikel über Diabetes

**Dauer:** ~1-5 Minuten (je nach Anzahl Treffer)

---

### **Pfad 2: Einzeilig AND (für alle Datenbanken)**

```
┌─────────────────────┐
│ Normale Suche       │
│ mit AND-Operator    │
│ im Query-String     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ API-Aufruf:         │
│ Query: A AND B      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Artikel             │
│ standardisieren     │
└──────────┬──────────┘
           │
           ▼
      Zum Export
```

**Was passiert?**
1. **API-Aufruf mit AND:** Die Datenbank bekommt: "Suche A AND B"
2. **Datenbank filtert:** Nur Artikel mit BEIDEN Begriffen werden zurückgegeben
3. **Standardisieren:** Einheitliches Format
4. **Export:** Fertig!

**Beispiel:**
- Suche: `"Diabetes AND Insulin"`
- Ergebnis: Nur Artikel, die SOWOHL "Diabetes" ALS AUCH "Insulin" erwähnen

**Dauer:** ~1-5 Minuten

**Vorteil:**
- ✅ Schnell
- ✅ Funktioniert bei allen Datenbanken

---

### **Pfad 3: Mehrzeilig AND (nur OpenAlex, aufwändig aber präzise)**

```
┌──────────────────┐
│ Query Splitter:  │
│  Split in A & B  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Suche A│ │ Suche B│
└───┬────┘ └───┬────┘
    │          │
    ▼          ▼
┌────────┐ ┌────────┐
│Export A│ │Export B│
└───┬────┘ └───┬────┘
    └────┬─────┘
         │
         ▼
   ┌────────────┐
   │   MERGER   │
   └─────┬──────┘
         │
         ▼
    Zum Export
```

**Was passiert? (Schritt für Schritt)**

#### **Schritt 1: Splitten**
```
Eingabe:
Parodontitis OR Parodontalerkrankung
AND
Ubiquinon OR Coenzym Q10
```

**Das Tool teilt auf:**
- **Gruppe A:** Parodontitis OR Parodontalerkrankung
- **Gruppe B:** Ubiquinon OR Coenzym Q10

**Warum?**
- OpenAlex kann nicht direkt mit mehrzeiligen AND-Suchen umgehen
- Wir müssen die Suche aufteilen

#### **Schritt 2: Parallele Suchen**
```
Suche A:                    Suche B:
"Parodontitis OR            "Ubiquinon OR
 Parodontalerkrankung"       Coenzym Q10"

↓                          ↓

95.513 Artikel             16.268 Artikel
gefunden                   gefunden
```

**Was passiert?**
- Zwei separate Suchen laufen
- Gruppe A findet ALLE Artikel über Parodontitis
- Gruppe B findet ALLE Artikel über Q10

#### **Schritt 3: Zwischenergebnisse speichern**
```
Export A:                   Export B:
periodontitis_A_*.csv       ubiquinone_B_*.json
periodontitis_A_*.json      ubiquinone_B_*.csv
```

**Warum speichern?**
- Falls etwas schief geht, können wir hier weitermachen
- Sie können die Zwischenergebnisse auch selbst nutzen

#### **Schritt 4: MERGER - Das Herzstück!**

Der Merger findet heraus, welche Artikel in **BEIDEN** Listen vorkommen.

**3 Unterschritte:**

##### **Schritt 4.1: Match-Finding**
```
Liste A: 95.513 Artikel
Liste B: 16.268 Artikel

Vergleich: Titel + Autoren

↓

161 Artikel sind in BEIDEN Listen!
```

**Wie funktioniert das?**
- Vergleicht jeden Artikel aus A mit jedem aus B
- Prüft: Ist Titel UND Autorenliste identisch?
- Wenn ja → Match!

**Beispiel:**
```
Artikel in Liste A:
- Titel: "Coenzyme Q10 in periodontal treatment"
- Autoren: "Smith J, Miller A"

Artikel in Liste B:
- Titel: "Coenzyme Q10 in periodontal treatment"
- Autoren: "Smith J, Miller A"

→ MATCH! (Titel und Autoren sind identisch)
```

##### **Schritt 4.2: Content-Validation (Qualitätskontrolle)**
```
161 Matches

Prüfung: Sind die Suchbegriffe wirklich im Text?

↓

61 Artikel bestehen die Prüfung
```

**Was wird geprüft?**
- Ist mindestens EIN Begriff aus Gruppe A im Text? (Titel ODER Abstract)
- Ist mindestens EIN Begriff aus Gruppe B im Text? (Titel ODER Abstract)
- Nur wenn BEIDE Bedingungen erfüllt → Artikel bleibt

**Warum ist das nötig?**
- Match-Finding ist nicht perfekt
- Manchmal gibt es falsche Treffer (z.B. ähnliche Titel)
- Diese Prüfung filtert sie raus

**Beispiel eines aussortierten Artikels:**
```
Artikel:
- Titel: "Periodontal treatment methods"
- Abstract: "...verschiedene Methoden..."

Problem: 
- Enthält "periodontal" (Gruppe A) ✓
- Enthält NICHT "ubiquinone" oder "coenzym q10" (Gruppe B) ✗

→ AUSGESCHLOSSEN (nur 1 von 2 Gruppen)
```

##### **Schritt 4.3: Deduplizierung (Duplikate entfernen)**
```
61 validierte Artikel

Prüfung auf Duplikate

↓

61 eindeutige Artikel
(0 Duplikate gefunden)
```

**Was wird geprüft?**
- Gibt es Artikel mit identischem Titel UND Autoren?
- Wenn ja → Nur der erste wird behalten

**In diesem Beispiel:** Keine Duplikate gefunden!

#### **Schritt 5: Finaler Export**
```
openalex_2026-01-13_17-07-23.csv
openalex_2026-01-13_17-07-23.json

Inhalt: 61 hochrelevante Artikel
```

**Was ist das Besondere?**
- Diese 61 Artikel behandeln DEFINITIV beide Themen
- Höchste Qualität und Relevanz
- Perfekt für Ihre Recherche!

**Dauer des gesamten Prozesses:** ~15-30 Minuten
- Suche A: ~13 Minuten
- Suche B: ~2 Minuten
- Merge: ~1 Minute

---

## 🎨 Die Farben im Diagramm

### **🔴 Rot (Terminatoren)**
```
( START )
( ENDE  )
```
**Bedeutung:** Anfang und Ende des Programms

### **🟢 Grün (Ein-/Ausgabe)**
```
┌──────────────┐
│/ Eingabe    /│
│\ Ausgabe    \│
└──────────────┘
```
**Bedeutung:** 
- Benutzer gibt etwas ein
- System gibt etwas aus (z.B. Dateien)

### **🟡 Gelb (Entscheidungen)**
```
    / \
   /   \
  /Frage\
  \  ?  /
   \   /
    \ /
```
**Bedeutung:** 
- Das Programm muss eine Entscheidung treffen
- "Wenn dies, dann das"

### **🔵 Blau (Prozesse)**
```
┌──────────────┐
│  Prozess     │
└──────────────┘
```
**Bedeutung:**
- Normale Verarbeitungsschritte
- Das Programm tut etwas

---

## 📊 Export: Was bekommen Sie am Ende?

Egal welcher Pfad: Am Ende werden **immer zwei Dateien** erstellt:

### **CSV-Datei** (für Excel, LibreOffice)
```
Spalten:
- authors   → Wer hat den Artikel geschrieben?
- title     → Wie heißt der Artikel?
- year      → Wann wurde er veröffentlicht?
- doi       → Eindeutige Kennung (wie eine ISBN für Bücher)
- url       → Wo kann ich ihn lesen?
- abstract  → Zusammenfassung des Artikels
```

**Verwendung:**
- In Excel öffnen
- Filtern, sortieren
- Für Ihre Arbeit weiterverarbeiten

### **JSON-Datei** (für weitere Programmierung)
```json
{
  "metadata": {
    "database": "openalex",
    "timestamp": "2026-01-13 17:07:23",
    "total_results": 61
  },
  "articles": [...]
}
```

**Verwendung:**
- Für weitere automatische Verarbeitung
- Datenanalyse mit Python/R
- Import in andere Tools

---

## 💡 Praktische Beispiele

### **Beispiel 1: Einfache Suche (keine AND-Logik)**

**Datei:** `pubmed.txt`
```
Diabetes
```

**Ablauf:**
1. Start → Eingabe → Datei einlesen
2. Datenbank: PubMed erkannt
3. AND-Logik? NEIN
4. Normale Suche → API-Aufruf → Export
5. Ende

**Ergebnis:** Alle PubMed-Artikel über Diabetes

**Dauer:** ~2 Minuten

---

### **Beispiel 2: Einzeilig AND (für alle Datenbanken)**

**Datei:** `europepmc.txt`
```
Diabetes AND Insulin
```

**Ablauf:**
1. Start → Eingabe → Datei einlesen
2. Datenbank: Europe PMC erkannt
3. AND-Logik? JA, einzeilig
4. Normale Suche mit AND → API-Aufruf ("Diabetes AND Insulin") → Export
5. Ende

**Ergebnis:** Artikel die SOWOHL Diabetes ALS AUCH Insulin behandeln

**Dauer:** ~3 Minuten

---

### **Beispiel 3: Mehrzeilig AND (nur OpenAlex)**

**Datei:** `openalex.txt`
```
Parodontitis OR Parodontalerkrankung OR Zahnfleischentzündung
AND
Ubiquinon OR "Coenzym Q10" OR Ubiquinol
2000-2024
```

**Ablauf:**
1. Start → Eingabe → Datei einlesen
2. Datenbank: OpenAlex erkannt
3. AND-Logik? JA, mehrzeilig
4. Query Splitter → 
   - Suche A (Parodontitis-Begriffe) → Export A
   - Suche B (Q10-Begriffe) → Export B
5. Merger:
   - Match-Finding (161 Treffer)
   - Content-Validation (61 Treffer)
   - Deduplizierung (61 Treffer)
6. Finaler Export
7. Ende

**Ergebnis:** 61 hochrelevante Artikel über Parodontitis UND Q10

**Dauer:** ~20 Minuten

---

## ❓ Häufige Fragen

### **Warum drei verschiedene Pfade?**
- **Einfache Suchen** → Einfacher Pfad (schnell)
- **Einzeilig AND** → Mittlerer Pfad (schnell, präzise)
- **Mehrzeilig AND** → Komplexer Pfad (langsam, aber am präzisesten)

### **Warum ist mehrzeilig AND nur für OpenAlex?**
- OpenAlex hat die meisten Artikel (>200 Millionen)
- Mehrzeiliger AND ist aufwändiger → lohnt sich bei großer Datenmenge
- PubMed/Europe PMC haben weniger Artikel → einzeiliges AND reicht

### **Was ist der Unterschied zwischen Match-Finding und Content-Validation?**
- **Match-Finding:** Findet Artikel die in beiden Listen sind (grob)
- **Content-Validation:** Prüft ob die Begriffe wirklich im Text sind (fein)
- Zusammen: Maximale Präzision!

### **Warum Zwischenergebnisse speichern?**
- Falls das Programm abstürzt, ist nicht alles weg
- Sie können die Einzelergebnisse auch für sich nutzen
- Transparenz: Sie sehen was das Programm macht

### **Kann ich den Merge-Prozess überspringen?**
- Ja! Nutzen Sie einzeiliges AND statt mehrzeilig
- Beispiel: `"Parodontitis AND Ubiquinon"` statt mehrzeilig
- Dann läuft Pfad 2 (schneller, aber eventuell weniger Treffer)

---

## 🎓 Technische Details (für Interessierte)

### **API = Application Programming Interface**
- Schnittstelle zur Datenbank
- Wie eine "Telefonhotline" für Computer
- Tool fragt, Datenbank antwortet

### **Standardisierung**
- Jede Datenbank liefert Daten anders
- "Standardisierung" = Einheitliches Format erstellen
- Dann sind alle Ergebnisse vergleichbar

### **Pagination**
- Datenbanken liefern nicht alle Artikel auf einmal
- Tool fragt mehrmals nach ("Seite 1", "Seite 2", ...)
- Wird automatisch gemacht

### **Rate Limiting**
- Datenbanken haben Limits (z.B. max. 10 Anfragen/Sekunde)
- Tool wartet automatisch zwischen Anfragen
- Vermeidet Blockierung

---

## 📚 Zusammenfassung

**Das Tool macht aus Ihrer Suchanfrage eine strukturierte CSV/JSON-Datei mit wissenschaftlichen Artikeln.**

**Drei Wege:**
1. **Einfach:** Suche ohne AND → Schnell
2. **Mittel:** Einzeiliges AND → Schnell + präzise
3. **Komplex:** Mehrzeiliges AND (nur OpenAlex) → Langsam aber am präzisesten

**Qualitätssicherung (bei mehrzeilig AND):**
- Match-Finding: Findet Überschneidungen
- Content-Validation: Prüft Relevanz
- Deduplizierung: Entfernt Dopplungen

**Ergebnis:** Hochrelevante Artikel für Ihre Forschung! 🎯
