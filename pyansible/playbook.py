from ansible.playbook import Playbook

class Playbook(Play):
    def __init__(self, playbook, inventory, host, basedir):
        super(self.__class__, self).__init__(inventory, host, basedir)
        self.playbook = None

    def get_command(self):
        pass

    def run(self):
        self.errors = None
        pb = Playbook.load(self.playbook, loader=, variable_manager=)
        plays = pb.get_plays()
        for play in plays:
            if not self._play(play):
                break
        self._tqm.cleanup()

