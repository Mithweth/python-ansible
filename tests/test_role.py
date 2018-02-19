#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import mock
from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.playbook.play import Play

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pyansible # noqa


class TestTask(unittest.TestCase):
    def test_no_roles(self):
        with self.assertRaises(TypeError):
            pyansible.Role()

    def test_name(self):
        t = pyansible.Role('test-role')
        self.assertEqual(t.name, 'roles')

    def test_local(self):
        t = pyansible.Role('test-role')
        self.assertEqual(t.play['connection'], 'local')
        self.assertEqual(t.play['hosts'], 'localhost')
        self.assertIn('roles', t.play)

    def test_remote(self):
        t = pyansible.Role('test-role', host='192.168.0.1')
        self.assertEqual(t.play['connection'], 'smart')
        self.assertEqual(t.play['hosts'], 'all')
        self.assertIn('roles', t.play)

    def test_wrong_vault_file(self):
        with self.assertRaises(AnsibleFileNotFound):
            pyansible.Role('test-role', vault_password_file='foobar')

    def test_no_ssh_key(self):
        t = pyansible.Role('test-role')
        self.assertIsNone(t._tqm._options.private_key_file)

    def test_ssh_key(self):
        t = pyansible.Role('test-role')
        t.ssh_key = 'ssh.key'
        self.assertIn('ssh.key', t._tqm._options.private_key_file)

    def test_wrong_module_path(self):
        t = pyansible.Role('test-role', basedir='wrong/path')
        self.assertFalse(t.run())
        self.assertIn("the role 'test-role' was not found in wrong/path/roles",
                      t.runtime_errors)

    def test_run_mock_no_hosts(self):
        m = mock.Mock()
        m2 = mock.Mock()
        from ansible.playbook.play import Play
        m.return_value = Play().load({'hosts':'toto'})
        m2.return_value = True
        with mock.patch(
                'ansible.playbook.play.Play.load',
                m, create=True):
            with mock.patch(
                    'ansible.executor.task_queue_manager.TaskQueueManager.run',
                    m2, create=True):
                t = pyansible.Role('test-role')
                self.assertFalse(t.run())
                self.assertIsNone(t.runtime_errors)

    def test_run_mock_ok(self):
        m = mock.Mock()
        m2 = mock.Mock()
        from ansible.playbook.play import Play
        m.return_value = Play().load({'hosts':'localhost'})
        m2.return_value = True
        with mock.patch('ansible.playbook.play.Play.load', m, create=True):
            with mock.patch('ansible.executor.task_queue_manager.TaskQueueManager.run', m2, create=True):
                t = pyansible.Role('test-role')
                self.assertTrue(t.run())
                self.assertIsNone(t.runtime_errors)

    def test_run_mock_ko(self):
        m = mock.Mock()
        m.side_effect = AnsibleError('Problem!')
        with mock.patch('ansible.executor.task_queue_manager.TaskQueueManager.run', m, create=True):
            t = pyansible.Role('test-role')
            self.assertFalse(t.run())
            self.assertIsNotNone(t.runtime_errors)

if __name__ == '__main__':
    import logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)-s %(funcName)s:%(lineno)d %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter)
    handler_console.setLevel(logging.DEBUG)
    logger.addHandler(handler_console)
    unittest.main()

