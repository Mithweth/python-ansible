from . import task


class Role(task.Task):
    def __init__(self, roles, inventory=None, host='localhost',
                 group=None, basedir=None, **options):
        self.roles = roles
        super(Role, self).__init__(
            roles, inventory, host,
            group, basedir, **options)
