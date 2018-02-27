import inspect, traceback
import logging as _logging
import os, sys
from . import shared_methods
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from fenx.config import config, settings
from fenx.py_console import console
from fenx.resources import get_icon, get_style
from fenx.user import user
from fenx.launcher import __version__ as version
from .widgets import main_menu
from fenx.studio.events import event
logger = _logging.getLogger(__name__)


class Launcher(QObject):
    """
    Tray menu for pipeline starter
    Run Help menu for details
    """
    NO_GUI = '-nogui' in sys.argv
    executeSignal = pyqtSignal(object)
    sharedMethodRequestedSignal = pyqtSignal(object)

    def __init__(self, creation_event):
        super(Launcher, self).__init__()
        self.executeSignal.connect(self._execute_signal)
        self.sharedMethodRequestedSignal.connect(self._shared_method_requested)
        if self.NO_GUI:
            print('NO GUI MODE')
            # todo: add no gui mode
            pass
        creation_event.connect(self.apply_stylesheet)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(get_icon('tray')))
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.set_normal()
        # https://github.com/robobenklein/openairplay/blob/master/main.py
        self.SHARED_METHODS = shared_methods.SharedMethods(self)
        self.CONSOLE = self.create_console()
        self.tray_menu = QMenu()
        self.tray_icon.show()
        self.plugins = {}
        self.init_plugins()
        self.login_action()
        if config._get('DEBUG') and self.CONSOLE:
            self.CONSOLE.show()
            # self.plugins['modules_manager'].open_manager()
            # from fenx.debug_tools.qt_test.window import show
            # self.tq = show()
            # if self.plugins.get('local_server'):
            #     self.plugins['local_server'].open_local_server_panel()
        event.emit('on_launcher_started')

    def apply_stylesheet(self, widget: QWidget):
        # icon
        widget.setWindowIcon(QIcon(get_icon('fenx')))
        # style
        st = get_style(config.DEFAULT_STYLE)
        if not st:
            return
        widget.setStyleSheet(st)
        # icons size
        iconsize = '''QTreeView:item,
QAbstractItemView:item
{
    height: %spx;
}'''
        for ch in widget.findChildren(QListView) + widget.findChildren(QTreeView):
            sz = max([ch.iconSize().height(), ch.iconSize().width()])
            ch.setStyleSheet(iconsize % sz)

    def create_console(self):
        frm = None
        # frm = formatter.FormatParser()
        # frm.add_rule('Callbacks', [re.compile(r"\w+\s>>.*")], italic=True, color='gray')
        # frm.add_rule('Process', [re.compile(r"process\w+Signal\s>>.*")], italic=True, color='#85C2C0')
        # frm.add_rule('Process', [re.compile(r"ws\w+Signal\s>>.*")], italic=True, color='#5D9DCA')
        # frm.add_rule('Process', [re.compile(r"localServer\w+Signal\s>>.*")], italic=True, color='#87ADA2')
        log_file = os.path.join(settings._root_dir, '.%sstarter_console.log' % (
        (config._get('STUDIO_NAME', '') + '_') if config._get('STUDIO_NAME') else ''))
        return console.Console(self, formatter=frm, log_file=log_file,
                                     load_settings_callback=lambda: settings.CONSOLE_PREFS,
                                     save_settings_callback=lambda x: settings._set_value('CONSOLE_PREFS',x)
                               )

    def set_waiting(self, text):
        self.tray_icon.setIcon(QIcon(get_icon('tray_wait')))
        self.waiting_menu(text)

    def set_normal(self):
        self.tray_icon.setIcon(QIcon(get_icon('tray')))

    def tray_icon_activated(self, reason):
        """
        Execute click on tray icon if is WINDOWS
        """
        # QSystemTrayIcon.Trigger       LMB
        # QSystemTrayIcon.Context       RMB
        # QSystemTrayIcon.MiddleClick   MMB
        if reason == QSystemTrayIcon.Context:
            pass
            # self.menu_context()
            # use default context menu trigger
        elif reason == QSystemTrayIcon.Trigger:
            # open menu on left click
            self.tray_menu.popup(QCursor.pos())
        else:
            # todo: maybe open menu?
            self.tray_menu.popup(QCursor.pos())
            # self.exitEvent()

    def tray_message(self, msg):
        """
        Show tray message
        :param msg: str
        """
        self.CONSOLE.log(msg)
        self.tray_icon.showMessage('Pipeline Menu v%s' % version, msg)

    def exitEvent(self):
        """
        Clear on exit
        """
        event.emit('on_before_launcher_closed')
        logger.debug('Stop clients...')
        # stop plugins
        for plg in self.plugins.values():
            try:
                plg.stop()
            except Exception as e:
                logger.error(str(e))
                print(e)
                traceback.print_exc()
        self.tray_icon.hide()
        del self.tray_icon
        event.emit('on_launcher_closed')
        QApplication.quit()

    # MENUS

    def set_menu(self, menu, icon=None):
        self.tray_menu = menu
        self.tray_icon.setContextMenu(self.tray_menu)
        normal_icon = get_icon(icon or 'tray')
        self.tray_icon.setIcon(QIcon(normal_icon))

    def update_menu(self):
        """
        Main action to rebuild menu
        """
        self.set_menu(main_menu.MainTrayMenu.waiting_menu('Waiting...'), 'tray_wait')
        data = self.generate_menu_data()
        tray_menu = main_menu.MainTrayMenu(data, self,
                                           # title=config.STUDIO_TITLE or 'STUDIO'
                                           )
        try:
            tray_menu.rebuildSignal.disconnect()
        except:
            pass
        tray_menu.rebuildSignal.connect(self.update_and_reopen)
        self.set_menu(tray_menu)

    def waiting_menu(self, text):
        """
        Text method. To discard changed call update_menu()
        :param text: Menu text
        """
        self.set_menu(main_menu.MainTrayMenu.waiting_menu(text), 'tray_wait')

    def update_and_reopen(self):
        """
        Rebuild action with re open menu
        """
        pos = self.tray_menu.pos()
        def reop(p=None):

            self.update_menu()
            if p:
                self.tray_menu.popup(p)
        QTimer.singleShot(100, lambda :reop(pos))

    def generate_menu_data(self):
        """
        Create menu data
        :return: main_menu.MainTrayMenu instance 
        """
        menu = main_menu.SubMenu('')
        is_need_auth = user.need_to_authorization
        is_logged_in = user.is_authorized or not is_need_auth
        # fill menu
        if is_logged_in:
            plug_items = []
            for name, plug in self.plugins.items():
                items = plug.menu_items()
                plug_items.append([plug.menu_index, items, plug])
            plugin_items = [[x[1], x[2]] for x in sorted(plug_items, key=lambda x: x[0])]
            for items, plug in plugin_items:
                menu.append(items)

        # add login\logout if need
        menu.append(main_menu.Divider())
        if is_need_auth:
            if is_logged_in:
                menu.append(main_menu.MenuItem('Logout', 'logout', self.logout_action))
            else:
                menu.append(main_menu.MenuItem('Login', 'login', self.login_action))

        if config._get('HELP_URL'):
            menu.append(main_menu.MenuItem('Help', 'help', self.show_help))

        menu.append(main_menu.MenuItem('Exit', 'power', self.exitEvent))
        return menu

    def _is_logged_in(self):
        return user.is_authorized

    def show_help(self):
        """
        Help action
        """
        if config._get('HELP_URL'):
            import webbrowser
            webbrowser.open(config.HELP_URL)
        else:
            self.tray_message('HELP!!!!!!!!!!!')

    # AUTH

    def login_action(self):
        """
        "Login" action. Open login dialog if need
        """
        if self._is_logged_in():
            self.update_menu()
            return
        if user.need_to_authorization:
            dialog_class = config._get('LOGIN_DIALOG_CLASS')
            if dialog_class:
                from pydoc import locate
                cls = locate(dialog_class)
                if not cls:
                    raise Exception('Login dialog class not found: {}'.format(dialog_class))
            else:
                from .widgets.login_dialog import LoginDialog as cls
            spec = inspect.getargspec(cls.__init__)
            defaults = dict(zip(spec.args[-len(spec.defaults):], spec.defaults))
            self._dial = cls(
                add_register_btn=bool(config._get('REGISTER_URL')),
                register_url=config._get('REGISTER_URL'),
                add_forgot_btn=bool(config._get('FORGOT_PASSWORD_URL')),
                forgot_url=config._get('FORGOT_PASSWORD_URL'),
                logo=config._get('LOGIN_DIALOG_LOGO', defaults.get('logo')),
                title=config._get('LOGIN_DIALOG_TITLE', defaults.get('title')),
                submit_btn_text=config._get('LOGIN_DIALOG_SUBMIT_BUTTON_TEXT', defaults.get('submit_btn_text')),
                # todo: add other arguments
            )
            self._dial.submitSignal.connect(self._do_login)
            self._dial.show()

    def _do_login(self, *args):
        if user.login(*args):
            self.update_menu()
        else:
            self.login_action()

    def logout_action(self):
        """
        "Logout" action
        """
        self.CONSOLE.log('Logout')
        user.logout()
        self.update_menu()

    @staticmethod
    def not_implement():
        QMessageBox.warning(None, 'Not Implement', 'Sorry. This function not implement yet')

    def init_plugins(self):
        from fenx.studio import plugins
        all_plugins = plugins.get_plugins()

        self.plugins = {x.name: x(self) for x in all_plugins}
        # emit events

        # add plugins to console namespace
        if self.CONSOLE:
            for name, plg in self.plugins.items():
                self.CONSOLE.extra_namespace[name] = plg
    #     import imp
    #     import inspect
    #     from fenx.launcher.plugins._base_plugin import Plugin
    #     plugin_dirs = []
    #     # default plugins
    #     default_plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
    #     plugin_dirs.append(default_plugins_dir)
    #     # extra plugins
    #     extra_dirs = config._get('PIPELINE_PLUGINS_PATH')
    #     if isinstance(extra_dirs, list):
    #         for extra_path in extra_dirs:
    #             if os.path.isdir(extra_path):
    #                 plugin_dirs.append(extra_path)
    #     plugins = []
    #     _skipped = []
    #     enabled_plugins = config._get('LAUNCHER_ENABLED_PLUGINS', [])
    #     for plugins_dir in plugin_dirs:
    #         plugins_files = [x for x in os.listdir(plugins_dir) if not x.startswith('_')]
    #         plugin_configs = []
    #         for f in plugins_files:
    #             full_path = os.path.join(plugins_dir, f)
    #
    #             if os.path.isdir(full_path):
    #                 init = os.path.join(full_path,  '__init__.py')
    #                 if not os.path.exists(init):
    #                     continue
    #                 # add configs
    #                 for c_name in config._config_default_file_names:
    #                     conf = os.path.join(plugins_dir, f, c_name)
    #                     if os.path.exists(conf):
    #                         plugin_configs.append(conf)
    #             else:
    #                 if not os.path.splitext(full_path)[-1] == '.py':
    #                     continue
    #
    #             name = os.path.splitext(os.path.basename(full_path))[0]
    #             if name == '__init__':
    #                 name = f
    #             import fenx.launcher.plugins
    #             # temporary apply config
    #             config._add_temporary_files(plugin_configs)
    #             # todo: fix for Python3, replace imp library
    #             if os.path.isfile(full_path):
    #                 # is module
    #                 try:
    #                     mod = imp.load_source(fenx.launcher.plugins.__name__+'.'+name, full_path)
    #                 except Exception as e:
    #                     logger.error('Error: {}'.format(e))
    #                     traceback.print_exc()
    #                     if self.CONSOLE:
    #                         self.CONSOLE.log('Error load launcher plugin "{}": {}'.format(name, str(e)))
    #                     config._clear_temporary_files()
    #                     continue
    #             else:
    #                 # is package
    #                 if not os.path.dirname(full_path) in sys.path and not os.path.exists(os.path.join(os.path.dirname(full_path), '__init__.py')):
    #                     sys.path.append(os.path.dirname(full_path))
    #                 try:
    #                     mod = imp.load_package(fenx.launcher.plugins.__name__+'.'+name, full_path)
    #                 except Exception as e:
    #                     logger.error('Error: {}'.format(e))
    #                     if self.CONSOLE:
    #                         traceback.print_exc()
    #                         self.CONSOLE.log('Error load launcher plugin "{}": {}'.format(name, str(e)))
    #                     config._clear_temporary_files()
    #                     continue
    #
    #             for key in mod.__dict__.keys():
    #                 cls = mod.__dict__[key]
    #                 if inspect.isclass(cls) and issubclass(cls, mod.__dict__.get(Plugin.__name__) or Plugin) and not cls.__name__ == Plugin.__name__ and hasattr(cls, 'name'):
    #                     plugin_name = cls.name
    #                     if not plugin_name in enabled_plugins:
    #                         # skip plugins
    #                         _skipped.append(os.path.splitext(f)[0])
    #                         config._clear_temporary_files()
    #                     else:
    #                         # accept plugin
    #                         plugins.append(cls)
    #                         config._accept_temporary_files()
    #             plugin_configs = []
    #     if _skipped:
    #         logger.debug('Plugins {} found but not enabled. Use LAUNCHER_ENABLED_PLUGINS value in config to unable it'.format(', '.join(list(set(_skipped)))))
    #     if not plugins:
    #         return
    #     self.plugins = {x.name: x(self) for x in plugins}
    #     # auth model
    #     if config._get('AUTH_PLUGIN'):
    #         if not config.AUTH_PLUGIN in self.plugins.keys():
    #             logger.error('Error: Auth plugin not in loaded plugin list')
    #         else:
    #             self.AUTH = self.plugins.get(config.AUTH_PLUGIN)
    #     # emit events
    #     map(lambda plug: event.emit('plugin_loaded', plug), self.plugins.values())
    #     # add plugins to console namespace
    #     if self.CONSOLE:
    #         for name, plg in self.plugins.items():
    #             self.CONSOLE.extra_namespace[name] = plg

    # UTILS
    def _execute_signal(self, callback):
        callback()

    def _shared_method_requested(self, data):
        if 'pong' in data:
            self.CONSOLE.log('PONG')
            return
        if not data.get('method'):
            raise Exception('Method not set')
        callback = self._get_callback(data['method'])
        if not callback:
            raise Exception('Method not found')
        return callback(*data.get('args', []), **data.get('kwargs', {}))

    def _get_callback(self, path):
        obj = None
        elem = path.split('.')
        if len(elem) == 1:
            # self methods
            obj = self.SHARED_METHODS
            method = path
        elif len(elem) == 2:
            method = elem[1]
            plg = self.plugins.get(elem[0])
            if not plg:
                raise Exception('Object not found')
            obj = plg.SHARED_METHODS
        else:
            raise Exception('Wrong path')
        if not obj:
            return
        return getattr(obj, method, None)

    def log(self, *args, **kwargs):
        msg = ' '.join([str(x) for x in args]).strip()
        if msg:
            self.CONSOLE.log(msg)
