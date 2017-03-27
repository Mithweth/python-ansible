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
        self.assertEqual(t.name(), 'tasks')

    def test_local(self):
        t = pyansible.Task({'command': 'ls'})
        self.assertEqual(t.get_play()['connection'], 'local')
        self.assertEqual(t.get_play()['hosts'], 'localhost')
        self.assertIn('tasks', t.get_play())

    def test_remote(self):
        t = pyansible.Task({'command': 'ls'}, host='192.168.0.1')
        self.assertEqual(t.get_play()['connection'], 'smart')
        self.assertEqual(t.get_play()['hosts'], 'all')
        self.assertIn('tasks', t.get_play())

    def test_wrong_vault_file(self):
        with self.assertRaises(AnsibleFileNotFound):
            pyansible.Task({'command': 'ls'}, vault_password_file='foobar')

    def test_no_ssh_key(self):
        t=pyansible.Task({'command': 'ls'})
        self.assertIsNone(t._tqm._options.private_key_file)

    def test_ssh_key(self):
        t=pyansible.Task({'command': 'ls'})
        t.set_ssh_key('ssh.key')
        self.assertIn('ssh.key', t._tqm._options.private_key_file)

    def test_run_mock_ok(self):
        m = mock.Mock()
        m.return_value = True
        with mock.patch(
                'ansible.executor.task_queue_manager.TaskQueueManager.run',
                m,
                create=True):
            t = pyansible.Task({'command': 'ls'})
            self.assertTrue(t.run())
            self.assertIsNone(t.runtime_errors)

    def test_run_mock_ko(self):
        m = mock.Mock()
        m.side_effect = AnsibleError('Problem!')
        with mock.patch(
                'ansible.executor.task_queue_manager.TaskQueueManager.run',
                m,
                create=True):
            t = pyansible.Task({'command': 'ls'})
            self.assertFalse(t.run())
            self.assertIsNotNone(t.runtime_errors)
