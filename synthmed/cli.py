"""
Command-line interface for SynthMed.

Based on org.synthetichealth.synthea.Synthea
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from synthmed import __version__
from synthmed.config import Config
from synthmed.engine import Engine
from synthmed.validation import Validator


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("synthmed")


@click.group()
@click.version_option(version=__version__)
def main():
    """
    SynthMed: Python implementation of Synthea for generating synthetic healthcare data.
    """
    pass


@main.command()
@click.option("--count", "-c", type=int, default=100, help="Number of patients to generate.")
@click.option("--modules-dir", "-m", type=click.Path(exists=True, file_okay=False, dir_okay=True),
              help="Path to module definitions directory.")
@click.option("--output-format", "-f", type=click.Choice(["fhir", "json", "csv"], case_sensitive=False),
              default="fhir", help="Output format for generated data.")
@click.option("--output-dir", "-o", type=click.Path(file_okay=False, dir_okay=True),
              default="output", help="Output directory for generated data.")
@click.option("--seed", "-s", type=int, help="Random seed for reproducible generation.")
@click.option("--perf-report", is_flag=True, help="Generate performance metrics report.")
@click.option("--max-workers", type=int, help="Maximum number of parallel workers.")
@click.option("--only-living", is_flag=True, help="Generate only living patients.")
@click.option("--min-age", type=int, default=0, help="Minimum patient age.")
@click.option("--max-age", type=int, default=100, help="Maximum patient age.")
def simulate(count: int, modules_dir: Optional[str], output_format: str, output_dir: str,
             seed: Optional[int], perf_report: bool, max_workers: Optional[int],
             only_living: bool, min_age: int, max_age: int):
    """
    Generate synthetic patient data.
    """
    start_time = time.time()
    
    # Configure the engine
    config = Config(
        population_size=count,
        modules_dir=modules_dir or "",
        output_format=output_format,
        output_dir=output_dir,
        seed=seed,
        perf_report=perf_report,
        generate_only_living_patients=only_living,
        min_age=min_age,
        max_age=max_age
    )
    
    if max_workers:
        config.max_workers = max_workers
    
    # Create and run the engine
    try:
        logger.info(f"Initializing SynthMed generation engine")
        logger.info(f"Generating {count} {'living ' if only_living else ''}patients")
        logger.info(f"Output format: {output_format}")
        logger.info(f"Output directory: {output_dir}")
        if seed is not None:
            logger.info(f"Using random seed: {seed}")
        
        engine = Engine(config)
        patients = engine.run()
        
        end_time = time.time()
        
        # Output summary
        logger.info(f"Generation complete. Generated {len(patients)} patients.")
        logger.info(f"Total time: {end_time - start_time:.2f} seconds")
        
        if perf_report:
            report_file = os.path.join(output_dir, "performance_report.txt")
            with open(report_file, "w") as f:
                f.write(f"SynthMed Performance Report\n")
                f.write(f"========================\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"Population size: {count}\n")
                f.write(f"Seed: {seed}\n")
                f.write(f"Total time: {end_time - start_time:.2f} seconds\n")
                f.write(f"Average time per patient: {(end_time - start_time) / count:.4f} seconds\n")
                f.write(f"========================\n")
                
                if engine.metrics:
                    f.write("\nComponent Performance:\n")
                    for component, time_taken in engine.metrics.items():
                        f.write(f"{component}: {time_taken:.2f} seconds\n")
            
            logger.info(f"Performance report written to {report_file}")
    
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}")
        if logger.level <= logging.DEBUG:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)


@main.command()
@click.option("--input-dir", "-i", type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=True, help="Input directory containing generated data.")
@click.option("--output-file", "-o", type=click.Path(file_okay=True, dir_okay=False),
              default="validation_report.txt", help="Output file for validation report.")
def validate(input_dir: str, output_file: str):
    """
    Validate generated patient data for consistency and realism.
    """
    try:
        logger.info(f"Validating data in {input_dir}")
        
        validator = Validator(input_dir)
        results = validator.run()
        
        # Write validation report
        with open(output_file, "w") as f:
            f.write(f"SynthMed Validation Report\n")
            f.write(f"========================\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"Input directory: {input_dir}\n")
            f.write(f"========================\n\n")
            
            for category, checks in results.items():
                f.write(f"{category}:\n")
                for check_name, (passed, message) in checks.items():
                    status = "PASS" if passed else "FAIL"
                    f.write(f"  {status}: {check_name} - {message}\n")
                f.write("\n")
                
        logger.info(f"Validation report written to {output_file}")
        
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        if logger.level <= logging.DEBUG:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main() 