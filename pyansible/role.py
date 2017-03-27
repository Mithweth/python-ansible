import ansible.playbook.play
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.errors import AnsibleError, AnsibleParserError
import task
import os
import yaml


class Role(task.Task):
    def __init__(self, roles, inventory=None, host='localhost',
                 group=None, basedir=None, **options):
        self.roles = roles
        super(Role, self).__init__(
            roles, inventory, host,
            group, basedir, **options)

