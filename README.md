# Bote

![Supported Python Versions](https://img.shields.io/pypi/pyversions/bote)
![Last commit](https://img.shields.io/github/last-commit/RuedigerVoigt/bote)
![pypi version](https://img.shields.io/pypi/v/bote)
[![Downloads](https://pepy.tech/badge/bote)](https://pepy.tech/project/bote)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellow)](https://www.ruediger-voigt.eu/coverage/bote/index.html)

"Bote" is German for messenger or courier. The `bote` library sends plain-text email from localhost or a remote SMTP server. The base functionality is in the standard library. Reasons to write yet another package were:
* Enforce that any connection to a SMTP server - except `localhost` / `127.0.0.1` / `::1` - is encrypted. (Of course this does not influence how the SMTP server sends the message to the recipient.)
* Extensive testing
* Type-Hints in the code ([PEP 484](https://www.python.org/dev/peps/pep-0484/))
* Good error messages
* Automatically wrap messages preserving intentional line-breaks.
* Modularity

## How to use it


```python
import os
import bote

mail_settings = {
    'server': 'smtp.example.com',
    'server_port': 587,
    'encryption': 'starttls',  # or 'ssl', or 'off'
    # Best practice: get secrets from environment variables
    # instead of hardcoded strings =>
    'username': os.environ.get('MAIL_USER'),
    'passphrase': os.environ.get('MAIL_PASSPHRASE'),
    'recipient': 'foo@example.com',
    'sender': 'bar@example.com',
    'wrap_width': 80}

mailer = bote.Mailer(mail_settings)

mailer.send_mail('Test bote',  # subject
                 'It worked!'  # mail body
                 )

# If the setting recipient is a dictionary and contains
# an admin key:
mailer.send_mail_to_admin('Test', 'Message for the admin')
```

All parameters except `recipient` and `sender` are optional as `bote` has defaults for all others:

Parameter | Default Value
--- | ---
`server`| `localhost`
`server_port`| `None`
`encryption`| `off`
`username`| `None`
`passphrase`| `None`
`wrap_width`| `80`

The parameter `recipient` can either be an email address as a string or a dictionary. In the later case, this should have a `default` key with the standard recipient as value. Otherwise the recipient has to be set for every message. If it contains an `admin` key, the shorthand command `send_mail_to_admin` can be used.

### Keeping Your Credentials Save

>You should not store secrets in code that may be shared or saved to source control.

To avoid accidental exposure of secrets it is best practice to use environment variables that can be accessed with `os.environ.get()`. The [`python-dotenv`](https://github.com/theskumar/python-dotenv) could be useful for this too - do not forget to add `.env` files to `.gitignore`.
