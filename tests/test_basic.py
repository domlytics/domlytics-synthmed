"""
Basic tests for SynthMed functionality.
"""

import os
import tempfile
from pathlib import Path
import unittest

from synthmed import Config, Engine
from synthmed.models import Patient, Gender, Race


class TestBasicFunctionality(unittest.TestCase):
    """
    Test basic functionality of SynthMed.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name
        
        # Create a modules directory for testing
        self.modules_dir = os.path.join(self.output_dir, "modules")
        os.makedirs(self.modules_dir, exist_ok=True)
        
        # Basic configuration with minimal settings
        self.config = Config(
            population_size=2,
            output_dir=self.output_dir,
            output_format="json",
            seed=12345,
            max_workers=1,
            modules_dir=self.modules_dir
        )
    
    def tearDown(self):
        """Clean up after the test case."""
        self.temp_dir.cleanup()
    
    def test_patient_creation(self):
        """Test that we can create a patient model."""
        patient = Patient(
            first_name="Test",
            last_name="Patient",
            gender=Gender.MALE,
            race=Race.WHITE,
            birth_date="1980-01-01"
        )
        
        self.assertEqual(patient.first_name, "Test")
        self.assertEqual(patient.last_name, "Patient")
        self.assertEqual(patient.gender, Gender.MALE)
        self.assertEqual(patient.race, Race.WHITE)
        self.assertEqual(str(patient.birth_date), "1980-01-01")
        
    def test_engine_instantiation(self):
        """Test that we can instantiate the engine."""
        engine = Engine(self.config)
        self.assertIsNotNone(engine)
        
    def test_fhir_serialization(self):
        """Test that a patient can be serialized to FHIR."""
        patient = Patient(
            first_name="Test",
            last_name="Patient",
            gender=Gender.MALE,
            race=Race.WHITE,
            birth_date="1980-01-01"
        )
        
        # Convert to FHIR
        fhir_dict = patient.to_fhir()
        
        # Check basic FHIR structure
        self.assertEqual(fhir_dict["resourceType"], "Patient")
        self.assertEqual(fhir_dict["name"][0]["family"], "Patient")
        self.assertEqual(fhir_dict["name"][0]["given"][0], "Test")
        self.assertEqual(fhir_dict["gender"], "male")
        self.assertEqual(fhir_dict["birthDate"], "1980-01-01")


if __name__ == "__main__":
    unittest.main() 