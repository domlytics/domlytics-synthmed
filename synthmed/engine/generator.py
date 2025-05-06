"""
Patient generator implementation for SynthMed.

Based on org.synthetichealth.synthea.engine.Generator
"""

import logging
import random
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set

import numpy as np

from synthmed.config import Config
from synthmed.models import Patient, Gender, Race
from synthmed.utils.demographics import Demographics
from synthmed.utils.providers import ProviderFactory

logger = logging.getLogger("synthmed.generator")


class Generator:
    """
    Generator for individual synthetic patients.
    
    The Generator applies clinical modules to create a complete medical history
    for a single patient.
    """
    
    def __init__(self, config: Config, modules: List[Dict]):
        """
        Initialize the patient generator.
        
        Args:
            config: Configuration settings for patient generation
            modules: List of loaded module definitions
        """
        self.config = config
        self.modules = modules
        self.demographics = Demographics()
        self.provider_factory = ProviderFactory()
        
    def generate_patient(self, patient_id: int) -> Patient:
        """
        Generate a complete synthetic patient record.
        
        Args:
            patient_id: Numeric ID of the patient to generate
            
        Returns:
            A fully populated Patient model with complete medical history
        """
        # Set a unique seed for this patient for reproducibility
        if self.config.seed is not None:
            random.seed(self.config.seed + patient_id)
            np.random.seed(self.config.seed + patient_id)
        
        # Generate demographics
        patient = self._generate_demographics(patient_id)
        
        # Run module simulations to generate clinical history
        self._run_modules(patient)
        
        # If configured, ensure the patient is alive
        if self.config.generate_only_living_patients and not patient.is_alive:
            # Recursive call to generate a living patient instead
            return self.generate_patient(patient_id)
        
        return patient
    
    def _generate_demographics(self, patient_id: int) -> Patient:
        """
        Generate patient demographic information.
        
        Args:
            patient_id: Numeric ID of the patient
            
        Returns:
            Patient model with demographic information
        """
        # Determine gender based on configured gender ratio
        gender = self._randomly_select_gender()
        
        # Select race, ethnicity, and location
        race = self._randomly_select_race()
        ethnicity = self.demographics.get_ethnicity(race)
        
        # Choose birth year based on min/max age
        today = date.today()
        min_birth_year = today.year - self.config.max_age
        max_birth_year = today.year - self.config.min_age
        
        birth_year = random.randint(min_birth_year, max_birth_year)
        
        # Choose random birth date within the year
        if birth_year == today.year:
            # If this year, only use days up to today
            birth_month = random.randint(1, today.month)
            max_day = today.day if birth_month == today.month else 28  # Simplification
            birth_day = random.randint(1, max_day)
        else:
            birth_month = random.randint(1, 12)
            max_day = 28  # Simplification to avoid month length issues
            birth_day = random.randint(1, max_day)
        
        birth_date = date(birth_year, birth_month, birth_day)
        
        # Get name appropriate for demographics
        first_name = self.demographics.get_first_name(gender)
        last_name = self.demographics.get_last_name(race)
        
        # Generate socioeconomic data
        income_level = random.randint(0, 100000)  # Simplified income model
        
        # Create the patient
        patient = Patient(
            id=f"p{patient_id:06d}",
            first_name=first_name,
            last_name=last_name,
            gender=Gender.MALE if gender == "M" else Gender.FEMALE,
            race=race,
            ethnicity=ethnicity,
            birth_date=birth_date,
            income=income_level
        )
        
        # Assign location
        state, city, zip_code = self.demographics.get_location()
        patient.state = state
        patient.city = city
        patient.zip_code = zip_code
        
        # Assign address - simplified
        patient.address = f"{random.randint(100, 9999)} Main St"
        
        return patient
    
    def _randomly_select_gender(self) -> str:
        """
        Randomly select a gender based on configured ratios.
        
        Returns:
            String code for the selected gender ("M" or "F")
        """
        rnd = random.random()
        cumulative = 0.0
        
        for gender, ratio in self.config.gender_ratio.items():
            cumulative += ratio
            if rnd < cumulative:
                return gender
                
        # Default if something goes wrong
        return "F"
    
    def _randomly_select_race(self) -> Race:
        """
        Randomly select a race based on demographic data.
        
        Returns:
            Race enum value for the selected race
        """
        race_probs = self.demographics.get_race_distribution()
        rnd = random.random()
        cumulative = 0.0
        
        for race_name, prob in race_probs.items():
            cumulative += prob
            if rnd < cumulative:
                # Convert to Race enum
                if race_name.lower() == "white":
                    return Race.WHITE
                elif race_name.lower() == "black":
                    return Race.BLACK
                elif race_name.lower() == "asian":
                    return Race.ASIAN
                elif race_name.lower() == "native":
                    return Race.NATIVE
                elif race_name.lower() == "hispanic":
                    return Race.HISPANIC
                else:
                    return Race.OTHER
                    
        # Default if something goes wrong
        return Race.OTHER
    
    def _run_modules(self, patient: Patient) -> None:
        """
        Run all clinical modules to simulate patient's medical history.
        
        Args:
            patient: The patient to simulate
        """
        # Sort modules by priority
        modules = sorted(self.modules, key=lambda m: m.get("priority", 0))
        
        # Track present clinical state
        time_step_days = 7  # Default time step is one week
        
        # Current simulation date starts at birth
        current_date = patient.birth_date
        end_date = date.today()
        
        # Record of module executions
        executed_modules: Set[str] = set()
        
        # Condition tracker
        active_conditions: Dict[str, Dict] = {}
        
        # Run the simulation over time
        while current_date <= end_date and patient.is_alive:
            # Calculate patient's age at this time step
            age_days = (current_date - patient.birth_date).days
            
            if age_days < 0:
                # Skip time steps before birth
                current_date += timedelta(days=time_step_days)
                continue
                
            # Evaluate each module for the current time step
            for module in modules:
                module_name = module.get("name", "")
                
                # Check if module should run (based on conditions or probability)
                if self._should_run_module(module, patient, active_conditions):
                    # Process module
                    self._process_module(module, patient, current_date)
                    executed_modules.add(module_name)
            
            # Advance time
            current_date += timedelta(days=time_step_days)
        
        # Record death if appropriate based on modules and age
        if not patient.is_alive:
            # If no death date was set, assign a reasonable one
            if not patient.death_date:
                patient.death_date = current_date - timedelta(days=random.randint(0, time_step_days))
    
    def _should_run_module(self, module: Dict, patient: Patient, active_conditions: Dict[str, Dict]) -> bool:
        """
        Determine whether a module should run for a specific patient at a specific time.
        
        Args:
            module: Module definition dictionary
            patient: The patient to check
            active_conditions: Dictionary of active conditions for the patient
            
        Returns:
            True if the module should run, False otherwise
        """
        # Check if module is applicable to patient gender
        if "remarks" in module:
            if "female only" in module["remarks"].lower() and patient.gender != Gender.FEMALE:
                return False
            if "male only" in module["remarks"].lower() and patient.gender != Gender.MALE:
                return False
        
        # Module-specific probability of execution
        if "probability" in module:
            if random.random() > module["probability"]:
                return False
        
        # Check required states or conditions
        if "required_states" in module:
            required_states = module["required_states"]
            if isinstance(required_states, list):
                for state in required_states:
                    if state not in active_conditions:
                        return False
        
        # By default, run the module
        return True
    
    def _process_module(self, module: Dict, patient: Patient, current_date: date) -> None:
        """
        Process a module for a patient at a specific time.
        
        Args:
            module: Module definition dictionary
            patient: The patient to process
            current_date: The current simulation date
        """
        # This would be a complex state machine implementation
        # For now, it's just a placeholder for the real module processing logic
        
        # Simple module simulation - if this is a death module, may set patient.is_alive = False
        if "states" in module:
            for state in module["states"]:
                state_type = state.get("type", "")
                
                # Process Death state types
                if state_type == "Death":
                    # Calculate probability of death at this stage
                    death_prob = state.get("direct_transition_probability", 0.01)
                    
                    if random.random() < death_prob:
                        patient.is_alive = False
                        patient.death_date = current_date
                        break 