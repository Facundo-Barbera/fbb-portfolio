#!/usr/bin/env python3
"""
Automated Notebook Export Script

This script exports all Jupyter notebooks in the notebooks/ directory to HTML reports
in the reports/exports/ directory. If Pandoc is installed, it can also export to PDF.

Usage:
    python scripts/export_reports.py [--format html|pdf|both] [--verbose]

Requirements:
    - nbconvert (pip install nbconvert)
    - For PDF export: pandoc (https://pandoc.org/installing.html)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import logging
from typing import List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Notebook configuration
NOTEBOOKS_DIR = Path("notebooks")
EXPORTS_DIR = Path("reports/exports")
NOTEBOOK_ORDER = [
    ("database_processing.ipynb", "01_database_processing_report"),
    ("data_imputation.ipynb", "02_data_imputation_report"),
    ("exploration.ipynb", "03_exploration_report"),
    ("statistical_analysis.ipynb", "04_statistical_analysis_report"),
    ("cuantitative_analysis.ipynb", "05_quantitative_analysis_report"),
]

def check_dependencies() -> dict:
    """Check if required dependencies are available."""
    deps = {
        'nbconvert': False,
        'pandoc': False
    }
    
    # Check nbconvert
    try:
        result = subprocess.run(['jupyter', 'nbconvert', '--version'], 
                              capture_output=True, text=True, check=True)
        deps['nbconvert'] = True
        logger.info(f"nbconvert available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("nbconvert not found. Install with: pip install nbconvert")
    
    # Check pandoc (for PDF export)
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, check=True)
        deps['pandoc'] = True
        logger.info(f"pandoc available: {result.stdout.split()[1]}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("pandoc not found. PDF export will not be available.")
        logger.warning("Install pandoc from: https://pandoc.org/installing.html")
    
    return deps

def create_export_directory():
    """Create the exports directory if it doesn't exist."""
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Export directory ready: {EXPORTS_DIR}")

def export_notebook(notebook_path: Path, output_name: str, format: str, verbose: bool = False) -> bool:
    """
    Export a single notebook to the specified format.
    
    Args:
        notebook_path: Path to the input notebook
        output_name: Name for the output file (without extension)
        format: Export format ('html' or 'pdf')
        verbose: Enable verbose logging
        
    Returns:
        True if export was successful, False otherwise
    """
    output_file = f"{output_name}.{format}"
    output_path = EXPORTS_DIR / output_file
    
    cmd = [
        'jupyter', 'nbconvert',
        '--to', format,
        str(notebook_path),
        '--output-dir', str(EXPORTS_DIR),
        '--output', output_file
    ]
    
    try:
        logger.info(f"Exporting {notebook_path.name} to {format.upper()}...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if verbose:
            logger.info(f"Export command: {' '.join(cmd)}")
            if result.stdout:
                logger.info(f"stdout: {result.stdout}")
        
        if result.stderr and "WARNING" in result.stderr:
            logger.warning(f"Export warnings for {notebook_path.name}: {result.stderr}")
        
        logger.info(f"✓ Successfully exported: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ Failed to export {notebook_path.name} to {format}")
        logger.error(f"Error: {e.stderr}")
        return False

def export_all_notebooks(formats: List[str], verbose: bool = False) -> Tuple[int, int]:
    """
    Export all notebooks in the configured order.
    
    Args:
        formats: List of formats to export ('html', 'pdf')
        verbose: Enable verbose logging
        
    Returns:
        Tuple of (successful_exports, total_attempts)
    """
    successful = 0
    total = 0
    
    for notebook_file, output_name in NOTEBOOK_ORDER:
        notebook_path = NOTEBOOKS_DIR / notebook_file
        
        if not notebook_path.exists():
            logger.warning(f"Notebook not found: {notebook_path}")
            continue
        
        for format in formats:
            total += 1
            if export_notebook(notebook_path, output_name, format, verbose):
                successful += 1
    
    return successful, total

def create_index_html():
    """Create an index.html file listing all exported reports."""
    index_path = EXPORTS_DIR / "index.html"
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Air Quality Analysis Reports</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .report-list {{ list-style: none; padding: 0; }}
        .report-list li {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .report-list a {{ text-decoration: none; color: #0066cc; font-weight: bold; }}
        .report-list a:hover {{ text-decoration: underline; }}
        .description {{ color: #666; font-size: 0.9em; margin-top: 5px; }}
        .timestamp {{ color: #999; font-size: 0.8em; text-align: center; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>Air Quality Analysis Reports</h1>
    <p>This collection contains the complete analysis pipeline for air quality data processing and visualization.</p>
    
    <ul class="report-list">
        <li>
            <a href="01_database_processing_report.html">1. Database Processing Report</a>
            <div class="description">Initial data processing and unification of multiple Excel datasets</div>
        </li>
        <li>
            <a href="02_data_imputation_report.html">2. Data Imputation Report</a>
            <div class="description">Missing data analysis and imputation methodologies</div>
        </li>
        <li>
            <a href="03_exploration_report.html">3. Data Exploration Report</a>
            <div class="description">Exploratory data analysis and dataset overview</div>
        </li>
        <li>
            <a href="04_statistical_analysis_report.html">4. Statistical Analysis Report</a>
            <div class="description">Statistical analysis and modeling of air quality data</div>
        </li>
        <li>
            <a href="05_quantitative_analysis_report.html">5. Quantitative Analysis Report</a>
            <div class="description">AQI calculation, metrics computation, and final visualizations</div>
        </li>
    </ul>
    
    <div class="timestamp">
        <p>Reports generated on: {timestamp}</p>
    </div>
</body>
</html>"""
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content.format(timestamp=timestamp))
    
    logger.info(f"✓ Created index file: {index_path}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Export Jupyter notebooks to HTML/PDF reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/export_reports.py                    # Export to HTML (default)
  python scripts/export_reports.py --format pdf       # Export to PDF only
  python scripts/export_reports.py --format both      # Export to both HTML and PDF
  python scripts/export_reports.py --verbose          # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--format', 
        choices=['html', 'pdf', 'both'], 
        default='html',
        help='Export format (default: html)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("=== Air Quality Analysis Report Export ===")
    
    # Check dependencies
    deps = check_dependencies()
    
    if not deps['nbconvert']:
        logger.error("nbconvert is required but not available. Exiting.")
        sys.exit(1)
    
    # Determine formats to export
    if args.format == 'html':
        formats = ['html']
    elif args.format == 'pdf':
        if not deps['pandoc']:
            logger.error("PDF export requested but pandoc is not available. Exiting.")
            sys.exit(1)
        formats = ['pdf']
    elif args.format == 'both':
        formats = ['html']
        if deps['pandoc']:
            formats.append('pdf')
        else:
            logger.warning("Pandoc not available. Exporting to HTML only.")
    
    # Create export directory
    create_export_directory()
    
    # Export notebooks
    logger.info(f"Exporting notebooks to: {', '.join(formats).upper()}")
    successful, total = export_all_notebooks(formats, args.verbose)
    
    # Create index for HTML exports
    if 'html' in formats:
        create_index_html()
    
    # Summary
    logger.info("=== Export Summary ===")
    logger.info(f"Successful exports: {successful}/{total}")
    
    if successful == total:
        logger.info("✓ All exports completed successfully!")
        logger.info(f"Reports available in: {EXPORTS_DIR.absolute()}")
        if 'html' in formats:
            logger.info(f"View index at: {(EXPORTS_DIR / 'index.html').absolute()}")
    else:
        logger.warning(f"Some exports failed. Check logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()