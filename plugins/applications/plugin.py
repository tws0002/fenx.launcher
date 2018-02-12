# from PySide.QtGui import QApplication
# from PySide.QtCore import Qt
import logging as _logging
import os
from functools import partial
from fenx.tools import shortcuts
from fenx.base_plugin.plugin import BasePlugin
from fenx.config import config, settings
from fenx.launcher.tray_menu.widgets import main_menu
from fenx.studio import app_wrappers
from fenx.resources import get_icon, convert

logger = _logging.getLogger(__name__)


class Plugin(BasePlugin):
    name = 'applications'
    item_name = 'applications_item'
    menu_index = 0

    def __init__(self, parent):
        super(Plugin, self).__init__(parent)
        # self.user = self.main.user

    def menu_items(self):
        ITEMS = []
        # pinned
        if settings.PINNED_APPLICATIONS:
            for app in settings.PINNED_APPLICATIONS:
                it = main_menu.MenuItem(
                        text=app.get('title', 'ERROR!!!'),
                        icon=app.get('icon', 'default'),
                        callback=partial(self.start_app, app.get('app'),
                                                app.get('version'),
                                                app.get('mode'),
                                                *app.get('args')),
                        shift_callback=partial(self.unpin_app, app)
                        )
                # it.is_pinned = True
                ITEMS.append(it)
            ITEMS.append(main_menu.Divider())
        # apps
        apps = app_wrappers.generate_menu_data()
        apps_menu = main_menu.SubMenu("Applications", 'play')

        for name, app_array in apps.items():
            if not app_array:
                # no applications
                continue
            for app in app_array:
                add_cmd = config._get('CMD_MOD_ON') and  app.have_cmd_binary
                # iterate application versions
                if False:
                    # fake import for auto completions
                    from fenx.studio.app_wrappers import _base
                    app = _base.BaseApplication()

                ico = get_icon(app.app_name) or app.icon
                if app.mods and len(app.mods) > 1:
                    # submenu
                    app_menu = main_menu.SubMenu(app.name, ico)
                    for mod in app.mods:
                        app_data = dict(
                                app=app.app_name,
                                version=app.version,
                                mode=mod.name,
                                title=app.name + (
                                (' / %s' % mod.title) if not mod.name == app._default_mod else ''),
                                icon=get_icon(mod.icon) or ico,
                                args=[]
                            )
                        it = main_menu.MenuItem(
                            text=mod.title,
                            icon=get_icon(mod.icon) or ico,
                            callback=partial(self.start_app, app.app_name, app.version, mod.name),
                            shift_callback=partial(self.pin_app, app_data),
                            ctrl_callback=partial(self.create_shortcut, app_data)
                        )
                        if add_cmd:
                            it.alt_callback = partial(self.start_app, app.app_name, app.version, 'cmd')
                        app_menu.append(it)
                    if not app_menu.actions:
                        # add EMPTY element
                        app_menu.append(None)
                    apps_menu.append(app_menu)
                else:
                    # single item
                    if app.mods:
                        # single mod
                        mod = app.mods[0]
                        app_data = dict(
                            app=app.app_name,
                            version=app.version,
                            mode=mod.name,
                            title=app.name + (
                                (' / %s' % mod.title) if not mod.name == app._default_mod else ''),
                            icon=get_icon(mod.icon) or ico,
                            args=[]
                        )
                        it = main_menu.MenuItem(
                            text=mod.title,
                            icon=get_icon(mod.icon) or ico,
                            callback=partial(self.start_app, app.app_name, app.version, mod.name),
                            shift_callback=partial(self.pin_app, app_data),
                            ctrl_callback=partial(self.create_shortcut, app_data),
                        )
                        if add_cmd:
                            it.alt_callback = partial(self.start_app, app.app_name, app.version, 'cmd')
                        apps_menu.append(it)
                    else:
                        app_data = dict(
                            app=app.app_name,
                            version=app.version,
                            mode='default',
                            title=app.name,
                            icon=get_icon(app.icon) or ico,
                            args=[]
                        )
                        # default command
                        it = main_menu.MenuItem(
                            text=app.name,
                            icon=get_icon(app.icon),
                            callback=partial(self.start_app, app.app_name, app.version, 'default'),
                            shift_callback=partial(self.pin_app, app_data),
                            ctrl_callback=partial(self.create_shortcut, app_data)
                        )
                        if add_cmd:
                            it.alt_callback = partial(self.start_app, app.app_name, app.version, 'cmd')
                        apps_menu.append(it)
                        continue
        apps_menu.append(main_menu.Divider())
        apps_menu.append(main_menu.MenuItem('Refresh Apps', 'search2', self.refresh_action))
        ITEMS.append(apps_menu)
        # ITEMS.append(main_menu.Divider())
        return ITEMS

    # LAUNCHER

    def start_app(self, app_name, version, mode, *args):
        """
        Start detached pipeline software.
        :param app_name: application pipeline name
        :param version: app version
        :param mode: app mode
        :param args: any other args
        """
        app = app_wrappers.get_app(app_name, version)
        if not app:
            logger.error('Application not found!: %s %s' % (app_name, version))
            self.log('Application not found!: %s %s' % (app_name, version))
            return
        self.log('Start app: {} >>> start_app -app {} -ver {} -mod {}'.format(app, app.app_name, app.version, mode))
        # launch
        app.start_detached(mode=mode, *args, with_console=False)

    def callback(self, func):
        func()

    def pin_app(self, data):
        pinned = settings.PINNED_APPLICATIONS or []
        if not data in pinned:
            pinned.append(data)
        settings.PINNED_APPLICATIONS = pinned
        self.update_and_open()

    def unpin_app(self, data):
        pinned = settings.PINNED_APPLICATIONS or []
        if data in pinned:
            pinned.remove(data)
        settings.PINNED_APPLICATIONS = pinned
        self.update_and_open()

    def clear_resent(self):
        """
        "Clear history" action
        """
        self.log('Clear resent history')
        settings.RECENTLY_STARTED = []
        self.update_menu()

    def refresh_action(self):
        """
        "Refresh Apps" action. Search installed applications in config.SOFTWARE_LOCATIONS locations.
        :return:
        """
        self.close_menu()
        app_wrappers.generate_menu_data(True)
        self.update_menu()
        self.show_message('Applications Updated')

    def create_shortcut(self, data):
        app = app_wrappers.get_app(data.get('app'), data.get('version'))
        executable = os.path.normpath(app.join(os.getenv('STUDIO_LOCATION'), 'start_app.cmd'))
        mode = data.get('mode', app._default_mod)
        ico = app.icon
        if os.path.exists(ico):
            if os.path.splitext(ico)[-1] != '.ico':
                ico = convert.png_to_ico(ico)
        else:
            ico = get_icon('noicon.ico')
        res = shortcuts.create_shortcut(source_app=executable,
                                        title=' '.join([app.name, mode.title()]),
                                        destination_dir=shortcuts.DIR.DESKTOP,
                                        icon=ico,
                                        description='Pipeline start for {}'.format(app.name.title()),
                                        workdir=app.work_dir() or os.getenv('STUDIO_LOCATION'),
                                        kwargs=dict(
                                            app=app.app_name,
                                            ver=app.version,
                                            mod=mode
                                          )
                                        )
        if not res:
            logger.error('Shortcut not created')
        # if os.name == 'nt':
        #     self._create_shortcut_win(data)
        # elif os.name == 'posix':
        #     self._create_shortcut_linux(data)
        # else:
        #     logger.error('not implemented')

