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
        self._tqm = TaskQueueManager(
                    inventory=inventory,
                    variable_manager=variable_manager,
                    loader=loader,
                    options=options,
                    passwords=passwords
                )

        self.errors = None

    def set_ssh_key(key):
        """blabla cle"""
        self._tqm._options.private_key_file = os.path.abspath(os.path.expanduser(key))

    def set_vault_password_file(filename):
        self._tqm._loader.set_vault_password(filename)

    def set_callback(callback):
        self._tqm._stdout_callback = callback
        
    def _play(self, play):
        try:
            self._tqm.run(play)
        except (AnsibleError, AnsibleParserError) as e:
            self.errors = e.message
            return False
        return True
