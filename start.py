from fenx.tools import envhelper
envhelper.fix_qt_platform_lib()
from PyQt5.QtWidgets import QApplication, QWidget, QMenu
from PyQt5.QtCore import QEvent, pyqtSignal
from fenx.launcher import main


class LauncherApp(QApplication):
    childWindowCreated = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(LauncherApp, self).__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.ChildPolished:
            if isinstance(object, QWidget) and not isinstance(object, QMenu) and not object.parent():
                self.childWindowCreated.emit(object)
        return False


if __name__ == '__main__':
    app = LauncherApp([])
    app.setQuitOnLastWindowClosed(False)
    w = main.Launcher(app.childWindowCreated)
    app.exec_()
