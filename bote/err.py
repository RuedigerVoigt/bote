"""
Bote: Custom Exceptions

Source: https://github.com/RuedigerVoigt/bote
(c) 2020-2025 Rüdiger Voigt and contributors
Released under the Apache License 2.0
"""


class BoteException(Exception):
    """Base class for all bote-specific exceptions."""
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        Exception.__init__(self, *args, **kwargs)


class UnencryptedRemoteConnection(BoteException):
    """Raised when sending via a remote server without encryption."""


class NotAnEmail(BoteException):
    """Raised when a value expected to be an email address is invalid."""


class MissingSubject(BoteException, ValueError):
    """Raised when an email is sent without a subject line."""


class MissingMailContent(BoteException, ValueError):
    """Raised when an email is sent without any content."""
