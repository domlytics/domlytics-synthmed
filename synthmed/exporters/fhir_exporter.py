"""
FHIR exporter for SynthMed generated data.

Based on org.synthetichealth.synthea.export.FhirR4Exporter
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Set

from synthmed.exporters.base import BaseExporter
from synthmed.models import Patient

logger = logging.getLogger("synthmed.exporters.fhir")


class FHIRExporter(BaseExporter):
    """
    Exporter for FHIR R4 format.
    
    This exporter creates FHIR R4 bundles for patient data.
    """
    
    def export(self, patients: List[Patient]) -> None:
        """
        Export patient data to FHIR bundles.
        
        Args:
            patients: List of patients to export
        """
        logger.info(f"Exporting {len(patients)} patients to FHIR R4 format")
        
        # Export each patient to a separate FHIR bundle
        for patient in patients:
            self._export_patient_bundle(patient)
            
        # Export all patients to a single bundle
        self._export_all_patients_bundle(patients)
        
        logger.info(f"FHIR export complete")
    
    def _export_patient_bundle(self, patient: Patient) -> None:
        """
        Export a patient to a FHIR bundle.
        
        Args:
            patient: Patient to export
        """
        bundle = self._create_bundle(patient)
        
        # Define file path
        filepath = self.get_output_path(f"{patient.id}.fhir.json")
        
        # Write to file
        with open(filepath, "w") as f:
            json.dump(bundle, f, indent=2)
            
    def _export_all_patients_bundle(self, patients: List[Patient]) -> None:
        """
        Export all patients to a single FHIR bundle.
        
        Args:
            patients: List of patients to export
        """
        # Create bundle structure
        bundle = {
            "resourceType": "Bundle",
            "id": "patient-bundle",
            "type": "collection",
            "meta": {
                "lastUpdated": datetime.now().isoformat()
            },
            "entry": []
        }
        
        # Add all patients to the bundle
        for patient in patients:
            patient_resource = patient.to_fhir()
            bundle["entry"].append({
                "fullUrl": f"urn:uuid:{patient.id}",
                "resource": patient_resource
            })
        
        # Define file path
        filepath = self.get_output_path("patients.fhir.json")
        
        # Write to file
        with open(filepath, "w") as f:
            json.dump(bundle, f, indent=2)
    
    def _create_bundle(self, patient: Patient) -> Dict[str, Any]:
        """
        Create a FHIR bundle for a patient.
        
        Args:
            patient: Patient to include in the bundle
            
        Returns:
            Dictionary representing a FHIR bundle
        """
        # Create bundle structure
        bundle = {
            "resourceType": "Bundle",
            "id": f"bundle-{patient.id}",
            "type": "collection",
            "meta": {
                "lastUpdated": datetime.now().isoformat()
            },
            "entry": []
        }
        
        # Add patient resource
        patient_resource = patient.to_fhir()
        bundle["entry"].append({
            "fullUrl": f"urn:uuid:{patient.id}",
            "resource": patient_resource
        })
        
        # In a complete implementation, we would also add:
        # - Conditions
        # - Encounters
        # - Medications
        # - Procedures
        # - Observations
        # But for this simplified version, we'll just include the patient
        
        return bundle
    
    def export_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Export metadata about the generation run.
        
        Args:
            metadata: Dictionary of metadata to export
        """
        # Create a Parameters resource
        parameters = {
            "resourceType": "Parameters",
            "id": "generation-metadata",
            "parameter": []
        }
        
        # Add parameters
        for key, value in metadata.items():
            param = {"name": key}
            
            # Determine value type
            if isinstance(value, bool):
                param["valueBoolean"] = value
            elif isinstance(value, int):
                param["valueInteger"] = value
            elif isinstance(value, float):
                param["valueDecimal"] = value
            elif isinstance(value, str):
                param["valueString"] = value
            elif isinstance(value, datetime):
                param["valueDateTime"] = value.isoformat()
            else:
                # Convert to string for other types
                param["valueString"] = str(value)
                
            parameters["parameter"].append(param)
            
        # Add timestamp
        parameters["parameter"].append({
            "name": "export_time",
            "valueDateTime": datetime.now().isoformat()
        })
        
        # Write to file
        filepath = self.get_output_path("metadata.fhir.json")
        with open(filepath, "w") as f:
            json.dump(parameters, f, indent=2) 