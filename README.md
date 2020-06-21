# Bote

![Supported Python Versions](https://img.shields.io/pypi/pyversions/bote)
![Last commit](https://img.shields.io/github/last-commit/RuedigerVoigt/bote)

"Bote" is German for messenger or courier. The `bote` library currently just sends plain-text email from localhost or a remote SMTP server.

There are plenty of libraries for this. My reasons to write another one:
* Modularity: I outsourced this code from my [exoskeleton](https://github.com/RuedigerVoigt/exoskeleton "GitHub Repository of exoskeleton") library.
* Extensive testing (currently this is a beta version!)
* Type-Hints in the code ([PEP 484](https://www.python.org/dev/peps/pep-0484/))
* Good error messages
* Enforce that any connection to a SMTP server - except localhost / 127.0.0.1 - is encrypted.
* Automatically wrap messages to 80 characters.

## How to use it

```python
import bote

mail_settings = {
    'server': 'smtp.example.com',
    'server_port': 587,
    'encryption': 'starttls',
    'username': 'example',
    'passphrase': 'example',
    'recipient': 'foo@example.com',
    'sender': 'bar@example.com'}

mailer = bote.Mailer(mail_settings)

mailer.send_mail('Test bote', 'It worked!')
```