"""
CSV exporter for SynthMed generated data.

Based on org.synthetichealth.synthea.export.CSVExporter
"""

import csv
import logging
import os
from collections import defaultdict
from typing import Dict, List, Any, Set

from synthmed.exporters.base import BaseExporter
from synthmed.models import Patient, Condition, Encounter, MedicationRequest, Procedure, Observation

logger = logging.getLogger("synthmed.exporters.csv")


class CSVExporter(BaseExporter):
    """
    Exporter for CSV format.
    
    This exporter creates separate CSV files for patients, encounters, conditions,
    medications, procedures, and observations.
    """
    
    def export(self, patients: List[Patient]) -> None:
        """
        Export patient data to CSV files.
        
        Args:
            patients: List of patients to export
        """
        logger.info(f"Exporting {len(patients)} patients to CSV format")
        
        # Export patients
        self._export_patients(patients)
        
        # Gather all other entities
        conditions: List[Dict] = []
        encounters: List[Dict] = []
        medications: List[Dict] = []
        procedures: List[Dict] = []
        observations: List[Dict] = []
        
        for patient in patients:
            # Here we'd collect the actual records from the patient
            # For now, we're just creating empty lists as a placeholder
            # In a full implementation, the patient model would have methods to
            # retrieve these records
            pass
        
        # Export other entities
        self._export_conditions(conditions)
        self._export_encounters(encounters)
        self._export_medications(medications)
        self._export_procedures(procedures)
        self._export_observations(observations)
        
        logger.info(f"CSV export complete")
    
    def _export_patients(self, patients: List[Patient]) -> None:
        """
        Export patients to CSV.
        
        Args:
            patients: List of patients to export
        """
        filepath = self.get_output_path("patients.csv")
        logger.debug(f"Exporting patients to {filepath}")
        
        # Get all fields from the first patient to determine headers
        if not patients:
            logger.warning("No patients to export")
            return
            
        # Extract patient records
        patient_records = [patient.to_csv_record() for patient in patients]
        
        # Get all possible field names
        fieldnames = set()
        for record in patient_records:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(patient_records)
    
    def _export_conditions(self, conditions: List[Dict]) -> None:
        """
        Export conditions to CSV.
        
        Args:
            conditions: List of condition records to export
        """
        filepath = self.get_output_path("conditions.csv")
        logger.debug(f"Exporting conditions to {filepath}")
        
        if not conditions:
            logger.debug("No conditions to export")
            return
            
        # Get all possible field names
        fieldnames = set()
        for record in conditions:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(conditions)
    
    def _export_encounters(self, encounters: List[Dict]) -> None:
        """
        Export encounters to CSV.
        
        Args:
            encounters: List of encounter records to export
        """
        filepath = self.get_output_path("encounters.csv")
        logger.debug(f"Exporting encounters to {filepath}")
        
        if not encounters:
            logger.debug("No encounters to export")
            return
            
        # Get all possible field names
        fieldnames = set()
        for record in encounters:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(encounters)
    
    def _export_medications(self, medications: List[Dict]) -> None:
        """
        Export medications to CSV.
        
        Args:
            medications: List of medication records to export
        """
        filepath = self.get_output_path("medications.csv")
        logger.debug(f"Exporting medications to {filepath}")
        
        if not medications:
            logger.debug("No medications to export")
            return
            
        # Get all possible field names
        fieldnames = set()
        for record in medications:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(medications)
    
    def _export_procedures(self, procedures: List[Dict]) -> None:
        """
        Export procedures to CSV.
        
        Args:
            procedures: List of procedure records to export
        """
        filepath = self.get_output_path("procedures.csv")
        logger.debug(f"Exporting procedures to {filepath}")
        
        if not procedures:
            logger.debug("No procedures to export")
            return
            
        # Get all possible field names
        fieldnames = set()
        for record in procedures:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(procedures)
    
    def _export_observations(self, observations: List[Dict]) -> None:
        """
        Export observations to CSV.
        
        Args:
            observations: List of observation records to export
        """
        filepath = self.get_output_path("observations.csv")
        logger.debug(f"Exporting observations to {filepath}")
        
        if not observations:
            logger.debug("No observations to export")
            return
            
        # Get all possible field names
        fieldnames = set()
        for record in observations:
            fieldnames.update(record.keys())
        
        # Convert to a sorted list
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(observations) 