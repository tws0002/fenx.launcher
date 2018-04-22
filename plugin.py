import logging as _logging
from . import shared_methods
from fenx.base_plugin.plugin import BasePlugin
from fenx.config import config
from fenx.launcher.widgets import main_menu

logger = _logging.getLogger(__name__)


class Plugin(BasePlugin):
    name = 'launcher'
    __version__ = '0.0'
    item_name = name

    def __init__(self, *args):
        super(Plugin, self).__init__(*args)
        self.SHARED_METHODS = shared_methods.SharedMethods(self)

    def log(self, *args, **kwargs):
        self.main.log(*args, **kwargs)