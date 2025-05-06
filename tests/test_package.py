"""
Tests for packaging aspects of SynthMed.

This tests package metadata and import functionality.
"""

import unittest
import importlib
import importlib.metadata


class TestPackaging(unittest.TestCase):
    """
    Test the packaging aspects of the SynthMed library.
    """
    
    def test_version(self):
        """Test that version is available and properly formatted."""
        import synthmed
        
        self.assertTrue(hasattr(synthmed, "__version__"))
        self.assertIsInstance(synthmed.__version__, str)
        
        # Check version format (should be semver-like)
        version_parts = synthmed.__version__.split(".")
        self.assertGreaterEqual(len(version_parts), 2)
        
        # Major version should be a number
        self.assertTrue(version_parts[0].isdigit())
    
    def test_core_imports(self):
        """Test that core modules can be imported."""
        # Should be able to import core components
        self.assertIsNotNone(importlib.import_module("synthmed.config"))
        self.assertIsNotNone(importlib.import_module("synthmed.engine"))
        self.assertIsNotNone(importlib.import_module("synthmed.models"))
        self.assertIsNotNone(importlib.import_module("synthmed.exporters"))
        self.assertIsNotNone(importlib.import_module("synthmed.cli"))
    
    def test_model_imports(self):
        """Test that model classes can be imported correctly."""
        from synthmed.models import Patient, Gender, Race, Condition, Encounter, MedicationRequest
        
        # These shouldn't raise exceptions if the imports are working
        self.assertIsNotNone(Patient)
        self.assertIsNotNone(Gender)
        self.assertIsNotNone(Race)
        self.assertIsNotNone(Condition)
        self.assertIsNotNone(Encounter)
        self.assertIsNotNone(MedicationRequest)
    
    def test_exporter_imports(self):
        """Test that exporter classes can be imported correctly."""
        from synthmed.exporters import CSVExporter, JSONExporter, FHIRExporter
        
        self.assertIsNotNone(CSVExporter)
        self.assertIsNotNone(JSONExporter)
        self.assertIsNotNone(FHIRExporter)


if __name__ == "__main__":
    unittest.main() 