#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import mock
from ansible.errors import AnsibleError, AnsibleFileNotFound

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pyansible # noqa


class TestTask(unittest.TestCase):
    def test_no_tasks(self):
        with self.assertRaises(TypeError):
            pyansible.Task()

    def test_name(self):
        t = pyansible.Task({'command': 'ls'})
        self.assertEqual(t.name, 'tasks')

    def test_local(self):
        t = pyansible.Task({'command': 'ls'})
        self.assertEqual(t.play['connection'], 'local')
        self.assertEqual(t.play['hosts'], 'localhost')
        self.assertIn('tasks', t.play)

    def test_remote(self):
        t = pyansible.Task({'command': 'ls'}, host='192.168.0.1')
        self.assertEqual(t.play['connection'], 'smart')
        self.assertEqual(t.play['hosts'], 'all')
        self.assertIn('tasks', t.play)

    def test_wrong_vault_file(self):
        with self.assertRaises(AnsibleFileNotFound):
            pyansible.Task({'command': 'ls'}, vault_password_file='foobar')

    def test_extra_vars(self):
        t = pyansible.Task({'command': 'ls'}, extra_vars={'toto': 'tata'})
        self.assertIn('vars', t.play)
        self.assertEquals({'toto': 'tata'}, t.play['vars'])

    def test_no_ssh_key(self):
        t = pyansible.Task({'command': 'ls'})
        self.assertIsNone(t._tqm._options.private_key_file)

    def test_ssh_key(self):
        t = pyansible.Task({'command': 'ls'})
        t.ssh_key = 'ssh.key'
        self.assertIn('ssh.key', t._tqm._options.private_key_file)

    def test_run_ok(self):
        t = pyansible.Task([{'command': 'ls'},])
        self.assertTrue(t.run())
        self.assertIsNone(t.runtime_errors)

    def test_run_mock_ko(self):
        t = pyansible.Task({'command': 'ls'})
        t._tqm._stats.increment('failures', 'localhost')
        self.assertFalse(t.run())

if __name__ == '__main__':
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-s %(funcName)s:%(lineno)d %(message)s")

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)
    handler_console.setLevel(logging.DEBUG)
    logger.addHandler(handler_console)
    unittest.main()
