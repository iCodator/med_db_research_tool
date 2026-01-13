# 📊 Flussdiagramm Export-Anleitung

## Dateien

- **`flowchart.mmd`** - Mermaid-Diagramm (Text-Format)
- **`FLOWCHART_ISO5807.txt`** - ASCII-Version (ISO 5807 konform)
- **`WORKFLOW_SCHEMA.txt`** - Detailliertes Workflow-Schema

---

## 🎨 SVG/PNG Export aus Mermaid

### **Option 1: Mermaid Live Editor** ⭐ EMPFOHLEN

1. Öffne: https://mermaid.live/
2. Kopiere Inhalt von `flowchart.mmd` ins linke Feld
3. Rechts siehst du die Live-Vorschau
4. **Export:**
   - **SVG** (Vektorgrafik) → Button "Actions" → "Export SVG"
   - **PNG** (Rastergrafik) → Button "Actions" → "Export PNG"
5. Datei speichern als `flowchart.svg` oder `flowchart.png`

**Vorteile:**
- ✅ Kein Installation nötig
- ✅ Sofortige Vorschau
- ✅ Anpassbar (Farben, Layout)

---

### **Option 2: Mermaid CLI** (für Automatisierung)

#### Installation:
```bash
npm install -g @mermaid-js/mermaid-cli
```

#### Export-Befehle:
```bash
# SVG Export (Vektorgrafik)
mmdc -i docs/flowchart.mmd -o docs/flowchart.svg

# PNG Export (Rastergrafik)
mmdc -i docs/flowchart.mmd -o docs/flowchart.png

# PNG mit höherer Auflösung
mmdc -i docs/flowchart.mmd -o docs/flowchart.png -w 2000

# PDF Export
mmdc -i docs/flowchart.mmd -o docs/flowchart.pdf
```

**Vorteile:**
- ✅ Automatisierbar
- ✅ Batch-Processing möglich
- ✅ CI/CD Integration

---

### **Option 3: VS Code Extension**

#### Installation:
1. VS Code öffnen
2. Extensions: Suche nach "Markdown Preview Mermaid Support"
3. Installieren

#### Verwendung:
1. Öffne `flowchart.mmd` in VS Code
2. **Preview:** `Ctrl+Shift+V` (oder `Cmd+Shift+V` auf Mac)
3. **Export:** Rechtsklick auf Preview → "Export as SVG" oder "Export as PNG"

**Vorteile:**
- ✅ Direkt im Editor
- ✅ Live-Preview
- ✅ Keine separate App

---

## 🔧 SVG Nachbearbeitung

### **Inkscape** (kostenlos, Open Source)
```bash
# Installation
sudo apt install inkscape    # Linux
# oder von https://inkscape.org/

# SVG → PDF
inkscape flowchart.svg --export-filename=flowchart.pdf

# SVG → PNG mit DPI
inkscape flowchart.svg --export-filename=flowchart.png --export-dpi=300
```

### **Adobe Illustrator** (kommerziell)
- SVG direkt öffnen und bearbeiten
- Export zu PDF, EPS, PNG, etc.

---

## 📐 ISO 5807 Symbole in Mermaid

Die Datei `flowchart.mmd` verwendet ISO 5807 konforme Symbole:

| Symbol | Mermaid-Syntax | Bedeutung |
|--------|----------------|-----------|
| Abgerundetes Rechteck | `([Text])` | **Terminator** (Start/Ende) |
| Rechteck | `[Text]` | **Prozess** |
| Raute | `{Text}` | **Entscheidung** |
| Parallelogramm | `[/Text/]` | **Ein-/Ausgabe** |
| Pfeil | `-->` | **Flussrichtung** |

---

## 🎨 Farben anpassen

In `flowchart.mmd` am Ende definiert:

```mermaid
classDef processStyle fill:#e1f5ff,stroke:#333,stroke-width:2px
classDef decisionStyle fill:#fff4e1,stroke:#333,stroke-width:2px
classDef ioStyle fill:#e8f5e9,stroke:#333,stroke-width:2px
classDef terminatorStyle fill:#ffebee,stroke:#333,stroke-width:3px
```

**Anpassen:**
- `fill:#RRGGBB` - Hintergrundfarbe
- `stroke:#RRGGBB` - Rahmenfarbe
- `stroke-width:Xpx` - Rahmendicke

---

## 🚀 Schnellstart

### 1. Einfachster Weg (kein Installation):
```bash
# Browser öffnen
https://mermaid.live/

# Datei kopieren
cat docs/flowchart.mmd | xclip -selection clipboard

# In Browser einfügen
# Export SVG klicken
```

### 2. Mit CLI (einmalige Installation):
```bash
# Installation
npm install -g @mermaid-js/mermaid-cli

# Export
mmdc -i docs/flowchart.mmd -o docs/flowchart.svg
```

---

## 📋 Checkliste

- [ ] `flowchart.mmd` in https://mermaid.live/ öffnen
- [ ] Vorschau prüfen
- [ ] **Export SVG** klicken
- [ ] Datei als `docs/flowchart.svg` speichern
- [ ] Optional: Auch PNG exportieren
- [ ] In Git committen:
  ```bash
  git add docs/flowchart.svg docs/flowchart.png
  git commit -m "Add flowchart visualizations"
  ```

---

## 🔗 Weitere Ressourcen

- **Mermaid Dokumentation:** https://mermaid.js.org/
- **Mermaid Live Editor:** https://mermaid.live/
- **ISO 5807 Standard:** https://www.iso.org/standard/11955.html
- **Mermaid CLI GitHub:** https://github.com/mermaid-js/mermaid-cli

---

## ⚠️ Troubleshooting

### Problem: "mmdc: command not found"
**Lösung:** Mermaid CLI nicht installiert
```bash
npm install -g @mermaid-js/mermaid-cli
```

### Problem: SVG wird nicht angezeigt
**Lösung:** Browser aktualisieren oder anderen Browser versuchen

### Problem: Layout sieht komisch aus
**Lösung:** In Mermaid Live:
- "Configuration" → "Theme" ändern
- "Direction" auf "TD" (Top-Down) setzen

---

## 📝 Hinweise

- **SVG ist empfohlen** für Dokumentation (verlustfrei skalierbar)
- **PNG** für E-Mails oder PowerPoint (falls SVG nicht unterstützt)
- **PDF** für Ausdrucke oder offizielle Dokumente
