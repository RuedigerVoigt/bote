#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from bote import mail as bote


class BoteTest(unittest.TestCase):

    def setUp(self):

        # False, but valid settings
        self.mail_settings = {
            'server': 'smtp.example.com',
            'server_port': 587,
            'encryption': 'starttls',
            'username': 'exampleuser',
            'passphrase': 'example',
            'recipient': 'foo@example.com',
            'sender': 'bar@example.com'}

        self.mailer = bote.Mailer(self.mail_settings)

    def test_send_mail(self):

        # missing subject
        self.assertRaises(ValueError, self.mailer.send_mail,
                          '', 'messageText')
        self.assertRaises(ValueError, self.mailer.send_mail,
                          None, 'messageText')
        # missing mail text
        self.assertRaises(ValueError, self.mailer.send_mail,
                          'subject', '')
        self.assertRaises(ValueError, self.mailer.send_mail,
                          'subject', None)


if __name__ == "__main__":

    unittest.main()
