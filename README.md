# Bote — Secure Python SMTP Client for Plain-Text Email

![Supported Python Versions](https://img.shields.io/pypi/pyversions/bote)
![Last commit](https://img.shields.io/github/last-commit/RuedigerVoigt/bote)
![pypi version](https://img.shields.io/pypi/v/bote)
[![Downloads](https://pepy.tech/badge/bote)](https://pepy.tech/project/bote)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![License](https://img.shields.io/pypi/l/bote)

**Bote is a small, security-focused Python library for sending plain-text email via SMTP — a safe wrapper around the standard-library `smtplib` that enforces STARTTLS/SSL encryption on every remote connection.**

Use it to send notifications, alerts, and automated email from your Python applications, whether through a local mail server on `localhost` or a remote SMTP provider. Bote validates your configuration up front and fails fast with clear, typed errors instead of cryptic SMTP tracebacks.

## Features

* **Enforced encryption** — any connection to an SMTP server other than `localhost` / `127.0.0.1` / `::1` *must* use STARTTLS or SSL. This cannot be bypassed. (It does not affect how the SMTP server then relays the message to the recipient.)
* **Early validation** — email addresses and configuration are checked when you create the `Mailer`, not when you send, so misconfiguration surfaces immediately.
* **Clear, typed errors** — custom exceptions (`UnencryptedRemoteConnection`, `NotAnEmail`, `MissingSubject`, `MissingMailContent`) with helpful messages instead of generic SMTP errors.
* **Header-injection protection** — rejects CR/LF in the subject line to prevent SMTP header injection.
* **Type safety** — full type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/), ships a `py.typed` marker) for better IDE support and fewer runtime errors.
* **Configurable timeouts** — every SMTP operation honors a timeout so an unresponsive server cannot block forever.
* **Automatic text wrapping** — messages are wrapped to a configurable width while preserving intentional line breaks.
* **Well tested** — 100% test coverage across Linux, macOS, and Windows.

> "Bote" is German for *messenger* or *courier*.

## Table of Contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Quick Start](#quick-start)
* [Keeping Your Credentials Safe](#keeping-your-credentials-safe)
* [Configuration Parameters](#configuration-parameters)
* [Recipient Options](#recipient-options)
* [Examples](#examples)
* [Error Handling](#error-handling)
* [API Summary](#api-summary)
* [Exceptions](#exceptions)
* [License](#license)
* [Resources](#resources)

## Requirements

* **Python 3.10 or newer** (uses modern type-hint syntax such as `dict[str, Any]` and `str | None`). Tested through Python 3.14.
* Dependencies (installed automatically): [`compatibility`](https://github.com/RuedigerVoigt/compatibility) `>= 2.2.0` and [`userprovided`](https://github.com/RuedigerVoigt/userprovided) `>= 2.5.0`.

## Installation

```bash
# Using pip
pip install bote

# Using Poetry
poetry add bote
```

## Quick Start

The simplest way to get started is with localhost (no credentials needed):

```python
import bote

# Minimal configuration - only sender and recipient required
mailer = bote.Mailer({
    'sender': 'dev@localhost',
    'recipient': 'test@example.com'
})

mailer.send_mail('Hello', 'This is a test email')
```

By default, bote connects to `localhost` without encryption.

### Keeping Your Credentials Safe

>You should not store secrets in code that may be shared or saved to source control.

To avoid accidental exposure of secrets it is best practice to use environment variables that can be accessed with `os.environ.get()`. The [`python-dotenv`](https://github.com/theskumar/python-dotenv) could be useful for this too - do not forget to add `.env` files to `.gitignore`.

Example using environment variables (optionally with `.env`):

```bash
# .env (do NOT commit this file)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=app@example.com
SMTP_PASSWORD=super-secret-app-password
SMTP_SENDER=noreply@example.com
SMTP_RECIPIENT=user@example.com
```

```python
import os
# Optional: load variables from .env during local development
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

import bote

mailer = bote.Mailer({
    'server': os.environ.get('SMTP_SERVER', 'localhost'),
    'server_port': int(os.environ.get('SMTP_PORT', '0')) or None,
    'encryption': 'starttls',
    'username': os.environ.get('SMTP_USER'),
    'passphrase': os.environ.get('SMTP_PASSWORD'),
    'sender': os.environ.get('SMTP_SENDER', 'noreply@localhost'),
    'recipient': os.environ.get('SMTP_RECIPIENT', 'user@localhost'),
})

mailer.send_mail('Hello', 'Email sent with env-sourced credentials')
```


### Configuration Parameters

Only `sender` and `recipient` are required. All other parameters are optional:

Parameter | Default | Description
--- | --- | ---
`server`| `localhost` | SMTP server hostname
`server_port`| `None` | SMTP server port
`encryption`| `off` | Encryption method: `'off'`, `'starttls'`, or `'ssl'`
`username`| `None` | SMTP authentication username
`passphrase`| `None` | SMTP authentication password
`wrap_width`| `80` | Line wrap width for email body
`timeout`| `60` | Socket timeout in seconds for SMTP operations

**Important:** `username` and `passphrase` must be provided together or both omitted.

### Recipient Options

The `recipient` parameter accepts either:
- **String**: A single email address
- **Dictionary**: Multiple recipients with keys like `'default'` and `'admin'`

```python
# Single recipient
'recipient': 'user@example.com'

# Multiple recipients
'recipient': {
    'default': 'user@example.com',
    'admin': 'admin@example.com'
}
```

When using a dictionary with an `'admin'` key, you can use the `send_mail_to_admin()` shortcut method.



## Examples

Here are common production scenarios for sending email via remote SMTP servers.

### Localhost with Custom Port

```python
import bote

mailer = bote.Mailer({
    'server': 'localhost',
    'server_port': 1025,
    'recipient': 'test@example.com',
    'sender': 'dev@localhost'
})
mailer.send_mail('Test Email', 'Testing with custom port')
```

### STARTTLS (Port 587)

```python
import os
import bote

mail_settings = {
    'server': 'smtp.example.com',
    'server_port': 587,
    'encryption': 'starttls',
    'username': os.environ.get('SMTP_USER'),
    'passphrase': os.environ.get('SMTP_PASSWORD'),
    'recipient': 'user@example.com',
    'sender': 'noreply@example.com'
}
mailer = bote.Mailer(mail_settings)
mailer.send_mail('Hello', 'Email sent via STARTTLS')
```

### SSL/TLS (Port 465)

```python
import os
import bote

mail_settings = {
    'server': 'smtp.gmail.com',
    'server_port': 465,
    'encryption': 'ssl',
    'username': os.environ.get('GMAIL_USER'),
    'passphrase': os.environ.get('GMAIL_APP_PASSWORD'),
    'recipient': 'recipient@example.com',
    'sender': os.environ.get('GMAIL_USER')
}
mailer = bote.Mailer(mail_settings)
mailer.send_mail('Notification', 'Email sent via SSL/TLS')
```

### Multiple Recipients with Admin

```python
import bote

mail_settings = {
    'server': 'smtp.example.com',
    'server_port': 587,
    'encryption': 'starttls',
    'username': 'user@example.com',
    'passphrase': 'password',
    'recipient': {
        'default': 'user@example.com',
        'admin': 'admin@example.com'
    },
    'sender': 'app@example.com'
}
mailer = bote.Mailer(mail_settings)

# Send to default recipient
mailer.send_mail('Update', 'New features available')

# Send to admin
mailer.send_mail_to_admin('Alert', 'System requires attention')

# Override recipient for one message
mailer.send_mail('Custom', 'One-off message', overwrite_recipient='other@example.com')
```

## Error Handling

Bote validates configuration when you create the `Mailer`, so most mistakes are caught before you ever try to send. Sending then raises clear, catchable exceptions:

```python
import bote

try:
    mailer = bote.Mailer({
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'user@example.com',
        'passphrase': 'app-password',
        'sender': 'noreply@example.com',
        'recipient': 'user@example.com',
    })
    mailer.send_mail('Subject', 'Body text')
except bote.UnencryptedRemoteConnection:
    print("Refused: remote connections must use STARTTLS or SSL.")
except bote.NotAnEmail:
    print("One of the addresses is not a valid email.")
except (bote.MissingSubject, bote.MissingMailContent):
    print("A subject and a body are both required.")
```

All custom exceptions inherit from `bote.BoteException`, so you can catch them all with a single `except bote.BoteException:`.

## API Summary

### Constructor

**`bote.Mailer(mail_settings: dict)`**

Creates a mailer instance with validated settings.

**Required settings:**
- `sender` (str): Sender email address
- `recipient` (str | dict): Recipient email address or dictionary with 'default'/'admin' keys

**Optional settings:**
- `server` (str): SMTP server hostname (default: `'localhost'`)
- `server_port` (int): SMTP server port (default: `None`)
- `encryption` (str): Encryption method - `'off'`, `'starttls'`, or `'ssl'` (default: `'off'`)
- `username` (str): SMTP authentication username (default: `None`)
- `passphrase` (str): SMTP authentication password (default: `None`)
- `wrap_width` (int): Line wrap width for email body (default: `80`)
- `timeout` (float): Socket timeout in seconds for all SMTP operations (default: `60`)

**Note:** `username` and `passphrase` must be provided together or both omitted.

### Methods

**`send_mail(message_subject: str, message_text: str, overwrite_recipient: str | None = None)`**

Send an email with the given subject and body text. Optionally override the default recipient.

**`send_mail_to_admin(message_subject: str, message_text: str)`**

Send an email to the admin address (requires `recipient` to be a dictionary with an `'admin'` key).

## Exceptions

Bote raises custom exceptions for common error cases. They are exported at the top level (`bote.NotAnEmail`) and are also available from the `bote.err` module:

- **`bote.UnencryptedRemoteConnection`**: Raised when attempting to connect to a remote SMTP server without encryption
- **`bote.NotAnEmail`**: Raised when an invalid email address is provided
- **`bote.MissingSubject`**: Raised when attempting to send an email without a subject line
- **`bote.MissingMailContent`**: Raised when attempting to send an email without body content

All exceptions inherit from `bote.BoteException`, which inherits from the standard `Exception` class, so `except bote.BoteException:` catches every bote-specific error.

## License

Bote is released under the [Apache License 2.0](LICENSE).

## Resources

* **Changelog:** [CHANGELOG.md](CHANGELOG.md)
* **Security policy / reporting a vulnerability:** [SECURITY.md](SECURITY.md)
* **Contributing:** [contributing.md](contributing.md)
* **Issue tracker:** <https://github.com/RuedigerVoigt/bote/issues>
* **PyPI:** <https://pypi.org/project/bote/>
