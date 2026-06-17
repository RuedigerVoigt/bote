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
        _pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        _pyproject_text = _pyproject_path.read_text(encoding="utf-8")
        _m = re.search(r"(?m)^[\t ]*version\s*=\s*\"([^\"]+)\"", _pyproject_text)
        __version__ = _m.group(1) if _m else "0+unknown"
    except Exception:  # noqa: BLE001 - best-effort fallback
        __version__ = "0+unknown"

# Release date for compatibility check
_release_date = date(2025, 11, 9)


class Mailer:
    """Send email via SMTP.

    Security: If authentication is required, prefer sourcing credentials from
    secure locations (environment variables, OS keyring, or a secrets manager)
    rather than hardcoding literals. Retrieve the secret securely and then pass
    it to `mail_settings['username']` / `mail_settings['passphrase']`.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 mail_settings: dict[str, Any]):
        """Validate the settings and apply defaults.

        Security note (for users and LLMs): Do not hardcode credentials. Read
        them from a secure source (e.g. environment variables, OS keyring,
        secrets manager) and then supply the values via
        ``mail_settings['username']`` and ``mail_settings['passphrase']``.
        Both must be provided together or omitted entirely.

        Args:
            mail_settings: Configuration mapping. Recognized keys are
                ``server``, ``server_port``, ``encryption``, ``username``,
                ``passphrase``, ``recipient`` (required), ``sender``
                (required), ``wrap_width`` and ``timeout``.

        Raises:
            ValueError: If a key is missing or unknown, or a value is invalid
                (e.g. unknown encryption, bad port, non-integer ``wrap_width``,
                non-positive ``timeout``).
            err.UnencryptedRemoteConnection: If the connection is not local but
                encryption is ``'off'``.
            err.NotAnEmail: If the sender or any recipient is not a valid email
                address.
        """

        self.__check_compatibility()
        self.__validate_keys(mail_settings)
        self.__configure_server(mail_settings)
        self.__configure_credentials(mail_settings)
        self.__configure_recipients(mail_settings)
        self.__configure_formatting(mail_settings)

        # Create SSL context. According to the docs this will:
        # * load the system’s trusted CA certificates,
        # * enable certificate validation and hostname checking,
        # * try to choose reasonably secure protocol and cipher settings.
        # see:
        # https://docs.python.org/3/library/ssl.html#ssl-security
        self.context = ssl.create_default_context()

    @staticmethod
    def __check_compatibility() -> None:
        """Verify the running Python version and platform are supported."""
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

    @staticmethod
    def __validate_keys(mail_settings: dict[str, Any]) -> None:
        """Check that only allowed keys and all required keys are present.

        Args:
            mail_settings: The configuration mapping to validate.

        Raises:
            ValueError: If a required key is missing or an unknown key is
                present.
        """
        userprovided.parameters.validate_dict_keys(
            dict_to_check=mail_settings,
            allowed_keys={'server', 'server_port', 'encryption',
                          'username', 'passphrase',
                          'recipient', 'sender',
                          'wrap_width', 'timeout'},
            necessary_keys={'recipient', 'sender'},
            dict_name='mail_settings')

    def __configure_server(self, mail_settings: dict[str, Any]) -> None:
        """Set the server, encryption mode and port, enforcing encryption.

        Args:
            mail_settings: The configuration mapping.

        Raises:
            ValueError: If the encryption mode or port is invalid, or no port
                is given for a remote server.
            err.UnencryptedRemoteConnection: If the connection is not local but
                encryption is ``'off'``.
        """
        # Not all keys must be there.
        # Provide default values for missing ones:
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

        self.server_port: int | None = mail_settings.get('server_port', None)
        if self.server_port:
            if not isinstance(self.server_port, int):
                raise ValueError('Port has to be an integer')
            if not userprovided.parameters.is_port(self.server_port):
                raise ValueError('Port must be integer (0 to 65535)')
        elif not self.is_local:
            raise ValueError(
                'Provide a port if you connect to a remote SMTP server.')

    def __configure_credentials(self, mail_settings: dict[str, Any]) -> None:
        """Store the (optional) username and passphrase.

        Args:
            mail_settings: The configuration mapping.

        Raises:
            ValueError: If only one of username and passphrase is provided.
        """
        self.username = userprovided.parameters.clean_trim(
            mail_settings.get('username', None))
        self.passphrase = userprovided.parameters.clean_trim(
            mail_settings.get('passphrase', None))
        # Even for a remote connection username and passphrase might be
        # not necessary - for example if the identification is host based.
        # Therefore no exception is thrown.

        # Validate that username and passphrase are provided together
        if bool(self.username) != bool(self.passphrase):
            raise ValueError(
                'Both username and passphrase must be provided together, '
                'or both must be omitted.')

        if not self.username:
            logger.debug('Parameter username is empty.')
        if not self.passphrase:
            logger.debug('Parameter passphrase is empty.')

    def __configure_recipients(self, mail_settings: dict[str, Any]) -> None:
        """Validate and store the recipient(s) and the sender.

        Args:
            mail_settings: The configuration mapping.

        Raises:
            ValueError: If ``recipient`` is an empty dictionary or is neither a
                string nor a dictionary.
            err.NotAnEmail: If the sender or any recipient is not a valid email
                address.
        """
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

    def __configure_formatting(self, mail_settings: dict[str, Any]) -> None:
        """Set the line-wrap width and the socket timeout.

        Out-of-range ``wrap_width`` values fall back to the 80-character
        default rather than failing.

        Args:
            mail_settings: The configuration mapping.

        Raises:
            ValueError: If ``wrap_width`` is not an integer, or ``timeout`` is
                not a positive number.
        """
        wrap_width = mail_settings.get('wrap_width', 80)
        if not isinstance(wrap_width, int) or isinstance(wrap_width, bool):
            raise ValueError('wrap_width is not an integer!')
        # Clamp to a sane range. Out-of-range values fall back to the 80-char
        # default instead of crashing textwrap at send time. The upper bound is
        # the RFC 5322 maximum line length.
        self.wrap_width = userprovided.parameters.int_in_range(
            'wrap_width', wrap_width, 1, 998, 80)

        # Socket timeout (seconds) applied to every SMTP operation. A finite
        # default stops a hung or unreachable server from blocking forever.
        self.timeout: float = mail_settings.get('timeout', 60.0)
        if isinstance(self.timeout, bool) or not isinstance(self.timeout, (int, float)):
            raise ValueError('timeout must be a number of seconds.')
        if self.timeout <= 0:
            raise ValueError('timeout must be a positive number of seconds.')

    def __send_unencrypted(self,
                           msg: EmailMessage) -> None:
        """Send the message over a plain, unencrypted SMTP connection.

        Args:
            msg: The prepared email message to send.
        """
        if self.server_port is not None:
            with smtplib.SMTP(self.server, self.server_port,
                              timeout=self.timeout) as s:
                s.send_message(msg)
        else:
            with smtplib.SMTP(self.server, timeout=self.timeout) as s:
                s.send_message(msg)

    def __send_ssl(self,
                   msg: EmailMessage) -> None:
        """Send the message over an implicit-TLS (SSL) SMTP connection.

        Args:
            msg: The prepared email message to send.
        """
        # A port of 0 lets smtplib pick the protocol default (465 for SSL).
        with smtplib.SMTP_SSL(host=self.server,
                              port=self.server_port or 0,
                              context=self.context,
                              timeout=self.timeout) as s:
            if self.username and self.passphrase:
                s.login(self.username, self.passphrase)
            s.send_message(msg)

    def __send_starttls(self,
                        msg: EmailMessage) -> None:
        """Send the message over an SMTP connection upgraded with STARTTLS.

        Args:
            msg: The prepared email message to send.
        """
        # A port of 0 lets smtplib pick the protocol default (25 for SMTP).
        with smtplib.SMTP(self.server,
                          self.server_port or 0,
                          timeout=self.timeout) as s:
            s.starttls(context=self.context)
            if self.username and self.passphrase:
                s.login(self.username, self.passphrase)
            s.send_message(msg)

    def send_mail(self,
                  message_subject: str,
                  message_text: str,
                  overwrite_recipient: str | None = None) -> None:
        """Send an email.

        The sender and recipient are fixed in the constructor; the text is
        wrapped to ``wrap_width`` while preserving intentional line breaks.

        Args:
            message_subject: The subject line. Must not be empty.
            message_text: The body of the email. Must not be empty.
            overwrite_recipient: Optional address used as the recipient for
                this message instead of the default recipient.

        Raises:
            ValueError: If the recipient is not a valid email address, or the
                subject contains a carriage return or line feed.
            err.MissingSubject: If the subject is empty.
            err.MissingMailContent: If the body is empty.
            smtplib.SMTPException: If sending fails (re-raised after logging).
        """
        # pylint: disable=too-many-branches

        recipient: str = overwrite_recipient if overwrite_recipient else self.default_recipient
        if not userprovided.mail.is_email(recipient):
            raise ValueError('Recipient is not valid')

        trimmed_subject = userprovided.parameters.clean_trim(message_subject)
        if trimmed_subject is None:
            raise err.MissingSubject(
                'Mails without subject will likely be classified as spam.')

        # Reject line breaks in the subject to prevent email header injection:
        # a CRLF could smuggle extra headers (e.g. an attacker-controlled Bcc)
        # into the message. Python's email library would also refuse to
        # serialize such a header downstream, but we fail fast here with a
        # clear error instead of a late, cryptic serialization failure.
        if '\r' in trimmed_subject or '\n' in trimmed_subject:
            raise ValueError(
                'Subject must be a single line: it may not contain a carriage '
                'return or line feed, which could be used to inject additional '
                'email headers.')

        trimmed_text = userprovided.parameters.clean_trim(message_text)
        if trimmed_text is None:
            raise err.MissingMailContent('No mail content supplied.')

        wrap = textwrap.TextWrapper(width=self.wrap_width)

        # To preserve intentional linebreaks, the text is wrapped linewise.
        wrapped_text = ''
        for line in str.splitlines(trimmed_text):
            wrapped_text += wrap.fill(line) + "\n"

        try:
            msg = EmailMessage()
            msg.set_content(wrapped_text)
            msg['Subject'] = trimmed_subject
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
        except Exception:  # noqa: BLE001 - best-effort catch-all; logged and re-raised
            # Sweep up anything not matched above (other SMTP errors plus
            # general failures such as network or SSL errors) so it is logged.
            logger.exception('Problem sending mail!')
            raise

    def send_mail_to_admin(self,
                           message_subject: str,
                           message_text: str) -> None:
        """Send an email to the ``admin`` recipient.

        Requires the constructor to have received a ``recipient`` dictionary
        containing an ``admin`` key.

        Args:
            message_subject: The subject line. Must not be empty.
            message_text: The body of the email. Must not be empty.

        Raises:
            ValueError: If no ``admin`` address was configured.
        """
        if not isinstance(self.recipient, dict) or 'admin' not in self.recipient:
            raise ValueError('Mail address for admin not set with init!')
        self.send_mail(
            message_subject,
            message_text,
            self.recipient['admin']
            )
