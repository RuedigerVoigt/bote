# Contribution Guidelines

## Contributing

Both bug reports and code contributions are welcome.
Before you spend a lot of time programming please check the issues page or get
in contact. It is a design goal to avoid bloat by implementing too many
features.

To report a bug, please
[open a bug report](https://github.com/RuedigerVoigt/bote/issues/new?template=bug_report.yml)
and search existing issues first to avoid duplicates.

*Security vulnerabilities are different:*
Please report them privately via GitHub's
["Report a vulnerability"](https://github.com/RuedigerVoigt/bote/security/advisories/new)
button or by email. See [SECURITY.md](SECURITY.md) for details.


### Requirements

* **Python Version:** Requires Python 3.10 or higher.
* **Build System:** Poetry + `pyproject.toml` for dependency management.

### Project Structure

* `bote/` – library source (`mailer.py` with the `Mailer` class, `err.py` for
  custom exceptions, `py.typed` marker).
* `tests/` – pytest suite (`test_bote.py`, `test_version_resolution.py`);
  `pytest.ini` discovers `test_*.py` files.
* `pyproject.toml` – PEP 621 `[project]` metadata with the Poetry build backend.
* `.github/workflows/` – CI workflows (see Continuous Integration below).

### Continuous Integration

Pushes and pull requests trigger the checks below (the "When it runs" column
notes any branch restrictions). They are expected to pass before a change is
merged.

| Workflow | When it runs | Purpose |
| --- | --- | --- |
| Pytest, MacOS Test, Windows Test | push & PR | Run the test suite on Linux (Python 3.10–3.14), macOS (3.10, 3.14), and Windows (3.10–3.14). |
| Coverage Check | push & PR | Fail if test coverage drops below 100%. |
| Ruff | push & PR | Lint the code. |
| Mypy | push & PR (`master`/`develop`) | Static type checking on Python 3.10 and 3.14. |
| Bandit | push & PR | Security scan of the package (tests excluded). |
| CodeQL | push & PR (`master`/`develop`), weekly | Static security analysis. |
| pip-audit | push & PR (`master`/`develop`), daily, manual | Scan dependencies for known CVEs. |

### Coding Style

* Please adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/);
  4-space indentation; prefer clear, short functions.
* Type hints are required.
* Use Python 3.10+ syntax.
* Naming: `snake_case` for functions and variables, `CamelCase` for classes,
  `UPPER_CASE` for constants. Use speaking names.
* Docstrings: Google style (`Args:`/`Returns:`/`Raises:` sections where
  applicable). Document non-trivial private methods too.
* Log via the package logger (`logging.getLogger(__name__)`).

### Testing


* Add new tests as `tests/test_*.py`.
* Write deterministic tests and mock network/SMTP
  (`mocker.patch('smtplib.SMTP')`) — never send real mail.

### Commits & Pull Requests

* Commit messages: imperative, concise, and scoped (e.g. `Add`, `Fix`,
  `Update`, `Remove`, `Migrate`).
* PRs: include a summary, the rationale, and linked issues. Ensure lint, type
  checks, and tests pass locally.
* Update the docs and `CHANGELOG.md` when user-facing behavior or compatibility
  changes.

