import inspect, traceback
import logging as _logging
import os, sys
# from . import shared_methods
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from fenx.config import config, settings
from fenx.dialogs.py_console import console
from fenx.launcher import binding
from fenx.resources import get_icon, get_style
from fenx.user import user
from fenx.api import Workspace
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
    exitSignal = pyqtSignal()
    reloadMenuSignal = pyqtSignal()
    _default_waiting_text = 'Waiting...'
    name = 'launcher'

    def __init__(self, creation_event):
        super(Launcher, self).__init__()
        self._bind = binding.WorkspaceBinding(workspace=Workspace.current(), parent=self)
        if self._bind.is_locked():
            try:
                from fenx.local_server.http import client
                client.REQUEST.launcher.say_hello()
            except:
                pass
            raise Exception('Launcher for workspace "{}" already started'.format(self._bind.name()))
        self._bind.lock()
        self.executeSignal.connect(self._execute_signal)
        self.reloadMenuSignal.connect(self.update_menu)
        if self.NO_GUI:
            print('NO GUI MODE')
            # todo: add no gui mode
            pass
        creation_event.connect(self.apply_stylesheet)
        __import__('__main__').__dict__['_main_launcher_object'] = self
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(get_icon('tray')))
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.set_normal()
        # https://github.com/robobenklein/openairplay/blob/master/main.py
        # self.SHARED_METHODS = shared_methods.SharedMethods(self)
        self.CONSOLE = self.create_console()
        self.tray_menu = QMenu()
        self.tray_icon.show()
        self.plugins = {}
        self.init_plugins()
        self.login_action()
        # self.tray_icon.messageClicked.connect(lambda :self.tray_menu.popup(QCursor.pos()))
        self.exitSignal.connect(self.exitEvent)
        if (config._get('DEBUG') or os.getenv('DEBUGCONSOLE') == '1') and self.CONSOLE:
            self.CONSOLE.show()
        event.emit('on_launcher_started', self)
        settings.LAUNCHER_START_COUNT = (settings.LAUNCHER_START_COUNT or 0) + 1
        if settings.LAUNCHER_START_COUNT < 3:
            self.startup_notification()

    def startup_notification(self):
        self.tray_icon.showMessage('Fenx Launcher v{}'.format(version),
                                   'Workspace: {}'.format(self._bind._workspace.title))

    @classmethod
    def apply_stylesheet(cls, widget):
        # icon
        widget.setWindowIcon(QIcon(get_icon('fenx')))
        # style
        st = get_style(config._get('DEFAULT_STYLE', ''))
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
        # log_file = os.path.join(settings._root_dir, '.%sstarter_console.log' % (
        # (config.WORKSPACE_NAME + '_') if config._get('WORKSPACE_NAME') else ''))
        return console.Console(self, formatter=frm,
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
            self.tray_menu.popup(QCursor.pos())
            # self.exitEvent()

    def tray_message(self, msg):
        """
        Show tray message
        :param msg: str
        """
        self.CONSOLE.log(msg)
        self.tray_icon.showMessage('Workspace Menu v%s' % version, msg)

    def exit(self):
        self.exitSignal.emit()

    def exitEvent(self):
        """
        Clear on exit
        """
        event.emit('on_before_launcher_closed', self)
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

    def update_menu(self, differed=True):
        """
        Main action to rebuild menu
        """
        if differed:
            QTimer.singleShot(100, self.__update_menu)
        else:
            self.__update_menu()

    def __update_menu(self):
        self.waiting_menu()
        self.set_menu(self._generate_menu())

    def _generate_menu(self):
        data = self.generate_menu_data()
        tray_menu = main_menu.MainTrayMenu(data, self)
        try:
            tray_menu.rebuildSignal.disconnect()
        except:
            pass
        tray_menu.rebuildSignal.connect(self.update_and_reopen)
        return tray_menu

    def waiting_menu(self, text=None):
        """
        Text method. To discard changed call update_menu()
        :param text: Menu text
        """
        text = text or self._default_waiting_text
        self.set_menu(main_menu.MainTrayMenu.waiting_menu(str(text)), 'tray_wait')

    def update_and_reopen(self):
        """
        Rebuild action with re open menu
        """
        pos = self.tray_menu.pos()
        def reop(p=None):

            self.update_menu(differed=False)
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
        # if self._is_logged_in():
        #     self.update_menu()
        #     return

        self.update_menu()
        if user.need_to_authorization:
            dialog_class = config._get('LOGIN_DIALOG_CLASS')
            if dialog_class:
                from pydoc import locate
                cls = locate(dialog_class)
                if not cls:
                    raise Exception('Login dialog class not found: {}'.format(dialog_class))
            else:
                from .widgets.login_dialog import LoginDialog as cls
            spec = inspect.getfullargspec(cls.__init__)
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

    def _execute_signal(self, callback):
        callback()

    def log(self, *args, **kwargs):
        msg = ' '.join([str(x) for x in args]).strip()
        if msg:
            self.CONSOLE.log(msg)




