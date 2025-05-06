"""
Tests for SynthMed CLI interface.
"""

import os
import unittest
import tempfile
import subprocess
import sys

class TestCLI(unittest.TestCase):
    """
    Test the command-line interface functionality.
    """
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary output directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name
        
        # Create a test modules directory
        self.modules_dir = os.path.join(self.output_dir, "modules")
        os.makedirs(self.modules_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after the test case."""
        self.temp_dir.cleanup()
    
    def test_cli_help(self):
        """Test the CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "synthmed.cli", "--help"],
            capture_output=True,
            text=True
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0)
        
        # Check expected content in help output
        self.assertIn("SynthMed", result.stdout)
        self.assertIn("simulate", result.stdout)
        self.assertIn("validate", result.stdout)
    
    def test_cli_simulate_help(self):
        """Test the CLI simulate help command."""
        result = subprocess.run(
            [sys.executable, "-m", "synthmed.cli", "simulate", "--help"],
            capture_output=True,
            text=True
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0)
        
        # Check expected content in help output
        self.assertIn("Generate synthetic patient data", result.stdout)
        self.assertIn("--count", result.stdout)
        self.assertIn("--output-format", result.stdout)
    
    def test_cli_simulate_csv(self):
        """Test the CLI simulate command with CSV output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "synthmed.cli",
                "simulate",
                "--count", "1",
                "--output-dir", self.output_dir,
                "--output-format", "csv",
                "--modules-dir", self.modules_dir
            ],
            capture_output=True,
            text=True
        )
        
        # Check command executed successfully
        self.assertEqual(result.returncode, 0)
        
        # Check output file was created
        csv_file = os.path.join(self.output_dir, "patients.csv")
        self.assertTrue(os.path.exists(csv_file))
        
        # Check content of the output file
        with open(csv_file, "r") as f:
            content = f.read()
        
        # Should have a header and a patient record
        self.assertIn("BIRTHDATE", content)
        self.assertIn("FIRST", content)
        self.assertIn("LAST", content)
        

if __name__ == "__main__":
    unittest.main() 