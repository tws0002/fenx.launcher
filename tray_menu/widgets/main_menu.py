import logging as _logging
import os
import re
from PySide.QtCore import *
from PySide.QtGui import *
from fenx.config import config
# todo: use Qt.py
from fenx.resources import get_icon

logger = _logging.getLogger(__name__)


class Menu(QMenu):
    # def __init__(self, *args, **kwargs):
    #     super(Menu, self).__init__(*args, **kwargs)
    #     self._alt_action = None
    #     self._old_text = ''

    def keyPressEvent(self, event, *args, **kwargs):
        # Qt.Key_Alt
        if event.key() == 16777251:
            return
            # action = self.actionAt(self.mapFromGlobal(QCursor.pos()))
            # if action:
            #     self._alt_action = action
            #     self._old_text = action.text()
            #     action.setText(self._old_text + ' CMD')
            # return
        super(Menu, self).keyPressEvent(event, *args, **kwargs)

    # def keyReleaseEvent(self, event, *args, **kwargs):
    #     if event.key() == 16777251:
    #         action = self.actionAt(self.mapFromGlobal(QCursor.pos()))
    #         if action:
    #             if action is self._alt_action:
    #                 action.setText(self._old_text)
    #     super(Menu, self).keyReleaseEvent(event, *args, **kwargs)

