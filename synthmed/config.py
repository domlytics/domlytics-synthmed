"""
Configuration settings for SynthMed.

Based on org.synthetichealth.synthea.Config
"""

import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union


@dataclass
class Config:
    """Configuration settings for the SynthMed simulation engine."""

    # Population parameters
    population_size: int = 100
    min_age: int = 0
    max_age: int = 100

    # Seed for reproducibility
    seed: Optional[int] = None

    # Paths
    modules_dir: str = field(default_factory=lambda: os.environ.get("SYNTHMED_MODULES_DIR", ""))
    output_dir: str = field(default_factory=lambda: os.environ.get("SYNTHMED_OUTPUT_DIR", "output"))

    # Export options
    output_format: str = "fhir"  # Options: fhir, json, csv
    
    # Demographics
    gender_ratio: Dict[str, float] = field(default_factory=lambda: {"M": 0.49, "F": 0.51})
    
    # Performance
    max_workers: int = field(default_factory=lambda: os.cpu_count() or 4)
    perf_report: bool = False
    
    # Clinical parameters
    generate_only_living_patients: bool = False
    generate_conditions: bool = True
    generate_encounters: bool = True
    generate_medications: bool = True
    generate_observations: bool = True
    generate_procedures: bool = True
    
    # Optional module-specific overrides
    module_overrides: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and initialize configuration parameters."""
        # Convert paths to absolute paths
        if self.modules_dir:
            self.modules_dir = str(Path(self.modules_dir).absolute())
        self.output_dir = str(Path(self.output_dir).absolute())
        
        # Ensure output dir exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize random seed
        if self.seed is not None:
            random.seed(self.seed)
        
        # Validate output format
        if self.output_format.lower() not in ["fhir", "json", "csv"]:
            raise ValueError(f"Invalid output format: {self.output_format}. Must be one of: fhir, json, csv")
        
        # Validate gender ratio
        total = sum(self.gender_ratio.values())
        if abs(total - 1.0) > 0.001:
            # Normalize if not already a probability distribution
            for key in self.gender_ratio:
                self.gender_ratio[key] /= total

    def get_modules_path(self) -> str:
        """Get the path to the modules directory."""
        if self.modules_dir:
            return self.modules_dir
            
        # Default to looking for Synthea repo
        paths_to_check = [
            os.path.join(os.getcwd(), "synthea", "src", "main", "resources", "modules"),
            os.path.join(os.getcwd(), "modules"),
        ]
        
        for path in paths_to_check:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError(
            "Module directory not found. Please specify --modules-dir or set SYNTHMED_MODULES_DIR environment variable."
        ) 