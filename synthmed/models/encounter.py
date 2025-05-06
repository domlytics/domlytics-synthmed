"""
Encounter model for SynthMed.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord.Encounter
"""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator

from synthmed.models.base import SynthmedBaseModel


class EncounterType(str, Enum):
    """Type of healthcare encounter."""
    
    AMBULATORY = "ambulatory"
    EMERGENCY = "emergency"
    INPATIENT = "inpatient"
    WELLNESS = "wellness"
    URGENTCARE = "urgentcare"
    VIRTUAL = "virtual"


class EncounterStatus(str, Enum):
    """Status of the encounter."""
    
    PLANNED = "planned"
    ARRIVED = "arrived"
    IN_PROGRESS = "in-progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Encounter(SynthmedBaseModel):
    """
    Encounter model representing a healthcare encounter between a patient and provider.
    """
    
    # Core attributes
    patient_id: str
    provider_id: Optional[str] = None
    provider_organization_id: Optional[str] = None
    
    # Encounter details
    encounter_type: EncounterType
    class_code: str  # SNOMED, CPT, etc.
    class_display: str
    reason_code: Optional[str] = None
    reason_display: Optional[str] = None
    
    # Timing
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Status
    status: EncounterStatus = EncounterStatus.FINISHED
    
    # Clinical components
    diagnoses: List[str] = Field(default_factory=list)  # IDs of conditions
    procedures: List[str] = Field(default_factory=list)  # IDs of procedures
    medications: List[str] = Field(default_factory=list)  # IDs of medications
    observations: List[str] = Field(default_factory=list)  # IDs of observations
    
    # Cost information
    base_cost: float = 0.0
    total_claim_cost: float = 0.0
    payer_coverage: float = 0.0
    copay: float = 0.0
    
    # Location information
    facility_id: Optional[str] = None
    
    @field_validator("end_date", mode="before")
    @classmethod
    def set_end_date(cls, end_date, info):
        """Set default end date based on encounter type if not provided."""
        if end_date:
            return end_date
            
        data = info.data
        start_date = data.get("start_date")
        encounter_type = data.get("encounter_type")
        
        if not start_date:
            return None
            
        # Default durations based on encounter type
        durations = {
            EncounterType.AMBULATORY: timedelta(hours=1),
            EncounterType.EMERGENCY: timedelta(hours=4),
            EncounterType.INPATIENT: timedelta(days=3),
            EncounterType.WELLNESS: timedelta(hours=1),
            EncounterType.URGENTCARE: timedelta(hours=2),
            EncounterType.VIRTUAL: timedelta(minutes=30),
        }
        
        duration = durations.get(encounter_type, timedelta(hours=1))
        return start_date + duration
    
    @property
    def duration_minutes(self) -> float:
        """Calculate the duration of the encounter in minutes."""
        if not self.end_date:
            return 0
        return (self.end_date - self.start_date).total_seconds() / 60
    
    @property
    def patient_cost(self) -> float:
        """Calculate the cost to the patient."""
        return self.total_claim_cost - self.payer_coverage
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the encounter to a FHIR Encounter resource."""
        # Map encounter type to FHIR codes
        encounter_class_map = {
            EncounterType.AMBULATORY: "AMB",
            EncounterType.EMERGENCY: "EMER",
            EncounterType.INPATIENT: "IMP",
            EncounterType.WELLNESS: "AMB",
            EncounterType.URGENTCARE: "AMB",
            EncounterType.VIRTUAL: "VR",
        }
        
        # Map encounter status to FHIR status
        status_map = {
            EncounterStatus.PLANNED: "planned",
            EncounterStatus.ARRIVED: "arrived",
            EncounterStatus.IN_PROGRESS: "in-progress",
            EncounterStatus.FINISHED: "finished",
            EncounterStatus.CANCELLED: "cancelled",
        }
        
        fhir_encounter = {
            "resourceType": "Encounter",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"
                ]
            },
            "status": status_map.get(self.status, "finished"),
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": encounter_class_map.get(self.encounter_type, "AMB"),
                "display": self.encounter_type.value.capitalize()
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": self.class_code,
                            "display": self.class_display
                        }
                    ],
                    "text": self.class_display
                }
            ],
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat() if self.end_date else None
            }
        }
        
        # Add provider if available
        if self.provider_id:
            fhir_encounter["participant"] = [
                {
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                    "code": "PPRF",
                                    "display": "primary performer"
                                }
                            ]
                        }
                    ],
                    "individual": {
                        "reference": f"Practitioner/{self.provider_id}"
                    }
                }
            ]
        
        # Add organization if available
        if self.provider_organization_id:
            fhir_encounter["serviceProvider"] = {
                "reference": f"Organization/{self.provider_organization_id}"
            }
        
        # Add reason if available
        if self.reason_code and self.reason_display:
            fhir_encounter["reasonCode"] = [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": self.reason_code,
                            "display": self.reason_display
                        }
                    ],
                    "text": self.reason_display
                }
            ]
        
        # Add diagnoses
        if self.diagnoses:
            fhir_encounter["diagnosis"] = [
                {
                    "condition": {
                        "reference": f"Condition/{diagnosis_id}"
                    },
                    "use": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                                "code": "AD",
                                "display": "Admission diagnosis"
                            }
                        ]
                    },
                    "rank": i + 1
                }
                for i, diagnosis_id in enumerate(self.diagnoses)
            ]
        
        # Add location if available
        if self.facility_id:
            fhir_encounter["location"] = [
                {
                    "location": {
                        "reference": f"Location/{self.facility_id}"
                    }
                }
            ]
            
        return fhir_encounter
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the encounter to a CSV record."""
        return {
            "Id": self.id,
            "START": self.start_date.isoformat(),
            "STOP": self.end_date.isoformat() if self.end_date else "",
            "PATIENT": self.patient_id,
            "PROVIDER": self.provider_id or "",
            "ORGANIZATION": self.provider_organization_id or "",
            "CODE": self.class_code,
            "DESCRIPTION": self.class_display,
            "BASE_ENCOUNTER_COST": self.base_cost,
            "TOTAL_CLAIM_COST": self.total_claim_cost,
            "PAYER_COVERAGE": self.payer_coverage,
            "REASON_CODE": self.reason_code or "",
            "REASON_DESCRIPTION": self.reason_display or ""
        } 