#     def _create_shortcut_win(self, data):
#         # todo: create shortcut
#         app = app_wrappers.get_app(data.get('app'), data.get('version'))
#         mode = data.get('mode', app._default_mod)
#         logger.debug('Create shortcut for %s in mode %s' % (app.app_name, mode))
#         executable = os.path.normpath(app.join(os.getenv('STUDIO_LOCATION'), 'start_app.cmd'))
#         if not os.path.exists(executable):
#             return
#         if settings.USE_MOD_ICONS_FOR_SHORTCITS:
#             mod = app.mod_by_name(mode)
#             if mod:
#                 ico = get_icon(mod.icon) or get_icon(app.icon)
#             else:
#                 ico = get_icon(app.icon)
#         else:
#             ico = get_icon(app.icon)
#
#         if os.path.exists(ico):
#             if os.path.splitext(ico)[-1] != '.ico':
#                 ico = convert.png_to_ico(ico)
#         else:
#             ico = None
#
#         ico = ico or get_icon('noicon.ico')
#         # todo: if not mode == default make compose from default icon and mode icon
#         workdir = os.path.normpath(os.getenv('STUDIO_LOCATION'))
#         cmd = '{exe} -app {app} -ver {version} -mod {mode}'.format(
#             exe=executable,
#             app=app.app_name,
#             version=app.version,
#             mode=mode)
#         logger.debug('Command for shortcut: %s' % cmd)
#         vb = r'''
#             Set objShell = WScript.CreateObject("WScript.Shell")
#             strDesktopFolder = objShell.SpecialFolders("Desktop")
#             Set objShortCut = objShell.CreateShortcut(strDesktopFolder & "\{title}.lnk")
#             objShortCut.TargetPath = "{executable}"
#             objShortCut.IconLocation = "{ico}"
#             objShortCut.WindowStyle = "7"
#             objShortCut.Description = "Pipeline launcher"
#             objShortCut.Arguments = " -app '{app}' -ver '{version}' -mod '{mod}'"
#             objShortCut.WorkingDirectory = "{wd}"
#             objShortCut.Save'''.format(
#             title=' '.join([app.name, mode.title()]),
#             executable=executable,
#             ico=ico,
#             app=app.app_name,
#             version=app.version,
#             mod=mode,
#             wd=workdir
#         ).replace("'", '" & chr(34) & "')
#         import tempfile
#         fileTemp = tempfile.NamedTemporaryFile(delete=False, suffix='.vbs')
#         fileTemp.write(vb)
#         fileTemp.close()
#         # create shortcut on desktop
#         os.startfile(fileTemp.name)
#
#     def _create_shortcut_linux(self, mode):
#         path = os.path.expanduser('~/Desktop/Launcher.desktop')
#
#         text = '''\
#     [Desktop Entry]
#     Version=1.0
#     Type=Application
#     Name={app_name}
#     Comment={app_name}
#     Exec={executable}
#     Icon={icon}
#     Path={path}
#     Terminal=false
#     StartupNotify=false
#     Keywords=Pipeline;cg;starter;launcher
#     Categories=GNOME;GTK;Graphics;3DGraphics;
#     X-GNOME-Autostart-Delay=5
#     '''.format(
#             app_name='HELLO',
#             executable='/home/paul/dev/studio_pipeline/start_tray.sh',
#             icon='/home/paul/dev/studio_pipeline/tools/pipeline_starter/icons/menu.png',
#             path='/home/paul/dev/studio_pipeline'
#         )
#         open(path, 'w').write(text)
#         os.system('chmod +x ' + path)
#
#
#             # class ApplicationItem(main_menu.MenuItem):
# #     def __init__(self, text, add_to_resent=None, *args, **kwargs):
# #         super(ApplicationItem, self).__init__(text, *args, **kwargs)
# #         self.add_to_resent = add_to_resent or {}
# #         self.is_resent = False
# #
# #     def resent_data(self):
# #         if self.add_to_resent:
# #             return self.add_to_resent
# #         else:
# #             return {}