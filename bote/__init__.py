"""A Python library to send email. Enforces encryption -
   if not sending via localhost."""

from bote.mailer import Mailer, __version__
from bote.err import (
    BoteException,
    UnencryptedRemoteConnection,
    NotAnEmail,
    MissingSubject,
    MissingMailContent,
)

NAME = "bote"
__author__ = "Rüdiger Voigt"

__all__ = [
    "Mailer",
    "BoteException",
    "UnencryptedRemoteConnection",
    "NotAnEmail",
    "MissingSubject",
    "MissingMailContent",
    "NAME",
    "__version__",
    "__author__",
]
