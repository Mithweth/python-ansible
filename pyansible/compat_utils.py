from collections import namedtuple
import os
import ansible.release
import subprocess
from ansible.errors import AnsibleFileNotFound, AnsibleError
version_info = namedtuple('version_info',
                          ['major', 'minor', 'micro', 'releaselevel'])(*[
                              int(n) for n in ansible.release.__version__.split('.')])

if version_info < (2, 0):
    raise ImportError('module for ansible 2.x only')


def add_host(inventory, group, host):
    if version_info < (2, 4):
        from ansible.inventory.host import Host
        from ansible.inventory.group import Group
        if group not in inventory.list_groups():
            inventory.add_group(Group(group))
        inventory.get_group(group).add_host(Host(host))
    else:
        if group not in inventory.list_groups():
            inventory.add_group(group)
        inventory.add_host(host, group)


def create_variable_manager(loader, host_file):
    if version_info < (2, 4):
        from ansible.vars import VariableManager
        from ansible.inventory import Inventory
        variable_manager = VariableManager()
        inventory = Inventory(loader=loader,
                              variable_manager=variable_manager,
                              host_list=host_file)
    else:
        from ansible.vars.manager import VariableManager
        from ansible.inventory.manager import InventoryManager
        variable_manager = VariableManager(loader)
        inventory = InventoryManager(loader=loader,
                                     sources=host_file)
    variable_manager.set_inventory(inventory)
    return variable_manager


def set_basedir(loader, basedir):
    if version_info < (2, 4):
        from ansible.plugins import module_utils_loader, module_loader
    else:
        from ansible.plugins.loader import module_utils_loader, module_loader
    module_loader.add_directory(os.path.join(basedir, 'library'))
    loader.set_basedir(basedir)
    module_utils_loader.add_directory(os.path.join(basedir, 'module_utils'))


def set_vault_password(loader, filename):
    if version_info < (2,4):
        this_path = os.path.realpath(os.path.expanduser(filename))
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

    else:
        from ansible.parsing.vault import get_file_vault_secret
        file_vault_secret = get_file_vault_secret(filename, loader=loader)
        file_vault_secret.load()
        loader.set_vault_secrets([('default', file_vault_secret)])
