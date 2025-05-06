"""
Core Engine implementation for SynthMed.

Based on org.synthetichealth.synthea.engine.Engine
"""

import logging
import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Any, Optional

from synthmed.config import Config
from synthmed.engine.generator import Generator
from synthmed.engine.module import ModuleLoader
from synthmed.models import Patient
from synthmed.exporters import exporter_factory

logger = logging.getLogger("synthmed.engine")


class Engine:
    """
    Core simulation engine for SynthMed.
    
    The Engine is responsible for coordinating the overall simulation process,
    including loading modules, generating patients, and exporting results.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the simulation engine.
        
        Args:
            config: Configuration settings for the simulation
        """
        self.config = config
        self.module_loader = ModuleLoader(config.get_modules_path())
        self.metrics: Dict[str, float] = {}
        
    def run(self) -> List[Patient]:
        """
        Run the simulation according to the provided configuration.
        
        This method coordinates the entire process:
        1. Load clinical modules
        2. Generate patients in parallel
        3. Export results in the specified format
        
        Returns:
            List of generated patient models
        """
        # Record overall time
        start_time = time.time()
        
        # Load modules
        modules_start_time = time.time()
        logger.info(f"Loading clinical modules from {self.config.get_modules_path()}")
        modules = self.module_loader.load_modules()
        modules_time = time.time() - modules_start_time
        self.metrics["module_loading"] = modules_time
        logger.info(f"Loaded {len(modules)} modules in {modules_time:.2f} seconds")
        
        # Generate patients
        generation_start_time = time.time()
        logger.info(f"Generating {self.config.population_size} patients using {self.config.max_workers} workers")
        patients = self._generate_population(modules)
        generation_time = time.time() - generation_start_time
        self.metrics["patient_generation"] = generation_time
        
        average_time = generation_time / max(1, len(patients))
        logger.info(f"Generated {len(patients)} patients in {generation_time:.2f} seconds " +
                   f"({average_time:.4f}s per patient)")
        
        # Export results
        export_start_time = time.time()
        logger.info(f"Exporting results in {self.config.output_format} format to {self.config.output_dir}")
        exporter = exporter_factory(self.config.output_format, self.config.output_dir)
        exporter.export(patients)
        export_time = time.time() - export_start_time
        self.metrics["data_export"] = export_time
        logger.info(f"Exported results in {export_time:.2f} seconds")
        
        # Record total time
        total_time = time.time() - start_time
        self.metrics["total_time"] = total_time
        logger.info(f"Total simulation time: {total_time:.2f} seconds")
        
        return patients
    
    def _generate_population(self, modules: List[Dict]) -> List[Patient]:
        """
        Generate a population of patients.
        
        Args:
            modules: List of loaded module definitions
            
        Returns:
            List of generated patient models
        """
        # Create a generator instance to share modules
        generator = Generator(self.config, modules)
        
        # For very small populations, don't use parallel processing
        if self.config.population_size <= 10 or self.config.max_workers == 1:
            return [generator.generate_patient(i) for i in range(self.config.population_size)]
            
        # Process in parallel for larger populations
        patients = []
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Map patient IDs to futures
            futures = [
                executor.submit(generator.generate_patient, i)
                for i in range(self.config.population_size)
            ]
            
            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    patient = future.result()
                    patients.append(patient)
                    
                    # Log progress
                    if (i + 1) % max(1, self.config.population_size // 10) == 0:
                        logger.info(f"Generated {i + 1}/{self.config.population_size} patients " +
                                   f"({((i + 1) / self.config.population_size * 100):.1f}%)")
                        
                except Exception as e:
                    logger.error(f"Error generating patient: {str(e)}")
                    
        return patients 