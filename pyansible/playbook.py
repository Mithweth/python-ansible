from ansible.playbook import Playbook
from ansible.errors import AnsibleError

class Playbook(Play):
    def __init__(self, playbook, inventory, host, basedir):
        super(self.__class__, self).__init__(inventory, host, basedir)
        self.playbook = None

    def get_command(self):
        ansible_opts = ' '.join([
            "--%s='%s'" % (key.replace('_','-'), val)
            for key, val in self._tqm._options.__dict__.iteritems()
            if val is not None
        ])

    def run(self):
        success = True
        try:
            pb = Playbook.load(self.playbook,
                loader=self._tqm._loader,
                variable_manager=self._tqm._variable_manager)
            plays = pb.get_plays()
        except AnsibleError as e:
            self.errors = e.message
            return False
        for play in plays:
            if not self._play(play):
                success = False
                break
        else: 
            hosts = sorted(self._tqm._stats.processed.keys())
            for h in hosts:
                t = stats.summarize(h)
                if t['unreachable'] > 0 or t['failures'] > 0:
                    success = False
        self._tqm.cleanup()
        return success

