from PyQt5.QtWidgets import QApplication, QWidget, QMenu
from PyQt5.QtCore import QEvent, pyqtSignal

# work dir should be in directory fenx.studio
import os, sys
# sys.path.append(r'D:\work\fenx_pipeline\lib')
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
