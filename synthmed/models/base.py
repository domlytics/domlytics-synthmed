"""
Base model for all SynthMed data models.

Based on org.synthetichealth.synthea.world.concepts.HealthRecord
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class SynthmedBaseModel(BaseModel):
    """Base model with common fields for all SynthMed models."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "json_encoders": {
                datetime: lambda dt: dt.isoformat(),
            }
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump()
    
    def to_fhir(self) -> Dict[str, Any]:
        """
        Convert the model to a FHIR resource.
        
        This method should be implemented by child classes.
        """
        raise NotImplementedError("Subclasses must implement to_fhir()")
    
    def to_csv_record(self) -> Dict[str, Any]:
        """
        Convert the model to a CSV-friendly record.
        
        This method should be implemented by child classes.
        """
        raise NotImplementedError("Subclasses must implement to_csv_record()") 