from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
Signal = pyqtSignal
from fenx.tools import setup_log
from fenx.resources import get_style
from fenx.resources import qstyle_util
import logging as _logging
import os
from fenx.config import config
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

    def mousePressEvent(self, event):
        # if event.button() == Qt.MouseButton.RightButton:
        #     return
            # menu = QMenu()
            # menu.addAction(QAction('velue1', self))
            # menu.addAction(QAction('velue2', self))
            # menu.exec_(QCursor.pos())
        super(Menu, self).mousePressEvent(event)


class MainTrayMenu(Menu):
    """
    Data class for tray menu
    """
    rebuildSignal = Signal()

    def __init__(self, root_menu, parent=None, title=None):
        super(MainTrayMenu, self).__init__()
        self.par = parent
        self.root_menu = root_menu
        self.title = title
        self.title_widget = self._title_separator = None
        self.__to_parent = []
        self.title_action = self.title_label = None
        self.generate_menu()
        self._apply_style()

    def generate_menu(self):
        # clear menu
        self.build_hierarchy()
        # title item ===========================================

        # self.title_label = QLabel()
        # self.title_label.setText(self.title or '')
        # style = get_style('title')
        # if style:
        #     self.title_label.setStyleSheet(open(style).read())
        # else:
        #     self.title_label.setStyleSheet('color: red')
        # self.title_label.setAlignment(Qt.AlignLeft)
        # self.title_action = QWidgetAction(self)
        # self.title_action.setDefaultWidget(self.title_label)
        # self.addAction(self.title_action)

        # ======================================================
        self.generate(self.root_menu, self)

    def build_hierarchy(self):
        to_parent = []
        n = []
        for elem in self.root_menu.actions:
            if elem.parent:
                to_parent.append(elem)
            else:
                n.append(elem)
        self.root_menu.actions = n
        def parent_items(items, menu):
            for item in items:
                for elem in menu:
                    if elem.type == SubMenu.type:
                        if elem.name == item.parent:
                            elem.actions.append(items.pop(items.index(item)))
                        else:
                            items = parent_items(items, elem)
                    # elem.actions = sorted(elem.actions, key=lambda x: x.index)

            return items
        if not to_parent:
            return
        count = len(to_parent)
        while True:
            to_parent = parent_items(to_parent, self.root_menu)
            if not to_parent or len(to_parent) == count:
                break
            count = len(to_parent)
        if to_parent:
            for it in to_parent:
                self.root_menu.actions.append(it)
        # self.root_menu.actions = sorted(self.root_menu.actions, key=lambda x: x.index)

    def generate(self, data, parent_menu=None, level=0):
        """
        Create QMenu from data with recursion
        :param data: menu data
        :param parent_menu: parent widget
        :param level: auto value of current level. Need for colorize levels with stylesheet
        """
        parent_menu = parent_menu or self
        for item in data:
            if isinstance(item, QAction):
                item.setData(dict(item=item))
                # parent_menu.addAction(item)
                parent_menu.insertAction(item, parent_menu.actions()[0])
                continue
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
        # self.setStyle(menu_style)
        # css = os.path.join(os.path.dirname(__file__), 'menu.css')
        self.setStyleSheet(get_style('menu') + get_style('custom_menu'))

    def create_shortcut(self, data):
        from fenx.applications import wrapper
        app = wrapper.get_app(data.get('app'), data.get('version'))
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
    class OS:
        WINDOWS = 'nt'
        LINUX = 'posix'

    type = 'item'

    def __init__(self,
                 text,
                 icon=None,
                 callback=None,
                 shift_callback=None,
                 ctrl_callback=None,
                 alt_callback=None,
                 os=None,
                 enabled=True,
                 parent=None,
                 index=0,
                 *args):
        self.text = text
        self.icon = icon
        self.callback = callback
        self.shift_callback = shift_callback
        self.ctrl_callback = ctrl_callback
        self.alt_callback = alt_callback
        self.enabled = enabled
        self.parent = parent
        self.index  =index
        self.__os = os

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


class MenuItemWidget(object):
    pass


class SubMenu(object):

    type = 'menu'

    def __init__(self, text, icon=None, actions=None, name='', parent=None, index=0):
        self.text = text
        self.icon = icon
        self.actions = actions or []
        self.name = name
        self.parent = parent
        self.index = index

    def append(self, item, index=-1):
        if isinstance(item, list):
            for it in item:
                self.append(it, index)
            return
        if index >= 0:
            self.actions.insert(index, item)
        else:
            self.actions.append(item)
    #     self.sort()

    def sort(self):
        self.actions.sort(key=lambda x: [x.index, x.text])

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
    parent = None

    def __init__(self):
        self.text = '---'

    def __repr__(self):
        return '<Divider>'

    def __str__(self):
        return self.__repr__()


from PyQt5.QtWidgets import QProxyStyle

class CustomMenuStyle(QProxyStyle):
    def __init__(self):
        super(CustomMenuStyle, self).__init__()

    def pixelMetric(self, metric, option,widget):
        if metric == QProxyStyle.PM_SmallIconSize:
            return config._get('MENU_ICON_SIZE', 16)
        else:
            return super(CustomMenuStyle, self).pixelMetric(metric, option, widget)
