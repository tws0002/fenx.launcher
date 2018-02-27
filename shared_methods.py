from fenx.base_plugin.shared_methods import SharedMethods as BaseSharedMethods
import logging as _logging
from fenx.studio.events import event
logger = _logging.getLogger(__name__)


class SharedMethods(BaseSharedMethods):

    def plugins(self, *args, **kwargs):
        return list(self.PLUGIN.plugins.keys())

    def emit(self, event_name, *args, **kwargs):
        event.emit(event_name, *args, **kwargs)

    def log(self, *args, **kwargs):
        msg = ' '.join([str(x) for x in args]).strip()
        if msg:
            self.PLUGIN.log(msg)
