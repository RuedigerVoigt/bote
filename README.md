# Bote

![Supported Python Versions](https://img.shields.io/pypi/pyversions/bote)
![Last commit](https://img.shields.io/github/last-commit/RuedigerVoigt/bote)
![pypi version](https://img.shields.io/pypi/v/bote)
[![Downloads](https://pepy.tech/badge/bote)](https://pepy.tech/project/bote)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

**A Python library for sending plain-text email via SMTP with enforced encryption for remote connections.**

Bote is a Python SMTP client library that sends plain-text emails. It wraps Python's built-in `smtplib` with a focus on security:
* **Enforcing encryption**: Any connection to a SMTP server - except `localhost` / `127.0.0.1` / `::1` - must be encrypted. (This does not influence how the SMTP server sends the message to the recipient.)
* **Validation**: Email addresses and configuration validated at initialization, not when sending
* **Clear Errors:** Provides custom exceptions with helpful messages instead of generic SMTP errors
* **Type safety**: Full type hints ([PEP 484](https://www.python.org/dev/peps/pep-0484/)) for better IDE support and fewer runtime errors.
* Extensive testing
* Automatically wrap messages preserving intentional line-breaks.

"Bote" is German for messenger or courier. The `bote` library sends plain-text email from localhost or a remote SMTP server. 

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

Bote raises custom exceptions for common error cases:

- **`UnencryptedRemoteConnection`**: Raised when attempting to connect to a remote SMTP server without encryption
- **`NotAnEmail`**: Raised when an invalid email address is provided
- **`MissingSubject`**: Raised when attempting to send an email without a subject line
- **`MissingMailContent`**: Raised when attempting to send an email without body content

All exceptions inherit from `BoteException`, which inherits from the standard `Exception` class.
