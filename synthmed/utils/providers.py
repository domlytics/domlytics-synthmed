"""
Provider utilities for SynthMed.

Based on org.synthetichealth.synthea.world.agents.Provider
"""

import csv
import logging
import os
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

logger = logging.getLogger("synthmed.providers")


@dataclass
class Provider:
    """
    Healthcare provider information.
    """
    
    id: str
    name: str
    resource_type: str  # "Practitioner", "Organization", etc.
    specialty: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "resourceType": self.resource_type,
            "specialty": self.specialty,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone
        }


@dataclass
class Organization:
    """
    Healthcare organization information.
    """
    
    id: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    providers: List[Provider] = None
    
    def __post_init__(self):
        if self.providers is None:
            self.providers = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": self.phone,
            "providers": [p.to_dict() for p in self.providers]
        }


# Default provider specialties if no data is available
DEFAULT_SPECIALTIES = [
    "Family Practice",
    "Internal Medicine",
    "Cardiology",
    "Dermatology",
    "Neurology",
    "Orthopedic Surgery",
    "Pediatrics",
    "Psychiatry",
    "Oncology",
    "Radiology"
]

# Default organization types
DEFAULT_ORGANIZATION_TYPES = [
    "Hospital",
    "Clinic",
    "Nursing Home",
    "Urgent Care Center",
    "Emergency Department"
]


class ProviderFactory:
    """
    Factory for generating healthcare providers and organizations.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the provider factory.
        
        Args:
            data_dir: Path to directory containing provider data files
        """
        self.data_dir = data_dir
        
        # Load provider data
        self.specialties = self._load_specialties()
        self.organizations = self._load_organizations()
        self.providers = self._load_providers()
        
        # Generate some default providers if none loaded
        if not self.providers:
            self._generate_default_providers()
    
    def get_provider(self, specialty: Optional[str] = None) -> Provider:
        """
        Get a random provider, optionally filtered by specialty.
        
        Args:
            specialty: Optional specialty to filter by
            
        Returns:
            A random provider
        """
        if specialty:
            matching_providers = [p for p in self.providers 
                                if p.specialty and p.specialty.lower() == specialty.lower()]
            if matching_providers:
                return random.choice(matching_providers)
                
        # Return any provider if no specialty match
        return random.choice(self.providers) if self.providers else self._generate_provider()
    
    def get_organization(self, org_type: Optional[str] = None) -> Organization:
        """
        Get a random organization, optionally filtered by type.
        
        Args:
            org_type: Optional organization type to filter by
            
        Returns:
            A random organization
        """
        if org_type and self.organizations:
            # This assumes organization type is in the name - would be a property in real implementation
            matching_orgs = [o for o in self.organizations 
                            if org_type.lower() in o.name.lower()]
            if matching_orgs:
                return random.choice(matching_orgs)
                
        # Return any organization if no type match
        return random.choice(self.organizations) if self.organizations else self._generate_organization()
    
    def _load_specialties(self) -> List[str]:
        """Load specialties from file."""
        if not self.data_dir:
            return DEFAULT_SPECIALTIES
            
        file_path = os.path.join(self.data_dir, "specialties.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Specialties file not found: {file_path}, using defaults")
            return DEFAULT_SPECIALTIES
            
        try:
            specialties = []
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        specialties.append(row[0].strip())
            
            if not specialties:
                logger.warning(f"No specialties found in {file_path}, using defaults")
                return DEFAULT_SPECIALTIES
                
            return specialties
            
        except Exception as e:
            logger.error(f"Error loading specialties from {file_path}: {str(e)}")
            return DEFAULT_SPECIALTIES
    
    def _load_organizations(self) -> List[Organization]:
        """Load organizations from file."""
        if not self.data_dir:
            return []
            
        file_path = os.path.join(self.data_dir, "organizations.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Organizations file not found: {file_path}")
            return []
            
        try:
            organizations = []
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 3:
                        org = Organization(
                            id=row[0].strip(),
                            name=row[1].strip(),
                            address=row[2].strip() if len(row) > 2 else None,
                            city=row[3].strip() if len(row) > 3 else None,
                            state=row[4].strip() if len(row) > 4 else None,
                            zip_code=row[5].strip() if len(row) > 5 else None,
                            phone=row[6].strip() if len(row) > 6 else None
                        )
                        organizations.append(org)
            
            return organizations
            
        except Exception as e:
            logger.error(f"Error loading organizations from {file_path}: {str(e)}")
            return []
    
    def _load_providers(self) -> List[Provider]:
        """Load providers from file."""
        if not self.data_dir:
            return []
            
        file_path = os.path.join(self.data_dir, "providers.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Providers file not found: {file_path}")
            return []
            
        try:
            providers = []
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 3:
                        provider = Provider(
                            id=row[0].strip(),
                            name=row[1].strip(),
                            resource_type="Practitioner",
                            specialty=row[2].strip() if len(row) > 2 else None,
                            address=row[3].strip() if len(row) > 3 else None,
                            city=row[4].strip() if len(row) > 4 else None,
                            state=row[5].strip() if len(row) > 5 else None,
                            zip_code=row[6].strip() if len(row) > 6 else None,
                            phone=row[7].strip() if len(row) > 7 else None
                        )
                        providers.append(provider)
            
            return providers
            
        except Exception as e:
            logger.error(f"Error loading providers from {file_path}: {str(e)}")
            return []
    
    def _generate_default_providers(self) -> None:
        """Generate default providers if none loaded."""
        self.providers = []
        self.organizations = []
        
        # Generate organizations
        for i in range(5):
            org_type = random.choice(DEFAULT_ORGANIZATION_TYPES)
            org = Organization(
                id=f"org{i:03d}",
                name=f"{org_type} {i+1}",
                address=f"{random.randint(100, 9999)} Main St",
                city="Boston",
                state="MA",
                zip_code="02108",
                phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            )
            self.organizations.append(org)
            
        # Generate providers
        for i in range(20):
            specialty = random.choice(self.specialties)
            org = random.choice(self.organizations) if self.organizations else None
            
            provider = Provider(
                id=f"prov{i:03d}",
                name=f"Dr. Provider {i+1}",
                resource_type="Practitioner",
                specialty=specialty,
                address=org.address if org else f"{random.randint(100, 9999)} Main St",
                city=org.city if org else "Boston",
                state=org.state if org else "MA",
                zip_code=org.zip_code if org else "02108",
                phone=org.phone if org else f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            )
            self.providers.append(provider)
            
            # Add provider to organization
            if org:
                org.providers.append(provider)
    
    def _generate_provider(self) -> Provider:
        """Generate a single random provider."""
        specialty = random.choice(self.specialties)
        
        return Provider(
            id=str(uuid.uuid4()),
            name=f"Dr. {random.choice(['Smith', 'Jones', 'Williams', 'Johnson', 'Brown'])}",
            resource_type="Practitioner",
            specialty=specialty,
            address=f"{random.randint(100, 9999)} Main St",
            city="Boston",
            state="MA",
            zip_code="02108",
            phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        )
    
    def _generate_organization(self) -> Organization:
        """Generate a single random organization."""
        org_type = random.choice(DEFAULT_ORGANIZATION_TYPES)
        
        return Organization(
            id=str(uuid.uuid4()),
            name=f"{org_type} {random.choice(['General', 'Regional', 'Community', 'University'])}",
            address=f"{random.randint(100, 9999)} Main St",
            city="Boston",
            state="MA",
            zip_code="02108",
            phone=f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        ) 