"""
Demographics utilities for SynthMed.

Based on org.synthetichealth.synthea.world.geography and related classes.
"""

import csv
import logging
import os
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from synthmed.models import Race

logger = logging.getLogger("synthmed.demographics")

# Default demographic distributions if no data files are available
DEFAULT_RACE_DISTRIBUTION = {
    "white": 0.60,
    "black": 0.13,
    "asian": 0.06,
    "native": 0.02,
    "hispanic": 0.18,
    "other": 0.01,
}

DEFAULT_FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua"
]

DEFAULT_FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Margaret", "Betty",
    "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna"
]

DEFAULT_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor",
    "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"
]

DEFAULT_LOCATIONS = [
    ("Massachusetts", "Boston", "02108"),
    ("New York", "New York", "10001"),
    ("California", "Los Angeles", "90001"),
    ("Texas", "Houston", "77001"),
    ("Florida", "Miami", "33101"),
]


class Demographics:
    """
    Demographics utility for generating realistic demographic data.
    
    This class handles sampling from demographic distributions for names,
    locations, and other characteristics.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize demographics generator.
        
        Args:
            data_dir: Path to directory containing demographic data files
        """
        self.data_dir = data_dir
        
        # Load demographic data
        self.first_names_male = self._load_names("first_names_male.csv", DEFAULT_FIRST_NAMES_MALE)
        self.first_names_female = self._load_names("first_names_female.csv", DEFAULT_FIRST_NAMES_FEMALE)
        self.last_names = self._load_names("last_names.csv", DEFAULT_LAST_NAMES)
        
        # Load demographic distributions
        self.race_distribution = self._load_race_distribution()
        self.locations = self._load_locations()
        
        # Ethnicity mapping - simplified
        self.ethnicity_map = {
            Race.WHITE: "non-hispanic",
            Race.BLACK: "non-hispanic",
            Race.ASIAN: "non-hispanic",
            Race.NATIVE: "non-hispanic",
            Race.HISPANIC: "hispanic",
            Race.OTHER: "non-hispanic",
        }
    
    def get_first_name(self, gender: str) -> str:
        """
        Get a random first name appropriate for the given gender.
        
        Args:
            gender: "M" for male, "F" for female
            
        Returns:
            A random first name
        """
        if gender == "M":
            return random.choice(self.first_names_male)
        else:
            return random.choice(self.first_names_female)
    
    def get_last_name(self, race: Race) -> str:
        """
        Get a random last name appropriate for the given race.
        
        Args:
            race: The race of the person
            
        Returns:
            A random last name
        """
        # In a real implementation, this would be race-specific
        return random.choice(self.last_names)
    
    def get_race_distribution(self) -> Dict[str, float]:
        """
        Get the race distribution.
        
        Returns:
            Dictionary mapping race names to probabilities
        """
        return self.race_distribution
    
    def get_ethnicity(self, race: Race) -> str:
        """
        Get an ethnicity appropriate for the given race.
        
        Args:
            race: The race of the person
            
        Returns:
            An ethnicity string
        """
        return self.ethnicity_map.get(race, "non-hispanic")
    
    def get_location(self) -> Tuple[str, str, str]:
        """
        Get a random location (state, city, zip).
        
        Returns:
            Tuple of (state, city, zip_code)
        """
        return random.choice(self.locations)
    
    def _load_names(self, filename: str, default_names: List[str]) -> List[str]:
        """
        Load names from a CSV file.
        
        Args:
            filename: Name of the CSV file
            default_names: Default names to use if file not found
            
        Returns:
            List of names
        """
        if not self.data_dir:
            return default_names
            
        file_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(file_path):
            logger.warning(f"Name file not found: {file_path}, using defaults")
            return default_names
            
        try:
            names = []
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0].strip():
                        names.append(row[0].strip())
            
            if not names:
                logger.warning(f"No names found in {file_path}, using defaults")
                return default_names
                
            return names
            
        except Exception as e:
            logger.error(f"Error loading names from {file_path}: {str(e)}")
            return default_names
    
    def _load_race_distribution(self) -> Dict[str, float]:
        """
        Load race distribution from a CSV file.
        
        Returns:
            Dictionary mapping race names to probabilities
        """
        if not self.data_dir:
            return DEFAULT_RACE_DISTRIBUTION
            
        file_path = os.path.join(self.data_dir, "race_distribution.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Race distribution file not found: {file_path}, using defaults")
            return DEFAULT_RACE_DISTRIBUTION
            
        try:
            distribution = {}
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 2:
                        race = row[0].strip().lower()
                        probability = float(row[1])
                        distribution[race] = probability
            
            # Ensure probabilities sum to 1
            total = sum(distribution.values())
            if total > 0:
                for race in distribution:
                    distribution[race] /= total
            
            if not distribution:
                logger.warning(f"No race distribution found in {file_path}, using defaults")
                return DEFAULT_RACE_DISTRIBUTION
                
            return distribution
            
        except Exception as e:
            logger.error(f"Error loading race distribution from {file_path}: {str(e)}")
            return DEFAULT_RACE_DISTRIBUTION
    
    def _load_locations(self) -> List[Tuple[str, str, str]]:
        """
        Load locations from a CSV file.
        
        Returns:
            List of (state, city, zip_code) tuples
        """
        if not self.data_dir:
            return DEFAULT_LOCATIONS
            
        file_path = os.path.join(self.data_dir, "locations.csv")
        
        if not os.path.exists(file_path):
            logger.warning(f"Locations file not found: {file_path}, using defaults")
            return DEFAULT_LOCATIONS
            
        try:
            locations = []
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                # Skip header
                next(reader, None)
                
                for row in reader:
                    if len(row) >= 3:
                        state = row[0].strip()
                        city = row[1].strip()
                        zip_code = row[2].strip()
                        locations.append((state, city, zip_code))
            
            if not locations:
                logger.warning(f"No locations found in {file_path}, using defaults")
                return DEFAULT_LOCATIONS
                
            return locations
            
        except Exception as e:
            logger.error(f"Error loading locations from {file_path}: {str(e)}")
            return DEFAULT_LOCATIONS 