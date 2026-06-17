#!/usr/bin/env python3

"""
Automatic Tests for bote
~~~~~~~~~~~~~~~~~~~~~
Source: https://github.com/RuedigerVoigt/bote
(c) 2020-2025 Rüdiger Voigt and contributors
Released under the Apache License 2.0
"""
import logging
import smtplib
from unittest.mock import patch


import pytest
import bote


# #############################################################################
# TEST MISSING AND INVALID PARAMETERS
# #############################################################################


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
        _ = bote.Mailer(missing_sender)
    assert 'Necessary key' in str(excinfo.value)


def test_whitespace_only_credentials():
    # Whitespace-only username with real passphrase should raise error
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': '   ',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)

    # Whitespace-only passphrase with real username should raise error
    mail_settings['username'] = 'exampleuser'
    mail_settings['passphrase'] = '   '
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)


def test_missing_username():
    # username set to None but passphrase provided should raise error
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': None,
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)

    # username key missing but passphrase provided should raise error
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)


def test_missing_passphrase():
    # passphrase set to None but username provided should raise error
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': None,
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)

    # passphrase key missing but username provided should raise error
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'Both username and passphrase must be provided together' in str(excinfo.value)


def test_logging_missing_default_key(caplog):
    caplog.set_level(logging.INFO)
    recipient_dict_without_default_key = {
        'server': 'smtp.example.com',
        'server_port': 123,
        'encryption': 'ssl',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': {'foo': 'bar@example.com'},
        'sender': 'foo@example.com'}
    _ = bote.Mailer(recipient_dict_without_default_key)
    assert "No default key" in caplog.text


def test_recipient_dict_invalid_value_email_format():
    # Invalid email address in recipient dictionary should raise NotAnEmail
    with pytest.raises(bote.err.NotAnEmail) as excinfo:
        settings = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': {'default': 'foo@example.com', 'admin': 'not_an_email'},
            'sender': 'bar@example.com',
        }
        _ = bote.Mailer(settings)
    assert 'recipient is not a valid email!' in str(excinfo.value)


def test_recipient_dict_invalid_value_type():
    # Non-string value in recipient dictionary should raise NotAnEmail
    with pytest.raises(bote.err.NotAnEmail) as excinfo:
        settings = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': {'default': 'foo@example.com', 'admin': 123},
            'sender': 'bar@example.com',
        }
        _ = bote.Mailer(settings)
    assert 'recipient is not a valid email!' in str(excinfo.value)


def test_invalid_parameters():
    with pytest.raises(bote.err.NotAnEmail) as excinfo:
        sender_is_not_email = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'not_an_email'}
        _ = bote.Mailer(sender_is_not_email)
    assert 'sender is not a valid email!' in str(excinfo.value)
    with pytest.raises(bote.err.NotAnEmail) as excinfo:
        recipient_is_not_email = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'not_an_email',
            'sender': 'foo@example.com'}
        _ = bote.Mailer(recipient_is_not_email)
    assert 'recipient is not a valid email!' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        recipient_is_empty_dict = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': dict(),
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(recipient_is_empty_dict)
    assert 'Dictionary recipient is empty' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        recipient_neither_str_nor_dict = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 1,
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(recipient_neither_str_nor_dict)
    assert 'must be' in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        port_not_int = {
            'server': 'smtp.example.com',
            'server_port': 'foo',
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'bar@example.com',
            'sender': 'foo@example.com'}
        mailer = bote.Mailer(port_not_int)
    assert 'Port has to be an integer' in str(excinfo.value)

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
    assert 'Port must be integer (0 to 65535)' in str(excinfo.value)

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

    with pytest.raises(ValueError) as excinfo:
        wrap_width_not_integer = {
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com',
            'wrap_width': 'not_an_integer'}
        mailer = bote.Mailer(wrap_width_not_integer)
    assert 'wrap_width is not an integer!' in str(excinfo.value)


def test_wrap_width_out_of_range_falls_back_to_default():
    # A wrap_width outside the allowed range falls back to the 80-char default
    # instead of reaching textwrap and raising at send time.
    for invalid_width in (0, -5, 5000):
        mailer = bote.Mailer({
            'server': 'smtp.example.com',
            'server_port': 123,
            'encryption': 'ssl',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com',
            'wrap_width': invalid_width})
        assert mailer.wrap_width == 80


# #############################################################################
# TEST PARAMETERS WITH CONTRADICTIONS
# #############################################################################


