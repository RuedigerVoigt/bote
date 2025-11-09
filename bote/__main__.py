"""
Bote

Source: https://github.com/RuedigerVoigt/bote
(c) 2020-2025 Rüdiger Voigt and contributors
Released under the Apache License 2.0
"""

from datetime import date
from email.message import EmailMessage
import logging
from pathlib import Path
import re
import smtplib
import ssl
import textwrap
from importlib.metadata import PackageNotFoundError, version
from typing import Any

# sister-projects:
import compatibility
import userprovided

from bote import err

# Use package-level logger for library best practices
logger = logging.getLogger(__name__)

# Resolve version from installed package metadata; fall back to local pyproject
try:
    __version__ = version("bote")
except PackageNotFoundError:
    # Source checkout fallback without requiring tomllib (works on Python 3.10)
    try:
        _pyproject_text = (Path(__file__).parent.parent / "pyproject.toml").read_text(encoding="utf-8")
        _m = re.search(r"(?m)^[\t ]*version\s*=\s*\"([^\"]+)\"", _pyproject_text)
        __version__ = _m.group(1) if _m else "0+unknown"
    except Exception:  # noqa: BLE001 - best-effort fallback
        __version__ = "0+unknown"

# Release date for compatibility check
_release_date = date(2025, 11, 9)


