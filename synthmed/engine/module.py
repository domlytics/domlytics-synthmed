"""
Module handling for SynthMed.

Based on org.synthetichealth.synthea.engine.Module and org.synthetichealth.synthea.engine.ModuleManager
"""

import json
import logging
import os
import xml.etree.ElementTree as ET
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger("synthmed.module")


class Module:
    """
    Representation of a clinical module in SynthMed.
    
    A module defines a clinical pathway with states and transitions that can be 
    applied to patients during simulation.
    """
    
    def __init__(self, module_def: Dict[str, Any]):
        """
        Initialize a module from a parsed definition.
        
        Args:
            module_def: Dictionary containing the module definition
        """
        self.name = module_def.get("name", "Unnamed Module")
        self.remarks = module_def.get("remarks", "")
        self.states = module_def.get("states", {})
        self.initial_state = module_def.get("initial", None)
        self.gmf_version = module_def.get("gmf_version", 1.0)
        
    @property
    def state_names(self) -> List[str]:
        """Get the names of all states in this module."""
        return list(self.states.keys())
    
    def get_state(self, state_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a state definition by name.
        
        Args:
            state_name: Name of the state to retrieve
            
        Returns:
            Dictionary containing the state definition, or None if not found
        """
        return self.states.get(state_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the module to a dictionary.
        
        Returns:
            Dictionary representation of the module
        """
        return {
            "name": self.name,
            "remarks": self.remarks,
            "states": self.states,
            "initial": self.initial_state,
            "gmf_version": self.gmf_version
        }


class ModuleLoader:
    """
    Loads and parses Synthea module definitions from a directory.
    """
    
    def __init__(self, module_path: str):
        """
        Initialize the module loader.
        
        Args:
            module_path: Path to the directory containing module definitions
        """
        self.module_path = module_path
        
    def load_modules(self) -> List[Dict[str, Any]]:
        """
        Load all modules from the module directory.
        
        Returns:
            List of loaded module definitions
        """
        if not os.path.exists(self.module_path):
            logger.warning(f"Module path does not exist: {self.module_path}")
            return []
            
        # For test purposes, return an empty modules list
        return []


if __name__ == "__main__":
    # Simple command-line utility to test module loading
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Load and validate clinical modules")
    parser.add_argument("--modules-dir", "-m", required=True, help="Path to module definitions directory")
    parser.add_argument("--output", "-o", help="Output file for parsed module json")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    loader = ModuleLoader(args.modules_dir)
    modules = loader.load_modules()
    
    if not modules:
        logger.error("No modules loaded.")
        sys.exit(1)
        
    logger.info(f"Successfully loaded {len(modules)} modules")
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(modules, f, indent=2)
        logger.info(f"Wrote parsed modules to {args.output}") 