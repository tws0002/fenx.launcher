import os
from fenx.base_plugin.plugin import BasePlugin
from fenx.config import config, settings
from fenx.tools.utils import open_folder, open_text_file
from fenx.launcher.widgets import main_menu
import shared_methods


class Plugin(BasePlugin):
    name = 'tools'
    item_name = 'tools'
    menu_index = 99

    def __init__(self, parent):
        super(Plugin, self).__init__(parent)
        self.SHARED_METHODS = shared_methods.SharedMethods(self)

    def menu_items(self):
        tools_menu = main_menu.SubMenu('Tools', 'tools', name=self.item_name)
        tools_menu.append(main_menu.MenuItem('Update...', 'update2', self.main.not_implement))
        tools_menu.append(main_menu.MenuItem('Wizards...', 'wizard', self.main.not_implement))
        admmin_menu = main_menu.SubMenu('Admin', 'gears', name=self.item_name + '_admin')
        admmin_menu.append(main_menu.MenuItem('Debug Info', 'nav', self.show_debug_panel))
        admmin_menu.append(
            main_menu.MenuItem('Pipeline Folder', 'folder_open', lambda: open_folder(config.PIPELINE_LOCATION)))
        admmin_menu.append(main_menu.MenuItem('Settings Folder', 'settings', lambda: open_folder(settings._root_dir)))
        admmin_menu.append(main_menu.MenuItem('Config File', 'document', lambda :open_text_file(os.path.join(os.getenv('STUDIO_LOCATION', ''), 'config.json'))))
        tools_menu.append(admmin_menu)
        if config._get('DEBUG'):
            dbg_menu = main_menu.SubMenu('Debug', 'debug', name=self.item_name + '_debug')
            dbg_menu.append(main_menu.MenuItem('Console', 'nav', lambda *a: [self.main.CONSOLE.show(), self.main.CONSOLE.activateWindow()]))
            dbg_menu.append(main_menu.MenuItem('Shell', 'console'))
            dbg_menu.append(main_menu.MenuItem('Python Shell', 'python', self.open_python_shell, os=['nt']))
            dbg_menu.append(main_menu.MenuItem('Reload Menu', 'list', self.main.update_and_reopen))
            dbg_menu.append(main_menu.MenuItem('Restart', 'update', self.restart_action))
            tools_menu.append(dbg_menu)
        return tools_menu

    def open_python_shell(self):
        from fenx.debug_tools import python_shell
        python_shell._open_shell()

    def show_debug_panel(self):
        """
        "Debug Info" action. Open debug window
        :return:
        """
        from fenx.debug_tools.debug_window import window
        self._debug_info_window = window.DebugWindow()
        self._debug_info_window.create_debug_data()
        self._debug_info_window.show()
        self._debug_info_window.activateWindow()

    def restart_action(self):
        """
        "Restart" action. Restart this app.
        :return:
        """
        from PyQt5.QtCore import QProcess
        import sys
        cmd = '%s %s' % (sys.executable, ' '.join(sys.argv))
        QProcess.startDetached(cmd)
        sys.exit()
