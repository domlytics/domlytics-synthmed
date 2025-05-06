"""
JSON exporter for SynthMed generated data.

Exports patient data to JSON files.
"""

import json
import logging
import os
from datetime import date, datetime
from typing import Dict, List, Any

from synthmed.exporters.base import BaseExporter
from synthmed.models import Patient

logger = logging.getLogger("synthmed.exporters.json")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class JSONExporter(BaseExporter):
    """
    Exporter for JSON format.
    
    This exporter creates JSON files for patient data, either as individual
    files per patient or as collections of records.
    """
    
    def export(self, patients: List[Patient]) -> None:
        """
        Export patient data to JSON files.
        
        Args:
            patients: List of patients to export
        """
        logger.info(f"Exporting {len(patients)} patients to JSON format")
        
        # Export all patients to a single file
        self._export_patients_collection(patients)
        
        # Export individual patient files
        if len(patients) <= 1000:  # Only for reasonable number of patients
            self._export_individual_patients(patients)
        
        logger.info(f"JSON export complete")
    
    def _export_patients_collection(self, patients: List[Patient]) -> None:
        """
        Export all patients to a single JSON file.
        
        Args:
            patients: List of patients to export
        """
        filepath = self.get_output_path("patients.json")
        logger.debug(f"Exporting all patients to {filepath}")
        
        # Convert patients to dictionaries
        patient_dicts = [patient.to_dict() for patient in patients]
        
        with open(filepath, "w") as f:
            json.dump(patient_dicts, f, indent=2, cls=DateTimeEncoder)
    
    def _export_individual_patients(self, patients: List[Patient]) -> None:
        """
        Export each patient to an individual JSON file.
        
        Args:
            patients: List of patients to export
        """
        # Create a directory for individual patient files
        patient_dir = os.path.join(self.output_dir, "patients")
        os.makedirs(patient_dir, exist_ok=True)
        
        logger.debug(f"Exporting individual patient files to {patient_dir}")
        
        for patient in patients:
            # Convert patient to dictionary
            patient_dict = patient.to_dict()
            
            # Define file path
            filepath = os.path.join(patient_dir, f"{patient.id}.json")
            
            # Write to file
            with open(filepath, "w") as f:
                json.dump(patient_dict, f, indent=2, cls=DateTimeEncoder)
    
    def export_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Export metadata about the generation run.
        
        Args:
            metadata: Dictionary of metadata to export
        """
        filepath = self.get_output_path("metadata.json")
        logger.debug(f"Exporting metadata to {filepath}")
        
        # Add timestamp
        metadata["export_time"] = datetime.now().isoformat()
        
        with open(filepath, "w") as f:
            json.dump(metadata, f, indent=2, cls=DateTimeEncoder) 