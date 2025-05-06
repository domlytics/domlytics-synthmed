"""
Exporters for SynthMed generated data.

This module provides exporters for different output formats.
"""

from typing import List, Optional, Type

from synthmed.exporters.base import BaseExporter
from synthmed.exporters.csv_exporter import CSVExporter
from synthmed.exporters.fhir_exporter import FHIRExporter
from synthmed.exporters.json_exporter import JSONExporter


def exporter_factory(output_format: str, output_dir: str) -> BaseExporter:
    """
    Create an exporter instance for the specified output format.
    
    Args:
        output_format: Format to export ("fhir", "json", or "csv")
        output_dir: Directory to write output files
        
    Returns:
        Instance of the appropriate exporter
        
    Raises:
        ValueError: If the output format is not supported
    """
    output_format = output_format.lower()
    
    if output_format == "fhir":
        return FHIRExporter(output_dir)
    elif output_format == "json":
        return JSONExporter(output_dir)
    elif output_format == "csv":
        return CSVExporter(output_dir)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


__all__ = [
    "BaseExporter",
    "CSVExporter",
    "FHIRExporter",
    "JSONExporter",
    "exporter_factory",
] 