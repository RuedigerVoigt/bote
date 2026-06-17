# Agent Guidelines

The conventions, project structure, commands, coding style, testing, and
security guidance for this repository are documented for all contributors —
human and agent — in **[contributing.md](contributing.md)**. Read it first; it
is the single source of truth.

## Agent-specific notes

- Before considering a change complete, make sure these all pass:
  - `poetry run ruff check .`
  - `poetry run mypy bote`
  - `poetry run pytest --cov=bote --cov-fail-under=100`
- Mock network/SMTP in tests (`mocker.patch('smtplib.SMTP')`); never send real
  mail and never reach out to a live SMTP server.
