from . import task


class Role(task.Task):
    def __init__(self, roles, inventory=None, host='localhost',
                 group=None, basedir=None, **options):
        self.roles = [roles] if isinstance(roles, str) else list(roles)
        super(Role, self).__init__(
            self.roles, inventory, host,
            group, basedir, **options)
