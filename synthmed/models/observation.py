"""
Observation model for SynthMed.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord.Observation
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator

from synthmed.models.base import SynthmedBaseModel


class ObservationStatus(str, Enum):
    """Status of an observation."""
    
    REGISTERED = "registered"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    AMENDED = "amended"
    CORRECTED = "corrected"
    CANCELLED = "cancelled"
    ENTERED_IN_ERROR = "entered-in-error"
    UNKNOWN = "unknown"


class ObservationType(str, Enum):
    """Type of observation value."""
    
    NUMERIC = "numeric"
    TEXT = "text"
    CODE = "code"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    QUANTITY = "quantity"


class Observation(SynthmedBaseModel):
    """
    Observation model representing a clinical observation or measurement.
    """
    
    # Core attributes
    patient_id: str
    code: str  # LOINC, SNOMED, etc.
    system: str = "http://loinc.org"  # Default to LOINC
    display: str  # Human readable description
    
    # Observation value - could be one of multiple types
    value_type: ObservationType
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_code: Optional[str] = None
    value_boolean: Optional[bool] = None
    value_datetime: Optional[datetime] = None
    
    # Units for numeric values
    unit: Optional[str] = None
    unit_code: Optional[str] = None
    
    # Reference ranges (for numeric values)
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    
    # Timing
    effective_date: datetime
    
    # Clinical context
    category: Optional[str] = None  # e.g., "vital-signs", "laboratory"
    encounter_id: Optional[str] = None
    provider_id: Optional[str] = None
    
    # Status
    status: ObservationStatus = ObservationStatus.FINAL
    
    # Component observations (for panels)
    components: List[Dict[str, Any]] = Field(default_factory=list)
    
    @field_validator("value_numeric", "value_text", "value_code", "value_boolean", "value_datetime", mode="after")
    @classmethod
    def validate_value_type(cls, v, info):
        """Validate that the value matches the specified value_type."""
        data = info.data
        value_type = data.get("value_type")
        if not value_type:
            return v
            
        value_field_map = {
            ObservationType.NUMERIC: "value_numeric",
            ObservationType.TEXT: "value_text",
            ObservationType.CODE: "value_code",
            ObservationType.BOOLEAN: "value_boolean",
            ObservationType.DATETIME: "value_datetime",
            ObservationType.QUANTITY: "value_numeric",  # Quantity uses numeric value with units
        }
        
        field_name = value_field_map.get(value_type)
        field_being_validated = info.field_name
        
        if field_name == field_being_validated:
            # If we're validating the field that should have a value, make sure it has one
            if v is None:
                raise ValueError(f"Expected a value for {field_name} when value_type is {value_type}")
                
        return v
    
    @property
    def value(self) -> Any:
        """Get the observation value based on its type."""
        value_map = {
            ObservationType.NUMERIC: self.value_numeric,
            ObservationType.TEXT: self.value_text,
            ObservationType.CODE: self.value_code,
            ObservationType.BOOLEAN: self.value_boolean,
            ObservationType.DATETIME: self.value_datetime,
            ObservationType.QUANTITY: self.value_numeric,
        }
        return value_map.get(self.value_type)
    
    @property
    def formatted_value(self) -> str:
        """Get a formatted string representation of the value."""
        if self.value_type == ObservationType.NUMERIC or self.value_type == ObservationType.QUANTITY:
            if self.unit:
                return f"{self.value_numeric} {self.unit}"
            return str(self.value_numeric)
        elif self.value_type == ObservationType.BOOLEAN:
            return "true" if self.value_boolean else "false"
        elif self.value_type == ObservationType.DATETIME:
            return self.value_datetime.isoformat() if self.value_datetime else ""
        else:
            return str(self.value or "")
    
    @property
    def is_abnormal(self) -> bool:
        """Check if the observation value is outside reference range."""
        if self.value_type != ObservationType.NUMERIC or self.value_numeric is None:
            return False
            
        if self.reference_low is not None and self.value_numeric < self.reference_low:
            return True
            
        if self.reference_high is not None and self.value_numeric > self.reference_high:
            return True
            
        return False
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the observation to a FHIR Observation resource."""
        # Map observation status to FHIR status
        status_map = {
            ObservationStatus.REGISTERED: "registered",
            ObservationStatus.PRELIMINARY: "preliminary",
            ObservationStatus.FINAL: "final",
            ObservationStatus.AMENDED: "amended",
            ObservationStatus.CORRECTED: "corrected",
            ObservationStatus.CANCELLED: "cancelled",
            ObservationStatus.ENTERED_IN_ERROR: "entered-in-error",
            ObservationStatus.UNKNOWN: "unknown",
        }
        
        fhir_observation = {
            "resourceType": "Observation",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"
                ]
            },
            "status": status_map.get(self.status, "final"),
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
            },
            "effectiveDateTime": self.effective_date.isoformat()
        }
        
        # Add category if available
        if self.category:
            fhir_observation["category"] = [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": self.category,
                            "display": self.category.capitalize()
                        }
                    ]
                }
            ]
        
        # Add value based on type
        if self.value_type == ObservationType.NUMERIC:
            fhir_observation["valueQuantity"] = {
                "value": self.value_numeric,
                "unit": self.unit or "",
                "system": "http://unitsofmeasure.org",
                "code": self.unit_code or self.unit or ""
            }
        elif self.value_type == ObservationType.QUANTITY:
            fhir_observation["valueQuantity"] = {
                "value": self.value_numeric,
                "unit": self.unit or "",
                "system": "http://unitsofmeasure.org",
                "code": self.unit_code or self.unit or ""
            }
        elif self.value_type == ObservationType.TEXT:
            fhir_observation["valueString"] = self.value_text
        elif self.value_type == ObservationType.CODE:
            fhir_observation["valueCodeableConcept"] = {
                "coding": [
                    {
                        "code": self.value_code,
                        "display": self.value_text or self.value_code
                    }
                ]
            }
        elif self.value_type == ObservationType.BOOLEAN:
            fhir_observation["valueBoolean"] = self.value_boolean
        elif self.value_type == ObservationType.DATETIME:
            if self.value_datetime:
                fhir_observation["valueDateTime"] = self.value_datetime.isoformat()
        
        # Add reference range if available
        if self.reference_low is not None or self.reference_high is not None:
            reference_range = {}
            
            if self.reference_low is not None:
                reference_range["low"] = {
                    "value": self.reference_low,
                    "unit": self.unit or "",
                    "system": "http://unitsofmeasure.org",
                    "code": self.unit_code or self.unit or ""
                }
                
            if self.reference_high is not None:
                reference_range["high"] = {
                    "value": self.reference_high,
                    "unit": self.unit or "",
                    "system": "http://unitsofmeasure.org",
                    "code": self.unit_code or self.unit or ""
                }
                
            fhir_observation["referenceRange"] = [reference_range]
        
        # Add encounter if available
        if self.encounter_id:
            fhir_observation["encounter"] = {
                "reference": f"Encounter/{self.encounter_id}"
            }
        
        # Add performer if available
        if self.provider_id:
            fhir_observation["performer"] = [
                {
                    "reference": f"Practitioner/{self.provider_id}"
                }
            ]
        
        # Add components for panels
        if self.components:
            fhir_components = []
            
            for component in self.components:
                fhir_component = {
                    "code": {
                        "coding": [
                            {
                                "system": component.get("system", "http://loinc.org"),
                                "code": component.get("code", ""),
                                "display": component.get("display", "")
                            }
                        ],
                        "text": component.get("display", "")
                    }
                }
                
                # Add value based on component type
                value_type = component.get("value_type")
                
                if value_type == "numeric" or value_type == "quantity":
                    fhir_component["valueQuantity"] = {
                        "value": component.get("value_numeric"),
                        "unit": component.get("unit", ""),
                        "system": "http://unitsofmeasure.org",
                        "code": component.get("unit_code", component.get("unit", ""))
                    }
                elif value_type == "text":
                    fhir_component["valueString"] = component.get("value_text", "")
                elif value_type == "code":
                    fhir_component["valueCodeableConcept"] = {
                        "coding": [
                            {
                                "code": component.get("value_code", ""),
                                "display": component.get("value_text", component.get("value_code", ""))
                            }
                        ]
                    }
                
                fhir_components.append(fhir_component)
            
            if fhir_components:
                fhir_observation["component"] = fhir_components
        
        return fhir_observation
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the observation to a CSV record."""
        return {
            "DATE": self.effective_date.isoformat(),
            "PATIENT": self.patient_id,
            "ENCOUNTER": self.encounter_id or "",
            "CODE": self.code,
            "DESCRIPTION": self.display,
            "VALUE": self.formatted_value,
            "UNITS": self.unit or "",
            "TYPE": self.value_type.value
        } 