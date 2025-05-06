"""
Tests for SynthMed exporters.
"""

import json
import os
import tempfile
from datetime import datetime, date
import unittest

from synthmed.models import Patient, Gender, Race
from synthmed.exporters import JSONExporter, CSVExporter, FHIRExporter


class TestExporters(unittest.TestCase):
    """
    Test the export functionality of SynthMed.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name
        
        # Create some test patients
        self.patients = [
            Patient(
                first_name="Test",
                last_name="Patient",
                gender=Gender.MALE,
                race=Race.WHITE,
                birth_date=date(1980, 1, 1)
            ),
            Patient(
                first_name="Jane",
                last_name="Doe",
                gender=Gender.FEMALE,
                race=Race.BLACK,
                birth_date=date(1990, 5, 15)
            )
        ]
    
    def tearDown(self):
        """Clean up after the test case."""
        self.temp_dir.cleanup()
    
    def test_json_export(self):
        """Test JSON export with datetime objects."""
        json_exporter = JSONExporter(self.output_dir)
        json_exporter.export(self.patients)
        
        # Check that the file was created
        json_file = os.path.join(self.output_dir, "patients.json")
        self.assertTrue(os.path.exists(json_file))
        
        # Check that we can read it back 
        with open(json_file, "r") as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["first_name"], "Test")
        self.assertEqual(data[1]["first_name"], "Jane")
        
        # Check that datetime was serialized correctly
        self.assertIn("created_at", data[0])
        self.assertIsInstance(data[0]["created_at"], str)
        
        # Check individual patient files
        patient_dir = os.path.join(self.output_dir, "patients")
        self.assertTrue(os.path.exists(patient_dir))
        
        # Should have 2 files, one for each patient
        patient_files = os.listdir(patient_dir)
        self.assertEqual(len(patient_files), 2)
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        csv_exporter = CSVExporter(self.output_dir)
        csv_exporter.export(self.patients)
        
        # Check that the file was created
        csv_file = os.path.join(self.output_dir, "patients.csv")
        self.assertTrue(os.path.exists(csv_file))
        
        # Check the content of the file
        with open(csv_file, "r") as f:
            content = f.read()
        
        # Should contain header and 2 patient records
        lines = content.strip().split("\n")
        self.assertEqual(len(lines), 3)  # Header + 2 patients
        
        # Check header has the expected fields
        header = lines[0]
        self.assertIn("FIRST", header)
        self.assertIn("LAST", header)
        self.assertIn("GENDER", header)
        self.assertIn("BIRTHDATE", header)
        
        # Check that patient data is present
        self.assertIn("Test", content)
        self.assertIn("Jane", content)
        self.assertIn("1980-01-01", content)
        self.assertIn("1990-05-15", content)
    
    def test_fhir_export(self):
        """Test FHIR export functionality."""
        fhir_exporter = FHIRExporter(self.output_dir)
        fhir_exporter.export(self.patients)
        
        # Check that the patients file was created
        fhir_file = os.path.join(self.output_dir, "patients.fhir.json")
        self.assertTrue(os.path.exists(fhir_file))
        
        # Check that we can read it back
        with open(fhir_file, "r") as f:
            data = json.load(f)
        
        # Should be a Bundle with 2 entries
        self.assertEqual(data["resourceType"], "Bundle")
        self.assertEqual(len(data["entry"]), 2)
        
        # Check that resources are of type Patient
        self.assertEqual(data["entry"][0]["resource"]["resourceType"], "Patient")
        self.assertEqual(data["entry"][1]["resource"]["resourceType"], "Patient")
        
        # Check patient data
        self.assertEqual(data["entry"][0]["resource"]["name"][0]["given"][0], "Test")
        self.assertEqual(data["entry"][1]["resource"]["name"][0]["given"][0], "Jane")


if __name__ == "__main__":
    unittest.main() 