class Mailer:
    "Class of bote to send email"
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 mail_settings: dict[str, Any]):
        """Check the mail settings for plausibility and set
           missing values to their default. """

        compatibility.Check(
            package_name='bote',
            package_version=__version__,
            release_date=_release_date,
            python_version_support={
                'min_version': '3.10',
                'incompatible_versions': ['3.8', '3.9'],
                'max_tested_version': '3.14'},
            nag_over_update={
                    'nag_days_after_release': 365,
                    'nag_in_hundred': 100},
            language_messages='en',
            system_support={
                'full': {'Linux', 'Windows', 'MacOS'}
            }
        )

        userprovided.parameters.validate_dict_keys(
            dict_to_check=mail_settings,
            allowed_keys={'server', 'server_port', 'encryption',
                          'username', 'passphrase',
                          'recipient', 'sender',
                          'wrap_width'},
            necessary_keys={'recipient', 'sender'},
            dict_name='mail_settings')

        # Not all keys must be there.
        # Provide default values for missing ones with defaultdict:

        self.server: str = mail_settings.get('server', 'localhost')
        self.is_local = bool(self.server in ('localhost', '127.0.0.1', '::1'))

        # Encryption defaults to 'off' as the default for server is localhost.
        self.encryption: str = mail_settings.get('encryption', 'off')

        if self.encryption not in ('off', 'starttls', 'ssl'):
            raise ValueError('Invalid value for the encryption parameter!')
        # Enforce encryption if the connection is not to localhost:
        if not self.is_local and self.encryption == 'off':
            raise err.UnencryptedRemoteConnection(
                'Connection is not local, but unencrypted!')

        self.server_port = mail_settings.get('server_port', None)
        if self.server_port:
            if not userprovided.parameters.is_port(self.server_port):
                raise ValueError('Port must be integer (0 to 65535)')
        elif not self.is_local:
            raise ValueError(
                'Provide a port if you connect to a remote SMTP server.')

        self.username = mail_settings.get('username', None)
        self.passphrase = mail_settings.get('passphrase', None)
        # Even for a remote connection username and passphrase might be
        # not necessary - for example if the identification is host based.
        # Therefore no exception is thrown.
        if not self.username:
            logger.debug('Parameter username is empty.')
        if not self.passphrase:
            logger.debug('Parameter passphrase is empty.')

        self.default_recipient: str = ''
        self.recipient: str | dict = mail_settings['recipient']

        if isinstance(self.recipient, dict):
            if len(self.recipient) == 0:
                raise ValueError('Dictionary recipient is empty.')

            # Warn if there is no default key
            try:
                self.default_recipient = self.recipient['default']
            except KeyError:
                logger.warning("No default key in recipient dictionary!")

            # Validate all recipient values are valid email addresses
            for _key, _value in self.recipient.items():
                if not isinstance(_value, str) or not userprovided.mail.is_email(_value):
                    raise err.NotAnEmail('recipient is not a valid email!')

        elif isinstance(self.recipient, str):
            if not userprovided.mail.is_email(str(self.recipient)):
                raise err.NotAnEmail('recipient is not a valid email!')
            self.default_recipient = self.recipient
        else:
            raise ValueError(
                'Parameter recipient must be either string or dictionary.')

        self.sender = mail_settings['sender']
        if not userprovided.mail.is_email(self.sender):
            raise err.NotAnEmail('sender is not a valid email!')

        self.wrap_width = mail_settings.get('wrap_width', 80)
        if not isinstance(self.wrap_width, int):
            raise ValueError('wrap_width is not an integer!')

        # Create SSL context. According to the docs this will:
        # * load the system’s trusted CA certificates,
        # * enable certificate validation and hostname checking,
        # * try to choose reasonably secure protocol and cipher settings.
        # see:
        # https://docs.python.org/3/library/ssl.html#ssl-security
        self.context = ssl.create_default_context()

    def __send_unencrypted(self,
                           msg: EmailMessage) -> None:
        if self.server_port is not None:
            with smtplib.SMTP(self.server, self.server_port) as s:
                s.send_message(msg)
        else:
            with smtplib.SMTP(self.server) as s:
                s.send_message(msg)

    def __send_ssl(self,
                   msg: EmailMessage) -> None:
        with smtplib.SMTP_SSL(host=self.server,
                              port=self.server_port,
                              context=self.context) as s:
            s.login(self.username, self.passphrase)
            s.send_message(msg)

    def __send_starttls(self,
                        msg: EmailMessage) -> None:
        with smtplib.SMTP(self.server,
                          self.server_port) as s:
            s.starttls(context=self.context)
            s.login(self.username, self.passphrase)
            s.send_message(msg)

    def send_mail(self,
                  message_subject: str,
                  message_text: str,
                  overwrite_recipient: str | None = None) -> None:
        """Send an email.
           Sender and receiver were fixed with the constructor.
           With overwrite_receiver you change the recipient for this mail."""
        # pylint: disable=too-many-branches

        recipient: str = overwrite_recipient if overwrite_recipient else self.default_recipient
        if not userprovided.mail.is_email(recipient):
            raise ValueError('Recipient is not valid')

        if message_subject == '' or message_subject is None:
            raise err.MissingSubject(
                'Mails without subject will likely be classified as spam.')

        if message_text == '' or message_text is None:
            raise err.MissingMailContent('No mail content supplied.')

        wrap = textwrap.TextWrapper(width=self.wrap_width)

        # To preserve intentional linebreaks, the text is wrapped linewise.
        wrapped_text = ''
        for line in str.splitlines(message_text):
            wrapped_text += wrap.fill(line) + "\n"

        try:
            msg = EmailMessage()
            msg.set_content(wrapped_text)
            msg['Subject'] = message_subject
            msg['From'] = self.sender
            msg['To'] = recipient

            if self.encryption == 'off':
                self.__send_unencrypted(msg)
            elif self.encryption == 'ssl':
                self.__send_ssl(msg)
            else:
                self.__send_starttls(msg)
        except smtplib.SMTPAuthenticationError:
            logger.exception(
                'SMTP authentication failed: check username / passphrase.')
            raise
        except smtplib.SMTPSenderRefused:
            logger.exception('SMTP server refused sender.')
            raise
        except smtplib.SMTPRecipientsRefused:
            logger.exception('SMTP server refused recipient.')
            raise
        except smtplib.SMTPServerDisconnected:
            logger.exception('SMTP server unexpectedly disconnected.')
            raise
        except (smtplib.SMTPException, Exception):
            # Catch both SMTP-specific exceptions and general exceptions
            # (e.g., network errors, SSL errors) to ensure all failures are logged
            logger.exception('Problem sending mail!')
            raise

    def send_mail_to_admin(self,
                           message_subject: str,
                           message_text: str) -> None:
        """If a dictionary is used for recipient and if it contains an
           admin key: send an email to the corresponding address."""
        if not isinstance(self.recipient, dict) or 'admin' not in self.recipient:
            raise ValueError('Mail address for admin not set with init!')
        self.send_mail(
            message_subject,
            message_text,
            self.recipient['admin']
            )
