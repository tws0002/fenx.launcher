from fenx.base_plugin import shared_methods
import logging as _logging
from fenx.studio import app_wrappers
logger = _logging.getLogger(__name__)


class SharedMethods(shared_methods.SharedMethods):

    def apps(self, *args, **kwargs):
        return app_wrappers.all_app_info().keys()

    def start_app(self, name=None, version=None, **kwargs):
        app = app_wrappers.get_app(name, version)
        if app:
            app.start()
            return True
        else:
            return False
