# Contributors

This document outlines the contribution guidelines for the Domlytics SynthMed project.

## Copyright

Copyright © 2025 Domlytics & Berto J. Rico

## Commercial Use

For commercial use, please contact Domlytics:
- Email: info@domlytics.com
- Phone: 888-398-5411

## Contribution Process

1. **Fork the Repository**: Create your own fork of the project.
2. **Create a Feature Branch**: Make your changes in a new branch.
3. **Follow Coding Standards**: 
   - Use Black for code formatting
   - Include appropriate docstrings
   - Follow the existing code style
   - Add unit tests for new functionality
4. **Submit a Pull Request**: Include a clear description of the changes and any relevant issue numbers.

## Code Review

All submissions require review before being merged:
1. Code must pass all automated tests
2. At least one maintainer must approve the changes
3. Documentation must be updated as needed

## Development Environment

We recommend using Poetry for dependency management:

```bash
poetry install
poetry shell
```

## Testing

Run the test suite before submitting changes:

```bash
poetry run pytest
```

## Documentation

Update documentation for any new or changed functionality:

```bash
poetry run sphinx-build docs/source docs/build
```

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior include:

- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at info@domlytics.com. All complaints will be reviewed and investigated and will result in a response that is deemed necessary and appropriate to the circumstances.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.0, available at [https://www.contributor-covenant.org/version/2/0/code_of_conduct.html](https://www.contributor-covenant.org/version/2/0/code_of_conduct.html).

## License

By contributing to this project, you agree that your contributions will be licensed under the project's AGPL-2.0 license.

## Core Contributors

- Berto J. Rico - Project Lead
- Domlytics Engineering Team 