def test_invalid_in_combination():
    with pytest.raises(ValueError) as excinfo:
        external_but_no_port = {
            'server': 'smtp.example.com',
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com'}
        _ = bote.Mailer(external_but_no_port)
    assert 'Provide a port' in str(excinfo.value)

# #############################################################################
# TEST SENDING MAIL
# #############################################################################


def test_send_mail(mocker):
    # False, but 'valid' settings
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
    with pytest.raises(bote.err.MissingSubject) as excinfo:
        mailer.send_mail('', 'random text')
    assert 'classified as spam' in str(excinfo.value)
    with pytest.raises(bote.err.MissingSubject) as excinfo:
        mailer.send_mail(None, 'random text')
    assert 'classified as spam' in str(excinfo.value)

    # Missing mail body
    with pytest.raises(bote.err.MissingMailContent) as excinfo:
        mailer.send_mail('random subject', '')
    assert 'No mail content supplied.' in str(excinfo.value)
    with pytest.raises(bote.err.MissingMailContent) as excinfo:
        mailer.send_mail('random subject', None)
    assert 'No mail content supplied.' in str(excinfo.value)

    # Whitespace-only subject
    with pytest.raises(bote.err.MissingSubject) as excinfo:
        mailer.send_mail('   ', 'random text')
    assert 'classified as spam' in str(excinfo.value)

    # Whitespace-only body
    with pytest.raises(bote.err.MissingMailContent) as excinfo:
        mailer.send_mail('random subject', '   ')
    assert 'No mail content supplied.' in str(excinfo.value)

    # ############### PATCH smtplib ##################
    # as we do not want to actually send an email
    mocker.patch('smtplib.SMTP')
    # send_mail: standard
    mailer.send_mail('random subject', 'random content')
    # Subject/body with surrounding whitespace should be trimmed and sent
    mailer.send_mail('  trimmed subject  ', '  trimmed body  ')
    # send_mail: overwrite recipient
    mailer.send_mail('random subject', 'random content', 'foo@example.com')
    # overwrite recipient with invalid value
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail('random subject', 'random content', 'not_valid')
    assert 'Recipient is not valid' in str(excinfo.value)
    # switch OFF encryption and switch to localhost
    mail_settings['encryption'] = 'off'
    mail_settings['server'] = 'localhost'
    mailer = bote.Mailer(mail_settings)
    mailer.send_mail('random subject', 'random content')
    # Switch to SSL encryption and not localhost
    ssl_mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 465,
        'encryption': 'ssl',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    ssl_mailer = bote.Mailer(ssl_mail_settings)
    mock_ssl = mocker.patch('smtplib.SMTP_SSL')
    ssl_mailer.send_mail('random subject', 'random content')
    # Verify SSL path was used
    assert mock_ssl.call_count == 1


def test_unencrypted_uses_custom_port(mocker):
    # Ensure that when encryption is off and a port is set, SMTP is called with that port
    mail_settings = {
        'server': 'localhost',
        'server_port': 2525,
        'encryption': 'off',
        'username': None,
        'passphrase': None,
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com',
    }
    mailer = bote.Mailer(mail_settings)
    mock_smtp = mocker.patch('smtplib.SMTP')
    mailer.send_mail('subject', 'body')
    # Called once with server and custom port
    assert mock_smtp.call_count == 1
    args, kwargs = mock_smtp.call_args
    assert args[:2] == ('localhost', 2525)


def test_unencrypted_without_port_uses_default_call(mocker):
    # Without a server_port, SMTP should be called with only the server argument
    mail_settings = {
        'server': 'localhost',
        'encryption': 'off',
        'username': None,
        'passphrase': None,
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com',
    }
    mailer = bote.Mailer(mail_settings)
    mock_smtp = mocker.patch('smtplib.SMTP')
    mailer.send_mail('subject', 'body')
    assert mock_smtp.call_count == 1
    args, kwargs = mock_smtp.call_args
    assert args == ('localhost',)


def test_send_mail_to_admin(mocker):
    # False, but 'valid' settings
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': {
            'default': 'foo@example.com',
            'admin': 'admin@example.com'},
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(mail_settings)
    # ############### PATCH smtplib ##################
    # as we do not want to actually send an email
    mocker.patch('smtplib.SMTP')
    # send_mail: standard
    mailer.send_mail_to_admin('random subject', 'random content')


def test_send_mail_to_admin_missing_admin():
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': {
            'default': 'foo@example.com'},
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(mail_settings)
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail_to_admin('random subject', 'random content')


