"""
Patient model for SynthMed.

Based on org.synthetichealth.synthea.world.agents.Person
"""

import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import Field, validator

from synthmed.models.base import SynthmedBaseModel


class Gender(str, Enum):
    """Gender enumeration for patients."""
    
    MALE = "M"
    FEMALE = "F"


class Race(str, Enum):
    """Race enumeration for patients."""
    
    WHITE = "white"
    BLACK = "black"
    ASIAN = "asian"
    NATIVE = "native"
    HISPANIC = "hispanic"
    OTHER = "other"


class MaritalStatus(str, Enum):
    """Marital status enumeration for patients."""
    
    NEVER_MARRIED = "S"  # Single
    MARRIED = "M"
    DIVORCED = "D"
    WIDOWED = "W"


class Patient(SynthmedBaseModel):
    """
    Patient model representing a person in the healthcare system.
    
    This is the core data structure for the patient simulation.
    """

    # Demographics
    first_name: str
    last_name: str
    gender: Gender
    race: Race
    ethnicity: Optional[str] = None
    birth_date: date
    death_date: Optional[date] = None
    marital_status: Optional[MaritalStatus] = None
    
    # Socioeconomic factors
    income: Optional[int] = None
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    
    # Geographic information
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    
    # Healthcare attributes
    healthcare_coverage: Optional[str] = None
    healthcare_expenses: float = 0.0
    healthcare_coverage_expenses: float = 0.0
    
    # Clinical attributes
    height_cm: Optional[float] = None  # Height in centimeters
    weight_kg: Optional[float] = None  # Weight in kilograms
    blood_type: Optional[str] = None
    
    # Attributes to track associated records
    conditions: List[str] = Field(default_factory=list)  # IDs of conditions
    encounters: List[str] = Field(default_factory=list)  # IDs of encounters
    medications: List[str] = Field(default_factory=list)  # IDs of medications
    procedures: List[str] = Field(default_factory=list)  # IDs of procedures
    observations: List[str] = Field(default_factory=list)  # IDs of observations
    
    # Flags to track patient state
    is_alive: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def age(self) -> int:
        """Calculate the patient's age in years."""
        end_date = self.death_date if self.death_date else date.today()
        age = end_date.year - self.birth_date.year
        
        # Adjust if birthday hasn't occurred yet this year
        if (end_date.month, end_date.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
            
        return max(0, age)
    
    @property
    def full_name(self) -> str:
        """Get the patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_fhir(self) -> Dict[str, Any]:
        """Convert the patient to a FHIR Patient resource."""
        deceased = bool(self.death_date)
        deceased_datetime = self.death_date.isoformat() if self.death_date else None
        
        # Map marital status to FHIR codes
        marital_status_map = {
            MaritalStatus.NEVER_MARRIED: "S",
            MaritalStatus.MARRIED: "M",
            MaritalStatus.DIVORCED: "D",
            MaritalStatus.WIDOWED: "W",
        }
        
        marital_status_code = None
        if self.marital_status:
            marital_status_code = marital_status_map.get(self.marital_status)
        
        fhir_patient = {
            "resourceType": "Patient",
            "id": self.id,
            "meta": {
                "profile": [
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
                ]
            },
            "identifier": [
                {
                    "system": "https://github.com/domlytics/domlytics-synthmed",
                    "value": self.id
                }
            ],
            "name": [
                {
                    "family": self.last_name,
                    "given": [self.first_name]
                }
            ],
            "gender": "male" if self.gender == Gender.MALE else "female",
            "birthDate": self.birth_date.isoformat(),
            "deceasedBoolean": deceased
        }
        
        if deceased_datetime:
            fhir_patient["deceasedDateTime"] = deceased_datetime
            
        if self.address:
            fhir_patient["address"] = [
                {
                    "line": [self.address],
                    "city": self.city or "",
                    "state": self.state or "",
                    "postalCode": self.zip_code or ""
                }
            ]
            
        if marital_status_code:
            fhir_patient["maritalStatus"] = {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                        "code": marital_status_code
                    }
                ]
            }
            
        # Add US Core extensions for race and ethnicity
        if self.race:
            race_extension = {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
                "extension": [
                    {
                        "url": "ombCategory",
                        "valueCoding": {
                            "system": "urn:oid:2.16.840.1.113883.6.238",
                            "code": self.race.value
                        }
                    },
                    {
                        "url": "text",
                        "valueString": self.race.value.capitalize()
                    }
                ]
            }
            
            if "extension" not in fhir_patient:
                fhir_patient["extension"] = []
                
            fhir_patient["extension"].append(race_extension)
            
        if self.ethnicity:
            ethnicity_extension = {
                "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
                "extension": [
                    {
                        "url": "text",
                        "valueString": self.ethnicity
                    }
                ]
            }
            
            if "extension" not in fhir_patient:
                fhir_patient["extension"] = []
                
            fhir_patient["extension"].append(ethnicity_extension)
            
        return fhir_patient
    
    def to_csv_record(self) -> Dict[str, Any]:
        """Convert the patient to a CSV record."""
        return {
            "ID": self.id,
            "BIRTHDATE": self.birth_date.isoformat(),
            "DEATHDATE": self.death_date.isoformat() if self.death_date else "",
            "SSN": f"999-{self.id[:2]}-{self.id[2:6]}"[:11],  # Fake SSN
            "FIRST": self.first_name,
            "LAST": self.last_name,
            "GENDER": self.gender.value,
            "RACE": self.race.value,
            "ETHNICITY": self.ethnicity or "",
            "MARITAL": self.marital_status.value if self.marital_status else "",
            "ADDRESS": self.address or "",
            "CITY": self.city or "",
            "STATE": self.state or "",
            "ZIP": self.zip_code or "",
            "COUNTY": self.county or "",
            "HEALTHCARE_EXPENSES": self.healthcare_expenses,
            "HEALTHCARE_COVERAGE": self.healthcare_coverage_expenses
        } 