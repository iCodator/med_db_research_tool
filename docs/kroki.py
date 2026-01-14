#!/usr/bin/env python3
"""
Kroki.io Mermaid Converter

Konvertiert alle .mmd Dateien im Script-Verzeichnis zu SVG und PNG
über die Kroki.io API (https://kroki.io).

Usage:
    python kroki.py --format svg    # Nur SVG generieren
    python kroki.py --format png    # Nur PNG generieren
    python kroki.py --format all    # SVG + PNG (Standard)

Das Script durchsucht das Verzeichnis, in dem es sich befindet,
nach allen *.mmd Dateien und konvertiert sie automatisch.

Output: Die generierten Dateien werden in Unterverzeichnissen gespeichert:
        - SVG-Dateien: ./svg/
        - PNG-Dateien: ./png/

Versionierung: Alle Dateien erhalten automatisch eine Versionsnummer (_XX)
               beginnend bei _00 und aufsteigend bei jedem Export.

Requirements:
    - requests library: pip install requests
"""

import argparse
import sys
from pathlib import Path
from typing import Literal

try:
    import requests
except ImportError:
    print("✗ Error: requests library not found")
    print("  Install with: pip install requests")
    sys.exit(1)


# Configuration
KROKI_API_URL = "https://kroki.io"
SCRIPT_DIR = Path(__file__).parent
MERMAID_DIR = SCRIPT_DIR / "mermaid"

FormatType = Literal["svg", "png"]


def find_mermaid_files() -> list[Path]:
    """Find all .mmd files in mermaid subdirectory."""
    if not MERMAID_DIR.exists():
        return []
    mermaid_files = list(MERMAID_DIR.glob('*.mmd'))
    return sorted(mermaid_files)


def get_next_version_filename(output_dir: Path, basename: str, ext: str) -> Path:
    """
    Find next available version number.
    Always uses versioning (_XX), starting at _00.
    
    Args:
        output_dir: Output directory
        basename: Base filename without extension
        ext: File extension (svg or png)
    
    Returns:
        Path with versioned filename
    """
    version = 0
    while True:
        versioned_path = output_dir / f"{basename}_{version:02d}.{ext}"
        if not versioned_path.exists():
            return versioned_path
        version += 1


def read_mermaid_file(filepath: Path) -> str:
    """Read Mermaid diagram from file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Mermaid file not found: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content


def export_diagram(mermaid_code: str, format_type: FormatType, output_path: Path) -> None:
    """Export Mermaid diagram to specified format using Kroki.io."""
    
    url = f"{KROKI_API_URL}/mermaid/{format_type}"
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "text/plain"},
            data=mermaid_code.encode("utf-8"),
            timeout=30
        )
        
        response.raise_for_status()
        
        # Write output
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"  ✓ {format_type.upper()}: {output_path.name} ({file_size:,} bytes)")
        
    except requests.exceptions.Timeout:
        print(f"  ✗ Error: Request timeout for {format_type.upper()}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ Error: HTTP {response.status_code} for {format_type.upper()}")
        print(f"    Response: {response.text[:200]}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: Network error for {format_type.upper()}: {e}")
        raise


def process_mermaid_file(mmd_file: Path, formats: list[FormatType]) -> tuple[int, int]:
    """
    Process a single Mermaid file.
    
    Returns:
        (success_count, error_count) tuple
    """
    basename = mmd_file.stem
    print(f"\n📄 Processing: {mmd_file.name}")
    
    # Read Mermaid content
    try:
        mermaid_code = read_mermaid_file(mmd_file)
    except Exception as e:
        print(f"  ✗ Failed to read file: {e}")
        return (0, len(formats))
    
    success_count = 0
    error_count = 0
    
    # Export to each format
    for fmt in formats:
        # Create output directory
        output_dir = SCRIPT_DIR / fmt
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get versioned filename
        output_path = get_next_version_filename(output_dir, basename, fmt)
        
        try:
            export_diagram(mermaid_code, fmt, output_path)
            success_count += 1
        except Exception as e:
            error_count += 1
    
    return (success_count, error_count)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Kroki.io Mermaid Converter - Convert all .mmd files to SVG/PNG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Das Script konvertiert alle .mmd Dateien im aktuellen Verzeichnis
zu SVG und/oder PNG über die Kroki.io API.

Output-Struktur:
  ./svg/filename_00.svg, filename_01.svg, ...
  ./png/filename_00.png, filename_01.png, ...

Beispiele:
  python kroki.py --format all    # SVG + PNG (Standard)
  python kroki.py --format svg    # Nur SVG
  python kroki.py --format png    # Nur PNG
        """
    )
    
    parser.add_argument(
        "--format",
        choices=["svg", "png", "all"],
        default="all",
        help="Export format (default: all)"
    )
    
    args = parser.parse_args()
    
    # Determine formats to export
    if args.format == "all":
        formats: list[FormatType] = ["svg", "png"]
    else:
        formats = [args.format]  # type: ignore
    
    # Find all Mermaid files
    mermaid_files = find_mermaid_files()
    
    if not mermaid_files:
        print("⚠ No .mmd files found in current directory")
        print(f"  Searched in: {SCRIPT_DIR}")
        sys.exit(0)
    
    # Print header
    print(f"\n{'='*60}")
    print(f"Kroki.io Mermaid Converter")
    print(f"{'='*60}")
    print(f"Directory: {SCRIPT_DIR}")
    print(f"Files found: {len(mermaid_files)}")
    print(f"Formats: {', '.join(f.upper() for f in formats)}")
    print(f"{'='*60}")
    
    # Process each file
    total_success = 0
    total_errors = 0
    
    for mmd_file in mermaid_files:
        success, errors = process_mermaid_file(mmd_file, formats)
        total_success += success
        total_errors += errors
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Files processed: {len(mermaid_files)}")
    print(f"Exports successful: {total_success}")
    print(f"Exports failed: {total_errors}")
    print(f"{'='*60}\n")
    
    if total_errors > 0:
        sys.exit(1)
    
    print("✓ All exports completed successfully!")


if __name__ == "__main__":
    main()
