import ansible.playbook.play
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.errors import AnsibleError, AnsibleParserError
from . import play
import os
import yaml


class Task(play.Play):
    def __init__(self, tasks, inventory=None, host='localhost',
                 group=None, basedir=None, **options):
        self.tasks = tasks
        if inventory is None:
            inventory = host
        if host == 'localhost':
            group = 'localhost'
        elif not group:
            group = 'all'
        self.group = group
        if 'connection' not in options:
            options['connection'] = ('local'
                                     if group == 'localhost'
                                     else 'smart')
        super(Task, self).__init__(
            inventory,
            basedir,
            **options)
        if os.path.isfile(inventory):
            if group not in self._tqm._inventory.list_groups():
                new_group = Group(group)
                self._tqm._inventory.add_group(new_group)
            self._tqm._inventory.get_group(
                group).add_host(Host(host))

    def get_play(self, readable=False, gather_facts='no'):
        actions = ([self.tasks]
                   if isinstance(self.tasks, str)
                   else list(self.tasks))
        play = {
            'hosts': self.group,
            'gather_facts': gather_facts,
            self.name(): actions
        }
        if len(self._tqm._variable_manager.extra_vars) > 0:
            play['vars'] = self._tqm._variable_manager.extra_vars
        for key in ('become_method', 'become_user',
                    'become', 'remote_user', 'connection'):
            if self._tqm._options.__dict__[key]:
                play[key] = self._tqm._options.__dict__[key]
        if readable:
            return yaml.dump(play, default_flow_style=False)
        else:
            return play

    def name(self):
        return self.__class__.__name__.lower() + 's'

    def run(self, gather_facts='no'):
        self._tqm.load_callbacks()
        try:
            play = ansible.playbook.play.Play().load(
                self.get_play(gather_facts=gather_facts),
                variable_manager=self._tqm._variable_manager,
                loader=self._tqm._loader)
        except (AnsibleParserError, AnsibleError) as e:
            self.runtime_errors = e.message
            return False
        success = self._play(play)
        self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)
        self._tqm.cleanup()
        return success
