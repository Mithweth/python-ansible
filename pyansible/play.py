from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.executor.task_queue_manager import TaskQueueManager
import os


class Options(object):
    def __init__(self, become=None, become_method=None, become_user=None,
                 check=None, connection=None, forks=None, module_path=None,
                 private_key_file=None, remote_user=None, tags=None,
                 skip_tags=None, timeout=None, verbosity=None):
        self.become_method = become_method
        self.become = become
        self.become_user = become_user
        self.check = check
        self.connection = connection
        self.forks = forks
        self.module_path = module_path
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.skip_tags = skip_tags
        self.tags = tags
        self.timeout = timeout
        self.verbosity = verbosity


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
            loader.read_vault_password_file(vault_password_file)

        if isinstance(tags, list):
            tags = ','.join(tags)
        if connection is None:
            connection = 'local' if host_file == 'localhost,' else 'smart'
        if basedir:
            module_path = basedir + os.sep + 'library'
            loader.set_basedir(basedir)
        else:
            module_path = None

        variable_manager = VariableManager()

        inventory = Inventory(loader=loader,
                              variable_manager=variable_manager,
                              host_list=host_file)
        if extra_vars:
            variable_manager.extra_vars = extra_vars
        variable_manager.set_inventory(inventory)

        self._tqm = TaskQueueManager(inventory=inventory,
                                     variable_manager=variable_manager,
                                     loader=loader,
                                     passwords=None,
                                     options=Options(
                                         connection=connection,
                                         module_path=module_path,
                                         become_user=become_user,
                                         become_method=become_method,
                                         become=become,
                                         check=check,
                                         forks=forks,
                                         tags=tags,
                                         remote_user=remote_user,
                                         verbosity=verbosity))
        self.runtime_errors = None

    def set_ssh_key(self, key):
        self._tqm._options.private_key_file = os.path.abspath(
            os.path.expanduser(key))

    def set_callback(self, callback):
        self._tqm._stdout_callback = callback

    def _play(self, play):
        self.runtime_errors = None
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
