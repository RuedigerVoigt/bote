# Changelog / History

## Version 2.0.0 (upcoming)

* Migrated from setup.py to pyproject.toml with Poetry as build backend.
* Migrated project metadata to the standardized PEP 621 `[project]` table (requires `poetry-core>=2.0.0`).
* Python Support:
  * Drop support for Python 3.8 and 3.9 (EOL or near EOL).
  * Tests and support for Python 3.10, 3.11, 3.12, 3.13, and 3.14.
* Code modernization:
  * Exceptions are now importable directly from the `bote` package (e.g. `bote.NotAnEmail`), not only from `bote.err`.
  * Switch to package-level logger instead of root logger (library best practice).
  * Updated dependencies: compatibility>=2.2.0 and userprovided>=2.5.0.
  * Fixed type annotations.
  * Bumped development tooling to current major versions.
  * Adopted Google-style docstrings (`Args:`/`Raises:` sections) throughout the package as the documentation convention.
* Behavior changes:
  * Credential validation: Username and passphrase must now be provided together or both omitted. Providing only one raises `ValueError` at initialization. This catches configuration errors early.
  * Conditional authentication: SMTP login is now skipped when both username and passphrase are omitted, enabling authentication methods that don't require credentials (e.g., IP-based auth).
  * Connection timeout: All SMTP operations now honor a configurable `timeout` setting (`mail_settings['timeout']`, default 60 seconds, validated as a positive number). Previously a connection could block indefinitely on an unresponsive server.
* Quality:
  * Workflow enforces 100% test coverage.
  * Added separate Ruff linting workflow.
  * All GitHub Actions workflows updated to latest versions.
  * Added a Dependabot configuration tracking Python dependencies and GitHub Actions versions.
  * Added an experimental CI run against the latest Python pre-release (currently 3.15 beta); it is allowed to fail, so upcoming breakage is reported without blocking the build.
* Security:
  * Added a `SECURITY.md` security policy documenting supported versions and how to report a vulnerability.
  * Enabled GitHub Private Vulnerability Reporting for confidential disclosure.
  * Added a release workflow that publishes to PyPI via OIDC trusted publishing (no long-lived API token) with build attestations.
  * Enabled immutable releases so published release tags and assets cannot be altered after the fact.
  * Added a Bandit workflow that scans the package for common security issues on every push and pull request.
  * Added a scheduled pip-audit workflow that scans dependencies for known vulnerabilities daily.

## Version 1.2.2 stable (2021-10-10)

* Tests (except mypy) now run with Python 3.10 final.
* Updated dependency.

## Version 1.2.1 stable (2021-08-05)

* Marked as compatible with Python 3.10 as tests with release candidate 1 run flawlessly on Linux, MacOS, and Windows.
* Update dependencies to versions compatible with Python 3.10.

## Version 1.2.0 stable (2021-07-24)

* Use [custom exceptions](bote/err.py).
* Run tests for Python 3.10 with Beta 4 instead of Beta 3.


## Version 1.1.1 stable (2021-06-24)

* Small code improvements.
* Updated dependencies.
* Improved code testing:
  * Tests now also run with Python `3.10.0-beta.3` on Ubuntu.
  * Although the code should be platform independent, tests are now also run with MacOS and Windows VMs to be sure.
  * Improved test coverage from 85 to 97%.


## Version 1.1.0 stable (2021-05-17)

* Make compatible with the newest version of its sister project `userprovided`. (Older versions still work.)
* The optional parameter `wrap_width` allows you to set after how many characters a line is wrapped. (Defaults to 80).
* The parameter `recipient` can now be either a string or a dictionary. If it is a string, that address will be used as a recipient as long that is not overwritten. In case you use a dictionary, the behavior is the same if you defined a key named `default`. Defining an additional `admin` key allows you to use the new `send_mail_to_admin` command.

## Version 1.0.0 stable (2021-01-30)

* Change development status from `beta` to `stable`.
* Check used Python version with the [`compatibility`](https://github.com/RuedigerVoigt/compatibility) package. (A sister-project so development is synchronized.)
* Replaced `unittest` with the `pytest` testing framework and increased test coverage.
* Fixed minor bug: Would not raise an exception if no port was provided for an external server

## Version 0.9.1 beta (2020-10-11)

* Now also test with Python 3.9.

## Version 0.9.0 beta (2020-06-21)

* Initial public release: The `bote` library is the former communication module of its sister-project [exoskeleton](https://github.com/RuedigerVoigt/exoskeleton "GitHub Repository of exoskeleton").
