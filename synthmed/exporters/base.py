"""
Base exporter for SynthMed generated data.

This module defines the base class that all data exporters must inherit from.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any

from synthmed.models import Patient

logger = logging.getLogger("synthmed.exporters")


class BaseExporter(ABC):
    """
    Base class for all data exporters.
    
    This abstract class defines the interface that all exporters must implement.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the exporter.
        
        Args:
            output_dir: Directory where output files will be written
        """
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    @abstractmethod
    def export(self, patients: List[Patient]) -> None:
        """
        Export patient data to the configured format.
        
        Args:
            patients: List of patients to export
        """
        pass
    
    def get_output_path(self, filename: str) -> str:
        """
        Get the full path for an output file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Full path to the output file
        """
        return os.path.join(self.output_dir, filename)
    
    def export_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Export metadata about the generation run.
        
        Args:
            metadata: Dictionary of metadata to export
        """
        # Default implementation - subclasses may override
        pass 