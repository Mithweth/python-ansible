import ansible.playbook.play
from ansible.errors import AnsibleError, AnsibleParserError
import play
import compat_utils
import os
import yaml


class Task(play.Play):
    def __init__(self, tasks, inventory=None, host='localhost',
                 group=None, basedir=None, **options):
        self.tasks = tasks
        self._gather_facts = 'no'
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
        super(Task, self).__init__(inventory, basedir, **options)
        if os.path.isfile(inventory):
            compat_utils.add_host(self._tqm._inventory, group, host)

    @property
    def play(self):
        actions = ([self.tasks]
                   if isinstance(self.tasks, dict)
                   else list(self.tasks))
        play = {
            'hosts': self.group,
            'gather_facts': self._gather_facts,
            self.name: actions
        }
        if len(self._tqm._variable_manager.extra_vars) > 0:
            play['vars'] = self._tqm._variable_manager.extra_vars
        for key in ('become_method', 'become_user',
                    'become', 'remote_user', 'connection'):
            if self._tqm._options.__dict__[key]:
                play[key] = self._tqm._options.__dict__[key]
        return play

    @property
    def name(self):
        return self.__class__.__name__.lower() + 's'

    def run(self, gather_facts='no'):
        self._tqm.load_callbacks()
        self._gather_facts = gather_facts
        try:
            play = ansible.playbook.play.Play().load(
                self.play,
                variable_manager=self._tqm._variable_manager,
                loader=self._tqm._loader)
        except (AnsibleParserError, AnsibleError) as e:
            self.runtime_errors = e.message
            return False
        success = self._play(play)
        self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)
        self._tqm.cleanup()
        return success
