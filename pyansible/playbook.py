import ansible.playbook
from ansible.errors import AnsibleError, AnsibleParserError
from . import play
import json
import os


class Playbook(play.Play):
    def __init__(self, playbook, inventory='localhost', **options):
        self.playbook = playbook
        super(Playbook, self).__init__(
            inventory,
            basedir=os.path.dirname(self.playbook),
            **options)
        self._tqm._inventory.set_playbook_basedir(
            os.path.realpath(os.path.dirname(self.playbook)))

    def get_command(self):
        if os.path.isfile(self._tqm._inventory.host_list):
            inventory = self._tqm._inventory.host_list
        else:
            inventory = ','.join([
                str(host)
                for host in self._tqm._inventory.list_hosts()
            ]) + ','
        opts = "--inventory-file=%s " % inventory
        for key in ('become_method', 'become_user', 'tags', 'forks'):
            if key in self._tqm._options.__dict__:
                opts += '--%s=%s ' % (
                    key.replace('_', '-'), self._tqm._options.__dict__[key])
        for key in ('become', 'check'):
            if key in self._tqm._options.__dict__ and \
                    str(self._tqm._options.__dict__[key]) in ('True', 'yes'):
                opts += '--%s ' % key
        if 'remote_user' in self._tqm._options.__dict__:
            opts += '--user=%s ' % self._tqm._options.remote_user
        if 'verbosity' in self._tqm._options.__dict__:
            opts += '-' + 'v' * self._tqm._options.verbosity
        if len(self._tqm._variable_manager.extra_vars) > 0:
            opts += "--extra-vars '%s' " % \
                json.dumps(self._tqm._variable_manager.extra_vars)
        return 'ansible-playbook %s %s' % (
            self.playbook,
            opts)

    def run(self):
        success = True
        try:
            pb = ansible.playbook.Playbook.load(
                self.playbook,
                loader=self._tqm._loader,
                variable_manager=self._tqm._variable_manager)
            self._tqm.load_callbacks()
            self._tqm.send_callback('v2_playbook_on_start', pb)
            plays = pb.get_plays()
        except (AnsibleParserError, AnsibleError) as e:
            self.runtime_errors = e.message
            return False
        for p in plays:
            if not self._play(p):
                success = False
                break

        self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)
        self._tqm.cleanup()
        return success
