from fenx.base_plugin import shared_methods
import logging as _logging
logger = _logging.getLogger(__name__)


class SharedMethods(shared_methods.SharedMethods):
    def open_debug(self, *args, **kwargs):
        self._execute_in_qt_thread(self.PLUGIN.show_debug_panel)
        return True

    def ping(self):
        print('PONG')
        self.PLUGIN.log('PONG')
        return 'PONG'