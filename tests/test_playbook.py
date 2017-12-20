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
        with self.assertRaises(AnsibleFileNotFound):
            pyansible.Playbook('test.yml', vault_password_file='foobar')

    def test_no_ssh_key(self):
        t = pyansible.Playbook('test.yml')
        self.assertIsNone(t._tqm._options.private_key_file)

    def test_ssh_key(self):
        t = pyansible.Playbook('test.yml')
        t.set_ssh_key('ssh.key')
        self.assertIn('ssh.key', t._tqm._options.private_key_file)

    def test_tags(self):
        t = pyansible.Playbook('toto.yml', tags=['start', 'action'])
        self.assertEqual('start,action', t._tqm._options.tags)

    def test_run_host_file(self):
        t = pyansible.Playbook('toto.yml', inventory='test_host')
        self.assertIn('test_host', t._tqm._inventory.host_list)

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
            t = pyansible.Playbook('toto.yml')
            self.assertFalse(t.run())
            self.assertIn('does not exist', t.runtime_errors)

    def test_run_mock_ok(self):
        m = mock.Mock()
        m.return_value = True
        m2 = mock.Mock()
        m2.return_value.get_plays.return_value = [1, 2]
        with mock.patch(
                'ansible.playbook.Playbook.load',
                m2, create=True):
            with mock.patch(
                    'ansible.executor.task_queue_manager.TaskQueueManager.run',
                    m, create=True):
                t = pyansible.Playbook('toto.yml')
                self.assertTrue(t.run())
                self.assertIsNone(t.runtime_errors)

    def test_run_mock_ko(self):
        m = mock.Mock()
        m.side_effect = AnsibleError('Problem!')
        with mock.patch(
                'ansible.executor.task_queue_manager.TaskQueueManager.run',
                m,
                create=True):
            t = pyansible.Playbook('toto.yml')
            self.assertFalse(t.run())
            self.assertIsNotNone(t.runtime_errors)
