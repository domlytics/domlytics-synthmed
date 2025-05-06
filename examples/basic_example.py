#!/usr/bin/env python
"""
Basic example of using SynthMed to generate synthetic patients.
"""

import os
import argparse
import logging
from pathlib import Path

from synthmed import Config, Engine


def main():
    """Run a basic SynthMed simulation."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate synthetic patient data with SynthMed")
    parser.add_argument("--count", "-c", type=int, default=10,
                        help="Number of patients to generate (default: 10)")
    parser.add_argument("--output-dir", "-o", type=str, default="output",
                        help="Directory to write output files (default: 'output')")
    parser.add_argument("--format", "-f", type=str, default="fhir",
                        choices=["fhir", "json", "csv"],
                        help="Output format (default: fhir)")
    parser.add_argument("--seed", "-s", type=int, help="Random seed for reproducibility")
    parser.add_argument("--modules-dir", "-m", type=str,
                        help="Directory containing module definitions")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Configure the simulation
    config = Config(
        population_size=args.count,
        output_dir=args.output_dir,
        output_format=args.format,
        seed=args.seed,
        modules_dir=args.modules_dir or ""
    )
    
    # Create and run the engine
    engine = Engine(config)
    patients = engine.run()
    
    # Print summary
    for i, patient in enumerate(patients[:5]):  # Show first 5 patients
        print(f"Patient {i+1}: {patient.full_name}, "
              f"Age: {patient.age}, Gender: {patient.gender.value}, "
              f"Location: {patient.city}, {patient.state}")
    
    if len(patients) > 5:
        print(f"... and {len(patients) - 5} more patients")
    
    print(f"\nGenerated data written to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main() 