# Domlytics SynthMed

A Python implementation of [Synthea](https://github.com/synthetichealth/synthea) for generating hyper-realistic, longitudinal synthetic patient records at scale.

## About

SynthMed is a Python library that provides the functionality of Synthea, originally implemented in Java. It generates synthetic patient records for healthcare research, software testing, and system integration. The synthetic data includes complete medical histories with demographics, conditions, encounters, medications, procedures, and observations.

## Features

- Generate synthetic patient records with realistic disease progression
- Support for multiple output formats: FHIR R4, JSON, and CSV
- Parallel processing for scalable data generation
- Use of Synthea's original module definitions
- Reproducible results with seed-based random generation
- Detailed demographic distributions based on U.S. census data
- Performance metrics and validation tools

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (recommended for dependency management)

### Install using Poetry

```bash
git clone https://github.com/domlytics/domlytics-synthmed.git
cd domlytics-synthmed
poetry install
```

### Install using pip

```bash
pip install domlytics-synthmed
```

## Usage

### Command Line Interface

Generate 100 synthetic patients:

```bash
pysynthea simulate --count 100
```

Specify output format:

```bash
pysynthea simulate --count 10 --output-format fhir
```

Use a specific seed for reproducible results:

```bash
pysynthea simulate --count 10 --seed 12345
```

Use custom module definitions:

```bash
pysynthea simulate --count 10 --modules-dir /path/to/modules
```

Run validation on generated data:

```bash
pysynthea validate --input-dir /path/to/output
```

Generate performance report:

```bash
pysynthea simulate --count 100 --perf-report
```

### Python API

```python
from synthmed import Engine, Config

config = Config(
    population_size=100,
    output_format="fhir",
    seed=12345,
    modules_dir="/path/to/modules"
)

engine = Engine(config)
patients = engine.run()

# Access generated data
for patient in patients:
    print(patient.id, patient.first_name, patient.last_name)
```

## Module Customization

SynthMed uses the same module definition format as the original Synthea. You can:

1. Use modules directly from the Synthea repository
2. Create your own modules following the Synthea format
3. Modify existing modules to suit your needs

### Using Original Synthea Modules

To use the original Synthea modules:

1. Clone the Synthea repository: `git clone https://github.com/synthetichealth/synthea.git`
2. Point to the modules directory: `pysynthea simulate --modules-dir /path/to/synthea/src/main/resources/modules`

### Creating Custom Modules

Module definitions are JSON files that describe disease progression, treatments, and clinical pathways. See the [Synthea wiki](https://github.com/synthetichealth/synthea/wiki/Generic-Module-Framework) for detailed information on creating custom modules.

## Architecture

SynthMed follows the architecture of the original Synthea implementation with Python equivalents:

- **Engine**: Coordinates the simulation process
- **Generator**: Creates individual patient records
- **Module**: Processes clinical modules and applies state transitions
- **World**: Manages demographics and population characteristics
- **Exporter**: Handles output formatting and file generation

## Performance Considerations

- Patient generation is parallelized across available CPU cores
- Memory usage increases with population size
- For very large populations, consider batching output or streaming to disk

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Documentation

Full API documentation is available at [https://domlytics.github.io/domlytics-synthmed/](https://domlytics.github.io/domlytics-synthmed/).

Generate documentation locally:

```bash
poetry run sphinx-build docs/source docs/build
```

## License

This project is licensed under the AGPL-2.0 License - see the LICENSE file for details.

This package is open source for personal and academic use. Commercial use requires a license - please contact Domlytics at info@domlytics.com or 888-398-5411.

## Contributing

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for contribution guidelines.

## Acknowledgements

- Synthea team for the original implementation
- Domlytics for sponsoring the development
- All contributors to the project