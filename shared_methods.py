from fenx.base_plugin import shared_methods
import logging as _logging
logger = _logging.getLogger(__name__)


class SharedMethods(shared_methods.SharedMethods):

    def plugins(self, *args, **kwargs):
        return self.PLUGIN.plugins.keys()
