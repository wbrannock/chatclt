#!/usr/bin/env python3
"""
Convert all doc/docx/html/rtf/xls/xlsx files in a directory tree to PDF,
then remove the originals. Skips files that are already PDF.

Uses:
  - pandoc --pdf-engine=weasyprint  for doc, docx, rtf, xlsx
  - weasyprint                      for html (handles local file references better)

Usage:
  python scripts/convert_to_pdf.py <directory>
  python scripts/convert_to_pdf.py <directory> --workers 8
  python scripts/convert_to_pdf.py <directory> --dry-run
"""

import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PANDOC_FORMATS = {".docx", ".rtf", ".xlsx"}
TEXTUTIL_FORMATS = {".doc", ".xls"}  # old binary formats — use macOS textutil -> weasyprint
WEASYPRINT_FORMATS = {".html", ".htm"}
SKIP_FORMATS = {".pdf"}


def _convert_via_html_strip_images(src: Path, dest: Path) -> tuple[Path, bool, str]:
    """Fallback: pandoc → HTML, strip img tags, weasyprint → PDF."""
    tmp_html = src.with_suffix(".stripped.html.tmp")
    try:
        r1 = subprocess.run(
            ["pandoc", str(src), "-o", str(tmp_html)],
            capture_output=True, text=True, timeout=60
        )
        if r1.returncode != 0 or not tmp_html.exists():
            return src, False, f"pandoc→html failed: {r1.stderr.strip()[:200]}"

        html = tmp_html.read_text(encoding="utf-8", errors="replace")
        html = re.sub(r"<img[^>]*>", "", html, flags=re.IGNORECASE)
        tmp_html.write_text(html, encoding="utf-8")

        r2 = subprocess.run(
            ["weasyprint", str(tmp_html), str(dest)],
            capture_output=True, text=True, timeout=60
        )
        if r2.returncode != 0 and not dest.exists():
            return src, False, f"weasyprint failed after image strip: {r2.stderr.strip()[:200]}"

        if not dest.exists() or dest.stat().st_size == 0:
            return src, False, "output PDF missing after image strip"

        src.unlink()
        return src, True, "converted (WMF images stripped) and removed original"
    finally:
        tmp_html.unlink(missing_ok=True)


def convert_file(src: Path, dry_run: bool) -> tuple[Path, bool, str]:
    suffix = src.suffix.lower()
    dest = src.with_suffix(".pdf")

    if dest.exists():
        return src, True, "already exists, skipped"

    if dry_run:
        tool = "pandoc" if suffix in PANDOC_FORMATS else "textutil→weasyprint" if suffix in TEXTUTIL_FORMATS else "weasyprint"
        return src, True, f"[dry-run] would convert via {tool}"

    try:
        if suffix in PANDOC_FORMATS:
            result = subprocess.run(
                ["pandoc", str(src), "--pdf-engine=weasyprint", "-o", str(dest)],
                capture_output=True, text=True, timeout=60
            )
            # If WMF image error, retry via HTML with images stripped
            if result.returncode != 0 and not dest.exists():
                if "WMF" in result.stderr or "cannot find loader" in result.stderr:
                    return _convert_via_html_strip_images(src, dest)
                return src, False, f"conversion failed: {result.stderr.strip()[:200]}"
        elif suffix in TEXTUTIL_FORMATS:
            tmp_html = src.with_suffix(".html.tmp")
            r1 = subprocess.run(
                ["textutil", "-convert", "html", str(src), "-output", str(tmp_html)],
                capture_output=True, text=True, timeout=30
            )
            if r1.returncode != 0:
                return src, False, f"textutil failed: {r1.stderr.strip()[:200]}"
            result = subprocess.run(
                ["weasyprint", str(tmp_html), str(dest)],
                capture_output=True, text=True, timeout=60
            )
            tmp_html.unlink(missing_ok=True)
            if result.returncode != 0 and not dest.exists():
                return src, False, f"weasyprint failed: {result.stderr.strip()[:200]}"
        elif suffix in WEASYPRINT_FORMATS:
            result = subprocess.run(
                ["weasyprint", str(src), str(dest)],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0 and not dest.exists():
                return src, False, f"conversion failed: {result.stderr.strip()[:200]}"
        else:
            return src, False, f"unsupported format: {suffix}"

        if not dest.exists() or dest.stat().st_size == 0:
            return src, False, "output PDF is missing or empty"

        src.unlink()
        return src, True, "converted and removed original"

    except subprocess.TimeoutExpired:
        if dest.exists():
            dest.unlink()
        return src, False, "timed out after 60s"
    except Exception as e:
        return src, False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Convert files to PDF recursively.")
    parser.add_argument("directory", help="Root directory to scan")
    parser.add_argument("--workers", type=int, default=6, help="Parallel workers (default: 6)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be converted without doing it")
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.exists():
        print(f"Error: directory not found: {root}")
        sys.exit(1)

    all_formats = PANDOC_FORMATS | TEXTUTIL_FORMATS | WEASYPRINT_FORMATS
    files = [f for f in root.rglob("*") if f.is_file() and f.suffix.lower() in all_formats]

    if not files:
        print("No convertible files found.")
        return

    print(f"Found {len(files)} files to convert ({'' if not args.dry_run else 'dry-run — '}using {args.workers} workers)\n")

    succeeded, failed = [], []

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(convert_file, f, args.dry_run): f for f in files}
        for i, future in enumerate(as_completed(futures), 1):
            src, ok, msg = future.result()
            status = "✓" if ok else "✗"
            print(f"[{i:>4}/{len(files)}] {status} {src.relative_to(root)}  —  {msg}")
            (succeeded if ok else failed).append(src)

    print(f"\n{'=' * 60}")
    print(f"Done. {len(succeeded)} succeeded, {len(failed)} failed.")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  {f}")


if __name__ == "__main__":
    main()
