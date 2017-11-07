from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.errors import AnsibleError, AnsibleParserError, AnsibleFileNotFound
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins import module_utils_loader
import os
import subprocess


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
            this_path = os.path.realpath(os.path.expanduser(vault_password_file))
            if not os.path.exists(this_path):
                raise AnsibleFileNotFound("The vault password file %s was not found" % this_path)

            if loader.is_executable(this_path):
                try:
                    p = subprocess.Popen(this_path, stdout=subprocess.PIPE)
                except OSError as e:
                    raise AnsibleError("Problem running vault password script %s." % (' '.join(this_path)))
                stdout, stderr = p.communicate()
                try:
                    loader.set_vault_password(stdout.strip('\r\n'))
                except TypeError:
                    loader.set_vault_password(stdout.decode('utf-8').strip('\r\n'))
            else:
                try:
                    f = open(this_path, "rb")
                    try:
                        loader.set_vault_password(f.read().strip())
                    except TypeError:
                        loader.set_vault_password(f.read().decode('utf-8').strip())
                    f.close()
                except (OSError, IOError) as e:
                    raise AnsibleError("Could not read vault password file %s: %s" % (this_path, e))

        if isinstance(tags, list):
            tags = ','.join(tags)
        if connection is None:
            connection = 'local' if host_file == 'localhost,' else 'smart'
        if basedir:
            module_path = os.path.join(basedir, 'library')
            loader.set_basedir(basedir)
            module_utils_loader._extra_dirs.append(os.path.join(basedir, 'module_utils'))
        else:
            module_path = None

        variable_manager = VariableManager()

        inventory = Inventory(loader=loader,
                              variable_manager=variable_manager,
                              host_list=host_file)
        if extra_vars:
            variable_manager.extra_vars = extra_vars
        variable_manager.set_inventory(inventory)

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
            verbosity=verbosity)
        options.module_path = module_path
        options.private_key_file = None
        self._tqm = TaskQueueManager(inventory=inventory,
                                     variable_manager=variable_manager,
                                     loader=loader,
                                     passwords=None,
                                     options=options)
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
