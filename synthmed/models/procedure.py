"""
Procedure model for SynthMed.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord.Procedure
"""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, validator

from synthmed.models.base import SynthmedBaseModel


class ProcedureStatus(str, Enum):
    """Status of a procedure."""
    
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class Procedure(SynthmedBaseModel):
    """
    Procedure model representing a medical procedure performed on a patient.
    """
    
    # Core attributes
    patient_id: str
    code: str  # SNOMED, CPT, HCPCS, etc.
    system: str = "http://snomed.info/sct"  # Default to SNOMED-CT
    display: str  # Procedure name
    
    # Timing
    date: date
    duration_minutes: Optional[int] = None
    
    # Clinical context
    reason_code: Optional[str] = None
    reason_display: Optional[str] = None
    encounter_id: Optional[str] = None
    provider_id: Optional[str] = None
    
    # Status
    status: ProcedureStatus = ProcedureStatus.COMPLETED
    
    # Cost information
    base_cost: float = 0.0
    payer_coverage: float = 0.0
    
    # Additional information
    body_site: Optional[str] = None
    outcome: Optional[str] = None
    
    # Complications or resulting conditions
    complications: List[str] = Field(default_factory=list)  # IDs of resulting conditions
    
    @property
    def end_date(self) -> date:
        """Calculate the end date of the procedure."""
        if not self.duration_minutes:
            return self.date
        
        # Convert duration to datetime for procedures that span multiple days
        start_datetime = datetime.combine(self.date, datetime.min.time())
        end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
        return end_datetime.date()
    
    @property
    def patient_cost(self) -> float:
        """Calculate the cost to the patient."""
        return max(0, self.base_cost - self.payer_coverage)
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the procedure to a FHIR Procedure resource."""
        # Map procedure status to FHIR status
        status_map = {
            ProcedureStatus.PREPARATION: "preparation",
            ProcedureStatus.IN_PROGRESS: "in-progress",
            ProcedureStatus.COMPLETED: "completed",
            ProcedureStatus.ENTERED_IN_ERROR: "entered-in-error",
            ProcedureStatus.STOPPED: "stopped",
            ProcedureStatus.UNKNOWN: "unknown",
        }
        
        # Calculate start and end time if duration is provided
        start_datetime = datetime.combine(self.date, datetime.min.time())
        performed_period = None
        
        if self.duration_minutes:
            end_datetime = start_datetime + timedelta(minutes=self.duration_minutes)
            performed_period = {
                "start": start_datetime.isoformat(),
                "end": end_datetime.isoformat()
            }
        
        fhir_procedure = {
            "resourceType": "Procedure",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure"
                ]
            },
            "status": status_map.get(self.status, "completed"),
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
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            }
        }
        
        # Add performed information
        if performed_period:
            fhir_procedure["performedPeriod"] = performed_period
        else:
            fhir_procedure["performedDateTime"] = start_datetime.isoformat()
        
        # Add encounter if available
        if self.encounter_id:
            fhir_procedure["encounter"] = {
                "reference": f"Encounter/{self.encounter_id}"
            }
        
        # Add performer if available
        if self.provider_id:
            fhir_procedure["performer"] = [
                {
                    "actor": {
                        "reference": f"Practitioner/{self.provider_id}"
                    }
                }
            ]
        
        # Add reason if available
        if self.reason_code and self.reason_display:
            fhir_procedure["reasonCode"] = [
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
        
        # Add body site if available
        if self.body_site:
            fhir_procedure["bodySite"] = [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "display": self.body_site
                        }
                    ],
                    "text": self.body_site
                }
            ]
        
        # Add outcome if available
        if self.outcome:
            fhir_procedure["outcome"] = {
                "text": self.outcome
            }
            
        # Add complication information
        if self.complications:
            fhir_procedure["complication"] = [
                {
                    "reference": f"Condition/{complication_id}"
                }
                for complication_id in self.complications
            ]
            
        return fhir_procedure
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the procedure to a CSV record."""
        return {
            "DATE": self.date.isoformat(),
            "PATIENT": self.patient_id,
            "ENCOUNTER": self.encounter_id or "",
            "CODE": self.code,
            "DESCRIPTION": self.display,
            "BASE_COST": self.base_cost,
            "PAYER_COVERAGE": self.payer_coverage,
            "REASON_CODE": self.reason_code or "",
            "REASON_DESCRIPTION": self.reason_display or ""
        } 