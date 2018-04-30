import os
from fenx.tools import setup_log
import logging as _logging
logger = _logging.getLogger(__name__)


class WorkspaceBinding(object):
    def __init__(self, workspace=None, parent=None):
        self._workspace = workspace
        self._parent = parent
        self.f = None

    @property
    def bind_file(self):
        return os.path.join(os.path.expanduser('~'), '.workspace_bind_file__{}'.format(self.name()))

    def name(self):
        if self._workspace:
            return self._workspace.fullname.replace(':', '-')
        return ''

    def is_locked(self):
        if not os.path.exists(self.bind_file):
            return False
        try:
            os.remove(self.bind_file)
            return False
        except:
            return True

    def lock(self):
        open(self.bind_file, 'w').write(self.name())
        self.f = open(self.bind_file, 'a')

    def unlock(self):
        if self.f:
            if not hasattr(self._parent, 'tray_icon'):
                logger.warning('You can\'t unlock launcher manually')
                return
            self.f.close()
            self.f = None