def test_send_mail_to_admin_no_dict():
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(mail_settings)
    with pytest.raises(ValueError) as excinfo:
        mailer.send_mail_to_admin('random subject', 'random content')


# #############################################################################
# TEST CRYPTO ENFORCEMENT
# #############################################################################


def test_recognize_localhost():
    localhost_as_string = {
        'server': 'localhost',
        'server_port': 587,
        'encryption': 'starttls',
        'username': None,
        'passphrase': None,
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


def test_enforce_crypto():
    with pytest.raises(bote.err.UnencryptedRemoteConnection) as excinfo:
        external_but_no_encryption = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'off',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com'}
        _ = bote.Mailer(external_but_no_encryption)
    assert 'Connection is not local' in str(excinfo.value)


# #############################################################################
# TEST SMTLIB EXCEPTIONS
# #############################################################################

# some smtplib exceptions need parameters to be called, see:
# https://github.com/python/cpython/blob/main/Lib/smtplib.py

false_but_valid_mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}


def test_send_mail_AUTH_FAILURE(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=smtplib.SMTPAuthenticationError(123, 'foo')):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(smtplib.SMTPAuthenticationError):
            mailer.send_mail('random subject', 'random content')
        assert "SMTP authentication failed" in caplog.text


def test_send_mail_SENDER_REFUSED(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=smtplib.SMTPSenderRefused(123, 'foo', 'foo')):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(smtplib.SMTPSenderRefused):
            mailer.send_mail('random subject', 'random content')
        assert "SMTP server refused sender" in caplog.text


def test_send_mail_RECIPIENT_REFUSED(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=smtplib.SMTPRecipientsRefused(dict())):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(smtplib.SMTPRecipientsRefused):
            mailer.send_mail('random subject', 'random content')
        assert "SMTP server refused recipient" in caplog.text


def test_send_mail_DISCONNECT(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=smtplib.SMTPServerDisconnected):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(smtplib.SMTPServerDisconnected):
            mailer.send_mail('random subject', 'random content')
        assert "SMTP server unexpectedly disconnected" in caplog.text


def test_send_mail_GENERIC_SMTP(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=smtplib.SMTPException):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(smtplib.SMTPException):
            mailer.send_mail('random subject', 'random content')
        assert "Problem sending mail" in caplog.text


def test_send_mail_GENERIC(caplog):
    with patch('bote.Mailer._Mailer__send_starttls',
               side_effect=Exception):
        mailer = bote.Mailer(false_but_valid_mail_settings)
        with pytest.raises(Exception):
            mailer.send_mail('random subject', 'random content')
        assert "Problem sending mail" in caplog.text


# #############################################################################
# TEST TIMEOUT
# #############################################################################


def test_invalid_timeout_type():
    # A non-numeric timeout should raise ValueError at initialization
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com',
        'timeout': 'soon'}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'timeout must be a number' in str(excinfo.value)


def test_invalid_timeout_value():
    # A non-positive timeout should raise ValueError at initialization
    mail_settings = {
        'server': 'smtp.example.com',
        'server_port': 587,
        'encryption': 'starttls',
        'username': 'exampleuser',
        'passphrase': 'example',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com',
        'timeout': 0}
    with pytest.raises(ValueError) as excinfo:
        bote.Mailer(mail_settings)
    assert 'positive' in str(excinfo.value)


def test_timeout_passed_to_smtp(mocker):
    # A custom timeout must be forwarded to smtplib
    mail_settings = {
        'server': 'localhost',
        'server_port': 2525,
        'encryption': 'off',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com',
        'timeout': 12.5}
    mailer = bote.Mailer(mail_settings)
    mock_smtp = mocker.patch('smtplib.SMTP')
    mailer.send_mail('subject', 'body')
    _, kwargs = mock_smtp.call_args
    assert kwargs.get('timeout') == 12.5


def test_default_timeout_applied(mocker):
    # Without an explicit timeout, the finite default is forwarded
    mail_settings = {
        'server': 'localhost',
        'encryption': 'off',
        'recipient': 'foo@example.com',
        'sender': 'bar@example.com'}
    mailer = bote.Mailer(mail_settings)
    assert mailer.timeout == 60.0
    mock_smtp = mocker.patch('smtplib.SMTP')
    mailer.send_mail('subject', 'body')
    _, kwargs = mock_smtp.call_args
    assert kwargs.get('timeout') == 60.0
