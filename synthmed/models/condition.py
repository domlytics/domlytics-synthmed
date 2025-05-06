"""
Condition model for SynthMed.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord.Condition
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field

from synthmed.models.base import SynthmedBaseModel


class ConditionStatus(str, Enum):
    """Status of a medical condition."""
    
    ACTIVE = "active"
    RESOLVED = "resolved"
    RECURRENCE = "recurrence"
    INACTIVE = "inactive"
    REMISSION = "remission"


class Condition(SynthmedBaseModel):
    """
    Condition model representing a patient's health condition or diagnosis.
    """
    
    # Core attributes
    patient_id: str
    code: str  # SNOMED-CT, ICD-10, etc.
    system: str = "http://snomed.info/sct"  # Default to SNOMED-CT
    display: str  # Human readable description
    
    # Timing
    onset_date: date
    abatement_date: Optional[date] = None
    
    # Clinical
    status: ConditionStatus = ConditionStatus.ACTIVE
    encounter_id: Optional[str] = None  # ID of the encounter where this was diagnosed
    provider_id: Optional[str] = None   # ID of the provider who diagnosed
    
    # Additional information
    category: Optional[str] = None  # e.g. "problem-list-item"
    severity: Optional[str] = None  # e.g. "mild", "moderate", "severe"
    
    @property
    def is_active(self) -> bool:
        """Check if the condition is currently active."""
        return (self.status == ConditionStatus.ACTIVE and 
                (self.abatement_date is None or self.abatement_date >= date.today()))
    
    @property
    def duration_days(self) -> int:
        """Calculate the duration of the condition in days."""
        end_date = self.abatement_date if self.abatement_date else date.today()
        return (end_date - self.onset_date).days
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the condition to a FHIR Condition resource."""
        abatement_date_str = self.abatement_date.isoformat() if self.abatement_date else None
        
        # Map condition status to FHIR clinical status
        clinical_status_map = {
            ConditionStatus.ACTIVE: "active",
            ConditionStatus.RESOLVED: "resolved",
            ConditionStatus.RECURRENCE: "active",
            ConditionStatus.INACTIVE: "inactive",
            ConditionStatus.REMISSION: "remission",
        }
        
        fhir_condition = {
            "resourceType": "Condition",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"
                ]
            },
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "code": {
                "coding": [
                    {
                        "system": self.system,
                        "code": self.code,
                        "display": self.display
                    }
                ],
                "text": self.display
            },
            "onsetDateTime": datetime.combine(self.onset_date, datetime.min.time()).isoformat(),
            "recordedDate": self.created_at.isoformat(),
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": clinical_status_map.get(self.status, "active")
                    }
                ]
            }
        }
        
        # Only include if the condition has resolved
        if abatement_date_str:
            fhir_condition["abatementDateTime"] = abatement_date_str
        
        # Add encounter if available
        if self.encounter_id:
            fhir_condition["encounter"] = {
                "reference": f"Encounter/{self.encounter_id}"
            }
        
        # Add provider if available
        if self.provider_id:
            fhir_condition["asserter"] = {
                "reference": f"Practitioner/{self.provider_id}"
            }
        
        # Add category if available
        if self.category:
            fhir_condition["category"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": self.category
                        }
                    ]
                }
            ]
        
        # Add severity if available
        if self.severity:
            fhir_condition["severity"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-severity",
                        "code": self.severity.lower(),
                        "display": self.severity.capitalize()
                    }
                ],
                "text": self.severity.capitalize()
            }
        
        return fhir_condition
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the condition to a CSV record."""
        return {
            "START": self.onset_date.isoformat(),
            "STOP": self.abatement_date.isoformat() if self.abatement_date else "",
            "PATIENT": self.patient_id,
            "ENCOUNTER": self.encounter_id or "",
            "CODE": self.code,
            "DESCRIPTION": self.display,
            "STATUS": self.status.value
        } 