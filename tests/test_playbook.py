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


class TestPlaybook(unittest.TestCase):
    def test_local_if_no_args(self):
        t = pyansible.Playbook('toto.yml')
        self.assertIn('inventory-file=localhost,', t.command)

    def test_no_playbook(self):
        with self.assertRaises(TypeError):
            pyansible.Playbook()

    def test_wrong_vault_file(self):
        ex = AnsibleFileNotFound if pyansible.version_info < (2, 5) else AnsibleError
        with self.assertRaises(ex):
            pyansible.Playbook('test.yml', vault_password_file='foobar')

    def test_no_ssh_key(self):
        t = pyansible.Playbook('test.yml')
        self.assertIsNone(t._tqm._options.private_key_file)
        self.assertIsNone(t.ssh_key)

    def test_ssh_key(self):
        t = pyansible.Playbook('test.yml')
        t.ssh_key = 'ssh.key'
        self.assertIn('ssh.key', t._tqm._options.private_key_file)
        self.assertIn('ssh.key', t.ssh_key)

    def test_no_callback(self):
        t = pyansible.Playbook('test.yml')
        self.assertIsNone(t._tqm._stdout_callback)
        self.assertIsNone(t.callback)

    def test_callback(self):
        t = pyansible.Playbook('test.yml')
        from ansible.plugins.callback.default import CallbackModule
        cb = CallbackModule()
        t.callback = cb
        self.assertEqual(cb, t._tqm._stdout_callback)
        self.assertEqual(cb, t.callback)

    def test_extra_vars(self):
        t = pyansible.Playbook('toto.yml', extra_vars={'toto':'tata'})
        self.assertIn('--extra-vars \'{"toto": "tata"}\'', t.command)

    def test_verbosity(self):
        t = pyansible.Playbook('toto.yml', verbosity=3)
        self.assertIn('-vvv', t.command)

    def test_check_mode(self):
        t = pyansible.Playbook('toto.yml', check=True)
        self.assertTrue(t._tqm._options.check)
        self.assertIn('--check', t.command)

    def test_tags(self):
        t = pyansible.Playbook('toto.yml', tags=['start', 'action'])
        self.assertEqual('start,action', t._tqm._options.tags)

    def test_run_host_file(self):
        t = pyansible.Playbook('toto.yml', inventory='test_host')
        self.assertIn('test_host', t._tqm._inventory.hosts)

    def test_run_hosts(self):
        t = pyansible.Playbook('toto.yml')
        self.assertEqual('localhost', str(t._tqm._inventory.list_hosts()[0]))

    def test_run_local_connection(self):
        t = pyansible.Playbook('toto.yml')
        self.assertEqual('local', t._tqm._options.connection)

    def test_run_remote_connection(self):
        t = pyansible.Playbook('toto.yml', inventory="192.168.0.1")
        self.assertEqual('smart', t._tqm._options.connection)

    def test_wrong_pb(self):
            msg = 'does not exist' if pyansible.version_info < (2, 5) else 'Could not find or access'
            t = pyansible.Playbook('toto.yml')
            self.assertFalse(t.run())
            self.assertIn(msg, t.runtime_errors)

    def test_run_mock_ok(self):
        m = mock.Mock()
        m.return_value = True
        m2 = mock.Mock()
        from ansible.playbook.play import Play
        m2.return_value.get_plays.return_value = [Play().load({'hosts':'localhost'})]
        with mock.patch('ansible.playbook.Playbook.load', m2, create=True):
            with mock.patch('ansible.executor.task_queue_manager.TaskQueueManager.run', m, create=True):
                t = pyansible.Playbook('toto.yml')
                self.assertTrue(t.run())
                self.assertIsNone(t.runtime_errors)

    def test_replay(self):
        m = mock.Mock()
        m.return_value = True
        m2 = mock.Mock()
        from ansible.playbook.play import Play
        m2.return_value.get_plays.return_value = [Play().load({'hosts':'localhost'})]
        with mock.patch('ansible.playbook.Playbook.load', m2, create=True):
            with mock.patch('ansible.executor.task_queue_manager.TaskQueueManager.run', m, create=True):
                t = pyansible.Playbook('toto.yml')
                self.assertTrue(t.run())
                self.assertIsNone(t.runtime_errors)
                self.assertTrue(t.run())
                self.assertIsNone(t.runtime_errors)

    def test_run_mock_ko(self):
        m = mock.Mock()
        m.side_effect = AnsibleError('Problem!')
        m2 = mock.Mock()
        from ansible.playbook.play import Play
        m2.return_value.get_plays.return_value = [Play().load({'hosts':'localhost'})]
        with mock.patch('ansible.playbook.Playbook.load', m2, create=True):
            with mock.patch('ansible.executor.task_queue_manager.TaskQueueManager.run', m, create=True):
                t = pyansible.Playbook('toto.yml')
                self.assertFalse(t.run())
                self.assertIsNotNone(t.runtime_errors)

    def test_pb_load(self):
        m = mock.Mock()
        m.side_effect = AnsibleError('Problem!')
        with mock.patch('ansible.playbook.Playbook.load', m):
            t = pyansible.Playbook('toto.yml')
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

