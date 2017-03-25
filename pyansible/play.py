from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.executor.task_queue_manager import TaskQueueManager
import options
import os

class Play(object):
    def __init__(self, inventory, host, basedir):
        """Creation du tqm"""
        self._tqm = None
        self.__ssh_key_file = None
        self.errors = None
        self.callback = None

    def __del__(self):
        if self.__ssh_key_file is not None:
           if os.path.isfile(self.__ssh_key_file):
              os.remove(self.__ssh_key_file)

    def set_ssh_key(key):
        """blabla cle"""
        self._tqm._variable_manager.extra_vars['ansible_private_ssh_key_file'] = key
        self.__ssh_key_file = key

    def set_vault_password_file(filename):
        self._tqm._loader.set_vault_password(filename)

    def _play(self, play):
        try:
            self._tqm.run(play)
        except (AnsibleError, AnsibleParserError) as e:
            self.errors = e.message
            return False
        return True
