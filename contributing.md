 # Contribution Guidelines


 ## Bug Reports

Guidelines:

 * Please avoid raising duplicate issues.
 * If you run into an exception please provide the complete traceback if possible.
 * Please answer the following questions:
     * How can the issue be reproduced?
     * What is your Operating System?
     * What version of bote are you using and how did you install it?
     * Which Python version do you use?


 ## Code Contributions

 Code Contributions are welcome. Before you spend a lot of time programming
 please check the issues page or get in contact. It is a design goal to avoid
 bloat by implementing too many features.

 ### Requirements

 * **Python Version:** Requires Python 3.10 or higher. We support Python 3.10, 3.11, 3.12, 3.13, and 3.14.
 * **Build System:** Poetry + `pyproject.toml` for dependency management.

 ### Quick Start (Poetry)

 ```bash
 # Install dependencies (incl. dev tools)
 poetry install --with dev

 # Run tests
 poetry run pytest

 # Run tests with coverage (min 95%)
 poetry run pytest --cov=bote --cov-fail-under=95

 # Type checking and linting
 poetry run mypy bote
 poetry run flake8 .
 ```
 * Please adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/).
 * The code should include some documentation.
 * Variable names should be speaking.
 * Type hints are necessary.
 * We use Python 3.10+ type hint syntax.