class MainTrayMenu(Menu):
    """
    Data class for tray menu
    """
    rebuildSignal = Signal()

    def __init__(self, data, parent=None):
        super(MainTrayMenu, self).__init__()
        self.par = parent
        self.data = data
        self.generate_menu()
        self._apply_style()

    def generate_menu(self):
        # clear menu
        # print self.data
        self.generate(self.data, self)

    def generate(self, data, parent_menu=None, level=0):
        """
        Create QMenu from data with recursion
        :param data: menu data
        :param parent_menu: parent widget
        :param level: auto value of current level. Need for colorize levels with stylesheet
        """
        parent_menu = parent_menu or self
        for item in data:
            if item is None:  # empty
                a = QAction('Empty', parent_menu)
                a.setDisabled(True)
                parent_menu.addAction(a)
            elif item.type == SubMenu.type:
                menu = Menu(item.text, parent_menu)
                menu.setObjectName('menulevel_%s' % level)
                ico = self.create_icon(get_icon(item.icon))
                menu.menuAction().setData(dict(name=item.name, level=level))
                if ico:
                    menu.setIcon(QIcon(ico))
                if item.is_empty():
                    menu.menuAction().setDisabled(True)
                else:
                    self.generate(item, menu, level+1)
                parent_menu.addMenu(menu)
            # elif item.__class__.__name__ == Divider.__name__:
            elif item.type == Divider.type:
                parent_menu.addSeparator()
            elif item.type == MenuItem.type:
                if not item.is_valid():
                    continue
                a = QAction(item.text, parent_menu)
                a.setData(dict(item=item))
                if not item.enabled:
                    a.setEnabled(False)
                ico = self.create_icon(get_icon(item.icon))
                if ico:
                    a.setIcon(QIcon(ico))
                # if item.callback:
                #     a.triggered.connect(item.callback)
                a.triggered.connect(self.action_triggered)
                parent_menu.addAction(a)
            else:
                logger.error('Wrong item type for add: {}'.format(item))

    def action_triggered(self):
        """
        Action triggered callback
        """
        action = self.sender()
        item = (action.data() or {}).get('item')
        if QApplication.keyboardModifiers() == Qt.ShiftModifier and item.shift_callback:
            if callable(item.shift_callback):
                item.shift_callback()
            else:
                logger.error('shift_callback is not callable')
            return
        elif QApplication.keyboardModifiers() == Qt.ControlModifier and item.ctrl_callback:
            if callable(item.ctrl_callback):
                item.ctrl_callback()
            else:
                logger.error('shift_callback is not callable')
            return
        elif QApplication.keyboardModifiers() == Qt.AltModifier and item.alt_callback:
            if callable(item.alt_callback):
                item.alt_callback()
            else:
                logger.error('alt_callback is not callable')
            return
        if callable(item.callback):
            item.callback()
        else:
            logger.error('callback is not callable')
        return
        # if item.is_resent:
        #     if QApplication.keyboardModifiers() == Qt.ShiftModifier:
        #         # remove from resent
        #         last = settings.RECENTLY_STARTED or []
        #         data = item.resent_data()
        #         if data in last:
        #             last.remove(data)
        #             settings.RECENTLY_STARTED = last[:config.RESENTLY_APPLICATIONS]
        #         self.rebuildSignal.emit()
        #     else:
        #         # start from resent
        #         if item.callback:
        #             item.callback()
        #     return
        # if item.resent_data():
        #     if QApplication.keyboardModifiers() == Qt.ShiftModifier:
        #         # add to resent
        #         if item.add_to_resent:
        #             data = item.resent_data()
        #             last = settings.RECENTLY_STARTED or []
        #             if data in last:
        #                 # remove is exists
        #                 last.remove(data)
        #             last.insert(0, item.resent_data())
        #             settings.RECENTLY_STARTED = last[:config.RESENTLY_APPLICATIONS]
        #             self.rebuildSignal.emit()
        #     elif QApplication.keyboardModifiers() == Qt.ControlModifier:
        #         # create shortcut
        #         self.create_shortcut(item.resent_data())
        #     else:
        #         if item.callback:
        #             item.callback()
        # else:
        #     if item.callback:
        #         item.callback()

    @classmethod
    def create_icon(cls, path):
        """
        Convert PNG to ICO
        :param path: str
        :return: QIcon
        """
        if os.path.splitext(path)[-1] in ['.jpeg', '.png', '.ico']:
            return QIcon(QPixmap(path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _apply_style(self):
        """
        Apply stylesheet to main QMenu
        """
        self.setStyle(CustomMenuStyle())
        css = os.path.join(os.path.dirname(__file__), 'menu.css')
        style = ''
        if os.path.exists(css):
            # default style
            style += open(css).read()
        custom_css = os.path.join(os.path.dirname(__file__), 'custom_menu.css')
        if os.path.exists(custom_css):
            # custom style if exists
            style += open(custom_css).read()
        if style:
            self.setStyleSheet(self.__expand_css_variables(style))
        else:
            logger.warning('Style not found in %s' % css)

    def __expand_css_variables(self, css):
        # config._reload()
        for f in re.finditer("(\$[A-Z_]+)(\(.*?\))", css):
            css = css.replace(f.group(0), config._get(f.group(1).strip('$'), f.group(2).strip('(').strip(')')))
        return css

    def create_shortcut(self, data):
        from fenx.studio import app_wrappers
        app = app_wrappers.get_app(data.get('app'), data.get('version'))
        if app:
            app.create_shortcut(data.get('mode'))

    @classmethod
    def waiting_menu(cls, text):
        menu = SubMenu('')
        it = MenuItem(
            text=text,
            icon='',
            enabled=False)
        menu.append(it)
        return cls(menu)

    # def keyPressEvent(self, *args, **kwargs):
    #     print 'PRESS'
    #     super(MainTrayMenu, self).keyPressEvent(*args, **kwargs)



class MenuItem(object):
    type = 'item'
    def __init__(self,
                 text,
                 icon=None,
                 callback=None,
                 shift_callback=None,
                 ctrl_callback=None,
                 alt_callback=None,
                 os=None, enabled=True,
                 *args):
        self.text = text
        self.icon = icon
        self.callback = callback
        self.shift_callback = shift_callback
        self.ctrl_callback = ctrl_callback
        self.alt_callback = alt_callback
        # self.add_to_resent = add_to_resent
        # self.is_resent = False
        self.enabled = enabled
        self.__os = os
    #
    # def resent_data(self):
    #     if self.add_to_resent:
    #         return self.add_to_resent
    #     else:
    #         return {}

    def __repr__(self):
        return '<MenuItem "%s">' % self.text

    def __str__(self):
        return self.__repr__()

    def is_empty(self):
        return False

    def __nonzero__(self):
        return True

    def is_valid(self):
        if self.__os:
            return os.name in self.__os
        return True


class SubMenu(object):
    type = 'menu'
    def __init__(self, text, icon=None, actions=None, name=''):
        self.text = text
        self.icon = icon
        self.actions = actions or []
        self.name = name

    def append(self, item, index=-1):
        if isinstance(item, list):
            for it in item:
                self.append(it, index)
            return
        # if item.__class__.__name__ in [x.__name__ for x in MenuItem, SubMenu, Divider]:
        if index >= 0:
            self.actions.insert(index, item)
        else:
            self.actions.append(item)
        # else:
        #     raise Exception('Wrong item type: {}'.format(item))

    def __repr__(self):
        return '<SubMenu "%s" (%s)>' % (self.text or 'root', len(self.actions))

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for x in self.actions:
            yield x

    def is_empty(self):
        return len(self.actions) == 0

    def __nonzero__(self):
        return not self.is_empty()


class Divider(object):
    type = 'div'
    def __init__(self):
        self.text = '---'

    def __repr__(self):
        return '<Divider>'

    def __str__(self):
        return self.__repr__()

class CustomMenuStyle(QPlastiqueStyle):
    def __init__(self):
        super(CustomMenuStyle, self).__init__()

    def pixelMetric(self, metric, option,widget):
        if metric == QStyle.PM_SmallIconSize:
            return config._get('MENU_ICON_SIZE', 16)
        else:
            return super(CustomMenuStyle, self).pixelMetric(metric, option, widget)