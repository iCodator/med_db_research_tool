#!/usr/bin/env python3
"""
Kroki.io Export Script for Mermaid Diagrams

Exports flowchart.mmd to SVG, PNG, and PDF using Kroki.io API.

Usage:
    python docs/export_kroki.py --format svg
    python docs/export_kroki.py --format png
    python docs/export_kroki.py --format pdf
    python docs/export_kroki.py --format all

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
    print("Error: requests library not found")
    print("Install with: pip install requests")
    sys.exit(1)


# Configuration
KROKI_API_URL = "https://kroki.io"
MERMAID_FILE = Path("docs/flowchart.mmd")
OUTPUT_DIR = Path("docs")

FormatType = Literal["svg", "png", "pdf"]


def read_mermaid_file(filepath: Path) -> str:
    """Read Mermaid diagram from file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Mermaid file not found: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"✓ Read {len(content)} bytes from {filepath}")
    return content


def export_diagram(mermaid_code: str, format_type: FormatType, output_path: Path) -> None:
    """Export Mermaid diagram to specified format using Kroki.io."""
    
    url = f"{KROKI_API_URL}/mermaid/{format_type}"
    
    print(f"→ Sending request to Kroki.io ({format_type.upper()})...")
    
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
        print(f"✓ Exported {format_type.upper()}: {output_path} ({file_size:,} bytes)")
        
    except requests.exceptions.Timeout:
        print(f"✗ Error: Request timeout for {format_type.upper()}")
        raise
    except requests.exceptions.HTTPError as e:
        print(f"✗ Error: HTTP {response.status_code} for {format_type.upper()}")
        print(f"  Response: {response.text[:200]}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: Network error for {format_type.upper()}: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export Mermaid diagrams via Kroki.io",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docs/export_kroki.py --format svg
  python docs/export_kroki.py --format png
  python docs/export_kroki.py --format all
  python docs/export_kroki.py --format all --output-dir output
        """
    )
    
    parser.add_argument(
        "--format",
        choices=["svg", "png", "pdf", "all"],
        required=True,
        help="Export format (or 'all' for all formats)"
    )
    
    parser.add_argument(
        "--input",
        type=Path,
        default=MERMAID_FILE,
        help=f"Input Mermaid file (default: {MERMAID_FILE})"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default="flowchart_kroki",
        help="Output filename prefix (default: flowchart_kroki)"
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read Mermaid diagram
    try:
        mermaid_code = read_mermaid_file(args.input)
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    
    # Determine formats to export
    if args.format == "all":
        formats: list[FormatType] = ["svg", "png", "pdf"]
    else:
        formats = [args.format]  # type: ignore
    
    # Export diagrams
    print(f"\n{'='*60}")
    print(f"Kroki.io Export")
    print(f"{'='*60}")
    print(f"Input:  {args.input}")
    print(f"Output: {args.output_dir}")
    print(f"Formats: {', '.join(f.upper() for f in formats)}")
    print(f"{'='*60}\n")
    
    success_count = 0
    error_count = 0
    
    for fmt in formats:
        output_path = args.output_dir / f"{args.prefix}.{fmt}"
        
        try:
            export_diagram(mermaid_code, fmt, output_path)
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to export {fmt.upper()}: {e}")
            error_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {success_count} succeeded, {error_count} failed")
    print(f"{'='*60}\n")
    
    if error_count > 0:
        sys.exit(1)
    
    print("✓ All exports completed successfully!")


if __name__ == "__main__":
    main()
