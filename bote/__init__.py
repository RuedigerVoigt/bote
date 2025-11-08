"""A Python library to send email. Enforces encryption -
   if not sending via localhost."""

from bote.__main__ import Mailer
from bote import _version

NAME = "bote"
__version__ = f"{_version.__version__}"
__author__ = "Rüdiger Voigt"
