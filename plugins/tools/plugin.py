from fenx.base_plugin.plugin import BasePlugin
from fenx.config import config, settings
from fenx.launcher.tray_menu.widgets import main_menu
from fenx.studio import app_wrappers


class Plugin(BasePlugin):
    name = 'tools'
    item_name = 'tools'
    menu_index = 99

    def __init__(self, parent):
        super(Plugin, self).__init__(parent)

    def menu_items(self):
        tools_menu = main_menu.SubMenu('Tools', 'tools2', name=self.item_name)
        tools_menu.append(main_menu.MenuItem('Update...', 'update2', self.main.not_implement))
        tools_menu.append(main_menu.MenuItem('Wizards...', 'wizard', self.main.not_implement))
        if config._get('LOG_LEVEL') == 'DEBUG':
            dbg_menu = main_menu.SubMenu('Debug', 'debug', name=self.item_name+'_debug')
            dbg_menu.append(main_menu.MenuItem('Console', 'console',
                                               lambda *a: [self.main.CONSOLE.show(), self.main.CONSOLE.activateWindow()]))
            dbg_menu.append(main_menu.MenuItem('Python Shell', 'console', self.open_python_shell, os=['nt']))
            dbg_menu.append(main_menu.MenuItem('Debug Info', 'search', self.show_debug_panel))
            dbg_menu.append(main_menu.MenuItem('Reload Menu', 'list', self.main.update_and_reopen))
            dbg_menu.append(main_menu.MenuItem('Restart', 'update', self.restart_action))
            dbg_menu.append(main_menu.MenuItem('Pipeline Folder', 'folder_open',
                                               lambda: app_wrappers.BaseApplication.open_folder(
                                               config.PIPELINE_LOCATION)))
            dbg_menu.append(main_menu.MenuItem('Settings Folder', 'settings',
                                               lambda: app_wrappers.BaseApplication.open_folder(
                                               settings._root_dir)))
            tools_menu.append(dbg_menu)
        return tools_menu


    def open_python_shell(self):
        from debug_tools import python_shell
        reload(python_shell)
        python_shell._open_shell()

    def show_debug_panel(self):
        """
        "Debug Info" action. Open debug window
        :return:
        """
        from fenx.debug_tools.debug_window import window
        reload(window)
        self._debug_info_window = window.DebugWindow()
        self._debug_info_window.create_debug_data()
        self._debug_info_window.show()
        self._debug_info_window.activateWindow()

    def restart_action(self):
        """
        "Restart" action. Restart this app.
        :return:
        """
        from PySide.QtCore import QProcess
        import sys
        cmd = '%s %s' % (sys.executable, ' '.join(sys.argv))
        QProcess.startDetached(cmd)
        sys.exit()
