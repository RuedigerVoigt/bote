#!/usr/bin/env python3
# -*- coding: utf-8 -*-

u""" Send email """

from email.message import EmailMessage
import logging
import smtplib
import ssl
import textwrap
from typing import Optional

import userprovided  # sister-project


class Mailer:
    u""" Class of bote to send mail """

    def __init__(self,
                 mail_settings: dict):
        u"""Check the mail settings for plausibility and set
            missing values to their default. """

        try:
            # Check whether it is a dict and if there are unknown keys:
            known_mail_keys = ('server',
                               'server_port',
                               'encryption',
                               'username',
                               'passphrase',
                               'recipient',
                               'sender')
            found_keys = mail_settings.keys()
            for key in found_keys:
                if key not in known_mail_keys:
                    raise ValueError('Unknown key in mail_settings: %s', key)
        except AttributeError:
            raise AttributeError('mail_settings must be a dictionary!')

        # Not all keys must be there. defaultdict lets us provide
        # default values for those missing!

        self.server: str = mail_settings.get('server', 'localhost')
        self.is_local = False
        if self.server in ('localhost', '127.0.0.1', '::1'):
            self.is_local = True

        # Encryption defaults to 'off' because the default for server
        # is localhost.
        self.encryption: str = mail_settings.get('encryption', 'off')
        # There are three valid values:
        if self.encryption not in ('off', 'starttls', 'ssl'):
            raise ValueError('Invalid value for the encryption parameter!')
        # Enforce some sort of encryption if the connection
        # is not to localhost:
        if not self.is_local and self.encryption == 'off':
            raise ValueError('Connection is not to localhost, ' +
                             'but an encryption method is not set!')

        self.server_port = mail_settings.get('server_port', None)
        if self.server_port:
            if not userprovided.port.port_in_range(self.server_port):
                raise ValueError('Port must be integer (0 to 65536)')
        if self.is_local and not self.server_port:
            raise ValueError('You need to provide a port if you connect ' +
                             'to a remote SMTP server.')

        self.username = mail_settings.get('username', None)
        self.passphrase = mail_settings.get('passphrase', None)

        self.recipient = mail_settings.get('recipient', None)
        if self.recipient:
            if not userprovided.mail.is_email(self.recipient):
                raise ValueError('recipient is not a valid email!')
        else:
            raise ValueError('Missing recipient in mail_settings!')

        self.sender = mail_settings.get('sender', None)
        if self.sender:
            if not userprovided.mail.is_email(self.sender):
                raise ValueError('sender is not a valid email!')
        else:
            raise ValueError('Missing sender in mail_settings!')
        # Create SSL context. According to the docs this will:
        # * load the system’s trusted CA certificates,
        # * enable certificate validation and hostname checking,
        # * try to choose reasonably secure protocol and cipher settings.
        # see:
        # https://docs.python.org/3/library/ssl.html#ssl-security
        self.context = ssl.create_default_context()

    def send_mail(self,
                  message_subject: str,
                  message_text: str,
                  overwrite_recipient: Optional[str] = None):
        u"""Send an email. Sender and receiver were fixed
            with the constructor. With the overwrite_receiver
            parameter you can change the recipient once."""

        recipient = self.recipient
        if overwrite_recipient:
            if userprovided.mail.is_email(overwrite_recipient):
                recipient = overwrite_recipient
                logging.debug('Overwritten mail recipient for this mail')
            else:
                raise ValueError('Invalid value for overwrite_recipient')

        if message_subject == '' or message_subject is None:
            raise ValueError('Mails need a subject line. Otherwise they' +
                             'most likely will be classified as spam.')

        if message_text == '' or message_text is None:
            raise ValueError('No mail content supplied.')

        wrap = textwrap.TextWrapper(width=80)

        # To preserve intentional linebreaks, the text is
        # wrapped linewise.
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
                s = smtplib.SMTP(self.server)
                s.send_message(msg)
                s.quit()
            elif self.encryption == 'ssl':
                with smtplib.SMTP_SSL(self.server,
                                      self.server_port,
                                      context=self.context) as s:
                    s.login(self.username, self.passphrase)
                    s.send_message(msg)
            else:
                # i.e. starttls
                with smtplib.SMTP(self.server,
                                  self.server_port) as s:
                    s.starttls(context=self.context)
                    s.login(self.username, self.passphrase)
                    s.send_message(msg)

        except smtplib.SMTPAuthenticationError:
            logging.exception('SMTP authentication failed. ' +
                              'Please check username / passphrase.')
        except Exception:
            logging.exception('Problem sending Mail!', exc_info=True)
            raise
        return
