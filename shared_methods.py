from fenx.base_plugin import shared_methods
import logging as _logging
from fenx.studio.events import event
logger = _logging.getLogger(__name__)


class SharedMethods(shared_methods.SharedMethods):

    def plugins(self, *args, **kwargs):
        return self.PLUGIN.plugins.keys()

    def emit(self, event_name, *args, **kwargs):
        event.emit(event_name, *args, **kwargs)

    def log(self, *args, **kwargs):
        msg = ' '.join([str(x) for x in args]).strip()
        if msg:
            self.PLUGIN.log(msg)
