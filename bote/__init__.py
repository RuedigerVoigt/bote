"""A Python library to send email. Enforces encryption -
   if not sending via localhost."""

from bote.err import (
    BoteException,
    MissingMailContent,
    MissingSubject,
    NotAnEmail,
    UnencryptedRemoteConnection,
)
from bote.mailer import Mailer, __version__

NAME = "bote"
__author__ = "Rüdiger Voigt"

__all__ = [
    "NAME",
    "BoteException",
    "Mailer",
    "MissingMailContent",
    "MissingSubject",
    "NotAnEmail",
    "UnencryptedRemoteConnection",
    "__author__",
    "__version__",
]
