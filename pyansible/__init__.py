from collections import namedtuple
import ansible.release
version_info = namedtuple('version_info',
                          ['major', 'minor', 'micro', 'releaselevel'])(*[
                              int(n) for n in ansible.release.__version__.split('.')])

from .playbook import Playbook
from .task import Task
from .role import Role

__all__ = ['Playbook', 'Task', 'Role', 'version_info']
