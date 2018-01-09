import compat_utils

from ansible.parsing.dataloader import DataLoader
from ansible.errors import AnsibleError, AnsibleParserError, AnsibleFileNotFound
from ansible.executor.task_queue_manager import TaskQueueManager
import ansible.constants as C
import os
import shutil


class Options(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                setattr(self, k, v)


class Play(object):
    def __init__(self, host_file, basedir=None, tags=None,
                 become_method='sudo', become='no', become_user='root',
                 check=False, forks=100, remote_user='root', verbosity=None,
                 extra_vars={}, vault_password_file=None, connection=None):
        self.succeeded_hosts = []
        self.failed_hosts = []
        if ',' not in host_file and not os.path.isfile(host_file):
            host_file += ','

        loader = DataLoader()

        if vault_password_file is not None:
            compat_utils.set_vault_password(loader, vault_password_file)

        variable_manager = compat_utils.create_variable_manager(loader, host_file)

        if extra_vars:
            variable_manager.extra_vars = extra_vars

        if isinstance(tags, list):
            tags = ','.join(tags)
        if connection is None:
            connection = 'local' if host_file == 'localhost,' else 'smart'
        if basedir:
            compat_utils.set_basedir(loader, basedir)

        options=Options(
            connection=connection,
            become_user=become_user,
            become_method=become_method,
            become=become,
            check=check,
            forks=forks,
            diff=False,
            tags=tags,
            remote_user=remote_user,
            verbosity=verbosity)
        options.private_key_file = None
        options.module_path = None
        self._tqm = TaskQueueManager(inventory=variable_manager._inventory,
                                     variable_manager=variable_manager,
                                     loader=loader,
                                     passwords=None,
                                     options=options)
        self.runtime_errors = None

    def __del__(self):
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    @property
    def ssh_key(self):
        return self._tqm._options.private_key_file

    @ssh_key.setter
    def ssh_key(self, key):
        self._tqm._options.private_key_file = os.path.abspath(
            os.path.expanduser(key))

    @property
    def callback(self):
        return self._tqm._stdout_callback

    @callback.setter
    def callback(self, _cb):
        self._tqm._stdout_callback = _cb

    def _play(self, play):
        self.runtime_errors = None
        used_hosts = self._tqm._inventory.get_hosts(play.hosts)
        if len(used_hosts) == 0:
              self._tqm.send_callback('v2_playbook_on_play_start', play)
              self._tqm.send_callback('v2_playbook_on_no_hosts_matched')
              return False
        try:
            self._tqm.run(play)
        except (AnsibleError, AnsibleParserError) as e:
            self.runtime_errors = e.message
            return False
        hosts = sorted(self._tqm._stats.processed.keys())
        for h in hosts:
            t = self._tqm._stats.summarize(h)
            if t['unreachable'] > 0 or t['failures'] > 0:
                if h not in self.failed_hosts:
                    self.failed_hosts.append(h)
                return False
            else:
                if h not in self.succeeded_hosts:
                    self.succeeded_hosts.append(h)
        return True
