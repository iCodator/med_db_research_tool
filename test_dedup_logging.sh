#!/bin/bash
# Test-Skript für dedup.py Logging-Funktionalität

echo "=========================================="
echo "Test 1: Help anzeigen"
echo "=========================================="
python dedup.py --help
echo ""
echo ""

echo "=========================================="
echo "Test 2: Syntax-Check"
echo "=========================================="
python -m py_compile dedup.py
python -m py_compile src/utils/deduplicator.py
echo "✓ Syntax OK"
echo ""
echo ""

echo "=========================================="
echo "Test abgeschlossen"
echo "=========================================="
echo ""
echo "Manuelle Tests erforderlich:"
echo "1. python dedup.py --log-mode none"
echo "   (keine Logs, nur Konsolen-Ausgabe)"
echo ""
echo "2. python dedup.py --log-mode simple"
echo "   (einfaches Logging pro Datenbank)"
echo ""
echo "3. python dedup.py --log-mode detailed"
echo "   (detailliertes Logging mit Duplikate-Liste)"
echo ""
echo "4. python dedup.py"
echo "   (interaktive Auswahl)"
