"""
Validation module for SynthMed generated data.

This module provides tools to validate the consistency and realism of generated patient data.
"""

import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd

logger = logging.getLogger("synthmed.validation")


class Validator:
    """
    Validator for SynthMed generated data.
    
    This class provides methods to validate the consistency and realism of
    generated patient data across various dimensions.
    """
    
    def __init__(self, input_dir: str):
        """
        Initialize the validator.
        
        Args:
            input_dir: Directory containing generated data to validate
        """
        self.input_dir = Path(input_dir)
        self.format = self._detect_format()
        self.results = defaultdict(dict)
        
    def _detect_format(self) -> str:
        """
        Detect the format of the generated data.
        
        Returns:
            str: The detected format (fhir, json, or csv)
        """
        # Check for FHIR bundles
        if list(self.input_dir.glob("*.fhir.json")):
            return "fhir"
            
        # Check for JSON files
        if (self.input_dir / "patients.json").exists():
            return "json"
            
        # Check for CSV files
        if (self.input_dir / "patients.csv").exists():
            return "csv"
            
        # Default to CSV if can't determine
        return "csv"
    
    def run(self) -> Dict[str, Dict[str, Tuple[bool, str]]]:
        """
        Run all validation checks on the generated data.
        
        Returns:
            Dict: A nested dictionary of validation results by category and check name
                  with tuples of (passed, message)
        """
        logger.info(f"Running validation on {self.input_dir} (format: {self.format})")
        
        # Run validators based on detected format
        if self.format == "csv":
            self._validate_csv()
        elif self.format == "json":
            self._validate_json()
        elif self.format == "fhir":
            self._validate_fhir()
        
        return dict(self.results)
    
    def _validate_csv(self):
        """Validate CSV-formatted data."""
        # Load CSV files
        try:
            patients_file = self.input_dir / "patients.csv"
            if not patients_file.exists():
                self.results["files"]["patients_csv"] = (False, "patients.csv file not found")
                return
                
            patients_df = pd.read_csv(patients_file)
            
            # Check if we have encounters
            encounters_file = self.input_dir / "encounters.csv"
            has_encounters = encounters_file.exists()
            
            if has_encounters:
                encounters_df = pd.read_csv(encounters_file)
                # Check demographic distribution
                self._validate_demographics(patients_df)
                
                # Check encounter consistency
                self._validate_encounter_consistency(patients_df, encounters_df)
                
                # Check conditions, if available
                conditions_file = self.input_dir / "conditions.csv"
                if conditions_file.exists():
                    conditions_df = pd.read_csv(conditions_file)
                    self._validate_condition_consistency(patients_df, encounters_df, conditions_df)
            else:
                # Just validate demographics
                self._validate_demographics(patients_df)
                
            # Record that we successfully loaded files
            self.results["files"]["csv_load"] = (True, "Successfully loaded CSV files")
            
        except Exception as e:
            logger.error(f"Error validating CSV data: {str(e)}")
            self.results["files"]["csv_load"] = (False, f"Error loading CSV files: {str(e)}")
    
    def _validate_json(self):
        """Validate JSON-formatted data."""
        try:
            patients_file = self.input_dir / "patients.json"
            if not patients_file.exists():
                self.results["files"]["patients_json"] = (False, "patients.json file not found")
                return
                
            with open(patients_file, "r") as f:
                patients = json.load(f)
                
            # Convert to DataFrame for easier validation
            patients_df = pd.json_normalize(patients)
            
            # Check demographic distribution
            self._validate_demographics(patients_df)
            
            # Record that we successfully loaded files
            self.results["files"]["json_load"] = (True, "Successfully loaded JSON files")
            
        except Exception as e:
            logger.error(f"Error validating JSON data: {str(e)}")
            self.results["files"]["json_load"] = (False, f"Error loading JSON files: {str(e)}")
    
    def _validate_fhir(self):
        """Validate FHIR-formatted data."""
        try:
            # Find all FHIR bundles
            fhir_files = list(self.input_dir.glob("*.fhir.json"))
            
            if not fhir_files:
                self.results["files"]["fhir_files"] = (False, "No FHIR bundle files found")
                return
                
            # Load all patient resources
            patients = []
            encounters = []
            conditions = []
            
            for fhir_file in fhir_files:
                with open(fhir_file, "r") as f:
                    bundle = json.load(f)
                    
                    if not isinstance(bundle, dict) or "resourceType" not in bundle:
                        continue
                    
                    if bundle["resourceType"] != "Bundle":
                        continue
                        
                    # Extract resources
                    for entry in bundle.get("entry", []):
                        resource = entry.get("resource", {})
                        resource_type = resource.get("resourceType", "")
                        
                        if resource_type == "Patient":
                            patients.append(resource)
                        elif resource_type == "Encounter":
                            encounters.append(resource)
                        elif resource_type == "Condition":
                            conditions.append(resource)
            
            # Convert to DataFrames for easier validation
            if patients:
                patients_df = pd.json_normalize(patients)
                
                # Basic validation on patients
                self._validate_fhir_patients(patients_df)
                
                # Record success
                self.results["files"]["fhir_load"] = (True, f"Successfully loaded {len(patients)} FHIR resources")
            else:
                self.results["files"]["fhir_load"] = (False, "No Patient resources found in FHIR bundles")
            
        except Exception as e:
            logger.error(f"Error validating FHIR data: {str(e)}")
            self.results["files"]["fhir_load"] = (False, f"Error loading FHIR files: {str(e)}")
    
    def _validate_demographics(self, patients_df: pd.DataFrame):
        """
        Validate demographic distributions.
        
        Args:
            patients_df: DataFrame containing patient data
        """
        try:
            # Check age distribution
            if "BIRTHDATE" in patients_df.columns:
                # Convert to datetime
                patients_df["BIRTHDATE"] = pd.to_datetime(patients_df["BIRTHDATE"])
                
                # Calculate age
                today = pd.Timestamp(datetime.now().date())
                patients_df["AGE"] = (today - patients_df["BIRTHDATE"]).dt.days / 365.25
                
                # Check age range
                min_age = patients_df["AGE"].min()
                max_age = patients_df["AGE"].max()
                mean_age = patients_df["AGE"].mean()
                
                self.results["demographics"]["age_range"] = (
                    0 <= min_age <= 120 and 0 <= max_age <= 120,
                    f"Age range: {min_age:.1f} to {max_age:.1f}, mean: {mean_age:.1f}"
                )
            
            # Check gender distribution
            if "GENDER" in patients_df.columns:
                gender_counts = patients_df["GENDER"].value_counts(normalize=True)
                
                # Expecting roughly 50/50 distribution
                m_pct = gender_counts.get("M", 0) * 100
                f_pct = gender_counts.get("F", 0) * 100
                
                # Check if within reasonable range (40-60%)
                self.results["demographics"]["gender_distribution"] = (
                    40 <= m_pct <= 60 and 40 <= f_pct <= 60,
                    f"Gender distribution: M={m_pct:.1f}%, F={f_pct:.1f}%"
                )
            
            # Check race distribution
            if "RACE" in patients_df.columns:
                race_counts = patients_df["RACE"].value_counts(normalize=True) * 100
                
                # Just report the distribution
                race_str = ", ".join([f"{race}={pct:.1f}%" for race, pct in race_counts.items()])
                self.results["demographics"]["race_distribution"] = (
                    True,
                    f"Race distribution: {race_str}"
                )
            
            # Check mortality rate
            if "DEATHDATE" in patients_df.columns:
                death_rate = patients_df["DEATHDATE"].notna().mean() * 100
                
                # Expecting death rate to be reasonable
                self.results["demographics"]["mortality_rate"] = (
                    0 <= death_rate <= 50,  # Very wide range to accommodate various settings
                    f"Mortality rate: {death_rate:.1f}%"
                )
                
        except Exception as e:
            logger.error(f"Error validating demographics: {str(e)}")
            self.results["demographics"]["validation_error"] = (False, f"Error: {str(e)}")
    
    def _validate_encounter_consistency(self, patients_df: pd.DataFrame, encounters_df: pd.DataFrame):
        """
        Validate consistency between patients and encounters.
        
        Args:
            patients_df: DataFrame containing patient data
            encounters_df: DataFrame containing encounter data
        """
        try:
            # Check that all encounters have valid patient IDs
            patient_ids = set(patients_df["Id"].astype(str))
            encounter_patient_ids = set(encounters_df["PATIENT"].astype(str))
            
            invalid_patient_ids = encounter_patient_ids - patient_ids
            self.results["consistency"]["valid_patient_refs"] = (
                len(invalid_patient_ids) == 0,
                f"Found {len(invalid_patient_ids)} encounters with invalid patient references"
            )
            
            # Check that encounters occur between birth and death (or present)
            if all(col in encounters_df.columns for col in ["START", "PATIENT"]):
                # Convert dates
                encounters_df["START"] = pd.to_datetime(encounters_df["START"])
                
                # Merge with patients to get birth/death dates
                if "BIRTHDATE" in patients_df.columns:
                    patients_df["BIRTHDATE"] = pd.to_datetime(patients_df["BIRTHDATE"])
                    
                    merged = encounters_df.merge(
                        patients_df[["Id", "BIRTHDATE", "DEATHDATE"]],
                        left_on="PATIENT",
                        right_on="Id",
                        how="left"
                    )
                    
                    # Check if any encounters occur before birth
                    before_birth = (merged["START"] < merged["BIRTHDATE"]).sum()
                    self.results["consistency"]["encounters_after_birth"] = (
                        before_birth == 0,
                        f"Found {before_birth} encounters occurring before patient birth"
                    )
                    
                    # Check if any encounters occur after death
                    if "DEATHDATE" in patients_df.columns:
                        merged["DEATHDATE"] = pd.to_datetime(merged["DEATHDATE"])
                        after_death = ((merged["START"] > merged["DEATHDATE"]) & merged["DEATHDATE"].notna()).sum()
                        self.results["consistency"]["encounters_before_death"] = (
                            after_death == 0,
                            f"Found {after_death} encounters occurring after patient death"
                        )
            
            # Check that patients have a reasonable number of encounters
            patient_encounter_counts = encounters_df["PATIENT"].value_counts()
            max_encounters = patient_encounter_counts.max()
            mean_encounters = patient_encounter_counts.mean()
            
            self.results["consistency"]["reasonable_encounter_count"] = (
                max_encounters <= 1000,  # Very high threshold to accommodate various settings
                f"Max encounters per patient: {max_encounters}, Mean: {mean_encounters:.1f}"
            )
                
        except Exception as e:
            logger.error(f"Error validating encounter consistency: {str(e)}")
            self.results["consistency"]["encounter_validation_error"] = (False, f"Error: {str(e)}")
    
    def _validate_condition_consistency(self, patients_df: pd.DataFrame, 
                                        encounters_df: pd.DataFrame, 
                                        conditions_df: pd.DataFrame):
        """
        Validate consistency between patients, encounters, and conditions.
        
        Args:
            patients_df: DataFrame containing patient data
            encounters_df: DataFrame containing encounter data
            conditions_df: DataFrame containing condition data
        """
        try:
            # Check that all conditions have valid patient IDs
            patient_ids = set(patients_df["Id"].astype(str))
            condition_patient_ids = set(conditions_df["PATIENT"].astype(str))
            
            invalid_patient_ids = condition_patient_ids - patient_ids
            self.results["conditions"]["valid_patient_refs"] = (
                len(invalid_patient_ids) == 0,
                f"Found {len(invalid_patient_ids)} conditions with invalid patient references"
            )
            
            # Check that all referenced encounters exist
            if "ENCOUNTER" in conditions_df.columns and "Id" in encounters_df.columns:
                encounter_ids = set(encounters_df["Id"].astype(str))
                condition_encounter_ids = set(
                    conditions_df.loc[conditions_df["ENCOUNTER"].notna(), "ENCOUNTER"].astype(str)
                )
                
                invalid_encounter_ids = condition_encounter_ids - encounter_ids
                self.results["conditions"]["valid_encounter_refs"] = (
                    len(invalid_encounter_ids) == 0,
                    f"Found {len(invalid_encounter_ids)} conditions with invalid encounter references"
                )
            
            # Check that conditions occur between birth and death (or present)
            if all(col in conditions_df.columns for col in ["START", "PATIENT"]):
                # Convert dates
                conditions_df["START"] = pd.to_datetime(conditions_df["START"])
                
                # Merge with patients to get birth/death dates
                if "BIRTHDATE" in patients_df.columns:
                    patients_df["BIRTHDATE"] = pd.to_datetime(patients_df["BIRTHDATE"])
                    
                    merged = conditions_df.merge(
                        patients_df[["Id", "BIRTHDATE", "DEATHDATE"]],
                        left_on="PATIENT",
                        right_on="Id",
                        how="left"
                    )
                    
                    # Check if any conditions occur before birth
                    before_birth = (merged["START"] < merged["BIRTHDATE"]).sum()
                    self.results["conditions"]["conditions_after_birth"] = (
                        before_birth == 0,
                        f"Found {before_birth} conditions occurring before patient birth"
                    )
                    
                    # Check if any conditions occur after death
                    if "DEATHDATE" in patients_df.columns:
                        merged["DEATHDATE"] = pd.to_datetime(merged["DEATHDATE"])
                        after_death = ((merged["START"] > merged["DEATHDATE"]) & merged["DEATHDATE"].notna()).sum()
                        self.results["conditions"]["conditions_before_death"] = (
                            after_death == 0,
                            f"Found {after_death} conditions occurring after patient death"
                        )
                
        except Exception as e:
            logger.error(f"Error validating condition consistency: {str(e)}")
            self.results["conditions"]["condition_validation_error"] = (False, f"Error: {str(e)}")
    
    def _validate_fhir_patients(self, patients_df: pd.DataFrame):
        """
        Validate FHIR patient resources.
        
        Args:
            patients_df: DataFrame containing patient resource data
        """
        try:
            # Check required fields
            required_fields = ["id", "gender", "birthDate"]
            missing_fields = [field for field in required_fields if field not in patients_df.columns]
            
            self.results["fhir"]["required_fields"] = (
                len(missing_fields) == 0,
                f"Missing required fields: {', '.join(missing_fields) if missing_fields else 'None'}"
            )
            
            # Check birthdates are valid
            if "birthDate" in patients_df.columns:
                try:
                    patients_df["birthDate"] = pd.to_datetime(patients_df["birthDate"])
                    min_date = patients_df["birthDate"].min()
                    max_date = patients_df["birthDate"].max()
                    
                    # Check that dates are in a reasonable range
                    today = pd.Timestamp(datetime.now().date())
                    min_reasonable_date = pd.Timestamp((today - timedelta(days=120*365)).date())
                    
                    self.results["fhir"]["valid_birthdates"] = (
                        min_date >= min_reasonable_date and max_date <= today,
                        f"Birthdate range: {min_date.date()} to {max_date.date()}"
                    )
                except Exception as e:
                    self.results["fhir"]["valid_birthdates"] = (
                        False,
                        f"Error parsing birthDate: {str(e)}"
                    )
            
            # Check gender values
            if "gender" in patients_df.columns:
                valid_genders = {"male", "female", "other", "unknown"}
                invalid_genders = set(patients_df["gender"].unique()) - valid_genders
                
                self.results["fhir"]["valid_genders"] = (
                    len(invalid_genders) == 0,
                    f"Invalid gender values: {', '.join(invalid_genders) if invalid_genders else 'None'}"
                )
                
        except Exception as e:
            logger.error(f"Error validating FHIR patients: {str(e)}")
            self.results["fhir"]["patient_validation_error"] = (False, f"Error: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate SynthMed generated data")
    parser.add_argument("--input-dir", "-i", required=True, help="Input directory containing generated data")
    parser.add_argument("--output-file", "-o", default="validation_report.txt", help="Output file for validation report")
    
    args = parser.parse_args()
    
    validator = Validator(args.input_dir)
    results = validator.run()
    
    # Write validation report
    with open(args.output_file, "w") as f:
        f.write(f"SynthMed Validation Report\n")
        f.write(f"========================\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Input directory: {args.input_dir}\n")
        f.write(f"========================\n\n")
        
        for category, checks in results.items():
            f.write(f"{category}:\n")
            for check_name, (passed, message) in checks.items():
                status = "PASS" if passed else "FAIL"
                f.write(f"  {status}: {check_name} - {message}\n")
            f.write("\n")
            
    print(f"Validation report written to {args.output_file}") 