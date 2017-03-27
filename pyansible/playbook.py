import ansible.playbook
from ansible.errors import AnsibleError
from ansible.errors import AnsibleError, AnsibleParserError
import play
import json
import os

class Playbook(play.Play):
    def __init__(self, playbook, inventory='localhost', **options):
        self.playbook = playbook
        super(self.__class__, self).__init__(
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
            if self._tqm._options.__dict__[key]:
                opts += '--%s=%s ' % (
                    key.replace('_','-'), self._tqm._options.__dict__[key])
        for key in ('become', 'check'):
            if str(self._tqm._options.__dict__[key]) in ('True', 'yes'):
                opts += '--%s ' % key
        if self._tqm._options.remote_user:
            opts += '--user=%s ' % self._tqm._options.remote_user
        if self._tqm._options.verbosity:
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
            pb = ansible.playbook.Playbook.load(self.playbook,
                loader=self._tqm._loader,
                variable_manager=self._tqm._variable_manager)
            self._tqm.load_callbacks()
            self._tqm.send_callback('v2_playbook_on_start', pb)
            plays = pb.get_plays()
        except (AnsibleParserError, AnsibleError) as e:
            self.runtime_errors = e.message
            return False
        for play in plays:
            if not self._play(play):
                success = False
                break
        else: 
            hosts = sorted(self._tqm._stats.processed.keys())
            for h in hosts:
                t = self._tqm._stats.summarize(h)
                if t['unreachable'] > 0 or t['failures'] > 0:
                    success = False

        self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)
        self._tqm.cleanup()
        return success
