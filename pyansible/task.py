from ansible.playbook.play import Play

class Task(Play):
    def __init__(self, tasks, inventory, host, basedir):
        super(self.__class__, self).__init__(inventory, host, basedir)
        self.tasks = tasks

    def get_play(self):
        pass

    def run(self):
        play_source = self.get_play()
        pass
