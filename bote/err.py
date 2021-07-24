#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bote: Custom Exceptions

Source: https://github.com/RuedigerVoigt/bote
(c) 2020-2021 Rüdiger Voigt:
Released under the Apache License 2.0
"""


class BoteException(Exception):
    "An exception speicific to bote occured"
    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        Exception.__init__(self, *args, **kwargs)


class UnencryptedRemoteConnection(BoteException):
    """Raised if you try to send via a remote machine, but
       do not encrypt the connection to it."""


class NotAnEmail(BoteException):
    """Raised if bote expects an email address, but the provided value
       is not a valid email address."""


class MissingSubject(BoteException, ValueError):
    "Raised if you try to send an email without subject line."


class MissingMailContent(BoteException, ValueError):
    "Raised if you try to send via an email without content."
