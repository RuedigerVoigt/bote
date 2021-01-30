#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automatic Tests for bote

To run these tests:
coverage run --source bote -m pytest tests.py
To generate a report afterwards.
coverage html
~~~~~~~~~~~~~~~~~~~~~
Source: https://github.com/RuedigerVoigt/bote
(c) 2020-2021 Rüdiger Voigt
Released under the Apache License 2.0
"""

import pytest
import bote


def test_send_mail():
    # False, but valid settings
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(mail_settings)
    # Missing subject line
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail('', 'random text')
    assert 'Mails need a subject line.' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail(None, 'random text')
    assert 'Mails need a subject line.' in str(excinfo.value)

    # Missing mail body
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail('random subject', '')
    assert 'No mail content supplied.' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail('random subject', None)
    assert 'No mail content supplied.' in str(excinfo.value)


def test_enforce_crypto():
    with pytest.raises(ValueError) as excinfo:
        external_but_no_encryption = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'off',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com'}
        mailer = bote.Mailer(external_but_no_encryption)
    assert 'Connection is not to localhost' in str(excinfo.value)


def test_invalid_in_combination():
    with pytest.raises(ValueError) as excinfo:
        external_but_no_port = {
            'server': 'smtp.example.com',
            'server_port': None,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com'}
        mailer = bote.Mailer(external_but_no_port)
    assert 'You must provide a port' in str(excinfo.value)


def test_invalid_parameters():
    with pytest.raises(ValueError) as excinfo:
        sender_is_not_email = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'not_an_email'}
        mailer = bote.Mailer(sender_is_not_email)
    assert 'sender is not a valid email!' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        recipient_is_not_email = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'not_an_email',
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(recipient_is_not_email)
    assert 'recipient is not a valid email!' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        port_out_of_range = {
            'server': 'smtp.example.com',
            'server_port': 999999999999,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'bar@example.com',
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(port_out_of_range)
    assert 'Port must be integer (0 to 65536)' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        unknown_encryption = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'start-tls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'bar@example.com',
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(unknown_encryption)
    assert 'Invalid value for the encryption parameter' in str(excinfo.value)


def test_recognize_localhost():
    localhost_as_string = {
        'server': 'localhost',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(localhost_as_string)
    assert mailer.is_local is True
    localhost_as_ipv4 = {
        'server': '127.0.0.1',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(localhost_as_ipv4)
    assert mailer.is_local is True
    localhost_as_ipv6short = {
        'server': '::1',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(localhost_as_ipv6short)
    assert mailer.is_local is True


def test_missing_required_parameters():
    with pytest.raises(ValueError) as excinfo:
        missing_recipient = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'sender': 'bar@example.com'}
        mailer = bote.Mailer(missing_recipient)
    assert 'Necessary key' in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        missing_sender = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com'}
        mailer = bote.Mailer(missing_sender)
    assert 'Necessary key' in str(excinfo.value)
