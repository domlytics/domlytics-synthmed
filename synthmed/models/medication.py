"""
Medication model for SynthMed.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord.Medication
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from synthmed.models.base import SynthmedBaseModel


class MedicationStatus(str, Enum):
    """Status of a medication."""
    
    ACTIVE = "active"
    STOPPED = "stopped"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    INTENDED = "intended"


class MedicationRequest(SynthmedBaseModel):
    """
    Medication model representing a medication prescribed to a patient.
    """
    
    # Core attributes
    patient_id: str
    code: str  # RxNorm code
    display: str  # Medication name
    
    # Timing
    start_date: date
    end_date: Optional[date] = None
    
    # Dosage information
    dosage: Optional[str] = None
    dosage_amount: Optional[float] = None
    dosage_frequency: Optional[str] = None
    dosage_period: Optional[str] = None
    route: Optional[str] = None  # e.g., "oral", "intravenous"
    
    # Clinical context
    reason_code: Optional[str] = None
    reason_display: Optional[str] = None
    encounter_id: Optional[str] = None
    provider_id: Optional[str] = None
    
    # Status
    status: MedicationStatus = MedicationStatus.ACTIVE
    
    # Financial
    dispenses: int = 0
    refills: Optional[int] = None
    basecost: float = 0.0  # Per unit cost
    payer_coverage: float = 0.0
    
    @property
    def is_active(self) -> bool:
        """Check if the medication is currently active."""
        return (self.status == MedicationStatus.ACTIVE and 
                (self.end_date is None or self.end_date >= date.today()))
    
    @property
    def duration_days(self) -> int:
        """Calculate the duration of the medication in days."""
        if self.end_date is None:
            return 0
        return (self.end_date - self.start_date).days
    
    @property
    def total_cost(self) -> float:
        """Calculate the total cost of the medication."""
        return self.basecost * self.dispenses
    
    @property
    def patient_cost(self) -> float:
        """Calculate the cost to the patient."""
        return self.total_cost - self.payer_coverage
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the medication to a FHIR MedicationRequest resource."""
        end_date_str = self.end_date.isoformat() if self.end_date else None
        
        # Map medication status to FHIR status
        status_map = {
            MedicationStatus.ACTIVE: "active",
            MedicationStatus.STOPPED: "stopped",
            MedicationStatus.CANCELLED: "cancelled",
            MedicationStatus.COMPLETED: "completed",
            MedicationStatus.ENTERED_IN_ERROR: "entered-in-error",
            MedicationStatus.INTENDED: "intended",
        }
        
        fhir_med_request = {
            "resourceType": "MedicationRequest",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"
                ]
            },
            "status": status_map.get(self.status, "active"),
            "intent": "order",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": self.code,
                        "display": self.display
                    }
                ],
                "text": self.display
            },
            "subject": {
                "reference": f"Patient/{self.patient_id}"
            },
            "authoredOn": datetime.combine(self.start_date, datetime.min.time()).isoformat()
        }
        
        # Add encounter if available
        if self.encounter_id:
            fhir_med_request["encounter"] = {
                "reference": f"Encounter/{self.encounter_id}"
            }
        
        # Add provider if available
        if self.provider_id:
            fhir_med_request["requester"] = {
                "reference": f"Practitioner/{self.provider_id}"
            }
        
        # Add dosage instructions if available
        if any([self.dosage, self.dosage_amount, self.dosage_frequency, self.route]):
            dosage_instruction = {
                "text": self.dosage or f"{self.dosage_amount or ''} {self.dosage_frequency or ''} {self.route or ''}".strip()
            }
            
            if self.dosage_amount:
                dosage_instruction["doseAndRate"] = [
                    {
                        "doseQuantity": {
                            "value": self.dosage_amount,
                            "unit": "mg",
                            "system": "http://unitsofmeasure.org",
                            "code": "mg"
                        }
                    }
                ]
                
            if self.route:
                dosage_instruction["route"] = {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "26643006",  # Just an example code for oral route
                            "display": self.route.capitalize()
                        }
                    ],
                    "text": self.route.capitalize()
                }
                
            fhir_med_request["dosageInstruction"] = [dosage_instruction]
        
        # Add reason if available
        if self.reason_code and self.reason_display:
            fhir_med_request["reasonCode"] = [
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
            
        # Add dispense request if refills are specified
        if self.refills is not None:
            fhir_med_request["dispenseRequest"] = {
                "numberOfRepeatsAllowed": self.refills
            }
            
        return fhir_med_request
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the medication to a CSV record."""
        return {
            "START": self.start_date.isoformat(),
            "STOP": self.end_date.isoformat() if self.end_date else "",
            "PATIENT": self.patient_id,
            "ENCOUNTER": self.encounter_id or "",
            "CODE": self.code,
            "DESCRIPTION": self.display,
            "DISPENSES": self.dispenses,
            "BASECOST": self.basecost,
            "PAYER_COVERAGE": self.payer_coverage,
            "REASON_CODE": self.reason_code or "",
            "REASON_DESCRIPTION": self.reason_display or ""
        } 